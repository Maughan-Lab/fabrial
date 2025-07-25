from __future__ import annotations

import time
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Self

import polars as pl
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from ..constants.paths.process.headers import metadata as metadata_headers
from ..enums import SequenceStatus, StatusStateMachine
from ..utility import datetime, events
from .lock import DataMutex
from .metaclasses import ABCQObjectMeta
from .plotting import LineSettings
from .signals import GraphSignals

if TYPE_CHECKING:
    from .runners import ProcessRunner


class AbstractProcess(QObject, metaclass=ABCQObjectMeta):
    """Abstract class for all processes."""

    newMessageCreated = pyqtSignal(str, str, QMessageBox.StandardButton, dict, QObject)
    """
    Emit this to send a message to the user. Send:
    - The message as a **str**.
    - The process' name as a **str**.
    - The buttons to show on the dialog as a **QMessageBox.StandardButton**.
    - A dictionary that maps **StandardButton**s to the text to display on the button. Can be empty.
    - The process sending the message as an **AbstractProcess** (or subclass).
    """
    errorOccurred = pyqtSignal(str, str, object)
    """
    Emit this when an error occurs and the user cannot do anything about it. Send
    - The message as a **str**.
    - The process' name as a **str**.
    - The process sending the message as an **AbstractProcess** (or subclass).
    """

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        QObject.__init__(self)
        self.data_as_dict = data
        self.process_runner = runner
        self.display_name = name
        self.process_start_time = 0.0
        self.process_status = StatusStateMachine(SequenceStatus.INACTIVE)
        self.data_directory = ""
        self.message_response = DataMutex[QMessageBox.StandardButton | None](None)

    @abstractmethod
    def run(self):
        """
        Run the process. When subclassing this method, you must ensure that long-running
        processes frequently call `wait()`, otherwise they will freeze the application.
        """
        pass

    def data(self):
        """Get this process' data."""
        return self.data_as_dict

    @staticmethod
    @abstractmethod
    def directory_name() -> str:
        """
        Get the name of the directory to store data in without preceding folder names. For example,
        "Set Temperature".
        """
        pass

    def set_directory(self, data_directory: str):
        """Set the data directory."""
        self.data_directory = data_directory

    def directory(self) -> str:
        """
        Get the directory to write this process' data to. The name and creation of this directory is
        managed by the **ProcessRunner**, so you can assume it already exists.
        """
        return self.data_directory

    def init_start_time(self):
        """Call this right before `run()` to set the start time from `time.time()`."""
        self.process_start_time = time.time()

    def start_time(self) -> float:
        """Get the start time of this process in seconds."""
        return self.process_start_time

    def runner(self) -> ProcessRunner:
        """Get the **ProcessRunner** running this process."""
        return self.process_runner

    def name(self) -> str:
        """Get the name associated with this process."""
        return self.display_name

    def status(self) -> SequenceStatus:
        """Get the process status."""
        return self.process_status.get()

    @abstractmethod
    def update_status(self, status: SequenceStatus) -> bool:
        """
        Set the status, possibly emitting signals.

        :returns: Whether the status was updated (a valid state change occurred).
        """
        pass

    def is_canceled(self) -> bool:
        """Whether the process has been canceled."""
        return self.status() == SequenceStatus.CANCELED

    def cancel(self):
        """Cancel the current process gracefully."""
        self.process_status.set(SequenceStatus.CANCELED)

    def metadata(self) -> pl.DataFrame:
        """
        Create a DataFrame containing metadata for the process. By default, this DataFrame contains
        the start datetime, end datetime, duration in seconds, and oven setpoint. You can override
        this method to add additional metadata.
        """
        start_time = self.start_time()
        end_time = time.time()
        duration = end_time - start_time
        metadata = pl.DataFrame(
            {
                metadata_headers.START_DATETIME: datetime.get_datetime(start_time),
                metadata_headers.END_DATETIME: datetime.get_datetime(end_time),
                metadata_headers.DURATION: duration,
            }
        )
        return metadata

    def send_message(
        self,
        message: str,
        buttons: QMessageBox.StandardButton,
        text_mapping: dict[QMessageBox.StandardButton, str] = dict(),
    ):
        """
        Send a message to the user. The display name of the process' item is used in the title.

        :param message: The message text.
        :param buttons: The buttons to display on the dialog.
        :param text_mapping: A dictionary of **StandardButton**s and the text to display on them.
        """
        self.newMessageCreated.emit(message, self.display_name, buttons, text_mapping, self)

    def communicate_error(self, error_message: str):
        """Communicate an error to the user. The user only has the **Ok** option."""
        self.errorOccurred.emit(error_message, self.display_name, self)

    def send_response(self, selected_button: QMessageBox.StandardButton | int):
        """Receive the response to a previously sent message."""
        self.message_response.set(selected_button)  # type: ignore

    def check_response(self) -> QMessageBox.StandardButton | None:
        """
        Check for a response to a previously sent message. Returns **None** when no response is
        present, otherwise returns the response. If a response is found, calling this function again
        without having sent a new message will return **None**.
        """
        response = self.message_response.get()
        if response is not None:
            self.message_response.set(None)
        return response

    def wait_on_response(self) -> QMessageBox.StandardButton | None:
        """
        Wait for the user to response to a sent message.

        If the process is canceled during this time, returns **None**.
        """
        response = self.check_response()
        while response is None:
            events.PROCESS_EVENTS()
            if self.is_canceled():
                return None
            response = self.check_response()
        return response


class AbstractForegroundProcess(AbstractProcess):
    """Abstract class for foreground processes."""

    statusChanged = pyqtSignal(SequenceStatus)
    """Send the status as a **SequenceStatus**."""

    def wait(self, delay_ms: int, unerror_fn: Callable[[], bool] = lambda: False) -> bool:
        """
        Hold for **delay** milliseconds or as long as the process is paused, whichever is longer.
        This is where signals are processed, so be sure to call this frequently.

        :param delay_ms: How long to hold for.
        :param unerror_fn: If the sequence is paused in an error state, this function can cause it
        to unpause and exit the error state. This function takes no arguments and should return\
        **True** to unpause, **False** otherwise.

        :returns: Whether the process should continue (i.e. it was not cancelled).
        """
        delay = delay_ms / 1000
        end_time = time.time() + delay
        while time.time() < end_time:
            if self.is_canceled():
                return False
            events.PROCESS_EVENTS()  # process events for 10 ms
        while self.is_paused():
            if self.is_canceled():
                return False
            events.PROCESS_EVENTS()  # process events for 10 ms
            if self.is_errored():
                if unerror_fn():
                    self.unpause()

        return True

    def is_paused(self) -> bool:
        """Whether the process is paused."""
        return self.status().is_pause()

    def is_errored(self) -> bool:
        """Whether the process is in an error state."""
        return self.status().is_error()

    def skip(self) -> Self:
        """
        Skip the current process. By default, this just calls **cancel()**. You can override this
        for nested processes to skip an inner process instead.
        """
        self.cancel()
        return self

    def pause(self) -> Self:
        """Pause the process."""
        self.update_status(SequenceStatus.PAUSED)
        return self

    def error_pause(self) -> Self:
        """Pause the process with an error"""
        self.update_status(SequenceStatus.ERROR_PAUSED)
        return self

    def unpause(self) -> Self:
        """Unpause the process."""
        self.update_status(SequenceStatus.ACTIVE)
        return self

    def update_status(self, status: SequenceStatus) -> bool:
        changed = self.process_status.set(status)
        if changed:
            self.statusChanged.emit(status)
        return changed


class AbstractGraphingProcess(AbstractForegroundProcess):
    """**AbstractForegroundProcess** with graphing capabilities."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        AbstractForegroundProcess.__init__(self, runner, data, name)
        self.graph_signals = GraphSignals(self)

    def graphing_signals(self) -> GraphSignals:
        """Get the process' graphing signals."""
        return self.graph_signals

    def init_line_plot(
        self,
        plot_index: int,
        name: str,
        title: str,
        x_label: str,
        y_label: str,
        legend_label: str,
        line_color: str,
        line_width: float,
        symbol: str,
        symbol_color: str,
        symbol_size: int,
    ):
        """Initialize the sequence graph as a line plot."""
        settings = LineSettings(
            title,
            x_label,
            y_label,
            legend_label,
            line_color,
            line_width,
            symbol,
            symbol_color,
            symbol_size,
        )
        self.graph_signals.initPlot.emit(plot_index, name, settings)

    def init_scatter_plot(
        self,
        plot_index: int,
        name: str,
        title: str,
        x_label: str,
        y_label: str,
        legend_label: str,
        symbol: str = "o",
        symbol_color: str = "orange",
        symbol_size: int = 7,
    ):
        """Initialize the sequence graph as a scatter plot."""
        settings = LineSettings(
            title,
            x_label,
            y_label,
            legend_label,
            None,
            None,
            symbol,
            symbol_color,
            symbol_size,
        )
        self.graph_signals.initPlot.emit(plot_index, name, settings)


class AbstractBackgroundProcess(AbstractProcess):
    """Abstract class for background processes."""

    finished = pyqtSignal()

    def wait(self, delay_ms: int) -> bool:
        """
        Hold for **delay** milliseconds. This is where signals are processed, so be sure to call
        this frequently.

        :returns: Whether the process should continue (i.e. it was not cancelled).
        """
        delay = delay_ms / 1000
        end_time = time.time() + delay
        while time.time() < end_time:
            if self.is_canceled():
                return False
            events.PROCESS_EVENTS()  # process events for 10 ms
        return True

    def update_status(self, status: SequenceStatus) -> bool:
        # there are no signals to emit here
        return self.process_status.set(status)

    def cancel(self):
        AbstractProcess.cancel(self)
        self.finished.emit()
