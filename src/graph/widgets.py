import matplotlib
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as Canvas,
    NavigationToolbar2QT as Toolbar,
)
from matplotlib.figure import Figure
from polars import DataFrame
import numpy as np
from PyQt6.QtWidgets import QVBoxLayout
from instruments import InstrumentSet  # ../instruments.py
from custom_widgets.groupbox import GroupBox  # ../custom_widgets
from helper_functions.layouts import add_to_layout

matplotlib.use("qtagg")


class GraphWidget(GroupBox):
    """Graph window that displays information from the temperature sequence."""

    def __init__(self, instruments: InstrumentSet):
        """
        :param instruments: Container for instruments.
        """

        super().__init__("Sequence Graph", QVBoxLayout, instruments)

        self.create_widgets()

    def create_widgets(self):
        layout = self.layout()

        # figure
        self.canvas = Canvas(Figure(figsize=(5, 4), dpi=100))
        self.axes = self.canvas.figure.add_subplot()
        self.axes.set_xlabel("Time (seconds)")
        self.axes.set_ylabel("Temperature ($\degree$C)")

        add_to_layout(layout, self.canvas, Toolbar(self.canvas, self))

    def initialize_graph(self):
        # plot empty data to initialize the graph
        self.plot = self.axes.plot([], [])[0]
        self.canvas.figure.tight_layout()

    def update(self):
        pass

    def add_point(self, time: float, temperature: float):
        self.plot.set_xdata(np.append(self.plot.get_xdata(), [time]))
        self.plot.set_ydata(np.append(self.plot.get_ydata(), [temperature]))
        # TODO: see if you need the pyqtSignal decorator
        # TODO: update this to use .plot instead because this is a scatterplot. I don't think
        # we need a reference to the stored data
        self.canvas.draw()
        print("Point added! POGGERS")

    def move_to_next_cycle(self, cycle_number: int):
        print("Cycle moved, YIPPEE")

    def clear(self):
        print("Graph cleared. MONKAW")
