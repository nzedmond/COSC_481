from pyray import *
from raylib import *
from settings import *

_CELL = SNAKE_SIZE
_OFF_X = WINDOW_WIDTH  % _CELL
_OFF_Y = WINDOW_HEIGHT % _CELL

# HUD rectangle — all elements inside are positioned relative to (HUD_X, HUD_Y)
HUD_X, HUD_Y = 10, 20
HUD_W, HUD_H = 160, 50
HUD_PAD      = 8   # inner padding


class UI:
    def draw_grid(self):
        for i in range(WINDOW_WIDTH // _CELL + 1):
            x = int(_CELL * i + _OFF_X / 2)
            draw_line(x, int(_OFF_Y / 2), x, int(WINDOW_HEIGHT - _OFF_Y / 2), LIGHTGRAY)
        for i in range(WINDOW_HEIGHT // _CELL + 1):
            y = int(_CELL * i + _OFF_Y / 2)
            draw_line(int(_OFF_X / 2), y, int(WINDOW_WIDTH - _OFF_X / 2), y, LIGHTGRAY)

    def draw_instructions(self):
        draw_text("Movement: ARROW KEYS  |  Speed: [ ]  |  Pause: P", 20, 10, 10, DARKGRAY)

    def draw_menu(self):
        draw_text("SNAKE", WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 3, 50, DARKGREEN)
        draw_text("Press ENTER to play", WINDOW_WIDTH // 2 - 110, WINDOW_HEIGHT // 2, 20, DARKGRAY)
        draw_text("Arrow keys to move  |  [ ] to change speed", WINDOW_WIDTH // 2 - 185, WINDOW_HEIGHT // 2 + 30, 18, GRAY)

    def draw_hud(self, score, high_score):
        # Container
        draw_rectangle(HUD_X, HUD_Y, HUD_W, HUD_H, LIGHTGRAY)
        draw_rectangle_lines(HUD_X, HUD_Y, HUD_W, HUD_H, DARKGRAY)
        # Elements — positioned relative to the container's top-left corner
        draw_text(f"Score: {score}",      HUD_X + HUD_PAD, HUD_Y + HUD_PAD,      18, BLACK)
        draw_text(f"Best:  {high_score}", HUD_X + HUD_PAD, HUD_Y + HUD_PAD + 22, 18, DARKGRAY)

    def draw_game_over(self, score, high_score):
        draw_text("GAME OVER", WINDOW_WIDTH // 2 - 115, WINDOW_HEIGHT // 3, 48, RED)
        draw_text(f"Score: {score}", WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 2, 24, BLACK)
        draw_text(f"Best:  {high_score}", WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 2 + 32, 24, DARKGRAY)
        draw_text("ENTER - Play Again  |  M - Menu", WINDOW_WIDTH // 2 - 165, WINDOW_HEIGHT // 2 + 80, 20, DARKGRAY)
