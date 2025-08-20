from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QDoubleSpinBox, QFormLayout, QWidget

from fabrial import ItemWidget

# need to create this first so the icon is valid
app = QApplication([])

NAME = "Random Data"
DIRECTORY = Path(__file__).parent
ICON = QIcon(str(DIRECTORY.joinpath("example_icon")))


class RandomDataWidget(ItemWidget):
    """Record random data on an interval; widget."""

    def __init__(self, data_interval: float):
        layout = QFormLayout()
        parameter_widget = QWidget()
        parameter_widget.setLayout(layout)

        ItemWidget.__init__(self, parameter_widget, NAME, ICON, None)

        self.interval_spinbox = QDoubleSpinBox()
        self.interval_spinbox.setMinimum(0.1)
        self.interval_spinbox.setMaximum(1000)
        self.interval_spinbox.setValue(data_interval)
        layout.addRow("Data Interval", self.interval_spinbox)


widget = RandomDataWidget(10)
widget.show()
app.exec()
