from PyQt6.QtWidgets import QTableView, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize, pyqtSignal
from custom_widgets.dialog import OkDialog
from polars import col
import polars as pl
from enum import Enum
from instruments import Oven  # ../instruments.py
from custom_widgets.tablemodel import TableModel
from custom_widgets.tableview import TableView


class DataNames(Enum):
    # TODO: finish adding the columns
    INITIAL_FREQUENCY = 0
    FINAL_FREQUENCY = 1
    POINTS_PER_DECADE = 2
    AC_VOLTAGE = 3
    DC_VOLTAGE = 4
    ESTIMATED_Z = 5
    OPTIMIZATION_MODE = 6
    # possibly unnecessary
    AREA = 7

    def __str__(self) -> str:
        """Get the column name."""
        match self:
            case DataNames.INITIAL_FREQUENCY:
                return "Initial\nFreq. (Hz)"
            case DataNames.FINAL_FREQUENCY:
                return "Final Freq. (Hz)"
            case DataNames.POINTS_PER_DECADE:
                return "Points/Decade"
            case DataNames.AC_VOLTAGE:
                return "AC Voltage\n(mV rms)"
            case DataNames.DC_VOLTAGE:
                return "DC Voltage (V)"
            case DataNames.OPTIMIZATION_MODE:
                return "Optimize for:"
            case DataNames.AREA:
                return "Area (cm^2)"
        return "ERROR"  # this should never run

    def default(self) -> int:
        match self:
            # TODO: get the actual default values
            case DataNames.INITIAL_FREQUENCY:
                return 0
            case DataNames.FINAL_FREQUENCY:
                return 0
            case DataNames.POINTS_PER_DECADE:
                return 10
            case DataNames.AC_VOLTAGE:
                return 20
            case DataNames.DC_VOLTAGE:
                return 0
            case DataNames.OPTIMIZATION_MODE:
                return 0
            case DataNames.AREA:
                return 1
        return -1  # this should never run


class EISTableModel(TableModel):
    def __init__(self):
        super().__init__()
        self.parameter_data = self.generate_data()

    def generate_data(self) -> pl.DataFrame:
        return pl.DataFrame({str(DataNames(i)): DataNames(i).default() for i in range(len(DataNames))})

    def disable(self):
        """Disable editing of this widget's data."""
        self.disable_rows(1)

    def enable(self):
        """Enable editing of this widget's data."""
        self.enable_all_rows()

    def is_enabled(self):
        """Is this widget's data editable?"""
        return self.disabled_row_index == 0

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def save_data(self):
        # TODO: implement
        pass

    def load_data(self):
        # TODO: implement
        pass

    def setData(self, index, value, role):
        # TODO: actually implement this instead of copying
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

    def flags(self, index):
        # TODO: actually implement this instead of copying
        if self.is_enabled():
            flags = Qt.ItemFlag.NoItemFlags
        else:
            flags = Qt.ItemFlag.ItemIsEnabled
            if index.column() > DataNames.CYCLE.value:
                flags |= Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable
        return flags
