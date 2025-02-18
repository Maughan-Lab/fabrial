from PyQt6.QtCore import Qt, pyqtSignal
from custom_widgets.dialog import OkDialog
from custom_widgets.tablemodel import TableModel
from polars import col
import polars as pl
from enum import Enum
import Files


from instruments import Oven  # ../instruments.py


class Column(Enum):
    CYCLE = 0
    TEMPERATURE = 1
    BUFFER_HOURS = 2
    BUFFER_MINUTES = 3
    HOLD_HOURS = 4
    HOLD_MINUTES = 5

    def __str__(self):
        """Return the name of the column as a string."""
        match self:
            case Column.CYCLE:
                return "Cycle"
            case Column.TEMPERATURE:
                return "Temp"
            case Column.BUFFER_HOURS:
                return "Buffer\nHours"
            case Column.BUFFER_MINUTES:
                return "Buffer\nMinutes"
            case Column.HOLD_HOURS:
                return "Hold\nHours"
            case Column.HOLD_MINUTES:
                return "Hold\nMinutes"
        return "ERROR"  # this should never run


class SequenceTableModel(TableModel):
    """TableModel for the temperature sequence."""

    dataLoaded = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def save_data(self):
        """Overridden method. Write the sequence settings to a file."""
        self.parameter_data.write_csv(Files.Sequence.SAVED_SETTINGS)

    def load_data(self):
        """
        Overridden method. Attempt to load previously saved sequency settings,
        showing a dialog on failure.
        """
        try:
            self.parameter_data = pl.scan_csv(Files.Sequence.SAVED_SETTINGS).collect()
        except Exception:
            OkDialog("Error", "Unable to load saved settings.").exec()
            self.parameter_data = self.generate_new_rows(1, 1)
        self.dataLoaded.emit(self.rowCount())
        self.layoutChanged.emit()

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
        return False

    def flags(self, index):
        if index.row() < self.disabled_row_index:
            flags = Qt.ItemFlag.NoItemFlags
        else:
            flags = Qt.ItemFlag.ItemIsEnabled
            if index.column() > Column.CYCLE.value:
                flags |= Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable
        return flags

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
            self.parameter_data = self.parameter_data.filter(
                col(str(Column.CYCLE)) <= new_row_count
            )
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
                str(Column.CYCLE): cycles,
                str(Column.TEMPERATURE): temperatures,
                str(Column.BUFFER_HOURS): times,
                str(Column.BUFFER_MINUTES): times,
                str(Column.HOLD_HOURS): times,
                str(Column.HOLD_MINUTES): times,
            }
        )
        return new_rows
