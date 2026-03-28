from pyray import *
from settings import *

from enum import IntEnum

# Warm-up difference with class code: couple of addition and fixes
# have been done

# This demo is using a different sheet; and has a own main to demo
# provided capability of class Animation
# It is just a proof of concept of the code we study in class

# Main task: Integrate with your own main.py, class Game/Player

# Your class Game and Player should use clean update function
# based on a planned state machine diagram of the action (state/transition)
# player can undergo

class AnimationType(IntEnum):
    REPEATING = 1
    ONESHOT = 2

class Direction(IntEnum):
    LEFT = -1
    RIGHT = 1

class Animation:
    def __init__(self, first, last, cur, step, duration, duration_left, anim_type, row, sprites_in_row):
        self.first = first
        self.last = last
        self.cur = cur
        self.step = step
        self.duration = duration
        self.duration_left = duration_left
        self.type = anim_type
        self.row = row
        self.sprites_in_row = sprites_in_row 
        self.done = False

    def update(self, dt):
        self.duration_left -= dt
        
        if (self.duration_left<=0):
            #print(self.cur, self.type)
            self.duration_left = self.duration
            self.cur += self.step

            if (self.cur > self.last):
                match(self.type):
                    case AnimationType.ONESHOT:
                        self.cur = self.last 
                        self.done = True
                    case AnimationType.REPEATING:
                        self.cur = self.first 

    def frame(self, row):  # FIXES happened there to generalize to sprite sheet
        x = (self.cur % self.sprites_in_row) * SPRITE_SHEET_TILE_SIZE
        y =  SPRITE_SHEET_TILE_SIZE * self.row

        return Rectangle(x, y, SPRITE_SHEET_TILE_SIZE, SPRITE_SHEET_TILE_SIZE)

    def reset(self): # ADDED
        self.cur = self.first
        self.done = False
        self.type = AnimationType.REPEATING


def test():
    init_window(600, 400, "Animation demo")

    player_idle_texture = load_texture(SHEET)
    player_direction = Direction.LEFT

    anim = Animation(
        first=3, last=0, cur=0,
        step=-1, duration=0.1, duration_left=0.1,
        anim_type=AnimationType.REPEATING,
        #anim_type=AnimationType.ONESHOT, #does not work fully; 
                                # will need some change provided through Player
        row=5, sprites_in_row=4,)

    anim2 = Animation(
        first=0, last=2, cur=0,
        step=1, duration=0.1, duration_left=0.1,
        anim_type=AnimationType.REPEATING,
        row=9, sprites_in_row=4,)

    while not window_should_close():
        if is_key_pressed(KEY_SPACE): # stop the animation
            anim.cur = anim.first

        if is_key_pressed(KEY_A):     
            player_direction = Direction.LEFT
        elif is_key_pressed(KEY_D):
            player_direction = Direction.RIGHT

        anim.update(get_frame_time())
        anim2.update(get_frame_time())

        begin_drawing()
        clear_background(SKYBLUE)

        player_frame = anim.frame(5) # hard-coded state
        player_frame.width *= player_direction

        draw_texture_pro(
            player_idle_texture,
            anim2.frame(9),  # again not best, 
                    # but demonstrate capability provided by frame
            Rectangle(200, 10, 100, 100), 
            Vector2(0, 0), 0.0, WHITE,
        )

        draw_texture_pro(
            player_idle_texture,
            player_frame,
            Rectangle(10, 10, 100, 100),
            Vector2(0, 0), 0.0, WHITE,
        )
        end_drawing()

    unload_texture(player_idle_texture)
    close_window()
      
if __name__ == "__main__":
    test()