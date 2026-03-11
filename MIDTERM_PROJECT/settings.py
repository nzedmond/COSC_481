from raylib import *
from pyray import *
from enum import Enum

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600


class Screen(Enum):
    MENU      = 0
    GAMEPLAY  = 1
    PAUSED    = 2
    GAME_OVER = 3


# ------------------CONSTANTS FOR SNAKE--------------------
SNAKE_LENGTH = 1
SNAKE_SIZE = 20
SNAKE_SPEED_MIN = 5
SNAKE_COLOR = GREEN

# ------------------CONSTANTS FOR FOOD---------------------
FOOD_SIZE = 20
FOOD_COLOR = RED
