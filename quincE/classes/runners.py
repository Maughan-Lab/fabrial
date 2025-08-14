from __future__ import annotations

import os
from abc import abstractmethod
from typing import TYPE_CHECKING, Self

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from ..constants.paths.process import filenames
from ..enums import SequenceStatus
from ..utility import events
from .metaclasses import ABCQObjectMeta
from .process import (
    AbstractBackgroundProcess,
    AbstractForegroundProcess,
    AbstractGraphingProcess,
    AbstractProcess,
)
from .signals import GraphSignals

if TYPE_CHECKING:
    from ..sequence_builder import TreeItem


class AbstractRunner(QObject, metaclass=ABCQObjectMeta):
    """Abstract class for process/sequence runners."""

    errorOccurred = pyqtSignal(str, str)
    newMessageCreated = pyqtSignal(str, str, QMessageBox.StandardButton, dict, AbstractProcess)
    statusChanged = pyqtSignal(SequenceStatus)
    currentItemChanged = pyqtSignal(object, object)

    def __init__(self, parent: QObject | None = None):
        QObject.__init__(self, parent)

    @abstractmethod
    def cancel(self):
        """Cancel the sequence."""
        pass

    @abstractmethod
    def pause(self):
        """Pause the sequence."""
        pass

    @abstractmethod
    def unpause(self):
        """Unpause the sequence."""
        pass

    @abstractmethod
    def skip(self):
        """Skip the current outermost process."""
        pass

    @abstractmethod
    def send_response(
        self, selected_button: QMessageBox.StandardButton | int, recipient: AbstractProcess
    ):
        """Receive a response to a previously sent message."""
        pass


class SequenceRunner(AbstractRunner):
    """
    Class for running sequences created by the SequenceBuilder.

    Parameters
    ----------
    data_directory
        The name of the base directory to write all data to.
    root_item
        The root item of the sequence builder.
    """

    finished = pyqtSignal()

    def __init__(self, data_directory: str, root_item: TreeItem):
        AbstractRunner.__init__(self)
        self.data_directory = data_directory
        self.root_item = root_item
        self.process_runner = ProcessRunner(self, data_directory)

    def connect_runner_signals(self):
        """Connect signals before running."""
        self.process_runner.currentItemChanged.connect(self.currentItemChanged)
        self.process_runner.statusChanged.connect(self.statusChanged)
        self.process_runner.errorOccurred.connect(self.errorOccurred)
        self.process_runner.newMessageCreated.connect(self.newMessageCreated)

    def current_item(self):
        """Get the current item."""
        return self.process_runner.current_item()

    def pre_run(self) -> bool:
        """Run this before `run()`. Returns whether the sequence should continue."""
        try:  # make the data directory
            os.makedirs(self.data_directory, exist_ok=True)
        except Exception:
            self.errorOccurred.emit("Failed to create data directory, aborting.")
            return False
        self.connect_runner_signals()
        return True

    def run(self):
        """Run the sequence."""
        final_status = SequenceStatus.COMPLETED
        try:
            proceed = self.pre_run()
            if not proceed:
                return  # don't run

            for item in self.root_item.subitems():
                proceed = self.run_task(item)
                if not proceed:
                    final_status = SequenceStatus.CANCELED
                    break
            # tell everyone else we finished
        finally:
            self.post_run(final_status)

    def post_run(self, final_status: SequenceStatus):
        """Post-run tasks."""
        self.cleanup()
        self.statusChanged.emit(final_status)
        self.finished.emit()

    def run_task(self, item: TreeItem) -> bool:
        """
        Run an individual item (helper function of `run()`).

        Parameters
        ----------
        item
            The current item.

        Returns
        -------
        Whether the sequence should continue.
        """
        process_type = item.process_type()  # setup
        if process_type is not None:
            # run
            widget = item.widget()
            process = process_type(self.process_runner, widget.to_dict(), widget.display_name())
            return self.process_runner.run_process(process, item)
        return True  # if we didn't run a process (for some reason (???)) we should continue

    def cleanup(self) -> Self:
        """This runs at the end of the sequence."""
        self.currentItemChanged.emit(None, self.process_runner.current_item())
        # check for and cancel any background processes
        self.process_runner.cancel_background_processes()
        return self

    def cancel(self):
        self.process_runner.cancel()

    def pause(self):
        self.process_runner.pause()

    def unpause(self):
        self.process_runner.unpause()

    def skip(self):
        self.process_runner.skip()

    def send_response(
        self, selected_button: QMessageBox.StandardButton | int, recipient: AbstractProcess
    ):
        self.process_runner.send_response(selected_button, recipient)

    def graphing_signals(self) -> GraphSignals:
        """Get the runner's graphing signals."""
        return self.process_runner.graphing_signals()


class ProcessRunner(AbstractRunner):
    """
    Runs `Process`es. Contains parameters used by the `run()` method of a `Process`.

    Parameters
    ----------
    parent
        The QObject that owns this runner. The parent should be in the same thread.
    data_directory
        The folder where all sequence data will be stored.
    """

    def __init__(self, parent: QObject, data_directory: str):
        AbstractRunner.__init__(self, parent)
        self.data_directory = data_directory
        self.process: AbstractForegroundProcess | None = None
        self.item: TreeItem | None = None

        self.background_processes: list[AbstractBackgroundProcess] = []

        self.graph_signals = GraphSignals(self)

        self.process_number = 0  # for file names
        self.canceled = False

    def pre_run(self, process: AbstractProcess):
        """Runs before the current process."""
        directory_name = process.directory_name()
        # example: "C:/Users/.../1 Set Temperature"
        directory = os.path.join(self.directory(), f"{self.number()} {directory_name}")
        os.makedirs(directory, exist_ok=True)
        process.set_directory(directory)

        process.update_status(SequenceStatus.ACTIVE)
        process.init_start_time()

    def run_process(
        self, process: AbstractForegroundProcess | AbstractBackgroundProcess, item: TreeItem
    ) -> bool:
        """
        Run a process.

        Parameters
        ----------
        process
            The process to run.
        item
            The item associated with the process.

        Returns
        -------
        Whether the sequence was canceled.
        """
        self.currentItemChanged.emit(item, self.item)
        self.item = item
        self.process_number += 1

        process.errorOccurred.connect(self.errorOccurred)
        process.newMessageCreated.connect(self.newMessageCreated)
        if isinstance(process, AbstractBackgroundProcess):
            self.pre_run(process)
            self.start_background_process(process)
        else:
            self.process = process
            process.statusChanged.connect(self.statusChanged)
            if isinstance(process, AbstractGraphingProcess):
                self.graph_signals.connect_to_other(process.graph_signals)
            self.pre_run(process)
            process.run()
            self.post_run(process)
        return not self.canceled

    def post_run(self, process: AbstractProcess):
        """This runs when the current process completes."""
        self.write_metadata(process)
        self.graph_signals.reset.emit()
        process.deleteLater()

    def write_metadata(self, process: AbstractProcess):
        """Create a metadata file and write to it. This calls the process' `metadata()` method."""
        process.metadata().write_csv(
            os.path.join(process.directory(), filenames.METADATA),
            null_value=str(None),
        )

    def current_process(self) -> AbstractForegroundProcess | None:
        """Get the current process."""
        return self.process

    def current_item(self) -> TreeItem | None:
        """Get the current item."""
        return self.item

    def directory(self) -> str:
        """Get the sequence data directory."""
        return self.data_directory

    def set_directory(self, directory: str):
        """Set the sequence data directory."""
        self.data_directory = directory

    def number(self) -> int:
        """Get the process number."""
        return self.process_number

    def set_number(self, number: int):
        """Set the process number."""
        self.process_number = number

    def reset_number(self):
        """Reset the process number."""
        self.set_number(0)

    def graphing_signals(self) -> GraphSignals:
        """Get the runner's graphing signals."""
        return self.graph_signals

    # ----------------------------------------------------------------------------------------------
    # background process utilities
    def start_background_process(self, process: AbstractBackgroundProcess) -> Self:
        """Start a BackgroundProcess."""
        self.background_processes.append(process)

        thread = QThread(self)
        process.moveToThread(thread)
        thread.started.connect(process.run)
        process.finished.connect(lambda: self.write_metadata(process))
        process.finished.connect(thread.quit)
        thread.finished.connect(lambda: self.background_processes.remove(process))

        thread.start()
        return self

    def background_process_running(self) -> bool:
        """Whether any background processes are running."""
        return len(self.background_processes) > 0

    def cancel_background_processes(self) -> Self:
        """Cancel all background processes (usually at the end of a sequence)."""
        if self.background_process_running():
            for process in self.background_processes:
                process.cancel()
            while self.background_process_running():  # wait for them to actually finish
                events.PROCESS_EVENTS()
        return self

    # ----------------------------------------------------------------------------------------------
    # commands
    def pause(self):
        if self.process is not None:
            self.process.pause()

    def unpause(self):
        if self.process is not None:
            self.process.unpause()

    def cancel(self):
        if self.process is not None:
            self.canceled = True
            self.process.cancel()

    def skip(self):
        if self.process is not None:
            self.process.skip()

    def send_response(
        self, selected_button: QMessageBox.StandardButton | int, recipient: AbstractProcess
    ):
        recipient.send_response(selected_button)
