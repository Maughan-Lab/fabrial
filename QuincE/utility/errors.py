import sys
import traceback
from types import TracebackType
from typing import TYPE_CHECKING, Callable

from PyQt6 import QtCore
from PyQt6.QtCore import QMessageLogContext, QtMsgType

from ..constants import APP_NAME
from ..custom_widgets import OkDialog
from . import events

if TYPE_CHECKING:
    from ..main_window import MainWindow


def generate_exception_handler(
    main_window: "MainWindow",
) -> Callable[[type[BaseException], BaseException, TracebackType | None], None]:
    """Generate an exception handler for the application."""

    # nested function definition
    def handle_exception(
        exception_type: type[BaseException], exception: BaseException, trace: TracebackType | None
    ):
        """
        This should get called when an uncaught exception occurs. It notifies the user of a possibly
        fatal exception and asks them if they want to quit.
        """
        if issubclass(exception_type, KeyboardInterrupt):
            sys.__excepthook__(exception_type, exception, trace)
            sys.exit()
        else:
            error_message = (
                f"{APP_NAME} encountered an application-level error. "
                f"Unless the error is obviously unimportant, you should close {APP_NAME}. "
                "If possible, please report this error."
            )
            exception_text = "".join(traceback.format_exception(exception_type, exception, trace))
            error_message = f"{error_message}\n\n{exception_text}\nClose {APP_NAME}?"
            main_window.showError.emit(error_message)

    return handle_exception  # return the nested function


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
