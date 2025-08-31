import pygame
import random
import sys
import numpy as np
import datetime
import os
from game_objects import Ship, Explosion  # your Ship + Explosion classes

# ------------------ CONFIG ------------------ #
WIDTH = 1900
HEIGHT = 1000
FPS = 60
SCORES_FILE = "scores.txt"

# ------------------ SAVE SCORE ------------------ #
def save_score(score, initials):
    """Save score with initials + timestamp to file"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(SCORES_FILE, "a") as f:
        f.write(f"{initials},{score},{now}\n")

# ------------------ GAME LOOP ------------------ #
def run_game(screen):
    clock = pygame.time.Clock()

    # Player setup
    own_ship_pos = HEIGHT // 2
    lasers = []
    explosions = []

    # Enemy ships
    ship_speed = 5
    max_ships = 2
    ships = []
    for _ in range(2):  # start with 2
        ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
        ship.ship_pos_x = WIDTH + random.randint(50, 300)
        ships.append(ship)

    # Game state
    running = True
    score = 0
    spawn_new_ship = False

    while running:
        clock.tick(FPS)
        screen.fill((0, 0, 0))  # clear screen

        # --------- Events --------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:  # fire laser
                    lasers.append([50, own_ship_pos])  # [x, y]

        # --------- Movement --------- #
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and own_ship_pos > 50:
            own_ship_pos -= 8
        if keys[pygame.K_DOWN] and own_ship_pos < HEIGHT - 50:
            own_ship_pos += 8

        # --------- Draw player --------- #
        pygame.draw.polygon(
            screen,
            (0, 255, 0),
            [(50, own_ship_pos), (20, own_ship_pos - 20), (20, own_ship_pos + 20)],
        )

        # --------- Update ships --------- #
        for ship in ships[:]:
            ship.update(screen)
            if ship.ship_pos_x < -50:  # went off screen
                ships.remove(ship)
                spawn_new_ship = True

        # --------- Update lasers --------- #
        for laser in lasers[:]:
            pygame.draw.line(screen, (255, 0, 0), (laser[0], laser[1]), (laser[0] + 40, laser[1]), 4)
            laser[0] += 12
            if laser[0] > WIDTH:
                lasers.remove(laser)

        # --------- Collisions --------- #
        for laser in lasers[:]:
            for ship in ships[:]:
                if np.abs(laser[0] - ship.ship_pos_x) < 40 and np.abs(laser[1] - ship.ship_pos_y) < 40:
                    explosions.append(Explosion(pos_x=laser[0], pos_y=laser[1]))
                    ships.remove(ship)
                    lasers.remove(laser)
                    score += 1
                    spawn_new_ship = True
                    break

        # --------- Spawn new ships --------- #
        if spawn_new_ship and len(ships) < max_ships:
            ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
            ship.ship_pos_x = WIDTH + random.randint(50, 300)
            ships.append(ship)
            spawn_new_ship = False

        # --------- Explosions --------- #
        for explosion in explosions[:]:
            if not explosion.update(screen):
                explosions.remove(explosion)

        # --------- Difficulty scaling --------- #
        if score > 0 and score % 3 == 0:
            ship_speed = 5 + score // 3
        if score > 0 and score % 10 == 0:
            max_ships = 2 + score // 10

        # --------- Draw score --------- #
        font = pygame.font.SysFont(None, 40)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))

        pygame.display.flip()

    return score

# ------------------ MAIN ------------------ #
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Game")

    score = run_game(screen)

    # After game ends → ask initials
    initials = ""
    asking = True
    font = pygame.font.SysFont(None, 60)

    while asking:
        screen.fill((0, 0, 0))
        text = font.render("Enter your initials (3 letters): " + initials, True, (255, 255, 255))
        screen.blit(text, (200, HEIGHT // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                asking = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(initials) > 0:
                    save_score(score, initials)
                    asking = False
                elif event.key == pygame.K_BACKSPACE:
                    initials = initials[:-1]
                elif len(initials) < 3 and event.unicode.isalpha():
                    initials += event.unicode.upper()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
