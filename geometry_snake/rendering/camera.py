import random
from pyray import *
from config.settings import *


class Camera:
    """Smooth-follow camera with lookahead, level-bounds clamping, and screen shake.

    World objects are drawn between camera.begin() / camera.end().
    The camera itself is updated once per fixed physics tick.
    """

    def __init__(self, level_width=LEVEL_WIDTH,
                 lookahead=CAMERA_LOOKAHEAD, lerp=CAMERA_LERP):
        self.level_width = level_width
        self._lookahead  = lookahead
        self._lerp       = lerp
        self._lerp_x     = SCREEN_WIDTH / 2.0
        self._lerp_y     = SCREEN_HEIGHT / 2.0
        self._trauma     = 0.0

        self._cam = Camera2D()
        self._cam.offset = Vector2(SCREEN_WIDTH / 2.0, SCREEN_HEIGHT / 2.0)
        self._cam.target = Vector2(SCREEN_WIDTH / 2.0, SCREEN_HEIGHT / 2.0)
        self._cam.rotation = 0.0
        self._cam.zoom = 1.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, player_pos, dt):
        """Advance the camera by one fixed tick.

        Lerps toward player position + lookahead, clamps to level bounds,
        then applies a randomised shake offset proportional to trauma².
        """
        desired_x = player_pos.x + self._lookahead
        # Y is fixed — level height equals screen height, so no vertical scroll
        desired_y = SCREEN_HEIGHT / 2.0

        self._lerp_x += (desired_x - self._lerp_x) * self._lerp
        self._lerp_y += (desired_y - self._lerp_y) * self._lerp

        # Clamp so the view never shows empty space outside level bounds
        min_x = SCREEN_WIDTH / 2.0
        max_x = max(min_x, self.level_width - SCREEN_WIDTH / 2.0)
        clamped_x = max(min_x, min(self._lerp_x, max_x))

        self._cam.target = Vector2(clamped_x, self._lerp_y)

        # Decay trauma and compute randomised shake offset
        self._trauma = max(0.0, self._trauma - SHAKE_DECAY * dt)
        shake = self._trauma ** 2 * SHAKE_MAX_OFFSET
        self._cam.offset = Vector2(
            SCREEN_WIDTH / 2.0 + shake * (random.random() * 2.0 - 1.0),
            SCREEN_HEIGHT / 2.0 + shake * (random.random() * 2.0 - 1.0),
        )

    def add_trauma(self, amount):
        """Add screen-shake trauma (clamped to [0, 1])."""
        self._trauma = min(1.0, self._trauma + amount)

    def begin(self):
        begin_mode_2d(self._cam)

    def end(self):
        end_mode_2d()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def scroll_x(self):
        """World x-coordinate of the screen's left edge — used by parallax."""
        return self._cam.target.x - SCREEN_WIDTH / 2.0

    @property
    def trauma(self):
        return self._trauma
