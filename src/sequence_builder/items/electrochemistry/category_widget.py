from ....gamry_integration.gamry import GAMRY
from ..base_widget import CategoryWidget


class ElectrochemistryCategoryWidget(CategoryWidget):
    def __init__(self):
        super().__init__("Electrochemistry")

    @staticmethod
    def allowed_to_create():
        return GAMRY.is_valid()
