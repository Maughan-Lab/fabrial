from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
import polars as pl

# TODO: remove this


class TableModel(QAbstractTableModel):
    """Partial implementation of a QAbstractTableModel."""

    def __init__(self):
        super().__init__()
        self.disabled_row_index = 0  # rows *before* this index are disabled
        self.parameter_data = pl.DataFrame()

    def disable_rows(self, disable_rows_at_and_before: int):
        """
        Disables rows in the model.

        :param disable_rows_at_and_before: Which rows to disable. For example, setting this to **3**
        will disable rows 1, 2, and 3.
        """
        self.disabled_row_index = disable_rows_at_and_before

    def enable_all_rows(self):
        """Enable all rows in the model."""
        self.disabled_row_index = 0

    def rowCount(self, index: QModelIndex | None = None):
        """Qt method. Get the number of rows in the DataFrame."""
        return self.parameter_data.select(pl.len()).item()

    def columnCount(self, index: QModelIndex | None = None):
        """Qt method. Get the number of columns in the DataFrame."""
        return self.parameter_data.width

    def data(self, index, role):
        """Qt method."""
        match role:
            case Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.EditRole:
                # return the item at the index to display it
                return str(self.parameter_data.item(index.row(), index.column()))

    def headerData(self, index, orientation, role):
        """Qt method."""
        match role:
            case Qt.ItemDataRole.DisplayRole:
                match orientation:
                    case Qt.Orientation.Horizontal:
                        return str(self.parameter_data.columns[index])
                    case _:
                        return ""

    def setData(self, index, value, role):
        """Qt method. Override this method."""

    def flags(self, index):
        """Qt method. Override this method."""
        pass

    def save_data(self):
        """Override this method."""
        pass

    def load_data(self):
        """Override this method."""
        pass
