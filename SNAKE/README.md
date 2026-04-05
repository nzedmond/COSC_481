# SNAKE — Improved Edition

A feature-rich Snake game built with Python and [raylib](https://github.com/electronstudio/raylib-python-cffi).

---

## Requirements

```
pip install raylib
```

## Running the game

```
cd SNAKE
python main.py
```

---

## Controls

| Key | Action |
|---|---|
| Arrow Keys | Change direction |
| `[` / `]` | Decrease / increase speed |
| `P` | Pause / resume |
| `ENTER` | Start game / restart after game over |
| `M` | Return to menu (game over screen only) |
| `I` / `BACKSPACE` | Open / close instructions screen |

---

## Game Modes

Select a mode from the main menu using **Up/Down** then **ENTER**.

| Mode | Description |
|---|---|
| **Classic** | Standard snake. Obstacles appear every 3 points (max 20). |
| **Time Attack** | Score as many points as possible within **60 seconds**. Timer shown in the header; turns red when ≤ 10 s remain. |
| **Survival** | Snake speeds up every 5 points. Obstacles spawn every 2 points. Designed to end — survive as long as you can. |

---

## Food

One food item is active at all times. When eaten, a floating score label appears briefly at the collision point, and a new food of a random type spawns immediately.

| Colour | Type | Score | Effect |
|---|---|---|---|
| Red | Normal | +1 | Snake grows |
| Gold | Golden | +3 | Snake grows (15% spawn chance) |
| Purple | Poison | −1 | Snake shrinks by 1 segment. Disappears on its own after **5 s** — a white timer bar above it shows how long it has left. Score cannot go below 0. |
| Orange | Moving | +2 | Bounces around the play area. Snake grows. |

---

## Power-ups

A white-bordered pickup appears on the field every **5 seconds**. Collecting it activates the effect immediately. Active effects are shown as a text label with a duration bar in the header.

| Colour | Effect | Duration |
|---|---|---|
| **Yellow** Shield | Absorbs the next lethal collision (wall, self, or obstacle) | 10 s or 1 hit |
| **Lime** Shrink | Instantly removes 3 tail segments — useful in tight spots | Instant |

---

## Obstacles

Brown wall segments that kill the snake on contact (Shield absorbs one hit).

- **Classic / Time Attack**: one new wall every 3 points, up to a maximum of 20.
- **Survival**: one new wall every 2 points, up to 20.

Food and power-up pickups never spawn on top of wall tiles.

---

## Scoring

| Event | Score change |
|---|---|
| Eat normal food | +1 |
| Eat golden food | +3 |
| Eat poison food | −1 (min 0) |
| Eat moving food | +2 |

The best score is saved to `data/highscore.json` and persists between sessions.

---

## Project structure

```
SNAKE/
├── main.py             # Window init, game loop
├── game.py             # Game class, screen routing, collision, mode logic
├── snake.py            # Snake movement, input, speed control
├── food.py             # Food types, movement, lifespan
├── powerups.py         # Powerup effects, pickup spawning, manager
├── obstacles.py        # Wall obstacles, manager
├── ui.py               # All rendering (header, menus, HUD, popups)
├── sprite_animator.py  # Spritesheet animation helper
├── audio.py            # Music and sound effect management
├── parallax.py         # Scrolling parallax background
├── settings.py         # All constants and enums (single source of truth)
└── data/
    ├── highscore.json
    └── snake.log
```
