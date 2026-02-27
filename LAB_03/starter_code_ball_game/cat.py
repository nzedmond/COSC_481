from pyray import *
from os.path import join
from settings import * 

class Cat():
    def __init__(self):
        self.x = 640
        self.y = 320
        self.vy = 0
        # Physics constants chosen for realistic jumping:
        # Target: 0.6-1.0 second airtime, 150-200 pixel jump height
        # Formulas: airtime ≈ (2 * -jump_force) / gravity
        #          max_height ≈ (-jump_force)^2 / (2 * gravity)
        # Selected: gravity=2000, jump_force=-800
        # Calculation: airtime = (2 * 800) / 2000 = 1.6 / 2000 = 0.8 seconds
        #            max_height = (800)^2 / (2 * 2000) = 640000 / 4000 = 160 pixels
        # Reasoning: 0.8s airtime and 160px height are within target ranges (0.6-1.0s, 150-200px)
        #           Provides smooth, game-feel jumping without being too floaty or snappy
        self.gravity = 2000  # pixels/s^2
        self.jump_force = -800  # upward velocity (pixels/s)
        self.ground_y = 320
        self.is_jumping = False
        self.speed = 200  # pixels/sec for horizontal movement

    def startup(self):
        pass  # No texture needed, we'll draw a simple shape

    def update(self):
        dt = get_frame_time()
        
        # Horizontal movement
        vx = 0
        if is_key_down(KeyboardKey.KEY_RIGHT):
            vx += self.speed
        if is_key_down(KeyboardKey.KEY_LEFT):
            vx -= self.speed
        
        self.x += vx * dt
        
        # Jump input (using J key to avoid conflicts with SPACE)
        if is_key_pressed(KeyboardKey.KEY_J) and not self.is_jumping:
            self.start_jump()
        
        # Apply physics
        self.apply_physics(dt)

    def start_jump(self):
        self.vy = self.jump_force
        self.is_jumping = True

    def apply_physics(self, dt):
        self.vy += self.gravity * dt
        self.y += self.vy * dt
        
        # Landing detection
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.vy = 0
            self.is_jumping = False

    def draw(self):
        draw_circle_v(Vector2(self.x, self.y), 20, ORANGE)