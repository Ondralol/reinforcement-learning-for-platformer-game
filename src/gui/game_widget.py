"""Visualisation of the Game"""

from dataclasses import dataclass, field

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QSlider, QLabel, QHBoxLayout
from PySide6.QtGui import QColor, QPainter, QPixmap, QFont, QFontMetrics
from PySide6.QtCore import Qt, QTimer, QSize

from game.game import TILE_SIZE, Game, MovementDirection
from agent.train import Train
from utils.args_config import Config

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
STEPS_PER_FRAME = 750  # How many steps does the agent move per frame


@dataclass
class VisualisationState:
    """Track rendering offsets and scaling."""

    steps_per_frame: int = STEPS_PER_FRAME
    cell_size: int = CELL_SIZE
    offset_x: int = 0
    offset_y: int = 0
    map_w_tiles: int = 0
    map_h_tiles: int = 0


@dataclass
class Sprites:
    """Sprints for the game."""

    raw: dict[str, QPixmap] = field(default_factory=dict)
    scaled: dict[str, QPixmap] = field(default_factory=dict)


class MapWidget(QWidget):
    """Widget for visualisation the map and the player"""

    def __init__(self, parent, game: Game, config: Config, agent=False):
        """Initialize the visualisation by loading the sprints, creating UI and movement loop.

        Args:
            game: the game "engine" class
            agent: if agent should play the game
            config: CLI Arguments
        """

        super().__init__(parent)
        self.game = game
        self.agent = agent
        self.train = Train(config)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Store dimensions
        self.vis_state = VisualisationState(map_w_tiles=len(game.map_state.map[0]), map_h_tiles=len(game.map_state.map))

        # Load sprints
        self.sprites = Sprites(
            raw={
                "X": QPixmap("data/dirt.png"),
                "#": QPixmap("data/grass.png"),
                "*": QPixmap("data/coin.png"),
                ".": QPixmap("data/sky.png"),
                "-": QPixmap("data/void.png"),
                "Player": QPixmap("data/player1.png"),
                "E": QPixmap("data/flag.png"),
            }
        )

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

    def update_step_size(self, val: int):
        """Updates agent's step size.

        Args:
            val: Value that the agent's speed is updated to
        """

        self.vis_state.steps_per_frame = val

    def recalculate_scale(self):
        """Calculates new scales based on window size."""
        curr_w = self.width()
        curr_h = self.height()

        scale_x = curr_w / self.vis_state.map_w_tiles
        scale_y = curr_h / self.vis_state.map_h_tiles

        # Calculate new cell size
        self.vis_state.cell_size = int(min(scale_x, scale_y))

        # Cell size needs to be always >= 1
        self.vis_state.cell_size = max(self.vis_state.cell_size, 1)

        # Calculate total area and offsets
        total_map_w = self.vis_state.cell_size * self.vis_state.map_w_tiles
        total_map_h = self.vis_state.cell_size * self.vis_state.map_h_tiles
        self.vis_state.offset_x = (curr_w - total_map_w) // 2
        self.vis_state.offset_y = (curr_h - total_map_h) // 2

        # Rescale the sprites
        self.sprites.scaled["#"] = self.sprites.raw["#"].scaled(self.vis_state.cell_size, self.vis_state.cell_size)
        self.sprites.scaled["X"] = self.sprites.raw["X"].scaled(self.vis_state.cell_size, self.vis_state.cell_size)
        self.sprites.scaled["."] = self.sprites.raw["."].scaled(self.vis_state.cell_size, self.vis_state.cell_size)
        self.sprites.scaled["*"] = self.sprites.raw["*"].scaled(self.vis_state.cell_size, self.vis_state.cell_size)
        self.sprites.scaled["-"] = self.sprites.raw["-"].scaled(self.vis_state.cell_size, self.vis_state.cell_size)

        self.sprites.scaled["Player"] = self.sprites.raw["Player"].scaled(
            self.vis_state.cell_size, self.vis_state.cell_size * 2
        )
        self.sprites.scaled["E"] = self.sprites.raw["E"].scaled(self.vis_state.cell_size, self.vis_state.cell_size * 2)

    def resizeEvent(self, event):
        """Recalculate scale factor upon resizing."""
        self.recalculate_scale()
        super().resizeEvent(event)

    def paint_agent_stats(self, painter):
        """Draws agents statistics

        Args:
            painter: Qt painter reference
            width: Reference with (kinda dumb idc)
        """
        width = QFontMetrics(QFont("Courier New", self.vis_state.cell_size / 1.5)).horizontalAdvance("--.----")

        ui_font = QFont("Courier New", self.vis_state.cell_size / 1.5)
        ui_font.setBold(True)
        painter.setFont(ui_font)
        painter.setPen(QColor("black"))
        generation_text = f"Generation: {self.train.training_stats.generation}"

        painter.drawText(
            self.vis_state.offset_x + width * 5, self.vis_state.offset_y + self.vis_state.cell_size, generation_text
        )
        painter.setPen(QColor("gold"))
        painter.drawText(
            self.vis_state.offset_x + width * 5 - 2,
            self.vis_state.offset_y + self.vis_state.cell_size - 2,
            generation_text,
        )

        painter.setPen(QColor("black"))
        win_count_text = f"Win Count: {self.train.training_stats.win_count}"
        painter.drawText(
            self.vis_state.offset_x + width * 8, self.vis_state.offset_y + self.vis_state.cell_size, win_count_text
        )
        painter.setPen(QColor("gold"))
        painter.drawText(
            self.vis_state.offset_x + width * 8 - 2,
            self.vis_state.offset_y + self.vis_state.cell_size - 2,
            win_count_text,
        )

        painter.setPen(QColor("black"))
        best_step_count_text = f"Least steps: {self.game.game_state.progress.best_step_count}"
        painter.drawText(
            self.vis_state.offset_x + width * 11,
            self.vis_state.offset_y + self.vis_state.cell_size,
            best_step_count_text,
        )
        painter.setPen(QColor("gold"))
        painter.drawText(
            self.vis_state.offset_x + width * 11 - 2,
            self.vis_state.offset_y + self.vis_state.cell_size - 2,
            best_step_count_text,
        )

        painter.setPen(QColor("black"))
        best_distance_text = f"Closest distance: {self.game.persistant_states.total_best_distance:.2f}"
        painter.drawText(
            self.vis_state.offset_x + width * 14, self.vis_state.offset_y + self.vis_state.cell_size, best_distance_text
        )
        painter.setPen(QColor("gold"))
        painter.drawText(
            self.vis_state.offset_x + width * 14 - 2,
            self.vis_state.offset_y + self.vis_state.cell_size - 2,
            best_distance_text,
        )

    def paint_game_ui(self, painter):
        """Paints coins, time and Victory + Game over"""
        # Draw Stats
        ui_font = QFont("Courier New", self.vis_state.cell_size / 1.5)
        ui_font.setBold(True)
        painter.setFont(ui_font)

        coin_text = f"Coins: {self.game.game_state.coins_collected}"
        width_coin = QFontMetrics(ui_font).horizontalAdvance(coin_text)
        time_text = f"Time:  {self.game.get_formatted_time()}"

        painter.setPen(QColor("black"))
        painter.drawText(
            self.vis_state.offset_x + self.vis_state.cell_size,
            self.vis_state.offset_y + self.vis_state.cell_size,
            coin_text,
        )
        painter.drawText(
            self.vis_state.offset_x + self.vis_state.cell_size + width_coin * 1.5,
            self.vis_state.offset_y + self.vis_state.cell_size,
            time_text,
        )

        painter.setPen(QColor("gold"))
        painter.drawText(
            self.vis_state.offset_x + self.vis_state.cell_size - 2,
            self.vis_state.offset_y + self.vis_state.cell_size - 2,
            coin_text,
        )
        painter.drawText(
            self.vis_state.offset_x + self.vis_state.cell_size + width_coin * 1.5 - 2,
            self.vis_state.offset_y + self.vis_state.cell_size - 2,
            time_text,
        )

        # Print Victory / Game over screens
        ui_font = QFont("Courier New", self.vis_state.cell_size * 1.5)
        painter.setPen(QColor("white"))
        ui_font.setBold(True)
        painter.setFont(ui_font)
        if self.game.game_state.game_completed:
            victory_text = "Victory!"
            width_victory = QFontMetrics(ui_font).horizontalAdvance(victory_text)
            painter.drawText(self.width() // 2 - width_victory // 2, self.height() // 2, victory_text)
        if self.game.game_state.game_over:
            game_over_text = "Game Over!"
            width_game_over = QFontMetrics(ui_font).horizontalAdvance(game_over_text)
            painter.drawText(self.width() // 2 - width_game_over // 2, self.height() // 2, game_over_text)

    def paintEvent(self, _event):
        """Re-renders the whole game widget"""

        painter = QPainter(self)
        # Draws the map
        for y, row in enumerate(self.game.map_state.map):
            for x, cell in enumerate(row):
                draw_x = self.vis_state.offset_x + (x * self.vis_state.cell_size)
                draw_y = self.vis_state.offset_y + (y * self.vis_state.cell_size)
                if cell == "E":
                    painter.drawPixmap(draw_x, draw_y - self.vis_state.cell_size, self.sprites.scaled[cell])
                else:
                    painter.drawPixmap(draw_x, draw_y, self.sprites.scaled[cell])

        # Draws player position
        scale_factor = self.vis_state.cell_size / TILE_SIZE
        player_x = self.vis_state.offset_x + int(self.game.player_state.x * scale_factor)
        player_y = self.vis_state.offset_y + int(self.game.player_state.y * scale_factor)
        # print(f"Current player coordinates: ({player_x}, {player_y})")

        painter.drawPixmap(player_x, player_y, self.sprites.scaled["Player"])

        # Prints game UI
        self.paint_game_ui(painter)

        # Agent debug
        if self.agent:
            self.paint_agent_stats(painter)

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
            for _ in range(self.vis_state.steps_per_frame):
                self.train.make_one_step()
                if self.train.training_state.done:
                    break

            self.game = self.train.game
            self.update()
            return

        # Default move (no move was made)
        move_dir = MovementDirection.IDLE

        # Movement positions

        # Jump
        if (Qt.Key_W in self.pressed_keys or Qt.Key_Space in self.pressed_keys) and self.game.player_state.on_ground:
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

    def __init__(self, parent, game: Game, agent: False, config: Config):
        """Initialize Game widget and create visualisation using MapWidget.

        Arguments:
            game: Game class
            agent: IF agent should play the game or not
            config: CLI Arguments
        """
        super().__init__(parent)
        self.parent = parent

        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.setLayout(self.layout)

        self.map_widget = MapWidget(self, game, config, agent)

        # Add agent controls
        if agent:
            self.add_controls()

        self.layout.addWidget(self.map_widget)
        self.layout.addStretch()
        self.game = Game(config)

    def add_controls(self):
        """Adds slider to change the agent's steps_per_frame."""

        controls_widget = QWidget()
        controls_layout = QHBoxLayout()
        self.speed_label = QLabel(f"Speed: {self.map_widget.vis_state.steps_per_frame}")
        self.speed_label.setStyleSheet("color: white; font-weight: bold; font-family: Courier New;")

        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(2500)  # Might crash application if it's too high because it takes too long to compute
        self.slider.setValue(self.map_widget.vis_state.steps_per_frame)

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
