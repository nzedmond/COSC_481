from pyray import *
from os.path import join
from settings import *
from paddle import Paddle

def update_score(game):
    '''check if the ball has gone past the left or right edge of the screen and update scores accordingly'''
    if game.ball.position.x - game.ball.radius <= 0:
        game.enemy_paddle.score += 1
        game.ball = Ball(10, Vector2(400, 210), Vector2(2.0, 2.5))
    elif game.ball.position.x + game.ball.radius > WINDOW_WIDTH:
        game.player_paddle.score += 1
        game.ball = Ball(10, Vector2(400, 210), Vector2(-2.0, -2.5))
    
    
class GameState:
    MENU = 0
    GAMEPLAY = 1
    GAME_OVER = 2
    
    
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

class Player_Paddle(Paddle):
    def __init__(self, position):
        super().__init__(position)
        self.color = BLUE


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
        self.state = GameState.MENU
        self.visible = True
        self.moving = False
        self.ball = Ball(10, Vector2(400, 210), Vector2(2.0, 2.5))
        self.player_paddle = Player_Paddle(Vector2(10, 200))
        self.enemy_paddle = Enemy_Paddle(Vector2(WINDOW_WIDTH - 30, 200))
        
    def startup(self):
        pass
    
    def update(self):
        if self.state == GameState.MENU:
            self.update_menu()
        elif self.state == GameState.GAMEPLAY:
            self.update_gameplay()
        elif self.state == GameState.GAME_OVER:
            self.update_game_over()
            
    def update_menu(self):
        '''Handle menu screen logic'''
        if is_key_pressed(KeyboardKey.KEY_ENTER):
            self.state = GameState.GAMEPLAY
            # self.visible = True
            self.moving = True
            
    def update_gameplay(self):
        '''Handle gameplay screen logic'''
        self.visible = not is_key_down(KeyboardKey.KEY_SPACE)  # change it to a toogle
        
        if is_key_pressed(KeyboardKey.KEY_S):
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

            
            self.ball.update(self.player_paddle)
            update_score(self)
            self.player_paddle.update()
            self.enemy_paddle.update(self.ball)
            
        # check for game over condition (first to 10 points wins)
        if self.player_paddle.score >= 10 or self.enemy_paddle.score >= 10:
            self.state = GameState.GAME_OVER

    def update_game_over(self):
        '''Handle game over screen logic'''
        if is_key_pressed(KeyboardKey.KEY_ENTER):
            self.__init__()  # Reset the game
    
    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.GAMEPLAY:
            self.draw_gameplay()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over() 
            
    def draw_menu(self):
        draw_text("PONG!", 150, 150, 40, DARKGREEN)
        draw_text("Press Enter to Start", 200, 200, 40, DARKGREEN)
        
    def draw_gameplay(self):
        draw_fps(20, 20)

        if (self.visible):
            # draw score boards
            draw_text(f"Player: {self.player_paddle.score}",
                      120, 20, 20, BLUE)
            draw_text(f"Enemy: {self.enemy_paddle.score}",
                      WINDOW_WIDTH - 150, 20, 20, RED)
            draw_line(WINDOW_WIDTH // 2, 0,
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT, GRAY)
            self.ball.draw()
            self.player_paddle.draw()
            self.enemy_paddle.draw()
        else:
            draw_text("Invisible!", 200, 200, 40, RED)
            
    def draw_game_over(self):
        winner = "Player" if self.player_paddle.score >= 10 else "Enemy"
        draw_text(f"{winner} Wins!", 150, 150, 40, DARKGREEN)
        draw_text("Press Enter to Restart", 200, 200, 40, DARKGREEN)
        
    # def update(self):
    #     self.visible = not is_key_down(
    #         KeyboardKey.KEY_SPACE)  # change it to a toogle

    #     if is_key_pressed(KeyboardKey.KEY_S):  # change it to a toogle
    #         self.moving = not self.moving

    #     if self.visible and self.moving:
    #         # check for ball and player_paddle collision
    #         if (self.ball.position.x - self.ball.radius <= self.player_paddle.position.x + self.player_paddle.width):
    #             if (self.ball.position.y >= self.player_paddle.position.y and
    #                 self.ball.position.y <= self.player_paddle.position.y + self.player_paddle.height):
    #                 self.ball.velocity.x = self.ball.velocity.x * -1.0
                    
    #         # check for ball and enemy_paddle collision
    #         if (self.ball.position.x + self.ball.radius >= self.enemy_paddle.position.x):
    #             if (self.ball.position.y >= self.enemy_paddle.position.y and
    #                 self.ball.position.y <= self.enemy_paddle.position.y + self.enemy_paddle.height):
    #                 self.ball.velocity.x = self.ball.velocity.x * -1.0

    #         # , self.screenWidth, 0, self.screenHeight)
    #         self.ball.update(self.player_paddle)
    #         update_score(self)
    #         self.player_paddle.update()
    #         self.enemy_paddle.update(self.ball)

    # def draw(self):
    #     draw_fps(20, 20)

    #     if (self.visible):
    #         # draw score boards
    #         draw_text(f"Player: {self.player_paddle.score}",
    #                   120, 20, 20, BLUE)
    #         draw_text(f"Enemy: {self.enemy_paddle.score}",
    #                   WINDOW_WIDTH - 150, 20, 20, RED)
    #         draw_line(WINDOW_WIDTH // 2, 0,
    #                   WINDOW_WIDTH // 2, WINDOW_HEIGHT, GRAY)
    #         self.ball.draw()
    #         self.player_paddle.draw()
    #         self.enemy_paddle.draw()
    #     else:
    #         draw_text("Invisible!", 200, 200, 40, RED)

    def shutdown(self):
        pass
