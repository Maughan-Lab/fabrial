import json
from os import PathLike

from PyQt6.QtWidgets import QCheckBox, QMessageBox


class Dialog(QMessageBox):
    """
    Base class for dialog pop-ups.

    Parameters
    ----------
    title
        The window title.
    message
        The message text.
    buttons
        The buttons used on the dialog.
    default_button
        The initially selected button. Defaults to `StandardButton.Ok` if the dialog has that
        button, otherwise no button is selected.
    """

    def __init__(
        self,
        title: str,
        message: str,
        buttons: QMessageBox.StandardButton,
        default_button: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    ):
        QMessageBox.__init__(self)

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
        Dialog.__init__(
            self,
            title,
            message,
            Dialog.StandardButton.Yes | Dialog.StandardButton.Cancel,
            Dialog.StandardButton.Yes,
        )


class OkDialog(Dialog):
    """Dialog pop-up with an Ok button. `run()` always returns `True`."""

    def __init__(self, title: str, message: str):
        Dialog.__init__(self, title, message, Dialog.StandardButton.Ok, Dialog.StandardButton.Ok)


class OkCancelDialog(Dialog):
    """Dialog pop-up with Ok and Cancel buttons."""

    def __init__(self, title: str, message: str):
        Dialog.__init__(
            self,
            title,
            message,
            Dialog.StandardButton.Ok | Dialog.StandardButton.Cancel,
            Dialog.StandardButton.Ok,
        )


class YesNoDialog(Dialog):
    """Dialog pop-up with Yes and No buttons."""

    def __init__(self, title: str, message: str):
        Dialog.__init__(
            self,
            title,
            message,
            Dialog.StandardButton.Yes | Dialog.StandardButton.No,
            Dialog.StandardButton.Yes,
        )


class DontShowAgainDialog(Dialog):
    """
    A dialog that has a "Don't show again" option.

    Parameters
    ----------
    title
        The title of the dialog.
    message
        The message text shown on the dialog.
    buttons
        `StandardButton`s to show on the dialog.
    default_button
        Which `StandardButton` to have selected by default.
    file
        The JSON file where the "don't show again" state is saved to and loaded from.
    """

    def __init__(
        self,
        title: str,
        message: str,
        buttons: QMessageBox.StandardButton,
        default_button: QMessageBox.StandardButton,
        file: PathLike[str] | str,
    ):

        Dialog.__init__(self, title, message, buttons, default_button)
        self.check_box = QCheckBox("Don't show again", self)
        self.setCheckBox(self.check_box)

        self.file = file
        try:
            with open(self.file, "r") as f:
                if not json.load(f):
                    self.check_box.setChecked(True)
        except OSError:
            pass

    def should_run(self) -> bool:
        """
        Whether we should even run the dialog (we shouldn't run if the user checked "Don't show
        again").
        """
        return not self.check_box.isChecked()

    def save_state(self):
        """Save the state of the "Don't show again" checkbox to a file."""
        try:
            with open(self.file, "w") as f:
                json.dump(not self.check_box.isChecked(), f)
        except OSError:
            pass

    def run(self) -> bool:
        """
        Show the dialog and save the state of the "Don't show again" checkbox afterward. Returns
        whether the proposed action was accepted. If the "Don't show again" checkbox is checked,
        this always returns `True` without showing the dialog.
        """
        if self.should_run():
            result = Dialog.run(self)
            self.save_state()
            return result
        return True
