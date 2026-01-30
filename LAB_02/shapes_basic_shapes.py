# Introduction to raylib: architecture; drawing
# Activity of Lecture 3, Jan 27, 2026

import pyray

# Initialization
screenWidth = 800
screenHeight = 450

# CONSTANTS FOR Z-shape
vectorTopLeft = pyray.Vector2(120, 100)
vectorBottomLeft = pyray.Vector2(120, 220)
vectorTopRight = pyray.Vector2(240, 100)
vectorBottomRight = pyray.Vector2(240, 220)
lineThickness = 5.0

# CONSTANTS FOR Circle
centerX = 190
centerY = 340
radius = 90

# CONSTANTS FOR Horizontal Lines
numLines = 5
gapBetweenLines = 20
startVectorTopLine = pyray.Vector2(400, 100)
endVectorTopLine = pyray.Vector2(600, 100)

# CONSTANTS FOR Triangle
baseV1 = pyray.Vector2(380, 262)
baseV2 = pyray.Vector2(480, 262)
triangleHeight = 80
gapBetweenTriangles = 20

# CONSTANTS FOR Polygon
center = pyray.Vector2(500, 360)
polySides = 12
polyRadius = 85


pyray.init_window(screenWidth, screenHeight,
                  "raylib [shapes] example - basic shapes drawing")

rotation = 0.0

pyray.set_target_fps(60)

# Draw triangle function


def draw_isoscele_triangle(base_v1, base_v2, height, color):
    v1 = base_v1
    v2 = base_v2
    v3 = pyray.Vector2((base_v1.x + base_v2.x) / 2, base_v1.y - height)
    pyray.draw_triangle(v1, v2, v3, color)


# Main game loop
while not pyray.window_should_close():
    # Update
    # rotation += 0.2

    # Draw
    pyray.begin_drawing()

    pyray.clear_background(pyray.RAYWHITE)

    pyray.draw_text("some basic shapes available on raylib",
                    20, 20, 20, pyray.DARKGRAY)

    # Z-shape
    pyray.draw_line_ex(vectorTopLeft, vectorTopRight, lineThickness, pyray.RED)
    pyray.draw_line_ex(vectorBottomLeft, vectorBottomRight,
                       lineThickness, pyray.RED)
    pyray.draw_line_ex(vectorTopRight, vectorBottomLeft,
                       lineThickness, pyray.RED)

    # Circle-shape

    pyray.draw_circle(centerX, centerY, radius, pyray.BLACK)
    pyray.draw_circle(centerX, centerY, radius - 10, pyray.DARKBLUE)

   # Horizontal lines
    for i in range(numLines):
        offset_y = i * gapBetweenLines
        startVector = pyray.Vector2(
            startVectorTopLine.x, startVectorTopLine.y + offset_y)
        endVector = pyray.Vector2(
            endVectorTopLine.x, endVectorTopLine.y + offset_y)
        pyray.draw_line_ex(startVector, endVector,
                           lineThickness, pyray.DARKBLUE)

    # Triangle shapes and lines
    draw_isoscele_triangle(baseV1, baseV2, triangleHeight, pyray.YELLOW)
    draw_isoscele_triangle(
        pyray.Vector2(baseV2.x + gapBetweenTriangles, baseV2.y),
        pyray.Vector2(baseV2.x + gapBetweenTriangles +
                      (baseV2.x - baseV1.x), baseV2.y),
        triangleHeight, pyray.YELLOW
    )

    pyray.draw_poly(center, polySides, polyRadius, rotation, pyray.MAROON)

    # NOTE: We draw all LINES based shapes together to optimize internal drawing,
    # this way, all LINES are rendered in a single draw pass
    pyray.draw_line(18, 42, screenWidth - 18, 42, pyray.BLACK)

    pyray.end_drawing()

# De-Initialization
pyray.close_window()
