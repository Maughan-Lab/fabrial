from PyQt6.QtWidgets import QGroupBox, QGridLayout
from helper_widgets.label import Label  # ../helper_widgets
from PyQt6.QtCore import Qt, QTimer
from instruments import InstrumentSet  # ../instruments.py


class PassiveMonitoringWidget(QGroupBox):
    """Widget for monitoring the oven."""

    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setTitle("Measurements")
        # manage the layout
        layout = QGridLayout()
        self.setLayout(layout)

        self.instruments = instruments
        self.create_widgets(layout)
        self.update()

        # timer to update the oven temperature and setpoint every few seconds
        update_timer = QTimer()
        update_timer.setInterval(1000)  # 1 second
        update_timer.timeout.connect(self.update)
        update_timer.start()

        self.setFixedSize(self.sizeHint())  # make sure expanding the window behaves correctly

    def create_widgets(self, layout: QGridLayout):
        """Create subwidgets."""
        layout.addWidget(Label("Oven Temperature:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        self.temperature_label = Label()
        layout.addWidget(self.temperature_label, 0, 1)

        layout.addWidget(Label("Oven Setpoint:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self.setpoint_label = Label()
        layout.addWidget(self.setpoint_label, 1, 1)

    def update(self):
        """Update the state of dynamic widgets."""
        temperature = self.instruments.oven.read_temp()
        self.temperature_label.setText(str(temperature) if temperature is not None else "-----")
        setpoint = self.instruments.oven.get_setpoint()
        self.setpoint_label.setText(str(setpoint) if setpoint is not None else "-----")
