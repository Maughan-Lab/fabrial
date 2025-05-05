from PyQt6.QtWidgets import QMessageBox

from ....classes.process import AbstractForegroundProcess
from . import encoding as DATA


class TestProcess(AbstractForegroundProcess):
    def run(self):
        self.send_message(
            "dskljf",
            QMessageBox.StandardButton.Ok
            | QMessageBox.StandardButton.Abort
            | QMessageBox.StandardButton.Retry,
        )
        print(self.wait_on_response())

    @staticmethod
    def directory_name():
        return "Test"
