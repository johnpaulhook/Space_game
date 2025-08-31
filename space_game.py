import pygame
import random
import sys
import numpy as np
from game_objects import Ship, Explosion
import datetime
import os

SCORES_FILE = "score.py"

def save_score(score):
    """Save the player's score with timestamp into a file."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(SCORES_FILE, "a") as f:
        f.write(f"{score},{now}\n")

def load_top_scores(limit=3):
    """Load scores from file and return top N as list of tuples (score, date)."""
    if not os.path.exists(SCORES_FILE):
        return []
    
    with open(SCORES_FILE, "r") as f:
        lines = f.readlines()
    
    scores = []
    for line in lines:
        try:
            s, d = line.strip().split(",", 1)
            scores.append((int(s), d))
        except:
            continue  # skip malformed lines
    
    # Sort by score (descending)
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:limit]

# Initialize Pygame and fonts
pygame.init()
pygame.font.init()

# Screen dimensions
WIDTH = 1900 
HEIGHT = 1000
num_stars = 1000   # number of stars in the background
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("-<>- Johnny's Space Game -<>-")

# Generate random star positions
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(num_stars)]

# ---------------------------
# GAME LOOP FUNCTION
# ---------------------------
def run_game():
    # Initialize variables for each new round
    spawn_new_ship = False  # flag to decide if we need a new ship
    lasers = []             # list to hold active lasers
    ships = [Ship(speed=5, ship_pos=random.randint(100, HEIGHT - 100))]  # first enemy ship
    explosions = []         # active explosions
    ship_speed = 5          # starting speed of enemy ships
    space_pressed = False   # track spacebar for shooting
    laser_width = 20        # horizontal length of laser beam
    max_blast_radius = 300  # explosion max size
    explosion_y = None
    circle_radius = max_blast_radius
    own_ship_pos = 250      # starting y-position of player rocket
    ship_pos = 250          # temp variable used in blast detection
    show_ship = True        # whether ship is visible
    running = True          # main loop flag

    score = 0   # <--- player score starts at 0
    font = pygame.font.SysFont(None, 50)  # <--- font for score display

    # ---------------------------
    # MAIN GAME LOOP
    # ---------------------------
    while running:
        # Spawn new enemy ship when flag is set
        if spawn_new_ship:
            new_ship = Ship(speed=ship_speed)
            ships.append(new_ship)
            spawn_new_ship = False

        # Clear screen (black background)
        screen.fill((0, 0, 0))

        # --- Draw Stars ---
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 2)

        # --- Draw Player Rocket ---
        rocket_x = 50
        rocket_y = own_ship_pos

        # Rocket body
        pygame.draw.rect(screen, (200, 200, 255), (rocket_x, rocket_y - 20, 50, 40))
        # Nose cone
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
        # Window
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
            if ship.ship_reached_end():  # if enemy reaches left edge
                print("GAME OVER")
                running = False
                ships.remove(ship)  # remove the ship -> triggers game over

        # --- Lasers (bullets from player rocket) ---
        for laser in lasers[:]:  # [:] = copy so we can safely remove
            # Draw red laser line
            pygame.draw.line(screen, (255,0,0), (laser[0], laser[1]), (laser[0]+laser_width, laser[1]), 10)
            laser[0] += 50  # move laser rightwards (speed)

            # If laser goes off screen -> trigger explosion
            if laser[0] >= 1850:
                circle_radius = 0
                explosion_y = laser[1]
                lasers.remove(laser)
                if np.abs(ship_pos - laser[1]) < max_blast_radius:
                    show_ship = False  # hide ship if in blast radius

            # Check collision with enemy ships
            for ship in ships:
                if np.abs(laser[0] - ship.ship_pos_x) < 40 and np.abs(laser[1] - ship.ship_pos_y) < 40:
                    # Hit detected -> explosion
                    explosions.append(Explosion(pos_x=laser[0], pos_y=laser[1]))
                    ships.remove(ship)   # destroy ship
                    lasers.remove(laser) # remove laser
                    spawn_new_ship = True
                    score += 1           # increase score
                    if score % 3 == 0:   # every 3 kills -> ships get faster
                        ship_speed += 1 

        # --- Explosions ---
        for blast in explosions:
            blast.draw_explosion(screen)
            if blast.circle_radius >= max_blast_radius:
                explosions.remove(blast)  # remove when fully expanded

        # --- Player Controls ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and own_ship_pos > 50:
            own_ship_pos -= 10   # move rocket up
        if keys[pygame.K_DOWN] and own_ship_pos < 950:
            own_ship_pos += 10   # move rocket down

        # --- Draw Score ---
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (WIDTH - 250, 20))  # top-right corner

        pygame.display.flip()

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # close window
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:       
                if event.key == pygame.K_SPACE:    # shoot laser
                    space_pressed = True
                    lasers.append([100, own_ship_pos])  # new laser starts at rocket
                elif event.key == pygame.key.key_code('r'):  # debug: spawn extra ship
                    new_ship = Ship()
                    ships.append(new_ship)

        pygame.time.Clock().tick(60)  # cap frame rate at 60 FPS
    return score

# ---------------------------
# MAIN LOOP: restart on ENTER
# ---------------------------
while True:
    score = run_game()  # play one round
    save_score(score)                 # save the score with date
    top_scores = load_top_scores(3)   # get top 3 scores

    # --- Game Over screen ---
    screen.fill((0, 0, 0))  # black background
    font = pygame.font.SysFont(None, 150)
    text_surface = font.render("GAME OVER", True, (255, 0, 0))
    text_surface2 = font.render(f"--Score: {score}--", True, (255, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    text_rect2 = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    screen.blit(text_surface, text_rect)
    screen.blit(text_surface2, text_rect2)
        # --- Draw Top 3 Scores ---
    font_small = pygame.font.SysFont(None, 70)
    y_offset = HEIGHT // 2 + 200
    for i, (s, d) in enumerate(top_scores, start=1):
        text = font_small.render(f"{i}. {s}  ({d})", True, (255, 0, 0))  # RED
        text_rect = text.get_rect(center=(WIDTH // 2, y_offset))         # CENTER
        screen.blit(text, text_rect)
        y_offset += 80

    # Wait for user to press ENTER before restarting
    end_display_running = True
    while end_display_running:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # quit game
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:   # Enter key restarts
                    end_display_running = False # end display
