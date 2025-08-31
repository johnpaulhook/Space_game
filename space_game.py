# ------------------- IMPORTS ------------------- #
import pygame                # Main game library for graphics, input, and sound
import random                # For randomness (spawn positions, flame flicker, etc.)
import sys                   # For system exit
import numpy as np           # For math (collision detection uses abs)
import os                    # To check if score file exists
from game_objects import Ship, Explosion   # Import custom Ship + Explosion classes

# ------------------- SETTINGS ------------------- #
SCORES_FILE = "scores.txt"   # File to save scores
WIDTH = 1900                 # Screen width
HEIGHT = 1000                # Screen height
FPS = 60                     # Frames per second (game speed cap)


# ---------------- SCORE HANDLING ---------------- #

def save_score(score, initials):
    """Save the player's score with initials into a file."""
    with open(SCORES_FILE, "a") as f:              # Open scores file in append mode
        f.write(f"{score},{initials}\n")           # Save score + initials (CSV style)


def load_top_scores(limit=3):
    """Load scores from file and return top N as list of (score, initials)."""
    if not os.path.exists(SCORES_FILE):            # If no file yet → return empty
        return []
    
    with open(SCORES_FILE, "r") as f:              # Open file for reading
        lines = f.readlines()                      # Read all lines
    
    scores = []                                    # List to store (score, initials)
    for line in lines:
        try:
            s, initials = line.strip().split(",", 1)   # Split "score,initials"
            scores.append((int(s), initials))          # Store as tuple
        except:
            continue                                   # Skip broken lines
    
    scores.sort(key=lambda x: x[0], reverse=True)  # Sort highest → lowest
    return scores[:limit]                          # Return only top `limit`


# ---------------- INITIALS INPUT ---------------- #

def get_initials(screen):
    """Ask the player to type 1–3 initials before game starts."""
    initials = ""                                    # Stores player input
    entering = True                                  # Loop until Enter pressed
    font_big = pygame.font.SysFont(None, 100)        # Big font
    font_small = pygame.font.SysFont(None, 50)       # Smaller font

    while entering:                                  # Keep looping until Enter
        screen.fill((0, 0, 0))                       # Clear screen (black)

        text = font_big.render("Enter Your Initials:", True, (255, 255, 0))  # Yellow text
        screen.blit(text, (WIDTH//2 - 300, HEIGHT//2 - 100))                 # Draw text

        text2 = font_big.render(initials, True, (0, 255, 0))  # Show current initials (green)
        screen.blit(text2, (WIDTH//2 - 100, HEIGHT//2 + 20))

        hint = font_small.render("Press ENTER when done (max 3 letters)", True, (200, 200, 200))
        screen.blit(hint, (WIDTH//2 - 250, HEIGHT//2 + 150))

        pygame.display.flip()                         # Update screen

        # Handle keyboard events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:             # Window closed
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:          # Key pressed
                if event.key == pygame.K_RETURN and initials:  # Enter → done
                    entering = False
                elif event.key == pygame.K_BACKSPACE: # Backspace → remove letter
                    initials = initials[:-1]
                elif len(initials) < 3 and event.unicode.isalpha():  # Add letter
                    initials += event.unicode.upper()

    return initials   # Return entered initials


# ---------------- GAME LOOP ---------------- #

def run_game(screen):
    own_ship_pos = HEIGHT // 2       # Player ship vertical position (middle of screen)
    ship_speed = 5                   # Starting enemy ship speed
    max_ships = 200                  # Max ships allowed
    spawn_new_ship = False           # Flag to add a new ship when one is destroyed

    ships = []                       # List of enemy ships
    for _ in range(2):               # Start with 2 ships
        ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
        ship.ship_pos_x = WIDTH + random.randint(50, 300)   # Spawn just offscreen
        ships.append(ship)

    lasers = []                      # List of lasers
    explosions = []                  # List of explosions
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(200)]  # Background stars
    PLAYER_SPEED = 10                # Player movement speed
    LASER_SPEED = 50                 # Laser speed
    score = 0                        # Player score
    running = True                   # Game loop flag
    clock = pygame.time.Clock()      # FPS timer
    font = pygame.font.SysFont(None, 55)  # Font for score text
    last_speed_increase = 0          # To avoid double-triggering difficulty scaling

    # -------- GAME LOOP STRUCTURE (FLOWCHART) -------- #
    # 
    #  ┌───────────────┐
    #  │   Start Game  │
    #  └───────┬───────┘
    #          │
    #  ┌───────▼────────┐
    #  │ Handle Input   │ (move, shoot, quit)
    #  └───────┬────────┘
    #          │
    #  ┌───────▼────────┐
    #  │ Update Objects │ (stars, ships, lasers)
    #  └───────┬────────┘
    #          │
    #  ┌───────▼────────┐
    #  │ Check Collisions│ (lasers vs ships)
    #  └───────┬────────┘
    #          │
    #  ┌───────▼────────┐
    #  │ Draw Everything│ (rocket, score, etc.)
    #  └───────┬────────┘
    #          │
    #  ┌───────▼────────┐
    #  │  Check Game Over│
    #  └───────┬────────┘
    #          │
    #       Repeat
    #
    # ------------------------------------------- #

    while running:
        screen.fill((0, 0, 0))       # Clear screen (black)

        # -------- Event handling -------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # Window closed
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # Space = shoot
                lasers.append([100, own_ship_pos])   # Add new laser from ship

        keys = pygame.key.get_pressed()     # Get current key states
        if keys[pygame.K_UP] or keys[pygame.K_w]:    # Move up
            own_ship_pos -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  # Move down
            own_ship_pos += PLAYER_SPEED

        # -------- Background stars -------- #
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 2)  # Draw star (white dot)
            star[0] -= 2                                          # Move star left
            if star[0] < 0:                                       # Wrap star back to right
                star[0] = WIDTH
                star[1] = random.randint(0, HEIGHT)

        # -------- Spawn new ship -------- #
        if spawn_new_ship and len(ships) < max_ships:
            ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
            ship.ship_pos_x = WIDTH + random.randint(50, 300)
            ships.append(ship)
            spawn_new_ship = False

        # -------- Update ships -------- #
        for ship in ships[:]:
            ship.show_ship(screen)                 # Draw ship
            if ship.ship_pos_x < 0:                # If enemy passes left edge
                running = False                    # GAME OVER

        # -------- Update lasers -------- #
        for laser in lasers[:]:
            pygame.draw.line(screen, (255, 0, 0), (laser[0], laser[1]), (laser[0] + 60, laser[1]), 10)  # Red core
            pygame.draw.line(screen, (255, 255, 0), (laser[0], laser[1]), (laser[0] + 60, laser[1]), 4) # Yellow glow
            laser[0] += LASER_SPEED   # Move laser forward

            if laser[0] >= WIDTH:     # Remove if offscreen
                lasers.remove(laser)
                continue

            # Check collision with ships
            for ship in ships[:]:
                if np.abs(laser[0] - ship.ship_pos_x) < 40 and np.abs(laser[1] - ship.ship_pos_y) < 40:
                    explosions.append(Explosion(laser[0], laser[1]))   # Add explosion
                    ships.remove(ship)     # Destroy ship
                    if laser in lasers:    # Remove laser too
                        lasers.remove(laser)
                    spawn_new_ship = True  # Queue a new ship
                    score += 1             # Increase score

        # -------- Difficulty scaling -------- #
        if score > 0 and score % 3 == 0 and last_speed_increase != score:
            ship_speed += 1               # Enemies move faster
            last_speed_increase = score
        if score > 0 and score % 5 == 0 and last_speed_increase != score:
            PLAYER_SPEED += 1             # Player moves faster
            last_speed_increase = score
        if score > 0 and score % 10 == 0 and last_speed_increase != score:
            max_ships += 1                # Allow more ships on screen
            last_speed_increase = score

        # -------- Explosions -------- #
        for exp in explosions[:]:
            exp.draw_explosion(screen)    # Draw explosion
            if exp.circle_radius > 200:   # Remove when too big
                explosions.remove(exp)

        # -------- Draw player rocket -------- #
        rocket_x = 50
        rocket_y = own_ship_pos

        # ROCKET ASCII DIAGRAM
        #
        #        ▲ Flame
        #       / \
        #      /   \        <--- Flickering orange flame
        #     /     \
        #    |       |
        #   [■][■][■]  <--- Body (rectangle)
        #    |  ●  |   <--- Window (blue circle)
        #   / \   / \
        #  /   \ /   \  <--- Fins (triangles)
        #
        # ------------------------------------ #

        pygame.draw.rect(screen, (200, 200, 255), (rocket_x, rocket_y - 20, 50, 40))  # Body
        pygame.draw.polygon(screen, (180, 0, 0), [(rocket_x + 50, rocket_y - 20),
                                                  (rocket_x + 50, rocket_y + 20),
                                                  (rocket_x + 70, rocket_y)])        # Nose cone
        pygame.draw.polygon(screen, (180, 0, 0), [(rocket_x, rocket_y - 20),
                                                  (rocket_x - 15, rocket_y - 30),
                                                  (rocket_x, rocket_y - 30)])        # Top fin
        pygame.draw.polygon(screen, (180, 0, 0), [(rocket_x, rocket_y + 20),
                                                  (rocket_x - 15, rocket_y + 30),
                                                  (rocket_x, rocket_y + 30)])        # Bottom fin
        pygame.draw.circle(screen, (0, 150, 255), (rocket_x + 25, rocket_y), 8)      # Window
        flame_length = random.randint(15, 30)                                        # Flickering flame
        pygame.draw.polygon(screen, (255, 140, 0), [(rocket_x, rocket_y - 20),
                                                    (rocket_x, rocket_y + 20),
                                                    (rocket_x - flame_length, rocket_y)])

        # -------- Score text -------- #
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (WIDTH - 250, 20))

        pygame.display.flip()            # Update screen
        clock.tick(FPS)                  # Lock FPS

    return score                         # Return final score after GAME OVER
