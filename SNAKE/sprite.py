"""raylib [textures] example - Sprite animation
Example complexity rating: [★★☆☆] 2/4
Example originally created with raylib 1.3, last time updated with raylib 1.3
Example licensed under an unmodified zlib/libpng license, which is an OSI-certified,
BSD-like license that allows static linking with closed source software
Copyright (c) 2014-2025 Ramon Santamaria (@raysan5)

This source has been converted from C raylib examples to Python.
"""

from pyray import *
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent

MAX_FRAME_SPEED = 15
MIN_FRAME_SPEED = 1

# Initialization
screenWidth = 800
screenHeight = 450

# # --------------SCARFY CONSTANTS------------
# fname = "resources/scarfy.png"
# scale = 0.99
# num = 6

# # --------------GIRL CONSTANTS------------  
# fname = "resources/girl_running.png"
# scale = 0.75
# num = 8

# # --------------CAT CONSTANTS------------
# fname = "resources/myCat01.png"
# scale = 0.529
# num = 5

# # --------------KILLER CONSTANTS------------
# fname = "Game_Assets/sprites/killer.png"
# scale = 1.32
# num = 8

# Devil constants
fname = "Game_Assets/sprites/devil.png"
scale = 0.2
num = 5


# --------------SPRITE CONSTANTS------------
SPRITE_SOURCE = fname
SPRITE_FNAME = str(THIS_DIR/SPRITE_SOURCE)
SPRITE_POSITION = Vector2(350.0, 280.0)
SPRITE_TEXTURE_POSITION = Vector2(15, 40)
SPRITE_SCALE = scale
NUM_SPRITES = num


# --------------OTHER CONSTANTS------------
currentFrame = 0
framesCounter = 0
framesSpeed = 8  # Number of spritesheet frames shown by second

init_window(screenWidth, screenHeight, "raylib [texture] example - sprite anim")

# Important NOTE: Textures MUST be loaded after Window initialization 
# (OpenGL context is required)
# Texture loading: one step vs. two steps (see other example)

# -----------------LOADING SPRITE-------------------------------
SPRITE = load_texture(SPRITE_FNAME) 
frameRec = Rectangle(0.0, 0.0, float(SPRITE.width)/NUM_SPRITES, float(SPRITE.height)) 



set_target_fps(60)  # Set our game to run at 60 frames-per-second

# Main game loop
while not window_should_close():  # Detect window close button or ESC key
    # Update
    framesCounter += 1

    if framesCounter >= (60/framesSpeed):
        framesCounter = 0
        currentFrame += 1

        if currentFrame > NUM_SPRITES - 1:
            currentFrame = 0

        frameRec.x = float(currentFrame) * float(SPRITE.width)/NUM_SPRITES

    # Control frames speed
    if is_key_pressed(KEY_RIGHT):
        framesSpeed += 1
    elif is_key_pressed(KEY_LEFT):
        framesSpeed -= 1

    if framesSpeed > MAX_FRAME_SPEED:
        framesSpeed = MAX_FRAME_SPEED
    elif framesSpeed < MIN_FRAME_SPEED:
        framesSpeed = MIN_FRAME_SPEED

    # Draw
    begin_drawing()
    
    clear_background(RAYWHITE)
    
    
    # -------------------------DRAW SPRITE ----------------------------------
    draw_texture_ex(SPRITE, SPRITE_TEXTURE_POSITION, 0.0, SPRITE_SCALE, WHITE)
    draw_rectangle_lines(int(SPRITE_TEXTURE_POSITION.x), int(SPRITE_TEXTURE_POSITION.y), int(SPRITE.width * SPRITE_SCALE), int(SPRITE.height * SPRITE_SCALE), LIME)
    draw_rectangle_lines(int(SPRITE_TEXTURE_POSITION.x + int(frameRec.x* SPRITE_SCALE)), int(SPRITE_TEXTURE_POSITION.y + int(frameRec.y * SPRITE_SCALE)), int(frameRec.width * SPRITE_SCALE), int(frameRec.height * SPRITE_SCALE), RED)
    
    
    draw_text("FRAME SPEED: ", 165, 210, 10, DARKGRAY)
    draw_text(f"{framesSpeed:02d} FPS", 575, 210, 10, DARKGRAY)
    draw_text("PRESS RIGHT/LEFT KEYS to CHANGE SPEED!", 290, 240, 10, DARKGRAY)
    
    for i in range(MAX_FRAME_SPEED):
        if i < framesSpeed:
            draw_rectangle(250 + 21*i, 205, 20, 20, RED)
        #draw_rectangle_lines(250 + 21*i, 205, 20, 20, MAROON)


    # Draw part of the texture 
    draw_texture_rec(SPRITE, frameRec, SPRITE_POSITION, WHITE)
    # draw_texture_rec(boy, boy_frameRec, boy_position, WHITE)
    
    draw_text("(c) Scarfy sprite by Eiden Marsal", screenWidth - 200,
               screenHeight - 20, 10, GRAY)
    end_drawing()

# De-Initialization
# unload_texture(boy)
unload_texture(SPRITE)  # Texture unloading
close_window()  # Close window and OpenGL context