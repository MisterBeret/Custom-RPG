"""
Main entry point for the RPG game.
"""
import pygame
import sys
import random
from constants import (BLACK, WHITE, GREEN, RED, GRAY, YELLOW, SCREEN_WIDTH, SCREEN_HEIGHT,
                      WORLD_MAP, BATTLE, PAUSE, SETTINGS, INVENTORY,
                      TEXT_SPEED_SLOW, TEXT_SPEED_MEDIUM, TEXT_SPEED_FAST,
                      PAUSE_OPTIONS, SETTINGS_OPTIONS, BATTLE_OPTIONS)
from game_states import GameStateManager
from entities.player import Player
from entities.enemy import Enemy
from systems.battle_system import BattleSystem
from systems.inventory import get_item_effect

# This is a comprehensive fix for the main.py file, focusing on the battle input handling
# and integrating it properly with our new state management system

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
                if battle_system.turn == 0:  # Player's turn
                    # Only accept inputs when text is fully displayed
                    if battle_system.message_index >= len(battle_system.full_message):
                        if event.key == pygame.K_UP:
                            battle_system.selected_option = (battle_system.selected_option - 1) % len(battle_system.battle_options)
                        elif event.key == pygame.K_DOWN:
                            battle_system.selected_option = (battle_system.selected_option + 1) % len(battle_system.battle_options)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            selected_action = battle_system.battle_options[battle_system.selected_option]
                            
                            # Handle the ITEMS action
                            if selected_action == "ITEMS":
                                state_manager.change_state(INVENTORY)
                                selected_inventory_option = 0  # Reset selection
                                inventory_mode = "battle"  # Set mode for context
                            else:
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


def draw_game(screen, state_manager, battle_system, all_sprites, enemies,
             selected_pause_option, selected_settings_option, text_speed_setting,
             selected_inventory_option, inventory_mode, font):
    """
    Draw the game based on the current state.
    
    Args:
        screen: The pygame surface to draw on
        state_manager: The game state manager
        battle_system: The current battle system (if in battle)
        all_sprites: The sprite group containing all sprites
        enemies: The sprite group containing enemies
        selected_pause_option: The currently selected pause menu option
        selected_settings_option: The currently selected settings menu option
        text_speed_setting: The current text speed setting
        selected_inventory_option: The currently selected inventory item
        inventory_mode: Whether viewing inventory from pause or battle
        font: The pygame font to use for text
    """
    # First clear the screen - this is essential
    screen.fill(BLACK)
    
    if state_manager.is_world_map:
        # Clear the screen
        screen.fill(BLACK)
        
        # Draw all sprites
        all_sprites.draw(screen)
        enemies.draw(screen)
        
    elif state_manager.is_battle:
        if battle_system:
            battle_system.draw(screen)
            
    elif state_manager.is_pause:
        # First draw the underlying state (world map or battle)
        if state_manager.previous_state == WORLD_MAP:
            # Draw world map
            all_sprites.draw(screen)
            enemies.draw(screen)
        elif state_manager.previous_state == BATTLE and battle_system:
            # Draw battle screen
            battle_system.draw(screen)
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black (50% opacity)
        screen.blit(overlay, (0, 0))
        
        # Draw pause menu
        menu_title = font.render("PAUSE", True, WHITE)
        screen.blit(menu_title, (SCREEN_WIDTH//2 - menu_title.get_width()//2, 200))
        
        for i, option in enumerate(PAUSE_OPTIONS):
            if i == selected_pause_option:
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
            screen.blit(option_text, (SCREEN_WIDTH//2 - 50, 250 + i*40))
            
    elif state_manager.is_settings:
        # First draw the underlying state (world map or battle)
        if state_manager.previous_state == WORLD_MAP:
            # Draw world map
            all_sprites.draw(screen)
            enemies.draw(screen)
        elif state_manager.previous_state == BATTLE and battle_system:
            # Draw battle screen
            battle_system.draw(screen)
        elif state_manager.previous_state == PAUSE:
            # If we came from pause, we need to draw what was under pause
            if state_manager.state_stack[0] == WORLD_MAP:
                all_sprites.draw(screen)
                enemies.draw(screen)
            elif state_manager.state_stack[0] == BATTLE and battle_system:
                battle_system.draw(screen)
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black (50% opacity)
        screen.blit(overlay, (0, 0))
        
        # Draw settings menu
        menu_title = font.render("SETTINGS", True, WHITE)
        screen.blit(menu_title, (SCREEN_WIDTH//2 - menu_title.get_width()//2, 200))
        
        # Draw TEXT SPEED option with current setting
        if selected_settings_option == 0:
            option_text = font.render(f"> TEXT SPEED: {text_speed_setting}", True, WHITE)
        else:
            option_text = font.render(f"  TEXT SPEED: {text_speed_setting}", True, GRAY)
        screen.blit(option_text, (SCREEN_WIDTH//2 - 100, 250))
        
        # Draw BACK option
        if selected_settings_option == 1:
            option_text = font.render(f"> {SETTINGS_OPTIONS[1]}", True, WHITE)
        else:
            option_text = font.render(f"  {SETTINGS_OPTIONS[1]}", True, GRAY)
        screen.blit(option_text, (SCREEN_WIDTH//2 - 100, 290))
        
    elif state_manager.is_inventory:
        # First draw the underlying state (world map or battle)
        if state_manager.previous_state == WORLD_MAP:
            # Draw world map
            all_sprites.draw(screen)
            enemies.draw(screen)
        elif state_manager.previous_state == BATTLE and battle_system:
            # Draw battle screen
            battle_system.draw(screen)
        elif state_manager.previous_state == PAUSE:
            # If we came from pause, we need to draw what was under pause
            if state_manager.state_stack[0] == WORLD_MAP:
                all_sprites.draw(screen)
                enemies.draw(screen)
            elif state_manager.state_stack[0] == BATTLE and battle_system:
                battle_system.draw(screen)
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black (50% opacity)
        screen.blit(overlay, (0, 0))
        
        # Draw inventory menu
        menu_title = font.render("INVENTORY", True, WHITE)
        screen.blit(menu_title, (SCREEN_WIDTH//2 - menu_title.get_width()//2, 150))
        
        # Get a reference to the player
        player = all_sprites.sprites()[0]  # Assuming player is the first sprite
        
        # Get item names and add BACK option
        item_names = player.inventory.get_item_names()
        options = item_names + ["BACK"]
        
        # Draw inventory header
        header_text = font.render("ITEM           QTY   DESCRIPTION", True, WHITE)
        screen.blit(header_text, (SCREEN_WIDTH//2 - 200, 190))
        
        # Draw horizontal line under header
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH//2 - 200, 220), (SCREEN_WIDTH//2 + 200, 220))
        
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
            screen.blit(name_text, (SCREEN_WIDTH//2 - 200, 230 + i*30))
            
            # Draw quantity
            qty_text = font.render(f"{quantity:2d}", True, GRAY if i != selected_inventory_option else WHITE)
            screen.blit(qty_text, (SCREEN_WIDTH//2 - 50, 230 + i*30))
            
            # Draw description (truncated if needed)
            if item:
                desc = item.description
                if len(desc) > 30:
                    desc = desc[:27] + "..."
                desc_text = font.render(desc, True, GRAY if i != selected_inventory_option else WHITE)
                screen.blit(desc_text, (SCREEN_WIDTH//2 - 25, 230 + i*30))
        
        # Draw BACK option
        if len(options) - 1 == selected_inventory_option:
            back_text = font.render(f"> BACK", True, WHITE)
        else:
            back_text = font.render(f"  BACK", True, GRAY)
        screen.blit(back_text, (SCREEN_WIDTH//2 - 200, 230 + len(item_names)*30))
        
        # Draw context-sensitive help
        if inventory_mode == "pause":
            help_text = font.render("Select an item to use outside of battle", True, YELLOW)
        else:
            help_text = font.render("Select an item to use in battle", True, YELLOW)
        screen.blit(help_text, (SCREEN_WIDTH//2 - 200, 230 + (len(options) + 1)*30))


def main():
    """
    Main function to run the game.
    """
    # Initialize Pygame
    pygame.init()
    
    # Create the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("My RPG Game")
    
    # Initialize fonts
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 24)
    
    # Clock for controlling the frame rate
    clock = pygame.time.Clock()
    
    # Game state management
    state_manager = GameStateManager()
    
    # Game settings
    text_speed_setting = TEXT_SPEED_FAST  # Default text speed
    
    # Menu options
    selected_pause_option = 0
    selected_settings_option = 0
    selected_inventory_option = 0  # New variable for inventory selection
    inventory_mode = "pause"       # New variable for inventory context
    
    # Create a player
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    # Create enemy group and add some enemies
    enemies = pygame.sprite.Group()
    for _ in range(3):  # Spawn 3 random enemies
        enemy = Enemy.spawn_random()
        enemies.add(enemy)
    
    # Create all sprites group and add player
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    
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
            
            # Handle input for all game states including text speed toggling
            updated_values = handle_input(
                event, state_manager, battle_system, player, collided_enemy, 
                selected_pause_option, selected_settings_option, text_speed_setting,
                selected_inventory_option, inventory_mode
            )
            
            # Unpack the returned values and update our local variables
            # Now expecting 6 values: the original 5 plus text_speed_setting
            selected_pause_option, selected_settings_option, selected_inventory_option, inventory_mode, battle_system_update, new_text_speed = updated_values
            
            # Update text_speed_setting if it was changed
            text_speed_setting = new_text_speed
            
            # Update battle_system if it was modified
            if battle_system_update is not None:
                battle_system = battle_system_update
        
        # Update game logic based on current state
        if state_manager.is_world_map:
            # Check if player collides with an enemy
            collided_enemy = player.update(enemies)
            if collided_enemy:
                # Switch to battle state
                state_manager.change_state(BATTLE)
                battle_system = BattleSystem(player, collided_enemy, text_speed_setting)
            
            enemies.update()
            
        elif state_manager.is_battle and battle_system:
            # Update battle animations and process turns
            battle_system.update_animations()
            
            # Check if battle is over and return to world map
            if battle_system.battle_over and battle_system.message_index >= len(battle_system.full_message):
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN]:
                    # Only remove enemy if player won (not if they fled)
                    if battle_system.victory:
                        collided_enemy.kill()
                    
                    # Return to world map
                    state_manager.change_state(WORLD_MAP)
                    player.reset_position()
                    battle_system = None
        
        # Draw the current game state
        draw_game(
            screen, state_manager, battle_system, all_sprites, enemies, 
            selected_pause_option, selected_settings_option, text_speed_setting,
            selected_inventory_option, inventory_mode, font
        )
        
        # Flip the display
        pygame.display.flip()
        
        # Maintain 60 frames per second
        clock.tick(60)
    
    # Quit the game
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()