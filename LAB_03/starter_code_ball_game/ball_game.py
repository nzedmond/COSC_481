from pyray import *
from os.path import join
from settings import *


class Ball():
    def __init__(self, radius, position, velocity):
        self.radius = radius
        self.position = position
        self.velocity = velocity

    def update(self, paddle):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

        # Check walls collision for bouncing
        if (self.position.x > WINDOW_WIDTH or self.position.x <= 0):
            self.velocity.x = self.velocity.x * -1.0

        if (self.position.y >= WINDOW_HEIGHT or self.position.y <= self.radius):
            self.velocity.y = self.velocity.y * - 1.0

    def draw(self):
        # draw_circle_lines_v(self.position, self.radius, BLACK)
        draw_circle_v(self.position, self.radius+5, BLACK)
        draw_circle_v(self.position, self.radius, DARKPURPLE)


class Paddle:
    def __init__(self, position):
        self.position = position
        self.score = 0
        self.color = BLUE
        self.width = 20
        self.height = 100
        self.speed = 200  # pixels per second
        self.rect = Rectangle(
            self.position.x, self.position.y, self.width, self.height)

    def draw(self):
        draw_rectangle_rec(self.rect, self.color)

    def update(self):
        '''Handles user input to move the paddle up and down'''
        motion = Vector2(0, 0)
        if is_key_down(KeyboardKey.KEY_UP):
            motion.y -= 1
        elif is_key_down(KeyboardKey.KEY_DOWN):
            motion.y += 1

        motion_this_frame = vector2_scale(
            motion, get_frame_time() * self.speed)
        self.position = vector2_add(self.position, motion_this_frame)

        if self.position.y < 0:
            self.position.y = 0
        elif self.position.y + self.height > WINDOW_HEIGHT:
            self.position.y = WINDOW_HEIGHT - self.height

        # Update rectangle position
        self.rect.y = self.position.y


class Enemy_Paddle(Paddle):
    def __init__(self, position):
        super().__init__(position)
        self.color = RED
        self.speed = 150  # pixels per second

    def update(self, ball):
        '''Simple AI to follow the ball'''
        # move the paddle down and up automatically
        motion = Vector2(0, 0)
        if ball.position.y < self.position.y + self.height / 2:
            motion.y -= 1
        elif ball.position.y > self.position.y + self.height / 2:
            motion.y += 1

        motion_this_frame = vector2_scale(
            motion, get_frame_time() * self.speed)
        self.position = vector2_add(self.position, motion_this_frame)

        if self.position.y < 0:
            self.position.y = 0
        elif self.position.y + self.height > WINDOW_HEIGHT:
            self.position.y = WINDOW_HEIGHT - self.height

        # Update rectangle position
        self.rect.y = self.position.y
    


class Game:

    def __init__(self):
        self.visible = True
        self.moving = False
        self.ball = Ball(10, Vector2(400, 210), Vector2(2.0, 2.5))
        self.player_paddle = Paddle(Vector2(10, 200))
        self.enemy_paddle = Enemy_Paddle(Vector2(WINDOW_WIDTH - 30, 200))

    # where game assets/resources will be initialized
    def startup(self):
        pass

    def update(self):
        self.visible = not is_key_down(
            KeyboardKey.KEY_SPACE)  # change it to a toogle

        if is_key_pressed(KeyboardKey.KEY_S):  # change it to a toogle
            self.moving = not self.moving

        if self.visible and self.moving:
            # check for ball and player_paddle collision
            if (self.ball.position.x - self.ball.radius <= self.player_paddle.position.x + self.player_paddle.width):
                if (self.ball.position.y >= self.player_paddle.position.y and
                    self.ball.position.y <= self.player_paddle.position.y + self.player_paddle.height):
                    self.ball.velocity.x = self.ball.velocity.x * -1.0
                    
            # check for ball and enemy_paddle collision
            if (self.ball.position.x + self.ball.radius >= self.enemy_paddle.position.x):
                if (self.ball.position.y >= self.enemy_paddle.position.y and
                    self.ball.position.y <= self.enemy_paddle.position.y + self.enemy_paddle.height):
                    self.ball.velocity.x = self.ball.velocity.x * -1.0

            # , self.screenWidth, 0, self.screenHeight)
            self.ball.update(self.player_paddle)
            self.player_paddle.update()
            self.enemy_paddle.update(self.ball)

    def draw(self):
        draw_fps(20, 20)

        if (self.visible):
            draw_line(WINDOW_WIDTH // 2, 0,
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT, LIGHTGRAY)
            self.ball.draw()
            self.player_paddle.draw()
            self.enemy_paddle.draw()
        else:
            draw_text("Invisible!", 200, 200, 40, WHITE)

    def shutdown(self):
        pass
