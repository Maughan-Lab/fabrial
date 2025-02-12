from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSlot
from matplotlib.patches import Patch
from custom_widgets.plot import PlotWidget  # ../custom_widgets
from custom_widgets.frame import Frame  # ../custom_widgets
from enums.status import StabilityStatus  # ../enums
from classes.points import TemperaturePoint  # ../classes


class GraphingThread(QRunnable):
    def __init__(self, plot: PlotWidget, point: TemperaturePoint, point_color: str):
        super().__init__()
        self.plot = plot
        self.point = point
        self.point_color = point_color

    @pyqtSlot()
    def run(self):
        self.plot.scatter(
            self.point.time, self.point.temperature, color=self.point_color, marker="."
        )
        self.plot.tight_layout()
        self.plot.draw()


class GraphWidget(Frame):
    """Graph window that displays information from the temperature sequence."""

    XLABEL = "Time (seconds)"
    YLABEL = "Temperature ($\degree$C)"

    def __init__(self):
        """:param instruments: Container for instruments."""
        self.threadpool = QThreadPool()

        super().__init__(QVBoxLayout, 0)
        layout = self.layout()
        if layout is not None:
            layout.setSpacing(0)

        self.create_widgets()

    def create_widgets(self):
        layout = self.layout()

        # figure
        self.plot = PlotWidget()
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

    def add_point(self, point: TemperaturePoint):
        thread = GraphingThread(self.plot, point, self.point_color)
        self.threadpool.start(thread)

    def move_to_next_cycle(self, cycle_number: int):
        self.plot.clean()
        self.plot.set_title(f"Cycle {str(cycle_number)}")
        self.plot.tight_layout()

    def handle_stability_change(self, status: StabilityStatus):
        match status:
            case StabilityStatus.CHECKING | StabilityStatus.BUFFERING | StabilityStatus.STABLE:
                self.point_color = status.to_color()

    def give_widget(self, widget: QWidget):
        """Transfer ownership of a widget to this widget."""
        widget.setParent(self)
        layout = self.layout()
        if layout is not None:
            layout.addWidget(widget)

    def show(self):  # overridden method
        """Resize the plot, then show."""
        self.plot.tight_layout()
        super().show()
