# Copyright (c) 2022-2025 IO-Swiss Aero GmbH. All rights reserved.
# Use of this source code is governed by the IO-Swiss Aero GmbH
# License, that can be found in the LICENSE.md file.

"""
ui.py
Minimal UI helpers for HUD (score) and game-over screen.

No pygame initialization occurs here. Callers must ensure pygame.init() and
pygame.font.init() (or SysFont calls) are made before using functions below.
"""

from __future__ import annotations

from typing import Optional, Tuple

import pygame

import settings as cfg


def draw_score(surface: pygame.Surface, score: int, font: Optional[pygame.font.Font] = None) -> None:
    """Draw the current score in the top-right corner.

    Args:
        surface (pygame.Surface): Target drawing surface.
        score (int): Current score value to display.
        font (Optional[pygame.font.Font]): Pre-created font. If None, a default
            font is created using cfg.SCORE_FONT_SIZE.

    Notes:
        - Creating fonts each frame is more expensive; prefer passing a cached font.
        - Color is taken from cfg.SCORE_COLOR.
    """
    if font is None:
        # Lazy-create a font if the caller didn't supply one.
        if not pygame.font.get_init():
            pygame.font.init()
        font = pygame.font.SysFont(None, cfg.SCORE_FONT_SIZE)

    text = font.render(f"Score: {score}", True, cfg.SCORE_COLOR)
    rect = text.get_rect()
    rect.top = 20
    rect.right = cfg.WIDTH - 20
    surface.blit(text, rect)


def show_game_over_blocking(surface: pygame.Surface, score: int) -> None:
    """Blocking 'Game Over' screen that waits for Enter to continue.

    Args:
        surface (pygame.Surface): Target drawing surface (already created).
        score (int): Final score to display.

    Behavior:
        - Renders "GAME OVER" and the score using cfg.GAME_OVER_FONT_SIZE.
        - Waits until the user presses Enter (Return) or closes the window.
        - Does not modify global state; caller decides what happens next.

    Raises:
        SystemExit: If the user closes the window (pygame.QUIT).
    """
    if not pygame.font.get_init():
        pygame.font.init()

    big_font = pygame.font.SysFont(None, cfg.GAME_OVER_FONT_SIZE)

    text1 = big_font.render("GAME OVER", True, (255, 0, 0))
    text2 = big_font.render(f"--Score: {score}--", True, (255, 0, 0))

    rect1 = text1.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 100))
    rect2 = text2.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 100))

    waiting = True
    clock = pygame.time.Clock()

    while waiting:
        surface.fill((0, 0, 0))
        surface.blit(text1, rect1)
        surface.blit(text2, rect2)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Let the caller decide whether to catch this.
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

        clock.tick(60)
