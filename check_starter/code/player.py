from pyray import *
from settings import *
from enum import Enum
from anim import *

class State(Enum):
    STANDING = 1
    RUNNING = 2
    

class Player:
    def __init__(self):
        self.sprite_str = SHEET
        self.size = PLAYER_SIZE
        self.sprite = load_texture(self.sprite_str)
        self.position = Vector2(380.0, 220.0)
        self.anim = Animation(first=3, last=0, cur=0, step=-1, duration=0.1, duration_left=0.1, anim_type=AnimationType.ONESHOT, row=5, sprites_in_row=2)
        
    def startup(self):
        pass
    
    def update(self):
        pass
        
    
    def draw(self):
        player_frame = self.anim.frame(2)
        draw_texture_pro(self.sprite, player_frame, Rectangle(200, 10, 100, 100), Vector2(0, 0), 0.0, WHITE)

        
        
        

        
        
        
    