"""
Main entry point for the RPG game.
"""
import pygame
import sys
import random
from constants import (
    BLACK, WHITE, GREEN, RED, GRAY, YELLOW, SCREEN_WIDTH, SCREEN_HEIGHT,
    ORIGINAL_WIDTH, ORIGINAL_HEIGHT, 
    WORLD_MAP, BATTLE, PAUSE, SETTINGS, INVENTORY,
    TEXT_SPEED_SLOW, TEXT_SPEED_MEDIUM, TEXT_SPEED_FAST,
    PAUSE_OPTIONS, SETTINGS_OPTIONS, BATTLE_OPTIONS,
    RESOLUTION_OPTIONS, DISPLAY_MODE_OPTIONS, 
    DISPLAY_WINDOWED, DISPLAY_BORDERLESS, DISPLAY_FULLSCREEN
)
from game_states import GameStateManager
from entities.player import Player
from entities.enemy import Enemy
from systems.battle_system import BattleSystem
from systems.inventory import get_item_effect
from systems.map_system import MapSystem, MapArea
import utils
from map_initialization import initialize_maps

"""
Updated handle_input function in main.py to support spell casting.
"""

def apply_display_settings(settings_manager, map_system=None):
    """
    Apply display settings based on current settings and update all entities.
    
    Args:
        settings_manager: The settings manager instance
        map_system: The map system containing all entities (optional)
        
    Returns:
        pygame.Surface: The new display surface
    """
    # Get current settings
    width, height = settings_manager.get_resolution()
    display_mode = settings_manager.get_display_mode()
    
    # Set the appropriate display mode flags
    flags = 0
    if display_mode == DISPLAY_FULLSCREEN:
        flags = pygame.FULLSCREEN
    elif display_mode == DISPLAY_BORDERLESS:
        flags = pygame.NOFRAME
    
    # Apply the new display settings
    screen = pygame.display.set_mode((width, height), flags)
    
    # If we have a map system, update all entities in all maps
    if map_system and hasattr(map_system, 'maps'):
        # Get all maps
        for map_id, map_area in map_system.maps.items():
            # Scale all entities in this map
            for entity in map_area.entities:
                if hasattr(entity, 'update_scale'):
                    entity.update_scale(width, height)
    
    return screen

def handle_input(event, state_manager, battle_system, player, collided_enemy, 
                selected_pause_option, selected_settings_option, text_speed_setting,
                selected_inventory_option, inventory_mode):
    """
    Handle user input based on the current game state.
    
    Args:
        event: The pygame event to process
        state_manager: The game state manager
        battle_system: The current battle system (if in battle)
        player: The player entity
        collided_enemy: The enemy collided with (if in battle)
        selected_pause_option: The currently selected pause menu option
        selected_settings_option: The currently selected settings menu option
        text_speed_setting: The current text speed setting
        selected_inventory_option: The currently selected inventory item
        inventory_mode: Whether viewing inventory from pause menu or battle
    """
    # Flag to track if text_speed_setting was modified
    text_speed_changed = False
    
    # Handle keyboard input for inventory screen
    if state_manager.is_inventory:
        if event.type == pygame.KEYDOWN:
            item_names = player.inventory.get_item_names()
            # Add BACK as the last option
            options = item_names + ["BACK"]
            
            if event.key == pygame.K_UP:
                selected_inventory_option = (selected_inventory_option - 1) % len(options)
            elif event.key == pygame.K_DOWN:
                selected_inventory_option = (selected_inventory_option + 1) % len(options)
            elif event.key == pygame.K_RETURN:
                selected_item = options[selected_inventory_option]
                
                if selected_item == "BACK":
                    # Return to previous state
                    state_manager.return_to_previous()
                else:
                    # Use the item based on context
                    if inventory_mode == "pause":
                        # Using item from pause menu (only healing items work here)
                        success, message = player.use_item(selected_item)
                        # TODO: Display message to user
                    elif inventory_mode == "battle" and battle_system:
                        # Using item in battle
                        if selected_item == "SCAN LENS":
                            # Scan the enemy
                            success, message = player.use_item(selected_item, battle_system.enemy)
                            if success:
                                battle_system.set_message(message)
                                # End player's turn after using an item
                                battle_system.turn = 1
                                battle_system.enemy_turn_processed = False
                                # Return to battle screen after using item
                                state_manager.return_to_previous()
                        else:
                            # Use the item (like POTION)
                            success, message = player.use_item(selected_item)
                            if success:
                                battle_system.set_message(message)
                                # End player's turn after using an item
                                battle_system.turn = 1
                                battle_system.enemy_turn_processed = False
                                # Return to battle screen after using item
                                state_manager.return_to_previous()

    # Handle keyboard input for pause menu
    elif state_manager.is_pause:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_pause_option = (selected_pause_option - 1) % len(PAUSE_OPTIONS)
            elif event.key == pygame.K_DOWN:
                selected_pause_option = (selected_pause_option + 1) % len(PAUSE_OPTIONS)
            elif event.key == pygame.K_RETURN:
                if PAUSE_OPTIONS[selected_pause_option] == "ITEMS":
                    state_manager.change_state(INVENTORY)
                    selected_inventory_option = 0  # Reset selection
                    inventory_mode = "pause"  # Set mode for context
                elif PAUSE_OPTIONS[selected_pause_option] == "SETTINGS":
                    state_manager.change_state(SETTINGS)
                    selected_settings_option = 0  # Reset selection
                elif PAUSE_OPTIONS[selected_pause_option] == "CLOSE":
                    state_manager.return_to_previous()
                    
    # Handle keyboard input for settings menu
    elif state_manager.is_settings:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_settings_option = (selected_settings_option - 1) % len(SETTINGS_OPTIONS)
            elif event.key == pygame.K_DOWN:
                selected_settings_option = (selected_settings_option + 1) % len(SETTINGS_OPTIONS)
            elif event.key == pygame.K_RETURN:
                # The first option (index 0) should be TEXT SPEED
                if selected_settings_option == 0:
                    # Cycle through text speed options
                    if text_speed_setting == TEXT_SPEED_SLOW:
                        text_speed_setting = TEXT_SPEED_MEDIUM
                    elif text_speed_setting == TEXT_SPEED_MEDIUM:
                        text_speed_setting = TEXT_SPEED_FAST
                    else:  # FAST
                        text_speed_setting = TEXT_SPEED_SLOW
                    
                    # Indicate that text speed was changed
                    text_speed_changed = True
                    
                    # Update battle system if we're in battle
                    if battle_system:
                        battle_system.set_text_speed(text_speed_setting)
                
                # The second option (index 1) should be BACK
                elif selected_settings_option == 1:
                    state_manager.return_to_previous()
        
    # Handle keyboard input for battle
    elif state_manager.is_battle and battle_system:
        if not battle_system.battle_over:
            if event.type == pygame.KEYDOWN:
                # Handle spell menu navigation if active
                if battle_system.in_spell_menu:
                    # Get spells list
                    spell_options = player.spellbook.get_spell_names() + ["BACK"]
                    
                    if event.key == pygame.K_UP:
                        battle_system.selected_spell_option = (battle_system.selected_spell_option - 1) % len(spell_options)
                    elif event.key == pygame.K_DOWN:
                        battle_system.selected_spell_option = (battle_system.selected_spell_option + 1) % len(spell_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        selected_spell = spell_options[battle_system.selected_spell_option]
                        
                        if selected_spell == "BACK":
                            # Return to main battle menu
                            battle_system.in_spell_menu = False
                        else:
                            # Try to cast the spell
                            success = battle_system.cast_spell(selected_spell)
                            if not success:
                                # If cast failed, stay in spell menu (message already set)
                                pass
                            else:
                                # Return to battle screen after successful cast
                                battle_system.in_spell_menu = False
                    
                    # Also exit spell menu with ESCAPE key
                    elif event.key == pygame.K_ESCAPE:
                        battle_system.in_spell_menu = False
                
                # Handle skill menu navigation if active
                if battle_system.in_skill_menu:
                    # Get skills list
                    skill_options = player.skillset.get_skill_names() + ["BACK"]
                    
                    if event.key == pygame.K_UP:
                        battle_system.selected_skill_option = (battle_system.selected_skill_option - 1) % len(skill_options)
                    elif event.key == pygame.K_DOWN:
                        battle_system.selected_skill_option = (battle_system.selected_skill_option + 1) % len(skill_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        selected_skill = skill_options[battle_system.selected_skill_option]
                        
                        if selected_skill == "BACK":
                            # Return to main battle menu
                            battle_system.in_skill_menu = False
                        else:
                            # Try to use the skill
                            success = battle_system.use_skill(selected_skill)
                            if not success:
                                # If use failed, stay in skill menu (message already set)
                                pass
                            else:
                                # Return to battle screen after successful use
                                battle_system.in_skill_menu = False
                    
                    # Also exit skill menu with ESCAPE key
                    elif event.key == pygame.K_ESCAPE:
                        battle_system.in_skill_menu = False

                # Handle regular battle options when not in spell or skill menu
                elif battle_system.turn == 0 and not battle_system.in_spell_menu:  # Player's turn and not in spell menu
                    # Only accept inputs when text is fully displayed
                    if battle_system.message_index >= len(battle_system.full_message):
                        if event.key == pygame.K_UP:
                            # Move up in the same column with wrap-around
                            if battle_system.selected_option >= 4:  # Right column
                                # Move up in right column (wrap to bottom if at top)
                                current_position = battle_system.selected_option - 4
                                new_position = (current_position - 1) % 4
                                battle_system.selected_option = 4 + new_position
                            else:  # Left column
                                # Move up in left column (wrap to bottom if at top)
                                battle_system.selected_option = (battle_system.selected_option - 1) % 4
                        elif event.key == pygame.K_DOWN:
                            # Move down in the same column with wrap-around
                            if battle_system.selected_option >= 4:  # Right column
                                # Move down in right column
                                current_position = battle_system.selected_option - 4
                                new_position = (current_position + 1) % 4
                                battle_system.selected_option = 4 + new_position
                            else:  # Left column
                                # Move down in left column
                                battle_system.selected_option = (battle_system.selected_option + 1) % 4
                        elif event.key == pygame.K_LEFT:
                            # Move to left column from right, or wrap around to right column from left
                            if battle_system.selected_option >= 4:  # Right column to left
                                battle_system.selected_option -= 4
                            else:  # Left column to right (wrap around)
                                battle_system.selected_option += 4
                        elif event.key == pygame.K_RIGHT:
                            # Move to right column from left, or wrap around to left column from right
                            if battle_system.selected_option < 4:  # Left column to right
                                battle_system.selected_option += 4
                            else:  # Right column to left (wrap around)
                                battle_system.selected_option -= 4
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            selected_action = battle_system.battle_options[battle_system.selected_option]
                            
                            # Handle the actions
                            if selected_action == "MAGIC":
                                battle_system.in_spell_menu = True
                                battle_system.selected_spell_option = 0
                            elif selected_action == "ITEM":
                                state_manager.change_state(INVENTORY)
                                selected_inventory_option = 0
                                inventory_mode = "battle"
                            elif selected_action == "MOVE":
                                # For now, MOVE uses the same functionality as RUN
                                battle_system.process_action("RUN")
                            elif selected_action == "SKILL":
                                battle_system.in_skill_menu = True
                                battle_system.selected_skill_option = 0
                            elif selected_action == "ULTIMATE":
                                # Placeholder for ULTIMATE (not yet implemented)
                                battle_system.set_message("Ultimate abilities not yet implemented.")
                            elif selected_action == "STATUS":
                                # Placeholder for STATUS (not yet implemented)
                                battle_system.set_message("Status screen not yet implemented.")
                            else:
                                # ATTACK and DEFEND remain the same
                                battle_system.process_action(selected_action)
                    else:
                        # If message is still scrolling, pressing any key will display it immediately
                        battle_system.displayed_message = battle_system.full_message
                        battle_system.message_index = len(battle_system.full_message)
                        
                # Check if battle has ended and player pressed ENTER to continue
                if battle_system.battle_over and battle_system.message_index >= len(battle_system.full_message):
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Only remove enemy if player won (not if they fled)
                        if battle_system.victory:
                            collided_enemy.kill()
                        
                        # Return to world map
                        state_manager.change_state(WORLD_MAP)
                        player.reset_position()
                        battle_system = None

    # Return updated values including the text_speed_setting
    return selected_pause_option, selected_settings_option, selected_inventory_option, inventory_mode, battle_system, text_speed_setting

def handle_settings_input(event, state_manager, selected_settings_option, settings_manager):
    """
    Handle input in the settings menu for resolution and display mode changes.
    
    Args:
        event: The pygame event
        state_manager: The game state manager
        selected_settings_option: The currently selected settings option
        settings_manager: The settings manager instance
        
    Returns:
        tuple: (new selected_settings_option, bool indicating if display settings changed)
    """
    display_changed = False
    new_selected_option = selected_settings_option
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            new_selected_option = (selected_settings_option - 1) % len(SETTINGS_OPTIONS)
        elif event.key == pygame.K_DOWN:
            new_selected_option = (selected_settings_option + 1) % len(SETTINGS_OPTIONS)
        elif event.key == pygame.K_RETURN:
            # TEXT SPEED option
            if selected_settings_option == 0:
                current_speed = settings_manager.get_text_speed()
                if current_speed == TEXT_SPEED_SLOW:
                    settings_manager.set_text_speed(TEXT_SPEED_MEDIUM)
                elif current_speed == TEXT_SPEED_MEDIUM:
                    settings_manager.set_text_speed(TEXT_SPEED_FAST)
                else:  # FAST
                    settings_manager.set_text_speed(TEXT_SPEED_SLOW)
            
            # RESOLUTION option
            elif selected_settings_option == 1:
                try:
                    # Get current resolution and find its index in the options list
                    current_res = settings_manager.settings["resolution"]
                    current_idx = RESOLUTION_OPTIONS.index(current_res)
                    
                    # Move to next resolution option
                    next_idx = (current_idx + 1) % len(RESOLUTION_OPTIONS)
                    settings_manager.set_resolution(RESOLUTION_OPTIONS[next_idx])
                    
                    # Set flag to change display
                    display_changed = True
                except Exception as e:
                    print(f"Error changing resolution: {e}")
            
            # DISPLAY MODE option
            elif selected_settings_option == 2:
                try:
                    # Get current display mode and find its index
                    current_mode = settings_manager.get_display_mode()
                    current_idx = DISPLAY_MODE_OPTIONS.index(current_mode)
                    
                    # Move to next mode option
                    next_idx = (current_idx + 1) % len(DISPLAY_MODE_OPTIONS)
                    settings_manager.set_display_mode(DISPLAY_MODE_OPTIONS[next_idx])
                    
                    # Set flag to change display
                    display_changed = True
                except Exception as e:
                    print(f"Error changing display mode: {e}")
            
            # BACK option
            elif selected_settings_option == 3:
                state_manager.return_to_previous()
    
    return new_selected_option, display_changed

def draw_settings_menu(screen, settings_manager, selected_settings_option, font):
    """
    Draw the settings menu with resolution and display mode options.
    
    Args:
        screen: The pygame surface to draw on
        settings_manager: The settings manager instance
        selected_settings_option: The currently selected option
        font: The font to use for text
    """
    from utils import scale_position, scale_dimensions
    from constants import ORIGINAL_WIDTH, ORIGINAL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY
    
    try:
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black (50% opacity)
        screen.blit(overlay, (0, 0))
        
        # Scale menu position and size
        menu_x, menu_y = scale_position(SCREEN_WIDTH//2, 200, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        option_x, option_y_base = scale_position(SCREEN_WIDTH//2 - 100, 250, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        option_spacing = int(40 * (current_height / ORIGINAL_HEIGHT))
        
        # Draw settings menu title
        menu_title = font.render("SETTINGS", True, WHITE)
        title_x = menu_x - menu_title.get_width()//2
        screen.blit(menu_title, (title_x, menu_y))
        
        # Draw TEXT SPEED option with current setting
        current_speed = settings_manager.get_text_speed()
        if selected_settings_option == 0:
            option_text = font.render(f"> TEXT SPEED: {current_speed}", True, WHITE)
        else:
            option_text = font.render(f"  TEXT SPEED: {current_speed}", True, GRAY)
        screen.blit(option_text, (option_x, option_y_base))
        
        # Draw RESOLUTION option with current setting
        current_res = settings_manager.settings["resolution"]
        if selected_settings_option == 1:
            option_text = font.render(f"> RESOLUTION: {current_res}", True, WHITE)
        else:
            option_text = font.render(f"  RESOLUTION: {current_res}", True, GRAY)
        screen.blit(option_text, (option_x, option_y_base + option_spacing))
        
        # Draw DISPLAY MODE option with current setting
        current_mode = settings_manager.get_display_mode()
        if selected_settings_option == 2:
            option_text = font.render(f"> DISPLAY MODE: {current_mode}", True, WHITE)
        else:
            option_text = font.render(f"  DISPLAY MODE: {current_mode}", True, GRAY)
        screen.blit(option_text, (option_x, option_y_base + option_spacing * 2))
        
        # Draw BACK option
        if selected_settings_option == 3:
            option_text = font.render(f"> BACK", True, WHITE)
        else:
            option_text = font.render(f"  BACK", True, GRAY)
        screen.blit(option_text, (option_x, option_y_base + option_spacing * 3))
    except Exception as e:
        print(f"Error drawing settings menu: {e}")
        # Draw a simple error message if something goes wrong
        error_msg = font.render("Error drawing settings menu.", True, WHITE)
        screen.blit(error_msg, (50, 50))

def draw_game(screen, state_manager, battle_system, map_system,
             selected_pause_option, selected_settings_option, text_speed_setting,
             selected_inventory_option, inventory_mode, font, settings_manager):
    """
    Draw the game based on the current state.
    
    Args:
        screen: The pygame surface to draw on
        state_manager: The game state manager
        battle_system: The current battle system (if in battle)
        map_system: The map system
        selected_pause_option: The currently selected pause menu option
        selected_settings_option: The currently selected settings menu option
        text_speed_setting: The current text speed setting
        selected_inventory_option: The currently selected inventory item
        inventory_mode: Whether viewing inventory from pause or battle
        font: The pygame font to use for text
        settings_manager: The settings manager
    """
    # First clear the screen - this is essential
    screen.fill(BLACK)
    
    if state_manager.is_world_map:
        # Draw the current map, which handles its own background, entities, and boundaries
        current_map = map_system.get_current_map()
        current_map.draw(screen)
        
    elif state_manager.is_battle:
        if battle_system:
            battle_system.draw(screen)
            
    elif state_manager.is_pause:
        # First draw the underlying world map
        current_map = map_system.get_current_map()
        current_map.draw(screen)
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black (50% opacity)
        screen.blit(overlay, (0, 0))
        
        # Use the scaling utility for pause menu
        from utils import scale_position
        
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600
        
        # Scale menu positions
        menu_title_pos = scale_position(SCREEN_WIDTH//2, 200, original_width, original_height, current_width, current_height)
        option_base_pos = scale_position(SCREEN_WIDTH//2 - 50, 250, original_width, original_height, current_width, current_height)
        option_spacing = int(40 * (current_height / original_height))
        
        # Draw pause menu
        menu_title = font.render("PAUSE", True, WHITE)
        screen.blit(menu_title, (menu_title_pos[0] - menu_title.get_width()//2, menu_title_pos[1]))
        
        for i, option in enumerate(PAUSE_OPTIONS):
            if i == selected_pause_option:
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
            screen.blit(option_text, (option_base_pos[0], option_base_pos[1] + i * option_spacing))
            
    elif state_manager.is_settings:
        # First draw the underlying world map
        current_map = map_system.get_current_map()
        current_map.draw(screen)
        
        # Draw the settings menu with resolution options
        draw_settings_menu(screen, settings_manager, selected_settings_option, font)
        
    elif state_manager.is_inventory:
        # First draw the underlying world map
        current_map = map_system.get_current_map()
        current_map.draw(screen)
        
        # Use scaling utility for inventory menu
        from utils import scale_position, scale_dimensions
        
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black (50% opacity)
        screen.blit(overlay, (0, 0))
        
        # Scale inventory menu positions
        menu_title_pos = scale_position(SCREEN_WIDTH//2, 150, original_width, original_height, current_width, current_height)
        header_pos = scale_position(SCREEN_WIDTH//2 - 200, 190, original_width, original_height, current_width, current_height)
        line_start_pos = scale_position(SCREEN_WIDTH//2 - 200, 220, original_width, original_height, current_width, current_height)
        line_end_pos = scale_position(SCREEN_WIDTH//2 + 200, 220, original_width, original_height, current_width, current_height)
        item_base_pos = scale_position(SCREEN_WIDTH//2 - 200, 230, original_width, original_height, current_width, current_height)
        qty_pos_x = scale_position(SCREEN_WIDTH//2 - 50, 0, original_width, original_height, current_width, current_height)[0]
        desc_pos_x = scale_position(SCREEN_WIDTH//2 - 25, 0, original_width, original_height, current_width, current_height)[0]
        item_spacing = int(30 * (current_height / original_height))
        
        # Draw inventory menu
        menu_title = font.render("INVENTORY", True, WHITE)
        screen.blit(menu_title, (menu_title_pos[0] - menu_title.get_width()//2, menu_title_pos[1]))
        
        # Get a reference to the player from the current map
        current_map = map_system.get_current_map()
        player = None
        for entity in current_map.entities:
            if isinstance(entity, Player):
                player = entity
                break
        
        if player:
            # Get item names and add BACK option
            item_names = player.inventory.get_item_names()
            options = item_names + ["BACK"]
            
            # Draw inventory header
            header_text = font.render("ITEM           QTY   DESCRIPTION", True, WHITE)
            screen.blit(header_text, (header_pos[0], header_pos[1]))
            
            # Draw horizontal line under header
            pygame.draw.line(screen, WHITE, line_start_pos, line_end_pos)
            
            # Draw each item with quantity and description
            for i, item_name in enumerate(item_names):
                # Get the item and its quantity
                quantity = player.inventory.get_quantity(item_name)
                item = get_item_effect(item_name)
                
                # Prepare display text with highlighted selection
                if i == selected_inventory_option:
                    name_text = font.render(f"> {item_name}", True, WHITE)
                else:
                    name_text = font.render(f"  {item_name}", True, GRAY)
                    
                # Draw item name
                screen.blit(name_text, (item_base_pos[0], item_base_pos[1] + i * item_spacing))
                
                # Draw quantity
                qty_text = font.render(f"{quantity:2d}", True, GRAY if i != selected_inventory_option else WHITE)
                screen.blit(qty_text, (qty_pos_x, item_base_pos[1] + i * item_spacing))
                
                # Draw description (truncated if needed)
                if item:
                    desc = item.description
                    if len(desc) > 30:
                        desc = desc[:27] + "..."
                    desc_text = font.render(desc, True, GRAY if i != selected_inventory_option else WHITE)
                    screen.blit(desc_text, (desc_pos_x, item_base_pos[1] + i * item_spacing))
            
            # Draw BACK option
            if len(options) - 1 == selected_inventory_option:
                back_text = font.render(f"> BACK", True, WHITE)
            else:
                back_text = font.render(f"  BACK", True, GRAY)
            screen.blit(back_text, (item_base_pos[0], item_base_pos[1] + len(item_names) * item_spacing))
            
            # Draw context-sensitive help
            help_y = item_base_pos[1] + (len(options) + 1) * item_spacing
            if inventory_mode == "pause":
                help_text = font.render("Select an item to use outside of battle", True, YELLOW)
            else:
                help_text = font.render("Select an item to use in battle", True, YELLOW)
            screen.blit(help_text, (item_base_pos[0], help_y))


def main():
    # Initialize Pygame
    pygame.init()
    
    # Initialize settings manager
    from systems.settings_manager import SettingsManager
    settings_manager = SettingsManager()
    
    # Create the screen with initial settings (no map_system yet)
    screen = apply_display_settings(settings_manager, None)  # Pass None for now
    pygame.display.set_caption("My RPG Game")
    
    # Initialize fonts - these will be recreated when resolution changes
    pygame.font.init()
    current_width, current_height = screen.get_size()
    font_size = utils.scale_font_size(24, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
    font = pygame.font.SysFont('Arial', font_size)
    pygame.display.set_caption("My RPG Game")
    
    # Clock for controlling the frame rate
    clock = pygame.time.Clock()
    
    # Game state management
    state_manager = GameStateManager()
    
    # Game settings from settings manager
    text_speed_setting = settings_manager.get_text_speed()
    
    # Menu options
    selected_pause_option = 0
    selected_settings_option = 0
    selected_inventory_option = 0
    inventory_mode = "pause"
    
    # Create a player using original dimensions
    player = Player(ORIGINAL_WIDTH // 2, ORIGINAL_HEIGHT // 2)
    
    # Initialize map system with the player
    map_system = initialize_maps(player)
    
    # Now that map_system exists, make sure player is properly scaled for current resolution
    player.update_scale(current_width, current_height)

    screen = apply_display_settings(settings_manager, map_system)
    
    # Battle system (will be initialized when battle starts)
    battle_system = None
    collided_enemy = None
    
    # Main game loop
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle ESC key for pause menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state_manager.is_world_map:
                    state_manager.change_state(PAUSE)
                elif state_manager.is_pause:
                    state_manager.return_to_previous()
                elif state_manager.is_settings or state_manager.is_inventory:
                    # Always return to the previous state (either PAUSE or BATTLE)
                    state_manager.return_to_previous()
            
            # Handle settings input specifically for resolution and display mode
            if state_manager.is_settings:
                new_selected_option, display_changed = handle_settings_input(
                    event, state_manager, selected_settings_option, settings_manager
                )
                selected_settings_option = new_selected_option
                
                # If display settings changed, update the screen and all entities
                if display_changed:
                    try:
                        screen = apply_display_settings(settings_manager, map_system)
                        # Recreate font with scaled size
                        font_size = utils.scale_font_size(24, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, 
                                                        *settings_manager.get_resolution())
                        font = pygame.font.SysFont('Arial', font_size)
                    except Exception as e:
                        print(f"Error applying display settings: {e}")
            else:
                # Handle input for all other game states including text speed toggling
                updated_values = handle_input(
                    event, state_manager, battle_system, player, collided_enemy, 
                    selected_pause_option, selected_settings_option, text_speed_setting,
                    selected_inventory_option, inventory_mode
                )
                
                # Unpack the returned values and update our local variables
                selected_pause_option, selected_settings_option, selected_inventory_option, inventory_mode, battle_system_update, new_text_speed = updated_values
                
                # Update text_speed_setting if it was changed
                text_speed_setting = new_text_speed
                settings_manager.set_text_speed(text_speed_setting)
                
                # Update battle_system if it was modified
                if battle_system_update is not None:
                    battle_system = battle_system_update
        
        # Update game logic based on current state
        if state_manager.is_world_map:
            # Get the current map
            current_map = map_system.get_current_map()
            
            # Update player with current map for boundary checking
            collided_enemy = player.update(current_map.enemies, current_map)
            
            if collided_enemy:
                # Switch to battle state
                state_manager.change_state(BATTLE)
                battle_system = BattleSystem(player, collided_enemy, text_speed_setting)
            else:
                # Only check for map transitions if no battle started
                map_transition = current_map.update(player)
                if map_transition:
                    new_map, entry_side = map_transition
                    map_system.transition_player(player, new_map, entry_side)
            
        elif state_manager.is_battle and battle_system:
            # Update battle animations and process turns
            battle_system.update_animations()
            
            # Check if battle is over and return to world map
            if battle_system.battle_over and battle_system.message_index >= len(battle_system.full_message):
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    # Only remove enemy if player won (not if they fled)
                    if battle_system.victory:
                        # Get current map and remove the defeated enemy
                        current_map = map_system.get_current_map()
                        battle_system.enemy.kill()
                    
                    # Return to world map
                    state_manager.change_state(WORLD_MAP)
                    player.reset_position()
                    battle_system = None
        
        # Draw the current game state
        draw_game(
            screen, state_manager, battle_system, map_system, 
            selected_pause_option, selected_settings_option, text_speed_setting,
            selected_inventory_option, inventory_mode, font, settings_manager
        )
        
        # Flip the display
        pygame.display.flip()
        
        # Maintain 60 frames per second
        clock.tick(60)
    
    # Save settings before quitting
    settings_manager.save_settings()
    
    # Quit the game
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()