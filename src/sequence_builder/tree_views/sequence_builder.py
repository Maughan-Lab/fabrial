import os
from typing import Self

from PyQt6.QtCore import QItemSelection, QModelIndex, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDropEvent, QKeyEvent
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QSizePolicy, QVBoxLayout

from ... import Files
from ...classes.actions import Shortcut
from ...classes.runners import SequenceRunner
from ...classes.signals import CommandSignals, GraphSignals
from ...custom_widgets.button import BiggerButton, FixedButton
from ...custom_widgets.container import Container
from ...custom_widgets.dialog import OkDialog, YesCancelDontShowDialog
from ...custom_widgets.label import IconLabel
from ...enums.status import SequenceStatus
from ...utility.images import make_icon, make_pixmap
from ...utility.layouts import add_sublayout, add_to_layout
from ..tree_item import TreeItem
from ..tree_model import TreeModel
from .tree_view import TreeView


class SequenceTreeView(TreeView):
    """Custom TreeView for displaying sequence settings."""

    def __init__(self):
        # initialize the model
        model = TreeModel("Sequence Builder")
        model.init_from_file(Files.SavedSettings.Sequence.AUTOSAVE)
        model.set_supported_drag_actions(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        model.set_supported_drop_actions(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        # initialize the super class
        super().__init__(model)
        self.expandAll()
        # configure
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.doubleClicked.connect(self.handle_double_click)

        self.connect_signals()
        self.create_shortcuts()

    def connect_signals(self):
        # expand the view when drops occur so it's easier to see what changed
        self.model().dropOccurred.connect(self.expand)

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

    def handle_double_click(self, index: QModelIndex):
        """On a double click event."""
        self.model().item(index).show_widget()  # show the selected item's widget

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def keyPressEvent(self, event: QKeyEvent | None):
        if event is not None:
            index = self.currentIndex()
            model = self.model()
            match event.key():
                case Qt.Key.Key_Delete:  # delete the current item
                    self.delete_event()
                case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                    model.item(index).show_widget()
        super().keyPressEvent(event)

    def dropEvent(self, event: QDropEvent | None):
        if event is not None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                event.setDropAction(Qt.DropAction.CopyAction)

            super().dropEvent(event)  # process the event


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
            make_pixmap("folder-open-document.png"), self.read_previous_directory()
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
            Files.SequenceBuilder.DEFAULT_DATA_FOLDER,
            QFileDialog.Option.ShowDirsOnly,
        )
        self.directory_label.label().setText(directory)
        self.directoryChanged.emit(self.directory_is_valid())
        return self

    def read_previous_directory(self) -> str:
        """Try to load the previously used directory."""
        try:
            with open(Files.SavedSettings.Sequence.SEQUENCE_DIRECTORY, "r") as f:
                directory = f.read()
                return directory
        except Exception:
            return ""

    def directory_is_valid(self) -> bool:
        """Whether the directory text represents a valid directory."""
        return False if self.directory_label.label().text() == "" else True

    def save_on_close(self):
        """Call this when closing the application to save settings."""
        self.view.model().save_to_file(Files.SavedSettings.Sequence.AUTOSAVE)
        directory = self.directory_label.label().text()
        with open(Files.SavedSettings.Sequence.SEQUENCE_DIRECTORY, "w") as f:
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
            self.view.model().save_to_file(filename)

    def load_settings(self):
        """Load a sequence from a file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select sequence file", filter="JSON files (*.json)"
        )
        if filename != "":
            self.view.model().init_from_file(filename)

    def data_directory(self) -> str:
        """Get the current data directory."""
        return self.directory_label.label().text()

    # ----------------------------------------------------------------------------------------------
    # running the sequence
    def is_running(self) -> bool:
        """Whether the sequence is currently running."""
        return len(self.threads) > 0

    def run_sequence(self) -> Self:
        """Run the sequence."""
        root_item = self.view.model().root()
        if not root_item.child_count() > 0:  # return early if there are no items to run
            return self

        directory = self.data_directory()
        if len(os.listdir(directory)) > 0:  # the directory isn't empty
            # ask the user if they are okay with writing to a non-empty directory
            if not YesCancelDontShowDialog(
                "Note",
                "Data directory is not empty, proceed?",
                Files.SavedSettings.Sequence.NON_EMPTY_DIRECTORY_WARNING,
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
        # up towards the parent
        runner.errorOccurred.connect(
            lambda message: OkDialog(f"Error in {runner.current_item().name()}", message).exec()
        )
        runner.currentItemChanged.connect(self.handle_item_change)
        runner.statusChanged.connect(self.sequenceStatusChanged)
        # down towards the child
        self.command_signals.cancelCommand.connect(runner.cancel)
        self.command_signals.pauseCommand.connect(runner.pause)
        self.command_signals.unpauseCommand.connect(runner.unpause)
        self.command_signals.skipCommand.connect(runner.skip)
        # internal-only signals
        runner.finished.connect(thread.quit)
        thread.started.connect(lambda: self.sequence_start_event(runner))
        thread.finished.connect(lambda: self.sequence_end_event(runner))

        return self

    def handle_item_change(self, current: TreeItem | None, previous: TreeItem | None):
        if previous is not None:
            previous.set_running(False)
        if current is not None:
            current.set_running(True)
        self.view.update()

    def sequence_start_event(self, runner: SequenceRunner):
        """This runs when the sequence starts."""
        self.adjust_view_state(True)
        self.view.expandAll()
        self.view.clearSelection()

        self.threads.append(runner)

    def sequence_end_event(self, runner: SequenceRunner):
        """This runs when the sequence ends."""
        self.adjust_view_state(False)

        self.threads.remove(runner)

    def adjust_view_state(self, running: bool):
        """Adjust the view's visual state for the sequence."""
        self.view.setDisabled(running)
        self.directory_button.setDisabled(running)
