""" Nenu Widget """
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

from game.game import Game
from gui.game_widget import GameWidget


class MenuWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.game = Game()
        self.game_widget = GameWidget(self.parent, self.game)
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.addStretch()
        self.setLayout(self.layout)
        
        self.play_game_button = QPushButton("Play Game")
        self.play_game_button.setFixedSize(300, 50)
        self.layout.addWidget(self.play_game_button, alignment=Qt.AlignCenter)
        self.play_game_button.clicked.connect(lambda: self.parent.setCentralWidget(self.game_widget))
        
        self.agent_game_button = QPushButton("Agent Plays Game")
        self.agent_game_button.setFixedSize(300, 50)
        self.layout.addWidget(self.agent_game_button, alignment=Qt.AlignCenter)
        
        self.layout.addStretch()

        
        
      
        
