"""

raylib version: 5.5.0.3

raylib [core] example - random sequence

"""

from pyray import *


class ColorRect:
    color: Color
    rect: Rectangle


def generate_random_color_rect_sequence(
    rect_count: int, rect_width: float, screen_width: int, screen_height: float
) -> list:
    rectangles = []

    seq = load_random_sequence(rect_count, 0, rect_count - 1)
    rect_seq_width = rect_count * rect_width
    start_x = (screen_width - rect_seq_width) * 0.5

    for i in range(rect_count):
        rect_height = remap(seq[i], 0, rect_count - 1, 0, screen_height)

        rectangles += [ColorRect()]
        rectangles[i].color = Color(
            get_random_value(0, 255),
            get_random_value(0, 255),
            get_random_value(0, 255),
            255,
        )
        rectangles[i].rect = Rectangle(
            start_x + i * rect_width,
            screen_height - rect_height,
            rect_width,
            rect_height,
        )
    return rectangles


def shuffle_color_rect_sequence(rectangles: list, rect_count: int):
    seq = load_random_sequence(rect_count, 0, rect_count - 1)

    for i in range(rect_count):
        r1 = rectangles[i]
        r2 = rectangles[seq[i]]

        tmp_color = r1.color
        tmp_h = r1.rect.height
        tmp_y = r1.rect.y

        r1.color = r2.color
        r1.rect.height = r2.rect.height
        r1.rect.y = r2.rect.y
        r2.color = tmp_color
        r2.rect.height = tmp_h
        r2.rect.y = tmp_y


def move_right(rectangles, rect_count):
    '''
    1. Not doing .rect.property when retrieving data
    2. I was confused by the question at first
    3. Tried swapping rectangles and didn't work(They're objects, I had to transfer properties)
    '''
    if rect_count <= 1:
        return
    
    last_color = rectangles[-1].color
    last_y = rectangles[-1].rect.y
    last_h = rectangles[-1].rect.height

    for i in range(rect_count-1, 0, -1):
        rectangles[i].color = rectangles[i-1].color
        rectangles[i].rect.height = rectangles[i-1].rect.height
        rectangles[i].rect.y = rectangles[i-1].rect.y

    rectangles[0].rect.height = last_h
    rectangles[0].color = last_color
    rectangles[0].rect.y = last_y


# WARMP UP
def sort_rectangles(rectangles, rect_count):
    for i in range(rect_count):
        for j in range(0, rect_count - i - 1):
            if rectangles[j].rect.height > rectangles[j+1].rect.height:
                rectangles[j].color, rectangles[j+1].color = ((rectangles[j+1].color, 
                                                              rectangles[j].color))
                
                rectangles[j].rect.height, rectangles[j+1].rect.height = (rectangles[j+1].rect.height, rectangles[j].rect.height )
                
                rectangles[j].rect.y, rectangles[j+1].rect.y = (rectangles[j+1].rect.y, rectangles[j].rect.y)


screen_width = 800
screen_height = 450

init_window(screen_width, screen_height,
            "raylib [core] example - random sequence")
set_target_fps(60)
rect_count = 20
rect_size = screen_width / rect_count
rectangles = generate_random_color_rect_sequence(
    rect_count, rect_size, screen_width, 0.65 * screen_height
)


while not window_should_close():

    if is_key_pressed(KeyboardKey.KEY_SPACE):
        shuffle_color_rect_sequence(rectangles, rect_count)

    if is_key_pressed(KeyboardKey.KEY_UP):
        rect_count += 1
        rect_size = screen_width / rect_count
        rectangles = generate_random_color_rect_sequence(
            rect_count, rect_size, screen_width, 0.65 * screen_height
        )

    if is_key_pressed(KeyboardKey.KEY_DOWN):
        if rect_count >= 4:
            rect_count -= 1
            rect_size = screen_width / rect_count
            rectangles = generate_random_color_rect_sequence(
                rect_count, rect_size, screen_width, 0.65 * screen_height
            )
    if is_key_pressed(KeyboardKey.KEY_RIGHT):
        move_right(rectangles, rect_count)
        
    if is_key_pressed(KeyboardKey.KEY_LEFT):
        sort_rectangles(rectangles, rect_count)
        
    begin_drawing()

    clear_background(RAYWHITE)

    for i in range(rect_count):
        draw_rectangle_rec(rectangles[i].rect, rectangles[i].color)
        draw_text(
            "Press SPACE to shuffle the current sequence",
            10,
            screen_height - 96,
            20,
            BLACK,
        )
        draw_text(
            "Press UP to add a rectangle and generate a new sequence",
            10,
            screen_height - 64,
            20,
            BLACK,
        )
        draw_text(
            "Press DOWN to remove a rectangle and generate a new sequence",
            10,
            screen_height - 32,
            20,
            BLACK,
        )
        draw_text(
            "Press RIGHT to rotate the sequence to the right",
            10,
            screen_height - 120,
            20,
            BLACK,
        )

    draw_text(f"Count: {rect_count} rectangles", 10, 10, 20, MAROON)
    draw_fps(screen_width - 80, 10)
    end_drawing()
close_window()
