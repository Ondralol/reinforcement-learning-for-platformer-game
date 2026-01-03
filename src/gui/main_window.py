"""Main window of the GUI"""

from PySide6.QtWidgets import QMainWindow, QApplication

from gui.menu_widget import MenuWidget
from utils.args_config import Config

class MainWindow(QMainWindow):
    """Main Application window."""

    def __init__(self, app: QApplication, config: Config):
        """Initialize window size, title, maximazes window and sets Menu widget as the main widget.
        
        Arguments:
            config: CLI Arguments
        """
        super().__init__()
        self.app = app
        self.setWindowTitle("Agent Learns to play Game")
        self.showMaximized()
        self.setMinimumSize(900, 450)

        self.setCentralWidget(MenuWidget(self, config))
