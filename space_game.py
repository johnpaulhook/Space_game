# ------------------- IMPORTS ------------------- #
import pygame                # Main game library (graphics, sound, input handling)
import random                # For randomness (ship spawn positions, etc.)
import sys                   # For exiting the program cleanly
import numpy as np           # For math functions (sinusoidal flame, collisions)
import os                    # To check if score file exists / handle file paths
from game_objects import Ship, Explosion   # Import custom Ship + Explosion classes

# ------------------- CONSTANTS ------------------- #
SCORES_FILE = "scores.txt"   # File where scores will be stored

WIDTH = 1900                 # Width of the game window
HEIGHT = 1000                # Height of the game window
FPS = 60                     # Frames per second limit (game speed)

PLAYER_BASE_SPEED = 10        # Player vertical movement speed (base)
LASER_SPEED = 50              # Laser horizontal speed
STAR_LAYERS = [1, 2, 3]       # Different star speeds for parallax
STARS_PER_LAYER = 70          # Number of stars in each layer

# ---------------- SCORE HANDLING ---------------- #
def save_score(score, initials):
    """Save the player's score with initials into a file."""
    with open(SCORES_FILE, "a") as f:
        f.write(f"{score},{initials}\n")

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
            scores.append((int(s), initials))
        except:
            continue

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

        text = font_big.render("Enter Your Initials:", True, (255, 255, 0))
        screen.blit(text, (WIDTH//2 - 300, HEIGHT//2 - 100))

        text2 = font_big.render(initials, True, (0, 255, 0))
        screen.blit(text2, (WIDTH//2 - 100, HEIGHT//2 + 20))

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
    own_ship_pos = HEIGHT // 2
    ship_speed = 5
    max_ships = 200
    spawn_new_ship = False

    # ---- Create starting enemy ships ---- #
    ships = []
    for _ in range(2):
        ship = Ship(speed=ship_speed, ship_pos=random.randint(100, HEIGHT - 100))
        ship.ship_pos_x = WIDTH + random.randint(50, 300)
        ships.append(ship)

    lasers = []
    explosions = []

    # --- Parallax starfield setup --- #
    stars = []
    for layer in STAR_LAYERS:
        for _ in range(STARS_PER_LAYER):
            stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), layer])

    player_speed = PLAYER_BASE_SPEED
    score = 0
    running = True
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 55)

    # Difficulty scaling flags
    last_enemy_speed_up = 0
    last_player_speed_up = 0
    last_enemy_count_up = 0

    # -------- Main game loop -------- #
    while running:
        dt = clock.tick(FPS) / 1000.0
        screen.fill((0, 0, 0))

        # --------- Handle events --------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                lasers.append([100, own_ship_pos])

        # Keyboard input (continuous)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            own_ship_pos -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            own_ship_pos += player_speed

        # --------- Background stars (parallax) --------- #
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), (star[0], star[1]), star[2])
            star[0] -= star[2]  # Move by its layer speed
            if star[0] < 0:
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
            ship.show_ship(screen)
            if ship.ship_pos_x < 0:  # Enemy passed → game over
                running = False

        # --------- Update lasers --------- #
        for laser in lasers[:]:
            # Laser beam (red core + yellow glow)
            pygame.draw.line(screen, (255, 0, 0), (laser[0], laser[1]), (laser[0] + 60, laser[1]), 10)
            pygame.draw.line(screen, (255, 255, 0), (laser[0], laser[1]), (laser[0] + 60, laser[1]), 4)
            laser[0] += LASER_SPEED

            if laser[0] >= WIDTH:
                lasers.remove(laser)
                continue

            # ---- Collision detection ---- #
            for ship in ships[:]:
                if np.abs(laser[0] - ship.ship_pos_x) < 40 and np.abs(laser[1] - ship.ship_pos_y) < 40:
                    explosions.append(Explosion(laser[0], laser[1]))
                    ships.remove(ship)
                    if laser in lasers:
                        lasers.remove(laser)
                    spawn_new_ship = True
                    score += 1

        # --------- Difficulty Scaling --------- #
        if score >= last_enemy_speed_up + 3:
            ship_speed += 1
            last_enemy_speed_up = score
        if score >= last_player_speed_up + 5:
            player_speed += 1
            last_player_speed_up = score
        if score >= last_enemy_count_up + 10:
            max_ships += 1
            last_enemy_count_up = score

        # --------- Update explosions --------- #
        for exp in explosions[:]:
            exp.draw_explosion(screen)
            if exp.circle_radius > 200:
                explosions.remove(exp)

        # --------- Draw Player Rocket --------- #
        rocket_x = 50
        rocket_y = own_ship_pos

        pygame.draw.rect(screen, (200, 200, 255), (rocket_x, rocket_y - 20, 50, 40))  # Body
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
        pygame.draw.circle(screen, (0, 150, 255), (rocket_x + 25, rocket_y), 8)  # Window

        # Smooth flame (sinusoidal "breathing")
        t = pygame.time.get_ticks() * 0.02
        flame_length = 20 + int(10 * np.sin(t))
        pygame.draw.polygon(screen, (255, 140, 0), [
            (rocket_x, rocket_y - 20),
            (rocket_x, rocket_y + 20),
            (rocket_x - flame_length, rocket_y)
        ])

        # --------- Draw Score --------- #
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (WIDTH - 250, 20))

        pygame.display.flip()

    return score

# ---------------- MAIN LOOP ---------------- #
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Game with Initials")

    font_big = pygame.font.SysFont(None, 100)
    font_small = pygame.font.SysFont(None, 55)

    while True:
        initials = get_initials(screen)
        score = run_game(screen)
        save_score(score, initials)
        top_scores = load_top_scores()

        # --------- Game Over Screen --------- #
        showing = True
        while showing:
            screen.fill((0, 0, 0))

            text = font_big.render("GAME OVER", True, (255, 0, 0))
            screen.blit(text, (WIDTH//2 - 200, HEIGHT//2 - 150))

            score_text = font_small.render(f"Your Score: {score} ({initials})", True, (255, 255, 0))
            screen.blit(score_text, (WIDTH//2 - 200, HEIGHT//2 - 50))

            top_text = font_small.render("Top Scores:", True, (0, 255, 0))
            screen.blit(top_text, (WIDTH//2 - 200, HEIGHT//2 + 20))

            for i, (s, ini) in enumerate(top_scores, start=1):
                entry = font_small.render(f"{i}. {s} ({ini})", True, (0, 200, 200))
                screen.blit(entry, (WIDTH//2 - 200, HEIGHT//2 + 60 + i * 40))

            restart_text = font_small.render("Press ENTER to Play Again or Q to Quit", True, (200, 200, 200))
            screen.blit(restart_text, (WIDTH//2 - 300, HEIGHT//2 + 250))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        showing = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

if __name__ == "__main__":
    main()
