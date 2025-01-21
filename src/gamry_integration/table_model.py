from PyQt6.QtWidgets import QTableView, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize, pyqtSignal
from custom_widgets.dialog import OkDialog
from polars import col
import polars as pl
from enum import Enum
from instruments import Oven  # ../instruments.py


class Column(Enum):
    # TODO: finish adding the columns
    CYCLE = 0

    def __str__(self):
        """Get the column name."""
        match self:
            case Column.CYCLE:
                return "Cycle"


class PotentiostatModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.enabled = True
        self.parameter_data = self.generate_data()
        pass

    def generate_data(self) -> pl.DataFrame:
        # TODO: determine what columns need to be included in the table
        return pl.DataFrame()

    def save_data(self):
        """Write the sequence settings to a file."""
        pass

    def load_data(self):
        """Attempt to load previously saved sequency settings, showing a dialog on failure."""
        pass

    def disable(self):
        """Disable editing of this widget's data."""
        self.enabled = False

    def enable(self):
        """Enable editing of this widget's data."""
        self.enabled = True

    def is_enabled(self):
        """Is this widget's data editable?"""
        return self.enabled

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def rowCount(self, index: QModelIndex | None = None):
        return self.parameter_data.select(pl.len()).item()

    def columnCount(self, index: QModelIndex | None = None):
        return self.parameter_data.width

    def flags(self, index):
        if self.is_enabled():
            flags = Qt.ItemFlag.NoItemFlags
        else:
            flags = Qt.ItemFlag.ItemIsEnabled
            if index.column() > Column.CYCLE.value:
                flags |= Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable
        return flags

    def data(self, index, role):
        match role:
            case Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.EditRole:
                # return the item at the index to display it
                return str(self.parameter_data.item(index.row(), index.column()))

    def headerData(self, index, orientation, role):
        match role:
            case Qt.ItemDataRole.DisplayRole:
                match orientation:
                    case Qt.Orientation.Horizontal:
                        return str(self.parameter_data.columns[index])
                    case Qt.Orientation.Vertical:
                        return ""

    def setData(self, index, value, role):
        match role:
            case Qt.ItemDataRole.EditRole:
                try:
                    match index.column():
                        # TODO: add more cases for each column
                        case _:  # this should never run
                            return False
                except Exception:
                    return False
                self.parameter_data[index.row(), index.column()] = new_value
                self.layoutChanged.emit()
                return True
            case _:  # do nothing otherwise
                pass


class PotentiostatTable(QTableView):
    """
    **QTableView** widget with additional functions for sizing.
    """

    def __init__(self, model: PotentiostatModel):
        super().__init__()
        self.setModel(model)
        self.connect_signals()
        self.initialize_size_policies()

    def connect_signals(self):
        self.model().layoutChanged.connect(self.updateSize)

    def initialize_size_policies(self):
        # TODO: this is a clone
        # hide the vertical header
        self.verticalHeader().hide()
        # make the header columns as small as possible
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # center align the header text
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        # hide the horizontal scrollbar (we don't need it)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.updateSize()

    def getCurrentWidth(self) -> int:
        # TODO: this is a clone
        """Get the column width accounting for the scrollbar."""
        width = self.frameWidth() * 2

        model = self.model()
        if model is not None:
            if model.rowCount() > self.MAX_VISIBLE_ROWS:
                # this means the scrollbar is visible
                vertical_scrollbar = self.verticalScrollBar()
                if vertical_scrollbar is not None:
                    width += vertical_scrollbar.sizeHint().width()
            for i in range(model.columnCount()):
                width += self.columnWidth(i)

        return width

    def getCurrentHeight(self) -> int:
        # TODO: this is a clone
        """Get the current table height based on how many rows there are."""
        height = self.frameWidth() * 2

        horizontal_header = self.horizontalHeader()
        if horizontal_header is not None:
            height += horizontal_header.sizeHint().height()

        model = self.model()
        if model is not None:
            for i in range(model.columnCount()):
                height += self.rowHeight(i)

        return height

    def updateSize(self):
        # TODO: this is a clone
        """
        Update the table size to show either **MAX_VISIBLE_ROWS** rows or the current number of
        rows, whichever is smaller.
        """
        self.resizeColumnsToContents()
        self.setFixedSize(
            QSize(self.getCurrentWidth(), min(self.getCurrentHeight(), self.getMaxHeight()))
        )
