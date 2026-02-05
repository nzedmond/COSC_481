from pyray import *
from os.path import join
from settings import * 

class Paddle():
    def __init__(self):
        self.speed = 300
        self.pos = Vector2(20, WINDOW_HEIGHT / 2)
        # self.rectangle = 
        self.size = Vector2(20, 100)
        
        
    def update(self):
        motion = Vector2(0, 0)
        if is_key_down(KeyboardKey.KEY_UP):
            motion.y += -1
        if is_key_down(KeyboardKey.KEY_DOWN):
            motion.y += 1   
            
        motion_this_frame = vector2_scale(motion, get_frame_time() * self.speed)
        self.pos = vector2_add(self.pos, motion_this_frame)
        
    def draw(self):
        paddle = Rectangle(self.pos.x, self.pos.y, self.size.x, self.size.y)
        draw_rectangle_re(paddle, BLUE)


        
class Cat():
    def __init__(self):
        self.pos = Vector2(640, 320)
        self.speed = 200 # 200 pixels/sec
        self.grounded = True # would jump

    def startup(self):
        # be careful path: how you run?>
        self.texture = load_texture(join('assets', 'cat_one.png'))

    def update(self):
        motion = Vector2(0, 0)

        if is_key_down(KeyboardKey.KEY_RIGHT):
            motion.x += 1
        if is_key_down(KeyboardKey.KEY_LEFT):
            motion.x += -1 

        if is_key_down(KeyboardKey.KEY_UP):
            motion.y += -1
        if is_key_down(KeyboardKey.KEY_DOWN):
            motion.y += 1 

        motion_this_frame = vector2_scale(motion, get_frame_time() * self.speed)
    
        self.pos = vector2_add(self.pos, motion_this_frame)
 
   
    def draw(self):
        #draw_texture_v(self.texture, self.pos, WHITE)
        draw_texture_ex(self.texture, self.pos, 0, 4, WHITE)


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
        self.paddle = Paddle()

    # where game assets/resources will be initialized
    def startup(self):
        self.cat.startup()
        


    def update(self):
       self.visible = not is_key_down(KeyboardKey.KEY_SPACE) # change it to a toogle
       
       if is_key_pressed(KeyboardKey.KEY_S): # change it to a toogle
           self.moving = not self.moving
           
    
       
       if self.visible and self.moving: 
           
           self.ball.update()#, self.screenWidth, 0, self.screenHeight)
           self.cat.update()
           self.paddle.update()
           
           if (check_collision_circle_rec(self.ball.position, self.ball.radius, self.paddle)):
            self.velocity.x = self.velocity.x * -1.0
            
           if (is_key_down(KeyboardKey.KEY_RIGHT_BRACKET)):
               self.cat.speed += 20
           if (is_key_down(KeyboardKey.KEY_LEFT_BRACKET)):
               self.cat.speed -= 20


        
    def draw(self):
        draw_fps(20, 20)

        if (self.visible):
            self.ball.draw()
            ##self.cat.draw()
            self.paddle.draw()
        else:      
            draw_text("Invisible!", 200, 200, 40, WHITE)

    def shutdown(self):
        pass

