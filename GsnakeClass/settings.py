from pyray import *

#  General constants
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
FPS           = 60

# Player/trail constants
FIXED_DT        = 1.0 / 60.0
MAX_ACCUMULATOR = 0.2
TRAIL_CORE_RADIUS  = 4.0
TRAIL_GLOW_MULTIPLIER = 2.5
TRAIL_GLOW_ALPHA   = 55
TRAIL_GLOW_LENGTH  = 80

PLAYER_SPEED_X = 250.0
PLAYER_SPEED_Y = 160.0

TRAIL_MAX_LENGTH = 500
TRAIL_MIN_STEP   = 6.0
LOOKAHEAD        = 200.0

# camera/level constants
LEVEL_WIDTH      = 5000
CAMERA_LERP      = 0.08
CAMERA_LOOKAHEAD = 160

# particle/collectible constants
PARTICLE_POOL_SIZE   = 200
PARTICLE_DEATH_COUNT = 25
PARTICLE_DEATH_SPEED = 180.0
FADE_DURATION      = 0.5
VIGNETTE_LAYERS    = 20
VIGNETTE_MAX_ALPHA = 160

# parallax background constants

PARALLAX_LAYER_CONFIGS = [
    {"speed": 0.15, "color": Color(18, 12, 28, 255),  "count": 25, "min_w": 60,  "max_w": 150, "min_h": 80,  "max_h": 200},
    {"speed": 0.35, "color": Color(28, 20, 45, 255),  "count": 20, "min_w": 30,  "max_w": 80,  "min_h": 40,  "max_h": 120},
    {"speed": 0.65, "color": Color(40, 30, 65, 255),  "count": 30, "min_w": 10,  "max_w": 30,  "min_h": 20,  "max_h":  60},
]
CAVE_BACKGROUND_COLOR = Color(8, 6, 16, 255)