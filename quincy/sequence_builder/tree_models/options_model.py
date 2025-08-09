from typing import Any, Iterable, Self

from PyQt6.QtCore import QModelIndex, Qt

from ...classes import Clipboard
from ...utility import sequence_builder
from ..tree_items import CategoryItem
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
        TreeModel.__init__(self, "Options", items, clipboard)

    @classmethod
    def from_initialization_directories(cls, clipboard: Clipboard) -> Self:
        """
        Create the model from the application's item initialization directories.

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
