"""Visualisation of the Game"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QSlider, QLabel, QHBoxLayout
from PySide6.QtGui import QColor, QPainter, QPixmap, QFont, QFontMetrics
from PySide6.QtCore import Qt, QTimer, QSize

from game.game import TILE_SIZE, Game, MovementDirection
from agent.train import Train

# Colors for tiles
COLORS = {
    "#": QColor(0, 204, 100),
    "X": QColor(61, 26, 2),
    ".": QColor(102, 178, 255),
    "*": QColor(255, 255, 0),
    "Player": QColor(255, 0, 0),
}

# Definive cell size for visualisation
CELL_SIZE = 16
STEPS_PER_FRAME = 1000  # How many steps does the agent move per frame


class MapWidget(QWidget):
    """Widget for visualisation the map and the player"""

    def __init__(self, parent, game: Game, agent=False):
        """Initialize the visualisation by loading the sprints, creating UI and movement loop.

        Args:
            game: the game "engine" class
            agent: if agent should play the game
        """

        super().__init__(parent)
        self.parent = parent
        self.game = game

        self.agent = agent
        self.train = Train()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Store dimensions
        self.map_w_tiles = len(game.map[0])
        self.map_h_tiles = len(game.map)

        self.cell_size = CELL_SIZE  # Default size
        self.offset_x = 0  # Offset to the center of the map horizontally
        self.offset_y = 0  # Offset to the center of the map vertically

        # Load sprints
        self.dirt = QPixmap("data/dirt.png")
        self.grass = QPixmap("data/grass.png")
        self.coin = QPixmap("data/coin.png")
        self.sky = QPixmap("data/sky.png")
        self.player = QPixmap("data/player1.png")
        self.flag = QPixmap("data/flag.png")
        self.void = QPixmap("data/void.png")

        # Scaled sprints
        self.scaled_dirt = None
        self.scaled_grass = None
        self.scaled_coin = None
        self.scaled_sky = None
        self.scaled_player = None
        self.scaled_flag = None
        self.scaled_void = None

        # Focus window
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # Initiate keyboard input set
        self.pressed_keys = set()

        # Initial resize
        self.recalculate_scale()

        # Game update loop
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_loop)
        self.game_timer.start(16)  # 60fps

        # Set agent's steps per frame to a default value
        self.steps_per_frame = STEPS_PER_FRAME

    def update_step_size(self, val: int):
        """Updates agent's step size.

        Args:
            val: Value that the agent's speed is updated to
        """

        self.steps_per_frame = val

    def recalculate_scale(self):
        """Calculates new scales based on window size."""
        curr_w = self.width()
        curr_h = self.height()

        scale_x = curr_w / self.map_w_tiles
        scale_y = curr_h / self.map_h_tiles

        # Calculate new cell size
        self.cell_size = int(min(scale_x, scale_y))

        # Cell size needs to be always >= 1
        self.cell_size = max(self.cell_size, 1)

        # Calculate total area and offsets
        total_map_w = self.cell_size * self.map_w_tiles
        total_map_h = self.cell_size * self.map_h_tiles
        self.offset_x = (curr_w - total_map_w) // 2
        self.offset_y = (curr_h - total_map_h) // 2

        # Rescale the sprites
        self.scaled_dirt = self.dirt.scaled(self.cell_size, self.cell_size)
        self.scaled_grass = self.grass.scaled(self.cell_size, self.cell_size)
        self.scaled_coin = self.coin.scaled(self.cell_size, self.cell_size)
        self.scaled_sky = self.sky.scaled(self.cell_size, self.cell_size)
        self.scaled_void = self.void.scaled(self.cell_size, self.cell_size)

        self.scaled_player = self.player.scaled(self.cell_size, self.cell_size * 2)
        self.scaled_flag = self.flag.scaled(self.cell_size, self.cell_size * 2)

    def resizeEvent(self, event):
        """Recalculate scale factor upon resizing."""
        self.recalculate_scale()
        super().resizeEvent(event)

    def paintEvent(self, _event):
        """Re-renders the whole game widget"""

        painter = QPainter(self)
        # Draws the map
        for y, row in enumerate(self.game.map):
            for x, cell in enumerate(row):
                draw_x = self.offset_x + (x * self.cell_size)
                draw_y = self.offset_y + (y * self.cell_size)

                match cell:
                    case "#":
                        painter.drawPixmap(draw_x, draw_y, self.scaled_grass)
                    case "X":
                        painter.drawPixmap(draw_x, draw_y, self.scaled_dirt)
                    case ".":
                        painter.drawPixmap(draw_x, draw_y, self.scaled_sky)
                    case "*":
                        painter.drawPixmap(draw_x, draw_y, self.scaled_coin)
                    case "-":
                        painter.drawPixmap(draw_x, draw_y, self.scaled_void)
                    case "E":
                        painter.drawPixmap(draw_x, draw_y - self.cell_size, self.scaled_flag)

        # Draws player position
        scale_factor = self.cell_size / TILE_SIZE
        player_x = self.offset_x + int(self.game.x * scale_factor)
        player_y = self.offset_y + int(self.game.y * scale_factor)
        # print(f"Current player coordinates: ({player_x}, {player_y})")
        painter.drawPixmap(player_x, player_y, self.scaled_player)

        # Draw Stats
        ui_font = QFont("Courier New", self.cell_size / 1.5)
        ui_font.setBold(True)
        painter.setFont(ui_font)

        coin_text = f"Coins: {self.game.coins_collected}"
        width_coin = QFontMetrics(ui_font).horizontalAdvance(coin_text)
        time_text = f"Time:  {self.game.get_formatted_time()}"

        painter.setPen(QColor("black"))
        painter.drawText(self.offset_x + self.cell_size, self.offset_y + self.cell_size, coin_text)
        painter.drawText(self.offset_x + self.cell_size + width_coin * 1.5, self.offset_y + self.cell_size, time_text)

        painter.setPen(QColor("gold"))
        painter.drawText(self.offset_x + self.cell_size - 2, self.offset_y + self.cell_size - 2, coin_text)
        painter.drawText(
            self.offset_x + self.cell_size + width_coin * 1.5 - 2, self.offset_y + self.cell_size - 2, time_text
        )

        # Print Victory / Game over screens
        ui_font = QFont("Courier New", self.cell_size * 1.5)
        painter.setPen(QColor("white"))
        ui_font.setBold(True)
        painter.setFont(ui_font)
        if self.game.game_completed:
            victory_text = "Victory!"
            width_victory = QFontMetrics(ui_font).horizontalAdvance(victory_text)
            painter.drawText(self.width() // 2 - width_victory // 2, self.height() // 2, victory_text)
        if self.game.game_over:
            game_over_text = "Game Over!"
            width_game_over = QFontMetrics(ui_font).horizontalAdvance(game_over_text)
            painter.drawText(self.width() // 2 - width_game_over // 2, self.height() // 2, game_over_text)

        # Agent debug
        if self.agent:
            ui_font = QFont("Courier New", self.cell_size / 1.5)
            painter.setFont(ui_font)
            ui_font.setBold(True)
            painter.setPen(QColor("black"))
            generation_text = f"Generation: {self.train.generation}"
            painter.drawText(self.offset_x + width_coin * 10, self.offset_y + self.cell_size, generation_text)
            painter.setPen(QColor("gold"))
            painter.drawText(self.offset_x + width_coin * 10 - 2, self.offset_y + self.cell_size - 2, generation_text)

            painter.setPen(QColor("black"))
            win_count_text = f"Win Count: {self.train.win_count}"
            painter.drawText(self.offset_x + width_coin * 14, self.offset_y + self.cell_size, win_count_text)
            painter.setPen(QColor("gold"))
            painter.drawText(self.offset_x + width_coin * 14 - 2, self.offset_y + self.cell_size - 2, win_count_text)

    def keyPressEvent(self, event):
        """Detects key presses."""
        self.pressed_keys.add(event.key())

    def keyReleaseEvent(self, event):
        """Detects released key presses."""
        if event.key() in self.pressed_keys:
            self.pressed_keys.remove(event.key())

    def game_loop(self):
        """Game loop that updates the game state and makes a movement based on pressed keys."""

        # If agent is playing
        if self.agent:
            self.train.make_step(step_size=self.steps_per_frame)
            self.game = self.train.game
            self.update()
            return

        # Default move (no move was made)
        move_dir = MovementDirection.IDLE

        # Movement positions

        # Jump
        if (Qt.Key_W in self.pressed_keys or Qt.Key_Space in self.pressed_keys) and self.game.on_ground:
            move_dir = MovementDirection.JUMP
        # Left
        elif Qt.Key_A in self.pressed_keys and Qt.Key_D not in self.pressed_keys:
            move_dir = MovementDirection.LEFT
        # Right
        elif Qt.Key_D in self.pressed_keys and Qt.Key_A not in self.pressed_keys:
            move_dir = MovementDirection.RIGHT
        # Restart game
        elif Qt.Key_R in self.pressed_keys:
            self.game.restart_game()
            return

        # Make move
        self.game.update(move_dir)

        self.update()

    def sizeHint(self):
        """Preffered widget size"""
        return QSize(1440, 950)


class GameWidget(QWidget):
    """Game widget, that has MapWidget inside of it."""

    def __init__(self, parent, game: Game, agent: False):
        """Initialize Game widget and create visualisation using MapWidget."""
        super().__init__(parent)
        self.parent = parent

        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.setLayout(self.layout)

        self.map_widget = MapWidget(self, game, agent)

        # Add agent controls
        if agent:
            self.add_controls()

        self.layout.addWidget(self.map_widget)
        self.layout.addStretch()
        self.game = Game()

    def add_controls(self):
        """Adds slider to change the agent's steps_per_frame."""

        controls_widget = QWidget()
        controls_layout = QHBoxLayout()
        self.speed_label = QLabel(f"Speed: {self.map_widget.steps_per_frame}")
        self.speed_label.setStyleSheet("color: white; font-weight: bold; font-family: Courier New;")

        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(5000)  # Might crash application if it's too high because it takes too long to compute
        self.slider.setValue(self.map_widget.steps_per_frame)

        # Connect slider to a function that updates speed
        self.slider.valueChanged.connect(self.update_step_size_ui)

        controls_layout.addWidget(QLabel("Slow", parent=self))
        controls_layout.addWidget(self.slider)
        controls_layout.addWidget(QLabel("Fast", parent=self))
        controls_layout.addWidget(self.speed_label)

        controls_widget.setLayout(controls_layout)

        self.layout.addWidget(controls_widget)

    def update_step_size_ui(self, val: int):
        """Updates steps size UI and value.

        Args:
            val: Value that the agent's speed is updated to
        """
        self.speed_label.setText(f"Speed: {val}")
        self.map_widget.update_step_size(val)
