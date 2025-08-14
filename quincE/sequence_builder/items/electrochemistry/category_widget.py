from ....gamry_integration import GAMRY
from ..base_widget import CategoryWidget


class ElectrochemistryCategoryWidget(CategoryWidget):
    def __init__(self):
        CategoryWidget.__init__(self, "Electrochemistry")

    @staticmethod
    def allowed_to_create():
        return GAMRY.is_valid()
