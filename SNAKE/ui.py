from pyray import *
from raylib import *
from settings import *

_MODE_LABELS = {
    Mode.CLASSIC:     "CLASSIC",
    Mode.TIME_ATTACK: "TIME ATTACK",
    Mode.SURVIVAL:    "SURVIVAL",
    Mode.MAZE:        "MAZE",
}

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

    def draw_header(self, score, high_score, mode=None, time_left=0):
        # Background + bottom border
        draw_rectangle(0, 0, WINDOW_WIDTH, HEADER_HEIGHT, DARKGRAY)
        draw_line(0, HEADER_HEIGHT, WINDOW_WIDTH, HEADER_HEIGHT, BLACK)
        # Score on the left
        draw_text(f"Score: {score}",      HDR_PAD,       HDR_PAD, 18, WHITE)
        draw_text(f"Best:  {high_score}", HDR_PAD + 130, HDR_PAD, 18, LIGHTGRAY)
        # Mode tag + timer (centre)
        if mode is not None and mode != Mode.CLASSIC:
            tag = _MODE_LABELS[mode]
            if mode == Mode.TIME_ATTACK:
                secs = max(0, time_left // 60)
                tag += f"  {secs}s"
                color = YELLOW if secs > 10 else RED
            elif mode == Mode.SURVIVAL:
                color = ORANGE
            else:
                color = SKYBLUE
            draw_text(tag, WINDOW_WIDTH // 2 - 20, HDR_PAD, 16, color)
        # Controls hint on the right
        draw_text("Arrow Keys  |  [ ] Speed  |  P Pause",
                  WINDOW_WIDTH - 290, HDR_PAD + 2, 14, GRAY)

    def draw_menu(self, selected_mode=0):
        # self.draw_grid() # DELETE AFTER MEASURING SCREEN DIMENSIONS !!!!!!!!!!!!!!!
        # draw_rectangle_gradient_v(280, 140, 260, 240, Color(112, 128, 144, 255), Color(47, 79, 79, 255))
        draw_text("SNAKE", WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 4, 50, DARKGREEN)

        # Mode selector
        modes      = list(_MODE_LABELS.values())
        item_h     = 32
        start_y    = WINDOW_HEIGHT // 2 - (len(modes) * item_h) // 2
        for i, label in enumerate(modes):
            y       = start_y + i * item_h
            active  = (i == selected_mode)
            color   = GREEN if active else DARKGRAY
            prefix  = "> " if active else "  "
            draw_text(prefix + label, WINDOW_WIDTH // 2 - 90, y, 22, color)

        draw_text("Up/Down to select  |  ENTER to play",
                  WINDOW_WIDTH // 2 - 175, WINDOW_HEIGHT - 70, 16, GRAY)
        draw_text("I  -  How to play",
                  WINDOW_WIDTH // 2 - 88, WINDOW_HEIGHT - 44, 16, DARKGRAY)

    def draw_instructions(self):
        # ── Background ────────────────────────────────────────────────────────
        draw_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, Color(20, 20, 20, 255))

        # ── Title ─────────────────────────────────────────────────────────────
        draw_text("HOW TO PLAY", WINDOW_WIDTH // 2 - 120, 20, 36, GREEN)
        draw_line(40, 64, WINDOW_WIDTH - 40, 64, DARKGRAY)

        # ── Controls (left column) ────────────────────────────────────────────
        cx, cy = 50, 80
        draw_text("CONTROLS", cx, cy, 20, LIGHTGRAY)
        rows = [
            ("Arrow Keys",  "Move the snake"),
            ("[ ]",         "Decrease / increase speed"),
            ("P",           "Pause / resume"),
            ("ENTER",       "Start / restart game"),
            ("M",           "Return to menu (game over)"),
            ("I / BACKSPACE", "Open / close this screen"),
        ]
        for i, (key, desc) in enumerate(rows):
            y = cy + 28 + i * 26
            draw_text(key,  cx,       y, 16, YELLOW)
            draw_text(desc, cx + 160, y, 16, WHITE)

        # ================ Food types (right column) =========================
        fx, fy = 450, 80
        draw_text("FOOD TYPES", fx, fy, 20, LIGHTGRAY)
        foods = [
            (RED,    "Normal",  "+1 score,  grow"),
            (GOLD,   "Golden",  "+3 score,  grow  (rare)"),
            (PURPLE, "Poison",  "-1 score,  shrink  (fades in 5 s)"),
            (ORANGE, "Moving",  "+2 score,  bounces around"),
        ]
        for i, (color, name, effect) in enumerate(foods):
            y = fy + 28 + i * 36
            draw_rectangle(fx, y, 16, 16, color)
            draw_text(name,   fx + 24, y,      16, color)
            draw_text(effect, fx + 24, y + 18, 13, GRAY)

        # ========================== Power-ups ===================================
        draw_line(40, 290, WINDOW_WIDTH - 40, 290, DARKGRAY)
        draw_text("POWER-UPS", 50, 298, 20, LIGHTGRAY)
        draw_text("(white-bordered pickups — appear every 5 s)", 200, 300, 14, GRAY)

        powerups = [
            (SKYBLUE, "S  Speed Boost", "Move interval -3 for 5 s"),
            (YELLOW,  "H  Shield",      "Absorbs the next lethal collision (10 s)"),
            (PINK,    "M  Magnet",      "Pulls food toward your head for 5 s"),
            (LIME,    "Z  Shrink",      "Instantly removes 3 tail segments"),
        ]
        cols = [(50, 322), (430, 322)]
        for i, (color, name, effect) in enumerate(powerups):
            px, py = cols[i % 2]
            row_y  = py + (i // 2) * 72
            draw_rectangle(px, row_y, 20, 20, WHITE)
            draw_rectangle(px + 2, row_y + 2, 16, 16, color)
            draw_text(name,   px + 28, row_y,      16, color)
            draw_text(effect, px + 28, row_y + 20, 13, GRAY)

        # ── Obstacles ─────────────────────────────────────────────────────────
        draw_line(40, 464, WINDOW_WIDTH - 40, 464, DARKGRAY)
        draw_text("OBSTACLES", 50, 472, 20, LIGHTGRAY)
        draw_rectangle(50, 498, 16, 16, BROWN)
        draw_rectangle_lines(50, 498, 16, 16, BLACK)
        draw_text("Wall segment — avoid or use Shield to survive one hit",
                  74, 500, 14, WHITE)
        draw_text(f"A new wall spawns every {OBSTACLE_SPAWN_EVERY} points  (max {OBSTACLE_MAX})",
                  74, 518, 13, GRAY)

        # ── Footer ────────────────────────────────────────────────────────────
        draw_line(40, WINDOW_HEIGHT - 36, WINDOW_WIDTH - 40, WINDOW_HEIGHT - 36, DARKGRAY)
        draw_text("I or BACKSPACE  -  Back to menu",
                  WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 26, 16, DARKGRAY)

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
        draw_rectangle_gradient_v(210, 180, 380, 230, GRAY, RAYWHITE)
        draw_text("GAME OVER", WINDOW_WIDTH // 2 - 115, WINDOW_HEIGHT // 3, 48, RED)
        draw_text(f"Score: {score}", WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 2, 24, BLACK)
        draw_text(f"Best:  {high_score}", WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 2 + 32, 24, DARKGRAY)
        draw_text("ENTER - Play Again  |  M - Menu", WINDOW_WIDTH // 2 - 165, WINDOW_HEIGHT // 2 + 80, 20, DARKGRAY)
