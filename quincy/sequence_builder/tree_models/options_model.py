from typing import Any, Iterable, Self

from PyQt6.QtCore import QModelIndex, Qt

from ...utility import sequence_builder
from ..clipboard import Clipboard
from ..tree_items import CategoryItem, RootItem
from . import tree_model
from .tree_model import TreeModel


class OptionsModel(TreeModel[CategoryItem]):
    """
    `TreeModel` for the sequence options.

    Parameters
    ----------
    items
        The direct subitems of the root item.
    clipboard
        The clipboard to copy items to.
    """

    def __init__(self, items: Iterable[CategoryItem], clipboard: Clipboard):
        self.root: RootItem[CategoryItem] = RootItem()
        self.root.append_subitems(items)
        self.clipboard = clipboard

        self.base_flag = Qt.ItemFlag.ItemIsEnabled

    @classmethod
    def from_initialization_directories(cls, clipboard: Clipboard) -> Self:
        """
        Initialize the model's data from the application's item initialization directories.

        This calls `sequence_builder.items_from_directories()` and
        `sequence_builder.get_initialization_directories()`.

        Parameters
        ----------
        directories
            The directories to load items from.
        clipboard
            The clipboard to copy items to.
        """
        return cls(
            sequence_builder.items_from_directories(
                sequence_builder.get_initialization_directories()
            ),
            clipboard,
        )

    def get_title(self) -> str:  # implementation
        return "Options"

    def get_root(self):  # implementation
        return self.root

    def copy_items(self, indexes: Iterable[QModelIndex]):  # implementation
        tree_model.copy_items(self, self.clipboard, indexes)

    def is_enabled(self) -> bool:  # implementation
        return self.base_flag != Qt.ItemFlag.NoItemFlags

    def set_enabled(self, enabled: bool):  # implementation
        self.base_flag = Qt.ItemFlag.ItemIsEnabled if enabled else Qt.ItemFlag.NoItemFlags

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:  # implementation
        return tree_model.flags(self, self.base_flag, index)

    def data(self, index: QModelIndex, role: int | None = None) -> Any:  # implementation
        if not index.isValid():
            return None
        item = self.get_item(index)
        if item is not None:
            match role:
                case Qt.ItemDataRole.DisplayRole:
                    return item.get_display_name()
                case Qt.ItemDataRole.DecorationRole:
                    return item.get_icon()
        return None

    def supportedDragActions(self) -> Qt.DropAction:  # overridden
        return Qt.DropAction.CopyAction
