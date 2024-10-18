from PyQt6.QtCore import Qt, QAbstractTableModel
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


class TableModel(QAbstractTableModel):
    """
    Concrete version of a QAbstractTableModel for working with **Polars** **DataFrames**.
    """

    def __init__(self, data: pl.DataFrame):
        super().__init__()
        self.parameters = data

    def data(self, index, role):
        match role:
            case Qt.ItemDataRole.DisplayRole:
                # return the item at the index to display it
                return str(
                    self.parameters.select(pl.exclude(CYCLE_COLUMN)).item(
                        index.row(), index.column()
                    )
                )
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
                        return str(self.parameters.select(col(CYCLE_COLUMN)).item(section))
                        pass
            case _:
                pass

        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])

    def rowCount(self, index):
        return self.parameters.select(pl.len()).item()

    def columnCount(self, index):
        return self.parameters.width
