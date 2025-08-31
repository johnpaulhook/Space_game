import pygame
import random
import sys
import numpy as np
import os
from game_objects import Ship, Explosion   # your custom ship + explosion class

# File to save high scores
SCORES_FILE = "scores.txt"

# Screen dimensions
WIDTH = 1900
HEIGHT = 1000


# ---------------- SCORE HANDLING ---------------- #

def save_score(score, initials):
    """Save the player's score with initials into a file."""
    with open(SCORES_FILE, "a") as f:
        f.write(f"{score},{initials}\n")  # Format: 120,ABC


def load_top_scores(limit=3):
    """Load scores from file and return top N as list of (score, initials)."""
    if not os.path.exists(SCORES_FILE):
        return []
    
    with open(SCORES_FILE, "r") as f:
        lines = f.readlines()
    
    scores = []
    for line in lines:
        try:
            s, initials = line.strip().split(",", 1)
            scores.append((int(s), initials))  # turn into tuple (score, initials)
        except:
            continue
    
    # Sort scores highest → lowest
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:limit]


# ---------------- INITIALS INPUT ---------------- #

def get_initials(screen):
    """Ask the player to type 1–3 initials before game starts."""
    initials = ""
    entering = True
    font_big = pygame.font.SysFont(None, 100)
    font_small = pygame.font.SysFont(None, 50)

    while entering:
        screen.fill((0, 0, 0))

        # Instructions
        text = font_big.render("Enter Your Initials:", True, (255, 255, 0))
        screen.blit(text, (WIDTH//2 - 300, HEIGHT//2 - 100))

        # Display what player typed so far
        text2 = font_big.render(initials, True, (0, 255, 0))
        screen.blit(text2, (WIDTH//2 - 100, HEIGHT//2 + 20))

        # Small instructions
        hint = font_small.render("Press ENTER when done (max 3 letters)", True, (200, 200, 200))
        screen.blit(hint, (WIDTH//2 - 250, HEIGHT//2 + 150))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and initials:
                    entering = False
                elif event.key == pygame.K_BACKSPACE:
                    initials = initials[:-1]
                elif len(initials) < 3 and event.unicode.isalpha():
                    initials += event.unicode.upper()

    return initials


# ---------------- GAME LOOP ---------------- #

def run_game(screen):
    """Run one round of the game and return the score."""

    # Player ship position (on the left)
    own_ship_pos = HEIGHT // 2

    # Difficulty settings
    ship_speed = 5
    max_ships = 2
    spawn_new_ship = False

    # Start with 2 enemy ships
    ships = []
    for _ in range(2):
        ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
        ship.ship_pos_x = WIDTH + random.randint(50, 300)  # spawn off-screen to the right
        ships.append(ship)

    # Game state variables
    # create stars once
    lasers = []
    explosions = []
    score = 0
    running = True
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 55)

    while running:
        screen.fill((0, 0, 0))

        # --------- Event handling --------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Fire laser (starts at player ship's nose)
                    lasers.append([100, own_ship_pos])

        # Player movement (W/S or arrow keys)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            own_ship_pos -= 7
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            own_ship_pos += 7
        own_ship_pos = np.clip(own_ship_pos, 50, HEIGHT - 50)

        # --------- Spawn new ship if needed --------- #
        if spawn_new_ship and len(ships) < max_ships:
            ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
            ship.ship_pos_x = WIDTH + random.randint(50, 300)
            ships.append(ship)
            spawn_new_ship = False

        # --------- Update ships --------- #
        for ship in ships:
            ship.update(screen)  # assuming your Ship class has update() to move & draw

        # --------- Update lasers --------- #
        for laser in lasers[:]:  # copy to safely remove
            pygame.draw.line(screen, (255, 0, 0), (laser[0], laser[1]), (laser[0] + 40, laser[1]), 8)
            laser[0] += 15

            # Remove if off-screen
            if laser[0] >= WIDTH:
                lasers.remove(laser)
                continue

            # Collision check with enemy ships
            for ship in ships[:]:
                if np.abs(laser[0] - ship.ship_pos_x) < 40 and np.abs(laser[1] - ship.ship_pos_y) < 40:
                    explosions.append(Explosion(pos_x=laser[0], pos_y=laser[1]))
                    ships.remove(ship)
                    if laser in lasers:
                        lasers.remove(laser)
                    spawn_new_ship = True
                    score += 1

                    # Difficulty scaling
                    if score % 3 == 0:   # every 3 kills → ships faster
                        ship_speed += 1
                    if score % 10 == 0:  # every 10 kills → add new ship slot
                        max_ships += 1

        # --------- Draw explosions --------- #
        for exp in explosions[:]:
            if not exp.update(screen):
                explosions.remove(exp)

        # --------- Draw player ship --------- #
        pygame.draw.polygon(screen, (0, 255, 0), [(50, own_ship_pos), (100, own_ship_pos - 25), (100, own_ship_pos + 25)])

        # --------- Draw score --------- #
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (WIDTH - 250, 20))

        pygame.display.flip()
        clock.tick(60)

    return score


# ---------------- MAIN LOOP ---------------- #

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Game with Initials")

    font_big = pygame.font.SysFont(None, 100)
    font_small = pygame.font.SysFont(None, 55)

    while True:
        # Get player initials before starting
        initials = get_initials(screen)

        # Run one game round
        score = run_game(screen)

        # Save score
        save_score(score, initials)

        # Load top scores
        top_scores = load_top_scores()

        # --------- Game Over Screen --------- #
        showing = True
        while showing:
            screen.fill((0, 0, 0))

            text = font_big.render("GAME OVER", True, (255, 0, 0))
            screen.blit(text, (WIDTH//2 - 200, HEIGHT//2 - 150))

            score_text = font_small.render(f"Your Score: {score} ({initials})", True, (255, 255, 0))
            screen.blit(score_text, (WIDTH//2 - 200, HEIGHT//2 - 50))

            # Top scores list
            top_text = font_small.render("Top Scores:", True, (0, 255, 0))
            screen.blit(top_text, (WIDTH//2 - 200, HEIGHT//2 + 20))

            for i, (s, ini) in enumerate(top_scores, start=1):
                entry = font_small.render(f"{i}. {s} ({ini})", True, (0, 200, 200))
                screen.blit(entry, (WIDTH//2 - 200, HEIGHT//2 + 60 + i * 40))

            # Instruction to restart
            restart_text = font_small.render("Press ENTER to Play Again or Q to Quit", True, (200, 200, 200))
            screen.blit(restart_text, (WIDTH//2 - 300, HEIGHT//2 + 250))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        showing = False  # restart loop
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()


if __name__ == "__main__":
    main()