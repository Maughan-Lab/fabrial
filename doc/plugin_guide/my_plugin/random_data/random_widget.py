from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDoubleSpinBox, QFormLayout, QWidget

from fabrial import FilesDescription, ItemWidget, Substitutions

# we'll refer to these constants a few times
NAME = "Random Data"
DIRECTORY = Path(__file__).parent
# you should create the icon once instead of inside `__init__()`
ICON = QIcon(str(DIRECTORY.joinpath("example_icon")))


# we inherit from `ItemWidget` so Fabrial can work with our custom widget
class RandomDataWidget(ItemWidget):
    """Record random data on an interval; widget."""

    def __init__(self, data_interval: float):
        # this is a layout for other widgets
        layout = QFormLayout()
        # this widget holds the layout
        parameter_widget = QWidget()
        parameter_widget.setLayout(layout)

        # you must call the base `__init__()` method
        # for now, we're not supplying a description
        ItemWidget.__init__(
            self,
            parameter_widget,
            NAME,
            ICON,
            FilesDescription(
                # we provide the absolute path to the descriptions folder
                DIRECTORY.joinpath("descriptions"),
                NAME,
                Substitutions(
                    # notice how the dictionary keys correspond to the
                    # substitutions in the files
                    parameters={"DATA_INTERVAL": "Data Interval"},
                    data_recording={"DATA_FILE": "random_data.txt"},
                ),
            ),
        )

        # let's create the widgets!
        self.interval_spinbox = QDoubleSpinBox()
        # minimum and maximum values
        self.interval_spinbox.setMinimum(0.1)
        self.interval_spinbox.setMaximum(1000)
        # start at the supplied value
        self.interval_spinbox.setValue(data_interval)
        # add the spinbox to the layout
        # this creates an entry labeled "Data Interval" where the user
        # can enter the desired data interval
        layout.addRow("Data Interval", self.interval_spinbox)
