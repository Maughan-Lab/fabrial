from PyQt6.QtWidgets import QFormLayout, QVBoxLayout
from ..enums.status import StabilityStatus
from ..utility.layouts import add_sublayout
from ..custom_widgets.label import Label
from ..custom_widgets.groupbox import GroupBox
from ..instruments import INSTRUMENTS
from ..custom_widgets.progressbar import StabilityProgressBar


class StabilityCheckWidget(GroupBox):
    """Widget for monitoring whether the oven's temperature is stable."""

    NULL_TEXT = "----------"

    def __init__(self) -> None:
        super().__init__("Oven Stability", QVBoxLayout())
        self.previous_count = 0
        self.status_label: Label
        self.progress_bar: StabilityProgressBar
        self.create_widgets()
        self.connect_signals()
        # TODO: create widgets
        # TODO: connect the oven to the widgets
        # TODO: add this to the oven control tab

    def create_widgets(self):
        """Create subwidgets."""
        layout: QVBoxLayout = self.layout()  # type: ignore
        label_layout = add_sublayout(layout, QFormLayout)
        self.status_label = Label(self.NULL_TEXT)
        self.progress_bar = StabilityProgressBar(INSTRUMENTS.oven, self)
        self.handle_stability_change(False)  # initialize text and color

        label_layout.addRow("Status:", self.status_label)
        layout.addWidget(self.progress_bar)

    def connect_signals(self):
        """Connect widget signals."""
        oven = INSTRUMENTS.oven
        oven.stabilityChanged.connect(self.handle_stability_change)
        oven.stabilityCountChanged.connect(self.handle_stability_count_change)
        oven.connectionChanged.connect(self.handle_connection_change)

    def handle_stability_change(self, stable: bool):
        """Handle a stability change from the oven."""
        if INSTRUMENTS.oven.is_connected():
            text = StabilityStatus.bool_to_str(stable)
            color = StabilityStatus.bool_to_color(stable)
            self.status_label.setText(text)
            self.status_label.set_color(color)

    def handle_stability_count_change(self, count: int):
        """Handle the oven's stability count changing."""
        self.progress_bar.setValue(count)

    def handle_connection_change(self, connected: bool):
        """Handle the oven disconnecting/reconnecting."""
        if not connected:
            self.status_label.reset(self.NULL_TEXT)
        else:
            self.handle_stability_change(INSTRUMENTS.oven.is_stable())
            self.handle_stability_count_change(INSTRUMENTS.oven.stability_count())
