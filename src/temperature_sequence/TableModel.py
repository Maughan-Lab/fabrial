from PyQt6.QtCore import Qt, QAbstractTableModel, QSize
from PyQt6.QtWidgets import QTableView, QHeaderView
from polars import col
import polars as pl
from .constants import (
    CYCLE_COLUMN,
    TEMPERATURE_COLUMN,
    BUFFER_HOURS_COLUMN,
    BUFFER_MINUTES_COLUMN,
    HOLD_HOURS_COLUMN,
    HOLD_MINUTES_COLUMN,
)
from instruments import Oven  # ../instruments.py


class TableModel(QAbstractTableModel):
    """
    Concrete version of a QAbstractTableModel for working with **Polars** **DataFrames**.
    """

    def __init__(self, data: pl.DataFrame):
        super().__init__()
        self.parameters = data

    def rowCount(self, index):
        return self.parameters.select(pl.len()).item()

    def columnCount(self, index):
        return self.parameters.width

    def flags(self, index):
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if index.column() > 0:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def data(self, index, role):
        match role:
            case Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.EditRole:
                # return the item at the index to display it
                return str(self.parameters.item(index.row(), index.column()))
            case _:  # TODO: implement other ItemDataRoles
                pass

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        match role:
            case Qt.ItemDataRole.DisplayRole:
                match orientation:
                    case Qt.Orientation.Horizontal:
                        return str(self.parameters.columns[section])
                    case Qt.Orientation.Vertical:
                        return str(self.parameters.select(col(CYCLE_COLUMN)).item(section, 0))
            case _:
                pass

    def setData(self, index, value, role):
        match role:
            case Qt.ItemDataRole.EditRole:
                try:
                    match index.column():
                        case 1:  # TEMPERATURE_COLUMN
                            new_value = round(float(value), 1)
                            # MINIMUM_TEMPERATURE <= temperature <= MAXIMUM_TEMPERATURE
                            if new_value > Oven.MAXIMUM_TEMPERATURE:
                                new_value = Oven.MAXIMUM_TEMPERATURE
                            elif new_value < Oven.MINIMUM_TEMPERATURE:
                                new_value = Oven.MINIMUM_TEMPERATURE
                        case 2 | 4:  # BUFFER_HOURS_COLUMN or HOLD_HOURS_COLUMN
                            new_value = int(float(value))
                            # hours >= 0
                            if new_value < 0:
                                new_value = 0
                        case 3 | 5:  # BUFFER_MINUTES_COLUMN or HOLD_MINUTES_COLUMN
                            new_value = int(float(value))
                            # 0 =< minutes =< 59
                            if new_value < 0:
                                new_value = 0
                            elif new_value > 59:
                                new_value = 59
                        case _:  # this should never run
                            return False
                except Exception:
                    return False
                self.parameters[index.row(), index.column()] = new_value
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
                return True


class TableView(QTableView):
    """
    **QTableView** widget with additional functions for sizing.
    """

    MAX_VISIBLE_ROWS = 5

    def __init__(self):
        super().__init__()
        self.verticalHeader().hide()  # hide the vertical header
        # make the header columns as small as possible
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # center align the header text
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        # hide the horizontal scrollbar (we don't need it)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def getCurrentWidth(self) -> int:
        """
        Get the column width accounting for the scrollbar.
        """
        width = self.frameWidth() * 2
        if self.model().rowCount(None) > self.MAX_VISIBLE_ROWS:
            # this means the scrollbar is visible
            width += self.verticalScrollBar().sizeHint().width()
        for i in range(self.model().columnCount(None)):
            width += self.columnWidth(i)
        return width

    def getMaxHeight(self) -> int:
        """
        Get the maximum height, dictated by **MAX_VISIBLE_ROWS**.
        """
        height = (
            self.frameWidth() * 2
            + self.horizontalHeader().sizeHint().height()
            + self.rowHeight(0) * self.MAX_VISIBLE_ROWS
        )
        return height

    def getCurrentHeight(self) -> int:
        """
        Get the current table height based on how many rows there are.
        """
        height = self.frameWidth() * 2 + self.horizontalHeader().sizeHint().height()
        for i in range(self.model().columnCount(None)):
            height += self.rowHeight(i)
        return height

    def updateSize(self):
        """
        Update the table size to show either **MAX_VISIBLE_ROWS** rows or the current number of
        rows, whichever is smaller.
        """
        self.setFixedSize(
            QSize(self.getCurrentWidth(), min(self.getCurrentHeight(), self.getMaxHeight()))
        )

    def dataChanged(self, topLeft, bottomRight, roles):
        self.resizeColumnsToContents()
        # TODO: figure out if this is even necessary
