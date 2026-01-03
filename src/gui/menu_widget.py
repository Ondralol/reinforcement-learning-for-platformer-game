"""Menu Widget that serves as basic navigation throughout the application"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

from game.game import Game
from gui.game_widget import GameWidget


class MenuWidget(QWidget):
    """Main navigation Menu widget."""

    def __init__(self, parent):
        """Initialize Menu widget.

        Create "Play Game" and "Agent Plays Game" buttons"
        """
        super().__init__(parent)
        self.parent = parent

        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.addStretch()
        self.setLayout(self.layout)

        # First button
        self.play_game_button = QPushButton("Play Game")
        self.play_game_button.setFixedSize(300, 50)
        self.layout.addWidget(self.play_game_button, alignment=Qt.AlignCenter)
        self.play_game_button.clicked.connect(lambda: self.create_and_show_game(False))

        # Second button
        self.agent_game_button = QPushButton("Agent Plays Game")
        self.agent_game_button.setFixedSize(300, 50)
        self.layout.addWidget(self.agent_game_button, alignment=Qt.AlignCenter)
        self.agent_game_button.clicked.connect(lambda: self.create_and_show_game(True))

        self.layout.addStretch()

    def create_and_show_game(self, agent):
        """Creates game widget.

        Args:
            agent: Whether or not agent plays the game
        """

        # Initialize Game
        self.game = Game()
        game_widget = GameWidget(self.parent, self.game, agent)
        self.parent.setCentralWidget(game_widget)
        game_widget.map_widget.setFocus()
