from PyQt6.QtWidgets import QTableView, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize, pyqtSignal
from custom_widgets.dialog import OkDialog
from polars import col
import polars as pl
from enum import Enum
from .constants import (
    CYCLE_COLUMN,
    TEMPERATURE_COLUMN,
    BUFFER_HOURS_COLUMN,
    BUFFER_MINUTES_COLUMN,
    HOLD_HOURS_COLUMN,
    HOLD_MINUTES_COLUMN,
    SAVED_SETTINGS_FILE,
)
from instruments import Oven  # ../instruments.py


class Column(Enum):
    CYCLE = 0
    TEMPERATURE = 1
    BUFFER_HOURS = 2
    BUFFER_MINUTES = 3
    HOLD_HOURS = 4
    HOLD_MINUTES = 5


class TableModel(QAbstractTableModel):
    """Concrete version of a QAbstractTableModel for working with **Polars** **DataFrame**s."""

    # signals
    dataLoaded = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.parameter_data = self.generate_new_rows(1, 1)
        self.disabled_row_index = 0  # rows before this index are disabled

    def save_data(self):
        """Write the sequence settings to a file."""
        self.parameter_data.write_csv(SAVED_SETTINGS_FILE)

    def load_data(self):
        """Attempt to load previously saved sequency settings, showing a dialog on failure."""
        try:
            self.parameter_data = pl.scan_csv(SAVED_SETTINGS_FILE).collect()
        except Exception:
            OkDialog("Error", "Unable to load saved settings.").exec()
            return
        self.dataLoaded.emit(self.rowCount())
        self.layoutChanged.emit()

    def resize(self, new_row_count: int):
        """
        Updates the model's size based on **new_row_count**.

        :param new_row_count: The new row count of the model.
        """
        current_row_count = self.rowCount(None)
        difference = new_row_count - current_row_count
        if difference > 0:
            self.parameter_data = pl.concat(
                [self.parameter_data, self.generate_new_rows(current_row_count + 1, difference)],
                how="vertical",
            )
        else:
            self.parameter_data = self.parameter_data.filter(col(CYCLE_COLUMN) <= new_row_count)
        self.layoutChanged.emit()

    def generate_new_rows(self, starting_cycle_number: int, row_count: int) -> pl.DataFrame:
        """
        Generates and returns **row_count** new rows.

        :param starting_cycle_number: The number the row cycle numbers will start at.
        :param row_count: The number of rows to generate.
        """
        cycles = [i for i in range(starting_cycle_number, starting_cycle_number + row_count)]
        times = [0 for i in range(row_count)]
        temperatures = [Oven.MINIMUM_TEMPERATURE for i in range(row_count)]
        new_rows = pl.DataFrame(
            {
                CYCLE_COLUMN: cycles,
                TEMPERATURE_COLUMN: temperatures,
                BUFFER_HOURS_COLUMN: times,
                BUFFER_MINUTES_COLUMN: times,
                HOLD_HOURS_COLUMN: times,
                HOLD_MINUTES_COLUMN: times,
            }
        )
        return new_rows

    def disable_rows(self, disable_rows_at_and_before: int):
        """
        Disables rows in the ModelView.

        :param disable_rows_at_and_before: Which rows to disable. For example, setting this to **3**
        will disable rows 1, 2, and 3.
        """
        self.disabled_row_index = disable_rows_at_and_before

    def enable_all_rows(self):
        """Enable all rows in the model."""
        self.disabled_row_index = 0

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def rowCount(self, index: QModelIndex | None = None):
        return self.parameter_data.select(pl.len()).item()

    def columnCount(self, index: QModelIndex | None = None):
        return self.parameter_data.width

    def flags(self, index):
        if index.row() < self.disabled_row_index:
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
                        return str(self.parameter_data.select(col(CYCLE_COLUMN)).item(index, 0))

    def setData(self, index, value, role):
        match role:
            case Qt.ItemDataRole.EditRole:
                try:
                    match index.column():
                        case Column.TEMPERATURE.value:
                            new_value = round(float(value), 1)
                            # MINIMUM_TEMPERATURE <= temperature <= MAXIMUM_TEMPERATURE
                            if new_value > Oven.MAXIMUM_TEMPERATURE:
                                new_value = Oven.MAXIMUM_TEMPERATURE
                            elif new_value < Oven.MINIMUM_TEMPERATURE:
                                new_value = Oven.MINIMUM_TEMPERATURE
                        case Column.BUFFER_HOURS.value | Column.HOLD_HOURS.value:
                            new_value = int(float(value))
                            # hours >= 0
                            if new_value < 0:
                                new_value = 0
                        case Column.BUFFER_MINUTES.value | Column.HOLD_MINUTES.value:
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
                self.parameter_data[index.row(), index.column()] = new_value
                self.layoutChanged.emit()
                return True
            case _:  # do nothing otherwise
                pass


class TableView(QTableView):
    """
    **QTableView** widget with additional functions for sizing.
    """

    MAX_VISIBLE_ROWS = 5

    def __init__(self, model: TableModel):
        super().__init__()
        self.setModel(model)
        self.connect_signals()
        self.initialize_size_policies()

    def connect_signals(self):
        self.model().layoutChanged.connect(self.updateSize)

    def initialize_size_policies(self):
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

    def getMaxHeight(self) -> int:
        """Get the maximum height, dictated by **MAX_VISIBLE_ROWS**."""
        height = self.frameWidth() * 2

        horizontal_header = self.horizontalHeader()
        if horizontal_header is not None:
            height += horizontal_header.sizeHint().height()

        for i in range(self.MAX_VISIBLE_ROWS):
            height += self.rowHeight(i)
        return height

    def getCurrentHeight(self) -> int:
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
        """
        Update the table size to show either **MAX_VISIBLE_ROWS** rows or the current number of
        rows, whichever is smaller.
        """
        self.resizeColumnsToContents()
        self.setFixedSize(
            QSize(self.getCurrentWidth(), min(self.getCurrentHeight(), self.getMaxHeight()))
        )
