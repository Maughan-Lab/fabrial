from PyQt6.QtWidgets import QVBoxLayout, QWidget
from custom_widgets.plot import PlotWidget  # ../custom_widgets
from custom_widgets.frame import Frame  # ../custom_widgets
from enums.status import StabilityStatus  # ../enums
from classes.points import TemperaturePoint  # ../classes


class GraphWidget(Frame):
    """Graph window that displays information from the temperature sequence."""

    XLABEL = "Time (seconds)"
    YLABEL = "Temperature ($\degree$C)"

    def __init__(self):
        super().__init__(QVBoxLayout, 0)
        self.create_widgets()

    def create_widgets(self):
        self.plot = PlotWidget()
        self.plot_item = self.plot.plot_item
        self.legend()

        self.layout().addWidget(self.plot)

    def legend(self):
        self.plot_item.addLegend()

    def add_point(self, point: TemperaturePoint):
        self.plot.plot(point.time, point.temperature, color=self.point_color, marker=".")
        self.plot.tight_layout()
        self.plot.draw()

    def move_to_next_cycle(self, cycle_number: int):
        self.plot_item.clear()
        self.plot_item.setTitle(
            f"Cycle {str(cycle_number)}", color=self.plot.text_color, size="20pt"
        )
        # TODO: see if you need to re-add the legend

    def handle_stability_change(self, status: StabilityStatus):
        match status:
            case StabilityStatus.CHECKING | StabilityStatus.BUFFERING | StabilityStatus.STABLE:
                self.point_color = status.to_color()

    def give_widget(self, widget: QWidget):
        """Transfer ownership of a widget to this widget."""
        widget.setParent(self)
        self.layout().addWidget(widget)  # type: ignore
