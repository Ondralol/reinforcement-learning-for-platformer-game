"""This file includes the entire game logic/physics"""

import threading
from enum import Enum

PLAYER_RATIO = 32  # Number of sub-cells per cell
GRAVITY_TIMER_INTERVAL = 0.05  # in seconds


class MovementDirection(Enum):
    """Defines all possible movement directions."""

    LEFT = (-1, 0)
    RIGHT = (1, 0)
    JUMP = (0, -2 * PLAYER_RATIO)
    DOWN = (0, 1)
    LEFT_JUMP = (-1, -2 * PLAYER_RATIO)
    RIGHT_JUMP = (1, -2 * PLAYER_RATIO)

    @property
    def dx(self):
        """Returns movement in x direction."""
        return self.value[0]

    @property
    def dy(self):
        """Returns movement in y direction."""
        return self.value[1]


class Game:
    """Defines entire game logic, physics, etc."""

    def __init__(self, map_path: str = "maps/default.txt"):
        """Initializes game states.

        Args:
            map_path: Path to txt file containing map of the level
        """

        self.load_map(map_path)

        # Set starting position of the player
        self.player_position = (-1, -1)
        self.find_player_start()

        self.coins_collected = 0
        self.level_finished = False

        # Set last move
        self.last_move = MovementDirection.DOWN

        # self.on_ground false is just in the case the player is spawned in the air, so he can fall to the ground correctly
        self.on_ground = False

        # Start gravity timer, that is run every GRAVITY_TIMER_INTERVAL seconds
        threading.Timer(GRAVITY_TIMER_INTERVAL, self.gravity).start()

    def load_map(self, map_path: str):
        """Loads map from path."""
        with open(map_path, "r", encoding="UTF-8") as file:
            self.map = [list(line.strip()) for line in file.readlines()]

    def find_player_start(self):
        """Finds player's starting position on the map."""
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                # If cell is Starting position
                if cell == "S":
                    # Replace position with Air
                    self.map[y][x] = "."
                    # Represents players feet position in sub-cell coordinates, this allows for more precise movement
                    self.player_position = (PLAYER_RATIO * x, PLAYER_RATIO * y)
                    return

    def move_player(self, move: MovementDirection):
        """Validate and make player movement."""

        move_x, move_y = move.dx, move.dy

        # If last move was a jump and current move is also a jump and player is not on groud then return.
        # We don't allow double (or more) jumps
        if self.last_move.dy < 0 and move_y < 0 and not self.on_ground:
            return

        new_x, new_y = self.player_position[0] + move_x, self.player_position[1] + move_y

        # Check boundaries of the map
        if new_y < 0 or new_y >= len(self.map) * PLAYER_RATIO:
            return
        if new_x < 0 or new_x >= len(self.map[0]) * PLAYER_RATIO:
            return

        # Calculate feet positionto check for floor colision
        target_cell_feet = self.map[new_y // PLAYER_RATIO][new_x // PLAYER_RATIO]
        target_cell_head = (
            self.map[(new_y - PLAYER_RATIO) // PLAYER_RATIO][new_x // PLAYER_RATIO]
            if (new_y - PLAYER_RATIO) // PLAYER_RATIO >= 0
            else "X"
        )

        # Check for collisions with Wall/Floor/Ceiling
        if target_cell_feet in ("X", "#") or target_cell_head in ("X", "#"):
            if move == MovementDirection.DOWN:
                self.on_ground = True
            # Cannot move
            return

        # Check for collision with Coin
        if target_cell_feet == "*" or target_cell_head == "*":
            # Replace coin with air and collect the coint
            self.map[new_y // PLAYER_RATIO][new_x // PLAYER_RATIO] = "."
            self.coins_collected = 0

        # Check for collision with Finish flag
        elif target_cell_feet == "E" or target_cell_head == "E":
            self.level_finished = True
            print("Level Complete!")  # Reached the end

        
        # If move was successful
        
        # Move player
        self.player_position = (new_x, new_y)
        
        # Update last move and don't count gravity moves as a previous move as it's not move made by player
        if move != MovementDirection.DOWN:
            self.last_move = move
            
        # If move was Jump, update self.on_ground
        if move in (MovementDirection.JUMP, MovementDirection.LEFT_JUMP, MovementDirection.RIGHT_JUMP):
            self.on_ground = False

    def gravity(self):
        """Apply gravity on the player."""

        # Move player down
        self.move_player(MovementDirection.DOWN)
        # Restart gravity timer
        threading.Timer(GRAVITY_TIMER_INTERVAL, self.gravity).start()
