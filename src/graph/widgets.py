from PyQt6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.patches import Patch
from instruments import InstrumentSet  # ../instruments.py
from custom_widgets.plot import PlotWidget  # ../custom_widgets
from custom_widgets.frame import Frame
from enums.status import StabilityStatus
from .constants import XLABEL, YLABEL


class GraphWidget(Frame):
    """Graph window that displays information from the temperature sequence."""

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
        self.plot = PlotWidget()
        self.plot.set_xlabel(XLABEL)
        self.plot.set_ylabel(YLABEL)
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
        self.plot.scatter(time, temperature, c=self.point_color, marker=".")
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
