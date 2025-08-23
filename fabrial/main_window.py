from collections.abc import Iterable

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget

from .constants import APP_NAME
from .custom_widgets import YesCancelDialog
from .custom_widgets.settings import ApplicationSettingsWindow
from .menu import MenuBar
from .secondary_window import SecondaryWindow
from .sequence_builder import CategoryItem
from .tabs import SequenceBuilderTab, SequenceDisplayTab, sequence_builder, sequence_display
from .utility import images


class MainWindow(QMainWindow):
    def __init__(
        self,
        category_items: Iterable[CategoryItem],
        settings_menu_widget: ApplicationSettingsWindow,
    ):
        self.should_relaunch = False
        QMainWindow.__init__(self)
        self.setWindowTitle(APP_NAME)
        # create menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        # settings menu
        self.settings_window = settings_menu_widget
        self.settings_window.relaunchRequested.connect(self.relaunch)
        # tabs
        self.sequence_visuals_tab = SequenceDisplayTab()
        self.sequence_tab = SequenceBuilderTab(
            self.sequence_visuals_tab, self.menu_bar.sequence, category_items
        )
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # looks better
        self.tab_widget.addTab(
            self.sequence_tab, images.make_icon(sequence_builder.ICON_FILENAME), "Sequence Builder"
        )
        self.tab_widget.addTab(
            self.sequence_visuals_tab,
            images.make_icon(sequence_display.ICON_FILENAME),
            "Sequence Visuals",
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
    # relaunching
    def relaunch(self):
        """Relaunch the application."""
        self.should_relaunch = True
        QApplication.quit()

    # ----------------------------------------------------------------------------------------------
    # closing the window
    def closeEvent(self, event: QCloseEvent | None):  # overridden method
        """Prevent the window from closing if a sequence is running."""
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
                "Close?", "A sequence is currently running. Cancel sequence and close?"
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

    # ----------------------------------------------------------------------------------------------
    # settings
    def show_settings(self):
        """Show the application settings. These settings are saved when the window closes."""
        self.settings_window.show()
