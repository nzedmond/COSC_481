from pyray import *
from falling_objects import Game

# ----------------------- DEFINE CONSTANTS/GLOBALS -------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

current_game = Game()

if __name__ == "__main__":
    init_window(WINDOW_WIDTH, WINDOW_HEIGHT, b"Catch the Falling Objects")
    set_target_fps(60)
    
    while not window_should_close():
        current_game.update()
        begin_drawing()
        clear_background(RAYWHITE)
        
        current_game.draw()
        
        end_drawing()
        
close_window()

current_game.shutdown()
    