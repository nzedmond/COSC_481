from pyray import *
from raylib import *
from settings import *

_MODE_LABELS = {
    Mode.CLASSIC: "CLASSIC",
    Mode.TIME_ATTACK: "TIME ATTACK",
    Mode.SURVIVAL: "SURVIVAL",
}

_CELL = SNAKE_SIZE
_OFF_X = WINDOW_WIDTH % _CELL
_PLAYABLE_H = WINDOW_HEIGHT - HEADER_HEIGHT
_OFF_Y = _PLAYABLE_H % _CELL

# Header bar geometry — change these to reposition everything at once
HDR_PAD  = 10   # inner padding from header edges


class UI:
    def draw_grid(self):
        for i in range(WINDOW_WIDTH // _CELL + 1):
            x = int(_CELL * i + _OFF_X / 2)
            draw_line(x, HEADER_HEIGHT, x, WINDOW_HEIGHT, LIGHTGRAY)
        for i in range(_PLAYABLE_H // _CELL + 1):
            y = HEADER_HEIGHT + int(_CELL * i + _OFF_Y / 2)
            draw_line(0, y, WINDOW_WIDTH, y, LIGHTGRAY)

    def draw_header(self, score, high_score, mode=None, time_left=0, score_pop_timer=0):
        draw_rectangle(0, 0, WINDOW_WIDTH, HEADER_HEIGHT, DARKGRAY)
        draw_line(0, HEADER_HEIGHT, WINDOW_WIDTH, HEADER_HEIGHT, BLACK)
        if score_pop_timer > 0:
            ratio = score_pop_timer / SCORE_POP_DURATION
            score_size = int(18 + 8 * ratio)
            score_col  = Color(255, int(255 * (1 - ratio * 0.5)), 0, 255)
        else:
            score_size = 18
            score_col  = WHITE
        draw_text(f"Score: {score}",      HDR_PAD,       HDR_PAD, score_size, score_col)
        draw_text(f"Best:  {high_score}", HDR_PAD + 130, HDR_PAD, 18,         LIGHTGRAY)
        
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
            draw_text(tag, WINDOW_WIDTH // 2 - 100, HDR_PAD, 16, color)
            
        draw_text("Arrow Keys  |  [ ] Speed  |  P Pause",
                  WINDOW_WIDTH - 290, HDR_PAD + 2, 14, GRAY)

    def draw_menu(self, selected_mode=0):
        draw_text("SNAKE", WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 4, 50, DARKGREEN)

        # Mode selector
        modes = list(_MODE_LABELS.values())
        item_h = 32
        start_y = WINDOW_HEIGHT // 2 - (len(modes) * item_h) // 2
        
        for i, label in enumerate(modes):
            y = start_y + i * item_h
            active = (i == selected_mode)
            color = GREEN if active else DARKGRAY
            prefix = "> " if active else "  "
            draw_text(prefix + label, WINDOW_WIDTH // 2 - 90, y, 22, color)

        draw_text("Up/Down to select  |  ENTER to play",
                  WINDOW_WIDTH // 2 - 175, WINDOW_HEIGHT - 70, 16, GRAY)
        draw_text("I  -  How to play",
                  WINDOW_WIDTH // 2 - 88, WINDOW_HEIGHT - 44, 16, DARKGRAY)

    def draw_instructions(self):
        draw_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, Color(20, 20, 20, 255))
        draw_text("HOW TO PLAY", WINDOW_WIDTH // 2 - 120, 20, 36, GREEN)
        draw_line(40, 64, WINDOW_WIDTH - 40, 64, DARKGRAY)

        cx, cy = 50, 80
        draw_text("CONTROLS", cx, cy, 20, LIGHTGRAY)
        rows = [
            ("Arrow Keys",    "Move the snake"),
            ("[ ]",           "Decrease / increase speed"),
            ("P",             "Pause / resume"),
            ("ENTER",         "Start / restart game"),
            ("M",             "Return to menu (game over)"),
            ("I / BACKSPACE", "Open / close this screen"),
        ]
        
        for i, (key, desc) in enumerate(rows):
            y = cy + 28 + i * 26
            draw_text(key,  cx,       y, 16, YELLOW)
            draw_text(desc, cx + 160, y, 16, WHITE)

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

        draw_line(40, 290, WINDOW_WIDTH - 40, 290, DARKGRAY)
        draw_text("POWER-UPS", 50, 298, 20, LIGHTGRAY)
        draw_text("(white-bordered pickups — appear every 5 s)", 200, 300, 14, GRAY)

        powerups = [
            (YELLOW,  "H  Shield",  "Absorbs the next lethal collision (10 s)"),
            (LIME,    "Z  Shrink",  "Instantly removes 3 tail segments"),
        ]
        
        cols = [(50, 322), (430, 322)]
        for i, (color, name, effect) in enumerate(powerups):
            px, py = cols[i % 2]
            row_y  = py + (i // 2) * 72
            draw_rectangle(px, row_y, 20, 20, WHITE)
            draw_rectangle(px + 2, row_y + 2, 16, 16, color)
            draw_text(name,   px + 28, row_y,      16, color)
            draw_text(effect, px + 28, row_y + 20, 13, GRAY)

        draw_line(40, 464, WINDOW_WIDTH - 40, 464, DARKGRAY)
        draw_text("OBSTACLES", 50, 472, 20, LIGHTGRAY)
        draw_rectangle(50, 498, 16, 16, BROWN)
        draw_rectangle_lines(50, 498, 16, 16, BLACK)
        draw_text("Wall segment — avoid or use Shield to survive one hit",
                  74, 500, 14, WHITE)
        draw_text(f"A new wall spawns every {OBSTACLE_SPAWN_EVERY} points  (max {OBSTACLE_MAX})",
                  74, 518, 13, GRAY)

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
            draw_rectangle(x, y, 18, 18, p.color)
            draw_text(p.label, x + 4, y + 3, 12, BLACK)
            draw_rectangle(x + 20, y, 4, 18, DARKGRAY)
            bar_h = int(18 * p.ratio)
            if bar_h > 0:
                draw_rectangle(x + 20, y + (18 - bar_h), 4, bar_h, p.color)
            y += 26

    def draw_food_pops(self, pops):
        """Expanding + fading square at each recently eaten food position."""
        for pos, color, timer in pops:
            ratio = timer / FOOD_POP_DURATION
            size = int(FOOD_SIZE * (1 + ratio))
            alpha = int(255 * (1 - ratio))
            offset = (size - FOOD_SIZE) // 2
            draw_rectangle(
                int(pos.x) - offset,
                int(pos.y) - offset,
                size, size,
                color,
            )

    def draw_debug_overlay(self, game):
        X, Y = 6, HEADER_HEIGHT + 6
        LH, PAD = 15, 5
        head = game.snake.body[0]
        tx = int(head.x) // SNAKE_SIZE
        ty = int(head.y - HEADER_HEIGHT) // SNAKE_SIZE
        pu = [p.label for p in game.snake.active_powerups]
        
        lines = [
            f"FPS {get_fps()}",
            f"mode={game.mode.name}  score={game.score}  time={game.time_left}",
            f"head=({int(head.x)}, {int(head.y)})  tile=({tx}, {ty})  len={game.snake.length}  iv={game.snake.move_interval}",
            f"food={game.food.food_type.name}  pos=({int(game.food.position.x)}, {int(game.food.position.y)})",
            f"powerups=[{', '.join(pu) if pu else 'none'}]",
            ("GOD  " if game.god_mode else "") + "DEBUG ON  |  D=toggle  G=god  F=eat  N=spawn power-up",
        ]
        
        W = 400
        H = len(lines) * LH + PAD * 2
        draw_rectangle(X - PAD, Y - PAD, W, H, Color(0, 0, 0, 180))
        
        for i, line in enumerate(lines):
            draw_text(line, X, Y + i * LH, 12, LIME)

    def draw_paused(self, selected):
        overlay_x = WINDOW_WIDTH // 2 - 100
        overlay_y = WINDOW_HEIGHT // 2 - 60
        draw_rectangle(overlay_x, overlay_y, 200, 120, Color(0, 0, 0, 200))
        draw_rectangle_lines(overlay_x, overlay_y, 200, 120, DARKGRAY)
        draw_text("GAME PAUSED", overlay_x + 10, overlay_y + 12, 24, WHITE)
        draw_line(overlay_x + 10, overlay_y + 42, overlay_x + 190, overlay_y + 42, DARKGRAY)
        options = ["RESUME", "EXIT"]
        
        for i, label in enumerate(options):
            color = GREEN if i == selected else LIGHTGRAY
            prefix = "> " if i == selected else "  "
            draw_text(prefix + label, overlay_x + 30, overlay_y + 54 + i * 30, 20, color)

    def draw_game_over(self, score, high_score):
        draw_rectangle_gradient_v(210, 180, 380, 230, BLUE, BLACK)
        draw_text("GAME OVER", WINDOW_WIDTH // 2 - 115, WINDOW_HEIGHT // 3, 48, RED)
        draw_text(f"Score: {score}", WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 2, 24, BLACK)
        draw_text(f"Best:  {high_score}", WINDOW_WIDTH // 2 - 55, WINDOW_HEIGHT // 2 + 32, 24, DARKGRAY)
        draw_text("ENTER - Play Again  |  M - Menu", WINDOW_WIDTH // 2 - 165, WINDOW_HEIGHT // 2 + 80, 20, DARKGRAY)
