from PyQt6.QtWidgets import QGroupBox, QGridLayout, QDoubleSpinBox, QAbstractSpinBox, QVBoxLayout
from ..widgets.spin_box import TemperatureSpinBox


class SetTempWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Set Temperature")  # set the frame's title
        # manage the layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.create_widgets(layout)

    def create_widgets(self, layout: QVBoxLayout):
        layout.addWidget(TemperatureSpinBox())
