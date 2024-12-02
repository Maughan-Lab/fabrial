from PyQt6.QtWidgets import QVBoxLayout, QMainWindow
from PyQt6.QtGui import QCloseEvent
from matplotlib.patches import Patch
from instruments import InstrumentSet  # ../instruments.py
from custom_widgets.plot import PlotWidget  # ../custom_widgets
from custom_widgets.frame import Frame
from enums.status import StabilityStatus, STABILITY_COLOR_KEY
from actions import Shortcut  # ../actions.py


class GraphWidget(Frame):
    """Graph window that displays information from the temperature sequence."""

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""

        super().__init__(QVBoxLayout, 0)
        self.layout().setSpacing(0)

        self.xdata: list[float] = []
        self.ydata: list[float] = []

        self.create_widgets()

    def create_widgets(self):
        layout = self.layout()

        # figure
        self.plot = PlotWidget((5, 4), 100)
        self.axes = self.plot.axes  # shortcut
        self.axes.set_xlabel("Time (seconds)")
        self.axes.set_ylabel("Temperature ($\degree$C)")

        self.legend()

        self.plot.figure.tight_layout()

        layout.addWidget(self.plot)

    def legend(self):
        self.axes.legend(
            handles=(
                Patch(label="Pre-Stable", color=STABILITY_COLOR_KEY[StabilityStatus.CHECKING]),
                Patch(label="Buffer", color=STABILITY_COLOR_KEY[StabilityStatus.BUFFERING]),
                Patch(label="Stable", color=STABILITY_COLOR_KEY[StabilityStatus.STABLE]),
            ),
            fontsize="small",
        )

    def add_point(self, time: float, temperature: float):
        self.xdata.append(time)
        self.ydata.append(temperature)
        self.line.set_xdata(self.xdata)
        self.line.set_ydata(self.ydata)
        self.plot.draw()

        # TODO: remove this
        print("Point added! POGGERS")

    def move_to_next_cycle(self, cycle_number: int):
        self.plot.axes.set_title("Cycle " + str(cycle_number))
        self.clear()

        # TODO: remove this
        print("Cycle moved, YIPPEE")

    def handle_stability_status_change(self, status: StabilityStatus):
        line_index = -1  # need to instantiate this for later
        match status:
            case StabilityStatus.CHECKING:
                line_index = 0
            case StabilityStatus.BUFFERING:
                line_index = 1
            case StabilityStatus.STABLE:
                line_index = 2
            case StabilityStatus.NULL:
                return  # the sequence ended, do nothing
            case _:
                pass  # protect against an irrelevant StabilityStatus

        point_color = STABILITY_COLOR_KEY[status]

        if len(self.axes.lines) <= line_index:
            self.line = self.axes.plot([], [], color=point_color, linestyle="none")[line_index]

    def clear(self):
        # TODO: figure out how to clear the axes so that all lines are erased
        self.xdata.clear()
        self.ydata.clear()
        self.axes.clear()
        print("Graph cleared. MONKAW")


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
        event.accept()

    def take_ownership(self, widget: PlotWidget, parent: GraphWidget):
        parent.hide()
        widget.setParent(self)
        self.setCentralWidget(widget)

    def return_ownership(self, widget: PlotWidget, parent: GraphWidget):
        widget.setParent(parent)
        parent.layout().addWidget(widget)  # layout() will always return a QLayout type here
        parent.show()
        widget.figure.tight_layout()  # necessary to return to the proper size
