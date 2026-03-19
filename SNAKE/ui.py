from pyray import *
from raylib import *
from settings import *

_CELL          = SNAKE_SIZE
_OFF_X         = WINDOW_WIDTH % _CELL
_PLAYABLE_H    = WINDOW_HEIGHT - HEADER_HEIGHT
_OFF_Y         = _PLAYABLE_H % _CELL

# Header bar geometry — change these to reposition everything at once
HDR_PAD  = 10   # inner padding from header edges


class UI:
    def draw_grid(self):
        # Vertical lines — full playable height
        for i in range(WINDOW_WIDTH // _CELL + 1):
            x = int(_CELL * i + _OFF_X / 2)
            draw_line(x, HEADER_HEIGHT, x, WINDOW_HEIGHT, LIGHTGRAY)
        # Horizontal lines — confined below the header
        for i in range(_PLAYABLE_H // _CELL + 1):
            y = HEADER_HEIGHT + int(_CELL * i + _OFF_Y / 2)
            draw_line(0, y, WINDOW_WIDTH, y, LIGHTGRAY)

    def draw_header(self, score, high_score):
        # Background + bottom border
        draw_rectangle(0, 0, WINDOW_WIDTH, HEADER_HEIGHT, DARKGRAY)
        draw_line(0, HEADER_HEIGHT, WINDOW_WIDTH, HEADER_HEIGHT, BLACK)
        # Score on the left
        draw_text(f"Score: {score}",      HDR_PAD,       HDR_PAD, 18, WHITE)
        draw_text(f"Best:  {high_score}", HDR_PAD + 130, HDR_PAD, 18, LIGHTGRAY)
        # Controls hint on the right
        draw_text("Arrow Keys  |  [ ] Speed  |  P Pause",
                  WINDOW_WIDTH - 290, HDR_PAD + 2, 14, GRAY)

    def draw_menu(self):
        draw_text("SNAKE", WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 3, 50, DARKGREEN)
        draw_text("Press ENTER to play", WINDOW_WIDTH // 2 - 110, WINDOW_HEIGHT // 2, 20, DARKGRAY)
        draw_text("Arrow keys to move  |  [ ] to change speed", WINDOW_WIDTH // 2 - 185, WINDOW_HEIGHT // 2 + 30, 18, GRAY)

    def draw_active_powerups(self, active_powerups):
        """Draw a column of icons on the right edge of the play area."""
        if not active_powerups:
            return
        x = WINDOW_WIDTH - 28
        y = HEADER_HEIGHT + 6
        for p in active_powerups:
            # Icon
            draw_rectangle(x, y, 18, 18, p.color)
            draw_text(p.label, x + 4, y + 3, 12, BLACK)
            # Vertical timer bar (shrinks downward as the effect expires)
            draw_rectangle(x + 20, y, 4, 18, DARKGRAY)
            bar_h = int(18 * p.ratio)
            if bar_h > 0:
                draw_rectangle(x + 20, y + (18 - bar_h), 4, bar_h, p.color)
            y += 26

    def draw_game_over(self, score, high_score):
        draw_text("GAME OVER", WINDOW_WIDTH // 2 - 115, WINDOW_HEIGHT // 3, 48, RED)
        draw_text(f"Score: {score}", WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 2, 24, BLACK)
        draw_text(f"Best:  {high_score}", WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 2 + 32, 24, DARKGRAY)
        draw_text("ENTER - Play Again  |  M - Menu", WINDOW_WIDTH // 2 - 165, WINDOW_HEIGHT // 2 + 80, 20, DARKGRAY)
