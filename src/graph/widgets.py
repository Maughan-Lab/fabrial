from PyQt6.QtWidgets import QVBoxLayout
from instruments import InstrumentSet  # ../instruments.py
from custom_widgets.groupbox import GroupBox  # ../custom_widgets
from custom_widgets.plot import PlotWidget  # ../custom_widgets
from enums.stability_check_status import StabilityCheckStatus


class GraphWidget(GroupBox):
    """Graph window that displays information from the temperature sequence."""

    def __init__(self, instruments: InstrumentSet):
        """
        :param instruments: Container for instruments.
        """

        super().__init__("Sequence Graph", QVBoxLayout, instruments)

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
        self.plot.figure.tight_layout()

        layout.addWidget(self.plot)

    def update(self):
        pass

    def add_point(self, time: float, temperature: float):
        self.xdata.append(time)
        self.ydata.append(temperature)
        self.line.set_xdata(self.xdata)
        self.line.set_ydata(self.ydata)
        self.plot.draw()

        # TODO: remove this
        print("Point added! POGGERS")

    def move_to_next_cycle(self, cycle_number: int):
        self.plot.axes.set_title("Cycle" + str(cycle_number))
        self.clear()

        # TODO: remove this
        print("Cycle moved, YIPPEE")

    def handle_status_change(self, status: StabilityCheckStatus):
        # TODO: add the actual colors for point_color
        match status:
            case StabilityCheckStatus.CHECKING:
                line_index = 0
                point_color = ""
            case StabilityCheckStatus.BUFFERING:
                line_index = 1
                point_color = ""
            case StabilityCheckStatus.STABLE:
                line_index = 2
                point_color = ""
            case _:
                pass  # protect against race conditions
        if len(self.axes.lines) <= line_index:
            self.line = self.axes.plot([], [], color=point_color, linestyle="none")[line_index]

    def clear(self):
        # TODO: figure out how to clear the axes so that all lines are erased
        self.xdata.clear()
        self.ydata.clear()
        self.axes.clear()
        print("Graph cleared. MONKAW")
