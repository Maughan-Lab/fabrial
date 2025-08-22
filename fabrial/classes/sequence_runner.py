from __future__ import annotations

import logging
import os
import typing
from collections.abc import Callable
from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING

from PyQt6.QtCore import QModelIndex
from PyQt6.QtWidgets import QMessageBox, QPushButton

from ..constants.paths.settings import sequence as sequence_paths
from ..custom_widgets import DontShowAgainDialog, YesNoDialog
from ..enums import SequenceCommand
from ..utility import errors
from .exceptions import PluginError
from .lock import DataLock
from .sequence_step import SequenceStep
from .sequence_thread import SequenceThread

if TYPE_CHECKING:
    from ..sequence_builder import SequenceModel
    from ..tabs import SequenceBuilderTab, SequenceDisplayTab


class ValueButton(QPushButton):
    """A button with an associated value."""

    def __init__(self, text: str, value: int):
        QPushButton.__init__(self, text)
        self.value = value


class SequenceRunner:
    """Initialize and run a sequence."""

    def __init__(self):
        self.command_queue: Queue[SequenceCommand] = Queue()
        self.thread: SequenceThread | None = None  # we have to keep a reference to the thread

    def run_sequence(
        self, sequence_tab: SequenceBuilderTab, model: SequenceModel, data_directory: Path
    ):
        """
        Run the sequence. Creates the data directory if it doesn't exist. Logs errors. Returns
        whether the sequence was successfully started.
        """
        if not model.root().subitem_count() > 0:  # do nothing if there are no items
            return False
        # make the data directory
        if not self.create_files(model, data_directory):
            return False
        # create the `SequenceStep`s
        try:
            sequence_steps, step_item_map = self.create_sequence_steps(model)
        except PluginError:
            logging.getLogger(__name__).exception(
                "Item from plugin generated error during sequence construction"
            )
            errors.show_error(
                "Sequence Error",
                "Unable to generate sequence steps, likely due to a faulty plugin. "
                "See the error log for details.",
            )
            return False
        # create the thread
        self.thread = SequenceThread(sequence_steps, data_directory, self.command_queue)
        # connect signals so the application responds to changes in the sequence
        self.connect_signals(self.thread, sequence_tab, model, step_item_map)
        # start
        self.thread.start()
        return True

    def create_files(self, model: SequenceModel, data_directory: Path) -> bool:
        """Create the sequence's root data directory and generate a sequence autosave."""
        # make the directory (does nothing if the directory exists)
        os.makedirs(data_directory, exist_ok=True)
        # check if the directory is empty
        try:
            empty = len(list(os.scandir(data_directory))) == 0
        except OSError:
            logging.getLogger(__name__).exception("Failed to check if data directory is empty")
            errors.show_error(
                "Sequence Error",
                "Unable to start the sequence because of an operating system error. "
                "See the error log for details.",
            )
            return False
        if not empty:
            # ask the user if they are okay with writing to a non-empty directory
            if not DontShowAgainDialog(
                "Note",
                "Data directory is not empty. Proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes,
                sequence_paths.NON_EMPTY_DIRECTORY_WARNING_FILE,
            ).run():
                return False
        # try to generate an autosave of the sequence
        if not model.to_json(data_directory.joinpath("autosave.json")):
            return YesNoDialog(
                "Minor Error",
                "Failed to generate sequence autosave. "
                "See the error log for details. Continue sequence?",
            ).run()
        return True

    def create_sequence_steps(
        self, model: SequenceModel
    ) -> tuple[list[SequenceStep], dict[int, QModelIndex]]:
        """
        Create `SequenceStep`s from the items in **model**. Logs errors.

        Returns
        -------
        A tuple of (the created steps, a mapping of memory addresses of sequence steps to the
        `QModelIndex` of the corresponding model item).

        Raises
        ------
        ValueError
            The model returned `None` for a subitem. This indicates an error with the codebase and
            is fatal.
        PluginError
            There was an error while creating a `SequenceStep`, which indicates a faulty plugin. The
            sequence cannot start.
        """
        step_item_map: dict[int, QModelIndex] = {}

        # helper function to create all substeps of an item by index
        def create_substeps(index: QModelIndex) -> list[SequenceStep]:
            sequence_steps: list[SequenceStep] = []
            for i in range(model.rowCount(index)):
                subindex = model.index(i, 0, index)
                substeps = create_substeps(subindex)
                subitem = model.get_item(subindex)
                if subitem is None:  # this should never happen
                    raise ValueError(
                        "A subitem was `None` when it should have been a `SequenceItem`"
                    )
                try:
                    sequence_step = subitem.create_sequence_step(substeps)
                except Exception:
                    raise PluginError(f"Error while creating sequence step from item {subitem!r}")
                # we can use the step's ID because steps are not added to/removed from the sequence
                step_item_map[id(sequence_step)] = subindex
                sequence_steps.append(sequence_step)
            return sequence_steps

        return (create_substeps(QModelIndex()), step_item_map)

    def connect_signals(
        self,
        sequence_thread: SequenceThread,
        sequence_tab: SequenceBuilderTab,
        model: SequenceModel,
        step_item_map: dict[int, QModelIndex],
    ):
        """Connect signals at construction."""
        # send the status to the sequence tab
        sequence_thread.statusChanged.connect(sequence_tab.handle_sequence_status_change)
        # make the corresponding step bold/not bold in the model
        sequence_thread.stepStateChanged.connect(
            lambda step_address, running: model.set_emphasized(step_item_map[step_address], running)
        )
        # show the prompt and send the response
        sequence_thread.promptRequested.connect(self.show_prompt)
        # run the command on the visuals tab
        sequence_thread.plotCommandRequested.connect(
            lambda command: self.run_plot_command(command, sequence_tab.visuals_tab)
        )
        # notify finish
        sequence_thread.finished.connect(lambda: sequence_tab.handle_sequence_state_change(False))

    def show_prompt(
        self, title: str, message: str, options: dict[int, str], receiver: DataLock[int | None]
    ):
        """Show a prompt to the user, then send the response back to the sequence."""
        # create the prompt
        prompt = QMessageBox()
        prompt.setWindowTitle(title)
        prompt.setText(message)
        for value, button_text in options.items():  # add the options from **options**
            prompt.addButton(ValueButton(button_text, value), QMessageBox.ButtonRole.NoRole)
        prompt.exec()  # run the prompt
        selected_value = typing.cast(ValueButton, prompt.clickedButton()).value  # get the result
        receiver.set(selected_value)  # send to the receiver

    def run_plot_command(
        self, command: Callable[[SequenceDisplayTab], None], visuals_tab: SequenceDisplayTab
    ):
        """Run a plot **command**."""
        try:
            command(visuals_tab)
        except Exception:
            logging.getLogger(__name__).exception(
                "Error while running a plot command. This usually indicates that a plugin used an "
                "invalid `PlotHandle` or `LineHandle`"
            )
            self.command_queue.put_nowait(SequenceCommand.RaiseFatal)

    def pause(self):
        """Pause the sequence."""
        self.command_queue.put_nowait(SequenceCommand.Pause)

    def unpause(self):
        """Unpause the sequence."""
        self.command_queue.put_nowait(SequenceCommand.Unpause)

    def cancel(self):
        """Cancel the sequence."""
        self.command_queue.put_nowait(SequenceCommand.Cancel)
