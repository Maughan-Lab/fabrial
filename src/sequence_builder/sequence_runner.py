from PyQt6.QtCore import pyqtSignal, QObject
from ..classes.process_runner import ProcessRunner
from ..instruments import InstrumentSet
from typing import Self
from .tree_item import TreeItem
from ..enums.status import SequenceStatus
import os


class SequenceRunner(QObject):
    """Class for running sequences created by the SequenceBuilder."""

    finished = pyqtSignal()

    def __init__(self, instruments: InstrumentSet, data_directory: str, root_item: TreeItem):
        """
        :param instruments: The applications instruments.
        :param data_directory: The name of the base directory to write all data to.
        :root_item: The root item of the sequence builder.
        """
        super().__init__()
        self.data_directory = data_directory
        self.root_item = root_item
        self.process_runner = ProcessRunner(self, instruments, data_directory)
        self.canceled = False

        self.command_signals = self.process_runner.command_signals
        self.info_signals = self.process_runner.info_signals
        self.graph_signals = self.process_runner.graph_signals

    def pre_run(self) -> bool:
        """Run this before `run()`. Returns whether the sequence should continue."""
        try:
            os.makedirs(self.data_directory, exist_ok=True)
        except Exception:
            self.info_signals.errorOccurred.emit("Failed to create data directory, aborting.")
            return False
        if not self.root_item.child_count() > 0:
            return False
        return True

    def run(self):
        """Run the sequence."""
        proceed = self.pre_run()
        if not proceed:
            return  # don't run

        final_status = SequenceStatus.COMPLETED
        for item in self.root_item.subitems():
            proceed = self.run_task(item)
            if not proceed:
                final_status = SequenceStatus.CANCELED
                break

        self.cleanup()
        # tell everyone else we finished
        self.info_signals.statusChanged.emit(final_status)
        self.finished.emit()

    def run_task(self, item: TreeItem) -> bool:
        """
        Run an individual item (helper function of **run()**).

        :param item: The current item.
        :returns: Whether the sequence should continue.
        """
        # setup
        process_type = item.process_type()
        if process_type is not None:
            process = process_type(self.process_runner, item.widget().to_dict())
            # set the current item and process
            self.process_runner.set_current_item(item).set_current_proceses(process)
            # run
            self.process_runner.run()
        # return whether we should keep going
        return not self.canceled

    def cleanup(self) -> Self:
        """This runs at the end of the sequence."""
        self.info_signals.currentItemChanged.emit(None, self.process_runner.current_item())
        # check for and cancel any background processes
        self.process_runner.cancel_background_processes()
        return self

    def cancel(self) -> Self:
        """Cancel the sequence."""
        self.canceled = True
        self.command_signals.cancelCommand.emit()
        return self

    def pause(self) -> Self:
        """Pause the sequence."""
        self.command_signals.pauseCommand.emit()
        return self

    def unpause(self) -> Self:
        """Unpause the sequence."""
        self.command_signals.unpauseCommand.emit()
        return self

    def skip(self) -> Self:
        """Skip the current outermost process."""
        self.command_signals.skipCommand.emit()
        return self
