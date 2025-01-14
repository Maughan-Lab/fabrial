from PyQt6.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox
from .label import Label
from utility.layouts import add_to_layout  # ../utility


class Dialog(QDialog):
    """Base class for dialog pop-ups."""

    def __init__(self, title: str, message: str, buttons: QDialogButtonBox.StandardButton):
        super().__init__()

        self.setWindowTitle(title)
        self.button_box = QDialogButtonBox(buttons)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        self.setLayout(layout)
        add_to_layout(layout, Label(message), self.button_box)

        self.setFixedSize(self.sizeHint())

    def run(self) -> bool:
        return bool(self.exec())


class YesCancelDialog(Dialog):
    """Dialog pop-up with Yes and Cancel buttons."""

    def __init__(self, title: str, message: str):
        super().__init__(
            title,
            message,
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.Cancel,
        )


class OkDialog(Dialog):
    """Dialog pop-up with an Ok button."""

    def __init__(self, title: str, message: str):
        super().__init__(title, message, QDialogButtonBox.StandardButton.Ok)


class OkCancelDialog(Dialog):
    """Dialog pop-up with Ok and Cancel buttons."""

    def __init__(self, title: str, message: str):
        super().__init__(
            title,
            message,
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
        )
