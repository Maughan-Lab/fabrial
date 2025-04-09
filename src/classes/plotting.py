from dataclasses import dataclass
import pyqtgraph as pg  # type: ignore


@dataclass
class TemperaturePoint:
    time: float
    temperature: float


@dataclass
class LineData:
    line: pg.PlotDataItem
    x_data: list[float | int]
    y_data: list[float | int]
