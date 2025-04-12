from PyQt6.QtCore import Qt, QModelIndex, QItemSelection, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QDropEvent
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog, QSizePolicy, QWidget
from .tree_view import TreeView
from ..tree_model import TreeModel
from ...custom_widgets.button import FixedButton
from ...custom_widgets.container import Container
from ...custom_widgets.button import BiggerButton
from ...custom_widgets.label import IconLabel
from ...custom_widgets.dialog import OkDialog
from ...classes.actions import Shortcut
from ...classes.process import Process, ProcessRunner
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
        self.setExpandsOnDoubleClick(False)
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
    processWidgetChanged = pyqtSignal(QWidget)
    sequenceStatusChanged = pyqtSignal(SequenceStatus)
    # internal signals
    pauseCommand = pyqtSignal()
    unpauseCommand = pyqtSignal()
    cancelCommand = pyqtSignal()
    skipCommand = pyqtSignal()

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

    def choose_directory(self):
        """Open a dialog to choose the data-storage directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select sequence data location",
            Files.SequenceRunner.DEFAULT_DATA_FOLDER,
            QFileDialog.Option.ShowDirsOnly,
        )
        self.directory_label.label().setText(directory)

    def data_directory(self) -> str:
        """Get the current data directory."""
        return self.directory_label.label().text()

    def run_sequence(self):
        """Run the sequence."""
        runner = SequenceRunner(
            self.instruments, self.directory_label.label().text(), self.view.model().root()
        )
        # connect the runner's signals
        runner.processChanged.connect(
            lambda new_process: self.handle_process_change(new_process, runner.process_runner())
        )
        runner.statusChanged.connect(self.handle_status_change)
        runner.errorOccurred.connect(lambda message: OkDialog("Error", message).exec())
        # connect internal signals to the runner
        self.pauseCommand.connect(runner.pause)
        self.unpauseCommand.connect(runner.unpause)
        self.cancelCommand.connect(runner.cancel)
        self.skipCommand.connect(runner.skip_current_process)
        # run
        runner.start()

    def handle_process_change(self, new_process: Process, runner: ProcessRunner):
        self.view.update()
        if new_process.WIDGET_TYPE is not None:
            widget = new_process.WIDGET_TYPE()
            runner.set_process_widget(widget)
            self.processWidgetChanged.emit(widget)
        else:
            self.processWidgetChanged.emit(None)

    def handle_status_change(self, status: SequenceStatus):
        running = status.is_running()
        self.view.set_readonly(running)
        self.view.clearSelection()
        self.directory_button.setDisabled(running)
        self.sequenceStatusChanged.emit(status)
