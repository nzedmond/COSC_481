from pyray import *
from config.settings import *

class Player:
    def __init__(self):
        self.pos = Vector2(100, SCREEN_HEIGHT // 2)
        self.prev_pos = self.pos
        self.heading_up = False
        
    def apply_control(self, holding):
        self.heading_up = holding
        
    def update(self, dt):
        self.prev_pos = Vector2(self.pos.x, self.pos.y)
        vy = -PLAYER_SPEED_Y if self.heading_up else PLAYER_SPEED_Y
        self.pos.x += PLAYER_SPEED_X * dt
        self.pos.y += vy * dt
        