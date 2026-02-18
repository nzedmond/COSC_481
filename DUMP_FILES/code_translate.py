import pyray as rl

#----------------------------------------------------------------------------------
# Some Defines
#----------------------------------------------------------------------------------
PLAYER_MAX_LIFE = 5
LINES_OF_BRICKS = 5
BRICKS_PER_LINE = 20

#----------------------------------------------------------------------------------
# Types and Structures Definition
#----------------------------------------------------------------------------------
class Player:
    def __init__(self):
        self.position = rl.Vector2(0, 0)
        self.size = rl.Vector2(0, 0)
        self.life = 0

class Ball:
    def __init__(self):
        self.position = rl.Vector2(0, 0)
        self.speed = rl.Vector2(0, 0)
        self.radius = 0
        self.active = False

class Brick:
    def __init__(self):
        self.position = rl.Vector2(0, 0)
        self.active = False

#------------------------------------------------------------------------------------
# Global Variables Declaration
#------------------------------------------------------------------------------------
screenWidth = 800
screenHeight = 450

gameOver = False
pause = False

player = Player()
ball = Ball()
brick = [[Brick() for _ in range(BRICKS_PER_LINE)] for _ in range(LINES_OF_BRICKS)]
brickSize = rl.Vector2(0, 0)

#------------------------------------------------------------------------------------
# Module Functions Declaration (local)
#------------------------------------------------------------------------------------
def InitGame():
    global brickSize, player, ball, brick
    brickSize = rl.Vector2(rl.get_screen_width() / BRICKS_PER_LINE, 40)

    # Initialize player
    player.position = rl.Vector2(screenWidth / 2, screenHeight * 7 / 8)
    player.size = rl.Vector2(screenWidth / 10, 20)
    player.life = PLAYER_MAX_LIFE

    # Initialize ball
    ball.radius = 7
    ball.position = rl.Vector2(player.position.x, player.position.y - player.size.y / 2 - ball.radius)
    ball.speed = rl.Vector2(0, 0)
    ball.active = False

    # Initialize bricks
    initialDownPosition = 50

    for i in range(LINES_OF_BRICKS):
        for j in range(BRICKS_PER_LINE):
            brick[i][j].position = rl.Vector2(j * brickSize.x + brickSize.x / 2, i * brickSize.y + initialDownPosition)
            brick[i][j].active = True

def UpdateGame():
    global gameOver, pause, player, ball, brick
    if not gameOver:
        if rl.is_key_pressed(rl.KEY_P):
            pause = not pause

        if not pause:
            # Player movement logic
            if rl.is_key_down(rl.KEY_LEFT):
                player.position.x -= 5
            if (player.position.x - player.size.x / 2) <= 0:
                player.position.x = player.size.x / 2
            if rl.is_key_down(rl.KEY_RIGHT):
                player.position.x += 5
            if (player.position.x + player.size.x / 2) >= screenWidth:
                player.position.x = screenWidth - player.size.x / 2

            # Ball launching logic
            if not ball.active:
                if rl.is_key_pressed(rl.KEY_SPACE):
                    ball.active = True
                    ball.speed = rl.Vector2(0, -5)

            # Ball movement logic
            if ball.active:
                ball.position.x += ball.speed.x
                ball.position.y += ball.speed.y
            else:
                ball.position = rl.Vector2(player.position.x, player.position.y - player.size.y / 2 - ball.radius)

            # Collision logic: ball vs walls
            if ((ball.position.x + ball.radius) >= screenWidth) or ((ball.position.x - ball.radius) <= 0):
                ball.speed.x *= -1
            if (ball.position.y - ball.radius) <= 0:
                ball.speed.y *= -1
            if (ball.position.y + ball.radius) >= screenHeight:
                ball.speed = rl.Vector2(0, 0)
                ball.active = False
                player.life -= 1

            # Collision logic: ball vs player
            player_rect = rl.Rectangle(player.position.x - player.size.x / 2, player.position.y - player.size.y / 2, player.size.x, player.size.y)
            if rl.check_collision_circle_rec(ball.position, ball.radius, player_rect):
                if ball.speed.y > 0:
                    ball.speed.y *= -1
                    ball.speed.x = (ball.position.x - player.position.x) / (player.size.x / 2) * 5

            # Collision logic: ball vs bricks
            for i in range(LINES_OF_BRICKS):
                for j in range(BRICKS_PER_LINE):
                    if brick[i][j].active:
                        # Hit below
                        if (((ball.position.y - ball.radius) <= (brick[i][j].position.y + brickSize.y / 2)) and
                            ((ball.position.y - ball.radius) > (brick[i][j].position.y + brickSize.y / 2 + ball.speed.y)) and
                            (abs(ball.position.x - brick[i][j].position.x) < (brickSize.x / 2 + ball.radius * 2 / 3)) and (ball.speed.y < 0)):
                            brick[i][j].active = False
                            ball.speed.y *= -1
                        # Hit above
                        elif (((ball.position.y + ball.radius) >= (brick[i][j].position.y - brickSize.y / 2)) and
                              ((ball.position.y + ball.radius) < (brick[i][j].position.y - brickSize.y / 2 + ball.speed.y)) and
                              (abs(ball.position.x - brick[i][j].position.x) < (brickSize.x / 2 + ball.radius * 2 / 3)) and (ball.speed.y > 0)):
                            brick[i][j].active = False
                            ball.speed.y *= -1
                        # Hit left
                        elif (((ball.position.x + ball.radius) >= (brick[i][j].position.x - brickSize.x / 2)) and
                              ((ball.position.x + ball.radius) < (brick[i][j].position.x - brickSize.x / 2 + ball.speed.x)) and
                              (abs(ball.position.y - brick[i][j].position.y) < (brickSize.y / 2 + ball.radius * 2 / 3)) and (ball.speed.x > 0)):
                            brick[i][j].active = False
                            ball.speed.x *= -1
                        # Hit right
                        elif (((ball.position.x - ball.radius) <= (brick[i][j].position.x + brickSize.x / 2)) and
                              ((ball.position.x - ball.radius) > (brick[i][j].position.x + brickSize.x / 2 + ball.speed.x)) and
                              (abs(ball.position.y - brick[i][j].position.y) < (brickSize.y / 2 + ball.radius * 2 / 3)) and (ball.speed.x < 0)):
                            brick[i][j].active = False
                            ball.speed.x *= -1

            # Game over logic
            if player.life <= 0:
                gameOver = True
            else:
                gameOver = True
                for i in range(LINES_OF_BRICKS):
                    for j in range(BRICKS_PER_LINE):
                        if brick[i][j].active:
                            gameOver = False
    else:
        if rl.is_key_pressed(rl.KEY_ENTER):
            InitGame()
            gameOver = False

def DrawGame():
    rl.begin_drawing()
    rl.clear_background(rl.RAYWHITE)

    if not gameOver:
        # Draw player bar
        rl.draw_rectangle(int(player.position.x - player.size.x / 2), int(player.position.y - player.size.y / 2), int(player.size.x), int(player.size.y), rl.BLACK)

        # Draw player lives
        for i in range(player.life):
            rl.draw_rectangle(20 + 40 * i, screenHeight - 30, 35, 10, rl.LIGHTGRAY)

        # Draw ball
        rl.draw_circle_v(ball.position, ball.radius, rl.MAROON)

        # Draw bricks
        for i in range(LINES_OF_BRICKS):
            for j in range(BRICKS_PER_LINE):
                if brick[i][j].active:
                    color = rl.GRAY if (i + j) % 2 == 0 else rl.DARKGRAY
                    rl.draw_rectangle(int(brick[i][j].position.x - brickSize.x / 2), int(brick[i][j].position.y - brickSize.y / 2), int(brickSize.x), int(brickSize.y), color)

        if pause:
            text = "GAME PAUSED"
            rl.draw_text(text, screenWidth // 2 - rl.measure_text(text, 40) // 2, screenHeight // 2 - 40, 40, rl.GRAY)
    else:
        text = "PRESS [ENTER] TO PLAY AGAIN"
        rl.draw_text(text, rl.get_screen_width() // 2 - rl.measure_text(text, 20) // 2, rl.get_screen_height() // 2 - 50, 20, rl.GRAY)

    rl.end_drawing()

def UnloadGame():
    # TODO: Unload all dynamic loaded data (textures, sounds, models...)
    pass

def UpdateDrawFrame():
    UpdateGame()
    DrawGame()

#------------------------------------------------------------------------------------
# Program main entry point
#------------------------------------------------------------------------------------
def main():
    # Initialization
    rl.init_window(screenWidth, screenHeight, "classic game: arkanoid")
    InitGame()
    rl.set_target_fps(60)

    # Main game loop
    while not rl.window_should_close():
        UpdateDrawFrame()

    # De-Initialization
    UnloadGame()
    rl.close_window()

if __name__ == "__main__":
    main()