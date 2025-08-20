from types import ModuleType
from typing import Mapping

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget

from .constants import APP_NAME
from .custom_widgets import TabWidget, YesCancelDialog
from .menu import MenuBar
from .secondary_window import SecondaryWindow
from .tabs import SequenceBuilderTab, SequenceDisplayTab
from .utility import images


class MainWindow(QMainWindow):
    def __init__(self, plugin_modules: Mapping[str, ModuleType]):
        self.relaunch = False
        QMainWindow.__init__(self)
        self.setWindowTitle(APP_NAME)
        # create menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        # self.settings_window = ApplicationSettingsWindow(self) # TODO: fix
        # tabs
        self.sequence_visuals_tab = SequenceDisplayTab()
        self.sequence_tab = SequenceBuilderTab(
            self.sequence_visuals_tab, self.menu_bar.sequence, plugin_modules
        )
        self.tab_widget = TabWidget(
            [
                (self.sequence_tab, "Sequence Builder", images.make_icon("script-block.png")),
                (self.sequence_visuals_tab, "Sequence Visuals", images.make_icon("chart.png")),
            ]
        )
        self.setCentralWidget(self.tab_widget)

        # secondary windows are stored here
        self.secondary_windows: list[QMainWindow] = []

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
        self.resize(self.sizeHint())

    # ----------------------------------------------------------------------------------------------
    # multiple windows
    def new_window(self, title: str, central_widget: QWidget) -> SecondaryWindow:
        """
        Create a new window owned by the main window. The window is automatically shown.

        Parameters
        ----------
        title
            The window title.
        central_widget
            The widget to show inside the secondary window.

        Returns
        -------
        The created window.
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
            if self.allowed_to_close():
                self.save_on_close()
                event.accept()
            else:
                event.ignore()

    def allowed_to_close(self) -> bool:
        """Determine if the window should close."""
        # only close if a sequence is not running, otherwise ask to cancel the sequence
        if self.sequence_tab.is_running_sequence():
            if YesCancelDialog(
                "Are you sure you want to exit?", "A sequence is currently running."
            ).run():
                self.sequence_tab.cancel_sequence()
                while self.sequence_tab.is_running_sequence():
                    QApplication.processEvents()
                return True
            else:
                return False

        return True

    def save_on_close(self):
        """Save all data that gets saved on closing. Call this when closing the application."""
        self.sequence_tab.save_on_close()

    def should_relaunch(self) -> bool:
        """Whether the application should relaunch."""
        return self.relaunch

    def set_relaunch(self, should_relaunch: bool):
        """Set whether the application should relaunch."""
        self.relaunch = should_relaunch

    # ----------------------------------------------------------------------------------------------
    # settings
    def show_settings(self):
        """Show the application settings. These settings are saved when the window closes."""
        return
        # self.settings_window.show()
