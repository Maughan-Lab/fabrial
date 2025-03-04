from PyQt6.QtWidgets import QMenu, QMenuBar, QFileDialog
from polars.exceptions import ColumnNotFoundError
from classes.actions import Action  # ../actions.py
from instruments import InstrumentSet  # ../instruments.py
from sequence.widgets import SequenceWidget  # ../sequence
from custom_widgets.dialog import OkDialog
from custom_widgets.plot import PlotWidget
from enums.status import StabilityStatus  # ../enums
from utility.graph import graph_from_folder  # ../utility
from typing import TYPE_CHECKING
import Files


if TYPE_CHECKING:
    from main_window import MainWindow  # ../main_window.py


class SequenceMenu(QMenu):
    """Sequence menu."""

    def __init__(
        self,
        parent: QMenuBar,
        widget: SequenceWidget,
        main_window: "MainWindow",
        instruments: InstrumentSet,
    ):
        super().__init__("&Sequence", parent)
        self.oven = instruments.oven
        self.widget = widget

        self.create_actions(parent)
        self.connect_signals()

        self.addAction(Action(parent, "Save Settings", widget.model.save_data, shortcut="Ctrl+S"))
        self.addAction(self.load_settings)

        self.addSeparator()

        self.addAction(
            Action(
                parent,
                "Generate Graph",
                lambda: self.generate_graph(main_window),
                shortcut="Ctrl+Shift+G",
            )
        )

        self.addSeparator()

        self.addAction(self.skip_current_cycle)
        self.addAction(self.skip_current_buffer)
        self.addAction(self.cancel_sequence)

    def create_actions(self, parent: QMenuBar):
        self.load_settings = Action(
            parent, "Load Settings", self.widget.model.load_data, shortcut="Ctrl+Shift+L"
        )
        self.skip_current_cycle = Action(parent, "Skip Current Cycle", self.widget.skipCycle.emit)
        self.skip_current_buffer = Action(
            parent, "Skip Current Buffer", self.widget.skipBuffer.emit
        )
        self.cancel_sequence = Action(parent, "Cancel Sequence", self.widget.cancelSequence.emit)
        # disable these initially
        for action in (self.skip_current_cycle, self.skip_current_buffer, self.cancel_sequence):
            action.setEnabled(False)

    def connect_signals(self):
        """Connect external signals."""
        self.widget.statusChanged.connect(
            lambda running: self.update_action_states(running, self.oven.is_connected())
        )
        self.widget.stageChanged.connect(self.handle_stage_change)
        self.oven.connectionChanged.connect(
            lambda connected: self.update_action_states(self.widget.is_running(), connected)
        )

    def update_action_states(self, running: bool, connected: bool):
        self.load_settings.setEnabled(not running)
        self.cancel_sequence.setEnabled(running)
        self.skip_current_cycle.setEnabled(running and connected)
        if not running or not connected:
            self.skip_current_buffer.setEnabled(False)

    def handle_stage_change(self, status: StabilityStatus):
        match status:
            case StabilityStatus.BUFFERING:
                enabled = True
            case _:
                enabled = False
        self.skip_current_buffer.setEnabled(enabled)

    def generate_graph(self, main_window: "MainWindow"):
        folder = QFileDialog.getExistingDirectory(
            self, "Select data folder.", Files.Sequence.DATA_FOLDER
        )
        if folder != "":
            try:
                plot_container = graph_from_folder(folder)
                plot_widget = PlotWidget(plot_container)
                main_window.new_window("Sequence Graph", plot_widget)
                return
            except FileNotFoundError:
                message = "Folder contains no data."
            except ColumnNotFoundError:
                message = "Data is formatted incorrectly."
            OkDialog("Error", message)  # only runs if an exception occurs
