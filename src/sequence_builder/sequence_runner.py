from PyQt6.QtCore import pyqtSignal, QObject
from ..classes.process import ProcessRunner
from ..instruments import InstrumentSet
from typing import Self
from .tree_item import TreeItem
from ..enums.status import SequenceStatus
from ..classes.mutex import DataMutex
from ..classes.null import Null


class SequenceRunner(QObject):
    """Class for running sequences created by the SequenceBuilder."""

    finished = pyqtSignal()
    statusChanged = pyqtSignal(SequenceStatus)
    errorOccurred = pyqtSignal(str)
    widgetTypeChanged = pyqtSignal(object)  # this is a Callable[[], QWidget] | Null
    currentItemChanged = pyqtSignal(object, object)  # new, previous (TreeItem | Null)

    pauseCommand = pyqtSignal()
    unpauseCommand = pyqtSignal()
    cancelCommand = pyqtSignal()
    skipCommand = pyqtSignal()

    def __init__(self, instruments: InstrumentSet, data_directory: str, root_item: TreeItem):
        """
        :param instruments: The applications instruments.
        :param data_directory: The name of the base directory to write all data to.
        :root_item: The root item of the sequence builder.
        """
        super().__init__()
        self.root_item = root_item
        self.runner = ProcessRunner(self, instruments, data_directory)
        self.canceled = DataMutex(False)

        self.connect_signals()

    def connect_signals(self):
        """Connect signals."""
        # up toward parent
        self.runner.statusChanged.connect(self.statusChanged)
        self.runner.errorOccurred.connect(self.errorOccurred)
        self.runner.currentItemChanged.connect(self.currentItemChanged)
        self.runner.widgetTypeChanged.connect(self.widgetTypeChanged)
        # down toward children
        self.pauseCommand.connect(self.runner.pauseCommand)
        self.unpauseCommand.connect(self.runner.unpauseCommand)
        self.skipCommand.connect(self.runner.skipCommand)
        self.cancelCommand.connect(self.cancel_event)

    def run(self):
        """Run the sequence."""
        final_status = SequenceStatus.COMPLETED
        for item in self.root_item.subitems():
            proceed = self.run_task(item)
            if not proceed:
                final_status = SequenceStatus.CANCELED
                break

        self.cleanup()
        # tell everyone else we finished
        self.statusChanged.emit(final_status)
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
            process = process_type(self.runner, item.widget().to_dict())
            # set the current item and process
            self.runner.set_current_item(item).set_current_proceses(process)
            # run
            self.runner.run()
        # return whether we should keep going
        return not self.canceled.get()

    def cleanup(self) -> Self:
        """This runs at the end of the sequence."""
        self.currentItemChanged.emit(Null(), self.runner.current_item())
        self.widgetTypeChanged.emit(Null())
        # check for and cancel any background processes
        self.runner.cancel_background_processes()
        return self

    def process_runner(self) -> ProcessRunner:
        """Get the process runner."""
        return self.runner

    def cancel_event(self) -> Self:
        """Cancel the entire sequence."""
        self.canceled.set(True)
        self.runner.cancelCommand.emit()
        return self
