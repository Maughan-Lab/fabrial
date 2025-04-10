from PyQt6.QtCore import QRunnable, QThreadPool
from PyQt6.QtWidgets import QWidget
from ..classes.process import ProcessInputs
from ..instruments import InstrumentSet
from typing import Self
from .tree_item import TreeItem
from .items.base.process import BaseProcess


class SequenceRunner(QRunnable):
    """Class for running sequences created by the SequenceBuilder."""

    def __init__(self, instruments: InstrumentSet, data_directory: str, root_item: TreeItem):
        """
        :param instruments: The applications instruments.
        :param data_directory: The name of the base directory to write all data to.
        :root_item: The root item of the sequence builder.
        """
        super().__init__()
        self.root_item = root_item
        self.process_inputs = ProcessInputs(instruments, QThreadPool(), data_directory, root_item)
        self.current_process: BaseProcess
        self.current_widget: QWidget

    def set_paused(self, paused: bool) -> Self:
        """Pause/unpause the sequence."""
        # TODO
        return self

    def cancel(self) -> Self:
        """Cancel the entire sequence."""
        # TODO
        return self

    def skip_current_process(self) -> Self:
        """Skip the current process by cancelling it and moving to the next one."""
        # TODO
        return self

    def run(self):
        """Run the sequence."""
        # TODO: finish
        for item in self.root_item.subitems():
            self.process_inputs.current_item = item
            process_type = item.process_type()
            self.current_process = process_type(item.data())
            self.current_widget = self.current_process.visual_widget()
            # TODO: add the process' widget to the third tab on the main window
            self.current_process.run(self.process_inputs)
        if self.process_inputs.threadpool.activeThreadCount() > 0:
            # TODO: cancel all background processes
            # might need to have a list of background processes in ProcessInputs
            pass
