"""This file includes the entire game logic/physics"""

import threading
from enum import Enum, auto

TILE_SIZE = 32  # 32 pixels in one block
GRAVITY = 0.5  # Downward acceleration per frame
JUMP_STRENGTH = -12.0  # Upward velocity when jumping
MOVE_SPEED = 3.0  # Horizontal speed in pixels per frame
X_VELOCITY_SLIDING = 0.10 # Sliding effect for X-axis velocity
MAX_FALLING_SPEED = 10.0 # Maximal Y axis falling speed

class MovementDirection(Enum):
    """Defines all possible movement directions."""

    IDLE = auto()
    LEFT = auto()
    RIGHT = auto()
    JUMP = auto()


class Game:
    """Defines entire game logic, physics, etc."""

    def __init__(self, map_path: str = "maps/default.txt"):
        """Initializes game states.

        Args:
            map_path: Path to txt file containing map of the level
        """
        # Load map
        self.map = []
        self.width = 0
        self.height = 0
        self.load_map(map_path)

        # Set player state
        self.x = 0.0
        self.y = 0.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.coins_collected = 0
        self.level_finished = False
        self.find_player_start()

    def load_map(self, map_path: str):
        """Loads map from path."""
        with open(map_path, "r", encoding="UTF-8") as file:
            self.map = [list(line.strip()) for line in file.readlines()]

            self.height = len(self.map)
            self.width = len(self.map[0])

    def find_player_start(self):
        """Finds player's starting position on the map."""
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                # If cell is Starting position
                if cell == "S":
                    # Replace position with Air
                    self.map[y][x] = "."
                    # Represents players feet position in sub-cell coordinates, this allows for more precise movement
                    self.x = (TILE_SIZE * x)
                    self.y = TILE_SIZE * y
                    return

    def get_tile(self, x, y):
        """Return tile on map based on x, y coordinates """
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
                self.map[gy][gx] = '.'
            elif tile == "E":
                self.level_finished = True
                print("Victory")
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

        # If level is finished, make no additional move
        if self.level_finished:
            return

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
        if self.vel_y > MAX_FALLING_SPEED:
            self.vel_y = MAX_FALLING_SPEED
            
        # Apply the moves
        self.x += self.vel_x
        self.check_collisions(x_axis = True)
        self.y += self.vel_y
        self.check_collisions(x_axis = False)
        