"""
HUD drawn in screen space — call AFTER camera.end() and effects.draw().

Layout (top-left corner):
  ┌───────────────────────┐
  │  SCORE          1 750 │
  │  ● ● ◌ ◌ ◌   3 / 5   │
  └───────────────────────┘

Progress bar at bottom of screen:
  [████████░░░░░░░░░░░░]  64%

Dots represent individual collectibles (filled = collected).
If the level has more than MAX_DOTS collectibles the dots are replaced
by a plain "X / Y" counter to avoid overflow.
"""

from pyray import *
from config.settings import *

PANEL_W    = 200
PANEL_H    = 58
PANEL_X    = 8
PANEL_Y    = 8
MAX_DOTS   = 12

COL_LABEL  = Color(160, 160, 160, 255)
COL_SCORE  = WHITE
COL_HIT    = YELLOW
COL_MISS   = Color(90, 90, 90, 255)
COL_BG     = Color(0, 0, 0, 150)
COL_BORDER = Color(255, 255, 255, 30)

# Progress bar
BAR_H      = 6
BAR_MARGIN = 40  # left + right 
BAR_Y      = SCREEN_HEIGHT - 16
COL_BAR_BG = Color(40,  40,  40,  200)
COL_BAR_FG = Color(0,  220, 255,  220)   # cyan, matches trail head


class HUD:
    def draw(self, score_manager, progress: float = 0.0):
        score_mgr = score_manager

        # Background panel
        draw_rectangle(PANEL_X, PANEL_Y, PANEL_W, PANEL_H, COL_BG)
        draw_rectangle_lines(PANEL_X, PANEL_Y, PANEL_W, PANEL_H, COL_BORDER)

        # Row 1 — score
        draw_text("SCORE", PANEL_X + 10, PANEL_Y + 10, 12, COL_LABEL)
        score_str = f"{score_mgr.score:,}"
        draw_text(score_str, PANEL_X + PANEL_W - 10 - measure_text(score_str, 18),
                  PANEL_Y + 8, 18, COL_SCORE)

        # Row 2 — collectible indicators
        row_y = PANEL_Y + 36
        if score_mgr.total <= MAX_DOTS:
            for i in range(score_mgr.total):
                center_x = PANEL_X + 14 + i * 15
                if i < score_mgr.collected:
                    draw_circle(center_x, row_y, 5, COL_HIT)
                else:
                    draw_circle_lines(center_x, row_y, 5, COL_MISS)
        else:
            counter = f"{score_mgr.collected} / {score_mgr.total}"
            draw_text("ITEMS", PANEL_X + 10, row_y - 6, 12, COL_LABEL)
            draw_text(counter,  PANEL_X + 60, row_y - 7, 14, COL_HIT)

        # Progress bar at bottom of screen
        bar_w    = SCREEN_WIDTH - BAR_MARGIN * 2
        filled_w = int(bar_w * max(0.0, min(1.0, progress)))
        draw_rectangle(BAR_MARGIN, BAR_Y, bar_w,    BAR_H, COL_BAR_BG)
        if filled_w > 0:
            draw_rectangle(BAR_MARGIN, BAR_Y, filled_w, BAR_H, COL_BAR_FG)
        percentage_str = f"{progress:.0%}"
        draw_text(percentage_str,
                  BAR_MARGIN + bar_w + 8,
                  BAR_Y - 2, 12, COL_LABEL)
