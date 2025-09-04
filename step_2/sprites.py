# Copyright (c) 2022-2025 IO-Swiss Aero GmbH. All rights reserved.
# Use of this source code is governed by the IO-Swiss Aero GmbH
# License, that can be found in the LICENSE.md file.

"""
sprites.py
Sprite-like classes that encapsulate state, drawing, and per-frame updates.

This module keeps *behavior with the thing that owns it*:
- Player handles input, movement, rendering, and shooting.
- Enemy moves left, knows when it exits the screen, and renders itself.
- Explosion grows then disappears, and renders itself each frame.

Design notes
------------
- No global state. All state lives on objects.
- No pygame init here; callers are responsible for pygame setup.
- Screen-space coordinates:
  * x grows to the right (pixels)
  * y grows downward (pixels)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

import settings as cfg
from models import Laser


class Player:
    """The player rocket: position, input, drawing, and shooting.

    The player moves vertically around a fixed x-position (cfg.ROCKET_X).
    Shooting returns a new `Laser` instance that the caller manages.

    Attributes:
        x (int): Fixed horizontal position in pixels.
        y (int): Current vertical position in pixels.

    """

    __slots__ = ("x", "y")

    def __init__(self, x: int = cfg.ROCKET_X, y: int = cfg.PLAYER_START_Y) -> None:
        """Initialize the player at a given position.

        Args:
            x (int): Horizontal position in pixels. Defaults to cfg.ROCKET_X.
            y (int): Vertical position in pixels. Defaults to cfg.PLAYER_START_Y.
        """
        self.x = x
        self.y = y

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Apply continuous input (held keys) to the player's position.

        Args:
            keys: Result of pygame.key.get_pressed().

        Notes:
            - Movement is clamped to stay within the screen.
            - Uses cfg.PLAYER_MOVE_STEP for step size.
        """
        if keys[pygame.K_UP]:
            self.y = max(50, self.y - cfg.PLAYER_MOVE_STEP)
        if keys[pygame.K_DOWN]:
            self.y = min(cfg.HEIGHT - 50, self.y + cfg.PLAYER_MOVE_STEP)

    def shoot(self) -> Laser:
        """Create a new laser originating at the rocket's nose.

        Returns:
            Laser: A laser positioned slightly ahead of the rocket body.
        """
        return Laser(x=self.x + 50, y=self.y)

    def draw(self, surface: pygame.Surface) -> None:
        """Render the player rocket.

        Args:
            surface (pygame.Surface): Target drawing surface.
        """
        x, y = self.x, self.y

        # Body
        pygame.draw.rect(surface, cfg.ROCKET_BODY_COLOR, (x, y - 20, 50, 40))

        # Nose cone (triangle)
        pygame.draw.polygon(surface, cfg.ROCKET_NOSE_COLOR, [
            (x + 50, y - 20),
            (x + 50, y + 20),
            (x + 70, y),
        ])

        # Fins (triangles)
        pygame.draw.polygon(surface, cfg.ROCKET_NOSE_COLOR, [
            (x, y - 20),
            (x - 15, y - 30),
            (x, y - 30),
        ])
        pygame.draw.polygon(surface, cfg.ROCKET_NOSE_COLOR, [
            (x, y + 20),
            (x - 15, y + 30),
            (x, y + 30),
        ])

        # Window
        pygame.draw.circle(surface, cfg.ROCKET_WINDOW_COLOR, (x + 25, y), 8)

        # Flame (simple flicker)
        # Keep the random here if you prefer variation; otherwise a fixed MIN looks clean.
        flame_len = cfg.FLAME_MIN
        pygame.draw.polygon(surface, cfg.FLAME_COLOR, [
            (x, y - 20),
            (x, y + 20),
            (x - flame_len, y),
        ])

    @property
    def bbox(self) -> pygame.Rect:
        """Approximate bounding box for collisions.

        Returns:
            pygame.Rect: Rectangle approximating the rocket body.
        """
        # Matches draw rect above (x, y - 20, 50, 40), slightly padded.
        return pygame.Rect(self.x, self.y - 22, 52, 44)


class Enemy:
    """A basic enemy that moves left at a constant speed.

    Attributes:
        x (int): Current x-position in pixels.
        y (int): Current y-position in pixels.
        speed (int): Horizontal speed in pixels per frame (leftwards).
    """

    __slots__ = ("x", "y", "speed")

    def __init__(self, y: Optional[int] = None, speed: int = cfg.FIRST_SHIP_SPEED) -> None:
        """Initialize the enemy.

        Args:
            y (Optional[int]): Vertical spawn position in pixels. If None, mid-screen.
            speed (int): Horizontal speed (px/frame). Defaults to cfg.FIRST_SHIP_SPEED.
        """
        self.x = cfg.WIDTH - 100  # start near the right edge
        self.y = int(y if y is not None else cfg.HEIGHT * 0.5)
        self.speed = speed

    def update(self) -> None:
        """Advance the enemy left by its speed."""
        self.x -= self.speed

    def reached_end(self) -> bool:
        """Check if the enemy has left the screen at the left edge.

        Returns:
            bool: True if the enemy moved past x <= -50.
        """
        return self.x <= -50

    def draw(self, surface: pygame.Surface) -> None:
        """Render the enemy.

        Args:
            surface (pygame.Surface): Target drawing surface.
        """
        # Simple saucer: body + dome
        body_rect = pygame.Rect(self.x - 30, self.y - 10, 60, 20)
        pygame.draw.ellipse(surface, (180, 180, 180), body_rect)
        dome_rect = pygame.Rect(self.x - 15, self.y - 22, 30, 20)
        pygame.draw.ellipse(surface, (120, 170, 220), dome_rect)

    @property
    def bbox(self) -> pygame.Rect:
        """Bounding box used for coarse collision checks.

        Returns:
            pygame.Rect: Rectangle covering the saucer.
        """
        return pygame.Rect(self.x - 30, self.y - 20, 60, 40)


class Explosion:
    """Expanding circle that fades out when it reaches a max radius."""

    __slots__ = ("x", "y", "radius", "max_radius")

    def __init__(self, x: int, y: int, max_radius: int = cfg.MAX_BLAST_RADIUS) -> None:
        """Initialize an explosion at a position.

        Args:
            x (int): Horizontal center of the explosion.
            y (int): Vertical center of the explosion.
            max_radius (int): Maximum radius at which the explosion ends.
        """
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = max_radius

    def update(self) -> None:
        """Grow the explosion by a fixed amount per frame."""
        # You can tweak growth speed if desired.
        self.radius += 10

    def done(self) -> bool:
        """Whether the explosion has reached its maximum size.

        Returns:
            bool: True if the animation should be removed.
        """
        return self.radius >= self.max_radius

    def draw(self, surface: pygame.Surface) -> None:
        """Render the explosion as two expanding circles.

        Args:
            surface (pygame.Surface): Target drawing surface.
        """
        if self.radius <= 0:
            return
        # Outer ring
        pygame.draw.circle(surface, (255, 120, 60), (self.x, self.y), self.radius, width=4)
        # Inner core
        inner = max(0, self.radius // 3)
        if inner > 0:
            pygame.draw.circle(surface, (255, 200, 120), (self.x, self.y), inner, width=0)
