from matplotlib.figure import Figure
from matplotlib.axes import Axes
import polars as pl
from os import path
from graph.widgets import GraphWidget
from enums.status import StabilityStatus
import Files


def graph_from_folder(data_folder: str) -> Figure:
    """
    Graph the temperature data in data_folder.

    :param data_folder: The folder to read data from.
    :returns A figure with the plotted data.
    :raises FileNotFoundError: The selected folder does not contain data.
    :raises polars.exceptions.ColumnNotFoundError: The data is formatted incorrectly.
    """
    figure = Figure((6, 5))
    ax = figure.add_subplot()
    ax.set_xlabel(GraphWidget.XLABEL)
    ax.set_ylabel(GraphWidget.YLABEL)
    plot(ax, data_folder, Files.Sequence.PRE_STABLE, StabilityStatus.CHECKING.to_color())
    plot(ax, data_folder, Files.Sequence.BUFFER, StabilityStatus.BUFFERING.to_color())
    plot(ax, data_folder, Files.Sequence.STABLE, StabilityStatus.STABLE.to_color())

    return figure


def plot(ax: Axes, folder: str, filename: str, color: str):
    """
    Plot data from a file on an axis.

    :param ax: The axes to plot on.
    :param filename: The file to read data from.
    :param folder: The folder that contains **filename**.
    :param color: The color of points on the graph.
    """
    TIME = Files.Sequence.Headers.TIME
    TEMPERATURE = Files.Sequence.Headers.TEMPERATURE

    file = path.join(folder, filename)
    df = pl.scan_csv(file).select(TIME, TEMPERATURE).collect()
    ax.scatter(df[TIME], df[TEMPERATURE], c=color, marker=".")
