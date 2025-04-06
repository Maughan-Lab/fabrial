from PyQt6.QtWidgets import QApplication
from src.tree_model.tree_view import TreeView
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)
    TreeView()
    app.exec()
