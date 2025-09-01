# README DEVELOPER — Step 1

## Overview

The project grows in **tiny, beginner-friendly steps**.  
Step 0 was just a sketch of the end goal.  
Step 1 is the first real refactored: we split the game into three small files while still reusing the older `game_objects.py`.

At this stage we have:

* `settings.py` → **all constants in one place** (screen, colors, speeds)  
* `models.py` → **tiny typed data containers** (currently just `Laser`)  
* `game.py` → **main game loop**, commented for kids, calling into helper functions  
* `game_objects.py` → **legacy Ship + Explosion** (still used in Step 1, will be replaced later)  

---

## File Layout (Step 1)

```

.
├── settings.py         # Tunable constants (screen, rocket, lasers, UI)
├── models.py           # Lightweight dataclasses (Laser)
├── game\_objects.py     # Legacy Ship + Explosion (temporary)
├── game.py             # Main loop (orchestration + helpers)
└── README\_DEVELOPER.md # You are here

````

### game_objects.py

* `Ship`  
  - Spawns on the right and moves left  
  - Has random size and color  
  - Draws itself each frame (`show_ship`)  
  - Knows if it reached the left edge (`ship_reached_end`)  

* `Explosion`  
  - Expands a red circle around a hit  
  - Very simple, no animation stages yet  

This module will be **removed in Step 2** once we introduce proper `sprites.py`.

### game.py

Now orchestrates:

1. Setup (screen, stars, fonts)  
2. Create one `Ship` and the player rocket’s starting Y  
3. Loop:  
   - Handle quit and key events (shoot, spawn debug ship)  
   - Read held-down keys (up/down)  
   - Spawn new ships if flagged  
   - Draw background, player rocket, ships, lasers, explosions, score  
   - Detect collisions  
   - End round if a ship reaches the left edge  
4. Show Game Over screen and wait for Enter  
5. Restart  

---

## Coding Conventions

* **Type hints everywhere** (ints, tuples, lists).  
* **Docstrings** in Google style:  
  ```python
  def draw_and_move_lasers(surface: pygame.Surface, lasers: List[Laser]) -> None:
      """Draw each laser and move it rightward.
      
      Args:
          surface (pygame.Surface): Target surface.
          lasers (List[Laser]): List of active lasers to update.
      """
````

* **Constants** live only in `settings.py`.
* **Helper functions** keep `game.py` readable (`draw_star_field`, `draw_player_rocket`).
* **Beginner-friendly comments** explain *why*, not just *what*.

---

## Next Steps After Step 1

* Step 2 — Remove `game_objects.py`; introduce `sprites.py` (Player, Enemy, Explosion) and `ui.py` (score, Game Over).
* Step 3 — Add sound effects.
* Step 4 — Add menu screen and lives.

---

## Tips for Contributors

* Start by tweaking values in `settings.py` to see how gameplay changes.
* Avoid putting numbers directly in logic — if you need a new setting, add it to `settings.py`.
* Keep commits small and focused (e.g., “Add flame flicker”, “Adjust ship speed”).
* Remember: **Step 1 still depends on `game_objects.py`.** Don’t delete it until Step 2.

```
