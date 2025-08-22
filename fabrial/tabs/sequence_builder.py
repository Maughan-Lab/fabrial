import json
import os
import typing
from collections.abc import Iterable
from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QFileDialog, QGridLayout, QHBoxLayout, QSizePolicy, QStackedWidget

from ..classes import SequenceRunner
from ..constants.paths.settings import sequence as sequence_paths
from ..custom_widgets import Button, IconLabel, Label, Widget
from ..enums import SequenceStatus
from ..menu import SequenceMenu
from ..sequence_builder import CategoryItem, OptionsTreeWidget, SequenceTreeWidget
from ..utility import errors, images
from .sequence_display import SequenceDisplayTab

ICON_FILENAME = "script-block.png"


class SequenceBuilderTab(Widget):
    """
    Sequence tab.

    Parameters
    ----------
    visuals_tab
        The tab where plots are shown for sequence steps.
    menu
        The `QMenu` that holds sequence controls.
    plugin_modules
        A list of loaded plugin modules.
    """

    def __init__(
        self,
        visuals_tab: SequenceDisplayTab,
        menu: SequenceMenu,
        category_items: Iterable[CategoryItem],
    ):
        layout = QGridLayout()
        Widget.__init__(self, layout)

        self.sequence_runner: SequenceRunner | None = None  # have to keep a reference to the runner

        self.visuals_tab = visuals_tab  # another tab
        self.menu = menu

        self.options_tree_widget = OptionsTreeWidget.from_items(category_items)
        self.sequence_tree_widget = SequenceTreeWidget.from_autosave()

        self.directory_button = Button("Choose Data Directory", self.choose_directory)
        self.directory_label = IconLabel(
            images.make_pixmap("folder--arrow.png"), self.load_previous_directory()
        )

        self.button_layout = QStackedWidget()
        self.start_button = Button("Start", self.start_sequence)
        self.pause_button = Button("Pause")
        self.unpause_button = Button("Unpause")
        self.status_label = Label("Inactive").set_color("gray")

        self.arrange_widgets(layout)

    def arrange_widgets(self, layout: QGridLayout):
        """Arrange widgets at construction."""
        layout.addWidget(self.options_tree_widget, 0, 0)
        layout.addWidget(self.sequence_tree_widget, 0, 1)
        layout.setRowStretch(0, 1)

        BUTTON_SIZE = QSize(250, 50)

        # data directory widgets
        directory_layout = QHBoxLayout()
        layout.addLayout(directory_layout, 1, 0)
        self.directory_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.directory_button.setMinimumSize(BUTTON_SIZE)
        self.directory_label.label().setWordWrap(True)
        directory_layout.addWidget(self.directory_button)
        directory_layout.addWidget(self.directory_label)

        # start/pause button and status label
        runner_layout = QHBoxLayout()
        layout.addLayout(runner_layout, 1, 1)
        # buttons
        self.button_layout.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.button_layout.setMinimumSize(BUTTON_SIZE)
        runner_layout.addWidget(self.button_layout)
        self.start_button.setEnabled(self.directory_is_valid())
        for button in [self.start_button, self.pause_button, self.unpause_button]:
            self.button_layout.addWidget(button)
        # label
        font = self.status_label.font()
        font.setPointSize(16)
        self.status_label.setFont(font)
        runner_layout.addWidget(self.status_label)

    def choose_directory(self):
        """Open a dialog to choose the data-storage directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select sequence data location",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly,
        )
        self.directory_label.label().setText(directory)  # update label

        self.start_button.setEnabled(directory != "")  # enable/disable start button

    def directory_is_valid(self):
        """Whether the selected directory is valid."""
        return self.directory_label.label().text() != ""

    def load_previous_directory(self) -> str:
        """Try to load the previously used directory."""
        try:
            with open(sequence_paths.SEQUENCE_DIRECTORY_FILE, "r") as f:
                directory = typing.cast(str, json.load(f))
                return directory
        except Exception:
            return ""

    def data_directory(self) -> str:
        """Get the current data directory."""
        return self.directory_label.label().text()

    def save_on_close(self):
        """Call this when closing the application to save settings."""
        self.options_tree_widget.save_on_close()
        self.sequence_tree_widget.save_on_close()

        directory = self.data_directory()
        try:
            with open(sequence_paths.SEQUENCE_DIRECTORY_FILE, "w") as f:
                json.dump(directory, f)
        except OSError:
            pass

    # ----------------------------------------------------------------------------------------------
    # sequence
    def start_sequence(self):
        sequence_runner = SequenceRunner()
        self.pause_button.clicked.connect(sequence_runner.pause)
        self.unpause_button.clicked.connect(sequence_runner.unpause)
        self.menu.cancel.triggered.connect(sequence_runner.cancel)
        if sequence_runner.run_sequence(
            self, self.sequence_tree_widget.view.model(), Path(self.data_directory())
        ):
            self.handle_sequence_state_change(True)
            # store a reference to the sequence runner
            self.sequence_runner = sequence_runner

    def handle_sequence_status_change(self, status: SequenceStatus):
        """Handle the sequence's status changing."""
        match status:
            case SequenceStatus.Active:
                text = "Active"
                color = "green"
                button = self.pause_button

            case SequenceStatus.Paused:
                text = "Paused"
                color = "cyan"
                button = self.unpause_button

            case SequenceStatus.Completed:
                text = "Completed"
                color = "gray"
                button = self.start_button

            case SequenceStatus.Cancelled:
                text = "Cancelled"
                color = "gray"
                button = self.start_button

            case SequenceStatus.FatalError:
                text = "Fatal Error"
                color = "red"
                button = self.start_button
                # notify the user
                errors.show_error_delayed(
                    "Sequence: Fatal Error",
                    "The sequence encountered a fatal error and was terminated. "
                    "See the error log for details.",
                )
            case _:  # this should never run
                raise ValueError(f"Unknown `SequenceStatus`: {status}")

        self.button_layout.setCurrentWidget(button)
        self.status_label.setText(text)
        self.status_label.set_color(color)

    def handle_sequence_state_change(self, running: bool):
        """Handle the sequence starting/stopping."""
        self.menu.cancel.setEnabled(running)
        self.directory_button.setEnabled(not running)
        self.start_button.setEnabled(not running)  # make sure the user can't spam the start button
        self.sequence_tree_widget.set_readonly(running)  # disable editing the items
        if not running:
            self.sequence_runner = None  # delete the runner

    def is_running_sequence(self) -> bool:
        """Whether a sequence is currently being run."""
        return self.sequence_runner is not None

    def cancel_sequence(self):
        """Cancel the sequence."""
        if self.sequence_runner is not None:
            self.sequence_runner.cancel()
