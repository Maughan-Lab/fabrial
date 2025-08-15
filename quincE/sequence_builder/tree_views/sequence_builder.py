from __future__ import annotations

import json
import os
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from PyQt6.QtCore import (
    QItemSelection,
    QModelIndex,
    QPersistentModelIndex,
    QPoint,
    Qt,
    QThread,
    pyqtSignal,
)
from PyQt6.QtGui import QDragMoveEvent, QKeyEvent
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox, QSizePolicy, QVBoxLayout

from ...classes import (
    AbstractProcess,
    CommandSignals,
    GraphSignals,
    PluginError,
    SequenceStep,
    Shortcut,
    Timer,
)
from ...constants.paths.settings import sequence as sequence_paths
from ...custom_widgets import (
    BiggerButton,
    Container,
    Dialog,
    FixedButton,
    IconLabel,
    OkDialog,
    YesCancelDontShowDialog,
    YesNoDialog,
)
from ...enums import SequenceStatus
from ...utility import errors, images, layout as layout_util
from ..tree_items.tree_item import TreeItem
from ..tree_models import SequenceModel
from .tree_view import TreeView


@dataclass
class DragTracker:
    timer: Timer
    position: QPoint


class SequenceTreeView(TreeView[SequenceModel]):
    """
    Custom `TreeView` for displaying sequence settings.

    Parameters
    ----------
    model
        The model the view will use.
    """

    def __init__(self, model: SequenceModel):
        TreeView.__init__(self, model)
        # configure
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        # used to expand items when hovering over them
        point = QPoint()
        timer = Timer(self, 500, lambda: self.expand(self.indexAt(point)))
        timer.setSingleShot(True)
        self.drag_tracker = DragTracker(timer, point)

    @classmethod
    def from_autosave(cls) -> Self:
        """Create from the autosave files."""
        model = SequenceModel([])
        model.init_from_json(sequence_paths.SEQUENCE_ITEMS_FILE)
        view = cls(model)
        view.init_view_state_from_json(sequence_paths.SEQUENCE_STATE_FILE)
        return view

    def select_load(self):
        """Load sequence items from a user-selected file."""
        file, _ = QFileDialog.getOpenFileName(
            self, "Select sequence file", filter="JSON files (*.json)"
        )
        if file != "":
            if not self.model().init_from_json(file):
                OkDialog(
                    "Load Error",
                    "Failed to load the requested file. Ensure the file is correctly formatted and "
                    "that all plugins the file references are installed.",
                ).exec()
            else:
                self.expandAll()

    def select_save(self):
        """Save the sequence items to a user-selected file."""
        file, _ = QFileDialog.getSaveFileName(
            self, "Select save file", "untitled.json", "JSON files (*.json)"
        )
        if file != "":
            if not self.model().to_json(file):
                OkDialog(
                    "Save Error",
                    "Failed to save sequence. "
                    "This could be caused by a faulty plugin or permission issues. "
                    "See the error log for details.",
                ).exec()

    def save_on_close(self):
        """Call this when closing the application to save the item and view state."""
        self.model().to_json(sequence_paths.SEQUENCE_ITEMS_FILE)
        self.save_view_state_to_json(sequence_paths.SEQUENCE_STATE_FILE)

    def connect_signals(self):  # overridden
        TreeView.connect_signals(self)
        self.model().itemAdded.connect(self.handle_new_item)

    def items_editable(self) -> bool:  # overridden
        return True  # TODO: make this depend on whether the widget is enabled

    def handle_new_item(self, index: QModelIndex):
        """Handle an item being added to the model."""
        self.expand(index)  # expand the new item
        self.expand(index.parent())  # and its parent

    def create_shortcuts(self):  # overridden
        TreeView.create_shortcuts(self)
        Shortcut(
            self, "Ctrl+X", self.cut_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        Shortcut(
            self, "Ctrl+V", self.paste_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )

    def cut_event(self):
        """Move items to the clipboard."""
        self.copy_event()
        self.delete_event()

    def paste_event(self):
        """Paste items from the clipboard after the currently selected item."""
        self.model().paste_items(self.currentIndex())

    def delete_event(self):
        """Delete currently selected items."""
        # store the index below the current index
        persistent_new_selection_index = QPersistentModelIndex(self.indexBelow(self.currentIndex()))

        self.model().delete_items(self.selectedIndexes())

        # select the next available item after deleting
        new_selection_index = QModelIndex(persistent_new_selection_index)
        if not new_selection_index.isValid():
            # try the item below the currently selected item
            new_selection_index = self.indexBelow(self.currentIndex())
            if not new_selection_index.isValid():
                # try whatever is currently selected (usually the last item in this situation)
                new_selection_index = self.currentIndex()
                if not new_selection_index.isValid():
                    # at this point there should be no items in the model
                    self.clearSelection()

        self.setCurrentIndex(new_selection_index)

    # ----------------------------------------------------------------------------------------------
    def keyPressEvent(self, event: QKeyEvent | None):  # overridden
        if event is not None:
            match event.key():
                case Qt.Key.Key_Delete:  # delete the current item
                    self.delete_event()
                case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                    self.open_event(self.selectedIndexes())
        TreeView.keyPressEvent(self, event)

    def dragMoveEvent(self, event: QDragMoveEvent | None):  # overridden
        if event is not None:
            tracked_position = self.drag_tracker.position
            event_position = event.position().toPoint()
            tracked_position.setX(event_position.x())
            tracked_position.setY(event_position.y())
            self.drag_tracker.timer.start()
        TreeView.dragMoveEvent(self, event)


class SequenceTreeWidget(Container):
    """SequenceTreeView with a delete button."""

    # signals that get emitted to other objects
    directoryChanged = pyqtSignal(bool)  # whether the selected directory is valid

    sequenceStatusChanged = pyqtSignal(SequenceStatus)
    graphSignalsChanged = pyqtSignal(GraphSignals)

    def __init__(self, view: SequenceTreeView):
        layout = QVBoxLayout()
        Container.__init__(self, layout)

        self.view = view
        self.delete_button: FixedButton
        self.directory_button: BiggerButton
        self.directory_label: IconLabel
        self.create_widgets(layout)
        self.connect_signals()

        self.threads: list[SequenceRunner] = []

        self.command_signals = CommandSignals()
        self.cancelCommand = self.command_signals.cancelCommand  # shortcut for external users

    @classmethod
    def from_autosave(cls) -> Self:
        """Create from the autosave files."""
        view = SequenceTreeView.from_autosave()
        return cls(view)

    def create_widgets(self, layout: QVBoxLayout):
        """Create widgets at construction."""
        button_layout = QHBoxLayout()
        button_container = Container(button_layout)

        self.delete_button = FixedButton("Delete Selected Items", self.view.delete_event)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)

        button_sublayout = QHBoxLayout()
        self.save_button = FixedButton("Save", self.view.select_save)
        self.save_button.setIcon(images.make_icon("script-export.png"))
        button_sublayout.addWidget(self.save_button)
        self.load_button = FixedButton("Load", self.view.select_load)
        self.load_button.setIcon(images.make_icon("script-import.png"))
        button_sublayout.addWidget(self.load_button)

        button_layout.addWidget(self.delete_button, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addLayout(button_sublayout)

        layout_util.add_to_layout(layout, button_container, self.view)

        # the data directory selection widgets
        directory_layout = layout_util.add_sublayout(layout, QHBoxLayout())
        self.directory_button = BiggerButton(
            "Choose Data Directory", self.choose_directory, size_scalars=(1.5, 2)
        )
        self.directory_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.directory_label = IconLabel(
            images.make_pixmap("folder--arrow.png"), self.load_previous_directory()
        )
        self.directory_label.label().setWordWrap(True)
        directory_layout.addWidget(self.directory_button)
        directory_layout.addWidget(self.directory_label, alignment=Qt.AlignmentFlag.AlignVCenter)

    def connect_signals(self):
        """Connect signals at construction."""

        self.view.selectionModel().selectionChanged.connect(  # type: ignore
            self.handle_selection_change
        )

    def handle_selection_change(self, selected: QItemSelection, *args):
        """Handle the item selection changing."""
        enabled = True
        if selected.isEmpty():
            enabled = False
        else:
            for index in selected.indexes():
                if not index.isValid():
                    enabled = False
        self.delete_button.setEnabled(enabled)

    def choose_directory(self):
        """Open a dialog to choose the data-storage directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select sequence data location",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly,
        )
        self.directory_label.label().setText(directory)
        self.directoryChanged.emit(self.directory_is_valid())

    def directory_is_valid(self):
        """Whether the selected directory is valid."""
        return self.directory_label.label().text() != ""

    def load_previous_directory(self) -> str:
        """Try to load the previously used directory."""
        try:
            with open(sequence_paths.SEQUENCE_DIRECTORY_FILE, "r") as f:
                directory = typing.cast(str, json.load(f))
                return directory
        except Exception:
            return ""

    def save_on_close(self):
        """Call this when closing the application to save settings."""
        self.view.save_on_close()
        # try to save the data directory
        directory = self.data_directory()
        try:
            with open(sequence_paths.SEQUENCE_DIRECTORY_FILE, "w") as f:
                json.dump(directory, f)
        except OSError:
            pass

    def data_directory(self) -> str:
        """Get the current data directory."""
        return self.directory_label.label().text()

    # ----------------------------------------------------------------------------------------------
    # running the sequence
    def is_running(self) -> bool:
        """Whether the sequence is currently running."""
        return len(self.threads) > 0

    def run_sequence(self):
        """Run the sequence."""
        # TODO
        pass


# TODO: see if these functions should even be in a class
class SequenceRunner:
    """Initialize and run a sequence."""

    def run_sequence(self, model: SequenceModel, data_directory: Path):
        """Run the sequence. Creates the data directory if it doesn't exist."""
        if not model.root().subitem_count() > 0:  # do nothing if there are no items
            return
        # make the data directory
        if not self.create_files(model, data_directory):
            return
        # create the `SequenceStep`s
        try:
            sequence_steps, step_item_map = self.create_sequence_steps(model)
        except PluginError as e:
            errors.log_error(e)
            errors.show_error(
                "Sequence Error",
                "Unable to generate sequence steps, likely due to a faulty plugin. "
                "See the error log for details.",
            )
            return

        thread = QThread(self)
        # TODO: change SequenceRunner to accept Path
        runner = SequenceRunner(str(directory), root_item)
        runner.moveToThread(thread)
        self.connect_sequence_signals(runner, thread)
        self.graphSignalsChanged.emit(runner.graphing_signals())
        # run
        thread.started.connect(runner.run)
        thread.start()
        return self

    def create_files(self, model: SequenceModel, data_directory: Path) -> bool:
        """Create the sequence's root data directory and generate a sequence autosave."""
        # make the directory (does nothing if the directory exists)
        os.makedirs(data_directory, exist_ok=True)
        # check if the directory is empty
        try:
            empty = len(list(os.scandir(data_directory))) > 0
        except OSError as e:
            errors.log_error(e)
            errors.show_error(
                "Sequence Error",
                "Unable to start the sequence because of an operating system error. "
                "See the error log for details.",
            )
            return False
        if not empty:
            # ask the user if they are okay with writing to a non-empty directory
            if not YesCancelDontShowDialog(
                "Note",
                "Data directory is not empty. Proceed?",
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
                except Exception as e:
                    errors.log_error(e)
                    raise PluginError(f"Error while creating sequence step from item {subitem!r}")
                # we can use the step's ID because steps are not added to/removed from the sequence
                step_item_map[id(sequence_step)] = subindex
                sequence_steps.append(sequence_step)
            return sequence_steps

        return (create_substeps(QModelIndex()), step_item_map)

    # TODO: fix
    def connect_sequence_signals(self, runner: SequenceRunner, thread: QThread) -> Self:
        """Connect signals before starting the sequence."""

        def handle_message_creation(
            message: str,
            name: str,
            buttons: QMessageBox.StandardButton,
            text_mapping: dict[QMessageBox.StandardButton, str],
            sender: AbstractProcess,
        ):
            """Handle a message being sent from the sequence runner."""
            dialog = Dialog(f"Message from {name}", message, buttons)
            for standard_button, text in text_mapping.items():
                button = dialog.button(standard_button)
                if button is not None:
                    button.setText(text)
            runner.send_response(dialog.exec(), sender)

        def handle_item_change(current: TreeItem | None, previous: TreeItem | None):
            """Handle the current sequence item changing."""
            # TODO: fix
            return
            if previous is not None:
                previous.set_running(False)
            if current is not None:
                current.set_running(True)
            self.view.update()

        def set_running(running: bool):
            """Adjust the view and directory button based on whether a sequence is running."""
            not_running = not running
            if running:
                self.view.clearSelection()
            self.view.model().set_enabled(not_running)
            self.view.setDragEnabled(not_running)
            self.view.setAcceptDrops(not_running)
            self.view.update()
            self.directory_button.setDisabled(running)
            self.load_button.setDisabled(running)

        def sequence_start_event():
            """This runs when the sequence starts."""
            set_running(True)
            self.view.expandAll()
            self.threads.append(runner)

        def sequence_end_event():
            """This runs when the sequence ends."""
            set_running(False)
            self.threads.remove(runner)

        # up towards the parent
        runner.errorOccurred.connect(
            lambda message, name: OkDialog(f"Error in {name}", message).exec()
        )
        runner.newMessageCreated.connect(handle_message_creation)
        runner.currentItemChanged.connect(handle_item_change)
        runner.statusChanged.connect(self.sequenceStatusChanged)
        # down towards the child
        self.command_signals.cancelCommand.connect(runner.cancel)
        self.command_signals.pauseCommand.connect(runner.pause)
        self.command_signals.unpauseCommand.connect(runner.unpause)
        self.command_signals.skipCommand.connect(runner.skip)
        # internal-only signals
        runner.finished.connect(thread.quit)
        thread.started.connect(sequence_start_event)
        thread.finished.connect(sequence_end_event)

        return self
