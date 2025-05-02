from os import path

import polars as pl

from .. import Files
from ..custom_widgets.plot import PlotItem, PlotWidget
from ..enums.status import StabilityStatus
from ..graph.widgets import GraphWidget


def graph_from_folder(data_folder: str) -> PlotWidget:
    """
    Graph the temperature data in **data_folder**.

    :param data_folder: The folder to read data from.
    :returns A figure with the plotted data.
    :raises FileNotFoundError: The selected folder does not contain data.
    :raises polars.exceptions.ColumnNotFoundError: The data is formatted incorrectly.

    :returns: A PlotContainer containing a PlotItem with the graphed data. This is necessary
    so that the PlotItem's data is rendered and can be exported as an image.
    """

    plot_item = PlotItem()
    plot_item.label("bottom", GraphWidget.XLABEL)
    plot_item.label("left", GraphWidget.YLABEL)
    plot_item.set_title("Temperature Graph")

    plot_from_file(plot_item, data_folder, Files.Sequence.PRE_STABLE, StabilityStatus.CHECKING)
    plot_from_file(plot_item, data_folder, Files.Sequence.BUFFER, StabilityStatus.BUFFERING)
    plot_from_file(plot_item, data_folder, Files.Sequence.STABLE, StabilityStatus.STABLE)
    widget = PlotWidget()
    widget.plotItem = plot_item

    return widget


def plot_from_file(
    plot_item: PlotItem, folder: str, filename: str, stability_status: StabilityStatus
):
    """
    Plot data from a file on a **PlotItem**.

    :param plot_item: The PlotItem to plot on.
    :param filename: The file to read data from.
    :param folder: The folder that contains **filename**.
    :param stability_status: The stability status associated with **filename**.
    """
    TIME = Files.Sequence.Headers.TIME
    TEMPERATURE = Files.Sequence.Headers.TEMPERATURE

    file = path.join(folder, filename)
    df = pl.scan_csv(file).select(TIME, TEMPERATURE).collect()
    if df[TIME].len() != 0:  # don't plot empty files
        plot_item.scatter(
            df[TIME],
            df[TEMPERATURE],
            stability_status.legend_text(),
            GraphWidget.POINT_SIZE,
            stability_status.to_color(),
        )
