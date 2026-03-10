from pyray import *
from os.path import join
from settings import * 

# ------ global variables -----
max_height = None

class CalibrationCircle:
    def __init__(self):
        self.radius = CAL_RADIUS
        self.position = Vector2(100, 50)
        self.color = RED
        self.isVisible = False
    
    def draw(self):
        if self.isVisible:
            draw_circle_v(self.position, self.radius, self.color)
    
    def update(self):
        '''Listen for C Key to enter calibration mode. Listen for mouse click to draw the circle'''
        if is_key_pressed(KeyboardKey.KEY_C):
            self.isVisible = not self.isVisible
        
        if is_mouse_button_pressed(0):
            # draw_text("Calibration wrt to t_apex", 200, 200, 20, BLACK)
            self.position = get_mouse_position()
            global max_height
            max_height = self.position.y
            # print(f"max-height = {max_height}")
    
    
class Cat():
    def __init__(self):
        self.x = 40
        self.y = 550
        self.uy = 0
        '''FOR LAB 6: Implementing three different jump modes: The first mode is a fixed-time jump, where the jump height is determined by the time it takes to reach the apex. The second mode is a lateral-distance jump, where the jump height is determined by the horizontal distance traveled during the jump. The third mode is a restitution bounce jump, where the character bounces back up after landing based on a restitution coefficient.'''
        
        # ----------- JUMP CALIBRATION VARIABLES -------------
        self.gravity = 2000  # pixels/s^2
        self.time_to_apex = 0.4  # seconds (time from jump start to max height)
        self.ground_y = self.y
        self.is_jumping = False
        self.speed = 200  # pixels/sec for horizontal movement
        self.jump_force = -800  # upward velocity (pixels/s)
        self.last_facing_dir = 1

        # ----------- ADDITIONAL JUMP MODES -------------
        self.target_lateral_distance = 220  # pixels
        self.restitution_e = 0.6  # 0 < e < 1
        self.min_bounce_speed = 90  # stop bouncing below this speed
        self.active_jump_mode = "time"
        self.locked_air_vx = 0  # For distance-based jump, we lock the horizontal velocity at jump start to calculate the jump profile and maintain it during the jump
    
    def update(self):
        dt = get_frame_time()
        
        # Horizontal movement
        vx = 0
        if is_key_down(KeyboardKey.KEY_RIGHT):
            vx += self.speed
        if is_key_down(KeyboardKey.KEY_LEFT):
            vx -= self.speed

        if vx > 0:
            self.last_facing_dir = 1
        elif vx < 0:
            self.last_facing_dir = -1
        
        # Jump input
        if is_key_pressed(KeyboardKey.KEY_J) and not self.is_jumping:
            self.start_jump("time", vx)

        if is_key_pressed(KeyboardKey.KEY_K) and not self.is_jumping:
            self.start_jump("distance", vx)

        if is_key_pressed(KeyboardKey.KEY_L) and not self.is_jumping:
            self.start_jump("restitution", vx)

        horizontal_vx = vx
        if self.is_jumping and self.active_jump_mode == "distance":
            horizontal_vx = self.locked_air_vx
        
        # Apply physics
        self.apply_physics(dt, horizontal_vx)

    def start_jump(self, mode, current_vx):
        if mode == "distance":
            launch_vx = self.get_launch_vx(current_vx)
            self.gravity, self.jump_force = self.get_jump_profile_from_lateral_distance(
                launch_vx
            )
            self.locked_air_vx = launch_vx
        else:
            self.gravity, self.jump_force = self.get_jump_profile_from_calibration_and_time()
            self.locked_air_vx = 0

        self.active_jump_mode = mode
        self.uy = self.jump_force
        self.is_jumping = True

    def get_launch_vx(self, current_vx):
        '''Read key inputs to determine the direction of teh launch velocity. If no input, use the last facing direction.'''
        if current_vx > 0:
            return current_vx
        if current_vx < 0:
            return current_vx
        return self.last_facing_dir * self.speed

    def get_target_jump_height(self):
        '''Determine the target jump height based on the calibrated max height. If no calibration, use a default value.'''
        global max_height

        if max_height is None:
            return 160

        target_y = max(0, min(max_height, self.ground_y))
        jump_height = self.ground_y - target_y
        if jump_height <= 0:
            return 160

        return jump_height

    def get_jump_profile_from_calibration_and_time(self):
        jump_height = self.get_target_jump_height()

        if self.time_to_apex <= 0:
            return self.gravity, -800

        gravity = (2 * jump_height) / (self.time_to_apex * self.time_to_apex)
        jump_force = -(gravity * self.time_to_apex)

        return gravity, jump_force

    def get_jump_profile_from_lateral_distance(self, launch_vx):
        jump_height = self.get_target_jump_height()
        speed_x = abs(launch_vx)

        if speed_x <= 0:
            speed_x = self.speed

        total_flight_time = self.target_lateral_distance / speed_x
        if total_flight_time <= 0:
            total_flight_time = 0.4

        time_to_apex = total_flight_time / 2
        if time_to_apex <= 0:
            time_to_apex = 0.2

        gravity = (2 * jump_height) / (time_to_apex * time_to_apex)
        jump_force = -(gravity * time_to_apex)
        return gravity, jump_force

    def apply_physics(self, dt, horizontal_vx):
        new_x = self.x + horizontal_vx * dt
        self.x = max(0, min(new_x, WINDOW_WIDTH))

        if not self.is_jumping:
            return

        '''uy decreases(becomes more positive) as the ball goes up. It reaches 0 at the apex.'''
        self.uy += self.gravity * dt
        self.y += self.uy * dt
        # print(f"Y={self.y}")
        
        # Landing detection
        if self.y >= self.ground_y:
            self.y = self.ground_y

            if self.active_jump_mode == "restitution":
                impact_speed = self.uy
                bounce_speed = -self.restitution_e * impact_speed

                if abs(bounce_speed) < self.min_bounce_speed:
                    self.uy = 0
                    self.is_jumping = False
                else:
                    self.uy = bounce_speed
            else:
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
        draw_text("J: fixed-time jump", 20, 110, 10, DARKGRAY)
        draw_text("K: lateral-distance jump", 20, 130, 10, DARKGRAY)
        draw_text("L: restitution bounce jump", 20, 150, 10, DARKGRAY)
        draw_text("Use [ and ] to adjust speed", 20, 170, 10, DARKGRAY)
        draw_text("e = -(vf/vi), current e = 0.6", 20, 190, 10, DARKGRAY)
        
        if (self.visible):
            self.ball.draw()
            self.cat.draw()
        if self.visible and self.moving:
            self.calibDot.draw()
        elif not self.visible:      
            draw_text("Invisible!", 200, 200, 40, WHITE)

    def shutdown(self):
        pass

