from PyQt6.QtWidgets import QFrame, QSizePolicy


class HSeparator(QFrame):
    """A horizontal separator."""

    def __init__(self):
        QFrame.__init__(self)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setLineWidth(1)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)


class VSeparator(QFrame):
    """A vertical separator."""

    def __init__(self):
        QFrame.__init__(self)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setLineWidth(1)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
