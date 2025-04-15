from PyQt6.QtCore import Qt, QModelIndex, QItemSelection, pyqtSignal, QThread
from PyQt6.QtGui import QKeyEvent, QDropEvent
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog, QSizePolicy
from .tree_view import TreeView
from ..tree_item import TreeItem
from ..tree_model import TreeModel
from ...custom_widgets.button import FixedButton
from ...custom_widgets.container import Container
from ...custom_widgets.button import BiggerButton
from ...custom_widgets.label import IconLabel
from ...custom_widgets.dialog import OkDialog
from ...classes.actions import Shortcut
from ...classes.signals import CommandSignals, GraphSignals
from ...enums.status import SequenceStatus
from ...utility.layouts import add_to_layout, add_sublayout
from ...utility.images import make_pixmap
from typing import Self
from ..sequence_runner import SequenceRunner
from ...instruments import InstrumentSet
from ... import Files


class SequenceTreeView(TreeView):
    """Custom TreeView for displaying sequence settings."""

    def __init__(self):
        # initialize the model
        model = TreeModel("Sequence Builder")
        model.set_supported_drag_actions(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        model.set_supported_drop_actions(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        # initialize the super class
        super().__init__(model)
        # configure
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.doubleClicked.connect(self.handle_double_click)

        self.connect_signals()
        self.create_shortcuts()

    def connect_signals(self):
        # expand the view when drops occur so it's easier to see what changed
        self.model().dropOccurred.connect(lambda index: self.expand(index))

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
    sequenceStatusChanged = pyqtSignal(SequenceStatus)
    graphSignalsChanged = pyqtSignal(GraphSignals)

    def __init__(self, instruments: InstrumentSet):
        """
        :param instruments: The application's instruments.
        :param tabs: The
        """
        super().__init__(QVBoxLayout())

        self.view: SequenceTreeView
        self.delete_button: FixedButton
        self.directory_button: BiggerButton
        self.directory_label: IconLabel
        self.create_widgets().connect_signals()

        self.instruments = instruments
        self.threads: list[SequenceRunner] = []

        self.command_signals = CommandSignals()
        self.graph_signals = GraphSignals()

    def create_widgets(self) -> Self:
        layout: QVBoxLayout = self.layout()  # type: ignore
        self.view = SequenceTreeView()
        self.delete_button = FixedButton("Delete Selected Items", self.view.delete_event)
        self.delete_button.setEnabled(False)
        add_to_layout(layout, self.delete_button, self.view)

        # the data directory selection widgets
        directory_layout = add_sublayout(layout, QHBoxLayout)
        self.directory_button = BiggerButton(
            "Choose Data Directory", self.choose_directory, size_scalars=(1, 2)
        )
        # let the button expand vertically
        self.directory_button.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        self.directory_label = IconLabel(make_pixmap("folder-open-document.png"))
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
            Files.SequenceRunner.DEFAULT_DATA_FOLDER,
            QFileDialog.Option.ShowDirsOnly,
        )
        self.directory_label.label().setText(directory)
        return self

    def data_directory(self) -> str:
        """Get the current data directory."""
        return self.directory_label.label().text()

    def is_running(self) -> bool:
        """Whether the sequence is currently running."""
        return len(self.threads) > 0

    def run_sequence(self) -> Self:
        """Run the sequence."""
        thread = QThread(self)
        runner = SequenceRunner(
            self.instruments, self.directory_label.label().text(), self.view.model().root()
        )
        runner.moveToThread(thread)
        self.connect_sequence_signals(runner, thread)
        # run
        thread.started.connect(runner.run)
        thread.start()
        return self

    def connect_sequence_signals(self, runner: SequenceRunner, thread: QThread) -> Self:
        # up towards the parent
        runner.info_signals.errorOccurred.connect(lambda message: OkDialog("Error", message).exec())
        runner.info_signals.currentItemChanged.connect(self.handle_item_change)
        runner.info_signals.statusChanged.connect(self.sequenceStatusChanged)
        self.graph_signals.connect_to_other(runner.graph_signals)
        # down towards the child
        self.command_signals.connect_to_other(runner.command_signals)
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
