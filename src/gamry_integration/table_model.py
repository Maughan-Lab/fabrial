from PyQt6.QtWidgets import QTableView, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize, pyqtSignal
from custom_widgets.dialog import OkDialog
from polars import col
import polars as pl
from enum import Enum
from instruments import Oven  # ../instruments.py
from custom_widgets.tablemodel import TableModel
from custom_widgets.tableview import TableView


class Column(Enum):
    # TODO: finish adding the columns
    CYCLE = 0

    def __str__(self):
        """Get the column name."""
        match self:
            case Column.CYCLE:
                return "Cycle"


class EISTableModel(TableModel):
    def __init__(self):
        super().__init__()


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
