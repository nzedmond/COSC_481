"""
Screen-space menu overlays drawn AFTER camera.end() and effects.draw().

Exported classes
----------------
MainMenu   — full-screen title / level-select screen
PauseMenu  — semi-transparent overlay while game is paused
GameOverMenu   — shown on death
LevelCompleteMenu — shown on reaching the level end
"""

from pyray import *
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT

# ── palette ────────────────────────────────────────────────────────────
_BG_FULL   = Color(0,   0,   0,  210)   # full-screen dim overlay
_BG_PANEL  = Color(15,  15,  25, 230)   # panel background
_COL_TITLE = Color(0,  220, 255, 255)   # cyan — matches trail head colour
_COL_HEAD  = WHITE
_COL_BODY  = Color(200, 200, 200, 255)
_COL_DIM   = Color(120, 120, 120, 255)
_COL_GOOD  = Color(80,  220, 100, 255)  # green  — level complete / new best
_COL_BAD   = Color(255,  80,  80, 255)  # red    — game over
_COL_KEY   = YELLOW
_COL_BORDER= Color(255, 255, 255,  40)

_CX = SCREEN_WIDTH  // 2
_CY = SCREEN_HEIGHT // 2


# ── helpers ─────────────────────────────────────────────────────────────

def _draw_panel(x, y, w, h):
    draw_rectangle(x, y, w, h, _BG_PANEL)
    draw_rectangle_lines(x, y, w, h, _COL_BORDER)


def _centered_text(text, cy, size, color):
    tw = measure_text(text, size)
    draw_text(text, _CX - tw // 2, cy, size, color)


def _key_hint(key_label: str, action: str, cy: int):
    full = f"[{key_label}]  {action}"
    _centered_text(full, cy, 14, _COL_KEY)


# ── MainMenu ────────────────────────────────────────────────────────────

class MainMenu:
    """
    Shown at startup.  Displays title, level list, and best scores.
    *levels* is a list of dicts: {"name": str, "path": str}
    *save_manager* is a SaveManager instance.
    """

    def __init__(self, levels: list, save_manager):
        self._levels      = levels
        self._save        = save_manager
        self._selected    = 0          # index into self._levels

    # ---- input ---------------------------------------------------------

    def handle_input(self) -> str | None:
        """
        Call every frame.  Returns one of:
          "play"  — start selected level
          None    — nothing happened yet
        """
        if is_key_pressed(KEY_DOWN):
            self._selected = (self._selected + 1) % len(self._levels)
        if is_key_pressed(KEY_UP):
            self._selected = (self._selected - 1) % len(self._levels)
        if is_key_pressed(KEY_ENTER) or is_key_pressed(KEY_SPACE):
            return "play"
        return None

    @property
    def selected_level_path(self) -> str:
        return self._levels[self._selected]["path"]

    @property
    def selected_level_name(self) -> str:
        return self._levels[self._selected]["name"]

    # ---- draw ----------------------------------------------------------

    def draw(self):
        # Full-screen background dim
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, _BG_FULL)

        # Title
        _centered_text("GEOMETRY SNAKE", _CY - 160, 48, _COL_TITLE)
        _centered_text("navigate the cave without touching walls",
                       _CY - 105, 14, _COL_DIM)

        # Level list panel
        panel_w = 420
        panel_h = 30 + len(self._levels) * 54 + 16
        panel_x = _CX - panel_w // 2
        panel_y = _CY - 60
        _draw_panel(panel_x, panel_y, panel_w, panel_h)

        for i, lvl in enumerate(self._levels):
            row_y   = panel_y + 16 + i * 54
            is_sel  = (i == self._selected)
            name_col = _COL_TITLE if is_sel else _COL_HEAD

            # Selection indicator
            if is_sel:
                draw_rectangle(panel_x + 4, row_y - 2,
                               panel_w - 8, 50,
                               Color(0, 220, 255, 18))

            _centered_text(lvl["name"], row_y, 20, name_col)

            best_score, best_pct, attempts = self._save.get_best(lvl["name"])
            if attempts == 0:
                stats = "No attempts yet"
                scol  = _COL_DIM
            else:
                stats = (f"Best: {best_score:,} pts  |  "
                         f"{best_pct:.1%} complete  |  "
                         f"{attempts} attempt{'s' if attempts != 1 else ''}")
                scol = _COL_BODY
            _centered_text(stats, row_y + 24, 12, scol)

        # Controls hint
        hint_y = panel_y + panel_h + 20
        _key_hint("UP / DOWN",    "select level",   hint_y)
        _key_hint("SPACE / ENTER", "start",      hint_y + 22)
        _key_hint("HOLD SPACE / MOUSE", "steer up", hint_y + 44)


# ── PauseMenu ────────────────────────────────────────────────────────────

class PauseMenu:
    def draw(self):
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
                       Color(0, 0, 0, 120))

        panel_w, panel_h = 300, 140
        _draw_panel(_CX - panel_w // 2, _CY - panel_h // 2, panel_w, panel_h)

        _centered_text("PAUSED", _CY - 46, 28, _COL_HEAD)
        _key_hint("P",   "resume",       _CY +  2)
        _key_hint("M", "quit to menu", _CY + 26)


# ── GameOverMenu ─────────────────────────────────────────────────────────

class GameOverMenu:
    """
    *score*      — score this run
    *best_score* — all-time best score for this level
    *pct*        — progress reached this run (0-1)
    *best_pct*   — all-time best progress
    *new_best*   — True if this run set a new record
    """

    def draw(self, score: int, best_score: int,
             pct: float, best_pct: float, new_best: bool):
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
                       Color(0, 0, 0, 150))

        panel_w, panel_h = 360, 200
        _draw_panel(_CX - panel_w // 2, _CY - panel_h // 2, panel_w, panel_h)

        _centered_text("GAME OVER", _CY - 82, 30, _COL_BAD)

        _centered_text(f"Score:    {score:,}",         _CY - 38, 18, _COL_HEAD)
        _centered_text(f"Reached:  {pct:.1%}",         _CY - 14, 18, _COL_HEAD)
        _centered_text(f"Best:     {best_score:,}  |  {best_pct:.1%}",
                       _CY + 10, 14, _COL_BODY)

        if new_best:
            _centered_text("NEW BEST!", _CY + 34, 16, _COL_GOOD)

        _key_hint("R",   "retry",        _CY + 60)
        _key_hint("M", "quit to menu", _CY + 82)


# ── LevelCompleteMenu ────────────────────────────────────────────────────

class LevelCompleteMenu:
    def draw(self, score: int, best_score: int,
             pct: float, best_pct: float, new_best: bool):
        draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT,
                       Color(0, 0, 0, 150))

        panel_w, panel_h = 360, 200
        _draw_panel(_CX - panel_w // 2, _CY - panel_h // 2, panel_w, panel_h)

        _centered_text("LEVEL COMPLETE!", _CY - 82, 28, _COL_GOOD)

        _centered_text(f"Score:  {score:,}",           _CY - 38, 18, _COL_HEAD)
        _centered_text(f"Best:   {best_score:,}  |  {best_pct:.1%}",
                       _CY - 14, 14, _COL_BODY)

        if new_best:
            _centered_text("NEW BEST!", _CY + 10, 16, _COL_GOOD)

        _key_hint("R",   "play again",   _CY + 50)
        _key_hint("M", "quit to menu", _CY + 72)
