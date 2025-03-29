from PyQt6.QtWidgets import QVBoxLayout, QWidget
from ..custom_widgets.plot import PlotWidget
from ..custom_widgets.frame import Frame
from ..enums.status import StabilityStatus
from ..classes.plotting import TemperaturePoint, LineData
from ..custom_widgets.plot import PlotItem


class GraphWidget(Frame):
    """Graph window that displays information from the temperature sequence."""

    XLABEL = "Time (seconds)"
    YLABEL = "Temperature (°C)"
    POINT_SIZE = 7

    def __init__(self) -> None:
        super().__init__(QVBoxLayout, 0)
        self.plot: PlotWidget
        self.plot_item: PlotItem
        self.line_data: LineData

        self.create_widgets()

    def create_widgets(self):
        self.plot = PlotWidget()
        self.plot_item = self.plot.plot_item
        self.add_labels()
        self.layout().addWidget(self.plot)

    def add_labels(self):
        self.plot_item.label("bottom", self.XLABEL)
        self.plot_item.label("left", self.YLABEL)

    def add_point(self, point: TemperaturePoint):
        self.line_data.x_data.append(point.time)
        self.line_data.y_data.append(point.temperature)
        self.line_data.line.setData(self.line_data.x_data, self.line_data.y_data)

    def move_to_next_cycle(self, cycle_number: int):
        self.plot_item.clear()
        self.plot_item.set_title(f"Cycle {str(cycle_number)}")

    def handle_stage_change(self, status: StabilityStatus):
        """Add a new line to the graph that will get updated."""
        name: str
        match status:
            case StabilityStatus.CHECKING:
                name = "Pre-Stable"
            case StabilityStatus.BUFFERING:
                name = "Buffer"
            case StabilityStatus.STABLE:
                name = "Stable"
            case _:  # protect against irrelevant statuses
                return
        point_color = status.to_color()
        line = self.plot_item.scatter([], [], name, self.POINT_SIZE, point_color)
        self.line_data = LineData(line=line, x_data=[], y_data=[])

    def give_widget(self, widget: QWidget):
        """Transfer ownership of a widget to this widget."""
        widget.setParent(self)
        self.layout().addWidget(widget)  # type: ignore
        widget.show()
