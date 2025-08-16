from __future__ import annotations

from dataclasses import dataclass
from os import PathLike
from typing import TYPE_CHECKING

from pyqtgraph import PlotDataItem

if TYPE_CHECKING:
    from .sequence_step import StepRunner


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


@dataclass
class LineSettings:
    """
    Container for line settings (i.e. the line width, color, etc.).

    Parameters
    ----------
    legend_label
        The label to use for this line in the legend.
    line_color
        The line's color (for example, "red" or "#112233" for an exact color). If `None`, there
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

    def clear_lines(self):
        """Clear all lines from the plot. This does not affect the labels."""
        # TODO (make sure it adheres to the docstring)
        pass

    def set_log_scale(self, x_log: bool | None, y_log: bool | None):
        """
        Set whether the x- and/or y-axis use a logarithmic scale. A value of `None` for **x_log** or
        **y_log** will leave the corresponding axis unchanged.
        """
        # TODO
        pass

    def save_plot(self, file: PathLike[str] | str):
        """Save the plot to **file**."""
        # TODO: figure out if failure to save the file is fatal, silently ignored, or shown to the
        # user
        pass

    def add_line(self, line_settings: LineSettings) -> LineHandle:
        """Add an empty line to the plot."""
        line_number = ...

        # TODO: do some magic to get the number
        return LineHandle(self, LineIndex(self.plot_index, line_number))


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
        # TODO
        pass
