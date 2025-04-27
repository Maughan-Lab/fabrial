from PyQt6.QtWidgets import QMessageBox


class Dialog(QMessageBox):
    """Base class for dialog pop-ups."""

    def __init__(
        self,
        title: str,
        message: str,
        buttons: QMessageBox.StandardButton,
        default_button: QMessageBox.StandardButton,
    ):
        super().__init__()

        self.setWindowTitle(title)
        self.setText(message)
        self.setStandardButtons(buttons)
        self.setDefaultButton(default_button)

    def run(self) -> bool:
        """Virtual, return whether the proposed action was accepted."""
        return True


class YesCancelDialog(Dialog):
    """Dialog pop-up with Yes and Cancel buttons."""

    def __init__(self, title: str, message: str):
        super().__init__(
            title,
            message,
            Dialog.StandardButton.Yes | Dialog.StandardButton.Cancel,
            Dialog.StandardButton.Yes,
        )

    def run(self) -> bool:
        match self.exec():
            case Dialog.StandardButton.Yes:
                return True
        return False


class OkDialog(Dialog):
    """Dialog pop-up with an Ok button. `run()` always returns **True**."""

    def __init__(self, title: str, message: str):
        super().__init__(title, message, Dialog.StandardButton.Ok, Dialog.StandardButton.Ok)


class OkCancelDialog(Dialog):
    """Dialog pop-up with Ok and Cancel buttons."""

    def __init__(self, title: str, message: str):
        super().__init__(
            title,
            message,
            Dialog.StandardButton.Ok | Dialog.StandardButton.Cancel,
            Dialog.StandardButton.Ok,
        )

    def run(self) -> bool:
        match self.exec():
            case Dialog.StandardButton.Ok:
                return True
        return False


class YesNoDialog(Dialog):
    """Dialog pop-up with Yes and No buttons."""

    def __init__(self, title: str, message: str):
        super().__init__(
            title,
            message,
            Dialog.StandardButton.Yes | Dialog.StandardButton.No,
            Dialog.StandardButton.Yes,
        )

    def run(self):
        match self.exec():
            case Dialog.StandardButton.Yes:
                return True
        return False
