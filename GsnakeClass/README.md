# Geometry Snake

A fast-paced arcade runner built with Python and [raylib](https://www.raylib.com/) (via the `pyray` bindings).
You guide a glowing snake through increasingly dangerous cave corridors, collecting gems, coins, and stars while avoiding walls and obstacles.

---

## Table of Contents

1. [How to Play](#how-to-play)
2. [Installation](#installation)
3. [Running the Game](#running-the-game)
4. [Game Mechanics](#game-mechanics)
5. [Scoring System](#scoring-system)
6. [Levels](#levels)
7. [Codebase Structure](#codebase-structure)
8. [Adding New Levels](#adding-new-levels)
9. [Adding New Collectible Types](#adding-new-collectible-types)
10. [Configuration Reference](#configuration-reference)

---

## How to Play

### Controls

| Input | Action |
|---|---|
| `↑` / `↓` arrow keys | Navigate the level select menu |
| `Space` or `Enter` | Start selected level |
| **Hold** `Space` or **Hold** left mouse button | Steer the snake **upward** |
| **Release** | Snake drifts **downward** |
| `P` | Pause / Resume |
| `M` | Quit to main menu (from Pause, Game Over, or Level Complete screen) |
| `R` | Retry (on Game Over or Level Complete screen) |
| `D` | Toggle debug overlay (shows position, speed, scroll position, state) |

### Objective

Reach the end of the level without hitting:
- The **top or bottom screen boundary**
- Any **rectangular obstacle** or **spike cluster**

Collect as many items as possible along the way to maximise your score.

### Tips

- The snake **accelerates** as you progress through a level — the farther you go, the faster it gets.
- Stars are worth 10× a coin but are always placed near spikes or tight gaps.
- Watch the progress bar: obstacles get denser and speed ramps up in the final third of each level.

---

## Installation

### Requirements

- Python 3.10 or higher
- [`pyray`](https://pypi.org/project/raylib/) — Python bindings for raylib

### Install dependencies

```bash
pip install raylib
```

> `pyray` is the Python package name for the raylib bindings.
> It ships `raylib` as a compiled binary — no separate C library install needed.

---

## Running the Game

From the `GsnakeClass/` directory:

```bash
python main.py
```

Save data is written automatically to `saves/progress.json`
the first time you finish or die in a level. The file is created if it does not exist.

---

## Game Mechanics

### Fixed-timestep physics loop

The game uses a **fixed-timestep accumulator** pattern. Physics ticks run at exactly
60 Hz (`FIXED_DT = 1/60 s`) regardless of frame rate. If the system falls behind,
ticks are batched; the accumulator is capped at `MAX_ACCUMULATOR = 0.2 s` (≈ 12 ticks)
to prevent a spiral-of-death on slow hardware.

### Movement

The snake moves **horizontally at constant speed** (modified by the level's speed curve).
Vertical movement is binary:

- **Holding** Space / mouse → `velocity_y = −PLAYER_SPEED_Y` (up)
- **Releasing** → `velocity_y = +PLAYER_SPEED_Y` (down)

There is no gravity or inertia — the snake reacts instantly to input.

### Collision detection

Two checks run every physics tick:

| Check | Method |
|---|---|
| **Boundary** | Point test: `pos.y < 0` or `pos.y > SCREEN_HEIGHT` |
| **Obstacle** | Segment sweep: the movement vector `prev_pos → pos` is tested against each obstacle rectangle using parametric line intersection. An AABB broad-phase skips obstacles more than `LOOKAHEAD = 200 px` away. |

The sweep-based approach means the snake **cannot tunnel** through thin walls even at high speed.

> **Why no self-collision?** The snake always moves to the right — its x coordinate strictly increases every tick, so the head can never reach a previous trail point. Self-collision is geometrically impossible with this movement model.

### Camera

The camera smoothly follows the snake using **lerp** smoothing
(`CAMERA_LERP`, overridable per-level) and applies a **lookahead offset** so
the player sees more of what is ahead.

### Trail

The snake leaves a coloured quad-mesh trail that shifts from **cyan** at the start
of the level to **magenta** at the end. The trail renders in two passes:

1. **Glow pass** — wider, semi-transparent, limited to the most recent segments near the head
2. **Core pass** — tapered opaque line, full trail length

---

## Scoring System

| Item | Points | Appearance |
|---|---|---|
| Coin | 5 | Gold circle |
| Gem | 10 | Cyan diamond (rotated square) |
| Star | 50 | Yellow pentagon — always in a risky position |

The HUD (top-left panel) shows:
- Your current score (comma-formatted)
- Collectible dot indicators — filled yellow = collected, grey outline = not yet collected.
  If there are more than 12 collectibles, dots are replaced by an `X / Y` counter.
- A **progress bar** at the bottom of the screen showing level completion percentage.

Best scores and completion percentages are **saved automatically** to
`saves/progress.json` and displayed on the main menu for each level.

---

## Levels

The game ships with three levels that form a difficulty progression:

| # | Name | Length | Starting speed | Max speed | Gap width |
|---|---|---|---|---|---|
| 1 | Cave Run | 5 000 px | 1.0× | 1.5× | ~130 px |
| 2 | Crystal Depths | 6 000 px | 1.0× | 1.8× | ~140 px |
| 3 | The Gauntlet | 7 000 px | 1.2× | 2.2× | ~100 px |

Each level has a unique procedural parallax background (controlled by `parallax_seed`).

---

## Codebase Structure

```
GsnakeClass/
│
├── main.py          # Entry point + game loop + player, trail, obstacle, level, save, collision
├── ui.py            # All rendering: trail, parallax, particles, effects, HUD, menus
├── camera.py        # Smooth-follow camera with lerp and lookahead
├── collectible.py   # Collectible data class and build_collectibles() factory
├── settings.py      # All numeric constants (speed, physics, rendering)
│
├── levels/
│   ├── level1.json  # Cave Run
│   ├── level2.json  # Crystal Depths
│   └── level3.json  # The Gauntlet
│
└── saves/
    └── progress.json  # Auto-generated; stores best score/% per level
```

### Key data-flow summary

```
main.py
  └── Game.__init__()           creates window, SaveManager, menu objects
      Game.run()
        └── _update(dt)
              ├── MENU state  → MainMenu.handle_input()
              └── PLAYING     → _tick() each accumulated physics tick
                    ├── Player.update()
                    ├── Trail.update()
                    ├── Camera.update()
                    ├── ParticleSystem.update()
                    ├── collectible pickup check
                    └── boundary + obstacle sweep → _die() or _end()
            _render()
              ├── Renderer.draw()       (world space via Camera)
              ├── ScreenEffects.draw()  (screen space)
              ├── HUD.draw()            (screen space)
              └── menu overlay          (screen space, state-dependent)
```

---

## Adding New Levels

Levels are plain JSON files in the `levels/` directory. To add a level:

### Step 1 — Create the JSON file

Create `levels/levelN.json` using the schema below:

```jsonc
{
    "name": "My Level Name",          // Displayed in the menu and saved in progress.json
    "length": 5000,                   // World-space x-coordinate of the finish line (px)
    "parallax_seed": 42,              // Integer seed for the procedural background (change per level for a unique look)

    "speed_curve": [                  // Speed multiplier ramp — must have at least one entry
        {"x":    0, "mult": 1.0},     // At x=0, speed is 1× base
        {"x": 2500, "mult": 1.3},     // Linearly interpolated between waypoints
        {"x": 5000, "mult": 1.6}      // At the finish line, speed is 1.6×
    ],

    "camera": {
        "lookahead": 160,             // How many px ahead of the player the camera centres on
        "lerp": 0.08                  // Camera smoothing (0=instant, 1=no movement; 0.06–0.12 feels good)
    },

    "parallax": [                     // One entry per background layer (3 layers total)
        {"speed": 0.15},              // Far layer  — moves slowly (appears distant)
        {"speed": 0.35},              // Mid layer
        {"speed": 0.65}               // Near layer — moves fast (appears close)
    ],

    "obstacles": [ ... ],             // See obstacle types below
    "collectibles": [ ... ]           // See collectible types below
}
```

### Step 2 — Add obstacle entries

**Rectangle** — an axis-aligned solid block:

```json
{"type": "rect", "x": 800, "y": 0, "w": 40, "h": 250}
```

| Field | Description |
|---|---|
| `x` | Left edge in world space |
| `y` | Top edge (`y=0` is the top of the screen) |
| `w` | Width in pixels (40 is the standard wall thickness) |
| `h` | Height in pixels |

**Spikes** — a row of spike columns (rendered as thin rectangles for collision):

```json
{"type": "spikes", "x": 1200, "y": 480, "dir": "up", "count": 6}
```

| Field | Description |
|---|---|
| `x` | X position of the first spike |
| `y` | The baseline: floor position for `"up"`, ceiling position for `"down"` |
| `dir` | `"up"` (spikes pointing up from floor) or `"down"` (hanging from ceiling) |
| `count` | Number of spike columns (each 15 px wide) |

**Designing navigable gaps**

The screen is 600 px tall. To create a corridor the player can pass through,
place a top rectangle and a bottom rectangle at the same x with a gap between them:

```
Screen top  (y = 0)
  ┌──────────────────────────────────────────────────────┐
  │████████ top obstacle (y=0, h=220) ████████           │  <- y=220
  │                                                      │
  │   ~~ gap of 140 px ~~  (player navigates here)       │
  │                                                      │
  │████ bottom obstacle (y=360, h=240) ████████████████  │  <- y=360
  └──────────────────────────────────────────────────────┘
Screen bottom (y = 600)
```

```json
{"type": "rect", "x": 500, "y":   0, "w": 40, "h": 220},
{"type": "rect", "x": 500, "y": 360, "w": 40, "h": 240}
```

**Gap size guidelines:**

| Difficulty | Recommended gap | Notes |
|---|---|---|
| Easy | 160–200 px | Forgiving; good for early sections |
| Medium | 130–150 px | Requires active steering |
| Hard | 100–120 px | Very tight; pair with high speed for maximum challenge |

### Step 3 — Add collectible entries

```json
{"type": "coin", "x": 600,  "y": 200},
{"type": "gem",  "x": 1200, "y": 300},
{"type": "star", "x": 2000, "y": 480}
```

| Type | Points | Radius | Suggested placement |
|---|---|---|---|
| `coin` | 5 | 8 px | Open areas, easy to collect |
| `gem` | 10 | 10 px | Inside gaps, slight detour required |
| `star` | 50 | 12 px | Near spikes or tight corners |

### Step 4 — Register the level in `main.py`

Open `main.py` and add your level to the `GAME_LEVELS` list:

```python
GAME_LEVELS = [
    {"name": "Cave Run",       "path": "levels/level1.json"},
    {"name": "Crystal Depths", "path": "levels/level2.json"},
    {"name": "The Gauntlet",   "path": "levels/level3.json"},
    {"name": "My Level Name",  "path": "levels/levelN.json"},  # <-- add this line
]
```

The level will appear immediately in the main menu, including best score tracking.

---

## Adding New Collectible Types

1. Open `collectible.py` and add an entry to `COLLECTIBLE_TYPES`:

```python
COLLECTIBLE_TYPES = {
    "gem":     {"value": 10,  "radius": 10.0, "color": (0,   220, 255)},
    "coin":    {"value":  5,  "radius":  8.0, "color": (255, 200,  50)},
    "star":    {"value": 50,  "radius": 12.0, "color": (255, 230,   0)},
    "diamond": {"value": 100, "radius": 14.0, "color": (200, 100, 255)},  # new type
}
```

2. Open `ui.py` and add a drawing branch inside `Renderer.draw()`:

```python
elif collectible.type == "diamond":
    draw_poly(center, 4, collectible.radius,        0.0, Color(red, green, blue, 255))
    draw_circle_v(center, collectible.radius * 0.4, Color(255, 255, 255, 200))
```

3. Use `{"type": "diamond", "x": ..., "y": ...}` in any level JSON.

No other changes are needed — the HUD dot indicators, particle burst colours,
and score tracking all work automatically from the `Collectible` data class.

---

## Configuration Reference

All tuneable constants live in `settings.py`:

| Constant | Default | Description |
|---|---|---|
| `SCREEN_WIDTH` | 800 | Window width in pixels |
| `SCREEN_HEIGHT` | 600 | Window height in pixels |
| `FPS` | 60 | Target frame rate |
| `FIXED_DT` | 1/60 | Physics tick duration (seconds) |
| `MAX_ACCUMULATOR` | 0.2 | Max physics debt before clamping |
| `PLAYER_SPEED_X` | 250.0 | Horizontal speed at mult=1.0 (px/s) |
| `PLAYER_SPEED_Y` | 160.0 | Vertical speed when steering (px/s) |
| `TRAIL_MAX_LENGTH` | 500 | Maximum trail point count |
| `TRAIL_MIN_STEP` | 6.0 | Minimum distance between trail points |
| `LOOKAHEAD` | 200.0 | AABB broad-phase culling range (px) |
| `CAMERA_LERP` | 0.08 | Camera smoothing factor per tick |
| `CAMERA_LOOKAHEAD` | 160 | Camera offset ahead of player (px) |
| `PARTICLE_POOL_SIZE` | 200 | Pre-allocated particle slots |
| `PARTICLE_DEATH_COUNT` | 25 | Particles emitted on death |
| `FADE_DURATION` | 0.5 | Level fade-in duration (seconds) |
