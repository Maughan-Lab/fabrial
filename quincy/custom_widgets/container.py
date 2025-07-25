from PyQt6.QtWidgets import QLayout, QSizePolicy

from .augmented.widget import Widget


class Container(Widget):
    """Widget that automatically sets the layout and has no contents margins."""

    def __init__(
        self,
        layout: QLayout,
        horizontal_size_policy: QSizePolicy.Policy = QSizePolicy.Policy.Preferred,
        vertical_size_policy: QSizePolicy.Policy = QSizePolicy.Policy.Preferred,
    ):
        """
        :param layout: The layout to initialize with.
        :param horizontal_size_policy: The horizontal size policy.
        :param vertical_size_policy: The vertical size policy.
        """
        Widget.__init__(self, layout)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(horizontal_size_policy, vertical_size_policy)


class FixedContainer(Container):
    """Container with a fixed size."""

    def __init__(self, layout: QLayout):
        Container.__init__(self, layout, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
