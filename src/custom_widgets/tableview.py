from PyQt6.QtWidgets import QTableView, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from .tablemodel import TableModel


class TableView(QTableView):
    """Partial implementation of a QTableView."""

    def __init__(self, model: TableModel, max_visible_rows: int):
        """
        :param model: The QAbstractTableModel to connect this view to.
        :param max_visible_rows: The maximum number of rows to display on screen (a scrollbar
        is displayed if the actual number of rows exceeds this).
        """
        super().__init__()
        self.max_visible_rows = max_visible_rows
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

    def get_current_width(self) -> int:
        """Get the column width accounting for the scrollbar."""
        width = self.frameWidth() * 2

        model = self.model()
        if model is not None:
            if model.rowCount() > self.max_visible_rows:
                # this means the scrollbar is visible
                vertical_scrollbar = self.verticalScrollBar()
                if vertical_scrollbar is not None:
                    width += vertical_scrollbar.sizeHint().width()
            for i in range(model.columnCount()):
                width += self.columnWidth(i)

        return width

    def get_max_height(self) -> int:
        """Get the maximum height, dictated by **MAX_VISIBLE_ROWS**."""
        height = self.frameWidth() * 2

        horizontal_header = self.horizontalHeader()
        if horizontal_header is not None:
            height += horizontal_header.sizeHint().height()

        for i in range(self.max_visible_rows):
            height += self.rowHeight(i)
        return height

    def get_current_height(self) -> int:
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
        Update the table size to show either **max_visible_rows** rows or the current number of
        rows, whichever is smaller.
        """
        self.resizeColumnsToContents()
        self.setFixedSize(
            QSize(self.get_current_width(), min(self.get_current_height(), self.get_max_height()))
        )
