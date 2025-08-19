from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QFrame, QTextBrowser


class MarkdownView(QTextBrowser):
    """Label with support for markdown."""

    def __init__(self):
        QTextBrowser.__init__(self)
        self.setReadOnly(True)
        self.setTextInteractionFlags(
            self.textInteractionFlags() | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        self.setOpenExternalLinks(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setViewportMargins(20, 20, 20, 20)  # this just looks better

    def sizeHint(self) -> QSize:
        return QTextBrowser.sizeHint(self) * 2  # looks better
