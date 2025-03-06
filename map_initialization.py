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