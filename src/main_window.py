from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt6.QtGui import QCloseEvent
from tabs.tab_widget import TabWidget
from custom_widgets.dialog import YesCancelDialog
from instruments import InstrumentSet
from secondary_window import SecondaryWindow
from menu.menu_bar import MenuBar
import time


class MainWindow(QMainWindow):
    def __init__(self, instruments: InstrumentSet) -> None:
        super().__init__()
        self.setWindowTitle("Quincy")

        # create tabs
        self.tabs = TabWidget(self, instruments)
        self.setCentralWidget(self.tabs)
        self.oven_control_tab = self.tabs.oven_control_tab  # shortcut
        # create menu bar
        self.menu_bar = MenuBar(self, instruments)
        self.setMenuBar(self.menu_bar)
        # secondary windows are stored here
        self.secondary_windows: list[QMainWindow] = []

        self.connect_signals()

    def connect_signals(self):
        """Connect widget signals."""
        # ensure the menubar responds to the popped graph being closed
        self.oven_control_tab.popped_graph.closed.connect(
            self.menu_bar.view.handle_popped_graph_destruction
        )
        self.tabs.currentChanged.connect(
            lambda *args: self.menu_bar.view.handle_tab_change(self.tabs)
        )

    # ----------------------------------------------------------------------------------------------
    # resizing
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def shrink(self):
        """Shrink the window to its minimum size. Exits fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        self.resize(self.minimumSize())

    # ----------------------------------------------------------------------------------------------
    # multiple windows
    def new_window(self, title: str, central_widget: QWidget) -> SecondaryWindow:
        """
        Create a new window owned by the main window. The window is automatically shown.

        :param title: The window title.
        :param central_widget: The widget to show inside the secondary window.
        :returns: The created window.
        """
        window = SecondaryWindow(title, central_widget)
        self.secondary_windows.append(window)
        window.closed.connect(lambda: self.secondary_windows.remove(window))
        window.show()
        return window

    # ----------------------------------------------------------------------------------------------
    # closing the window
    def closeEvent(self, event: QCloseEvent | None):  # overridden method
        """Prevent the window from closing if a sequence or stability check are running."""
        if event is not None:
            event.accept() if self.allowed_to_close() else event.ignore()

    def allowed_to_close(self) -> bool:
        """Determine if the window should close."""
        if self.oven_control_tab.stability_check_widget.is_running():
            message = "A stability check is currently running."
            signal = self.oven_control_tab.stability_check_widget.cancelStabilityCheck
        elif self.oven_control_tab.sequence_widget.is_running():
            message = "A sequence is currently running."
            signal = self.oven_control_tab.sequence_widget.cancelSequence
        else:
            return True  # we can close
        # this will run if either of the first two conditions triggered
        if YesCancelDialog("Are you sure you want to exit?", message).run():
            signal.emit()
            # NOTE: the below line forces PyQt to run all queued tasks (like handling signals), so
            # it will cancel whatever sequence is going. DO NOT use this in normal code. It is only
            # allowed here because we are about to close the application
            QApplication.processEvents()
            # wait until the sequence actually stops
            while (
                self.oven_control_tab.stability_check_widget.is_running()
                or self.oven_control_tab.sequence_widget.is_running()
            ):
                time.sleep(0.01)
            return True  # close
        return False  # do not close
