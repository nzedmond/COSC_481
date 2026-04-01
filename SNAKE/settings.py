from raylib import *
from pyray import *
from enum import Enum

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600


class Screen(Enum):
    MENU         = 0
    GAMEPLAY     = 1
    PAUSED       = 2
    GAME_OVER    = 3
    INSTRUCTIONS = 4


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

# Poison food lifespan in frames (300 = 5 seconds at 60 fps)
FOOD_POISON_LIFESPAN = 300

# Eat animation: expanding + fading square at the eaten food's position
FOOD_POP_DURATION  = 20   # frames
SCORE_POP_DURATION = 20   # frames the score text stays enlarged

# ------------------POWER-UPS---------------------
POWERUP_SIZE           = 20
POWERUP_SPAWN_INTERVAL = 300   # frames between pickups (~5 s at 60 fps)

class PowerupType(Enum):
    SPEED_BOOST = 0
    SHIELD      = 1
    MAGNET      = 2
    SHRINK      = 3

POWERUP_SPEED_BOOST_DURATION = 300   # 5 s
POWERUP_SHIELD_DURATION      = 600   # 10 s (or until a collision)
POWERUP_MAGNET_DURATION      = 300   # 5 s
POWERUP_SHRINK_DURATION      = 1     # instant

POWERUP_SPEED_BOOST_AMOUNT   = 3     # frames subtracted from move_interval
POWERUP_SHRINK_SEGMENTS      = 3     # tail segments removed instantly

# ------------------GAME MODES--------------------
class Mode(Enum):
    CLASSIC     = 0
    TIME_ATTACK = 1
    SURVIVAL    = 2
TIME_ATTACK_DURATION    = 3600  # 60 s at 60 fps
SURVIVAL_SPEED_INTERVAL = 5     # every N points, move_interval drops by 1

# ------------------OBSTACLES---------------------
OBSTACLE_SIZE        = 20
OBSTACLE_COLOR       = BROWN
OBSTACLE_SPAWN_EVERY = 3    # new wall segment every N points scored
OBSTACLE_MAX         = 20   # cap so the board never fills up
