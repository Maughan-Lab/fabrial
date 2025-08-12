import json
import os
from dataclasses import dataclass
from os import PathLike
from typing import Mapping, Self, Sequence

from PyQt6.QtCore import (
    QItemSelection,
    QModelIndex,
    QPersistentModelIndex,
    QPoint,
    Qt,
    QThread,
    pyqtSignal,
)
from PyQt6.QtGui import QDragMoveEvent, QKeyEvent
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox, QSizePolicy, QVBoxLayout

from ...classes import (
    AbstractProcess,
    CommandSignals,
    GraphSignals,
    SequenceRunner,
    Shortcut,
    Timer,
)
from ...constants.paths.settings import sequence as sequence_paths
from ...custom_widgets import (
    BiggerButton,
    Container,
    Dialog,
    FixedButton,
    IconLabel,
    OkDialog,
    YesCancelDontShowDialog,
)
from ...enums import SequenceStatus
from ...utility import images, layout as layout_util
from ...utility.serde import Json
from ..tree_items.tree_item import TreeItem
from ..tree_models import SequenceModel
from .tree_view import TreeView

ITEM_DATA = "items"
VIEW_DATA = "view_state"


@dataclass
class DragTracker:
    timer: Timer
    position: QPoint


class SequenceTreeView(TreeView[SequenceModel]):
    """
    Custom `TreeView` for displaying sequence settings.

    Parameters
    ----------
    model
        The model the view will use.
    """

    def __init__(self, model: SequenceModel):
        TreeView.__init__(self, model)
        # configure
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        # used to expand items when hovering over them
        point = QPoint()
        timer = Timer(self, 500, lambda: self.expand(self.indexAt(point)))
        timer.setSingleShot(True)
        self.drag_tracker = DragTracker(timer, point)

    @classmethod
    def from_json(cls, file: PathLike[str] | str) -> Self:
        model = SequenceModel([])
        return cls(model).init_from_json(file)

    def init_from_json(self, file: PathLike[str] | str) -> Self:
        """Initialize the items from a JSON file."""
        try:
            with open(file, "r") as f:
                data: Mapping[str, Sequence[Mapping[str, Json]]] = json.load(f)
            self.model().init_from_jsonlike(data[ITEM_DATA])
            self.init_view_state(data[VIEW_DATA])
        except Exception:  # if we fail just don't load anything
            pass
        return self

    def to_json(self, file: PathLike[str] | str) -> bool:
        """Save to a JSON file. Returns whether the operation succeeded."""
        try:
            data: dict[str, Sequence[Json]] = {}
            data[ITEM_DATA] = self.model().to_jsonlike()
            data[VIEW_DATA] = self.get_view_state()
            with open(file, "w") as f:
                json.dump(data, f)
            return True
        except Exception:
            return False

    def connect_signals(self):  # overridden
        TreeView.connect_signals(self)
        self.model().itemAdded.connect(self.handle_new_item)

    def items_editable(self) -> bool:  # overridden
        return True  # TODO: make this depend on whether the widget is enabled

    def handle_new_item(self, index: QModelIndex):
        """Handle an item being added to the model."""
        self.expand(index)  # expand the new item
        self.expand(index.parent())  # and its parent

    def create_shortcuts(self):  # overridden
        TreeView.create_shortcuts(self)
        Shortcut(
            self, "Ctrl+X", self.cut_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        Shortcut(
            self, "Ctrl+V", self.paste_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )

    def cut_event(self):
        """Move items to the clipboard."""
        self.copy_event()
        self.delete_event()

    def paste_event(self):
        """Paste items from the clipboard after the currently selected item."""
        self.model().paste_items(self.currentIndex())

    def delete_event(self):
        """Delete currently selected items."""
        # store the index below the current index
        persistent_new_selection_index = QPersistentModelIndex(self.indexBelow(self.currentIndex()))

        self.model().delete_items(self.selectedIndexes())

        # select the next available item after deleting
        new_selection_index = QModelIndex(persistent_new_selection_index)
        if not new_selection_index.isValid():
            # try the item below the currently selected item
            new_selection_index = self.indexBelow(self.currentIndex())
            if not new_selection_index.isValid():
                # try whatever is currently selected (usually the last item in this situation)
                new_selection_index = self.currentIndex()
                if not new_selection_index.isValid():
                    # at this point there should be no items in the model
                    self.clearSelection()

        self.setCurrentIndex(new_selection_index)

    # ----------------------------------------------------------------------------------------------
    def keyPressEvent(self, event: QKeyEvent | None):  # overridden
        if event is not None:
            match event.key():
                case Qt.Key.Key_Delete:  # delete the current item
                    self.delete_event()
                case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                    self.open_event(self.selectedIndexes())
        TreeView.keyPressEvent(self, event)

    def dragMoveEvent(self, event: QDragMoveEvent | None):  # overridden
        if event is not None:
            tracked_position = self.drag_tracker.position
            event_position = event.position().toPoint()
            tracked_position.setX(event_position.x())
            tracked_position.setY(event_position.y())
            self.drag_tracker.timer.start()
        TreeView.dragMoveEvent(self, event)


class SequenceTreeWidget(Container):
    """SequenceTreeView with a delete button."""

    # signals that get emitted to other objects
    directoryChanged = pyqtSignal(bool)  # whether the selected directory is valid

    sequenceStatusChanged = pyqtSignal(SequenceStatus)
    graphSignalsChanged = pyqtSignal(GraphSignals)

    def __init__(self, view: SequenceTreeView):
        layout = QVBoxLayout()
        Container.__init__(self, layout)

        self.view = view
        self.delete_button: FixedButton
        self.directory_button: BiggerButton
        self.directory_label: IconLabel
        self.create_widgets(layout)
        self.connect_signals()

        self.threads: list[SequenceRunner] = []

        self.command_signals = CommandSignals()
        self.cancelCommand = self.command_signals.cancelCommand  # shortcut for external users

    @classmethod
    def from_json(cls, file: PathLike[str] | str) -> Self:
        view = SequenceTreeView.from_json(file)
        return cls(view)

    def create_widgets(self, layout: QVBoxLayout) -> Self:
        button_layout = QHBoxLayout()
        button_container = Container(button_layout)

        self.delete_button = FixedButton("Delete Selected Items", self.view.delete_event)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)

        button_sublayout = QHBoxLayout()
        self.save_button = FixedButton("Save", self.save_settings)
        self.save_button.setIcon(images.make_icon("script-export.png"))
        button_sublayout.addWidget(self.save_button)
        self.load_button = FixedButton("Load", self.load_settings)
        self.load_button.setIcon(images.make_icon("script-import.png"))
        button_sublayout.addWidget(self.load_button)

        button_layout.addWidget(self.delete_button, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addLayout(button_sublayout)

        layout_util.add_to_layout(layout, button_container, self.view)

        # the data directory selection widgets
        directory_layout = layout_util.add_sublayout(layout, QHBoxLayout())
        self.directory_button = BiggerButton(
            "Choose Data Directory", self.choose_directory, size_scalars=(1.5, 2)
        )
        self.directory_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.directory_label = IconLabel(
            images.make_pixmap("folder--arrow.png"), self.read_previous_directory()
        )
        self.directory_label.label().setWordWrap(True)
        directory_layout.addWidget(self.directory_button)
        directory_layout.addWidget(self.directory_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        return self

    def connect_signals(self) -> Self:
        self.view.selectionModel().selectionChanged.connect(  # type: ignore
            self.handle_selection_change
        )
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

    def directory_is_valid(self):
        """Whether the selected directory is valid."""
        return self.directory_label.label().text() != ""

    def read_previous_directory(self) -> str:
        """Try to load the previously used directory."""
        try:
            with open(sequence_paths.SEQUENCE_DIRECTORY_FILE, "r") as f:
                directory = f.read()
                return directory
        except Exception:
            return ""

    def save_on_close(self):
        """Call this when closing the application to save settings."""
        self.view.to_json(sequence_paths.SEQUENCE_AUTOSAVE_FILE)
        directory = self.data_directory()
        with open(sequence_paths.SEQUENCE_DIRECTORY_FILE, "w") as f:
            f.write(directory)

    def save_settings(self):
        """Save the sequence to a file."""
        file = QFileDialog.getSaveFileName(
            self,
            "Select save file",
            os.path.join(os.path.expanduser("~"), "untitled.json"),
            "JSON files (*.json)",
        )[0]
        if file != "":
            self.view.to_json(file)

    def load_settings(self):
        """Load a sequence from a file."""
        file = QFileDialog.getOpenFileName(
            self, "Select sequence file", filter="JSON files (*.json)"
        )[0]
        if file != "":
            self.view.init_from_json(file)

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
        if not root_item.subitem_count() > 0:  # return early if there are no items to run
            return self

        directory = self.data_directory()
        os.makedirs(directory, exist_ok=True)

        if len(os.listdir(directory)) > 0:  # the directory isn't empty
            # ask the user if they are okay with writing to a non-empty directory
            if not YesCancelDontShowDialog(
                "Note",
                "Data directory is not empty, proceed?",
                sequence_paths.NON_EMPTY_DIRECTORY_WARNING_FILE,
            ).run():
                return self

        # save the sequence settings automatically
        self.view.to_json(os.path.join(directory, "autosave.json"))

        thread = QThread(self)
        # TODO: change SequenceRunner to accept Path
        runner = SequenceRunner(str(directory), root_item)
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
            # TODO: fix
            return
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
