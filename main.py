"""
Main entry point for the RPG game.
"""
import pygame
import sys
import random
from constants import (BLACK, WHITE, GREEN, RED, GRAY, SCREEN_WIDTH, SCREEN_HEIGHT,
                      WORLD_MAP, BATTLE, PAUSE, SETTINGS,
                      TEXT_SPEED_SLOW, TEXT_SPEED_MEDIUM, TEXT_SPEED_FAST,
                      PAUSE_OPTIONS, SETTINGS_OPTIONS)
from game_states import GameStateManager
from entities.player import Player
from entities.enemy import Enemy
from systems.battle_system import BattleSystem

def handle_input(event, state_manager, battle_system, player, collided_enemy, 
                selected_pause_option, selected_settings_option, text_speed_setting):
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
    """
    # Handle keyboard input for pause menu
    if state_manager.is_pause:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_pause_option = (selected_pause_option - 1) % len(PAUSE_OPTIONS)
            elif event.key == pygame.K_DOWN:
                selected_pause_option = (selected_pause_option + 1) % len(PAUSE_OPTIONS)
            elif event.key == pygame.K_RETURN:
                if PAUSE_OPTIONS[selected_pause_option] == "SETTINGS":
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
                if SETTINGS_OPTIONS[selected_settings_option] == "TEXT SPEED":
                    # Cycle through text speed options
                    if text_speed_setting == TEXT_SPEED_SLOW:
                        text_speed_setting = TEXT_SPEED_MEDIUM
                    elif text_speed_setting == TEXT_SPEED_MEDIUM:
                        text_speed_setting = TEXT_SPEED_FAST
                    else:  # FAST
                        text_speed_setting = TEXT_SPEED_SLOW
                elif SETTINGS_OPTIONS[selected_settings_option] == "BACK":
                    state_manager.change_state(PAUSE)
                    selected_pause_option = 0  # Reset to first option in pause menu
        
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
                            battle_system.process_action(selected_action)
                    else:
                        # If message is still scrolling, pressing any key will display it immediately
                        battle_system.displayed_message = battle_system.full_message
                        battle_system.message_index = len(battle_system.full_message)


def draw_game(screen, state_manager, battle_system, all_sprites, enemies,
             selected_pause_option, selected_settings_option, text_speed_setting, font):
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
        font: The pygame font to use for text
    """
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
        # Draw the paused game in the background
        if state_manager.previous_state == WORLD_MAP:
            # First draw the world map
            screen.fill(BLACK)
            all_sprites.draw(screen)
            enemies.draw(screen)
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
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
        # Draw the paused game in the background (same as PAUSE)
        if state_manager.previous_state == WORLD_MAP:
            screen.fill(BLACK)
            all_sprites.draw(screen)
            enemies.draw(screen)
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
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
    
    # Pause menu options
    selected_pause_option = 0
    selected_settings_option = 0
    
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
                
            # Handle ESC key for pause menu (only when in WORLD_MAP)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state_manager.is_world_map:
                    state_manager.change_state(PAUSE)
                elif state_manager.is_pause:
                    state_manager.return_to_previous()
                elif state_manager.is_settings:
                    state_manager.change_state(PAUSE)
                    selected_pause_option = 0  # Reset to first option in pause menu
            
            handle_input(event, state_manager, battle_system, player, collided_enemy, 
                         selected_pause_option, selected_settings_option, text_speed_setting)
        
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
                if pygame.key.get_pressed()[pygame.K_RETURN]:
                    # Only remove enemy if player won (not if they fled)
                    if battle_system.victory:
                        collided_enemy.kill()
                    
                    # Return to world map
                    state_manager.change_state(WORLD_MAP)
                    player.reset_position()
                    battle_system = None
        
        # Draw the current game state
        draw_game(screen, state_manager, battle_system, all_sprites, enemies, 
                 selected_pause_option, selected_settings_option, text_speed_setting, font)
        
        # Flip the display
        pygame.display.flip()
        
        # Maintain 60 frames per second
        clock.tick(60)
    
    # Quit the game
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()