"""
models.py
Small, typed data containers that are easy to understand.
"""

from dataclasses import dataclass

@dataclass
class Laser:
    """A laser beam shot by the player.

    x: current horizontal position
    y: current vertical position
    """
    x: int
    y: int
