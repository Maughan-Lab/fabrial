from collections.abc import Iterable
from typing import Any

from PyQt6.QtCore import QModelIndex, QSize, Qt

from ..tree_items import CategoryItem
from .tree_model import TreeModel


class OptionsModel(TreeModel[CategoryItem]):
    """
    `TreeModel` for the sequence options.

    Parameters
    ----------
    items
        The direct subitems of the root item.
    """

    def __init__(self, items: Iterable[CategoryItem]):
        TreeModel.__init__(self, "Options", items)

    def data(self, index: QModelIndex, role: int | None = None) -> Any:  # implementation
        if not index.isValid():
            return None
        item = self.get_item(index)
        if item is not None:
            match role:
                case Qt.ItemDataRole.DisplayRole:
                    return item.display_name()
                case Qt.ItemDataRole.DecorationRole:
                    return item.icon()
                case Qt.ItemDataRole.SizeHintRole:
                    return QSize(0, 23)
        return None

    def supportedDragActions(self) -> Qt.DropAction:  # overridden
        return Qt.DropAction.CopyAction
