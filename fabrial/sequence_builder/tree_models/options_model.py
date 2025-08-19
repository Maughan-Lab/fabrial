from types import ModuleType
from typing import Any, Iterable, Mapping, Self

from PyQt6.QtCore import QModelIndex, QSize, Qt

from ...utility import errors, sequence_builder
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

    @classmethod
    def from_plugins(cls, plugin_modules: Mapping[str, ModuleType]) -> Self:
        """
        Create the model from the application's available plugins. Logs errors.

        This calls `plugins.items_from_plugins()`.

        Parameters
        ----------
        plugin_modules
            A list of modules that represent plugins for the application.

        """
        items, failure_plugins, failure_categories = sequence_builder.items_from_plugins(
            plugin_modules
        )
        # if anything failed to load, report it to the user
        if len(failure_plugins) > 0 or len(failure_categories) > 0:
            message = ""
            if len(failure_plugins) > 0:
                message += f"Failed to load items from plugins:\n\n{", ".join(failure_plugins)}\n\n"
            if len(failure_categories) > 0:
                message += f"Failed to load categories:\n\n{", ".join(failure_categories)}\n\n"
            message += "See the error log for details."
            errors.show_error_delayed("Plugin Error", message)
        return cls(items)  # return the new instance

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
