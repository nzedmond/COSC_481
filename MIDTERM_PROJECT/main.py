from raylib import *
from food import Food
from snake import Snake
from snakeGame import Game
from pyray import *
from settings import *

current_game = Game()
if __name__ == '__main__':  

  init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Mid-Project: Snake Game")
  set_target_fps(60)

  current_game.startup()

  while not window_should_close():

    current_game.update()
      
    begin_drawing()
    clear_background(GRAY)

    current_game.draw()

    end_drawing()

close_window()
  
current_game.shutdown()