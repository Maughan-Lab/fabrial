from PyQt6.QtWidgets import QCheckBox, QMessageBox


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
        """Show the dialog and return whether the proposed action was accepted."""
        self.exec()
        role = self.buttonRole(self.clickedButton())
        Roles = QMessageBox.ButtonRole
        match role:
            case Roles.AcceptRole | Roles.YesRole | Roles.ApplyRole:
                return True
        return False


class YesCancelDialog(Dialog):
    """Dialog pop-up with Yes and Cancel buttons."""

    def __init__(self, title: str, message: str):
        super().__init__(
            title,
            message,
            Dialog.StandardButton.Yes | Dialog.StandardButton.Cancel,
            Dialog.StandardButton.Yes,
        )


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


class YesNoDialog(Dialog):
    """Dialog pop-up with Yes and No buttons."""

    def __init__(self, title: str, message: str):
        super().__init__(
            title,
            message,
            Dialog.StandardButton.Yes | Dialog.StandardButton.No,
            Dialog.StandardButton.Yes,
        )


class DontShowAgainDialog(Dialog):

    def __init__(
        self,
        title: str,
        message: str,
        buttons: QMessageBox.StandardButton,
        default_button: QMessageBox.StandardButton,
        filepath: str,
    ):
        """
        :param title: The title of the dialog.
        :param message: The message text shown on the dialog.
        :param buttons: **StandardButton**s to show on the dialog.
        :param default_button: Which **StandardButton** to have selected by default.
        :param filepath: The filepath where the "don't show again" state is saved to and loaded
        from.
        """
        super().__init__(title, message, buttons, default_button)
        self.check_box = QCheckBox("Don't show again", self)
        self.setCheckBox(self.check_box)

        self.filepath = filepath
        try:
            with open(self.filepath, "r") as f:
                if f.read().strip() == str(False):
                    self.check_box.setChecked(True)
        except Exception:
            pass

    def should_run(self) -> bool:
        """
        Whether we should even run the dialog (we shouldn't run if the user checked "Don't show
        again").
        """
        return not self.check_box.isChecked()

    def save_state(self):
        """Save the state of the "Don't show again" checkbox to a file."""
        with open(self.filepath, "w") as f:
            f.write(str(not self.check_box.isChecked()))

    def run(self) -> bool:
        """
        Show the dialog and save the state of the "Don't show again" checkbox afterward. Returns
        whether the proposed action was accepted. If the "Don't show again" checkbox is checked,
        this always returns **True** without showing the dialog.
        """
        if self.should_run():
            result = super().run()
            self.save_state()
            return result
        return True


class YesCancelDontShowDialog(DontShowAgainDialog):
    """Yes and Cancel buttons."""

    def __init__(self, title: str, message: str, dont_show_again_filepath: str):
        super().__init__(
            title,
            message,
            Dialog.StandardButton.Yes | Dialog.StandardButton.Cancel,
            Dialog.StandardButton.Yes,
            dont_show_again_filepath,
        )
