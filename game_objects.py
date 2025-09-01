import pygame
import random
import numpy as np

class Ship:
    def __init__(self, ship_pos=None, speed=5):
        if ship_pos is None:
            ship_pos = random.randint(100, HEIGHT - 100)
        self.ship_pos_x = WIDTH + 50
        self.ship_pos_y = ship_pos
        self.speed = speed
        self.color = random.choice([(200, 50, 50), (50, 200, 200), (200, 200, 50)])

    def show_ship(self, screen):
        body_width = 60
        body_height = 30
        x = self.ship_pos_x
        y = self.ship_pos_y

        # --- Rectangle body ---
        pygame.draw.rect(screen, self.color, (x, y - body_height//2, body_width, body_height))

        # --- Cockpit (circle in middle of body) ---
        cockpit_radius = 8
        pygame.draw.circle(screen, (0, 150, 255), (x + body_width//2, y), cockpit_radius)

        # --- Side wings (triangles left + right) ---
        wing_color = (180, 0, 0)

        # Left wing triangle
        left_wing = [
            (x, y - body_height//2),      # top of body left
            (x, y + body_height//2),      # bottom of body left
            (x - 25, y)                   # point extending left
        ]
        pygame.draw.polygon(screen, wing_color, left_wing)

        # Right wing triangle
        right_wing = [
            (x + body_width, y - body_height//2),   # top right of body
            (x + body_width, y + body_height//2),   # bottom right of body
            (x + body_width + 25, y)                # point extending right
        ]
        pygame.draw.polygon(screen, wing_color, right_wing)

        # Move ship left
        self.ship_pos_x -= self.speed


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_radius = 120
        self.rings = []  # multiple staggered rings

        # Create 3–5 rings, each starting offset
        for i in range(random.randint(3, 5)):
            start_offset = random.randint(0, 15)
            self.rings.append({
                "radius": 5 + start_offset,
                "alpha": 255,
                "growth": random.randint(6, 10),   # fast growth
                "fade": random.randint(6, 10),     # fast fade
                "color": random.choice([
                    (255, 60, 0), 
                    (255, 140, 0), 
                    (255, 200, 0)
                ])
            })

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.alpha = 255
        self.growth = 12     # how fast the circle grows
        self.fade = 10       # how fast it fades
        self.max_radius = 120

        # pre-generate spike directions
        self.spikes = []
        for i in range(20):   # number of spikes
            angle = random.uniform(0, 2*np.pi)
            length = random.randint(30, 80)
            self.spikes.append((angle, length))

    def update(self):
        self.radius += self.growth
        self.alpha -= self.fade
        if self.radius > self.max_radius:
            self.alpha = 0

    def draw(self, screen):
        if self.alpha <= 0:
            return

        surf = pygame.Surface((self.max_radius*2, self.max_radius*2), pygame.SRCALPHA)

        # core explosion circle
        color = (255, 180, 0, max(0, self.alpha))
        pygame.draw.circle(
            surf, color, (self.max_radius, self.max_radius), self.radius
        )

        # spiky rays
        r, g, b, a = color
        for angle, length in self.spikes:
            end_x = self.max_radius + int(np.cos(angle) * (self.radius + length))
            end_y = self.max_radius + int(np.sin(angle) * (self.radius + length))
            pygame.draw.line(
                surf,
                (255, random.randint(100, 255), 0, max(0, self.alpha)),
                (self.max_radius, self.max_radius),
                (end_x, end_y),
                width=3
            )

        screen.blit(surf, (self.x - self.max_radius, self.y - self.max_radius))

    @property
    def done(self):
        return self.alpha <= 0
