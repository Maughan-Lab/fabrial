from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from src.main_window import MainWindow
from src.custom_widgets.dialog import YesNoDialog
from src import Files
from src.gamry_integration.Gamry import GAMRY
import sys
import os
from types import TracebackType
import traceback


def update_id():
    """
    On Windows, this will make the application icon show up in the task bar. It does nothing on
    other platforms.
    """
    try:
        from ctypes import windll  # Only exists on Windows.

        appid = "maughangroup.quincy.1"
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except ImportError:
        pass


def make_application_folders():
    """Create folders for the application."""
    for folder in Files.FOLDERS_TO_CREATE:
        os.makedirs(folder, exist_ok=True)


def exception_handler(
    exception_type: type[BaseException], exception: BaseException, trace: TracebackType | None
):
    """
    This gets called when an uncaught exception occurs. It notifies the user of a possibly fatal
    exception and asks them if they want to quit.
    """
    if issubclass(exception_type, KeyboardInterrupt):
        sys.__excepthook__(exception_type, exception, trace)
        sys.exit()
    else:
        error_message = (
            f"{Files.APPLICATION_NAME} encountered an application-level error. "
            f"Unless the error is obviously unimportant, you should close {Files.APPLICATION_NAME}."
        )
        exception_text = "".join(traceback.format_exception(exception_type, exception, trace))
        error_message = f"{error_message}\n\n{exception_text}\nClose Quincy?"
        if YesNoDialog("Application Error", error_message).run():
            sys.exit()


def main(main_window_type: type[MainWindow] = MainWindow):
    sys.excepthook = exception_handler
    update_id()
    make_application_folders()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(Files.Icons.MAIN_ICON))
    # create the main window using `main_window_type`
    main_window = main_window_type()  # necessary for testing
    main_window.showMaximized()
    # run Quincy
    app.exec()
    # close GamryCOM
    GAMRY.cleanup()


if __name__ == "__main__":
    main()
