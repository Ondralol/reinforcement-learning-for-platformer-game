""" Main window of the GUI """
from PySide6.QtWidgets import QMainWindow, QApplication

from gui.menu_widget import MenuWidget

class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.setWindowTitle("Agent Learns to play Game")
        self.showMaximized()
        self.setMinimumSize(1440, 920)
        
        self.setCentralWidget(MenuWidget(self))
        