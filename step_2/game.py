# Copyright (c) 2022-2025 IO-Swiss Aero GmbH. All rights reserved.
# Use of this source code is governed by the IO-Swiss Aero GmbH
# License, that can be found in the LICENSE.md file.

"""
game.py
Main game loop, now delegating drawing/behavior to sprites and UI helpers.

Reading guide for kids:
- Big blocks: setup → input → update → draw → collide → score → game over.
- Each block is short and commented.
- If you don't know a word, search for the variable in this file.
"""

from __future__ import annotations

import random
import sys
from typing import List, Tuple

import pygame

import settings as cfg
from models import Laser
from sprites import Player, Enemy, Explosion      # Step 2: our own sprites
from ui import draw_score, show_game_over_blocking  # Step 2: UI helpers

# --- Pygame setup (window + fonts) ---
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
pygame.display.set_caption(cfg.GAME_TITLE)

# Cache fonts (creating fonts per frame is slower)
score_font = pygame.font.SysFont(None, cfg.SCORE_FONT_SIZE)

# Pre-create star positions once so they don't "jump" each frame.
stars: List[Tuple[int, int]] = [
    (random.randint(0, cfg.WIDTH), random.randint(0, cfg.HEIGHT))
    for _ in range(cfg.NUM_STARS)
]


def draw_star_field(surface: pygame.Surface) -> None:
    """Draw small white dots (stars) in the background."""
    for sx, sy in stars:
        pygame.draw.circle(surface, cfg.STAR_COLOR, (sx, sy), cfg.STAR_RADIUS)


def draw_and_move_lasers(surface: pygame.Surface, lasers: List[Laser]) -> None:
    """Draw each laser and move it to the right."""
    for l in lasers:
        start = (l.x, l.y)
        end = (l.x + cfg.LASER_WIDTH, l.y)
        pygame.draw.line(surface, cfg.LASER_COLOR, start, end, cfg.LASER_THICKNESS)
        l.x += cfg.LASER_SPEED_X


def _laser_rect(l: Laser) -> pygame.Rect:
    """A small rectangle approximating the laser beam for collisions."""
    half_thick = max(1, cfg.LASER_THICKNESS // 2)
    return pygame.Rect(l.x, l.y - half_thick, cfg.LASER_WIDTH, cfg.LASER_THICKNESS)


def run_round() -> int:
    """Run one round of the game and return the final score."""
    # --- Round state (resets every round) ---
    player = Player()
    enemies: List[Enemy] = [Enemy(speed=cfg.FIRST_SHIP_SPEED)]
    explosions: List[Explosion] = []
    lasers: List[Laser] = []

    ship_speed: int = cfg.FIRST_SHIP_SPEED
    score: int = 0
    spawn_new_enemy: bool = False

    clock = pygame.time.Clock()
    running = True

    # --- Main loop ---
    while running:
        # 1) Events (quit, one-shot keys like SPACE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    lasers.append(player.shoot())
                elif event.key == pygame.key.key_code("r"):
                    # Debug: spawn an extra enemy
                    enemies.append(Enemy(speed=ship_speed))

        # 2) Continuous input (held keys)
        player.handle_input(pygame.key.get_pressed())

        # 3) Spawn a new enemy if flagged (after a destroy)
        if spawn_new_enemy:
            enemies.append(Enemy(speed=ship_speed))
            spawn_new_enemy = False

        # 4) UPDATE world (move enemies, grow explosions, cull finished)
        for e in enemies[:]:
            e.update()
            if e.reached_end():
                # An enemy got past us → round ends.
                enemies.remove(e)
                running = False

        for ex in explosions[:]:
            ex.update()
            if ex.done():
                explosions.remove(ex)

        # 5) DRAW everything (background → player → enemies → lasers → explosions → UI)
        screen.fill((0, 0, 0))
        draw_star_field(screen)
        player.draw(screen)

        for e in enemies:
            e.draw(screen)

        draw_and_move_lasers(screen, lasers)

        for ex in explosions:
            ex.draw(screen)

        # 6) LASER housekeeping (offscreen → big boom for fun)
        for l in lasers[:]:
            if l.x >= cfg.LASER_RIGHT_LIMIT:
                explosions.append(Explosion(x=l.x, y=l.y))
                lasers.remove(l)

        # 7) COLLISIONS: laser vs enemy
        for l in lasers[:]:
            lrect = _laser_rect(l)
            for e in enemies[:]:
                if lrect.colliderect(e.bbox):
                    explosions.append(Explosion(x=l.x, y=l.y))
                    enemies.remove(e)
                    lasers.remove(l)
                    spawn_new_enemy = True
                    score += 1
                    if cfg.SPEED_UP_EVERY > 0 and (score % cfg.SPEED_UP_EVERY == 0):
                        ship_speed += 1
                    break  # this laser is consumed

        # 8) UI (score on top-right)
        draw_score(screen, score, font=score_font)

        pygame.display.flip()
        clock.tick(cfg.FPS)

    return score


def main() -> None:
    """Play forever: run a round → show game over → repeat."""
    while True:
        score = run_round()
        show_game_over_blocking(screen, score)


if __name__ == "__main__":
    main()
