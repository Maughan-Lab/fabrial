from dataclasses import dataclass

from pyqtgraph import PlotDataItem  # type: ignore


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


@dataclass
class LineData:
    line: PlotDataItem
    x_data: list[float | int]
    y_data: list[float | int]

    def add_point(self, x_value: float, y_value: float):
        """Add a point to the line."""
        self.x_data.append(x_value)
        self.y_data.append(y_value)
        self.line.setData(self.x_data, self.y_data)
