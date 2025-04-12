from PyQt6.QtCore import pyqtSignal, QThread
from ..classes.process import ProcessRunner, Process
from ..instruments import InstrumentSet
from typing import Self
from .tree_item import TreeItem
from ..enums.status import SequenceStatus


class SequenceRunner(QThread):
    """Class for running sequences created by the SequenceBuilder."""

    statusChanged = pyqtSignal(SequenceStatus)
    errorOccurred = pyqtSignal(str)
    processChanged = pyqtSignal(Process)

    def __init__(
        self,
        instruments: InstrumentSet,
        data_directory: str,
        root_item: TreeItem,
    ):
        """
        :param instruments: The applications instruments.
        :param data_directory: The name of the base directory to write all data to.
        :root_item: The root item of the sequence builder.
        """
        super().__init__()
        self.root_item = root_item
        self.runner = ProcessRunner(instruments, data_directory)
        self.canceled = False
        # self.signals = SequenceRunnerSignals()

        self.connect_signals()

    def connect_signals(self):
        """Connect signals."""
        # self.runner.statusChanged.connect(self.signals.statusChanged.emit)
        # self.runner.errorOccurred.connect(self.signals.errorOccurred.emit)
        self.runner.statusChanged.connect(self.statusChanged.emit)
        self.runner.errorOccurred.connect(self.errorOccurred.emit)

    def process_runner(self) -> ProcessRunner:
        """Get the process runner."""
        return self.runner

    def pause(self) -> Self:
        """Pause the sequence."""
        self.runner.pause()
        return self

    def unpause(self) -> Self:
        """Pause the sequence."""
        self.runner.unpause()
        return self

    def cancel(self) -> Self:
        """Cancel the entire sequence."""
        self.canceled = True
        self.runner.cancel()
        return self

    def skip_current_process(self) -> Self:
        """Skip the current process by cancelling it and moving to the next one."""
        self.runner.cancel()
        return self

    def run(self):
        """Run the sequence."""
        final_status = SequenceStatus.COMPLETED
        for item in self.root_item.subitems():
            # setup
            process_type = item.process_type()
            process = process_type(self.runner, item.widget().to_dict())
            # set the current item and process
            self.runner.set_current_item(item).set_current_proceses(process)
            # update the visual widget
            self.processChanged.emit(process)
            # run
            self.runner.run()
            # check to see if we are cancelled
            if self.canceled:
                final_status = SequenceStatus.CANCELED
                break

        # check for and cancel any background processes
        self.runner.cancel_background_processes()
        # tell everyone else we finished
        self.statusChanged.emit(final_status)
