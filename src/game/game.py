"""This file includes the entire game logic/physics"""

from enum import Enum
from dataclasses import dataclass, field

from PySide6.QtCore import QElapsedTimer
import numpy as np

from utils.args_config import Config

TILE_SIZE = 32  # 32 pixels in one block
GRAVITY = 0.5  # Downward acceleration per frame
JUMP_STRENGTH = -12.0  # Upward velocity when jumping
MOVE_SPEED = 3.0  # Horizontal speed in pixels per frame
X_VELOCITY_SLIDING = 0.10  # Sliding effect for X-axis velocity (Btw, this makes it kinda annoying if it's too high)
MAX_FALLING_SPEED = 10.0  # Maximal Y axis falling speed


class MovementDirection(Enum):
    """Defines all possible movement directions."""

    IDLE = 0
    LEFT = 1
    RIGHT = 2
    JUMP = 3


TILE_MAPPING = {"#": 1, "X": 1, "-": -1, "*": 2, "E": 3, ".": 0}  # Barriers  # Void  # Coin  # End


@dataclass
class PlayerState:
    """Defines player state."""

    x: float = 0.0
    y: float = 0.0
    vel_x: float = 0.0
    vel_y: float = 0.0
    on_ground: bool = False


@dataclass
class PersistantStates:
    """Defines persistant stats"""

    config: Config
    total_best_distance: float = float("inf")


@dataclass
class Progress:
    """Defines players progress"""

    best_step_count: float = float("inf")
    total_distance: float = 0.0
    best_distance: float = float("inf")
    steps_since_progress: int = 0


@dataclass
class GameState:
    """Defines game state."""

    progress: Progress = field(default_factory=Progress)
    steps: int = 0
    coins_collected: int = 0
    start_time: float = 0.0
    current_game_time: int = 0
    game_over: bool = False
    game_completed: bool = False


@dataclass
class MapState:
    """Defines map state."""

    map: list = field(default_factory=list)
    width: int = 0
    height: int = 0
    start_x: int = 0
    start_y: int = 0
    end_pos: np.ndarray = field(default_factory=lambda: np.array([0, 0]))


@dataclass
class Bounds:
    """Player bounds wraper"""

    grid_left: int
    grid_right: int
    grid_top: int
    grid_bottom: int

    def __iter__(self):
        """For unpacking"""
        yield self.grid_left
        yield self.grid_right
        yield self.grid_top
        yield self.grid_bottom


class Game:
    """Defines entire game logic, physics, etc."""

    def __init__(self, config: Config):
        """Initializes game states.

        Args:
            map_path: Path to txt file containing map of the level
        """

        # Set timer
        self.game_timer = QElapsedTimer()

        self.persistant_states = PersistantStates(config=config)
        self.game_state = GameState()
        self.player_state = PlayerState()
        self.map_state = MapState()

        # Restart level initially
        self.restart_game()

    def load_map(self, map_path: str):
        """Loads map from path."""
        with open(map_path, "r", encoding="UTF-8") as file:
            self.map_state.map = [list(line.strip()) for line in file.readlines()]

            self.map_state.height = len(self.map_state.map)
            self.map_state.width = len(self.map_state.map[0])

    def find_player_start(self):
        """Finds player's starting position on the map."""

        self.map_state.end_pos = np.array([0, 0])

        for y, row in enumerate(self.map_state.map):
            for x, cell in enumerate(row):
                # If cell is Starting position
                if cell == "S":
                    # Replace position with Air
                    self.map_state.map[y][x] = "."
                    # Represents players feet position in sub-cell coordinates, this allows for more precise movement
                    self.map_state.start_x = TILE_SIZE * x
                    self.map_state.start_y = TILE_SIZE * y
                # Mark End coordinates
                if cell == "E":
                    self.map_state.end_pos = np.array([x, y])

    def restart_game(self):
        """Restarts game."""

        # Reset states
        self.game_state = GameState()
        self.player_state = PlayerState()
        self.map_state = MapState()

        self.load_map(self.persistant_states.config.map_path)

        self.find_player_start()
        self.player_state.x = self.map_state.start_x
        self.player_state.y = self.map_state.start_y

        # Set best distance
        player_pos_x = self.player_state.x / TILE_SIZE
        self.game_state.progress.best_distance = abs(player_pos_x - self.map_state.end_pos[0])

        # Restarts timer
        self.game_timer.start()

    def get_formatted_time(self):
        """Formats elapsed time"""

        seconds = (self.game_state.current_game_time // 1000) % 60
        minutes = self.game_state.current_game_time // 60000

        return f"{minutes:02}:{seconds:02}"

    def get_tile(self, x, y):
        """Return tile on map based on x, y coordinates"""
        if 0 <= y < self.map_state.height and 0 <= x < self.map_state.width:
            return self.map_state.map[y][x]
        return "None"

    def is_wall(self, x, y):
        """Check if the tile on coords (x, y) is wall or out of bounds."""
        return self.get_tile(x, y) in ("None", "#", "X")

    def check_collision_x_axis(self, bounds: Bounds, player_width):
        """Checks collision on x-axis."""
        grid_left, grid_right, grid_top, grid_bottom = bounds

        # If player is moving to the right
        if self.player_state.vel_x > 0:
            if self.is_wall(grid_right, grid_top) or self.is_wall(grid_right, grid_bottom):
                # Snap to the left edge of the wall
                self.player_state.x = (grid_right * TILE_SIZE) - player_width
                self.player_state.vel_x = 0

        # If player is moving to the left
        elif self.player_state.vel_x < 0:
            if self.is_wall(grid_left, grid_top) or self.is_wall(grid_left, grid_bottom):
                # Snap to the right edge of the wall
                self.player_state.x = (grid_left + 1) * TILE_SIZE
                self.player_state.vel_x = 0

    def check_collision_y_axis(self, bounds: Bounds, player_height):
        """Checks collision on y-axis."""
        grid_left, grid_right, grid_top, grid_bottom = bounds
        self.player_state.on_ground = False

        # If player is moving down (falling due to gravity)
        if self.player_state.vel_y > 0:
            if self.is_wall(grid_left, grid_bottom) or self.is_wall(grid_right, grid_bottom):
                # Snap on top of the floor
                self.player_state.y = (grid_bottom * TILE_SIZE) - player_height
                self.player_state.vel_y = 0
                self.player_state.on_ground = True
            else:
                self.player_state.on_ground = False

        # If player is moving up (jumping)
        if self.player_state.vel_y < 0:
            if self.is_wall(grid_left, grid_top) or self.is_wall(grid_right, grid_top):
                # Snap to the bottom top of the ceiling
                self.player_state.y = (grid_top + 1) * TILE_SIZE
                self.player_state.vel_y = 0

    def check_collisions(self, x_axis: bool):
        """Checks collisions and if needed, clips player's position

        Args:
            axis: If x_axis = True, then check collision for x axis, else check for y axes
        """
        player_dimensions = (TILE_SIZE, 2 * TILE_SIZE)

        # Calculate the edges of the player in pixels
        left_pixel = self.player_state.x
        right_pixel = self.player_state.x + player_dimensions[0] - 1
        top_pixel = self.player_state.y
        bottom_pixel = self.player_state.y + player_dimensions[1] - 1

        # Convert pixels to grid coordinates
        grid_left = int(left_pixel // TILE_SIZE)
        grid_right = int(right_pixel // TILE_SIZE)
        grid_top = int(top_pixel // TILE_SIZE)
        grid_bottom = int(bottom_pixel // TILE_SIZE)

        corners = [(grid_left, grid_top), (grid_right, grid_top), (grid_left, grid_bottom), (grid_right, grid_bottom)]

        # Check coint collision
        for gx, gy in corners:
            tile = self.get_tile(gx, gy)
            if tile == "*":
                self.game_state.coins_collected += 1
                # Replace coin with air upon collecting it
                self.map_state.map[gy][gx] = "."
            elif tile == "E":
                self.game_state.game_completed = True
                # print("Victory")
                self.game_state.progress.best_step_count = min(
                    self.game_state.progress.best_step_count, self.game_state.steps
                )
                return
            elif tile == "-":
                self.game_state.game_over = True
                # print("Game Over")
                return

        # Check wall collisions for x axis movement
        if x_axis:
            self.check_collision_x_axis(Bounds(grid_left, grid_right, grid_top, grid_bottom), player_dimensions[0])
        # Check wall collision for y axis movement
        else:
            self.check_collision_y_axis(Bounds(grid_left, grid_right, grid_top, grid_bottom), player_dimensions[1])

    def update(self, move: MovementDirection = MovementDirection.IDLE):
        """Runs one tick of game physics

        Args:
            move: New movement. Default movement is IDLE (no move)
        """

        # If level is finished (successfully) or game is over (player died), make no additional move
        if self.game_state.game_completed or self.game_state.game_over:
            return

        # Update time
        self.game_state.current_game_time = self.game_timer.elapsed()

        # Update steps
        self.game_state.steps += 1

        # Apply horizontal input
        if move == MovementDirection.LEFT:
            self.player_state.vel_x = -MOVE_SPEED
        elif move == MovementDirection.RIGHT:
            self.player_state.vel_x = MOVE_SPEED
        else:
            # Sliding effect (Might be annoying as hell)
            if self.player_state.vel_x > 0:
                self.player_state.vel_x = max(0, self.player_state.vel_x - X_VELOCITY_SLIDING)
            elif self.player_state.vel_x < 0:
                self.player_state.vel_x = min(0, self.player_state.vel_x + X_VELOCITY_SLIDING)

        # Apply vertical input (jump)
        if move == MovementDirection.JUMP and self.player_state.on_ground:
            self.player_state.vel_y = JUMP_STRENGTH
            self.player_state.on_ground = False

        # Apply gravity
        self.player_state.vel_y += GRAVITY
        # Limit falling speed
        self.player_state.vel_y = min(self.player_state.vel_y, MAX_FALLING_SPEED)

        self.player_state.x += self.player_state.vel_x
        self.check_collisions(x_axis=True)
        self.player_state.y += self.player_state.vel_y
        self.check_collisions(x_axis=False)

    def get_state(self, size=2):
        """Returns simplifed size x size grind around the player

        Args:
            size: Size of the grid
        """
        state = []

        # Player's position
        player_x = int(self.player_state.x // TILE_SIZE)
        player_y = int(self.player_state.y // TILE_SIZE)

        offset_x = (self.player_state.x % TILE_SIZE) / TILE_SIZE
        # offset_y = (self.y % TILE_SIZE) / TILE_SIZE

        # Player can stand on 1  TILE_SIZE, there is difference if he is on right edge, left edge or in the middle of the tile
        offset_state = 0
        if offset_x < 0.5:
            offset_state = 0  # Left side
        else:  # Right side
            offset_state = 1

        for y in range(-size, size + 1):
            row = []
            for x in range(-size, size + 1):
                tile = self.get_tile(player_x + x, player_y + y)
                row.append(TILE_MAPPING.get(tile, 0))
            state.append(row)

        vel_x_dir = 0
        if self.player_state.vel_x > 0.5:
            vel_x_dir = 1
        elif self.player_state.vel_x < -0.5:
            vel_x_dir = -1

        vel_y_dir = 0
        if self.player_state.vel_y > 0.5:
            vel_y_dir = 1
        elif self.player_state.vel_y < -0.5:
            vel_y_dir = -1

        state.append(
            [
                # offset_x,
                # offset_y,
                # self.vel_x / MOVE_SPEED,  # Normalized X velocity
                # self.vel_y / MAX_FALLING_SPEED,  # Normalized Y velocity
                offset_state,
                vel_x_dir,
                vel_y_dir,
                1 if self.player_state.on_ground else 0,  # Ground state
            ]
        )

        return state

    def step(self, action: int):
        """Executes one agent action and returns result of that action.

        Args:
            action: Type of action (0, 1, 2, etc..)
        """

        # Previously collected coins
        prev_coins = self.game_state.coins_collected

        # Make a move
        self.update(MovementDirection(action))

        reward = 0

        if self.game_state.coins_collected > prev_coins:
            reward += 50

        done = False

        if self.game_state.game_over:
            reward = -100
            done = True
        elif self.game_state.game_completed:
            reward = 500
            done = True
        else:
            # Add distance of player from the finish
            player_pos_x = self.player_state.x / TILE_SIZE
            distance = abs(player_pos_x - self.map_state.end_pos[0])
            diff = self.game_state.progress.best_distance - distance

            if diff > 0:
                self.game_state.progress.best_distance = distance
                self.game_state.progress.steps_since_progress = 0
                reward += diff * 10
            else:
                # Punish no progress in long time
                self.game_state.progress.steps_since_progress += 1
                if self.game_state.progress.steps_since_progress >= 175:
                    reward -= 50
                    done = True

            self.persistant_states.total_best_distance = min(self.persistant_states.total_best_distance, distance)

            # If player is on the right side of finish flag
            if player_pos_x > self.map_state.end_pos[0] + 1:
                reward -= 5.0

            # Penalty for existing
            reward -= 0.05

        next_state = self.get_state(self.persistant_states.config.visibility)
        return next_state, reward, done
