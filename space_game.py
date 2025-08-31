# ------------------- IMPORTS ------------------- #
import pygame                # Main game library (graphics, sound, input handling)
import random                # For randomness (ship spawn positions, flame flicker, etc.)
import sys                   # For exiting the program cleanly
import numpy as np           # For math functions (used here for abs in collision detection)
import os                    # To check if score file exists / handle file paths
from game_objects import Ship, Explosion   # Import custom Ship + Explosion classes

# ------------------- CONSTANTS ------------------- #

SCORES_FILE = "scores.txt"   # File where scores will be stored

WIDTH = 1900                 # Width of the game window
HEIGHT = 1000                # Height of the game window
FPS = 60                     # Frames per second limit (game speed)

# ---------------- SCORE HANDLING ---------------- #

def save_score(score, initials):
    """Save the player's score with initials into a file."""
    with open(SCORES_FILE, "a") as f:           # Open the score file in append mode
        f.write(f"{score},{initials}\n")        # Write score + initials (e.g. "120,ABC")

def load_top_scores(limit=3):
    """Load scores from file and return top N as list of (score, initials)."""
    if not os.path.exists(SCORES_FILE):         # If no score file exists yet
        return []                               # Return empty list (no scores)

    with open(SCORES_FILE, "r") as f:           # Open file in read mode
        lines = f.readlines()                   # Read all lines

    scores = []                                 # Store parsed scores
    for line in lines:
        try:
            s, initials = line.strip().split(",", 1)   # Split by comma → (score, initials)
            scores.append((int(s), initials))          # Store as (int_score, initials)
        except:
            continue                              # Skip any bad/invalid lines

    scores.sort(key=lambda x: x[0], reverse=True) # Sort high → low
    return scores[:limit]                        # Return only top `limit` scores

# ---------------- INITIALS INPUT ---------------- #

def get_initials(screen):
    """Ask the player to type 1–3 initials before game starts."""
    initials = ""                                # Store what player types
    entering = True                              # Loop until Enter is pressed
    font_big = pygame.font.SysFont(None, 100)    # Large font for title
    font_small = pygame.font.SysFont(None, 50)   # Smaller font for hints

    while entering:                              # Keep looping until done
        screen.fill((0, 0, 0))                   # Black background

        text = font_big.render("Enter Your Initials:", True, (255, 255, 0)) # Yellow text
        screen.blit(text, (WIDTH//2 - 300, HEIGHT//2 - 100))                 # Draw centered

        text2 = font_big.render(initials, True, (0, 255, 0))                 # Green initials typed
        screen.blit(text2, (WIDTH//2 - 100, HEIGHT//2 + 20))                 # Show input

        hint = font_small.render("Press ENTER when done (max 3 letters)", True, (200, 200, 200))
        screen.blit(hint, (WIDTH//2 - 250, HEIGHT//2 + 150))                 # Hint below

        pygame.display.flip()                                               # Refresh screen

        for event in pygame.event.get():           # Process all input events
            if event.type == pygame.QUIT:          # If window closed
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:       # Key pressed
                if event.key == pygame.K_RETURN and initials:  # Enter finishes
                    entering = False
                elif event.key == pygame.K_BACKSPACE:          # Backspace deletes last char
                    initials = initials[:-1]
                elif len(initials) < 3 and event.unicode.isalpha(): # Only letters allowed
                    initials += event.unicode.upper()                # Add uppercase letter

    return initials   # Return typed initials

# ---------------- GAME LOOP ---------------- #

def run_game(screen):
    own_ship_pos = HEIGHT // 2     # Player’s rocket starts at vertical center
    ship_speed = 5                 # Speed of enemy ships
    max_ships = 200                # Maximum number of ships on screen
    spawn_new_ship = False         # Flag to control spawning a new ship

    # ---- Create starting enemy ships ---- #
    ships = []
    for _ in range(2):                                       # Start with 2 enemies
        ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
        ship.ship_pos_x = WIDTH + random.randint(50, 300)    # Start offscreen to the right
        ships.append(ship)

    lasers = []                       # List to track fired lasers
    explosions = []                   # List to track explosions
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(200)] # Starfield

    PLAYER_SPEED = 10                 # Player vertical movement speed
    LASER_SPEED = 50                  # Laser horizontal speed
    score = 0                         # Player score
    running = True                    # Game loop flag
    clock = pygame.time.Clock()       # Control framerate
    font = pygame.font.SysFont(None, 55)  # Score font
    last_speed_increase = 0           # Prevents multiple speed boosts at same score

    # -------- Main game loop -------- #
    while running:
        screen.fill((0, 0, 0))        # Clear screen (black)

        # --------- Handle events --------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       # Window close
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: # Shoot
                lasers.append([100, own_ship_pos])  # Start laser at rocket’s nose

        # Keyboard input (continuous, not just events)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:    # Move up
            own_ship_pos -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  # Move down
            own_ship_pos += PLAYER_SPEED

        # --------- Background stars --------- #
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 2)  # Draw star
            star[0] -= 2                                          # Move left
            if star[0] < 0:                                       # Wrap around
                star[0] = WIDTH
                star[1] = random.randint(0, HEIGHT)

        # --------- Spawn new ship if needed --------- #
        if spawn_new_ship and len(ships) < max_ships:             # If replacement flagged
            ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
            ship.ship_pos_x = WIDTH + random.randint(50, 300)
            ships.append(ship)
            spawn_new_ship = False

        # --------- Update ships --------- #
        for ship in ships[:]:
            ship.show_ship(screen)     # Draw each enemy ship
            if ship.ship_pos_x < 0:    # If ship passes player → GAME OVER
                running = False

        # --------- Update lasers --------- #
        for laser in lasers[:]:
            # Draw glowing laser beam
            pygame.draw.line(screen, (255, 0, 0), (laser[0], laser[1]), (laser[0] + 60, laser[1]), 10)
            pygame.draw.line(screen, (255, 255, 0), (laser[0], laser[1]), (laser[0] + 60, laser[1]), 4)
            laser[0] += LASER_SPEED    # Move right

            if laser[0] >= WIDTH:      # Remove laser offscreen
                lasers.remove(laser)
                continue

            # ---- Collision detection ---- #
            for ship in ships[:]:
                if np.abs(laser[0] - ship.ship_pos_x) < 40 and np.abs(laser[1] - ship.ship_pos_y) < 40:
                    explosions.append(Explosion(laser[0], laser[1]))  # Add explosion
                    ships.remove(ship)                                # Destroy ship
                    if laser in lasers: lasers.remove(laser)          # Remove laser
                    spawn_new_ship = True                             # Mark replacement
                    score += 1                                        # Increase score

        # --------- Difficulty Scaling --------- #
        if score > 0 and score % 3 == 0 and last_speed_increase != score:
            ship_speed += 1        # Enemy ships get faster
            last_speed_increase = score
        if score > 0 and score % 5 == 0 and last_speed_increase != score:
            PLAYER_SPEED += 1      # Player moves faster
            last_speed_increase = score
        if score > 0 and score % 10 == 0 and last_speed_increase != score:
            max_ships += 1         # More enemies can appear
            last_speed_increase = score

        # --------- Update explosions --------- #
        for exp in explosions[:]:
            exp.draw_explosion(screen)               # Draw explosion expanding
            if exp.circle_radius > 200:              # Remove once too big
                explosions.remove(exp)

        # --------- Draw Player Rocket --------- #
        rocket_x = 50
        rocket_y = own_ship_pos

        pygame.draw.rect(screen, (200, 200, 255), (rocket_x, rocket_y - 20, 50, 40)) # Body
        pygame.draw.polygon(screen, (180, 0, 0), [   # Nose cone
            (rocket_x + 50, rocket_y - 20),
            (rocket_x + 50, rocket_y + 20),
            (rocket_x + 70, rocket_y)
        ])
        pygame.draw.polygon(screen, (180, 0, 0), [   # Top fin
            (rocket_x, rocket_y - 20),
            (rocket_x - 15, rocket_y - 30),
            (rocket_x, rocket_y - 30)
        ])
        pygame.draw.polygon(screen, (180, 0, 0), [   # Bottom fin
            (rocket_x, rocket_y + 20),
            (rocket_x - 15, rocket_y + 30),
            (rocket_x, rocket_y + 30)
        ])
        pygame.draw.circle(screen, (0, 150, 255), (rocket_x + 25, rocket_y), 8) # Window
        flame_length = random.randint(15, 30)        # Random flickering flame
        pygame.draw.polygon(screen, (255, 140, 0), [
            (rocket_x, rocket_y - 20),
            (rocket_x, rocket_y + 20),
            (rocket_x - flame_length, rocket_y)
        ])

        # --------- Draw Score --------- #
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (WIDTH - 250, 20))

        pygame.display.flip()       # Update screen
        clock.tick(FPS)             # Cap FPS

    return score   # Return score when player dies

# ---------------- MAIN LOOP ---------------- #

def main():
    pygame.init()                                      # Initialize pygame
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Create game window
    pygame.display.set_caption("Space Game with Initials")  # Window title

    font_big = pygame.font.SysFont(None, 100)          # Large font
    font_small = pygame.font.SysFont(None, 55)         # Smaller font

    while True:   # Infinite loop (restart after death)
        initials = get_initials(screen)                # Ask initials
        score = run_game(screen)                       # Play game
        save_score(score, initials)                    # Save score
        top_scores = load_top_scores()                 # Load leaderboard

        # --------- Game Over Screen --------- #
        showing = True
        while showing:
            screen.fill((0, 0, 0))  # Clear screen black

            text = font_big.render("GAME OVER", True, (255, 0, 0))          # Red GAME OVER
            screen.blit(text, (WIDTH//2 - 200, HEIGHT//2 - 150))

            score_text = font_small.render(f"Your Score: {score} ({initials})", True, (255, 255, 0))
            screen.blit(score_text, (WIDTH//2 - 200, HEIGHT//2 - 50))

            top_text = font_small.render("Top Scores:", True, (0, 255, 0))
            screen.blit(top_text, (WIDTH//2 - 200, HEIGHT//2 + 20))

            # Draw top scores list
            for i, (s, ini) in enumerate(top_scores, start=1):
                entry = font_small.render(f"{i}. {s} ({ini})", True, (0, 200, 200))
                screen.blit(entry, (WIDTH//2 - 200, HEIGHT//2 + 60 + i * 40))

            restart_text = font_small.render("Press ENTER to Play Again or Q to Quit", True, (200, 200, 200))
            screen.blit(restart_text, (WIDTH//2 - 300, HEIGHT//2 + 250))

            pygame.display.flip()   # Refresh screen

            for event in pygame.event.get():   # Handle input
                if event.type == pygame.QUIT:  # Window closed
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:   # Restart
                        showing = False
                    elif event.key == pygame.K_q:      # Quit game
                        pygame.quit()
                        sys.exit()

# Run game if file executed directly
if __name__ == "__main__":
    main()
