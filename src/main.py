"""Main application entrypoint"""

import sys
import signal
import qdarkstyle
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

if __name__ == "__main__":
    # Enable ctrl + c to exit app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Qt Application intance
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))
    window = MainWindow(app)
    window.show()
    app.exec()
