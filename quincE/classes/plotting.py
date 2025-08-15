from dataclasses import dataclass

from pyqtgraph import PlotDataItem


@dataclass
class TemperaturePoint:
    time: float
    temperature: float


@dataclass
class LineSettings:
    title: str
    x_label: str
    y_label: str
    legend_label: str
    line_color: str | None
    line_width: float | None
    symbol: str
    symbol_color: str
    symbol_size: int


class LineData:
    """Container for a line and its data. This is similar to a `Line2D` in `matplotlib`."""

    def __init__(self, line: PlotDataItem, x_data: list[float], y_data: list[float]):
        self.line = line
        self.x_data = x_data
        self.y_data = y_data

    def add_point(self, x: float, y: float):
        """Add a point to the line."""
        self.x_data.append(x)
        self.y_data.append(y)
        self.line.setData(self.x_data, self.y_data)
