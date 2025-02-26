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
        
        # Battle stats
        self.max_hp = 10
        self.hp = 10
        self.attack = 1
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
        
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
            
    def is_defeated(self):
        return self.hp <= 0

class BattleSystem:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.turn = 0  # 0 for player's turn, 1 for enemy's turn
        self.message = "Battle started! Choose your action."
        self.battle_options = ["ATTACK", "DEFEND", "RUN"]
        self.selected_option = 0
        self.battle_over = False
        self.victory = False
        self.pending_victory = False
        self.fled = False
        
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
                
                # Process damage
                damage = self.player.attack
                self.enemy.take_damage(damage)
                self.message = f"You attacked for {damage} damage!"
                
                # Check if enemy is defeated, but don't end battle yet
                # Wait for animation to complete
                if self.enemy.is_defeated():
                    self.pending_victory = True
                    self.message = f"You attacked for {damage} damage! You defeated the enemy!"
                
                # Note: turn switching happens after animation completes
                # in the update_animations method
                
            elif action == "DEFEND":
                self.player.defend()
                self.message = "You are defending against the next attack!"
                # Switch to enemy turn immediately for non-attack actions
                self.turn = 1
                # Trigger enemy turn
                self.process_enemy_turn()
                
            elif action == "RUN":
                # Start flee animation
                self.player_fleeing = True
                self.animation_timer = 0
                self.message = "You're fleeing from battle!"
                
                # Set battle as pending completion (will be set to over after animation)
                # Note: actual ending happens in update_animations when animation completes
    
    def update_animations(self):
        # Handle attack animations
        if self.player_attacking or self.enemy_attacking or self.player_fleeing:
            self.animation_timer += 1
            
            # When animation ends
            if (self.player_attacking or self.enemy_attacking) and self.animation_timer >= self.animation_duration:
                if self.player_attacking:
                    self.player_attacking = False
                    
                    # If this was the final blow, end the battle
                    if self.pending_victory:
                        self.battle_over = True
                        self.victory = True
                        return
                    
                    # Otherwise switch to enemy turn after player attack animation completes
                    self.turn = 1
                    # Automatically trigger enemy turn
                    self.process_enemy_turn()
                elif self.enemy_attacking:
                    self.enemy_attacking = False
                    
                    # Apply pending damage and message at the end of enemy animation
                    self.player.take_damage(self.pending_damage)
                    self.message = self.pending_message
                    
                    if self.player.is_defeated():
                        self.message = f"Enemy attacked for {self.pending_damage} damage! You were defeated!"
                        self.battle_over = True
                    
                    # Switch back to player turn after enemy attack animation completes
                    self.turn = 0
            
            # Check flee animation completion separately (longer duration)
            elif self.player_fleeing and self.animation_timer >= self.flee_animation_duration:
                self.player_fleeing = False
                self.message = "You successfully fled from battle!"
                self.battle_over = True
                self.fled = True
                    
    def process_enemy_turn(self):
        # Only start enemy attack animation if not already animating
        if not self.enemy_attacking:
            # Start enemy attack animation
            self.enemy_attacking = True
            self.animation_timer = 0
            
            # Calculate damage values (but don't apply them yet)
            self.pending_damage = self.enemy.attack
            self.original_damage = self.pending_damage
            
            # Prepare message based on player's defending status
            if self.player.defending:
                self.pending_damage = max(0, self.pending_damage - 1)
                self.pending_message = f"Enemy attacked for {self.original_damage} damage, but you defended! Took {self.pending_damage} damage."
            else:
                self.pending_message = f"Enemy attacked for {self.pending_damage} damage!"
            
            # Note: The actual damage application happens at the end of the animation
            # in the update_animations method
                    
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
        
        # Draw HP information
        player_hp_text = font.render(f"Player HP: {self.player.hp}/{self.player.max_hp}", True, WHITE)
        enemy_hp_text = font.render(f"Enemy HP: {self.enemy.hp}/{self.enemy.max_hp}", True, WHITE)
        screen.blit(player_hp_text, (100, 350))
        screen.blit(enemy_hp_text, (500, 250))
        
        # Draw battle message
        message_text = font.render(self.message, True, WHITE)
        screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 100))
        
        # Draw battle options (only on player's turn when not animating)
        if self.turn == 0 and not self.battle_over and not self.player_attacking and not self.enemy_attacking and not self.player_fleeing:
            for i, option in enumerate(self.battle_options):
                if i == self.selected_option:
                    # Highlight selected option
                    option_text = font.render(f"> {option}", True, WHITE)
                else:
                    option_text = font.render(f"  {option}", True, GRAY)
                screen.blit(option_text, (SCREEN_WIDTH//2 - 50, 450 + i*40))
                
        # Display continue message if battle is over
        if self.battle_over:
            continue_text = font.render("Press ENTER to continue", True, WHITE)
            screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, 500))

# Create a player
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Create an enemy
enemy = Enemy(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)

# Create sprite groups
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

enemies = pygame.sprite.Group()
enemies.add(enemy)

# Initialize game state
game_state = WORLD_MAP
battle_system = None
collided_enemy = None

# Main game loop
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Handle keyboard input for battle
        if game_state == BATTLE and battle_system:
            if not battle_system.battle_over:
                if event.type == pygame.KEYDOWN:
                    if battle_system.turn == 0:  # Player's turn
                        if event.key == pygame.K_UP:
                            battle_system.selected_option = (battle_system.selected_option - 1) % len(battle_system.battle_options)
                        elif event.key == pygame.K_DOWN:
                            battle_system.selected_option = (battle_system.selected_option + 1) % len(battle_system.battle_options)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            selected_action = battle_system.battle_options[battle_system.selected_option]
                            battle_system.process_action(selected_action)
            else:
                # Battle is over, wait for ENTER key to continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    # Only remove enemy if player won (not if they fled)
                    if battle_system.victory:
                        collided_enemy.kill()
                    
                    # Return to world map
                    game_state = WORLD_MAP
                    player.reset_position()
                    battle_system = None
        
    # Update game objects based on game state
    if game_state == WORLD_MAP:
        # Check if player collides with an enemy
        collided_enemy = player.update(enemies)
        if collided_enemy:
            # Switch to battle state
            game_state = BATTLE
            battle_system = BattleSystem(player, collided_enemy)
        
        enemies.update()
    elif game_state == BATTLE and battle_system:
        # Update battle animations
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
    
    # Flip the display
    pygame.display.flip()
    
    # Maintain 60 frames per second
    clock.tick(60)

# Quit the game
pygame.quit()
sys.exit()