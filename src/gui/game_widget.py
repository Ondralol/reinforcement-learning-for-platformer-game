""" Game Widget module of the GUI """
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtCore import Qt, QTimer

from game.game import PLAYER_RATIO, Game

colors = {
    "#": QColor(0, 204, 100),
    "X": QColor(61, 26, 2),
    ".": QColor(102, 178, 255),
    "*": QColor(255, 255, 0),
    "Player": QColor(255, 0, 0),
}


CELL_SIZE = 32

class MapWidget(QWidget):
    def __init__(self, parent, game: Game):
        super().__init__(parent)
        self.parent = parent
        self.game = game
  
        self.setFixedSize(len(game.map[0]) * CELL_SIZE, len(game.map) * CELL_SIZE)
        
        
        self.dirt = QPixmap("data/dirt.png").scaled(CELL_SIZE, CELL_SIZE)
        self.grass = QPixmap("data/grass.png").scaled(CELL_SIZE, CELL_SIZE)
        self.coin = QPixmap("data/coin.png").scaled(CELL_SIZE, CELL_SIZE)
        self.sky = QPixmap("data/sky.png").scaled(CELL_SIZE, CELL_SIZE)
        self.player = QPixmap("data/player1.png").scaled(CELL_SIZE, CELL_SIZE * 2)
        self.flag = QPixmap("data/flag.png").scaled(CELL_SIZE, CELL_SIZE * 2)
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
        # Game UI loop
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update)
        self.render_timer.start(16)  # Approximately 60 FPS
        
        # Game movement loop
        self.movement_timer = QTimer()
        self.movement_timer.timeout.connect(self.update_movement)
        self.movement_timer.start(50)
        
        self.pressed_keys = set()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        for y, row in enumerate(self.game.map):
            for x, cell in enumerate(row):
                match cell:
                    case "#":
                        painter.drawPixmap(x * CELL_SIZE, y * CELL_SIZE, self.grass)
                    case "X":
                        painter.drawPixmap(x * CELL_SIZE, y * CELL_SIZE, self.dirt)
                    case ".":
                        painter.drawPixmap(x * CELL_SIZE, y * CELL_SIZE, self.sky)
                    case "*":
                        painter.drawPixmap(x * CELL_SIZE, y * CELL_SIZE, self.coin)
                    case "E":
                        painter.drawPixmap(x * CELL_SIZE, y * CELL_SIZE - CELL_SIZE, self.flag)
                        
        x, y = self.game.player_position
        painter.drawPixmap((x // PLAYER_RATIO) * CELL_SIZE + (x % PLAYER_RATIO) * CELL_SIZE//PLAYER_RATIO,
                          (y // PLAYER_RATIO) * CELL_SIZE + (y % PLAYER_RATIO) * CELL_SIZE//PLAYER_RATIO - CELL_SIZE, 
                          self.player)
                        
                        
                #color = colors.get(cell, QColor(255, 255, 255))
                #painter.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, color)
                #painter.setPen(Qt.black)
                #painter.drawRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    def keyPressEvent(self, event):
        self.pressed_keys.add(event.key())
    
    def keyReleaseEvent(self, event):
        if event.key() in self.pressed_keys:
            self.pressed_keys.remove(event.key())
    
    def update_movement(self):
        if Qt.Key_A in self.pressed_keys and len(self.pressed_keys) == 1:
            self.game.move_player(-1, 0)
        elif Qt.Key_D in self.pressed_keys and len(self.pressed_keys) == 1:
            self.game.move_player(1, 0)
        elif Qt.Key_W in self.pressed_keys and len(self.pressed_keys) == 1:
            self.game.move_player(0, -2)
        elif Qt.Key_A in self.pressed_keys and Qt.Key_W in self.pressed_keys and len(self.pressed_keys) == 2:
            self.game.move_player(-1, -2)
        elif Qt.Key_D in self.pressed_keys and Qt.Key_W in self.pressed_keys and len(self.pressed_keys) == 2:
            self.game.move_player(1, -2)
    
    
class GameWidget(QWidget):
    
    def __init__(self, parent, game: Game):
        super().__init__(parent)
        self.parent = parent
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.addStretch()
        self.setLayout(self.layout)
        
        self.layout.addWidget(MapWidget(self, game), alignment=Qt.AlignCenter)

        
        
        self.game = Game()
        