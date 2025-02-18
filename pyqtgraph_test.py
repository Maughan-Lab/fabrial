import pyqtgraph as pg
from PyQt6 import QtWidgets
from PyQt6.QtGui import QPalette


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Temperature vs time plot
        color = self.palette().window().color().name()
        self.plot_graph = pg.PlotWidget()
        self.plot_graph.setBackground(color)
        self.setCentralWidget(self.plot_graph)
        minutes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 30]
        self.plot_graph.plot(minutes, temperature)


app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
app.exec()
