"""

raylib [shapes] example - Logo Raylib

"""
from pyray import *

# Change it to be the FedEx logo

# COMMON CONSTANTS
color1 = DARKPURPLE
color2 = MAROON
# CONSTANTS FOR F
xPos = 50
yPos = 100
fWidth = 100
fHeight = 200
lineThickness = 60

# CONSTANTS FOR e
circleRadius = 80
circleCenterX = 205
circleCenterY = 220

# CONSTANTS FOR d
xD = 450
yD = 100
dLineHeight = 200
ellipseRadiusVertical = circleRadius
ellipseRadiusHorizontal = 85
ellipseCenterX = circleCenterX + circleRadius + ellipseRadiusHorizontal
ellipseCenterY = circleCenterY

# CONSTANTS FOR E
xE = 500

# CONSTANTS FOR x
posX = xE + fWidth
posY = 160
xWidth = 160
xHeight = 140
xColor = RAYWHITE

# Initialization
screenWidth = 800
screenHeight = 450

init_window(screenWidth, screenHeight,
            'raylib [shapes] example - raylib logo using shapes')

set_target_fps(60)  # Set our game to run at 60 frames-per-second


def draw_letter_f(x, y, width, height, color, thickness):
    # Vertical line left side
    draw_line_ex(
        Vector2(x, y),
        Vector2(x, y + height),
        thickness,
        color
    )

    # Horizontal line at top
    draw_line_ex(
        Vector2(x-30, y),
        Vector2(x + width, y),
        thickness,
        color
    )

    # Horizontal line in middle
    draw_line_ex(
        Vector2(x, y + height * 0.5),
        Vector2(x + width * 0.8, y + height * 0.5),
        thickness,
        color
    )


def draw_letter_d():
    # draw the vertical line
    draw_line_ex(
        Vector2(xD, 70),
        Vector2(xD, 100 + dLineHeight),
        lineThickness,
        color1
    )
    # draw the outer ellipse
    draw_ellipse(
        ellipseCenterX,
        ellipseCenterY,
        ellipseRadiusHorizontal,
        ellipseRadiusVertical,
        color1)
    # draw the inner ellipse to create hollow part
    draw_ellipse(
        ellipseCenterX+5,
        ellipseCenterY,
        ellipseRadiusHorizontal - lineThickness//1.2,
        ellipseRadiusVertical - lineThickness//1.5,
        RAYWHITE)


def draw_letter_E(color):
    # Vertical line left side
    draw_line_ex(
        Vector2(xE, 100),
        Vector2(xE, 100 + 200),
        lineThickness,
        color
    )
    # Horizontal line at top
    draw_line_ex(
        Vector2(xE-30, 100),
        Vector2(xE + fWidth, 100),
        lineThickness,
        color
    )
    draw_line_ex(
        Vector2(xE-30, 180),
        Vector2(xE + fWidth, 180),
        lineThickness//1.5,
        color
    )
    draw_line_ex(
        Vector2(xE-30, 270),
        Vector2(xE + fWidth, 270),
        lineThickness,
        color
    )

# draw  letter x


def draw_letter_x():
    draw_rectangle(posX, posY, xWidth, xHeight, color2)
    draw_triangle(Vector2(posX+50, posY+60), Vector2(posX, posY),
                  Vector2(posX, posY + xHeight), xColor)
    draw_triangle(Vector2(posX + xWidth, posY), Vector2(posX+50+lineThickness,
                  posY+60), Vector2(posX + xWidth, posY + xHeight), xColor)
    draw_triangle(Vector2(posX+lineThickness-10, posY), Vector2(posX +
                  lineThickness+20, posY+40), Vector2(posX+lineThickness+50, posY), xColor)
    draw_triangle(Vector2(posX+lineThickness+20, posY+xHeight-40), Vector2(posX +
                  lineThickness, posY+xHeight), Vector2(posX+lineThickness+50, posY+xHeight), xColor)


def draw_letter_e(color):

    # Outer circle
    draw_circle(circleCenterX, circleCenterY, circleRadius, color)

    # Inner circle (to create the hollow part)
    draw_circle(circleCenterX, circleCenterY, circleRadius * 0.5, RAYWHITE)

    # Horizontal line in the middle
    draw_line_ex(
        Vector2(circleCenterX - circleRadius, circleCenterY-5),
        Vector2(circleCenterX + circleRadius * 0.6, circleCenterY-5),
        lineThickness//3,
        color
    )

    # draw_small_line
    draw_line_ex(
        Vector2(circleCenterX + circleRadius * 0.4, circleCenterY+15),
        Vector2(circleCenterX + circleRadius, circleCenterY+15),
        lineThickness//3,
        RAYWHITE
    )


# Main game loop
while not window_should_close():  # Detect window close button or ESC key
    # Update
    # ----------------------------------------------------------------------------------
    # TODO: Update your variables here
    # ----------------------------------------------------------------------------------

    # Draw
    # ----------------------------------------------------------------------------------
    begin_drawing()

    clear_background(RAYWHITE)
    draw_letter_f(xPos, yPos, fWidth, fHeight, color1, lineThickness)
    draw_letter_e(color1)
    draw_letter_d()
    draw_letter_E(color2)
    draw_letter_x()

    end_drawing()

# De-Initialization
close_window()  # Close window and OpenGL context
