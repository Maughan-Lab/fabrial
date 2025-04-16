from ..instruments import InstrumentSet
from ..enums.status import SequenceStatus
from ..utility.events import PROCESS_EVENTS
from PyQt6.QtCore import QThread, QObject
from typing import Self, Union
from .signals import CommandSignals, GraphSignals, InformationSignals
from .process import Process, BackgroundProcess
from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from ..sequence_builder.tree_item import TreeItem


class ProcessRunner(QObject):
    """Runs **Process**es. Contains parameters used by the `run()` method of a **Process**."""

    def __init__(self, parent: QObject, instruments: InstrumentSet, data_directory: str):
        """
        :param parent: The QObject that owns this runner. The parent should be in the same thread.
        :param instruments: The application's instruments.
        :param data_directory: The folder where all sequence data will be stored.
        """
        super().__init__(parent)
        self.application_instruments = instruments
        self.data_directory = data_directory
        self.current_process: Process | BackgroundProcess
        self.item: "TreeItem" | None = None

        self.command_signals = CommandSignals()
        self.graph_signals = GraphSignals()
        self.info_signals = InformationSignals()

        self.background_processes: list[BackgroundProcess] = []

        self.process_number = 0  # for file names

    def pre_run(self) -> Self:
        """Runs before the current process."""
        directory_base = self.current_process.DIRECTORY
        if directory_base != "":
            # example: "C:/Users/.../1 Temperature Data"
            directory = os.path.join(self.directory(), f"{self.number()} {directory_base}")
            os.makedirs(directory, exist_ok=True)
            self.current_process.set_directory(directory)

        self.current_process.update_status(SequenceStatus.ACTIVE)
        self.current_process.init_start_time()
        return self

    def run(self) -> Self:
        """Run the current process."""
        self.connect_process_signals()
        if isinstance(self.current_process, BackgroundProcess):
            self.pre_run()
            self.start_background_process(self.current_process)
        else:
            self.pre_run()
            self.current_process.run()
            self.post_run()
        return self

    def post_run(self):
        """This runs when the current process completes."""
        self.current_process.deleteLater()

    def connect_process_signals(self) -> Self:
        """Connect signals before the current process runs."""
        if not isinstance(self.current_process, BackgroundProcess):
            # up toward parent
            self.info_signals.connect_to_other(self.current_process.info_signals)
            # down toward children
            self.command_signals.pauseCommand.connect(self.current_process.pause)
            self.command_signals.unpauseCommand.connect(self.current_process.unpause)
            self.command_signals.cancelCommand.connect(self.current_process.cancel)
            self.command_signals.skipCommand.connect(self.current_process.skip)
        else:
            self.current_process.errorOccurred.connect(self.info_signals.errorOccurred)
        return self

    def set_current_proceses(self, process: Process | BackgroundProcess) -> Self:
        """Set the current process. This also updates the process number."""
        self.current_process = process
        self.process_number += 1
        if not isinstance(process, BackgroundProcess):
            self.graph_signals.connect_to_other(process.graph_signals)
            self.info_signals.graphSignalsChanged.emit(process.graph_signals)
        return self

    def process(self) -> Process | BackgroundProcess:
        """Get the current process."""
        return self.current_process

    def set_current_item(self, item: "TreeItem") -> Self:
        """Set the current item and emit signals."""
        self.info_signals.currentItemChanged.emit(item, self.item)
        self.item = item
        return self

    def current_item(self) -> Union["TreeItem", None]:
        """Get the current item."""
        return self.item

    def instruments(self) -> InstrumentSet:
        """Get the instruments."""
        return self.application_instruments

    def directory(self) -> str:
        """Get the sequence data directory."""
        return self.data_directory

    def number(self) -> int:
        """Get the process number."""
        return self.process_number

    # ----------------------------------------------------------------------------------------------
    # background process utilities
    def start_background_process(self, process: BackgroundProcess) -> Self:
        """Start a BackgroundProcess."""
        self.background_processes.append(process)

        thread = QThread()
        process.moveToThread(thread)
        thread.started.connect(process.run)
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
                PROCESS_EVENTS()

            self.background_processes.clear()
        return self
