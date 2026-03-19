from raylib import *
from pyray import *
from enum import Enum

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600


class Screen(Enum):
    MENU      = 0
    GAMEPLAY  = 1
    PAUSED    = 2
    GAME_OVER = 3


# ------------------HEADER / PLAYABLE AREA-----------------
HEADER_HEIGHT = 40   # px reserved at the top for HUD + instructions (2 grid cells)

# ------------------CONSTANTS FOR SNAKE--------------------
SNAKE_LENGTH   = 1
SNAKE_SIZE     = 20
SNAKE_COLOR    = GREEN
SNAKE_MOVE_INTERVAL = 5   # Frames between moves; lower = faster

# ------------------CONSTANTS FOR FOOD---------------------
FOOD_SIZE  = 20

class FoodType(Enum):
    NORMAL = 0
    GOLDEN = 1   # rare, +3 score, grows snake
    POISON = 2   # shrinks snake, negative score
    MOVING = 3   # bounces around the play area, +2 score

# Colors per food type
FOOD_NORMAL_COLOR = RED
FOOD_GOLDEN_COLOR = GOLD
FOOD_POISON_COLOR = PURPLE
FOOD_MOVING_COLOR = ORANGE

# Score delta per food type
FOOD_NORMAL_SCORE = 1
FOOD_GOLDEN_SCORE = 3
FOOD_POISON_SCORE = -1
FOOD_MOVING_SCORE = 2

# Spawn probability for non-normal types (remaining chance = NORMAL)
FOOD_GOLDEN_CHANCE = 0.15
FOOD_POISON_CHANCE = 0.15
FOOD_MOVING_CHANCE = 0.10

# Moving food pixel speed per frame
FOOD_MOVING_SPEED = 2
