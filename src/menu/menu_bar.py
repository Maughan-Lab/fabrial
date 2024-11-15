from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtCore import pyqtSignal
from .file import FileMenu
from .edit import EditMenu
from .view import ViewMenu
from .stability import StabilityMenu
from .sequence import SequenceMenu

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class MenuBar(QMenuBar):
    """The application's menubar."""

    # signals
    # stability check
    stabilityCheckStatusChanged = pyqtSignal(bool)  # receive
    # send
    cancelStabilityCheck = pyqtSignal()
    # sequence
    # receive
    sequenceStatusChanged = pyqtSignal(bool)
    sequenceCycleSkipped = pyqtSignal()
    sequenceBufferSkipped = pyqtSignal()
    # send
    cancelSequence = pyqtSignal()
    skipSequenceCycle = pyqtSignal()
    skipSequenceBuffer = pyqtSignal()

    def __init__(self, parent: "MainWindow"):
        super().__init__()
        self.create_submenus(parent)
        self.connect_signals()

    def connect_signals(self):
        # receive
        # stability check
        self.stabilityCheckStatusChanged.connect(self.stability.handle_status_change)
        # sequence
        self.sequenceStatusChanged.connect(self.sequence.handle_status_change)
        self.sequenceCycleSkipped.connect(self.sequence.handle_cycle_skip)
        self.sequenceBufferSkipped.connect(self.sequence.handle_buffer_skip)
        # send
        # stability check
        self.stability.cancel_stability_check.triggered.connect(self.cancelStabilityCheck.emit)
        # sequence
        self.sequence.cancel_sequence.triggered.connect(self.cancelSequence.emit)
        self.sequence.skip_current_cycle.triggered.connect(self.skipSequenceCycle.emit)
        self.sequence.skip_current_buffer.triggered.connect(self.skipSequenceBuffer.emit)

        self.sequence.skip_current_buffer.triggered.connect(lambda: print("HERE"))

    def create_submenus(self, parent):
        # need to store these because they have signals
        self.stability = StabilityMenu(self)
        self.sequence = SequenceMenu(self)

        self.addMenu(FileMenu(self, parent))
        self.addMenu(EditMenu(self))
        self.addMenu(ViewMenu(self))
        self.addMenu(self.stability)
        self.addMenu(self.sequence)
