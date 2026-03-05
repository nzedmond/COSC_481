from pyray import *
from os.path import join
from settings import * 

# ------ global variables -----
max_height = 0

class CalibrationCircle:
    def __init__(self):
        self.radius = CAL_RADIUS
        self.position = Vector2(100, 50)
        self.color = RED
        self.isVisible = False
    
    def draw(self):
        draw_circle_v(self.position, self.radius, self.color)
    
    def update(self):
        '''Listen for C Key to enter calibration mode. Listen for mouse click to draw the circle'''
        if is_key_pressed(KeyboardKey.KEY_C):
            self.isVisible = not self.isVisible
        
        if is_mouse_button_pressed(0):
            self.position = get_mouse_position()
            max_height = self.position.y
            print(f"max-height = {max_height}")
    
    
class Cat():
    def __init__(self):
        self.x = 40
        self.y = 550
        self.uy = 0
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
        self.ground_y = self.y
        self.is_jumping = False
        self.speed = 200  # pixels/sec for horizontal movement
        self.jump_height = max_height
    
    def update(self):
        dt = get_frame_time()
        
        # Horizontal movement
        vx = 0
        if is_key_down(KeyboardKey.KEY_RIGHT):
            vx += self.speed
        if is_key_down(KeyboardKey.KEY_LEFT):
            vx -= self.speed
        
        # screen bounds check for horizontal movement
        new_x = self.x + vx * dt
        self.x = max(0, min(new_x, WINDOW_WIDTH))
        
        self.x += vx * dt
        
        
        # Jump input (using J key to avoid conflicts with SPACE)
        if is_key_pressed(KeyboardKey.KEY_J) and not self.is_jumping:
            self.start_jump()
        
        # Apply physics
        self.apply_physics(dt)

    def start_jump(self):
        self.uy = self.jump_force
        self.is_jumping = True

    def apply_physics(self, dt):
        '''uy decreases(becomes more positive) as the ball goes up. It reaches 0 at the apex.'''
        self.uy += self.gravity * dt
        self.y += self.uy * dt
        print(f"Y={self.y}")
        
        # Landing detection
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.uy = 0
            self.is_jumping = False

    def draw(self):
        draw_circle_v(Vector2(self.x, self.y), 20, ORANGE)
        
        
class Ball():
    def __init__(self, radius, position, velocity):
        self.radius = radius
        self.position = position
        self.velocity = velocity

    def update(self):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

        # Check walls collision for bouncing
        if (self.position.x > WINDOW_WIDTH or self.position.x <= 0):
            self.velocity.x = self.velocity.x * -1.0


        if (self.position.y >=  WINDOW_HEIGHT  or self.position.y <= self.radius):
            self.velocity.y =  self.velocity.y * - 1.0

    def draw(self):
        #draw_circle_lines_v(self.position, self.radius, BLACK)
        draw_circle_v(self.position, self.radius+5, BLACK)
        draw_circle_v(self.position, self.radius, DARKPURPLE)


class Game:
    def __init__(self):
        self.visible = True
        self.moving = False
        self.ball = Ball(10, Vector2(100, 100),
                Vector2(2.0, 2.5))
        self.cat = Cat()
        self.calibDot = CalibrationCircle()

    # where game assets/resources will be initialized
    def startup(self):
        pass
        
    def update(self):
       self.visible = not is_key_down(KeyboardKey.KEY_SPACE) # change it to a toogle
       
       if is_key_pressed(KeyboardKey.KEY_S): # change it to a toogle
           self.moving = not self.moving
           
       if self.visible and self.moving: 
           self.calibDot.update()
           self.ball.update()#, self.screenWidth, 0, self.screenHeight)
           self.cat.update()
           if (is_key_down(KeyboardKey.KEY_RIGHT_BRACKET)):
               self.cat.speed += 20
           if (is_key_down(KeyboardKey.KEY_LEFT_BRACKET)):
               self.cat.speed -= 20
        
    def draw(self):
        draw_fps(20, 20)
        draw_text("Press SPACE to toggle visibility", 20, 50, 10, DARKGRAY)
        draw_text("Press S to toggle movement", 20, 70, 10, DARKGRAY)
        draw_text("Use LEFT/RIGHT to move horizontally", 20, 90, 10, DARKGRAY)
        draw_text("Press J to jump", 20, 110, 10, DARKGRAY)
        draw_text("Use [ and ] to adjust speed", 20, 130, 10, DARKGRAY)
        
        if (self.visible):
            self.ball.draw()
            self.cat.draw()
        if self.visible and self.moving:
            self.calibDot.draw()
        elif not self.visible:      
            draw_text("Invisible!", 200, 200, 40, WHITE)

    def shutdown(self):
        pass

