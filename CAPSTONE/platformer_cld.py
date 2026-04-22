from pyray import *

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 1024

GRAVITY_ACCELERATION = 50.0
MAX_N_OBSTACLES = 64

PLAYER_MAX_HEALTH = 100.0
MAX_SPEED_WITHOUT_DAMAGE = 30.0

BACKGROUND_COLOR = Color(20, 20, 20, 255)
OBSTACLE_COLOR = Color(80, 80, 80, 255)
UI_BACKGROUND_COLOR = Color(40, 40, 40, 255)


# -----------------------------------------------------------------------
# Player state
class PlayerState:
    def __init__(self):
        self.position = Vector2(0.0, 0.0)
        self.velocity = Vector2(0.0, 0.0)
        self.size = Vector2(0.0, 0.0)
        self.speed = 0.0
        self.jump_impulse = 0.0
        self.health = 0.0
        self.max_health = 0.0
        self.is_grounded = False


PLAYER = PlayerState()


# -----------------------------------------------------------------------
# Obstacle state
class ObstacleState:
    def __init__(self):
        self.rect = Rectangle(0.0, 0.0, 0.0, 0.0)
        self.start = Vector2(0.0, 0.0)
        self.end = Vector2(0.0, 0.0)
        self.speed = 0.0
        self.is_moving_to_start = False
        self.is_player_attached = False


N_OBSTACLES = 0
OBSTACLES = [ObstacleState() for _ in range(MAX_N_OBSTACLES)]

# -----------------------------------------------------------------------
# Camera
CAMERA = Camera2D(
    Vector2(0.5 * SCREEN_WIDTH, 0.5 * SCREEN_HEIGHT),  # offset
    Vector2(0.0, 0.0),                                  # target
    0.0,                                                 # rotation
    20.0                                                 # zoom
)

# health view persists across frames
health_view = PLAYER_MAX_HEALTH


# -----------------------------------------------------------------------
# utils

def randf():
    return get_random_value(0, 2147483647) / 2147483647.0


def randf_min_max(min_val, max_val):
    p = randf()
    return min_val + p * (max_val - min_val)


def get_aabb_mtv(r1: Rectangle, r2: Rectangle) -> Vector2:
    mtv = Vector2(0.0, 0.0)
    if not check_collision_recs(r1, r2):
        return mtv

    x_west = r2.x - r1.x - r1.width
    x_east = r2.x + r2.width - r1.x
    mtv.x = x_west if abs(x_west) < abs(x_east) else x_east

    y_south = r2.y + r2.height - r1.y
    y_north = r2.y - r1.y - r1.height
    mtv.y = y_south if abs(y_south) < abs(y_north) else y_north

    if abs(mtv.x) > abs(mtv.y):
        mtv.x = 0.0
    else:
        mtv.y = 0.0

    return mtv


def lerp_color(min_color: Color, max_color: Color, ratio: float) -> Color:
    return Color(
        int((1.0 - ratio) * min_color[0] + ratio * max_color[0]),
        int((1.0 - ratio) * min_color[1] + ratio * max_color[1]),
        int((1.0 - ratio) * min_color[2] + ratio * max_color[2]),
        int((1.0 - ratio) * min_color[3] + ratio * max_color[3]),
    )


# -----------------------------------------------------------------------
# obstacle

def spawn_obstacle(rect: Rectangle, start: Vector2, end: Vector2, speed: float) -> int:
    global N_OBSTACLES
    if N_OBSTACLES == MAX_N_OBSTACLES:
        return -1

    idx = N_OBSTACLES
    N_OBSTACLES += 1
    o = OBSTACLES[idx]
    o.rect = rect
    o.start = start
    o.end = end
    o.speed = speed
    return idx


def spawn_static_obstacle(rect: Rectangle) -> int:
    start = Vector2(rect.x, rect.y)
    end = Vector2(rect.x, rect.y)
    return spawn_obstacle(rect, start, end, 0.0)


def draw_obstacles():
    for i in range(N_OBSTACLES):
        draw_rectangle_rec(OBSTACLES[i].rect, OBSTACLE_COLOR)


def update_obstacles():
    dt = get_frame_time()

    for i in range(N_OBSTACLES):
        o = OBSTACLES[i]
        if not (o.speed > 0.0):
            continue

        direction = vector2_subtract(o.end, o.start)
        direction = vector2_normalize(direction)
        if o.is_moving_to_start:
            direction = vector2_negate(direction)

        position_step = vector2_scale(direction, dt * o.speed)
        o.rect.x += position_step.x
        o.rect.y += position_step.y

        if o.is_player_attached:
            PLAYER.position = vector2_add(PLAYER.position, position_step)

        position = Vector2(o.rect.x, o.rect.y)
        target = o.start if o.is_moving_to_start else o.end
        to_target_direction = vector2_subtract(target, position)
        is_to_target = vector2_dot_product(direction, to_target_direction) > 0.0

        if not is_to_target:
            clamped = o.start if o.is_moving_to_start else o.end
            o.rect.x = clamped.x
            o.rect.y = clamped.y
            o.is_moving_to_start = not o.is_moving_to_start


# -----------------------------------------------------------------------
# player

def get_player_rect() -> Rectangle:
    return Rectangle(
        PLAYER.position.x + 0.5 * PLAYER.size.x,
        PLAYER.position.y + PLAYER.size.y,
        PLAYER.size.x,
        PLAYER.size.y,
    )


def update_player():
    dt = get_frame_time()

    PLAYER.velocity.y += GRAVITY_ACCELERATION * dt

    direction = Vector2(0.0, 0.0)
    if is_key_down(KeyboardKey.KEY_A):
        direction.x -= 1.0
    if is_key_down(KeyboardKey.KEY_D):
        direction.x += 1.0

    direction = vector2_normalize(direction)
    position_step = vector2_scale(direction, PLAYER.speed * dt)

    if is_key_pressed(KeyboardKey.KEY_W) and PLAYER.is_grounded:
        PLAYER.velocity.y -= PLAYER.jump_impulse

    position_step = vector2_add(position_step, vector2_scale(PLAYER.velocity, dt))
    PLAYER.position = vector2_add(PLAYER.position, position_step)


def update_player_collisions():
    mtv_min_x = 0.0
    mtv_max_x = 0.0
    mtv_min_y = 0.0
    mtv_max_y = 0.0

    for i in range(N_OBSTACLES):
        o = OBSTACLES[i]
        player_rect = get_player_rect()
        mtv = get_aabb_mtv(player_rect, o.rect)

        mtv_min_x = min(mtv_min_x, mtv.x)
        mtv_max_x = max(mtv_max_x, mtv.x)
        mtv_min_y = min(mtv_min_y, mtv.y)
        mtv_max_y = max(mtv_max_y, mtv.y)

        o.is_player_attached = mtv.y < 0.0 and o.speed > 0.0

    mtv = Vector2(mtv_min_x, mtv_min_y)
    if abs(mtv_max_x) > abs(mtv_min_x):
        mtv.x = mtv_max_x
    if abs(mtv_max_y) > abs(mtv_min_y):
        mtv.y = mtv_max_y

    PLAYER.position = vector2_add(PLAYER.position, mtv)

    is_just_grounded = mtv.y < 0.0 and PLAYER.velocity.y > 0.0
    if is_just_grounded:
        speed = vector2_length(PLAYER.velocity)
        damage = speed - MAX_SPEED_WITHOUT_DAMAGE
        damage = max(0.0, damage)
        PLAYER.health -= damage
        PLAYER.velocity = Vector2(0.0, 0.0)
        PLAYER.is_grounded = True
    elif mtv.y > 0.0 and PLAYER.velocity.y < 0.0:
        PLAYER.velocity.y = 0.0
    else:
        PLAYER.is_grounded = False


def draw_player():
    draw_rectangle_rec(get_player_rect(), ORANGE)


# -----------------------------------------------------------------------
# UI

def draw_ui():
    global health_view

    margin = 10.0
    pad = 5.0
    width = 300.0
    height = 40.0
    health_view_speed = 80.0
    dt = get_frame_time()

    if PLAYER.health < health_view:
        health_view -= dt * health_view_speed
        health_view = max(health_view, PLAYER.health)
    else:
        health_view = PLAYER.health

    background_rect = Rectangle(margin, margin, width, height)

    health_ratio = PLAYER.health / PLAYER.max_health
    healthbar_rect = Rectangle(
        background_rect.x + pad,
        background_rect.y + pad,
        (background_rect.width - 2.0 * pad) * health_ratio,
        background_rect.height - 2.0 * pad,
    )

    healthbar_color = lerp_color(RED, GREEN, health_ratio)

    difference_ratio = health_view / PLAYER.max_health
    difference_rect = Rectangle(
        healthbar_rect.x,
        healthbar_rect.y,
        (background_rect.width - 2.0 * pad) * difference_ratio,
        healthbar_rect.height,
    )

    draw_rectangle_rounded(background_rect, 0.2, 16, UI_BACKGROUND_COLOR)
    draw_rectangle_rounded(difference_rect, 0.2, 16, WHITE)
    draw_rectangle_rounded(healthbar_rect, 0.2, 16, healthbar_color)


# -----------------------------------------------------------------------
# game

def load_game():
    global N_OBSTACLES, health_view

    PLAYER.position = Vector2(0.0, 0.0)
    PLAYER.velocity = Vector2(0.0, 0.0)
    PLAYER.size = Vector2(1.0, 2.0)
    PLAYER.speed = 15.0
    PLAYER.jump_impulse = 30.0
    PLAYER.max_health = PLAYER_MAX_HEALTH
    PLAYER.health = PLAYER.max_health

    health_view = PLAYER_MAX_HEALTH
    N_OBSTACLES = 0

    # ground
    spawn_static_obstacle(Rectangle(-20.0, 20.0, 40.0, 2.5))

    # left wall
    spawn_static_obstacle(Rectangle(-20.0, -100.0, 2.5, 120.0))

    # left stair
    spawn_static_obstacle(Rectangle(-17.5, 15.0, 2.5, 5.0))

    # right wall
    spawn_static_obstacle(Rectangle(17.5, -100.0, 2.5, 120.0))

    # moving platforms
    x_min = -15.0
    x_max = 5.0
    for i in range(10):
        y = 8.0 - i * 8.0
        x = randf_min_max(x_min, x_max)
        speed = randf_min_max(5.0, 9.0)
        spawn_obstacle(
            Rectangle(x, y, 10.0, 2.5),
            Vector2(x_min, y),
            Vector2(x_max, y),
            speed,
        )


def load():
    set_config_flags(ConfigFlags.FLAG_MSAA_4X_HINT)
    init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Platforms")
    set_target_fps(60)
    load_game()


def update_reset():
    if is_key_pressed(KeyboardKey.KEY_R):
        load_game()


def update_camera():
    target = PLAYER.position
    distance = vector2_distance(target, CAMERA.target)
    direction = vector2_normalize(vector2_subtract(target, CAMERA.target))
    position_step = vector2_scale(direction, 0.1 * distance)
    CAMERA.target = vector2_add(CAMERA.target, position_step)


def update():
    update_reset()
    update_player()
    update_obstacles()
    update_player_collisions()
    update_camera()


def draw():
    begin_drawing()
    clear_background(BACKGROUND_COLOR)

    begin_mode_2d(CAMERA)
    draw_player()
    draw_obstacles()
    end_mode_2d()

    draw_ui()
    end_drawing()


def unload():
    close_window()


# -----------------------------------------------------------------------
# main

if __name__ == "__main__":
    load()

    while not window_should_close():
        update()
        draw()

    unload()
