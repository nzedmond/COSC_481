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

# --------------SCARFY CONSTANTS------------
scarfy_fname = str(THIS_DIR/"resources/scarfy.png")
scarfy_position = Vector2(350.0, 280.0)
scarfy_scale = 0.5
num_scarfies = 6

# --------------OTHER CONSTANTS------------
currentFrame = 0
framesCounter = 0
framesSpeed = 8  # Number of spritesheet frames shown by second


# ------CONSTANTS FOR RUNNING GIRL
girl_fname = str(THIS_DIR/"resources/girl_running.png")
girl_position = Vector2(350.0, 280.0)
girl_scale_fixed = 0.76
num_girls = 8
girl_texture_position = Vector2(15, 40)

# -------CONSTANTS FOR FORMAL BOY -------------
boy_fname = str(THIS_DIR/"resources/kkiller.png")
boy_position = Vector2(350.0, 280.0)
boy_scale_fixed = 1.2
num_boys = 8
boy_texture_position = Vector2(15, 40)

init_window(screenWidth, screenHeight, "raylib [texture] example - sprite anim")

# Important NOTE: Textures MUST be loaded after Window initialization 
# (OpenGL context is required)
# Texture loading: one step vs. two steps (see other example)

# -----------------LOADING SCARFY-------------------------------
scarfy = load_texture(scarfy_fname) 
scarfy_frameRec = Rectangle(0.0, 0.0, float(scarfy.width)/num_scarfies, float(scarfy.height)) 


# -----------------LOADING GIRL --------------------------------
girl = load_texture(girl_fname)
girl_frameRec = Rectangle(0.0, 0.0, float(girl.width)/num_girls, float(girl.height))

# ---------------LOADING BOY -----------------------------------
boy = load_texture(boy_fname)
boy_frameRec = Rectangle(0.0, 0.0, float(boy.width)/num_boys, float(boy.height))


set_target_fps(60)  # Set our game to run at 60 frames-per-second

# Main game loop
while not window_should_close():  # Detect window close button or ESC key
    # Update
    framesCounter += 1

    if framesCounter >= (60/framesSpeed):
        framesCounter = 0
        currentFrame += 1

        if currentFrame > 5:
            currentFrame = 0

        scarfy_frameRec.x = float(currentFrame) * float(scarfy.width)/num_scarfies
        girl_frameRec.x = float(currentFrame) * float(girl.width)/num_girls
        boy_frameRec.x = float(currentFrame) * float(boy.width)/num_boys
        
        frameRec.x = float(currentFrame) * float(sprite.width)/num_sprites

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
    
    # # -------------------------DRAW SCARFY ----------------------------------
    # draw_texture(scarfy, 15, 40, WHITE)
    # draw_rectangle_lines(15, 40, scarfy.width, scarfy.height, LIME)
    # draw_rectangle_lines(15 + int(scarfy_frameRec.x), 40 + int(scarfy_frameRec.y), 
    #                        int(scarfy_frameRec.width), int(scarfy_frameRec.height), RED)
    
    # -------------------------DRAW GIRL --------------------------------------
    # draw_texture(girl, 15, 40, WHITE)
    draw_texture_ex(girl, girl_texture_position, 0.0, girl_scale_fixed, WHITE)
    draw_rectangle_lines(15, 40, int(girl.width*girl_scale_fixed), int(girl.height*girl_scale_fixed), LIME)
    draw_rectangle_lines(int(15 + int(girl_frameRec.x)), 40 + int(girl_frameRec.y),
                         int(girl_scale_fixed*girl_frameRec.width), int(girl_scale_fixed*girl_frameRec.height), RED)
    
    # # ------------------DRAW BOY---------------------------------------------
    # draw_texture_ex(boy, boy_texture_position, 0.0, boy_scale_fixed, WHITE)
    # draw_rectangle_lines(15, 40, int(boy.width*boy_scale_fixed), int(boy.height*boy_scale_fixed), LIME)
    # draw_rectangle_lines(int(15 + int(boy_frameRec.x)), 40 + int(boy_frameRec.y),
    #                      int(boy_scale_fixed*boy_frameRec.width), int(boy_scale_fixed*boy_frameRec.height), RED)
    
    draw_text("FRAME SPEED: ", 165, 210, 10, DARKGRAY)
    draw_text(f"{framesSpeed:02d} FPS", 575, 210, 10, DARKGRAY)
    draw_text("PRESS RIGHT/LEFT KEYS to CHANGE SPEED!", 290, 240, 10, 
    DARKGRAY)
    
    for i in range(MAX_FRAME_SPEED):
        if i < framesSpeed:
            draw_rectangle(250 + 21*i, 205, 20, 20, RED)
        #draw_rectangle_lines(250 + 21*i, 205, 20, 20, MAROON)
        
     
    # Draw part of the texture
    # draw_texture_rec(scarfy, scarfy_frameRec, scarfy_position, WHITE)  
    draw_texture_rec(girl, girl_frameRec, girl_position, WHITE)
    # draw_texture_rec(boy, boy_frameRec, boy_position, WHITE)
    
    draw_text("(c) Scarfy sprite by Eiden Marsal", screenWidth - 200,
               screenHeight - 20, 10, GRAY)
    end_drawing()

# De-Initialization
# unload_texture(boy)
unload_texture(scarfy)  # Texture unloading
unload_texture(girl)
close_window()  # Close window and OpenGL context