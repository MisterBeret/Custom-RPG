import pygame
import os
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Game states
WORLD_MAP = 0
BATTLE = 1
PAUSE = 2
SETTINGS = 3

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My RPG Game")

# Initialize fonts
pygame.font.init()
font = pygame.font.SysFont('Arial', 24)

# Clock for controlling the frame rate
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Create a simple character (a green rectangle for now)
        self.image = pygame.Surface([32, 48])
        self.image.fill(GREEN)
        
        # Set the position
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Movement speed
        self.speed = 5
        
        # RPG Stats
        self.level = 1
        self.experience = 0
        self.max_level = 100
        
        # Battle stats
        self.max_hp = 10
        self.hp = 10
        self.attack = 1
        self.spd = 5  # Speed determines turn order
        self.defending = False
        
    def update(self, enemies=None):
        if game_state == WORLD_MAP:
            # Store the current position to revert if there's a collision
            previous_x = self.rect.x
            previous_y = self.rect.y
            
            # Get keyboard input
            keys = pygame.key.get_pressed()
            
            # Move the character based on key presses
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
            if keys[pygame.K_UP]:
                self.rect.y -= self.speed
            if keys[pygame.K_DOWN]:
                self.rect.y += self.speed
                
            # Keep player within screen bounds
            if self.rect.x < 0:
                self.rect.x = 0
            if self.rect.x > SCREEN_WIDTH - self.rect.width:
                self.rect.x = SCREEN_WIDTH - self.rect.width
            if self.rect.y < 0:
                self.rect.y = 0
            if self.rect.y > SCREEN_HEIGHT - self.rect.height:
                self.rect.y = SCREEN_HEIGHT - self.rect.height
                
            # Check for collision with enemies
            if enemies:
                for enemy in enemies:
                    if self.rect.colliderect(enemy.rect):
                        return enemy  # Return the enemy we collided with
        
        return None  # No collision with enemies

    def reset_position(self):
        # Reset to center of screen after battle
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT // 2
        
    def take_damage(self, amount):
        # Apply damage reduction if defending
        if self.defending:
            amount = max(0, amount - 1)
            self.defending = False  # Reset defending status
        
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        
    def is_defeated(self):
        return self.hp <= 0
        
    def defend(self):
        self.defending = True

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Create a simple enemy (a red rectangle)
        self.image = pygame.Surface([32, 32])
        self.image.fill(RED)
        
        # Set the position
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Battle stats
        self.max_hp = 3
        self.hp = 3
        self.attack = 1
        self.spd = 3  # Speed determines turn order
        self.xp = 5   # XP awarded to player upon defeat
        
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
            
    def is_defeated(self):
        return self.hp <= 0

class BattleSystem:
    def __init__(self, player, enemy, text_speed_setting):
        self.player = player
        self.enemy = enemy
        
        # Determine who goes first based on speed
        if player.spd >= enemy.spd:
            self.turn = 0  # Player's turn
            self.first_message = "Battle started! You move first!"
        else:
            self.turn = 1  # Enemy's turn
            self.first_message = "Battle started! Enemy moves first!"
            
        self.full_message = self.first_message
        self.displayed_message = ""
        self.message_index = 0
        self.displayed_message = ""
        self.message_index = 0
        
        # Text speed based on global setting
        if text_speed_setting == "SLOW":
            self.text_speed = 1
        elif text_speed_setting == "MEDIUM":
            self.text_speed = 2
        else:  # FAST
            self.text_speed = 4
            
        self.text_timer = 0
        self.battle_options = ["ATTACK", "DEFEND", "RUN"]
        self.selected_option = 0
        self.battle_over = False
        self.victory = False
        self.pending_victory = False
        self.fled = False
        
        # Add a delay timer for action transitions
        self.action_delay = 0
        self.action_delay_duration = 30  # Wait 0.5 seconds after message completes
        
        # Add a flag to prevent multiple enemy attacks
        self.enemy_turn_processed = False
        
        # Message log to store recent battle messages
        self.message_log = [self.first_message]
        self.max_log_size = 3  # Number of messages to keep in the log
        
        # Animation properties
        self.player_pos = (200, 400)
        self.enemy_pos = (550, 300)
        self.player_attacking = False
        self.enemy_attacking = False
        self.player_fleeing = False
        self.animation_timer = 0
        self.animation_duration = 20  # frames
        self.flee_animation_duration = 40  # longer animation for fleeing
        
        # Pending values for delayed application
        self.pending_damage = 0
        self.original_damage = 0
        self.pending_message = ""
        
    def process_action(self, action):
        if self.turn == 0:  # Player's turn
            if action == "ATTACK":
                # Start player attack animation
                self.player_attacking = True
                self.animation_timer = 0
                
                # Process damage but don't set message yet
                damage = self.player.attack
                self.enemy.take_damage(damage)
                
                # Store the message for later display after animation
                if self.enemy.is_defeated():
                    self.pending_message = f"You attacked for {damage} damage! You defeated the enemy!"
                    self.pending_victory = True
                else:
                    self.pending_message = f"You attacked for {damage} damage!"
                
            elif action == "DEFEND":
                self.player.defend()
                self.set_message("You are defending against the next attack!")
                # Reset the action delay timer
                self.action_delay = 0
                
            elif action == "RUN":
                # Start flee animation
                self.player_fleeing = True
                self.animation_timer = 0
                self.set_message("You're fleeing from battle!")

    def set_message(self, message):
        self.full_message = message
        self.displayed_message = ""
        self.message_index = 0
        self.text_timer = 0
        
        # Always add message to log, even if it's the same as a previous one
        self.message_log.append(message)
        # Keep only the most recent messages
        if len(self.message_log) > self.max_log_size:
            self.message_log.pop(0)
    
    def update_text_animation(self):
        # Only update text if we haven't displayed the full message yet
        if self.message_index < len(self.full_message):
            self.text_timer += self.text_speed
            
            # Add characters one at a time but at a rate determined by text_speed
            # This creates smoother scrolling while maintaining the same overall speed
            while self.text_timer >= 4 and self.message_index < len(self.full_message):
                self.text_timer -= 4
                self.displayed_message += self.full_message[self.message_index]
                self.message_index += 1
    
    def update_animations(self):
        # Update text scrolling animation
        self.update_text_animation()
        
        # Only proceed with other updates if text animation is complete
        if self.message_index < len(self.full_message):
            return
            
        # Handle player attack animation
        if self.player_attacking:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_duration:
                self.player_attacking = False
                self.animation_timer = 0
                
                # Now that animation is complete, display the message
                self.set_message(self.pending_message)
                
                # If enemy was defeated, end battle and award XP
                if self.pending_victory:
                    # Award XP to player
                    xp_gained = self.enemy.xp
                    self.player.experience += xp_gained
                    
                    # Add XP message to the log
                    self.message_log.append(f"You gained {xp_gained} XP!")
                    if len(self.message_log) > self.max_log_size:
                        self.message_log.pop(0)
                    
                    self.battle_over = True
                    self.victory = True
                else:
                    # Switch to enemy's turn
                    self.turn = 1
                    self.enemy_turn_processed = False  # Reset the flag
        
        # Handle enemy attack animation
        elif self.enemy_attacking:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_duration:
                self.enemy_attacking = False
                self.animation_timer = 0
                
                # Apply damage to player
                self.player.take_damage(self.pending_damage)
                self.set_message(self.pending_message)
                
                # Check if player was defeated
                if self.player.is_defeated():
                    self.set_message(f"Enemy attacked for {self.pending_damage} damage! You were defeated!")
                    self.battle_over = True
                else:
                    # Switch back to player turn
                    self.turn = 0
        
        # Handle fleeing animation
        elif self.player_fleeing:
            self.animation_timer += 1
            if self.animation_timer >= self.flee_animation_duration:
                self.player_fleeing = False
                self.animation_timer = 0
                self.set_message("You successfully fled from battle!")
                self.battle_over = True
                self.fled = True
        
        # Handle delay for the defend action
        elif self.turn == 0 and "defending" in self.full_message:
            self.action_delay += 1
            if self.action_delay >= self.action_delay_duration:
                self.action_delay = 0
                # Switch to enemy turn
                self.turn = 1
                self.enemy_turn_processed = False  # Reset the flag
        
        # Process enemy turn if it's enemy's turn and no animation is active
        elif self.turn == 1 and not self.enemy_attacking and not self.enemy_turn_processed:
            self.process_enemy_turn()
            self.enemy_turn_processed = True  # Set the flag to prevent multiple attacks
                    
    def process_enemy_turn(self):
        # Only start enemy attack if no animation is in progress
        if not self.enemy_attacking and self.turn == 1:
            # Start enemy attack animation
            self.enemy_attacking = True
            self.animation_timer = 0
            
            # Calculate damage values
            self.pending_damage = self.enemy.attack
            self.original_damage = self.pending_damage
            
            # Prepare message based on player's defending status
            if self.player.defending:
                self.pending_damage = max(0, self.pending_damage - 1)
                self.pending_message = f"Enemy attacked for {self.original_damage} damage, but you defended! Took {self.pending_damage} damage."
            else:
                self.pending_message = f"Enemy attacked for {self.pending_damage} damage!"
                    
    def draw(self, screen):
        # Clear screen
        screen.fill(BLACK)
        
        # Calculate animation offsets
        player_offset_x = 0
        enemy_offset_x = 0
        
        if self.player_attacking:
            # Move player toward enemy during first half, then back
            if self.animation_timer < self.animation_duration / 2:
                player_offset_x = int(30 * (self.animation_timer / (self.animation_duration / 2)))
            else:
                player_offset_x = int(30 * (1 - (self.animation_timer - self.animation_duration / 2) / (self.animation_duration / 2)))
                
        elif self.player_fleeing:
            # Move player off the left side of the screen
            # Start at normal position, then move increasingly to the left
            player_offset_x = -int(300 * (self.animation_timer / self.flee_animation_duration))
        
        if self.enemy_attacking:
            # Move enemy toward player during first half, then back
            if self.animation_timer < self.animation_duration / 2:
                enemy_offset_x = int(-30 * (self.animation_timer / (self.animation_duration / 2)))
            else:
                enemy_offset_x = int(-30 * (1 - (self.animation_timer - self.animation_duration / 2) / (self.animation_duration / 2)))
        
        # Draw player unless player has fled (either during animation or after)
        if not self.fled:
            # During fleeing animation, only draw player until they're mostly off-screen
            if not self.player_fleeing or player_offset_x > -200:
                pygame.draw.rect(screen, GREEN, (self.player_pos[0] + player_offset_x, self.player_pos[1], 50, 75))  # Player
        
        # Draw enemy
        pygame.draw.rect(screen, RED, (self.enemy_pos[0] + enemy_offset_x, self.enemy_pos[1], 50, 50))    # Enemy
        
        # Draw HP and player stats information
        player_hp_text = font.render(f"Player HP: {self.player.hp}/{self.player.max_hp}", True, WHITE)
        player_lv_text = font.render(f"LV: {self.player.level}  XP: {self.player.experience}", True, WHITE)
        enemy_hp_text = font.render(f"Enemy HP: {self.enemy.hp}/{self.enemy.max_hp}", True, WHITE)
        
        screen.blit(player_hp_text, (100, 350))
        screen.blit(player_lv_text, (100, 380))
        screen.blit(enemy_hp_text, (500, 250))
        
        # Draw battle message log - a text box showing multiple recent messages
        message_box_height = 30 * len(self.message_log) + 20  # Height based on number of messages
        message_box_rect = pygame.Rect(
            SCREEN_WIDTH//2 - 300, 
            70, 
            600, 
            message_box_height
        )
        pygame.draw.rect(screen, BLACK, message_box_rect)
        pygame.draw.rect(screen, WHITE, message_box_rect, 2)  # White border
        
        # Draw all messages in the log
        for i, message in enumerate(self.message_log):
            # Only the newest message scrolls, others are shown in full
            if i == len(self.message_log) - 1 and message == self.full_message:
                message_text = font.render(self.displayed_message, True, WHITE)
                screen.blit(message_text, (SCREEN_WIDTH//2 - 290, 80 + i * 30))
                
                # Draw "..." when text is still being displayed
                if self.message_index < len(self.full_message):
                    typing_indicator = font.render("...", True, WHITE)
                    screen.blit(typing_indicator, (SCREEN_WIDTH//2 + 290, 80 + i * 30))
            else:
                message_text = font.render(message, True, GRAY)  # Older messages in gray
                screen.blit(message_text, (SCREEN_WIDTH//2 - 290, 80 + i * 30))
        
        # Draw battle options (only on player's turn when not animating)
        if self.turn == 0 and not self.battle_over and not self.player_attacking and not self.enemy_attacking and not self.player_fleeing:
            # Only display battle options when the text is fully displayed
            if self.message_index >= len(self.full_message):
                for i, option in enumerate(self.battle_options):
                    if i == self.selected_option:
                        # Highlight selected option
                        option_text = font.render(f"> {option}", True, WHITE)
                    else:
                        option_text = font.render(f"  {option}", True, GRAY)
                    screen.blit(option_text, (SCREEN_WIDTH//2 - 50, 450 + i*40))
                
        # Display continue message if battle is over
        if self.battle_over:
            # Only display the continue message when the text is fully displayed
            if self.message_index >= len(self.full_message):
                continue_text = font.render("Press ENTER to continue", True, WHITE)
                screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, 500))

# Function to determine if an action needs delay based on message content
def action_needs_delay(message):
    return True  # Apply delay to all battle actions

# Create a player
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Create an enemy
enemy = Enemy(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)

# Create sprite groups
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

enemies = pygame.sprite.Group()
enemies.add(enemy)

# Game settings
text_speed_setting = "FAST"  # Default text speed (options: "SLOW", "MEDIUM", "FAST")

# Pause menu options
pause_options = ["SETTINGS", "CLOSE"]
settings_options = ["TEXT SPEED", "BACK"]
selected_pause_option = 0
selected_settings_option = 0

# Initialize game state
game_state = WORLD_MAP
previous_game_state = WORLD_MAP  # Used when returning from PAUSE
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
            if game_state == WORLD_MAP:
                game_state = PAUSE
                previous_game_state = WORLD_MAP
                selected_pause_option = 0  # Reset selection
            elif game_state == PAUSE:
                game_state = previous_game_state
            elif game_state == SETTINGS:
                game_state = PAUSE
                selected_pause_option = 0  # Reset to first option in pause menu
                
        # Handle keyboard input for pause menu
        if game_state == PAUSE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_pause_option = (selected_pause_option - 1) % len(pause_options)
                elif event.key == pygame.K_DOWN:
                    selected_pause_option = (selected_pause_option + 1) % len(pause_options)
                elif event.key == pygame.K_RETURN:
                    if pause_options[selected_pause_option] == "SETTINGS":
                        game_state = SETTINGS
                        selected_settings_option = 0  # Reset selection
                    elif pause_options[selected_pause_option] == "CLOSE":
                        game_state = previous_game_state
                        
        # Handle keyboard input for settings menu
        elif game_state == SETTINGS:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_settings_option = (selected_settings_option - 1) % len(settings_options)
                elif event.key == pygame.K_DOWN:
                    selected_settings_option = (selected_settings_option + 1) % len(settings_options)
                elif event.key == pygame.K_RETURN:
                    if settings_options[selected_settings_option] == "TEXT SPEED":
                        # Cycle through text speed options
                        if text_speed_setting == "SLOW":
                            text_speed_setting = "MEDIUM"
                        elif text_speed_setting == "MEDIUM":
                            text_speed_setting = "FAST"
                        else:  # FAST
                            text_speed_setting = "SLOW"
                    elif settings_options[selected_settings_option] == "BACK":
                        game_state = PAUSE
                        selected_pause_option = 0  # Reset to first option in pause menu
            
        # Handle keyboard input for battle
        elif game_state == BATTLE and battle_system:
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
            else:
                # Battle is over, wait for ENTER key to continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    # Only allow continuing when text is fully displayed
                    if battle_system.message_index >= len(battle_system.full_message):
                        # Only remove enemy if player won (not if they fled)
                        if battle_system.victory:
                            collided_enemy.kill()
                        
                        # Return to world map
                        game_state = WORLD_MAP
                        player.reset_position()
                        battle_system = None
                    else:
                        # If text is still scrolling, display it immediately
                        battle_system.displayed_message = battle_system.full_message
                        battle_system.message_index = len(battle_system.full_message)
        
    # Update game objects based on game state
    if game_state == WORLD_MAP:
        # Check if player collides with an enemy
        collided_enemy = player.update(enemies)
        if collided_enemy:
            # Switch to battle state
            game_state = BATTLE
            battle_system = BattleSystem(player, collided_enemy, text_speed_setting)
        
        enemies.update()
    elif game_state == BATTLE and battle_system:
        # Update battle animations and process turns
        battle_system.update_animations()
    
    # Draw everything based on game state
    if game_state == WORLD_MAP:
        # Clear the screen
        screen.fill(BLACK)
        
        # Draw all sprites
        all_sprites.draw(screen)
        enemies.draw(screen)
        
    elif game_state == BATTLE:
        if battle_system:
            battle_system.draw(screen)
            
    elif game_state == PAUSE:
        # Draw the paused game in the background
        if previous_game_state == WORLD_MAP:
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
        
        for i, option in enumerate(pause_options):
            if i == selected_pause_option:
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
            screen.blit(option_text, (SCREEN_WIDTH//2 - 50, 250 + i*40))
            
    elif game_state == SETTINGS:
        # Draw the paused game in the background (same as PAUSE)
        if previous_game_state == WORLD_MAP:
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
            option_text = font.render(f"> {settings_options[1]}", True, WHITE)
        else:
            option_text = font.render(f"  {settings_options[1]}", True, GRAY)
        screen.blit(option_text, (SCREEN_WIDTH//2 - 100, 290))
    
    # Flip the display
    pygame.display.flip()
    
    # Maintain 60 frames per second
    clock.tick(60)

# Quit the game
pygame.quit()
sys.exit()