from enum import Enum
import threading
import math

PLAYER_RATIO = 1 # Number of sub-cells per cell
GRAVITY_TIMER_INTERVAL = 0.05 # seconds
class MovementDirection(Enum):
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    JUMP = (0, -2)
    LEFT_JUMP = (-1, -2)
    RIGHT_JUMP = (1, -2)

class Game():
    def __init__(self, map_path: str = "maps/default.txt"):
        self.load_map(map_path)
        self.find_player_start()
        self.coins_collected = 0
        self.last_move = (0, 0)
        self.on_ground = False
        threading.Timer(GRAVITY_TIMER_INTERVAL, self.gravity).start()
    
    def load_map(self, map_path: str):
        with open(map_path, 'r') as file:
            self.map = [list(line.strip()) for line in file.readlines()]


    def find_player_start(self):
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                if cell == "S":
                    self.map[y][x] = "."
                    # Represents players feet position in sub-cell coordinates
                    self.player_position = (PLAYER_RATIO * x, PLAYER_RATIO * y)
                    return
      
    def move_player(self, new_pos: MovementDirection):
        if self.last_move[1] < 0 and dy < 0:
            return  # Prevent double jumpes
        
        # Ignore gravity moves 
        if dx != 0 and dy != 1:
            self.last_move = (dx, dy)
            
        x, y = self.player_position
        new_x, new_y = x + dx, y + dy
        
        # Check boundaries
        if new_y < 0 or new_y >= len(self.map) * PLAYER_RATIO :
            return
        if new_x < 0 or new_x >= len(self.map[0]) * PLAYER_RATIO:
            return
    
        target_cell_feet = self.map[new_y // PLAYER_RATIO][new_x // PLAYER_RATIO]
        target_cell_head = self.map[(new_y - PLAYER_RATIO) // PLAYER_RATIO][new_x // PLAYER_RATIO] if (new_y - PLAYER_RATIO) // PLAYER_RATIO >=0 else "X"
        
        # Check for collisions
        if target_cell_feet == "X" or target_cell_feet == "#":
            return  # Hit dirt, cannot move
        elif target_cell_feet == "*" or target_cell_head == "*":
            self.map[new_y // PLAYER_RATIO][new_x // PLAYER_RATIO] = "."  # Collect coin
        elif target_cell_feet == "E" or target_cell_head == "E":
            print("Level Complete!")  # Reached the end
        
        # Move player
        self.player_position = (new_x, new_y)
        
    def gravity(self):
        self.move_player(0, 1)
        threading.Timer(GRAVITY_TIMER_INTERVAL, self.gravity).start()