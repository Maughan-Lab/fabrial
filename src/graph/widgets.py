import matplotlib
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as Canvas,
    NavigationToolbar2QT as Toolbar,
)
from matplotlib.figure import Figure
from polars import DataFrame
from PyQt6.QtWidgets import QVBoxLayout
from instruments import InstrumentSet  # ../instruments.py
from custom_widgets.groupbox import GroupBox  # ../custom_widgets
from helper_functions.layouts import add_to_layout

matplotlib.use("qtagg")


class GraphWidget(GroupBox):
    """
    Graph window that displays information from the temperature sequence.
    """

    def __init__(self, instruments: InstrumentSet, data: DataFrame):
        super().__init__("Sequence Graph", QVBoxLayout, instruments)

        self.sequence_data = data

        self.create_widgets()

    def create_widgets(self):
        layout = self.layout()

        # figure
        self.canvas = Canvas(Figure(figsize=(5, 4), dpi=100))
        axes = self.canvas.figure.add_subplot(111)
        axes.plot([2, 3], [1, 2])
        self.canvas.figure.tight_layout()
        add_to_layout(layout, self.canvas, Toolbar(self.canvas, self))

        # TODO: fix this it's super broken

    def update(self):
        pass
