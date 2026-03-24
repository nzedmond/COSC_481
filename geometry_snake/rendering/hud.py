"""
HUD drawn in screen space — call AFTER camera.end() and effects.draw().

Layout (top-left corner):
  ┌───────────────────────┐
  │  SCORE          1 750 │
  │  ● ● ◌ ◌ ◌   3 / 5   │
  └───────────────────────┘

Dots represent individual collectibles (filled = collected).
If the level has more than MAX_DOTS collectibles the dots are replaced
by a plain "X / Y" counter to avoid overflow.
"""

from pyray import *
from config.settings import *

_PANEL_W    = 200
_PANEL_H    = 58
_PANEL_X    = 8
_PANEL_Y    = 8
_MAX_DOTS   = 12

_COL_LABEL  = Color(160, 160, 160, 255)
_COL_SCORE  = WHITE
_COL_HIT    = YELLOW
_COL_MISS   = Color(90, 90, 90, 255)
_COL_BG     = Color(0, 0, 0, 150)
_COL_BORDER = Color(255, 255, 255, 30)


class HUD:
    def draw(self, score_manager):
        sm = score_manager

        # Background panel
        draw_rectangle(_PANEL_X, _PANEL_Y, _PANEL_W, _PANEL_H, _COL_BG)
        draw_rectangle_lines(_PANEL_X, _PANEL_Y, _PANEL_W, _PANEL_H, _COL_BORDER)

        # Row 1 — score
        draw_text("SCORE", _PANEL_X + 10, _PANEL_Y + 10, 12, _COL_LABEL)
        score_str = f"{sm.score:,}"
        draw_text(score_str, _PANEL_X + _PANEL_W - 10 - measure_text(score_str, 18),
                  _PANEL_Y + 8, 18, _COL_SCORE)

        # Row 2 — collectible indicators
        row_y = _PANEL_Y + 36
        if sm.total <= _MAX_DOTS:
            for i in range(sm.total):
                cx = _PANEL_X + 14 + i * 15
                if i < sm.collected:
                    draw_circle(cx, row_y, 5, _COL_HIT)
                else:
                    draw_circle_lines(cx, row_y, 5, _COL_MISS)
        else:
            counter = f"{sm.collected} / {sm.total}"
            draw_text("ITEMS", _PANEL_X + 10, row_y - 6, 12, _COL_LABEL)
            draw_text(counter,  _PANEL_X + 60, row_y - 7, 14, _COL_HIT)
