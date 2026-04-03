from raylib import *
from pyray import *
from settings import *
from game import Game

current_game = Game()

if __name__ == '__main__':
    init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Snake")
    set_target_fps(60)

    current_game.startup()

    while not window_should_close():
        current_game.update()

        begin_drawing()
        current_game.draw()
        end_drawing()
        

    close_window()

current_game.shutdown()
