"""This file includes the entire game logic/physics"""

from enum import Enum

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


class Game:
    """Defines entire game logic, physics, etc."""

    def __init__(self, config: Config):
        """Initializes game states.

        Args:
            map_path: Path to txt file containing map of the level
        """
        self.config = config
        # Set timer
        self.game_timer = QElapsedTimer()
        self.current_game_time = 0.0

        # The best amount of steps to reach finish
        self.best_step_count = float("inf")

        # Total best distance throughout all games
        self.total_best_distance = float("inf")

        # Restart level initially
        self.restart_game()

    def load_map(self, map_path: str):
        """Loads map from path."""
        with open(map_path, "r", encoding="UTF-8") as file:
            self.map = [list(line.strip()) for line in file.readlines()]

            self.height = len(self.map)
            self.width = len(self.map[0])

    def find_player_start(self):
        """Finds player's starting position on the map."""

        self.end_pos = np.array([0, 0])

        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                # If cell is Starting position
                if cell == "S":
                    # Replace position with Air
                    self.map[y][x] = "."
                    # Represents players feet position in sub-cell coordinates, this allows for more precise movement
                    self.start_x = TILE_SIZE * x
                    self.start_y = TILE_SIZE * y
                # Mark End coordinates
                if cell == "E":
                    self.end_pos = np.array([x, y])

    def restart_game(self):
        """Restarts game."""

        # Load map
        self.map = []
        self.width = 0
        self.height = 0
        self.load_map(self.config.map_path)

        self.find_player_start()

        # Set player state
        self.x = self.start_x
        self.y = self.start_y

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.game_completed = False
        self.game_over = False
        self.steps = 0

        player_pos_x = self.x / TILE_SIZE
        self.best_distance = abs(player_pos_x - self.end_pos[0])

        # Stats
        self.game_timer.start()  # Restarts timer
        self.coins_collected = 0
        self.step_count = 0
        self.steps_since_progress = 0

    def get_formatted_time(self):
        """Formats elapsed time"""

        seconds = (self.current_game_time // 1000) % 60
        minutes = self.current_game_time // 60000

        return f"{minutes:02}:{seconds:02}"

    def get_tile(self, x, y):
        """Return tile on map based on x, y coordinates"""
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.map[y][x]
        return "None"

    def is_wall(self, x, y):
        """Check if the tile on coords (x, y) is wall or out of bounds."""
        return self.get_tile(x, y) in ("None", "#", "X")

    def check_collisions(self, x_axis: bool):
        """Checks collisions and if needed, clips player's position

        Args:
            axis: If x_axis = True, then check collision for x axis, else check for y axes
        """
        player_width = TILE_SIZE
        player_height = 2 * TILE_SIZE

        # Calculate the edges of the player in pixels
        left_pixel = self.x
        right_pixel = self.x + player_width - 1
        top_pixel = self.y
        bottom_pixel = self.y + player_height - 1

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
                self.coins_collected += 1
                # Replace coin with air upon collecting it
                self.map[gy][gx] = "."
            elif tile == "E":
                self.game_completed = True
                # print("Victory")
                if self.steps < self.best_step_count:
                    self.best_step_count = self.steps
                return
            elif tile == "-":
                self.game_over = True
                # print("Game Over")
                return

        # Check wall collisions for x axis movement
        if x_axis:

            # If player is moving to the right
            if self.vel_x > 0:
                if self.is_wall(grid_right, grid_top) or self.is_wall(grid_right, grid_bottom):
                    # Snap to the left edge of the wall
                    self.x = (grid_right * TILE_SIZE) - player_width
                    self.vel_x = 0

            # If player is moving to the left
            elif self.vel_x < 0:
                if self.is_wall(grid_left, grid_top) or self.is_wall(grid_left, grid_bottom):
                    # Snap to the right edge of the wall
                    self.x = (grid_left + 1) * TILE_SIZE
                    self.vel_x = 0

        # Check wall collision for y axis movement
        else:
            self.on_ground = False

            # If player is moving down (falling due to gravity)
            if self.vel_y > 0:
                if self.is_wall(grid_left, grid_bottom) or self.is_wall(grid_right, grid_bottom):
                    # Snap on top of the floor
                    self.y = (grid_bottom * TILE_SIZE) - player_height
                    self.vel_y = 0
                    self.on_ground = True
                else:
                    self.on_ground = False

            # If player is moving up (jumping)
            if self.vel_y < 0:
                if self.is_wall(grid_left, grid_top) or self.is_wall(grid_right, grid_top):
                    # Snap to the bottom top of the ceiling
                    self.y = (grid_top + 1) * TILE_SIZE
                    self.vel_y = 0

    def update(self, move: MovementDirection = MovementDirection.IDLE):
        """Runs one tick of game physics

        Args:
            move: New movement. Default movement is IDLE (no move)
        """

        # If level is finished (successfully) or game is over (player died), make no additional move
        if self.game_completed or self.game_over:
            return

        # Update time
        self.current_game_time = self.game_timer.elapsed()

        # Update steps
        self.steps += 1

        # Apply horizontal input
        if move == MovementDirection.LEFT:
            self.vel_x = -MOVE_SPEED
        elif move == MovementDirection.RIGHT:
            self.vel_x = MOVE_SPEED
        else:
            # Sliding effect (Might be annoying as hell)
            if self.vel_x > 0:
                self.vel_x = max(0, self.vel_x - X_VELOCITY_SLIDING)
            elif self.vel_x < 0:
                self.vel_x = min(0, self.vel_x + X_VELOCITY_SLIDING)

        # Apply vertical input (jump)
        if move == MovementDirection.JUMP and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

        # Apply gravity
        self.vel_y += GRAVITY
        # Limit falling speed
        self.vel_y = min(self.vel_y, MAX_FALLING_SPEED)

        # Apply the moves
        self.step_count += 1
        self.x += self.vel_x
        self.check_collisions(x_axis=True)
        self.y += self.vel_y
        self.check_collisions(x_axis=False)

    def get_state(self, size=2):
        """Returns simplifed size x size grind around the player

        Args:
            size: Size of the grid
        """
        state = []

        # Player's position
        player_x = int(self.x // TILE_SIZE)
        player_y = int(self.y // TILE_SIZE)

        offset_x = (self.x % TILE_SIZE) / TILE_SIZE
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
                # Barrier
                if tile in ("#", "X"):
                    row.append(1)
                # Void
                elif tile == "-":
                    row.append(-1)
                # Coin
                elif tile == "*":
                    row.append(2)
                # End
                elif tile == "E":
                    row.append(3)
                else:
                    row.append(0)
            state.append(row)

        vel_x_dir = 0
        if self.vel_x > 0.5:
            vel_x_dir = 1
        elif self.vel_x < -0.5:
            vel_x_dir = -1

        vel_y_dir = 0
        if self.vel_y > 0.5:
            vel_y_dir = 1
        elif self.vel_y < -0.5:
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
                1 if self.on_ground else 0,  # Ground state
            ]
        )

        return state

    def step(self, action: int):
        """Executes one agent action and returns result of that action.

        Args:
            action: Type of action (0, 1, 2, etc..)
        """

        # Previously collected coins
        prev_coins = self.coins_collected

        # Make a move
        self.update(MovementDirection(action))

        reward = 0

        if self.coins_collected > prev_coins:
            reward += 50

        done = False

        if self.game_over:
            reward = -100
            done = True
        elif self.game_completed:
            reward = 500
            done = True
        else:
            # Add distance of player from the finish
            player_pos_x = self.x / TILE_SIZE
            distance = abs(player_pos_x - self.end_pos[0])
            diff = self.best_distance - distance

            if diff > 0:
                self.best_distance = distance
                self.steps_since_progress = 0
                reward += diff * 10
            else:
                # Punish no progress in long time
                self.steps_since_progress += 1
                if self.steps_since_progress >= 175:
                    reward -= 50
                    done = True

            if distance < self.total_best_distance:
                self.total_best_distance = distance

            # If player is on the right side of finish flag
            if player_pos_x > self.end_pos[0] + 1:
                reward -= 5.0

            # Penalty for existing
            reward -= 0.05

        next_state = self.get_state(self.config.visibility)
        return next_state, reward, done
