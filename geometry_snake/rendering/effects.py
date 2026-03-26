"""
Screen-space overlay effects — drawn AFTER camera.end() so they sit on top
of all world objects.

  • Fade-in: black overlay that dissolves over FADE_DURATION seconds on level load.
  • Vignette: permanent dark gradient at screen edges for depth/framing.
"""

from pyray import *
from config.settings import *


class ScreenEffects:
    def __init__(self):
        self._fade_alpha  = 255.0
        self._fading_in   = False

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def start_fade_in(self):
        self._fade_alpha = 255.0
        self._fading_in  = True

    # ------------------------------------------------------------------
    # Update  (call once per fixed physics tick)
    # ------------------------------------------------------------------

    def update(self, dt):
        if self._fading_in:
            self._fade_alpha -= (255.0 / FADE_DURATION) * dt
            if self._fade_alpha <= 0.0:
                self._fade_alpha = 0.0
                self._fading_in  = False

    # ------------------------------------------------------------------
    # Draw  (call in screen space, after camera.end())
    # ------------------------------------------------------------------

    def draw(self):
        self._draw_vignette()
        if self._fade_alpha > 0.0:
            draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
                           Color(0, 0, 0, int(self._fade_alpha)))


    @staticmethod
    def _draw_vignette():
        """Draw VIGNETTE_LAYERS concentric dark bands at each screen edge."""
        for i in range(VIGNETTE_LAYERS):
            t     = 1.0 - i / VIGNETTE_LAYERS
            alpha = int(VIGNETTE_MAX_ALPHA * t * t)
            c     = Color(0, 0, 0, alpha)
            draw_rectangle(0,                        i,                      SCREEN_WIDTH,  1, c)
            draw_rectangle(0,                        SCREEN_HEIGHT - 1 - i,  SCREEN_WIDTH,  1, c)
            draw_rectangle(i,                        0,                      1, SCREEN_HEIGHT, c)
            draw_rectangle(SCREEN_WIDTH - 1 - i,     0,                      1, SCREEN_HEIGHT, c)
