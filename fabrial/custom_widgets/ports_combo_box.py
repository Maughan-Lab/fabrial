from PyQt6.QtWidgets import QComboBox

from ..utility import ports


class PortComboBox(QComboBox):
    """A `QComboBox` for COM ports."""

    def __init__(self, initial_port: str | None = None):
        QComboBox.__init__(self)
        self.reload_ports()
        self.setCurrentText(initial_port)

    def reload_ports(self):
        """Refresh the list of ports."""
        current = self.currentText()
        self.clear()
        self.addItems(ports.list_ports())
        self.setCurrentText(current)  # restore the selection

    def showPopup(self):  # overridden
        # refresh the list of ports every time the item list is shown
        self.reload_ports()
        QComboBox.showPopup(self)
