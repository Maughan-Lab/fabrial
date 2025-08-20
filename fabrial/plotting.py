from __future__ import annotations

import asyncio
import copy
from dataclasses import dataclass
from os import PathLike
from typing import TYPE_CHECKING

from pyqtgraph import PlotDataItem

from .classes.lock import DataLock

if TYPE_CHECKING:
    from .classes.step_runner import StepRunner


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
        return PlotSettings(copy.copy(self.title), copy.copy(self.x_label), copy.copy(self.y_label))


@dataclass
class LineParams:
    """
    Describes a line should look.

    Parameters
    ----------
    color
        The line's color (i.e. "red" or "#112233").
    width
        The line's width.
    """

    color: str
    width: float

    def __copy__(self) -> LineParams:
        return LineParams(copy.copy(self.color), self.width)


@dataclass
class SymbolParams:
    """
    Describes how symbols on a line should look.

    Parameters
    ----------
    symbol
        The symbol to use, (i.e. "o" for a dot) See
        [`pyqtgraph`](https://pyqtgraph.readthedocs.io/en/latest/)'s documentation for more info.
    color
        The symbol's color.
    size
        The symbol's point size.
    """

    symbol: str
    color: str
    size: int

    def __copy__(self) -> SymbolParams:
        return SymbolParams(copy.copy(self.symbol), copy.copy(self.color), self.size)


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

    async def add_line(
        self,
        legend_label: str | None,
        line_params: LineParams | None,
        symbol_params: SymbolParams | None,
    ) -> LineHandle:
        """
        Add an empty line to the plot.

        Parameters
        ----------
        legend_label
            The label to use for the legend. If `None` there will be no legend label.
        line_params
            How the line should look. If `None` there will be no line.
        symbol_params
            How the symbols (aka markers) should look. If `None` there will be no symbols.
        """
        receiver: DataLock[LineIndex | None] = DataLock(None)
        # we make copies because sending the originals is not thread-safe
        plot_index = copy.copy(self.plot_index)
        legend_label = copy.copy(legend_label)
        line_params = copy.copy(line_params)
        symbol_params = copy.copy(symbol_params)
        self.runner.submit_plot_command(
            lambda plot_tab: plot_tab.add_line(
                plot_index, legend_label, line_params, symbol_params, receiver
            )
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
