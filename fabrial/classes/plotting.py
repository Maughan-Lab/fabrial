from __future__ import annotations

import asyncio
import copy
from dataclasses import dataclass
from os import PathLike
from typing import TYPE_CHECKING

from pyqtgraph import PlotDataItem

from .lock import DataLock

if TYPE_CHECKING:
    from .step_runner import StepRunner


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


@dataclass
class PlotSettings:
    """
    Container for plot settings (i.e. title and axis labels).

    Parameters
    ----------
    title
        The plot's title.
    x_label
        The plot's x-label.
    y_label
        The plot's y-label.
    """

    title: str
    x_label: str
    y_label: str

    def __copy__(self) -> PlotSettings:
        return PlotSettings(self.title, self.x_label, self.y_label)


@dataclass
class LineSettings:
    """
    Container for line settings (i.e. the line width, color, etc.).

    Parameters
    ----------
    legend_label
        The label to use for this line in the legend.
    line_color
        The line's color (for example, "red", or "#112233" for an exact color). If `None`, there
        will only be markers.
    line_width
        The line's width. If `None`, there will only be markers.
    symbol
        The marker symbol, i.e. "o" for a dot.
    symbol_size
        The point size.
    symbol_color
        The color of the points. Same style as **line_color**.
    """

    legend_label: str
    line_color: str | None
    line_width: float | None
    symbol: str
    symbol_color: str
    symbol_size: int

    def __copy__(self) -> LineSettings:
        return LineSettings(
            self.legend_label,
            self.line_color,
            self.line_width,
            self.symbol,
            self.symbol_color,
            self.symbol_size,
        )


@dataclass
class PlotIndex:
    """
    An index to a plot on the visuals tab.

    Parameters
    ----------
    step_address
        The memory address (aka the result of `id()`) of the step that created the plot.
    plot_number
        The number that can be used to index the actual plot.
    """

    step_address: int
    plot_number: int

    def __copy__(self) -> PlotIndex:
        return PlotIndex(self.step_address, self.plot_number)


@dataclass
class LineIndex:
    """
    An index to a line on a plot.

    Parameters
    ----------
    plot_index
        The `PlotIndex` of the plot where this the line exists.
    line_number
        The number that can be used to index the actual line.
    """

    plot_index: PlotIndex
    line_number: int

    def __copy__(self) -> LineIndex:
        return LineIndex(copy.copy(self.plot_index), self.line_number)


class PlotHandle:
    """
    A thread-safe handle to a plot on the sequence visuals tab.

    Parameters
    ----------
    runner
        The `StepRunner` being used by the sequence.
    plot_index
        The `PlotIndex` that can be used to index the actual plot.
    """

    def __init__(self, runner: StepRunner, plot_index: PlotIndex):
        self.runner = runner
        self.plot_index = plot_index

    def set_log_scale(self, x_log: bool | None, y_log: bool | None):
        """
        Set whether the x- and/or y-axis use a logarithmic scale. A value of `None` for **x_log** or
        **y_log** will leave the corresponding axis unchanged.
        """
        plot_index = copy.copy(self.plot_index)
        self.runner.submit_plot_command(
            lambda plot_tab: plot_tab.set_log_scale(plot_index, x_log, y_log)
        )

    def save_plot(self, file: PathLike[str] | str):
        """Save the plot to **file**."""
        plot_index = copy.copy(self.plot_index)
        self.runner.submit_plot_command(lambda plot_tab: plot_tab.save_plot(plot_index, file))

    async def add_line(self, line_settings: LineSettings) -> LineHandle:
        """Add an empty line to the plot."""
        receiver: DataLock[LineIndex | None] = DataLock(None)
        # we make copies of the plot index because sending the original is not thread-safe
        plot_index = copy.copy(self.plot_index)
        self.runner.submit_plot_command(
            lambda plot_tab: plot_tab.add_line(plot_index, line_settings, receiver)
        )
        while True:
            await asyncio.sleep(0)
            if (line_index := receiver.get()) is not None:
                return LineHandle(self, line_index)


class LineHandle:
    """
    A thread-safe handle to a line on a plot.

    Parameters
    ----------
    plot_handle
        The `PlotHandle` that created this object.
    line_index
        The `LineIndex` that can be used to index the actual line.
    """

    def __init__(self, plot_handle: PlotHandle, line_index: LineIndex):
        self.parent = plot_handle
        self.line_index = line_index

    def add_point(self, x: float, y: float):
        """Add a point to the line."""
        line_index = copy.copy(self.line_index)
        self.parent.runner.submit_plot_command(
            lambda plot_tab: plot_tab.add_point(line_index, x, y)
        )
