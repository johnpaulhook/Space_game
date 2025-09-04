"""
game.py
The main game loop. Written to be friendly for beginners.

Reading guide for kids:
- Look at the big blocks first: setup, draw, input, update, game over.
- Each block is short and has comments that tell you what's happening.
- If you don't know a word, search for the variable in this file.
"""

from __future__ import annotations

import random
import sys
from typing import List, Tuple

import numpy as np
import pygame

import settings as cfg
from models import Laser
from game_objects import Ship, Explosion  # we’ll replace these later with our own

# --- Pygame setup (window + fonts) ---
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
pygame.display.set_caption(cfg.GAME_TITLE)

# We create all star positions once (so they don't "jump" each frame).
stars: List[Tuple[int, int]] = [
    (random.randint(0, cfg.WIDTH), random.randint(0, cfg.HEIGHT))
    for _ in range(cfg.NUM_STARS)
]


def draw_star_field(surface: pygame.Surface) -> None:
    """Draws small white dots (stars) in the background."""
    for sx, sy in stars:
        pygame.draw.circle(surface, cfg.STAR_COLOR, (sx, sy), cfg.STAR_RADIUS)


def draw_player_rocket(surface: pygame.Surface, y: int) -> None:
    """Draws the player's rocket at x = ROCKET_X and given y position."""
    x = cfg.ROCKET_X

    # Body
    pygame.draw.rect(surface, cfg.ROCKET_BODY_COLOR, (x, y - 20, 50, 40))

    # Nose cone (a triangle)
    pygame.draw.polygon(surface, cfg.ROCKET_NOSE_COLOR, [
        (x + 50, y - 20),
        (x + 50, y + 20),
        (x + 70, y)
    ])

    # Fins (triangles)
    pygame.draw.polygon(surface, cfg.ROCKET_NOSE_COLOR, [
        (x, y - 20),
        (x - 15, y - 30),
        (x, y - 30)
    ])
    pygame.draw.polygon(surface, cfg.ROCKET_NOSE_COLOR, [
        (x, y + 20),
        (x - 15, y + 30),
        (x, y + 30)
    ])

    # Window (a circle)
    pygame.draw.circle(surface, cfg.ROCKET_WINDOW_COLOR, (x + 25, y), 8)

    # Flame (random length so it flickers)
    flame_length = random.randint(cfg.FLAME_MIN, cfg.FLAME_MAX)
    pygame.draw.polygon(surface, cfg.FLAME_COLOR, [
        (x, y - 20),
        (x, y + 20),
        (x - flame_length, y)
    ])


def draw_and_move_lasers(surface: pygame.Surface, lasers: List[Laser]) -> None:
    """Draw each laser and move it to the right."""
    for l in lasers:
        start = (l.x, l.y)
        end = (l.x + cfg.LASER_WIDTH, l.y)
        pygame.draw.line(surface, cfg.LASER_COLOR, start, end, cfg.LASER_THICKNESS)
        l.x += cfg.LASER_SPEED_X


def run_round() -> int:
    """Runs one round of the game. Returns the final score."""
    # --- Round state (variables that reset each round) ---
    lasers: List[Laser] = []
    ships: List[Ship] = [Ship(speed=cfg.FIRST_SHIP_SPEED, ship_pos=random.randint(100, cfg.HEIGHT - 100))]
    explosions: List[Explosion] = []

    ship_speed: int = cfg.FIRST_SHIP_SPEED
    own_y: int = cfg.PLAYER_START_Y
    score: int = 0

    # We pre-create fonts we need.
    score_font = pygame.font.SysFont(None, cfg.SCORE_FONT_SIZE)

    clock = pygame.time.Clock()
    running: bool = True
    spawn_new_ship: bool = False

    # --- Main loop ---
    while running:
        # 1) Handle quit + keyboard events (shooting, extra ship for debug)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Add a new laser that starts near the rocket nose
                    lasers.append(Laser(x=cfg.ROCKET_X + 50, y=own_y))
                elif event.key == pygame.key.key_code('r'):
                    # Debug key: spawn an extra enemy ship
                    ships.append(Ship())

        # 2) Read held-down keys (up/down to move)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and own_y > 50:
            own_y -= cfg.PLAYER_MOVE_STEP
        if keys[pygame.K_DOWN] and own_y < cfg.HEIGHT - 50:
            own_y += cfg.PLAYER_MOVE_STEP

        # 3) Spawn a new enemy ship if flagged
        if spawn_new_ship:
            ships.append(Ship(speed=ship_speed))
            spawn_new_ship = False

        # 4) DRAW everything (background → player → enemies → lasers → explosions → score)
        screen.fill((0, 0, 0))
        draw_star_field(screen)
        draw_player_rocket(screen, own_y)

        # Enemies
        for ship in ships[:]:
            ship.show_ship(screen=screen)
            if ship.ship_reached_end():
                # If an enemy reaches the left edge, the round ends
                running = False
                ships.remove(ship)

        # Lasers (draw + move)
        draw_and_move_lasers(screen, lasers)

        # If any laser goes off the right edge, trigger a big blast
        for l in lasers[:]:
            if l.x >= cfg.LASER_RIGHT_LIMIT:
                # Big "screen edge" explosion at laser.y
                explosions.append(Explosion(pos_x=l.x, pos_y=l.y))
                lasers.remove(l)

        # Laser vs enemy collision
        for l in lasers[:]:
            for ship in ships[:]:
                if abs(l.x - ship.ship_pos_x) < 40 and abs(l.y - ship.ship_pos_y) < 40:
                    explosions.append(Explosion(pos_x=l.x, pos_y=l.y))
                    ships.remove(ship)
                    lasers.remove(l)
                    spawn_new_ship = True
                    score += 1
                    if score % cfg.SPEED_UP_EVERY == 0:
                        ship_speed += 1

        # Explosions grow and then disappear
        for blast in explosions[:]:
            blast.draw_explosion(screen)
            if blast.circle_radius >= cfg.MAX_BLAST_RADIUS:
                explosions.remove(blast)

        # Score (top-right)
        score_text = score_font.render(f"Score: {score}", True, cfg.SCORE_COLOR)
        screen.blit(score_text, (cfg.WIDTH - 250, 20))

        pygame.display.flip()
        clock.tick(cfg.FPS)

    return score


def show_game_over(score: int) -> None:
    """Shows GAME OVER and waits for Enter to restart."""
    screen.fill((0, 0, 0))
    big_font = pygame.font.SysFont(None, cfg.GAME_OVER_FONT_SIZE)

    text1 = big_font.render("GAME OVER", True, (255, 0, 0))
    text2 = big_font.render(f"--Score: {score}--", True, (255, 0, 0))

    rect1 = text1.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 100))
    rect2 = text2.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 100))

    screen.blit(text1, rect1)
    screen.blit(text2, rect2)

    waiting = True
    while waiting:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False


def main() -> None:
    """Plays forever: run a round → show game over → repeat."""
    while True:
        score = run_round()
        show_game_over(score)


if __name__ == "__main__":
    main()
