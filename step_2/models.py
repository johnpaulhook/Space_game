# models.py
# Copyright (c) 2022-2025 IO-Swiss Aero GmbH. All rights reserved.
# Use of this source code is governed by the IO-Swiss Aero GmbH
# License, that can be found in the LICENSE.md file.

"""
Small, typed data containers used by the game.

This module intentionally keeps state objects minimal and explicit so that
gameplay code is easy to follow and unit test.

Conventions
-----------
- Coordinates use a screen-space Cartesian system:
  * x grows to the right (pixels)
  * y grows downward (pixels)
- All numeric fields are integers unless noted otherwise.
"""

from dataclasses import dataclass


@dataclass
class Laser:
    """A single laser shot emitted by the player's rocket.

    The laser's position represents the *front/leading point* of the beam that
    moves horizontally to the right each frame. Rendering code is expected to
    draw the beam relative to this tip (e.g., as a short rectangle or line
    segment extending backward from (x, y)).

    Args:
        x (int): Current horizontal position in pixels.
                 Increases as the laser travels to the right.
        y (int): Current vertical position in pixels (top of screen is 0).
                 Typically matches the rocket's muzzle height at fire time.

    Notes:
        - Collision systems can treat (x, y) as either the beam tip or the
          beam's bounding box center, depending on how you render lasers.
          Keep that consistent across render and collide code.
        - Lifespan is usually enforced by a right-edge limit in settings
          (see LASER_RIGHT_LIMIT) to avoid tracking off-screen shots.
    """
    x: int
    y: int
