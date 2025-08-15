import os
import sys
import traceback
from types import TracebackType

from PyQt6 import QtCore
from PyQt6.QtCore import QMessageLogContext, QtMsgType

from ..constants import APP_NAME
from ..custom_widgets import OkDialog
from . import events


def exception_handler(
    exception_type: type[BaseException], exception: BaseException, trace: TracebackType | None
):
    """
    This replaces `sys.excepthook`. It logs uncaught exceptions, then runs `sys.__excepthook__()`.
    """
    sys.__excepthook__(exception_type, exception, trace)  # run the default exception hook
    if not issubclass(exception_type, KeyboardInterrupt):  # don't notify/log `KeyboardInterrupt`
        log_error(exception)
        show_error(
            "Fatal Application Error",
            f"{APP_NAME} encountered a fatal error. See the error log for details.\n\n"
            "The application will now exit.",
        )
    sys.exit()  # exit


def suppress_warnings():
    """Suppress unnecessary warnings from PyQt6 (version 6.9.1 has a bug on Windows)."""

    def warning_suppressor(msg_type: QtMsgType, context: QMessageLogContext, msg: str | None):
        match msg_type:
            case QtMsgType.QtWarningMsg:
                return
            case _:
                print(msg)

    QtCore.qInstallMessageHandler(warning_suppressor)


def show_error(title: str, message: str):
    """Show an error to the user (this is just an `OkDialog`)."""
    OkDialog(title, message).exec()


def show_error_delayed(title: str, message: str):
    """
    Wait until the application is running and the main window is shown, then show an error to the
    user.
    """
    events.delay_until_running(lambda: show_error(title, message))


def log_error(exception: BaseException):
    """Write the **exception**'s traceback to the error log."""
    if os.environ.get("PYTEST_VERSION") is not None:  # if running from pytest, don't log
        return

    print("".join(traceback.format_exception(exception)))  # TEMP
    # TODO
    # TODO: see if the below statement is a good idea
    # if writing the error log fails, show a dialog then exit

    pass
