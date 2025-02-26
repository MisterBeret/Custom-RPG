"""
Battle system for the RPG game.
"""
import pygame
from constants import (BLACK, WHITE, GREEN, RED, GRAY, SCREEN_WIDTH, SCREEN_HEIGHT,
                      ATTACK_ANIMATION_DURATION, FLEE_ANIMATION_DURATION,
                      ACTION_DELAY_DURATION, BATTLE_OPTIONS, MAX_LOG_SIZE,
                      ORANGE)  # Added ORANGE color

class BattleSystem:
    """
    Manages turn-based battles between player and enemies.
    """
    def __init__(self, player, enemy, text_speed_setting):
        """
        Initialize the battle system.
        
        Args:
            player: The player entity
            enemy: The enemy entity
            text_speed_setting: The current text speed setting
        """
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
        
        # Text speed based on global setting
        self.set_text_speed(text_speed_setting)
            
        self.text_timer = 0
        self.battle_options = BATTLE_OPTIONS
        self.selected_option = 0
        self.battle_over = False
        self.victory = False
        self.pending_victory = False
        self.fled = False
        
        # Add a delay timer for action transitions
        self.action_delay = 0
        self.action_delay_duration = ACTION_DELAY_DURATION
        
        # Add a flag to prevent multiple enemy attacks
        self.enemy_turn_processed = False
        
        # Message log to store recent battle messages
        self.message_log = [self.first_message]
        self.max_log_size = MAX_LOG_SIZE
        
        # Animation properties
        self.player_pos = (550, 400)  # Player now on the right
        self.enemy_pos = (200, 300)   # Enemy now on the left
        self.player_attacking = False
        self.enemy_attacking = False
        self.player_fleeing = False
        self.animation_timer = 0
        self.animation_duration = ATTACK_ANIMATION_DURATION
        self.flee_animation_duration = FLEE_ANIMATION_DURATION
        
        # Pending values for delayed application
        self.pending_damage = 0
        self.original_damage = 0
        self.pending_message = ""
        
    def set_text_speed(self, text_speed_setting):
        """
        Set the text speed based on the given setting.
        
        Args:
            text_speed_setting: The text speed setting ("SLOW", "MEDIUM", or "FAST")
        """
        if text_speed_setting == "SLOW":
            self.text_speed = 1
        elif text_speed_setting == "MEDIUM":
            self.text_speed = 2
        else:  # FAST
            self.text_speed = 4
    
    def calculate_damage(self, attacker, defender):
        """
        Calculate damage based on attacker's ATK and defender's DEF stats.
        
        Args:
            attacker: The attacking entity
            defender: The defending entity
            
        Returns:
            int: The calculated damage amount (minimum 0)
        """
        # Calculate effective defense based on defense multiplier
        effective_defense = defender.defense * defender.defense_multiplier
        
        # Calculate damage as attacker's attack minus defender's effective defense
        damage = max(0, attacker.attack - effective_defense)
        
        return damage
        
    def process_action(self, action):
        """
        Process a player action.
        
        Args:
            action: The action to process ("ATTACK", "DEFEND", or "RUN")
        """
        if self.turn == 0:  # Player's turn
            if action == "ATTACK":
                # Start player attack animation
                self.player_attacking = True
                self.animation_timer = 0
                
                # Calculate damage
                damage = self.calculate_damage(self.player, self.enemy)
                self.enemy.take_damage(damage)
                
                # Store the message for later display after animation
                if self.enemy.is_defeated():
                    self.pending_message = f"You attacked for {damage} damage! You defeated the enemy!"
                    self.pending_victory = True
                else:
                    self.pending_message = f"You attacked for {damage} damage!"
                
            elif action == "DEFEND":
                self.player.defend()
                self.set_message(f"You are defending! DEF increased to {self.player.defense * self.player.defense_multiplier}!")
                # Reset the action delay timer
                self.action_delay = 0
                
            elif action == "RUN":
                # Start flee animation
                self.player_fleeing = True
                self.animation_timer = 0
                self.set_message("You're fleeing from battle!")

    def set_message(self, message):
        """
        Set a new battle message and reset text animation.
        
        Args:
            message: The message to display
        """
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
        """
        Update the text scrolling animation.
        """
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
        """
        Update all battle animations and process turn logic.
        """
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
                    self.player.gain_experience(xp_gained)
                    
                    # Add XP message to the log
                    self.message_log.append(f"You gained {xp_gained} XP!")
                    if len(self.message_log) > self.max_log_size:
                        self.message_log.pop(0)
                    
                    self.battle_over = True
                    self.victory = True
                else:
                    # Reset player's defense multiplier at end of turn if defending
                    self.player.end_turn()
                    
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
                    # Reset enemy's defense multiplier at end of turn if defending
                    self.enemy.end_turn()
                    
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
        """
        Process the enemy's turn in battle.
        """
        # Only start enemy attack if no animation is in progress
        if not self.enemy_attacking and self.turn == 1:
            # Start enemy attack animation
            self.enemy_attacking = True
            self.animation_timer = 0
            
            # Calculate damage values using our new method
            self.pending_damage = self.calculate_damage(self.enemy, self.player)
            self.original_damage = self.enemy.attack
            
            # Prepare message based on player's defending status
            if self.player.defending:
                self.pending_message = f"Enemy attacked for {self.original_damage} ATK, but you defended with {self.player.defense * self.player.defense_multiplier} DEF! Took {self.pending_damage} damage."
            else:
                self.pending_message = f"Enemy attacked for {self.original_damage} ATK against your {self.player.defense} DEF! Took {self.pending_damage} damage."
                    
    def draw(self, screen):
        """
        Draw the battle scene.
        
        Args:
            screen: The Pygame surface to draw on
        """
        # Clear screen
        screen.fill(BLACK)
        
        # Calculate animation offsets
        player_offset_x = 0
        enemy_offset_x = 0
        
        if self.player_attacking:
            # Move player toward enemy during first half, then back
            # Now player moves left (-) toward enemy
            if self.animation_timer < self.animation_duration / 2:
                player_offset_x = int(-30 * (self.animation_timer / (self.animation_duration / 2)))
            else:
                player_offset_x = int(-30 * (1 - (self.animation_timer - self.animation_duration / 2) / (self.animation_duration / 2)))
                
        elif self.player_fleeing:
            # Move player off the right side of the screen
            # Start at normal position, then move increasingly to the right
            player_offset_x = int(300 * (self.animation_timer / self.flee_animation_duration))
        
        if self.enemy_attacking:
            # Move enemy toward player during first half, then back
            # Now enemy moves right (+) toward player
            if self.animation_timer < self.animation_duration / 2:
                enemy_offset_x = int(30 * (self.animation_timer / (self.animation_duration / 2)))
            else:
                enemy_offset_x = int(30 * (1 - (self.animation_timer - self.animation_duration / 2) / (self.animation_duration / 2)))
        
        # Draw player unless player has fled (either during animation or after)
        if not self.fled:
            # During fleeing animation, only draw player until they're mostly off-screen
            if not self.player_fleeing or player_offset_x > -200:
                pygame.draw.rect(screen, GREEN, (self.player_pos[0] + player_offset_x, self.player_pos[1], 50, 75))  # Player
        
        # Draw enemy
        pygame.draw.rect(screen, RED, (self.enemy_pos[0] + enemy_offset_x, self.enemy_pos[1], 50, 50))    # Enemy
        
        self._draw_battle_ui(screen)
        
    def _draw_battle_ui(self, screen):
        """
        Draw the battle UI elements.
        
        Args:
            screen: The Pygame surface to draw on
        """
        # Get the font
        font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 20)
        
        # Draw stat windows at the bottom of the screen
        self._draw_player_stat_window(screen, font, small_font)
        self._draw_enemy_stat_window(screen, font, small_font)
        
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
        
        # Draw battle options in their own box (only on player's turn when not animating)
        if self.turn == 0 and not self.battle_over and not self.player_attacking and not self.enemy_attacking and not self.player_fleeing:
            # Only display battle options when the text is fully displayed
            if self.message_index >= len(self.full_message):
                # Create options box in the middle bottom
                options_box_width = 200
                options_box_height = 120
                options_box_x = SCREEN_WIDTH // 2 - options_box_width // 2
                options_box_y = SCREEN_HEIGHT - options_box_height - 75  # Above the stat windows
                
                # Draw box background and border
                pygame.draw.rect(screen, BLACK, (options_box_x, options_box_y, options_box_width, options_box_height))
                pygame.draw.rect(screen, WHITE, (options_box_x, options_box_y, options_box_width, options_box_height), 2)
                
                # Draw "Actions" header
                actions_text = font.render("Actions", True, WHITE)
                screen.blit(actions_text, (options_box_x + options_box_width // 2 - actions_text.get_width() // 2, options_box_y + 10))
                
                # Draw battle options
                for i, option in enumerate(self.battle_options):
                    if i == self.selected_option:
                        # Highlight selected option
                        option_text = font.render(f"> {option}", True, WHITE)
                    else:
                        option_text = font.render(f"  {option}", True, GRAY)
                    screen.blit(option_text, (options_box_x + 30, options_box_y + 40 + i * 25))
                
        # Display continue message if battle is over
        if self.battle_over:
            # Only display the continue message when the text is fully displayed
            if self.message_index >= len(self.full_message):
                continue_text = font.render("Press ENTER to continue", True, WHITE)
                screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, 500))
                
    def _draw_player_stat_window(self, screen, font, small_font):
        """
        Draw the player's stat window at the bottom of the screen.
        Shows only LV, XP, and HP as requested.
        
        Args:
            screen: The Pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for detailed stats
        """
        # Create player stat window (right side of bottom)
        window_width = SCREEN_WIDTH // 2 - 10
        window_height = 60  # Reduced height since we're showing fewer stats
        window_x = SCREEN_WIDTH // 2 + 5  # Now on the right side
        window_y = SCREEN_HEIGHT - window_height - 5
        
        # Draw window background and border
        pygame.draw.rect(screen, BLACK, (window_x, window_y, window_width, window_height))
        pygame.draw.rect(screen, GREEN, (window_x, window_y, window_width, window_height), 2)
        
        # Draw player name and level at top of window
        player_name = font.render(f"Player  LV: {self.player.level}", True, GREEN)
        screen.blit(player_name, (window_x + 10, window_y + 5))
        
        # Draw HP as a bar with text
        hp_bar_width = window_width - 110  # Leave room for the text
        hp_bar_height = 15
        hp_bar_x = window_x + 100
        hp_bar_y = window_y + 10
        
        # Draw the HP bar background (depleted health shown as gray)
        pygame.draw.rect(screen, GRAY, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        
        # Draw the current HP fill (active health shown as orange)
        hp_fill_width = int((self.player.hp / self.player.max_hp) * hp_bar_width)
        pygame.draw.rect(screen, ORANGE, (hp_bar_x, hp_bar_y, hp_fill_width, hp_bar_height))
        
        # Draw HP text
        hp_text = small_font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, WHITE)
        screen.blit(hp_text, (window_x + 10, window_y + 10))
        
        # Draw XP in bottom of window
        xp_text = small_font.render(f"XP: {self.player.experience}", True, WHITE)
        screen.blit(xp_text, (window_x + 10, window_y + 35))
    
    def _draw_enemy_stat_window(self, screen, font, small_font):
        """
        Draw the enemy's stat window at the bottom left of the screen.
        Shows only HP as requested.
        
        Args:
            screen: The Pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for detailed stats
        """
        # Create enemy stat window (left side of bottom)
        window_width = SCREEN_WIDTH // 2 - 10
        window_height = 60  # Reduced height since we're showing fewer stats
        window_x = 5  # Now on the left side
        window_y = SCREEN_HEIGHT - window_height - 5
        
        # Draw window background and border
        pygame.draw.rect(screen, BLACK, (window_x, window_y, window_width, window_height))
        pygame.draw.rect(screen, RED, (window_x, window_y, window_width, window_height), 2)
        
        # Draw enemy name at top of window
        enemy_name = font.render("Enemy", True, RED)
        screen.blit(enemy_name, (window_x + 10, window_y + 5))
        
        # Draw HP as a bar with text
        hp_bar_width = window_width - 110  # Leave room for the text
        hp_bar_height = 15
        hp_bar_x = window_x + 100
        hp_bar_y = window_y + 10
        
        # Draw the HP bar background (depleted health shown as gray)
        pygame.draw.rect(screen, GRAY, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        
        # Draw the current HP fill (active health shown as orange)
        hp_fill_width = int((self.enemy.hp / self.enemy.max_hp) * hp_bar_width)
        pygame.draw.rect(screen, ORANGE, (hp_bar_x, hp_bar_y, hp_fill_width, hp_bar_height))
        
        # Draw HP text
        hp_text = small_font.render(f"HP: {self.enemy.hp}/{self.enemy.max_hp}", True, WHITE)
        screen.blit(hp_text, (window_x + 10, window_y + 10))