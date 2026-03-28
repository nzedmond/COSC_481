from pyray import *
from settings import *


class Camera:
    def __init__(self, level_width=LEVEL_WIDTH, lookahead=CAMERA_LOOKAHEAD, lerp=CAMERA_LERP):
        self.level_width  = level_width
        self._lookahead   = lookahead
        self._lerp        = lerp
        self._smooth_x    = SCREEN_WIDTH / 2.0
        self._smooth_y    = SCREEN_HEIGHT / 2.0
        self._raylib_cam            = Camera2D()
        self._raylib_cam.offset     = Vector2(SCREEN_WIDTH / 2.0, SCREEN_HEIGHT / 2.0)
        self._raylib_cam.target     = Vector2(SCREEN_WIDTH / 2.0, SCREEN_HEIGHT / 2.0)
        self._raylib_cam.rotation   = 0.0
        self._raylib_cam.zoom       = 1.0

    def update(self, player_pos, dt):
        self._smooth_x += (player_pos.x + self._lookahead - self._smooth_x) * self._lerp
        self._smooth_y += (SCREEN_HEIGHT / 2.0 - self._smooth_y) * self._lerp
        min_x     = SCREEN_WIDTH / 2.0
        max_x     = max(min_x, self.level_width - SCREEN_WIDTH / 2.0)
        clamped_x = max(min_x, min(self._smooth_x, max_x))
        self._raylib_cam.target = Vector2(clamped_x, self._smooth_y)
        self._raylib_cam.offset = Vector2(SCREEN_WIDTH / 2.0, SCREEN_HEIGHT / 2.0)

    def begin(self):  begin_mode_2d(self._raylib_cam)
    def end(self):    end_mode_2d()

    @property
    def scroll_x(self):
        return self._raylib_cam.target.x - SCREEN_WIDTH / 2.0
