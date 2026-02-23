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

# constants for the scarfy sprite animation
scarfy_file_name = str(THIS_DIR/"resources/scarfy.png")
num_scarfy = 6

# constants for the girl sprite animation
girl_file_name = str(THIS_DIR/"resources/girl_running.png")
girl_scale = 0.75
num_girls = 8

# constants for cat sprite animation
cat_filename = str(THIS_DIR/"resources/myCat01.png")
cat_scale = 0.5
num_cats = 5

# constants for karate girl sprite animation
karate_girl_filename = str(THIS_DIR/"resources/karate_girl.png")
karate_girl_scale = 1.5
num_karate_girls = 14

# Initialization
screenWidth = 800
screenHeight = 450


init_window(screenWidth, screenHeight, "raylib [texture] example - sprite anim")

# Important NOTE: Textures MUST be loaded after Window initialization 
# scarfy = load_texture(scarfy_file_name)  
# position = Vector2(350.0, 280.0)
# frameRec = Rectangle(0.0, 0.0, float(scarfy.width)/num_scarfy, float(scarfy.height))

# LOADING GIRL SPRITE
girl = load_texture(girl_file_name)
position2 = Vector2(350.0, 280.0)
frameRec2 = Rectangle(0.0, 0.0, float(girl.width)/num_girls, float(girl.height))

# LOADING CAT SPRITE
cat = load_texture(cat_filename)
position3 = Vector2(350.0, 280.0)
frameRec3 = Rectangle(0.0, 0.0, float(cat.width)/num_cats, float(cat.height))

# LOADING KARATE GIRL SPRITE
karate_girl = load_texture(karate_girl_filename)
position4 = Vector2(350.0, 280.0)
frameRec4 = Rectangle(0.0, 0.0, float(karate_girl.width)/num_karate_girls, float(karate_girl.height))

currentFrame = 0

framesCounter = 0
framesSpeed = 8  # Number of spritesheet frames shown by second

set_target_fps(60)  # Set our game to run at 60 frames-per-second

# Main game loop
while not window_should_close():  # Detect window close button or ESC key
    # Update
    framesCounter += 1

    if framesCounter >= (60/framesSpeed):
        framesCounter = 0
        currentFrame += 1

        if currentFrame > 7:
            currentFrame = 0

        # frameRec.x = float(currentFrame) * float(scarfy.width)/num_scarfy
        frameRec2.x = float(currentFrame) * float(girl.width)/num_girls
        frameRec3.x = float(currentFrame) * float(cat.width)/num_cats
        frameRec4.x = float(currentFrame) * float(karate_girl.width)/num_karate_girls

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
    
    # Draw scarfy texture and frame rectangle
    # draw_texture(scarfy, 15, 40, WHITE)
    # draw_rectangle_lines(15, 40, scarfy.width, scarfy.height, LIME)
    # draw_rectangle_lines(15 + int(frameRec.x), 40 + int(frameRec.y), 
    #                        int(frameRec.width), int(frameRec.height), RED)
    
    # Draw girl texture and frame rectangle
    # draw_texture_ex(girl, Vector2(15, 40), 0.0, girl_scale, WHITE)
    # # draw_texture(girl, 1, 40, WHITE)
    

    # Draw girl texture and frame rectangle
    # # Draw rectangle lines with the scaled size of the GIRL texture and the frame
    # draw_rectangle_lines(15, 40, int(girl.width*girl_scale), int(girl.height*girl_scale), LIME)
    # draw_rectangle_lines(15 + int(frameRec2.x), 40 + int(frameRec2.y), 
    #                        int(frameRec2.width*girl_scale), int(frameRec2.height*girl_scale), RED)
    
    # # Draw cat texture and frame rectangle
    # draw_texture_ex(cat, Vector2(15, 40), 0.0, cat_scale, WHITE)
    # # Draw rectangle lines with the scaled size of the CAT texture and the frame
    # draw_rectangle_lines(15, 40, int(cat.width*cat_scale), int(cat.height*cat_scale), BLUE)
    # draw_rectangle_lines(15 + int(frameRec3.x), 40 + int(frameRec3.y), 
    #                        int(frameRec3.width*cat_scale), int(frameRec3.height*cat_scale), RED)
    
    # Draw karate girl texture and frame rectangle
    draw_texture_ex(karate_girl, Vector2(15, 40), 0.0, karate_girl_scale, WHITE)
    # Draw rectangle lines with the scaled size of the KARATE   GIRL texture and the frame
    draw_rectangle_lines(15, 40, int(karate_girl.width*karate_girl_scale), int(karate_girl.height*karate_girl_scale), ORANGE)
    draw_rectangle_lines(15 + int(frameRec4.x), 40 + int(frameRec4.y), 
                           int(frameRec4.width*karate_girl_scale), int(frameRec4.height*karate_girl_scale), RED)
    
    
    draw_text("FRAME SPEED: ", 165, 210, 10, DARKGRAY)
    draw_text(f"{framesSpeed:02d} FPS", 575, 210, 10, DARKGRAY)
    draw_text("PRESS RIGHT/LEFT KEYS to CHANGE SPEED!", 290, 240, 10, 
    DARKGRAY)
    
    for i in range(MAX_FRAME_SPEED):
        if i < framesSpeed:
            draw_rectangle(250 + 21*i, 205, 20, 20, RED)
        #draw_rectangle_lines(250 + 21*i, 205, 20, 20, MAROON)

    # Draw part of the texture
    # draw_texture_rec(scarfy, frameRec, position, WHITE) 
    # draw_texture_rec(girl, frameRec2, position2, WHITE)
    # draw_texture_rec(cat, frameRec3, position3, WHITE)
    draw_texture_rec(karate_girl, frameRec4, position4, WHITE)
    draw_text("(c) Scarfy sprite by Eiden Marsal", screenWidth - 200,
               screenHeight - 20, 10, GRAY)
    end_drawing()

# De-Initialization
# unload_texture(scarfy)  # Texture unloading
unload_texture(girl)
unload_texture(cat)
unload_texture(karate_girl)
close_window()  # Close window and OpenGL context