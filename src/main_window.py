from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget
from PyQt6.QtGui import QCloseEvent
from setpoint.widgets import SetpointWidget
from passive_monitoring.widgets import PassiveMonitoringWidget
from instrument_connection.widgets import InstrumentConnectionWidget
from stability_check.widgets import StabilityCheckWidget
from sequence.widgets import SequenceWidget
from graph.widgets import GraphWidget, PoppedGraph
from custom_widgets.dialog import YesCancelDialog
from instruments import InstrumentSet
from utility.layouts import add_to_layout_grid
from menu.menu_bar import MenuBar


class MainWindow(QMainWindow):
    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setWindowTitle("Quincy")
        self.secondary_windows: list[QMainWindow] = []

        self.create_widgets(instruments)
        self.connect_signals()
        self.create_menu()

    def create_widgets(self, instruments):
        """Create subwidgets."""
        # create the layout
        layout = QGridLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setpoint_widget = SetpointWidget(instruments)
        self.stability_check_widget = StabilityCheckWidget(instruments)
        self.sequence_widget = SequenceWidget(instruments)
        self.graph_widget = GraphWidget(instruments)
        # do not move these two above the other ones
        self.passive_monitoring_widget = PassiveMonitoringWidget(instruments)
        self.instrument_connection_widget = InstrumentConnectionWidget(instruments)
        # add the widgets
        add_to_layout_grid(
            layout,
            (self.setpoint_widget, 0, 0),
            (self.stability_check_widget, 1, 0),
            (self.passive_monitoring_widget, 0, 1),
            (self.instrument_connection_widget, 0, 2),
            (self.sequence_widget, 2, 0),
        )
        layout.addWidget(self.graph_widget, 1, 1, 2, 2)

    def connect_signals(self):
        """Connect widget signals."""
        # connect the graph
        self.sequence_widget.newDataAquired.connect(self.graph_widget.add_point)
        self.sequence_widget.cycleNumberChanged.connect(self.graph_widget.move_to_next_cycle)
        self.sequence_widget.stabilityChanged.connect(self.graph_widget.handle_stability_change)
        # connect the stability check
        self.sequence_widget.statusChanged.connect(
            lambda running: self.stability_check_widget.reset() if running else None
        )

    def create_menu(self):
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

    def new_window(self, new_window: QMainWindow):
        new_window.show()
        self.secondary_windows.append(new_window)
        new_window.destroyed.connect(lambda: self.secondary_windows.remove(new_window))

    # ----------------------------------------------------------------------------------------------
    # resizing
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def shrink(self):
        if self.isFullScreen():
            self.showNormal()
        self.resize(self.minimumSize())

    # ----------------------------------------------------------------------------------------------
    # pop the graph
    def pop_graph(self):
        popped_graph = PoppedGraph(self.graph_widget)
        popped_graph.destroyed.connect(self.menu_bar.view.poppedGraphDestroyed.emit)
        self.new_window(popped_graph)

    # ----------------------------------------------------------------------------------------------
    # closing the window
    def closeEvent(self, event: QCloseEvent | None):  # overridden method
        """Prevent the window from closing if a sequence or stability check are running."""
        if event is not None:
            event.accept() if self.allowed_to_close() else event.ignore()

    def allowed_to_close(self) -> bool:
        """Determine if the window should close."""
        if self.stability_check_widget.is_running():
            message = "A stability check is currently running."
            signal = self.stability_check_widget.cancelStabilityCheck
        elif self.sequence_widget.is_running():
            message = "A sequence is currently running."
            signal = self.sequence_widget.cancelSequence
        else:
            return True  # we can close
        # this will run if either of the first two conditions triggered
        if YesCancelDialog("Are you sure you want to exit?", message).run():
            signal.emit()
            return True
        return False
