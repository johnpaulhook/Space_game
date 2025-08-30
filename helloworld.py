def run_game():
    # Initialize variables for each game run
    spawn_new_ship = False
    lasers=[]
    ships=[Ship(ship_pos=250, speed=5)]
    explosions = []
    space_pressed = False
    laser_width = 20
    max_blast_radius = 300
    explosion_y = None
    circle_radius = max_blast_radius
    own_ship_pos = 250
    ship_pos = 250
    show_ship = True
    running = True

    while running:
        if spawn_new_ship == True:
            new_ship = Ship(speed=5)
            ships.append(new_ship)
            spawn_new_ship = False
        screen.fill((0, 0, 0))  # black background
        
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 2)  # white star, radius 2
            
        rocket_x = 50   # fixed X position (left edge)
        rocket_y = own_ship_pos  # vertical movement with arrows

        # --- Rocket Body (horizontal rectangle) ---
        pygame.draw.rect(screen, (200, 200, 255), (rocket_x, rocket_y - 20, 50, 40))

        # --- Rocket Nose (triangle pointing right) ---
        pygame.draw.polygon(screen, (180, 0, 0), [
            (rocket_x + 50, rocket_y - 20),
            (rocket_x + 50, rocket_y + 20),
            (rocket_x + 70, rocket_y)
        ])

        # --- Rocket Fins (top and bottom) ---
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

        # --- Cockpit Window ---
        pygame.draw.circle(screen, (0, 150, 255), (rocket_x + 25, rocket_y), 8)

        # --- Thruster Flame (flickers, behind rocket) ---
        flame_length = random.randint(15, 30)
        pygame.draw.polygon(screen, (255, 140, 0), [
            (rocket_x, rocket_y - 20),
            (rocket_x, rocket_y + 20),
            (rocket_x - flame_length, rocket_y)
        ])



        
        for ship in ships:
            ship.show_ship(screen=screen)
            if ship.ship_reached_end():
                print("GAME OVER")
                running = False
                ships.remove(ship)
        # Draw laser on space pressed
        for laser in lasers[:]:
            pygame.draw.line(screen, (255,0,0), (laser[0], laser[1]), (laser[0]+laser_width, laser[1]), 10)
            laser[0] += 50
            if laser[0] >= 1850:
                circle_radius = 0
                explosion_y = laser[1]   # store the y position of THIS laser
                lasers.remove(laser)
                if np.abs(ship_pos - laser[1]) < max_blast_radius:
                    show_ship = False
            for ship in ships:
                if np.abs(laser[0] - ship.ship_pos_x) < 40 and np.abs(laser[1] - ship.ship_pos_y) < 40:
                    explosions.append(Explosion(pos_x=laser[0], pos_y=laser[1]))
                    ships.remove(ship)
                    lasers.remove(laser)
                    spawn_new_ship = True
            
        
        for blast in explosions:
            blast.draw_explosion(screen)
            if blast.circle_radius >= max_blast_radius:
                explosions.remove(blast)
            
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if own_ship_pos > 50:
                own_ship_pos = own_ship_pos - 10
        if keys[pygame.K_DOWN]:
            if own_ship_pos < 950:
                own_ship_pos = own_ship_pos + 10


        pygame.display.flip()

        # Event handling
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


# ---------------------------
# MAIN LOOP: restart on ENTER
# ---------------------------
# ---------------------------
# MAIN LOOP: restart on ENTER
# ---------------------------
while True:
    run_game()  # play one round
    
    # Game Over screen
    screen.fill((0, 0, 0))  # black background
    font = pygame.font.SysFont(None, 150)
    text_surface = font.render("YOU LOST - TRY AGAIN", True, (255, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    
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

