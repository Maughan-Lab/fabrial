import sys
import traceback
from types import TracebackType
from typing import Callable

from ..Files import APPLICATION_NAME
from ..main_window import MainWindow


def generate_exception_handler(
    main_window: MainWindow,
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
        if issubclass(exception_type, SystemExit):
            print("here")
        else:
            name = APPLICATION_NAME
            error_message = (
                f"{name} encountered an application-level error. "
                f"Unless the error is obviously unimportant, you should close {name}. "
                "If possible, please report this error."
            )
            exception_text = "".join(traceback.format_exception(exception_type, exception, trace))
            error_message = f"{error_message}\n\n{exception_text}\nClose Quincy?"
            main_window.showError.emit(error_message)

    return handle_exception  # return the nested function
