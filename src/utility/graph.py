from matplotlib.figure import Figure
from matplotlib.axes import Axes
import polars as pl
from os import path
from sequence.constants import PRE_STABLE_FILE, BUFFER_FILE, STABLE_FILE, TIME, TEMPERATURE
from graph.constants import XLABEL, YLABEL
from enums.status import StabilityStatus


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
    ax.set_xlabel(XLABEL)
    ax.set_ylabel(YLABEL)
    plot(ax, data_folder, PRE_STABLE_FILE, StabilityStatus.CHECKING.to_color())
    plot(ax, data_folder, BUFFER_FILE, StabilityStatus.BUFFERING.to_color())
    plot(ax, data_folder, STABLE_FILE, StabilityStatus.STABLE.to_color())

    return figure


def plot(ax: Axes, folder: str, filename: str, color: str):
    """
    Plot data from a file on an axis.

    :param ax: The axes to plot on.
    :param filename: The file to read data from.
    :param folder: The folder that contains **filename**.
    :param color: The color of points on the graph.
    """
    file = path.join(folder, filename)
    df = pl.scan_csv(file).select(TIME, TEMPERATURE).collect()
    ax.scatter(df[TIME], df[TEMPERATURE], c=color, marker=".")
