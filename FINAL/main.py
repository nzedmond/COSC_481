from pyray import *
from player import Player
from level import Level

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Platformer Starter")

set_target_fps(60)

level = Level()
player = Player(100, 100)

camera = Camera2D()
camera.target = Vector2(player.x, player.y)
camera.offset = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
camera.rotation = 0.0
camera.zoom = 1.0

while not window_should_close():
    # --- UPDATE ---
    player.update(level)

    # Camera follows player
    camera.target = Vector2(player.x, player.y)

    # --- DRAW ---
    begin_drawing()
    clear_background(BLACK)

    begin_mode_2d(camera)

    level.draw()
    player.draw()

    end_mode_2d()

    draw_text("Platformer Starter", 10, 10, 20, WHITE)

    end_drawing()

close_window()