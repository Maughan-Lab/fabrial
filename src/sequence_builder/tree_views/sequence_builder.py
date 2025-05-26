import os
from dataclasses import dataclass
from typing import Self

from PyQt6.QtCore import QItemSelection, QModelIndex, QPoint, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragMoveEvent, QDropEvent, QKeyEvent
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox, QSizePolicy, QVBoxLayout

from ...classes.actions import Shortcut
from ...classes.process import AbstractProcess
from ...classes.runners import SequenceRunner
from ...classes.signals import CommandSignals, GraphSignals
from ...custom_widgets.augmented.button import BiggerButton, FixedButton
from ...custom_widgets.augmented.dialog import Dialog, OkDialog, YesCancelDontShowDialog
from ...custom_widgets.augmented.label import IconLabel
from ...custom_widgets.container import Container
from ...enums.status import SequenceStatus
from ...Files.Settings import Sequence as Settings
from ...utility.images import make_icon, make_pixmap
from ...utility.layouts import add_sublayout, add_to_layout
from ...utility.timers import Timer
from ..tree_item import TreeItem
from ..tree_model import TreeModel
from .tree_view import TreeView


@dataclass
class DragTracker:
    timer: Timer
    position: QPoint


class SequenceTreeView(TreeView):
    """Custom TreeView for displaying sequence settings."""

    def __init__(self):
        # initialize the super class
        model = TreeModel("Sequence Builder")
        super().__init__(model)
        # configure the model and view
        try:
            self.init_from_file(Settings.SEQUENCE_AUTOSAVE_FILE)
        except Exception:  # if we fail just don't load anything
            pass
        model.set_supported_drag_actions(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        model.set_supported_drop_actions(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        # configure
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        self.create_shortcuts()

        # used to expand expandable items when hovering over them
        point = QPoint()
        timer = Timer(self, 500, lambda: self.expand(self.indexAt(point)))
        timer.setSingleShot(True)
        self.drag_tracker = DragTracker(timer, point)

    def connect_signals(self):  # overridden
        super().connect_signals()
        self.model().itemAdded.connect(self.handle_new_item)

    def handle_new_item(self, index: QModelIndex):
        """Handle an item being added to the model."""
        self.expand(index)
        self.expand(index.parent())

    def create_shortcuts(self):
        Shortcut(
            self, "Ctrl+C", self.copy_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        Shortcut(
            self, "Ctrl+X", self.cut_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        Shortcut(
            self, "Ctrl+V", self.paste_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )

    # ----------------------------------------------------------------------------------------------
    def keyPressEvent(self, event: QKeyEvent | None):  # overridden
        if event is not None:
            index = self.currentIndex()
            match event.key():
                case Qt.Key.Key_Delete:  # delete the current item
                    self.delete_event()
                case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                    self.show_item_widget(index)
        super().keyPressEvent(event)

    def dropEvent(self, event: QDropEvent | None):  # overridden
        if event is not None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                event.setDropAction(Qt.DropAction.CopyAction)

            super().dropEvent(event)  # process the event

    def dragMoveEvent(self, event: QDragMoveEvent | None):  # overridden
        if event is not None:
            tracked_position = self.drag_tracker.position
            event_position = event.position().toPoint()
            tracked_position.setX(event_position.x())
            tracked_position.setY(event_position.y())
            self.drag_tracker.timer.start()
        super().dragMoveEvent(event)


class SequenceTreeWidget(Container):
    """SequenceTreeView with a delete button."""

    # signals that get emitted to other objects
    directoryChanged = pyqtSignal(bool)  # whether the selected directory is valid

    sequenceStatusChanged = pyqtSignal(SequenceStatus)
    graphSignalsChanged = pyqtSignal(GraphSignals)

    def __init__(self) -> None:
        super().__init__(QVBoxLayout())

        self.view: SequenceTreeView
        self.delete_button: FixedButton
        self.directory_button: BiggerButton
        self.directory_label: IconLabel
        self.create_widgets().connect_signals()

        self.threads: list[SequenceRunner] = []

        self.command_signals = CommandSignals()
        self.cancelCommand = self.command_signals.cancelCommand  # shortcut for external users

    def create_widgets(self) -> Self:
        layout: QVBoxLayout = self.layout()  # type: ignore

        self.view = SequenceTreeView()

        button_layout = QHBoxLayout()
        button_container = Container(button_layout)

        self.delete_button = FixedButton("Delete Selected Items", self.view.delete_event)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)

        button_sublayout = QHBoxLayout()
        self.save_button = FixedButton("Save", self.save_settings)
        self.save_button.setIcon(make_icon("script-export.png"))
        button_sublayout.addWidget(self.save_button)
        self.load_button = FixedButton("Load", self.load_settings)
        self.load_button.setIcon(make_icon("script-import.png"))
        button_sublayout.addWidget(self.load_button)

        button_layout.addWidget(self.delete_button, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addLayout(button_sublayout)

        add_to_layout(layout, button_container, self.view)

        # the data directory selection widgets
        directory_layout = add_sublayout(layout, QHBoxLayout)
        self.directory_button = BiggerButton(
            "Choose Data Directory", self.choose_directory, size_scalars=(1, 2)
        )
        # let the button expand vertically
        self.directory_button.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        self.directory_label = IconLabel(
            make_pixmap("folder--arrow.png"), self.read_previous_directory()
        )
        self.directory_label.label().setWordWrap(True)
        directory_layout.addWidget(self.directory_button)
        directory_layout.addWidget(self.directory_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        return self

    def connect_signals(self) -> Self:
        self.view.selectionModel().selectionChanged.connect(self.handle_selection_change)  # type: ignore
        return self

    def handle_selection_change(self, selected: QItemSelection, *args):
        enabled = True
        if selected.isEmpty():
            enabled = False
        else:
            for index in selected.indexes():
                if not index.isValid():
                    enabled = False
        self.delete_button.setEnabled(enabled)

    def choose_directory(self) -> Self:
        """Open a dialog to choose the data-storage directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select sequence data location",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly,
        )
        self.directory_label.label().setText(directory)
        self.directoryChanged.emit(self.directory_is_valid())
        return self

    def read_previous_directory(self) -> str:
        """Try to load the previously used directory."""
        try:
            with open(Settings.SEQUENCE_DIRECTORY_FILE, "r") as f:
                directory = f.read()
                return directory
        except Exception:
            return ""

    def directory_is_valid(self) -> bool:
        """Whether the directory text represents a valid directory."""
        return False if self.directory_label.label().text() == "" else True

    def save_on_close(self):
        """Call this when closing the application to save settings."""
        self.view.to_file(Settings.SEQUENCE_AUTOSAVE_FILE)
        directory = self.directory_label.label().text()
        with open(Settings.SEQUENCE_DIRECTORY_FILE, "w") as f:
            f.write(directory)

    def save_settings(self):
        """Save the sequence to a file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Select save file",
            os.path.join(os.path.expanduser("~"), "untitled.json"),
            "JSON files (*.json)",
        )
        if filename != "":
            self.view.to_file(filename)

    def load_settings(self):
        """Load a sequence from a file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select sequence file", filter="JSON files (*.json)"
        )
        if filename != "":
            self.view.init_from_file(filename)

    def data_directory(self) -> str:
        """Get the current data directory."""
        return self.directory_label.label().text()

    # ----------------------------------------------------------------------------------------------
    # running the sequence
    def is_running(self) -> bool:
        """Whether the sequence is currently running."""
        return len(self.threads) > 0

    def run_sequence(self) -> Self:
        """Run the sequence. Creates the data directory if it doesn't exist."""
        root_item = self.view.model().root()
        if not root_item.child_count() > 0:  # return early if there are no items to run
            return self

        directory = self.data_directory()
        os.makedirs(directory, exist_ok=True)

        if len(os.listdir(directory)) > 0:  # the directory isn't empty
            # ask the user if they are okay with writing to a non-empty directory
            if not YesCancelDontShowDialog(
                "Note",
                "Data directory is not empty, proceed?",
                Settings.NON_EMPTY_DIRECTORY_WARNING_FILE,
            ).run():
                return self

        thread = QThread(self)
        runner = SequenceRunner(directory, root_item)
        runner.moveToThread(thread)
        self.connect_sequence_signals(runner, thread)
        self.graphSignalsChanged.emit(runner.graphing_signals())
        # run
        thread.started.connect(runner.run)
        thread.start()
        return self

    def connect_sequence_signals(self, runner: SequenceRunner, thread: QThread) -> Self:
        """Connect signals before starting the sequence."""

        def handle_message_creation(
            message: str,
            name: str,
            buttons: QMessageBox.StandardButton,
            text_mapping: dict[QMessageBox.StandardButton, str],
            sender: AbstractProcess,
        ):
            """Handle a message being sent from the sequence runner."""
            dialog = Dialog(f"Message from {name}", message, buttons)
            for standard_button, text in text_mapping.items():
                button = dialog.button(standard_button)
                if button is not None:
                    button.setText(text)
            runner.send_response(dialog.exec(), sender)

        def handle_item_change(current: TreeItem | None, previous: TreeItem | None):
            """Handle the current sequence item changing."""
            if previous is not None:
                previous.set_running(False)
            if current is not None:
                current.set_running(True)
            self.view.update()

        def set_running(running: bool):
            """Adjust the view and directory button based on whether a sequence is running."""
            not_running = not running
            if running:
                self.view.clearSelection()
            self.view.model().set_enabled(not_running)
            self.view.setDragEnabled(not_running)
            self.view.setAcceptDrops(not_running)
            self.view.update()
            self.directory_button.setDisabled(running)
            self.load_button.setDisabled(running)

        def sequence_start_event():
            """This runs when the sequence starts."""
            set_running(True)
            self.view.expandAll()
            self.threads.append(runner)

        def sequence_end_event():
            """This runs when the sequence ends."""
            set_running(False)
            self.threads.remove(runner)

        # up towards the parent
        runner.errorOccurred.connect(
            lambda message, name: OkDialog(f"Error in {name}", message).exec()
        )
        runner.newMessageCreated.connect(handle_message_creation)
        runner.currentItemChanged.connect(handle_item_change)
        runner.statusChanged.connect(self.sequenceStatusChanged)
        # down towards the child
        self.command_signals.cancelCommand.connect(runner.cancel)
        self.command_signals.pauseCommand.connect(runner.pause)
        self.command_signals.unpauseCommand.connect(runner.unpause)
        self.command_signals.skipCommand.connect(runner.skip)
        # internal-only signals
        runner.finished.connect(thread.quit)
        thread.started.connect(sequence_start_event)
        thread.finished.connect(sequence_end_event)

        return self
