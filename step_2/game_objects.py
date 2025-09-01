import pygame
import random

class Ship:
    def __init__(self, ship_pos=None, speed=5):
        # If no position given, choose random between 250–850
        if ship_pos is None:
            ship_pos = random.randint(250, 850)

        self.ship_pos_x = 1800   # start off right edge
        self.ship_pos_y = ship_pos
        self.speed = speed

        # 🎨 Random color
        self.color = (
            random.randint(100, 255),  # R
            random.randint(50, 200),   # G
            random.randint(50, 255)    # B
        )

        # 📏 Random size (scale factor)
        self.size = random.randint(15, 30)  # body height
        self.width = self.size * 3          # body width

    def ship_reached_end(self):
        return self.ship_pos_x <= 0

    def show_ship(self, screen):
        half_h = self.size // 2
        half_w = self.width // 2

        # Body (rectangle)
        body = pygame.Rect(self.ship_pos_x - half_w, self.ship_pos_y - half_h,
                           self.width, self.size)
        pygame.draw.rect(screen, self.color, body)

        # Left wing
        pygame.draw.polygon(screen, self.color, [
            (self.ship_pos_x - half_w, self.ship_pos_y - half_h),
            (self.ship_pos_x - half_w - 20, self.ship_pos_y),
            (self.ship_pos_x - half_w, self.ship_pos_y + half_h)
        ])

        # Right wing
        pygame.draw.polygon(screen, self.color, [
            (self.ship_pos_x + half_w, self.ship_pos_y - half_h),
            (self.ship_pos_x + half_w + 20, self.ship_pos_y),
            (self.ship_pos_x + half_w, self.ship_pos_y + half_h)
        ])

        # Cockpit
        pygame.draw.circle(screen, (0, 100, 255), (self.ship_pos_x, self.ship_pos_y),
                           self.size // 3)

        # Move ship left each frame
        self.ship_pos_x -= self.speed

class Explosion:
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.circle_radius = 30
    
    def draw_explosion(self, screen):
        pygame.draw.circle(surface=screen, color=(255,0,0), center=(self.pos_x, self.pos_y), radius=self.circle_radius)
        self.circle_radius += 30