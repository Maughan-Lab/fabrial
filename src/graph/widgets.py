from PyQt6.QtWidgets import QVBoxLayout, QMainWindow
from PyQt6.QtGui import QCloseEvent
from matplotlib.patches import Patch
from instruments import InstrumentSet  # ../instruments.py
from custom_widgets.plot import PlotWidget  # ../custom_widgets
from custom_widgets.frame import Frame
from enums.status import StabilityStatus
from actions import Shortcut  # ../actions.py


class GraphWidget(Frame):
    """Graph window that displays information from the temperature sequence."""

    XLABEL = "Time (seconds)"
    YLABEL = "Temperature ($\degree$C)"

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""

        super().__init__(QVBoxLayout, 0)
        layout = self.layout()
        if layout is not None:
            layout.setSpacing(0)

        self.create_widgets()

    def create_widgets(self):
        layout = self.layout()

        # figure
        self.plot = PlotWidget((5, 4), 100)
        self.plot.set_xlabel(self.XLABEL)
        self.plot.set_ylabel(self.YLABEL)
        self.legend()

        layout.addWidget(self.plot)

    def legend(self):
        self.plot.legend(
            handles=(
                Patch(label="Pre-Stable", color=StabilityStatus.CHECKING.to_color()),
                Patch(label="Buffer", color=StabilityStatus.BUFFERING.to_color()),
                Patch(label="Stable", color=StabilityStatus.STABLE.to_color()),
            ),
            fontsize="small",
        )

    def add_point(self, time: float, temperature: float):
        # self.plot.scatter(time, temperature, c=self.point_color, marker=".")
        self.plot.plot(time, temperature, color=self.point_color, marker=".", linestyle="none")
        self.plot.tight_layout()
        self.plot.draw()

    def move_to_next_cycle(self, cycle_number: int):
        self.plot.clean()
        self.plot.set_title(f"Cycle {str(cycle_number)}")
        self.plot.tight_layout()

    def handle_stability_change(self, status: StabilityStatus):
        match status:
            case StabilityStatus.CHECKING | StabilityStatus.BUFFERING | StabilityStatus.STABLE:
                self.point_color = status.to_color()

    def clear(self):
        self.plot.clean()


class PoppedGraph(QMainWindow):
    """Secondary window for holding popped graphs."""

    def __init__(self, graph_widget: GraphWidget):
        super().__init__()
        self.setWindowTitle("Quincy - Popped Graph")
        self.take_ownership(graph_widget.plot, graph_widget)

        self.create_shortcuts(graph_widget.plot)

        self.handle_perishing = lambda: self.return_ownership(graph_widget.plot, graph_widget)

    def create_shortcuts(self, plot: PlotWidget):
        self.close_shortcut = Shortcut(self, "Ctrl+G", self.close)
        self.save_shortcut = Shortcut(self, "Ctrl+S", plot.toolbar.save_figure)

    def closeEvent(self, event: QCloseEvent | None):  # overridden method
        self.handle_perishing()
        self.destroyed.emit()
        if event is not None:
            event.accept()

    def take_ownership(self, widget: PlotWidget, parent: GraphWidget):
        parent.hide()
        widget.setParent(self)
        self.setCentralWidget(widget)

    def return_ownership(self, widget: PlotWidget, parent: GraphWidget):
        widget.setParent(parent)
        layout = parent.layout()
        if layout is not None:
            layout.addWidget(widget)
        parent.show()
        widget.figure.tight_layout()  # necessary to return to the proper size
