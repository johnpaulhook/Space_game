import pygame
import random
import sys
import numpy as np
from game_objects import Ship, Explosion

# # Ask user for number of stars
# try:
#     num_stars = int(input("Enter number of stars: "))
# except ValueError:
#     print("Invalid input! Defaulting to 100 stars.")
#     num_stars = 100

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions
WIDTH = 1900 
HEIGHT = 1000
num_stars = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("-<>- Johnny's Space Game -<>-")

# Generate random star positions
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(num_stars)]

# Main loop
def run_game():
    # Initialize variables for each game run
    spawn_new_ship = False
    lasers=[]
    ships = [Ship(speed=5, ship_pos=random.randint(100, HEIGHT - 100))]
    explosions = []
    ship_speed = 5
    space_pressed = False
    laser_width = 20
    max_blast_radius = 300
    explosion_y = None
    circle_radius = max_blast_radius
    own_ship_pos = 250
    ship_pos = 250
    show_ship = True
    running = True

    score = 0   # <--- score starts at 0
    font = pygame.font.SysFont(None, 50)  # <--- font for score

    while running:
        if spawn_new_ship == True:
            new_ship = Ship(speed=ship_speed)
            ships.append(new_ship)
            spawn_new_ship = False

        screen.fill((0, 0, 0))  # black background
        
        # --- Draw Stars ---
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 2)

        # --- Rocket Drawing ---
        rocket_x = 50
        rocket_y = own_ship_pos

        pygame.draw.rect(screen, (200, 200, 255), (rocket_x, rocket_y - 20, 50, 40))
        pygame.draw.polygon(screen, (180, 0, 0), [
            (rocket_x + 50, rocket_y - 20),
            (rocket_x + 50, rocket_y + 20),
            (rocket_x + 70, rocket_y)
        ])
        pygame.draw.polygon(screen, (180, 0, 0), [
            (rocket_x, rocket_y - 20),
            (rocket_x - 15, rocket_y - 30),
            (rocket_x, rocket_y - 30)
        ])
        pygame.draw.polygon(screen, (180, 0, 0), [
            (rocket_x, rocket_y + 20),
            (rocket_x - 15, rocket_y + 30),
            (rocket_x, rocket_y + 30)
        ])
        pygame.draw.circle(screen, (0, 150, 255), (rocket_x + 25, rocket_y), 8)

        flame_length = random.randint(15, 30)
        pygame.draw.polygon(screen, (255, 140, 0), [
            (rocket_x, rocket_y - 20),
            (rocket_x, rocket_y + 20),
            (rocket_x - flame_length, rocket_y)
        ])

        # --- Ships ---
        for ship in ships:
            ship.show_ship(screen=screen)
            if ship.ship_reached_end():
                print("GAME OVER")
                running = False
                ships.remove(ship)

        # --- Lasers ---
        for laser in lasers[:]:
            pygame.draw.line(screen, (255,0,0), (laser[0], laser[1]), (laser[0]+laser_width, laser[1]), 10)
            laser[0] += 50
            if laser[0] >= 1850:
                circle_radius = 0
                explosion_y = laser[1]
                lasers.remove(laser)
                if np.abs(ship_pos - laser[1]) < max_blast_radius:
                    show_ship = False
            for ship in ships:
                if np.abs(laser[0] - ship.ship_pos_x) < 40 and np.abs(laser[1] - ship.ship_pos_y) < 40:
                    explosions.append(Explosion(pos_x=laser[0], pos_y=laser[1]))
                    ships.remove(ship)
                    lasers.remove(laser)
                    spawn_new_ship = True
                    score += 1   # <--- ADD POINT when ship destroyed
                    if score%3 == 0:
                        ship_speed +=1 

        # --- Explosions ---
        for blast in explosions:
            blast.draw_explosion(screen)
            if blast.circle_radius >= max_blast_radius:
                explosions.remove(blast)

        # --- Controls ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and own_ship_pos > 50:
            own_ship_pos -= 10
        if keys[pygame.K_DOWN] and own_ship_pos < 950:
            own_ship_pos += 10

        # --- Draw Score ---
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (WIDTH - 250, 20))  # top-right corner

        pygame.display.flip()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:       
                if event.key == pygame.K_SPACE:    
                    space_pressed = True
                    lasers.append([100, own_ship_pos])
                elif event.key == pygame.key.key_code('r'):
                    new_ship = Ship()
                    ships.append(new_ship)

        pygame.time.Clock().tick(60)  # 60 FPS
    return score
# ---------------------------
# MAIN LOOP: restart on ENTER
# ---------------------------
while True:
    score = run_game()  # play one round
    
    # Game Over screen
    screen.fill((0, 0, 0))  # black background
    font = pygame.font.SysFont(None, 150)
    text_surface = font.render("GAME OVER", True, (255, 0, 0))
    text_surface2 = font.render(f"--Score: {score}--", True, (255, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2-100))
    text_rect2 = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2+100))
    screen.blit(text_surface, text_rect)
    screen.blit(text_surface2, text_rect2)
    
    end_display_running = True
    while end_display_running:
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:   # Enter key
                    end_display_running = False   # break -> restart game
