from pyray import *
from game import *
from settings import *

 
if __name__ == "__main__":

    init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Sprite sheet demo")
    set_target_fps(FPS)
    current_game = Game()


    current_game.startup()

    while not window_should_close():
        current_game.update()

        begin_drawing()
        clear_background(PINK)


        current_game.draw()

        end_drawing()

    close_window()
    current_game.shutdown()