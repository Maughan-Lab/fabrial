import logging
import sys
from types import TracebackType

from PyQt6 import QtCore
from PyQt6.QtCore import QMessageLogContext, QtMsgType

from ..constants import APP_NAME
from ..constants.paths import SAVED_DATA_FOLDER
from ..custom_widgets import OkDialog
from . import events


def exception_handler(
    exception_type: type[BaseException], exception: BaseException, trace: TracebackType | None
):
    """
    This replaces `sys.excepthook`. It logs uncaught exceptions, then runs `sys.__excepthook__()`.
    """
    if not issubclass(exception_type, KeyboardInterrupt):  # don't notify/log `KeyboardInterrupt`
        # log the exception
        logging.getLogger(__name__).critical(
            "Uncaught exception", exc_info=(exception_type, exception, trace)
        )
        show_error(  # notify the user
            "Fatal Application Error",
            f"{APP_NAME} encountered a fatal error. "
            "Please save the contents of the error log and report the issue.\n\n"
            f"{APP_NAME} will now exit.",
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
    """Wait until the event loop is running, then show an error to the user."""
    events.delay_until_running(lambda: show_error(title, message))


def set_up_logging():
    """Configure the root logger of the `logging` module."""
    logging.basicConfig(
        level=logging.INFO,  # log INFO and up
        style="{",  # used for the format specifier
        datefmt="%Y-%m-%d %H:%M:%S",  # datetime format
        # show datetime, error level, logger name, the calling function's name, and the log message
        format="{asctime}.{msecs:.0f} {levelname} {message} - {name}:{funcName}()",
        filename=SAVED_DATA_FOLDER.joinpath("lastrun.log"),  # send to `lastrun.log`
        filemode="w+",  # wipe the file between runs
    )
