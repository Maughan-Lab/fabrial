from PyQt6.QtWidgets import QWidget, QSizePolicy, QLayout


class Container(QWidget):
    """QWidget that automatically sets the layout and has no contents margins."""

    def __init__(self, layout: QLayout):
        """:param layout: The layout to initialize with."""
        super().__init__()

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class FixedContainer(Container):
    """Container with a fixed size."""

    def __init__(self, layout: QLayout):
        super().__init__(layout)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
