"""
Map initialization for the RPG game.
"""
from systems.map_system import MapSystem, MapArea
from entities.enemy import Enemy
from entities.npc import NPC
from data.encounter_pools import initialize_encounter_pools
import random
import pygame
from constants import BLACK, BLUE, GREEN, RED, PURPLE, WHITE, ORIGINAL_WIDTH, ORIGINAL_HEIGHT

def initialize_maps(player):
    """
    Create and initialize all map areas.
    
    Args:
        player: The player entity to place on the initial map
        
    Returns:
        MapSystem: The initialized map system
    """
    # Initialize encounter pools
    encounter_manager = initialize_encounter_pools()
    
    # Create the map system with the encounter manager
    map_system = MapSystem(encounter_manager)
    
    # Create map areas with different background colors for visual distinction
    center_map = MapArea("Debug Area - Center", BLACK, "center")
    north_map = MapArea("Debug Area - North", (0, 0, 20), "north")  # Very dark blue
    east_map = MapArea("Debug Area - East", (20, 0, 0), "east")   # Very dark red
    south_map = MapArea("Debug Area - South", (0, 20, 0), "south")  # Very dark green
    west_map = MapArea("Debug Area - West", (20, 0, 20), "west")  # Very dark purple
    
    # Set encounter chances
    center_map.encounter_chance = 0.15  # 15% chance per step
    north_map.encounter_chance = 0.10   # 10% chance per step
    east_map.encounter_chance = 0.20    # 20% chance per step (rat-infested)
    south_map.encounter_chance = 0.05   # 5% chance per step
    west_map.encounter_chance = 0.15    # 15% chance per step
    
    # Add maps to the system
    map_system.add_map("center", center_map)
    map_system.add_map("north", north_map)
    map_system.add_map("east", east_map)
    map_system.add_map("south", south_map)
    map_system.add_map("west", west_map)
    
    # Connect maps
    map_system.connect_maps("center", "north", "north")
    map_system.connect_maps("center", "east", "east")
    map_system.connect_maps("center", "south", "south")
    map_system.connect_maps("center", "west", "west")
    
    # Get current screen dimensions
    current_width, current_height = pygame.display.get_surface().get_size()
    
    # Scale player to match current resolution
    player.update_scale(current_width, current_height)
    
    # Add test NPC with dialog
    test_dialogue = [
        "This is sample text!",
        "I've heard there are more monsters around these days.",
        "Be careful, sometimes you'll encounter multiple enemies at once!",
        "The east area is particularly dangerous with all those rats..."
    ]

    # Position NPC in the top right area
    npc_x = ORIGINAL_WIDTH * 0.75
    npc_y = ORIGINAL_HEIGHT * 0.3

    test_npc = NPC(npc_x, npc_y, 32, 48, WHITE, "Test NPC", test_dialogue)

    # Scale NPC to match current resolution
    test_npc.update_scale(current_width, current_height)

    # Add NPC to north map
    north_map.add_entity(test_npc)
    
    # Add player to center map
    center_map.add_entity(player)
    
    # Set center as current map
    map_system.set_current_map("center")
    
    return map_system

def add_random_enemies(map_area, count):
    """
    Add random enemies to a map area.
    
    Args:
        map_area: The map area to add enemies to
        count: How many enemies to add
    """
    # Get current screen dimensions
    current_width, current_height = pygame.display.get_surface().get_size()
    
    for _ in range(count):
        # Create enemy at random position (with some margin from edges)
        # Use original resolution for position calculation
        margin = 100
        x = random.randint(margin, ORIGINAL_WIDTH - margin)
        y = random.randint(margin, ORIGINAL_HEIGHT - margin)
        
        # Create enemy
        enemy = Enemy(x, y)
        
        # Scale enemy to match current resolution
        enemy.update_scale(current_width, current_height)
        
        # Add to map
        map_area.add_enemy(enemy)


def update_main_game_loop(main_module_code):
    """
    Updates the main.py file to integrate the map system.
    This is a simplified way to show the needed changes - in practice
    you would directly modify the main.py file.
    
    Args:
        main_module_code: The current code from main.py
        
    Returns:
        str: The updated code
    """
    # Here we'd show the key modifications to make to main.py:
    changes = """
# In the imports section at the top:
from systems.map_system import MapSystem, MapArea
from map_initialization import initialize_maps

# Replace the creation of all_sprites and enemies groups in main():
# Instead of:
# enemies = pygame.sprite.Group()
# for _ in range(3):
#     enemy = Enemy.spawn_random()
#     enemies.add(enemy)
# all_sprites = pygame.sprite.Group()
# all_sprites.add(player)

# Use this:
map_system = initialize_maps(player)

# In the world map state update section:
if state_manager.is_world_map:
    # Get the current map
    current_map = map_system.get_current_map()
    
    # Update player and check for map transitions
    collided_enemy = player.update()
    
    # Check if player collided with enemy
    if collided_enemy:
        # Switch to battle state
        state_manager.change_state(BATTLE)
        battle_system = BattleSystem(player, collided_enemy, text_speed_setting)
    
    # Check for map transitions
    map_transition = current_map.update(player)
    if map_transition:
        new_map, entry_side = map_transition
        map_system.transition_player(player, new_map, entry_side)

# In the draw_game function, replace:
# if state_manager.is_world_map:
#     screen.fill(BLACK)
#     all_sprites.draw(screen)
#     enemies.draw(screen)

# With:
if state_manager.is_world_map:
    current_map = map_system.get_current_map()
    current_map.draw(screen)
"""
    return changes