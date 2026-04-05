# SNAKE — Improved Edition

> A modern take on the classic Snake game — built in Python with raylib, featuring multiple game modes, dynamic obstacles, power-ups, animated sprites, a procedural parallax background, and per-mode music.

Snake is a single-player arcade game where you guide a growing snake around a grid, eating food to score points while avoiding walls, obstacles, and your own tail. This improved edition layers on top of that foundation with four food variants (including a bouncing moving food and a timed poison), two power-up effects, progressively spawning wall obstacles, three distinct game modes with unique difficulty curves, and real-time audio and visual feedback for every game event.

---

## Key Features

### Multiple Food Types with Distinct Mechanics
Food is not a single item — each of the four types has different behaviour, score value, and spawn probability. Poison food has a **5-second lifespan** tracked by an on-tile timer bar; if ignored it expires and re-randomises. Moving food bounces around the play area using per-frame velocity with wall reflection, forcing the player to intercept a moving target.

### Three Game Modes
- **Classic** — standard Snake with progressively spawning wall obstacles.
- **Time Attack** — fixed 60-second window; score as much as possible before time runs out.
- **Survival** — speed escalates every 5 points using `move_interval = max(1, BASE - score // 5)`, approaching 60 moves/second. Designed to always end eventually.

### Power-up System
Power-ups use a base class / subclass pattern with `apply()` and `remove()` hooks. A pickup spawns every 5 seconds; collecting it either triggers an instant effect (Shrink: removes 3 tail segments) or a timed effect (Shield: absorbs the next lethal collision). Active timed effects are shown as a labelled duration bar in the header — intentionally separated from the play field to avoid confusion with collectible items.

### Floating Score Popups
Each food collision spawns a floating `+1` / `+3` / `-1` label at the eaten tile's position. It rises upward and fades out over 20 frames, coloured green for gains and red for losses, giving spatially-grounded feedback without interrupting gameplay.

### Animated Sprites via Spritesheet
A `SpriteAnimator` class steps through frames of a single-row spritesheet using `draw_texture_pro`, scaling each frame to fit the tile size regardless of source resolution. The Poison food and obstacle tiles use animated sprites; other types fall back to coloured rectangles with letter labels.

### Procedural Parallax Background
The background is generated from three layers of randomly placed rectangles (far, mid, near) with different colours, densities, and size ranges. A fixed random seed (`42`) ensures it looks identical every session without needing an image asset.

### Collision-Safe Spawning
Food, power-ups, and obstacles all use the same pattern: build a set of occupied `(x, y)` coordinates from the snake body + existing obstacles, then retry random grid candidates until a clear cell is found. This guarantees nothing ever spawns on top of something else, even on a crowded board.

### Per-Mode Music and Per-Food Sound Effects
Each game mode plays a distinct background track. Each food type triggers its own sound effect on collision. The `AudioManager` tracks the currently playing track and only switches when the screen or mode actually changes, avoiding unnecessary restarts.

### High Score Persistence and Event Logging
The best score is saved to `data/highscore.json` and restored on startup. Every significant event (mode start, food eaten, shield absorbed, game over, new record) is appended to `data/snake.log` via Python's `logging` module.

### Debug Mode
Press `D` during gameplay to reveal an overlay with FPS, head tile coordinates, snake length, move interval, food type, and active power-ups. `G` toggles collision immunity (god mode); `F` / `N` force-eat food or spawn a power-up instantly — useful for testing any mechanic without playing through naturally.

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

## Resources

>NOTE: I MADE ALL THE MUSIC AND SOUND EFFECT BY HITTING RANDOM KEYS ON THE PIANO AND DRUMS IN COLGATE MEMORIAL CHAPEL BASEMENT (SOME MIGHT NOT HAVE GOOD MELODY). I THEN USED DAVINCI RESOLVE SOFTWARE TO ADJUST VOLUMES AND CONVERT TO THE FORMATS SUPPORTED BY RAYLIB.

### Music
| File | Used in |
|---|---|
| `menu.mp3` | Main menu and all non-gameplay screens |
| `classic.mp3` | Classic mode |
| `attack.mp3` | Time Attack mode |
| `survival.mp3` | Survival mode |

### Sound Effects
| File | Triggered by |
|---|---|
| `hit-01.wav` | Eating Normal food |
| `hit-02.wav` | Eating Golden food |
| `hit-03.wav` | Eating Poison food |
| `hit-04.wav` | Eating Moving food |

### Sprites
| File | Used for |
|---|---|
| `devil.png` | Poison food animated tile (5-frame spritesheet) |
| `kkiller.png` | Obstacle animated tile (8-frame spritesheet) |

**SOURCES:** `https://www.freepik.com/vectors/demon-sprite-sheet`, `https://www.spriters-resource.com/arcade/kingofdragons/asset/522706/`

### Some Code Snippets
`sprite_animator.py`: Recycled from LAB_04, `text_anim.py`
`parallax.py`: Inspired by the lecture on `Camera+background`

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
