"""
Battle system for the RPG game.
"""
import pygame
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import scale_position, scale_dimensions, scale_font_size

from constants import (BLACK, WHITE, GREEN, RED, GRAY, SCREEN_WIDTH, SCREEN_HEIGHT,
                      ATTACK_ANIMATION_DURATION, FLEE_ANIMATION_DURATION,
                      ACTION_DELAY_DURATION, SPELL_ANIMATION_DURATION, 
                      BATTLE_OPTIONS, MAX_LOG_SIZE,
                      ORANGE, BLUE, DARK_BLUE, PURPLE)

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
        self.action_processing = False  # Flag to prevent multiple actions per turn
        
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
        
        # Magic system additions
        self.in_spell_menu = False
        self.selected_spell_option = 0
        self.player_casting = False
        self.spell_animation_duration = SPELL_ANIMATION_DURATION
        self.current_spell = None
        
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
    
    def calculate_hit_chance(self, attacker, defender):
        """
        Calculate the chance to hit based on attacker's ACC and defender's SPD.
        
        Args:
            attacker: The attacking entity
            defender: The defending entity
            
        Returns:
            float: The chance to hit as a decimal between 0 and 1
        """
        # Base formula: When ACC equals SPD, hit chance is 0.9 (90%)
        # For each point ACC is higher than SPD, hit chance increases by 0.05
        # For each point ACC is lower than SPD, hit chance decreases by 0.2
        
        if attacker.acc >= defender.spd:
            # High accuracy case - 90% base hit chance, +5% per point above opponent's speed
            hit_chance = 0.9 + (attacker.acc - defender.spd) * 0.05
            # Cap at 99% hit chance (always a small chance to miss)
            hit_chance = min(0.99, hit_chance)
        else:
            # Low accuracy case - lose 20% hit chance per point below opponent's speed
            hit_chance = 0.9 - (defender.spd - attacker.acc) * 0.2
            # Minimum 10% hit chance (always a small chance to hit)
            hit_chance = max(0.1, hit_chance)
    
        # If defender is defending, reduce hit chance by 25%
        if defender.defending:
            hit_chance = max(0, hit_chance - 0.25)
        
        return hit_chance
    
    def calculate_damage(self, attacker, defender):
        """
        Calculate damage based on attacker's ATK and defender's DEF stats.
        Also applies a 50% damage reduction if defending.
    
        Args:
            attacker: The attacking entity
            defender: The defending entity
        
        Returns:
            int: The calculated damage amount (minimum 0)
        """
        # Calculate base damage as attacker's attack minus defender's defense
        damage = max(0, attacker.attack - defender.defense)
    
        # If defender is defending, reduce all damage by 50% (rounded up)
        if defender.defending:
            import math
            damage = math.ceil(damage / 2)
    
        return damage
    
    def calculate_magic_damage(self, caster, target, base_power=0):
        """
        Calculate magic damage based on caster's INT and target's RES stats.
    
        Args:
            caster: The entity casting the spell
            target: The target of the spell
            base_power: Base power of the spell
        
        Returns:
            int: The calculated magic damage amount (minimum 0)
        """
        # Magic damage formula: (caster's INT + spell base power) - target's RES
        damage = max(0, (caster.intelligence + base_power) - target.resilience)

        # If target is defending, reduce all damage by 50% (rounded up)
        if target.defending:
            import math
            damage = math.ceil(damage / 2)
    
        return damage
        
    def process_action(self, action):
        """
        Process a player action.
        
        Args:
            action: The action to process ("ATTACK", "DEFEND", "MAGIC", "ITEMS", or "RUN")
        """
        if self.turn == 0 and not self.action_processing:  # Player's turn and not already processing
            self.action_processing = True
            if action == "ATTACK":
                # Start player attack animation
                self.player_attacking = True
                self.animation_timer = 0
                
                # Calculate hit chance and determine if attack hits
                hit_chance = self.calculate_hit_chance(self.player, self.enemy)
                attack_hits = random.random() < hit_chance
                
                if attack_hits:
                    # Calculate damage
                    damage = self.calculate_damage(self.player, self.enemy)
                    self.enemy.take_damage(damage)
                    
                    # Store the message for later display after animation
                    if self.enemy.is_defeated():
                        self.pending_message = f"You attacked for {damage} damage! Enemy defeated!"
                        self.pending_victory = True
                    else:
                        self.pending_message = f"You attacked for {damage} damage!"
                else:
                    # Attack missed
                    self.pending_message = "Your attack missed!"
                
            elif action == "DEFEND":
                self.player.defend()
                self.set_message("You're defending! Incoming damage reduced and evasion increased!")
                #Reset the action delay timer
                self.action_delay = 0
                #Make sure we're setting action_processing to True
                self.action_processing = True
                
            elif action == "MAGIC":
                # Open magic menu
                self.in_spell_menu = True
                self.selected_spell_option = 0
                self.set_message("Select a spell to cast:")
                self.action_processing = False  # Allow spell selection
                
            elif action == "RUN":
                # Start flee animation
                self.player_fleeing = True
                self.animation_timer = 0
                self.set_message("You tried to flee!")

    def cast_spell(self, spell_name):
        """
        Process casting a spell.
        
        Args:
            spell_name: The name of the spell to cast
        """
        if self.turn == 0 and not self.action_processing:
            # Get the spell data
            spell = self.player.spellbook.get_spell(spell_name)
            if not spell:
                self.set_message(f"You don't know the spell {spell_name}!")
                return False
                
            # Check if player has enough SP
            if self.player.sp < spell.sp_cost:
                self.set_message(f"Not enough SP to cast {spell_name}!")
                return False
                
            # Set the current spell for animation
            self.current_spell = spell
            self.action_processing = True
                
            # Start spell casting animation
            self.player_casting = True
            self.animation_timer = 0
                
            # Use the SP
            self.player.use_sp(spell.sp_cost)
                
            # Handle spell effects
            if spell.effect_type == "damage":
                # Calculate magic damage
                damage = self.calculate_magic_damage(self.player, self.enemy, spell.base_power)
                self.enemy.take_damage(damage)
                    
                # Store the message for later display after animation
                if self.enemy.is_defeated():
                    self.pending_message = f"Cast {spell_name}! Dealt {damage} magic damage! Enemy defeated!"
                    self.pending_victory = True
                else:
                    self.pending_message = f"Cast {spell_name}! Dealt {damage} magic damage!"
                
            elif spell.effect_type == "healing":
                # For healing spells, add intelligence to the base power
                healing_amount = spell.base_power + self.player.intelligence
                    
                # Store original HP to calculate actual healing
                original_hp = self.player.hp
                    
                # Apply healing (capped at max_hp)
                self.player.hp = min(self.player.hp + healing_amount, self.player.max_hp)
                    
                # Calculate actual healing done
                actual_healing = self.player.hp - original_hp
                    
                # Set pending message
                self.pending_message = f"Cast {spell_name}! Restored {actual_healing} HP!"
                
            return True
        
        return False

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
                        
                self.action_processing = False
        
        # Handle player spell casting animation
        elif self.player_casting:
            self.animation_timer += 1
            if self.animation_timer >= self.spell_animation_duration:
                self.player_casting = False
                self.animation_timer = 0
                self.current_spell = None
                
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
                    self.enemy_turn_processed = False
                
                self.action_processing = False
        
        # Handle enemy attack animation
        elif self.enemy_attacking:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_duration:
                self.enemy_attacking = False
                self.animation_timer = 0
                
                # Apply damage to player (only if attack didn't miss)
                if "missed" not in self.pending_message:
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

                    self.action_processing = False
        
        # Handle fleeing animation
        elif self.player_fleeing:
            self.animation_timer += 1
            if self.animation_timer >= self.flee_animation_duration:
                self.player_fleeing = False
                self.animation_timer = 0
                self.set_message("You fled from battle!")
                self.battle_over = True
                self.fled = True

                self.action_processing = False
        
        # Handle delay for the defend action
        elif self.turn == 0 and "defending" in self.full_message:
            self.action_delay += 1
            if self.action_delay >= self.action_delay_duration:
                self.action_delay = 0
                # Switch to enemy turn
                self.turn = 1
                self.enemy_turn_processed = False  # Reset the flag
                # Add this line:
                self.action_processing = False
        
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
        
            # Calculate hit chance and determine if attack hits
            hit_chance = self.calculate_hit_chance(self.enemy, self.player)
            attack_hits = random.random() < hit_chance
        
            if attack_hits:
                # Calculate damage values
                self.pending_damage = self.calculate_damage(self.enemy, self.player)
            
                # For display purposes, calculate what damage would be without defending
                if self.player.defending:
                    import math
                    self.original_damage = self.pending_damage * 2
                else:
                    self.original_damage = self.pending_damage
            
                # Prepare message based on player's defending status
                if self.player.defending:
                    self.pending_message = f"Enemy attacked! Your defense reduced damage from {self.original_damage} to {self.pending_damage}!"
                else:
                    self.pending_message = f"Enemy attacked for {self.pending_damage} damage!"
            else:
                # Attack missed
                self.pending_damage = 0
                # Prepare message based on why it might have missed
                if self.player.defending:
                    self.pending_message = "Enemy's attack missed! Your defensive stance helped you evade!"
                else:
                    self.pending_message = "Enemy's attack missed!"
                    
    def draw(self, screen):
        """
        Draw the battle scene with scaling support.
        
        Args:
            screen: The Pygame surface to draw on
        """
        # Import utils here to avoid circular imports
        from utils import scale_position, scale_dimensions
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Clear screen
        screen.fill(BLACK)
        
        # Calculate animation offsets
        player_offset_x = 0
        enemy_offset_x = 0
        
        if self.player_attacking:
            # Move player toward enemy during first half, then back
            # Player moves left (-) toward enemy
            if self.animation_timer < self.animation_duration / 2:
                player_offset_x = int(-30 * (self.animation_timer / (self.animation_duration / 2)))
            else:
                player_offset_x = int(-30 * (1 - (self.animation_timer - self.animation_duration / 2) / (self.animation_duration / 2)))
                    
        elif self.player_fleeing:
            # Move player off the right side of the screen
            player_offset_x = int(300 * (self.animation_timer / self.flee_animation_duration))
        
        elif self.player_casting:
            # For spell casting, add a subtle effect
            if self.animation_timer < self.spell_animation_duration / 2:
                player_offset_x = int(-10 * (self.animation_timer / (self.spell_animation_duration / 2)))
            else:
                player_offset_x = int(-10 * (1 - (self.animation_timer - self.spell_animation_duration / 2) / (self.spell_animation_duration / 2)))
        
        if self.enemy_attacking:
            # Move enemy toward player during first half, then back
            if self.animation_timer < self.animation_duration / 2:
                enemy_offset_x = int(30 * (self.animation_timer / (self.animation_duration / 2)))
            else:
                enemy_offset_x = int(30 * (1 - (self.animation_timer - self.animation_duration / 2) / (self.animation_duration / 2)))
        
        # Scale positions and dimensions
        player_pos_scaled = scale_position(self.player_pos[0], self.player_pos[1], 
                                        original_width, original_height, 
                                        current_width, current_height)
        enemy_pos_scaled = scale_position(self.enemy_pos[0], self.enemy_pos[1],
                                        original_width, original_height,
                                        current_width, current_height)
        
        player_size = scale_dimensions(50, 75, original_width, original_height, 
                                    current_width, current_height)
        enemy_size = scale_dimensions(50, 50, original_width, original_height,
                                    current_width, current_height)
        
        # Scale offset values
        player_offset_x = int(player_offset_x * (current_width / original_width))
        enemy_offset_x = int(enemy_offset_x * (current_width / original_width))
        
        # Draw player unless player has fled
        if not self.fled:
            # During fleeing animation, only draw player until they're mostly off-screen
            if not self.player_fleeing or player_offset_x > -200 * (current_width / original_width):
                # Draw magic effect if casting
                if self.player_casting and self.current_spell and self.current_spell.effect_type == "damage":
                    # Draw spell projectile traveling toward enemy
                    spell_progress = self.animation_timer / self.spell_animation_duration
                    spell_x, spell_y = scale_position(
                        self.player_pos[0] - 300 * spell_progress,
                        self.player_pos[1] + 35,
                        original_width, original_height,
                        current_width, current_height
                    )
                    
                    # Scale circle radius
                    circle_radius = int(10 * min(current_width / original_width, current_height / original_height))
                    pygame.draw.circle(screen, RED, (int(spell_x), int(spell_y)), circle_radius)
                
                # Draw player character
                pygame.draw.rect(screen, GREEN, 
                                (player_pos_scaled[0] + player_offset_x, 
                                player_pos_scaled[1], 
                                player_size[0], player_size[1]))
                
                # Draw healing effect if applicable
                if self.player_casting and self.current_spell and self.current_spell.effect_type == "healing":
                    # Scale radius for healing particles
                    base_radius = 20 * (current_width / original_width)
                    radius_increase = 10 * (current_width / original_width)
                    particle_size = int(5 * (current_width / original_width))
                    
                    # Draw healing particles around player
                    for i in range(5):
                        angle = self.animation_timer * 0.1 + i * (2 * 3.14159 / 5)
                        radius = base_radius + radius_increase * (self.animation_timer / self.spell_animation_duration)
                        
                        # Center of player for particle origin
                        center_x = player_pos_scaled[0] + player_size[0] / 2
                        center_y = player_pos_scaled[1] + player_size[1] / 2
                        
                        heal_x = center_x + int(radius * pygame.math.Vector2(1, 0).rotate(angle * 57.3).x)
                        heal_y = center_y + int(radius * pygame.math.Vector2(1, 0).rotate(angle * 57.3).y)
                        pygame.draw.circle(screen, BLUE, (heal_x, heal_y), particle_size)
        
        # Draw enemy
        pygame.draw.rect(screen, RED, 
                        (enemy_pos_scaled[0] + enemy_offset_x, 
                        enemy_pos_scaled[1], 
                        enemy_size[0], enemy_size[1]))
        
        # Draw the battle UI
        self._draw_battle_ui(screen)
        
        # Draw enemy
        pygame.draw.rect(screen, RED, (self.enemy_pos[0] + enemy_offset_x, self.enemy_pos[1], 50, 50))
        
        self._draw_battle_ui(screen)
        
    def _draw_battle_ui(self, screen):
        """
        Draw the battle UI elements with scaling support.
        
        Args:
            screen: The Pygame surface to draw on
        """
        from utils import scale_position, scale_dimensions, scale_font_size
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Scale font sizes
        font_size = scale_font_size(24, original_width, original_height, current_width, current_height)
        small_font_size = scale_font_size(18, original_width, original_height, current_width, current_height)
        
        # Create the scaled fonts
        font = pygame.font.SysFont('Arial', font_size)
        small_font = pygame.font.SysFont('Arial', small_font_size)
        
        # Draw only player stat window at the bottom of the screen
        self._draw_player_stat_window(screen, font, small_font)
        
        # Scale message box dimensions and position
        message_box_width = int(600 * (current_width / original_width))
        message_box_height = int((30 * len(self.message_log) + 20) * (current_height / original_height))
        message_box_x = (current_width // 2) - (message_box_width // 2)
        message_box_y = int(70 * (current_height / original_height))
        
        # Draw battle message log
        message_box_rect = pygame.Rect(
            message_box_x, 
            message_box_y, 
            message_box_width, 
            message_box_height
        )
        pygame.draw.rect(screen, BLACK, message_box_rect)
        pygame.draw.rect(screen, WHITE, message_box_rect, max(1, int(2 * (current_width / original_width))))  # Scale border width
        
        # Scale text positions
        message_x = message_box_x + int(10 * (current_width / original_width))
        message_y_base = message_box_y + int(10 * (current_height / original_height))
        message_line_height = int(30 * (current_height / original_height))
        
        # Draw all messages in the log
        for i, message in enumerate(self.message_log):
            # Calculate y position for this message
            message_y = message_y_base + i * message_line_height
            
            # Only the newest message scrolls, others are shown in full
            if i == len(self.message_log) - 1 and message == self.full_message:
                message_text = font.render(self.displayed_message, True, WHITE)
                screen.blit(message_text, (message_x, message_y))
                
                # Draw "..." when text is still being displayed
                if self.message_index < len(self.full_message):
                    typing_indicator = font.render("...", True, WHITE)
                    typing_x = message_box_x + message_box_width - typing_indicator.get_width() - int(10 * (current_width / original_width))
                    screen.blit(typing_indicator, (typing_x, message_y))
            else:
                message_text = font.render(message, True, GRAY)  # Older messages in gray
                screen.blit(message_text, (message_x, message_y))
        
        # Draw battle options or spell menu
        if self.turn == 0 and not self.battle_over and not self.player_attacking and not self.enemy_attacking and not self.player_fleeing and not self.player_casting and self.action_delay == 0:
            # Only display UI when the text is fully displayed
            if self.message_index >= len(self.full_message):
                if self.in_spell_menu:
                    self._draw_spell_menu(screen, font, small_font)
                else:
                    self._draw_battle_options(screen, font)
                    
        # Display continue message if battle is over
        if self.battle_over:
            # Only display the continue message when the text is fully displayed
            if self.message_index >= len(self.full_message):
                continue_text = font.render("Press ENTER to continue", True, WHITE)
                continue_x = (current_width // 2) - (continue_text.get_width() // 2)
                continue_y = int(500 * (current_height / original_height))
                screen.blit(continue_text, (continue_x, continue_y))
    
    def _draw_spell_menu(self, screen, font, small_font):
        """
        Draw the spell selection menu with scaling support.
        
        Args:
            screen: The pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for details
        """
        from utils import scale_position, scale_dimensions
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Scale menu dimensions and position
        spell_box_width, spell_box_height = scale_dimensions(
            250, 150, original_width, original_height, current_width, current_height
        )
        spell_box_x, spell_box_y = scale_position(
            20, SCREEN_HEIGHT - 150 - 5, original_width, original_height, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, BLACK, (spell_box_x, spell_box_y, spell_box_width, spell_box_height))
        border_width = max(1, int(2 * (current_width / original_width)))
        pygame.draw.rect(screen, PURPLE, (spell_box_x, spell_box_y, spell_box_width, spell_box_height), border_width)
        
        # Draw "Magic" header
        magic_text = font.render("Magic", True, PURPLE)
        header_x = spell_box_x + (spell_box_width // 2) - (magic_text.get_width() // 2)
        header_y = spell_box_y + int(10 * (current_height / original_height))
        screen.blit(magic_text, (header_x, header_y))
        
        # Get spell list from player's spellbook
        spell_names = self.player.spellbook.get_spell_names()
        # Add "BACK" option at the end
        options = spell_names + ["BACK"]
        
        # Scale text positions
        option_x = spell_box_x + int(30 * (current_width / original_width))
        option_y_base = spell_box_y + int(40 * (current_height / original_height))
        option_line_height = int(25 * (current_height / original_height))
        sp_cost_x = spell_box_x + int(150 * (current_width / original_width))
        
        # Draw each spell with SP cost
        for i, spell_name in enumerate(options):
            option_y = option_y_base + i * option_line_height
            
            if spell_name == "BACK":
                # Draw BACK option
                if i == self.selected_spell_option:
                    option_text = font.render(f"> {spell_name}", True, WHITE)
                else:
                    option_text = font.render(f"  {spell_name}", True, GRAY)
                screen.blit(option_text, (option_x, option_y))
            else:
                # Get the spell data
                spell = self.player.spellbook.get_spell(spell_name)
                
                # Determine text color based on whether player has enough SP
                has_sp = self.player.sp >= spell.sp_cost
                
                if i == self.selected_spell_option:
                    # Selected spell
                    if has_sp:
                        name_color = WHITE  # Can cast
                    else:
                        name_color = RED    # Can't cast (not enough SP)
                    option_text = font.render(f"> {spell_name}", True, name_color)
                else:
                    # Unselected spell
                    if has_sp:
                        name_color = GRAY   # Can cast
                    else:
                        name_color = RED    # Can't cast (not enough SP)
                    option_text = font.render(f"  {spell_name}", True, name_color)
                
                # Draw spell name
                screen.blit(option_text, (option_x, option_y))
                
                # Draw SP cost
                sp_text = small_font.render(f"{spell.sp_cost} SP", True, BLUE)
                screen.blit(sp_text, (sp_cost_x, option_y))
        
        # Draw spell description for selected spell
        if self.selected_spell_option < len(spell_names):
            spell = self.player.spellbook.get_spell(options[self.selected_spell_option])
            if spell:
                desc_y = option_y_base + len(options) * option_line_height
                desc_text = small_font.render(spell.description, True, WHITE)
                screen.blit(desc_text, (option_x, desc_y))
                
    def _draw_battle_options(self, screen, font):
        """
        Draw the main battle options menu with scaling support.
        
        Args:
            screen: The pygame surface to draw on
            font: The font to use
        """
        from utils import scale_position, scale_dimensions
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Scale dimensions and position
        options_box_width, options_box_height = scale_dimensions(
            200, 120, original_width, original_height, current_width, current_height
        )
        options_box_x, options_box_y = scale_position(
            20, SCREEN_HEIGHT - 120 - 5, original_width, original_height, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, BLACK, (options_box_x, options_box_y, options_box_width, options_box_height))
        border_width = max(1, int(2 * (current_width / original_width)))
        pygame.draw.rect(screen, WHITE, (options_box_x, options_box_y, options_box_width, options_box_height), border_width)
        
        # Draw "Actions" header
        actions_text = font.render("Actions", True, WHITE)
        header_x = options_box_x + (options_box_width // 2) - (actions_text.get_width() // 2)
        header_y = options_box_y + int(10 * (current_height / original_height))
        screen.blit(actions_text, (header_x, header_y))
        
        # Scale text positions
        option_x = options_box_x + int(30 * (current_width / original_width))
        option_y_base = options_box_y + int(40 * (current_height / original_height))
        option_line_height = int(20 * (current_height / original_height))
        
        # Draw battle options
        for i, option in enumerate(self.battle_options):
            option_y = option_y_base + i * option_line_height
            
            if i == self.selected_option:
                # Highlight selected option
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
            screen.blit(option_text, (option_x, option_y))
                
    def _draw_player_stat_window(self, screen, font, small_font):
        """
        Draw the player's stat window with scaling support.
        Shows LV, XP, HP, and SP
        
        Args:
            screen: The Pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for detailed stats
        """
        from utils import scale_position, scale_dimensions
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Scale dimensions and position
        window_width, window_height = scale_dimensions(
            300, 80, original_width, original_height, current_width, current_height
        )
        window_x, window_y = scale_position(
            SCREEN_WIDTH - 300 - 20, SCREEN_HEIGHT - 80 - 5, 
            original_width, original_height, current_width, current_height
        )
        
        # Draw window background and border
        pygame.draw.rect(screen, BLACK, (window_x, window_y, window_width, window_height))
        border_width = max(1, int(2 * (current_width / original_width)))
        pygame.draw.rect(screen, GREEN, (window_x, window_y, window_width, window_height), border_width)
        
        # Draw player name and level at top of window
        player_name = font.render(f"Player  LV: {self.player.level}", True, GREEN)
        name_x = window_x + int(10 * (current_width / original_width))
        name_y = window_y + int(5 * (current_height / original_height))
        screen.blit(player_name, (name_x, name_y))
        
        # Scale bars
        bar_width = window_width - int(110 * (current_width / original_width))
        bar_height = int(15 * (current_height / original_height))
        bar_x = window_x + int(100 * (current_width / original_width))
        hp_bar_y = window_y + int(10 * (current_height / original_height))
        
        # Draw the HP bar background (depleted health shown as gray)
        pygame.draw.rect(screen, GRAY, (bar_x, hp_bar_y, bar_width, bar_height))
        hp_fill_width = int((self.player.hp / self.player.max_hp) * bar_width)
        pygame.draw.rect(screen, ORANGE, (bar_x, hp_bar_y, hp_fill_width, bar_height))
        
        # Draw HP text
        hp_text = small_font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, WHITE)
        hp_text_x = window_x + int(10 * (current_width / original_width))
        hp_text_y = hp_bar_y + int(2 * (current_height / original_height))
        screen.blit(hp_text, (hp_text_x, hp_text_y))

        # Draw SP as a bar with text
        sp_bar_y = hp_bar_y + bar_height + int(5 * (current_height / original_height))

        # Draw the SP bar background (depleted SP shown as gray)
        pygame.draw.rect(screen, GRAY, (bar_x, sp_bar_y, bar_width, bar_height))

        # Draw the current SP fill (active special points shown as bright blue)
        if self.player.max_sp > 0:  # Avoid division by zero
            sp_fill_width = int((self.player.sp / self.player.max_sp) * bar_width)
            pygame.draw.rect(screen, BLUE, (bar_x, sp_bar_y, sp_fill_width, bar_height))

        # Draw SP text
        sp_text = small_font.render(f"SP: {self.player.sp}/{self.player.max_sp}", True, WHITE)
        sp_text_x = window_x + int(10 * (current_width / original_width))
        sp_text_y = sp_bar_y + int(2 * (current_height / original_height))
        screen.blit(sp_text, (sp_text_x, sp_text_y))
        
        # Draw XP in bottom of window
        xp_text = small_font.render(f"XP: {self.player.experience}", True, WHITE)
        xp_text_x = window_x + int(10 * (current_width / original_width))
        xp_text_y = sp_bar_y + int(25 * (current_height / original_height))
        screen.blit(xp_text, (xp_text_x, xp_text_y))