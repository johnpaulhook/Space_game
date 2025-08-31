import pygame
import random
import sys
import numpy as np
import os
from game_objects import Ship, Explosion   # Import custom Ship + Explosion classes

# File to save high scores
SCORES_FILE = "scores.txt"

# Screen dimensions
WIDTH = 1900
HEIGHT = 1000
FPS = 60   # frames per second cap


# ---------------- SCORE HANDLING ---------------- #

def save_score(score, initials):
    """Save the player's score with initials into a file."""
    # Open file in append mode, add score + initials
    with open(SCORES_FILE, "a") as f:
        f.write(f"{score},{initials}\n")  # Example: "120,ABC"


def load_top_scores(limit=3):
    """Load scores from file and return top N as list of (score, initials)."""
    if not os.path.exists(SCORES_FILE):
        return []   # No scores yet
    
    # Read scores file
    with open(SCORES_FILE, "r") as f:
        lines = f.readlines()
    
    scores = []
    for line in lines:
        try:
            s, initials = line.strip().split(",", 1)
            scores.append((int(s), initials))  # Turn into tuple (score, initials)
        except:
            continue   # Skip bad lines
    
    # Sort scores highest → lowest
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:limit]   # Only return top `limit` scores


# ---------------- INITIALS INPUT ---------------- #

def get_initials(screen):
    """Ask the player to type 1–3 initials before game starts."""
    initials = ""    # Stores player input
    entering = True
    font_big = pygame.font.SysFont(None, 100)
    font_small = pygame.font.SysFont(None, 50)

    # Loop until player presses Enter
    while entering:
        screen.fill((0, 0, 0))

        # Instructions text
        text = font_big.render("Enter Your Initials:", True, (255, 255, 0))
        screen.blit(text, (WIDTH//2 - 300, HEIGHT//2 - 100))

        # Display typed initials
        text2 = font_big.render(initials, True, (0, 255, 0))
        screen.blit(text2, (WIDTH//2 - 100, HEIGHT//2 + 20))

        # Hint text
        hint = font_small.render("Press ENTER when done (max 3 letters)", True, (200, 200, 200))
        screen.blit(hint, (WIDTH//2 - 250, HEIGHT//2 + 150))

        pygame.display.flip()

        # Handle key input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # Window closed
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and initials:
                    entering = False   # Done entering initials
                elif event.key == pygame.K_BACKSPACE:
                    initials = initials[:-1]   # Remove last character
                elif len(initials) < 3 and event.unicode.isalpha():
                    initials += event.unicode.upper()   # Add letter

    return initials   # Return player initials


# ---------------- GAME LOOP ---------------- #

def run_game(screen):
    # Player’s ship position
    own_ship_pos = HEIGHT // 2
    ship_speed = 5         # Speed of enemy ships
    max_ships = 200          # Start with 2 enemy ships max
    spawn_new_ship = False # Flag to add new ship after one destroyed

    # Create starting ships
    ships = []
    for _ in range(2):
        ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
        ship.ship_pos_x = WIDTH + random.randint(50, 300)   # Spawn offscreen
        ships.append(ship)
    # Lists for lasers and explosions
    lasers = []
    explosions = []
    # Generate background stars (random positions)
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(200)]
    PLAYER_SPEED = 10
    LASER_SPEED = 50
    score = 0
    running = True
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 55)

    # -------- Main game loop -------- #
    while running:
        screen.fill((0, 0, 0))

        # --------- Handle events --------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                lasers.append([100, own_ship_pos])

        # ✅ Get keyboard state every frame
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            own_ship_pos -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            own_ship_pos += PLAYER_SPEED


        # --------- Background stars --------- #
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 2)  # Draw star
            star[0] -= 2   # Move left
            if star[0] < 0:   # Wrap star back to right side
                star[0] = WIDTH
                star[1] = random.randint(0, HEIGHT)

        # --------- Spawn new ship if needed --------- #
        if spawn_new_ship and len(ships) < max_ships:
            ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
            ship.ship_pos_x = WIDTH + random.randint(50, 300)
            ships.append(ship)
            spawn_new_ship = False

        # --------- Update ships --------- #
        for ship in ships[:]:
            ship.show_ship(screen)   # Draw enemy ship

            # 🚨 GAME OVER if ship passes player
            if ship.ship_pos_x < 0:
                running = False   # End game loop

        # --------- Update lasers --------- #
        for laser in lasers[:]:
            # Draw laser (two lines for glowing effect)
            pygame.draw.line(screen, (255, 0, 0), (laser[0], laser[1]), (laser[0] + 60, laser[1]), 10)
            pygame.draw.line(screen, (255, 255, 0), (laser[0], laser[1]), (laser[0] + 60, laser[1]), 4)
            laser[0] += LASER_SPEED

            if laser[0] >= WIDTH:
                lasers.remove(laser)   # Remove offscreen lasers
                continue

            # Collision detection with ships
            for ship in ships[:]:
                if np.abs(laser[0] - ship.ship_pos_x) < 40 and np.abs(laser[1] - ship.ship_pos_y) < 40:
                    explosions.append(Explosion(laser[0], laser[1]))  # Explosion at hit
                    ships.remove(ship)     # Destroy ship
                    if laser in lasers:
                        lasers.remove(laser)
                    spawn_new_ship = True  # Flag to spawn replacement
                    score += 1             # Increase score

                    # Difficulty scaling
                    if score % 3 == 0:
                        ship_speed += 1    # Speed up enemy ships
                    if score % 10 == 0:
                        max_ships += 1     # Raise the limit
                        # Immediately spawn a new ship if under limit
                        if len(ships) < max_ships:
                            new_ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
                            new_ship.ship_pos_x = WIDTH + random.randint(50, 300)
                            ships.append(new_ship)
                        # More ships allowed

        # --------- Update explosions --------- #
        for exp in explosions[:]:
            exp.draw_explosion(screen)
            if exp.circle_radius > 200:   # Remove after expansion
                explosions.remove(exp)

 # --- Draw Player Rocket ---
        rocket_x = 50
        rocket_y = own_ship_pos

        # Rocket body (rectangle)
        pygame.draw.rect(screen, (200, 200, 255), (rocket_x, rocket_y - 20, 50, 40))
        # Nose cone (triangle)
        pygame.draw.polygon(screen, (180, 0, 0), [
            (rocket_x + 50, rocket_y - 20),
            (rocket_x + 50, rocket_y + 20),
            (rocket_x + 70, rocket_y)
        ])
        # Top fin
        pygame.draw.polygon(screen, (180, 0, 0), [
            (rocket_x, rocket_y - 20),
            (rocket_x - 15, rocket_y - 30),
            (rocket_x, rocket_y - 30)
        ])
        # Bottom fin
        pygame.draw.polygon(screen, (180, 0, 0), [
            (rocket_x, rocket_y + 20),
            (rocket_x - 15, rocket_y + 30),
            (rocket_x, rocket_y + 30)
        ])
        # Window (circle)
        pygame.draw.circle(screen, (0, 150, 255), (rocket_x + 25, rocket_y), 8)
        # Rocket flame (random size so it flickers)
        flame_length = random.randint(15, 30)
        pygame.draw.polygon(screen, (255, 140, 0), [
            (rocket_x, rocket_y - 20),
            (rocket_x, rocket_y + 20),
            (rocket_x - flame_length, rocket_y)
        ])

        # --------- Draw Score --------- #
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (WIDTH - 250, 20))

        pygame.display.flip()
        clock.tick(FPS)   # Limit to FPS

    return score   # Return final score when game ends


# ---------------- MAIN LOOP ---------------- #

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Game with Initials")

    font_big = pygame.font.SysFont(None, 100)
    font_small = pygame.font.SysFont(None, 55)

    while True:   # Infinite loop until quit
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

            # Big GAME OVER text
            text = font_big.render("GAME OVER", True, (255, 0, 0))
            screen.blit(text, (WIDTH//2 - 200, HEIGHT//2 - 150))

            # Show player score
            score_text = font_small.render(f"Your Score: {score} ({initials})", True, (255, 255, 0))
            screen.blit(score_text, (WIDTH//2 - 200, HEIGHT//2 - 50))

            # Top scores list
            top_text = font_small.render("Top Scores:", True, (0, 255, 0))
            screen.blit(top_text, (WIDTH//2 - 200, HEIGHT//2 + 20))

            # Print high scores
            for i, (s, ini) in enumerate(top_scores, start=1):
                entry = font_small.render(f"{i}. {s} ({ini})", True, (0, 200, 200))
                screen.blit(entry, (WIDTH//2 - 200, HEIGHT//2 + 60 + i * 40))

            # Restart or quit instructions
            restart_text = font_small.render("Press ENTER to Play Again or Q to Quit", True, (200, 200, 200))
            screen.blit(restart_text, (WIDTH//2 - 300, HEIGHT//2 + 250))

            pygame.display.flip()

            # Handle restart/quit input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:   # Window closed
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        showing = False  # Restart game
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()


if __name__ == "__main__":
    main()