# settings.py
# Copyright (c) 2022-2025 IO-Swiss Aero GmbH. All rights reserved.
# Use of this source code is governed by the IO-Swiss Aero GmbH
# License, that can be found in the LICENSE.md file.

"""
Centralized game settings.

Tweak values here to rebalance gameplay or adjust visuals without hunting
through the codebase. All distances are in pixels, speeds in pixels per frame,
and colors are RGB tuples in the 0–255 range.

Quick tuning tips
-----------------
- Make the game faster: raise FPS or increase *_SPEED_* / *_STEP constants.
- Make difficulty scale harder: lower SPEED_UP_EVERY, or raise FIRST_SHIP_SPEED.
- Reduce visual clutter/perf cost: reduce NUM_STARS or STAR_RADIUS.
"""

from typing import Tuple

# ───────────────────────────── Screen / Timing ──────────────────────────────
WIDTH: int = 1900
# Width of the game window in pixels. A wider screen gives enemies more travel
# distance and slightly increases average time-to-impact.

HEIGHT: int = 1000
# Height of the game window in pixels. Taller screens allow more vertical maneuvering.

FPS: int = 60
# Target frames per second. Higher values make motion smoother but can increase
# CPU/GPU usage. Typical ranges: 30 (low), 60 (standard), 120+ (high-refresh).


# ───────────────────────────── Background Stars ─────────────────────────────
NUM_STARS: int = 1000
# Number of background stars to render. Higher values look richer but cost more
# draw calls. Typical: 200–1500 for 2D games.

STAR_COLOR: Tuple[int, int, int] = (255, 255, 255)
# RGB color of stars. Keep near white for a space look (e.g., (220, 230, 255)
# for a cooler tone).

STAR_RADIUS: int = 2
# Pixel radius of each star. 1–3 is subtle; >3 starts to look like orbs.


# ───────────────────────────── Player Rocket ────────────────────────────────
PLAYER_START_Y: int = 250
# Initial vertical position (y) of the player's rocket in pixels from top.
# Choose a value that keeps the rocket comfortably visible on spawn.

PLAYER_MOVE_STEP: int = 10
# Vertical movement increment in pixels per input tick. Higher = snappier
# control, but easier to overshoot. Range: 4–20 for most screens.

ROCKET_X: int = 50
# Fixed x-position of the rocket (if player only moves vertically). Adjust
# if you change the screen width or want more oncoming space.

ROCKET_BODY_COLOR: Tuple[int, int, int] = (200, 200, 255)
# Main body color (RGB). Pastels read well against dark space backgrounds.

ROCKET_NOSE_COLOR: Tuple[int, int, int] = (180, 0, 0)
# Nose/cone accent color.

ROCKET_WINDOW_COLOR: Tuple[int, int, int] = (0, 150, 255)
# Window/porthole color.

FLAME_COLOR: Tuple[int, int, int] = (255, 140, 0)
# Engine flame color. Warm oranges suggest combustion; blues feel sci-fi.

FLAME_MIN: int = 15
FLAME_MAX: int = 30
# Minimum/maximum flame length in pixels. If your flame is animated with
# a random or sinusoidal size, these define the bounds. Keep MAX > MIN and
# avoid values so large that flames overlap UI or the rocket body.


# ───────────────────────────── Player Lasers ────────────────────────────────
LASER_SPEED_X: int = 50
# Horizontal laser speed in pixels per frame. Increasing this reduces the time
# a shot spends on screen and can reduce collision chance against fast enemies.

LASER_COLOR: Tuple[int, int, int] = (255, 0, 0)
# Beam color (RGB). Bright saturated colors maximize visibility on dark space.

LASER_WIDTH: int = 20
# Visual beam length in pixels (used by the renderer). Big values look like
# bolts; small values look like dots. Also affects collision if you use
# sprite-size based hitboxes.

LASER_THICKNESS: int = 10
# Beam thickness in pixels. Larger thickness increases perceived hit area if
# your collision matches render size.

LASER_RIGHT_LIMIT: int = 1850
# X-position beyond which lasers are removed to free resources. This should be
# slightly less than WIDTH to avoid drawing off-screen. If you change WIDTH,
# consider updating this to WIDTH - margin.


# ───────────────────────────── Explosions ───────────────────────────────────
MAX_BLAST_RADIUS: int = 300
# Maximum explosion radius in pixels at peak animation. Large radii feel epic
# but can obscure gameplay and cost more fill-rate (alpha blends).


# ───────────────────────────── Enemies / Difficulty ─────────────────────────
FIRST_SHIP_SPEED: int = 5
# Initial enemy horizontal speed in pixels per frame. Combined with speed-ups
# below, this sets early-game difficulty. Typical: 2–8.

SPEED_UP_EVERY: int = 3
# After every N enemy destroys, increase enemy speed (e.g., by +1 px/frame).
# Lower values = faster difficulty ramp. Set to 0/1 for very aggressive scaling.


# ───────────────────────────── UI / Text ────────────────────────────────────
SCORE_COLOR: Tuple[int, int, int] = (255, 255, 0)
# HUD score color (RGB). Yellow stands out against space and most sprites.

SCORE_FONT_SIZE: int = 50
# Font size for the score, in points/pixels depending on font backend.

GAME_OVER_FONT_SIZE: int = 150
# Font size for the "Game Over" banner. Should be large enough for instant read.

GAME_TITLE: str = "-<>- Johnny's Space Game -<>-"
# Window title / splash text. Keep it short to avoid clipping in window chrome.
