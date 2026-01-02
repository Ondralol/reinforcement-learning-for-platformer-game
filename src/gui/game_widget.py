"""Visualisation of the Game"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtCore import Qt, QTimer

from game.game import TILE_SIZE, Game, MovementDirection

# Colors for tiles
COLORS = {
    "#": QColor(0, 204, 100),
    "X": QColor(61, 26, 2),
    ".": QColor(102, 178, 255),
    "*": QColor(255, 255, 0),
    "Player": QColor(255, 0, 0),
}

# Definive cell size for visualisation
CELL_SIZE = 32


class MapWidget(QWidget):
    """Widget for visualisation the map and the player"""

    def __init__(self, parent, game: Game):
        """Initialize the visualisation by loading the sprints, creating UI and movement loop."""
        super().__init__(parent)
        self.parent = parent
        self.game = game

        # Set fix size of the game
        self.setFixedSize(len(game.map[0]) * CELL_SIZE, len(game.map) * CELL_SIZE)

        # Load sprints
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

        self.pressed_keys = set()

        # Game update loop
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_loop)
        self.game_timer.start(16) # 60fps

    def paintEvent(self, _event):
        """Re-renders the whole widget"""
        player_x = int(self.game.x)
        player_y = int(self.game.y)
        #print(f"Current player coordinates: ({player_x}, {player_y})")
        
        painter = QPainter(self)
        # Draws the map
        for y, row in enumerate(self.game.map):
            for x, cell in enumerate(row):
                draw_x = x * CELL_SIZE
                draw_y = y * CELL_SIZE
                
                match cell:
                    case "#":
                        painter.drawPixmap(draw_x, draw_y, self.grass)
                    case "X":
                        painter.drawPixmap(draw_x, draw_y, self.dirt)
                    case ".":
                        painter.drawPixmap(draw_x, draw_y, self.sky)
                    case "*":
                        painter.drawPixmap(draw_x, draw_y, self.coin)
                    case "E":
                        painter.drawPixmap(draw_x, draw_y - CELL_SIZE, self.flag)

        # Draws player position
        painter.drawPixmap(player_x, player_y, self.player)

        # color = colors.get(cell, QColor(255, 255, 255))
        # painter.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, color)
        # painter.setPen(Qt.black)
        # painter.drawRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    def keyPressEvent(self, event):
        """Detects key presses."""
        self.pressed_keys.add(event.key())

    def keyReleaseEvent(self, event):
        """Detects released key presses."""
        if event.key() in self.pressed_keys:
            self.pressed_keys.remove(event.key())

    def game_loop(self):
        """Game loop that updates the game state and makes a movement based on pressed keys."""
        
        # Default move (no move was made)
        move_dir = MovementDirection.IDLE
        
        if Qt.Key_W in self.pressed_keys and self.game.on_ground:
            move_dir = MovementDirection.JUMP
        elif Qt.Key_A in self.pressed_keys and Qt.Key_D not in self.pressed_keys:
            move_dir = MovementDirection.LEFT
        elif Qt.Key_D in self.pressed_keys and Qt.Key_A not in self.pressed_keys:
            move_dir = MovementDirection.RIGHT

        # Make move
        self.game.update(move_dir)    
        
        self.update()

class GameWidget(QWidget):
    """Game widget, that has MapWidget inside of it."""

    def __init__(self, parent, game: Game):
        """Initialize Game widget and create visualisation using MapWidget."""
        super().__init__(parent)
        self.parent = parent

        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.addStretch()
        self.setLayout(self.layout)

        self.layout.addWidget(MapWidget(self, game), alignment=Qt.AlignCenter)

        self.game = Game()
