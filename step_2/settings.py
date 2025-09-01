"""
settings.py
All the knobs in one place (screen size, colors, speeds).
This makes the game easy to tweak without hunting through code.
"""

from typing import Tuple

# Screen
WIDTH: int = 1900
HEIGHT: int = 1000
FPS: int = 60

# Stars
NUM_STARS: int = 1000
STAR_COLOR: Tuple[int, int, int] = (255, 255, 255)
STAR_RADIUS: int = 2

# Player rocket
PLAYER_START_Y: int = 250
PLAYER_MOVE_STEP: int = 10
ROCKET_X: int = 50
ROCKET_BODY_COLOR: Tuple[int, int, int] = (200, 200, 255)
ROCKET_NOSE_COLOR: Tuple[int, int, int] = (180, 0, 0)
ROCKET_WINDOW_COLOR: Tuple[int, int, int] = (0, 150, 255)
FLAME_COLOR: Tuple[int, int, int] = (255, 140, 0)
FLAME_MIN: int = 15
FLAME_MAX: int = 30

# Lasers
LASER_SPEED_X: int = 50
LASER_COLOR: Tuple[int, int, int] = (255, 0, 0)
LASER_WIDTH: int = 20
LASER_THICKNESS: int = 10
LASER_RIGHT_LIMIT: int = 1850

# Explosions
MAX_BLAST_RADIUS: int = 300

# Enemies
FIRST_SHIP_SPEED: int = 5
SPEED_UP_EVERY: int = 3  # every N destroys, increase enemy speed

# UI
SCORE_COLOR: Tuple[int, int, int] = (255, 255, 0)
SCORE_FONT_SIZE: int = 50
GAME_OVER_FONT_SIZE: int = 150
GAME_TITLE: str = "-<>- Johnny's Space Game -<>-"
