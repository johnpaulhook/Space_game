import pygame
import random
import sys
import numpy as np
from game_objects import Ship, Explosion
import datetime
import os

# ---------------------------
# SCORE SYSTEM
# ---------------------------

# File to save scores
# ⚠️ Changed from .py to .txt so we don’t corrupt a Python file
SCORES_FILE = "scores.txt"

def save_score(score):
    """Save the player's score with timestamp into a file."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")  # current date/time
    with open(SCORES_FILE, "a") as f:  # open file in append mode
        f.write(f"{score},{now}\n")    # save as: score,datetime

def load_top_scores(limit=3):
    """Load scores from file and return top N as list of tuples (score, date)."""
    if not os.path.exists(SCORES_FILE):  # if file doesn’t exist, return nothing
        return []
    
    with open(SCORES_FILE, "r") as f:    # read file
        lines = f.readlines()
    
    scores = []
    for line in lines:                   # parse each line
        try:
            s, d = line.strip().split(",", 1)  # split into score and date
            scores.append((int(s), d))        # store as tuple
        except:
            continue  # skip bad lines (if file is corrupted)
    
    # Sort scores from highest → lowest
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:limit]  # return only top N scores

# ---------------------------
# PYGAME INITIAL SETUP
# ---------------------------

pygame.init()          # start pygame
pygame.font.init()     # start fonts

# Screen dimensions
WIDTH = 1900 
HEIGHT = 1000

# Number of stars in background
num_stars = 1000

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("-<>- Johnny's Space Game -<>-")

# Generate random stars (list of (x, y) positions)
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(num_stars)]


# ---------------------------
# MAIN GAME LOOP FUNCTION
# ---------------------------
def run_game():
    """One round of gameplay"""
    # Create variables that reset each round
    spawn_new_ship = False          # flag to spawn new ship after one dies
    lasers = []                     # list of active lasers
    # Start game with 2 ships at random vertical positions
    ships = [
    Ship(speed=5, ship_pos=random.randint(100, HEIGHT - 100)),
    Ship(speed=5, ship_pos=random.randint(100, HEIGHT - 100))]
    explosions = []                 # list of active explosio  # main loop control
    ship_speed = 5                  # speed of enemy ships
    space_pressed = False           # whether spacebar is pressed
    laser_width = 20                # laser beam horizontal length
    max_blast_radius = 300          # explosion size
    explosion_y = None              # unused var (can remove later)
    circle_radius = max_blast_radius
    own_ship_pos = 250              # y-position of player rocket
    show_ship = True                # whether to show enemy ship
    running = True 
    # Player score
    score = 0

    # Font for drawing score in-game
    font = pygame.font.SysFont(None, 50)

    # Create a clock to control FPS
    clock = pygame.time.Clock()

    # ---------------------------
    # MAIN LOOP
    # ---------------------------
    while running:

        # Spawn new enemy ship if flagged
        if spawn_new_ship:
            new_ship = Ship(speed=ship_speed)
            ships.append(new_ship)
            spawn_new_ship = False

        # Clear screen (black background)
        screen.fill((0, 0, 0))

        # --- Draw Stars (background) ---
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 2)

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

        # --- Enemy Ships ---
        for ship in ships:
            ship.show_ship(screen=screen)
            if ship.ship_reached_end():  # ship reached left side = GAME OVER
                print("GAME OVER")
                running = False
                ships.remove(ship)

        # --- Lasers (shots fired by player) ---
        for laser in lasers[:]:  # [:] = copy so we can remove safely
            # Draw red laser
            pygame.draw.line(screen, (255,0,0), (laser[0], laser[1]), (laser[0]+laser_width, laser[1]), 10)
            laser[0] += 50  # move laser to the right

            # If laser goes off screen → explosion effect
            if laser[0] >= 1850:
                circle_radius = 0
                explosion_y = laser[1]
                lasers.remove(laser)

            # Check collision with enemy ships
            for ship in ships:
                if np.abs(laser[0] - ship.ship_pos_x) < 40 and np.abs(laser[1] - ship.ship_pos_y) < 40:
                    # Hit detected → explosion + remove ship + remove laser
                    explosions.append(Explosion(pos_x=laser[0], pos_y=laser[1]))
                    ships.remove(ship)
                    lasers.remove(laser)
                    spawn_new_ship = True  # schedule new ship
                    score += 1             # increase score
                    if score % 3 == 0:     # every 3 kills → enemies get faster
                        ship_speed += 1 

        # --- Explosions ---
        for blast in explosions:
            blast.draw_explosion(screen)
            if blast.circle_radius >= max_blast_radius:
                explosions.remove(blast)  # remove once done expanding

        # --- Player Controls ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and own_ship_pos > 50:
            own_ship_pos -= 10   # move up
        if keys[pygame.K_DOWN] and own_ship_pos < 950:
            own_ship_pos += 10   # move down

        # --- Draw Score ---
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (WIDTH - 250, 20))  # top-right corner

        # Update screen
        pygame.display.flip()

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # quit game
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:       
                if event.key == pygame.K_SPACE:    # shoot laser
                    space_pressed = True
                    lasers.append([100, own_ship_pos])  # laser starts at rocket
                elif event.key == pygame.key.key_code('r'):  # debug: spawn ship
                    new_ship = Ship()
                    ships.append(new_ship)

        # Control FPS (60 frames per second)
        clock.tick(60)

    # Return final score after loop ends (GAME OVER)
    return score


# ---------------------------
# GAME OVER + RESTART LOOP
# ---------------------------
while True:
    score = run_game()              # play one round
    save_score(score)               # save the score with date
    top_scores = load_top_scores(3) # get top 3 scores

    # --- Game Over screen ---
    screen.fill((0, 0, 0))  # black background
    font = pygame.font.SysFont(None, 150)

    # Main GAME OVER text
    text_surface = font.render("GAME OVER", True, (255, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(text_surface, text_rect)

    # Player’s score text
    text_surface2 = font.render(f"--Score: {score}--", True, (255, 0, 0))
    text_rect2 = text_surface2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))  # ✅ fixed bug
    screen.blit(text_surface2, text_rect2)

    # --- Draw Top 3 Scores ---
    font_small = pygame.font.SysFont(None, 70)
    y_offset = HEIGHT // 2 + 200
    for i, (s, d) in enumerate(top_scores, start=1):
        text = font_small.render(f"{i}. {s}  ({d})", True, (255, 0, 0))  # red text
        text_rect = text.get_rect(center=(WIDTH // 2, y_offset))         # center
        screen.blit(text, text_rect)
        y_offset += 80

    # Wait for ENTER key to restart game
    end_display_running = True
    while end_display_running:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # quit game completely
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:   # restart on Enter
                    end_display_running = False
