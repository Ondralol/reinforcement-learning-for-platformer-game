"""Main window of the GUI"""

from PySide6.QtWidgets import QMainWindow, QApplication

from gui.menu_widget import MenuWidget


class MainWindow(QMainWindow):
    """Main Application window."""

    def __init__(self, app: QApplication):
        """Initialize window size, title, maximazes window and sets Menu widget as the main widget."""
        super().__init__()
        self.app = app
        self.setWindowTitle("Agent Learns to play Game")
        self.showMaximized()
        self.setMinimumSize(900, 450)

        self.setCentralWidget(MenuWidget(self))
