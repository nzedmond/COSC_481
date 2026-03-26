from pyray import *
from config.settings import *

class Player:
    """The snake head — owns position, velocity, and input state.

    Moves automatically to the right each frame; vertical direction is controlled
    by the player holding or releasing the control key.
    """

    def __init__(self):
        self.pos = Vector2(100, SCREEN_HEIGHT // 2)
        self.prev_pos = self.pos
        self.vel = Vector2(PLAYER_SPEED_X, 0.0)
        self.heading_up = False
        self.speed_mult = 1.0   # set each tick by the level's speed curve
        
    def apply_control(self, holding):
        self.heading_up = holding

    def update(self, dt):
        self.prev_pos = Vector2(self.pos.x, self.pos.y)
        vx = PLAYER_SPEED_X * self.speed_mult
        vy = -PLAYER_SPEED_Y if self.heading_up else PLAYER_SPEED_Y
        self.vel = Vector2(vx, vy)
        self.pos.x += vx * dt
        self.pos.y += vy * dt
        