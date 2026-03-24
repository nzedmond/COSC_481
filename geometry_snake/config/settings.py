SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

FIXED_DT = 1.0 / 60.0       # physics tick duration
MAX_ACCUMULATOR = 0.2        # clamp to avoid spiral of death (~12 ticks max)

PLAYER_SPEED_X = 250.0
PLAYER_SPEED_Y = 160.0

TRAIL_MAX_LENGTH = 500
TRAIL_MIN_STEP = 6.0
COLLISION_RADIUS = 8.0
COLLISION_MARGIN = 2.0       # forgiveness pixels shrunk from collision radius
SELF_COLLISION_SKIP = 8      # ignore this many newest trail points near head
LOOKAHEAD = 200.0            # x-range for AABB broad-phase culling

LEVEL_WIDTH = 5000           # default level length; overridden by JSON in Phase 4
DEFAULT_LEVEL = "levels/level1.json"

CAMERA_LERP = 0.08           # smoothing factor applied each fixed tick
CAMERA_LOOKAHEAD = 160       # world pixels ahead of player shown at screen centre
SHAKE_MAX_OFFSET = 8.0       # max pixel displacement at full trauma
SHAKE_DECAY = 3.0            # trauma units lost per second
SHAKE_DEATH_TRAUMA = 0.8     # trauma added on death

# Visual polish (Phase 5)
TRAIL_CORE_RADIUS  = 4.0     # base half-width of trail at speed_mult=1
TRAIL_GLOW_MULT    = 2.5     # glow layer width = core * this
TRAIL_GLOW_ALPHA   = 55      # alpha of glow layer at head (fades to 0 at tail)
TRAIL_GLOW_LENGTH  = 80      # segments near head that receive glow pass
PARTICLE_POOL_SIZE   = 200
PARTICLE_DEATH_COUNT = 25
PARTICLE_DEATH_SPEED = 180.0
FADE_DURATION      = 0.5     # seconds for level fade-in
VIGNETTE_LAYERS    = 20      # gradient bands drawn at screen edges
VIGNETTE_MAX_ALPHA = 160     # darkest alpha at screen corner
