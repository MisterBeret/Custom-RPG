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
                      BATTLE_OPTIONS, MAX_LOG_SIZE, ORIGINAL_WIDTH, ORIGINAL_HEIGHT,
                      ORANGE, BLUE, DARK_BLUE, PURPLE, YELLOW)

class BattleSystem:
    """
    Manages turn-based battles between player and enemies.
    """
    def __init__(self, player, enemies, text_speed_setting):
        """
        Initialize the battle system.
        
        Args:
            player: The player entity
            enemies: A list of enemy entities or a single enemy
            text_speed_setting: The current text speed setting
        """
        self.player = player
        
        # Ensure enemies is a list
        if not isinstance(enemies, list):
            self.enemies = [enemies]
        else:
            self.enemies = enemies
        
        self.action_processing = False  # Flag to prevent multiple actions per turn
        
        # Position enemies in a formation
        self._setup_enemy_formation()

        # Create targeting system for enemy selection
        from systems.targeting_system import TargetingSystem
        self.targeting_system = TargetingSystem(self.enemies)
        self.in_targeting_mode = False  # Whether player is selecting a target
        
        # Track the current enemy attack sequence
        self.current_enemy_index = 0
        
        # Determine who goes first based on speed
        # Compare player speed to the fastest enemy
        fastest_enemy_speed = max([enemy.spd for enemy in self.enemies]) if self.enemies else 0
        
        if player.spd >= fastest_enemy_speed:
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

        # Skill system additions
        self.in_skill_menu = False
        self.selected_skill_option = 0
        self.player_using_skill = False
        self.skill_animation_duration = ACTION_DELAY_DURATION  # Reuse action delay for skills
        self.current_skill = None
        
        # Ultimate system additions
        self.in_ultimate_menu = False
        self.selected_ultimate_option = 0
        self.player_using_ultimate = False
        self.ultimate_animation_duration = SPELL_ANIMATION_DURATION  # Make ultimates as flashy as spells
        self.current_ultimate = None

        # Passive system additions
        self.counter_may_trigger = False
        self.counter_triggered = False
        self.counter_message = ""
        self.counter_damage = 0

        self.player_countering = False  # Flag to track counter attack animation
        self.counter_animation_timer = 0  # Separate timer for counter animations
        
    def _setup_enemy_formation(self):
        """Position enemies in a formation based on their count."""
        enemy_count = len(self.enemies)
        
        # Get current screen dimensions
        current_width, current_height = pygame.display.get_surface().get_size()
        
        # Base enemy positions (we'll position enemies from the left side now)
        if enemy_count == 1:
            # Single enemy centered
            self.enemies[0].battle_position = 0
            self.enemies[0].rect.topleft = (current_width * 0.25, current_height * 0.4)
        elif enemy_count == 2:
            # Two enemies side by side
            self.enemies[0].battle_position = 0
            self.enemies[0].rect.topleft = (current_width * 0.2, current_height * 0.3)
            self.enemies[1].battle_position = 1
            self.enemies[1].rect.topleft = (current_width * 0.3, current_height * 0.5)
        elif enemy_count == 3:
            # Three enemies in triangle formation
            self.enemies[0].battle_position = 0
            self.enemies[0].rect.topleft = (current_width * 0.15, current_height * 0.3)
            self.enemies[1].battle_position = 1
            self.enemies[1].rect.topleft = (current_width * 0.25, current_height * 0.5)
            self.enemies[2].battle_position = 2
            self.enemies[2].rect.topleft = (current_width * 0.35, current_height * 0.4)
        elif enemy_count >= 4:
            # Four or more enemies in rows
            row1_count = min(2, enemy_count)
            row2_count = min(2, enemy_count - row1_count)
            row3_count = min(2, enemy_count - row1_count - row2_count)
            
            # First row (top)
            for i in range(row1_count):
                self.enemies[i].battle_position = i
                x_pos = current_width * (0.15 + 0.15 * i)
                y_pos = current_height * 0.25
                self.enemies[i].rect.topleft = (x_pos, y_pos)
                
            # Second row (middle)
            for i in range(row2_count):
                idx = row1_count + i
                self.enemies[idx].battle_position = idx
                x_pos = current_width * (0.2 + 0.15 * i)
                y_pos = current_height * 0.4
                self.enemies[idx].rect.topleft = (x_pos, y_pos)
                
            # Third row (bottom)
            for i in range(row3_count):
                idx = row1_count + row2_count + i
                self.enemies[idx].battle_position = idx
                x_pos = current_width * (0.25 + 0.15 * i)
                y_pos = current_height * 0.55
                self.enemies[idx].rect.topleft = (x_pos, y_pos)
                
            # Any remaining enemies
            for i in range(row1_count + row2_count + row3_count, enemy_count):
                idx = i
                self.enemies[idx].battle_position = idx
                x_pos = current_width * 0.3
                y_pos = current_height * (0.25 + 0.15 * (i - row1_count - row2_count - row3_count))
                self.enemies[idx].rect.topleft = (x_pos, y_pos)
        
        # Update original positions to match the new positions
        for enemy in self.enemies:
            scale_factor_x = ORIGINAL_WIDTH / current_width
            scale_factor_y = ORIGINAL_HEIGHT / current_height
            enemy.original_x = enemy.rect.x * scale_factor_x
            enemy.original_y = enemy.rect.y * scale_factor_y
    
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
            action: The action to process ("ATTACK", "DEFEND", "MOVE", "SKILL", etc.)
        """
        if self.turn == 0 and not self.action_processing:  # Player's turn and not already processing
            self.action_processing = True
            if action == "ATTACK":
                if len(self.enemies) == 1:
                    # With just one enemy, attack it directly
                    self._perform_player_attack(self.enemies[0])
                else:
                    # With multiple enemies, enter targeting mode
                    self.in_targeting_mode = True
                    self.targeting_system.start_targeting(self.enemies)
                    self.set_message("Select a target.")
                    self.action_processing = False  # Keep accepting input for target selection
                    
            elif action == "DEFEND":
                self.player.defend()
                self.set_message("You're defending! Incoming damage reduced and evasion increased!")
                # Reset the action delay timer
                self.action_delay = 0
                # Make sure we're setting action_processing to True
                self.action_processing = True
                
            elif action == "RUN":
                # Start flee animation (this will be replaced by MOVE later)
                self.player_fleeing = True
                self.animation_timer = 0
                self.set_message("You tried to flee!")
                
            # Handle SKILL action
            elif action == "SKILL":
                # Skill system is implemented now
                pass
                
            # Handle ULTIMATE action
            elif action == "ULTIMATE":
                # Ultimate system is now implemented
                pass
                
            # STATUS is still not implemented
            elif action == "STATUS":
                self.set_message("STATUS system not yet implemented.")
                self.action_processing = False

    def handle_player_input(self, event):
        """
        Handle player input for targeting and other interactive states.
        
        Args:
            event: The pygame event
            
        Returns:
            bool: True if input was handled, False otherwise
        """
        # Only handle inputs when in targeting mode
        if self.in_targeting_mode and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                # Navigate between enemies
                if event.key == pygame.K_LEFT:
                    self.targeting_system.previous_target()
                else:
                    self.targeting_system.next_target()
                return True
                
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Select the current target
                target = self.targeting_system.get_selected_target()
                if target:
                    # Disable targeting mode
                    self.in_targeting_mode = False
                    self.targeting_system.stop_targeting()
                    # Perform attack on selected target
                    self._perform_player_attack(target)
                return True
                
            elif event.key == pygame.K_ESCAPE:
                # Cancel targeting and return to battle menu
                self.in_targeting_mode = False
                self.action_processing = False
                return True
                
        return False
    
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
            
            # For damage spells, we need a target
            if spell.effect_type == "damage":
                if len(self.enemies) == 1:
                    # With just one enemy, target it directly
                    target = self.enemies[0]
                else:
                    # With multiple enemies, we need targeting mode
                    self.in_targeting_mode = True
                    self.targeting_system.start_targeting(self.enemies)
                    self.current_spell = spell  # Store the spell for later use
                    self.set_message(f"Select a target for {spell_name}.")
                    return True
            else:
                # Non-targeting spells (like healing) continue as normal
                target = None
                
            # Set the current spell for animation
            self.current_spell = spell
            self.action_processing = True
                
            # Start spell casting animation
            self.player_casting = True
            self.animation_timer = 0
                
            # Use the SP
            self.player.use_sp(spell.sp_cost)
                
            # Handle spell effects
            if spell.effect_type == "damage" and target:
                # Calculate magic damage
                damage = self.calculate_magic_damage(self.player, target, spell.base_power)
                target.take_damage(damage)
                    
                # Store the message for later display after animation
                if target.is_defeated():
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
    
    def use_skill(self, skill_name):
        """
        Process using a skill.
        
        Args:
            skill_name: The name of the skill to use
            
        Returns:
            bool: True if skill was used successfully, False otherwise
        """
        if self.turn == 0 and not self.action_processing:
            # Get the skill data
            skill = self.player.skillset.get_skill(skill_name)
            if not skill:
                self.set_message(f"You don't know the skill {skill_name}!")
                return False
                
            # Check if player has enough resources to use the skill
            if skill.cost_type == "sp" and self.player.sp < skill.sp_cost:
                self.set_message(f"Not enough SP to use {skill_name}!")
                return False
            elif skill.cost_type == "hp" and self.player.hp <= skill.hp_cost:
                self.set_message(f"Not enough HP to use {skill_name}!")
                return False
            elif skill.cost_type == "both" and (self.player.sp < skill.sp_cost or self.player.hp <= skill.hp_cost):
                self.set_message(f"Not enough resources to use {skill_name}!")
                return False
                
            # For skills that need a target, use targeting system
            if skill.effect_type == "analyze":
                if len(self.enemies) == 1:
                    # With just one enemy, target it directly
                    target = self.enemies[0]
                else:
                    # With multiple enemies, we need targeting mode
                    self.in_targeting_mode = True
                    self.targeting_system.start_targeting(self.enemies)
                    self.current_skill = skill  # Store the skill for later use
                    self.set_message(f"Select a target for {skill_name}.")
                    return True
            else:
                # Non-targeting skills continue as normal
                target = None
                    
            # Set the current skill for animation
            self.current_skill = skill
            self.action_processing = True
                
            # Start skill animation
            self.player_using_skill = True
            self.animation_timer = 0
                
            # Apply resource costs
            if skill.sp_cost > 0:
                self.player.use_sp(skill.sp_cost)
            if skill.hp_cost > 0:
                self.player.take_damage(skill.hp_cost)
                
            # Handle skill effects
            if skill.effect_type == "analyze" and target:
                # Store the message for later display after animation
                self.pending_message = f"Used {skill_name}! {target.__class__.__name__} stats:\nHP: {target.hp}/{target.max_hp}\nATK: {target.attack}\nDEF: {target.defense}\nSPD: {target.spd}\nACC: {target.acc}\nRES: {target.resilience}"
                
            # Add more skill effect types here as needed
                
            return True
        
        return False

    def use_ultimate(self, ultimate_name):
        """
        Process using an ultimate ability.
        
        Args:
            ultimate_name: The name of the ultimate to use
            
        Returns:
            bool: True if ultimate was used successfully, False otherwise
        """
        if self.turn == 0 and not self.action_processing:
            # Get the ultimate data
            ultimate = self.player.ultimates.get_ultimate(ultimate_name)
            if not ultimate:
                self.set_message(f"You don't know the ultimate {ultimate_name}!")
                return False
                
            # Check if the ultimate is available
            if not ultimate.available:
                self.set_message(f"{ultimate_name} has already been used! Rest to restore it.")
                return False
                
            # For ultimates that need a target, use targeting system
            if ultimate.effect_type == "damage":
                if len(self.enemies) == 1:
                    # With just one enemy, target it directly
                    target = self.enemies[0]
                else:
                    # With multiple enemies, we need targeting mode
                    self.in_targeting_mode = True
                    self.targeting_system.start_targeting(self.enemies)
                    self.current_ultimate = ultimate  # Store the ultimate for later use
                    self.set_message(f"Select a target for {ultimate_name}.")
                    return True
            else:
                # Non-targeting ultimates continue as normal
                target = None
                
            # Set the current ultimate for animation
            self.current_ultimate = ultimate
            self.action_processing = True
                
            # Start ultimate animation
            self.player_using_ultimate = True
            self.animation_timer = 0
                
            # Handle ultimate effects
            if ultimate.effect_type == "damage" and target:
                # Calculate damage with power multiplier
                damage = int(self.player.attack * ultimate.power_multiplier)
                
                # Apply damage to target
                target.take_damage(damage)
                
                # Mark as used
                ultimate.available = False
                
                # Store the message for later display after animation
                if target.is_defeated():
                    self.pending_message = f"Used {ultimate_name}! Dealt a massive {damage} damage! Enemy defeated!"
                    self.pending_victory = True
                else:
                    self.pending_message = f"Used {ultimate_name}! Dealt a massive {damage} damage!"
                
            # Add more ultimate effect types here as needed
                
            return True
        
        return False

    # Helper method to check if all enemies are defeated:
    def _check_all_enemies_defeated(self):
        """
        Check if all enemies are defeated.
        
        Returns:
            bool: True if all enemies are defeated, False otherwise
        """
        return all(enemy.is_defeated() for enemy in self.enemies)
    
    def _draw_ultimate_menu(self, screen, font, small_font):
        """
        Draw the ultimate ability selection menu with scaling support.
        
        Args:
            screen: The pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for details
        """
        from utils import scale_position, scale_dimensions
        from constants import RED, GREEN
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Scale menu dimensions and position
        ultimate_box_width, ultimate_box_height = scale_dimensions(
            250, 150, original_width, original_height, current_width, current_height
        )
        ultimate_box_x, ultimate_box_y = scale_position(
            20, SCREEN_HEIGHT - 150 - 5, original_width, original_height, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, BLACK, (ultimate_box_x, ultimate_box_y, ultimate_box_width, ultimate_box_height))
        border_width = max(1, int(2 * (current_width / original_width)))
        pygame.draw.rect(screen, RED, (ultimate_box_x, ultimate_box_y, ultimate_box_width, ultimate_box_height), border_width)
        
        # Draw "Ultimate" header
        ultimate_text = font.render("Ultimate", True, RED)
        header_x = ultimate_box_x + (ultimate_box_width // 2) - (ultimate_text.get_width() // 2)
        header_y = ultimate_box_y + int(10 * (current_height / original_height))
        screen.blit(ultimate_text, (header_x, header_y))
        
        # Get ultimate list from player's ultimates
        ultimate_names = self.player.ultimates.get_ultimate_names()
        # Add "BACK" option at the end
        options = ultimate_names + ["BACK"]
        
        # Scale text positions
        option_x = ultimate_box_x + int(30 * (current_width / original_width))
        option_y_base = ultimate_box_y + int(40 * (current_height / original_height))
        option_line_height = int(25 * (current_height / original_height))
        status_x = ultimate_box_x + int(150 * (current_width / original_width))
        
        # Draw each ultimate with availability status
        for i, ultimate_name in enumerate(options):
            option_y = option_y_base + i * option_line_height
            
            if ultimate_name == "BACK":
                # Draw BACK option
                if i == self.selected_ultimate_option:
                    option_text = font.render(f"> {ultimate_name}", True, WHITE)
                else:
                    option_text = font.render(f"  {ultimate_name}", True, GRAY)
                screen.blit(option_text, (option_x, option_y))
            else:
                # Get the ultimate data
                ultimate = self.player.ultimates.get_ultimate(ultimate_name)
                
                # Determine text color based on whether ultimate is available
                is_available = ultimate.available
                
                if i == self.selected_ultimate_option:
                    # Selected ultimate
                    if is_available:
                        name_color = WHITE  # Can use
                    else:
                        name_color = RED    # Can't use (already used)
                    option_text = font.render(f"> {ultimate_name}", True, name_color)
                else:
                    # Unselected ultimate
                    if is_available:
                        name_color = GRAY   # Can use
                    else:
                        name_color = RED    # Can't use (already used)
                    option_text = font.render(f"  {ultimate_name}", True, name_color)
                
                # Draw ultimate name
                screen.blit(option_text, (option_x, option_y))
                
                # Draw availability status
                status_text = small_font.render("READY" if is_available else "USED", True, 
                                            GREEN if is_available else RED)
                screen.blit(status_text, (status_x, option_y))
        
        # Draw ultimate description for selected ultimate
        if self.selected_ultimate_option < len(ultimate_names):
            ultimate = self.player.ultimates.get_ultimate(options[self.selected_ultimate_option])
            if ultimate:
                desc_y = option_y_base + len(options) * option_line_height
                desc_text = small_font.render(ultimate.description, True, WHITE)
                screen.blit(desc_text, (option_x, desc_y))
    
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

        # Update targeting system
        if self.in_targeting_mode:
            self.targeting_system.update()
        
        # Only proceed with other updates if text animation is complete
        if self.message_index < len(self.full_message):
            return
            
        # Handle counter passive effect after enemy attack message is shown
        if self.counter_triggered and self.turn == 1:
            # Get the current enemy safely
            if self.current_enemy_index < len(self.enemies):
                current_enemy = self.enemies[self.current_enemy_index]
                
                # Start counter-attack animation
                self.player_countering = True
                self.counter_animation_timer = 0
                self.counter_triggered = False
            else:
                # Handle error case
                self.counter_triggered = False
                self.turn = 0  # Return to player's turn as fallback
        
        # Handle counter-attack animation
        elif self.player_countering:
            self.counter_animation_timer += 1
            if self.counter_animation_timer >= self.animation_duration:
                self.player_countering = False
                self.counter_animation_timer = 0
                
                # Now that counter animation is complete, display the message
                self.set_message(self.counter_message)
                
                # Get the current enemy safely
                if self.current_enemy_index < len(self.enemies):
                    current_enemy = self.enemies[self.current_enemy_index]
                    
                    # Check if enemy was defeated by the counter
                    if current_enemy.is_defeated():
                        # Award XP to player
                        xp_gained = current_enemy.xp
                        self.player.gain_experience(xp_gained)
                        
                        # Add XP message to the log
                        self.message_log.append(f"You gained {xp_gained} XP!")
                        if len(self.message_log) > self.max_log_size:
                            self.message_log.pop(0)
                        
                        # Check if all enemies are defeated
                        if self._check_all_enemies_defeated():
                            self.battle_over = True
                            self.victory = True
                        else:
                            # Move to next enemy
                            self.current_enemy_index += 1
                            self.enemy_turn_processed = False
                    else:
                        # Switch to player's turn after counter effect
                        self.turn = 0
                        self.action_processing = False
                else:
                    # Safety fallback
                    self.turn = 0
                    self.action_processing = False
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
        
        # Handle player skill animation
        elif self.player_using_skill:
            self.animation_timer += 1
            if self.animation_timer >= self.skill_animation_duration:
                self.player_using_skill = False
                self.animation_timer = 0
                self.current_skill = None
                
                # Now that animation is complete, display the message
                self.set_message(self.pending_message)
                
                # Reset player's defense multiplier at end of turn if defending
                self.player.end_turn()
                
                # Switch to enemy's turn
                self.turn = 1
                self.enemy_turn_processed = False

                self.action_processing = False
        
        # Handle player ultimate animation
        elif self.player_using_ultimate:
            self.animation_timer += 1
            if self.animation_timer >= self.ultimate_animation_duration:
                self.player_using_ultimate = False
                self.animation_timer = 0
                self.current_ultimate = None
                
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
                    # We pass the battle system and current enemy for potential passive triggers
                    current_enemy = self.enemies[self.current_enemy_index]
                    passive_triggered, passive_message = self.player.take_damage(
                        self.pending_damage, 
                        damage_type="physical", 
                        attacker=current_enemy, 
                        battle_system=self
                    )
                    
                    # Display the standard attack message first
                    self.set_message(self.pending_message)
                    
                    # If a passive ability was triggered, store that info for display after the regular message
                    if passive_triggered:
                        self.counter_triggered = True
                        self.counter_message = passive_message
                else:
                    # If the attack missed, just show the regular message
                    self.set_message(self.pending_message)
                    self.counter_triggered = False
                
                # Check if player was defeated
                if self.player.is_defeated():
                    self.set_message(f"Enemy attacked for {self.pending_damage} damage! You were defeated!")
                    self.battle_over = True
                    self.counter_triggered = False
                else:
                    # Move to the next enemy's turn
                    current_enemy = self.enemies[self.current_enemy_index]
                    current_enemy.end_turn()
                    self.current_enemy_index += 1
                    
                    # If no counter was triggered, immediately start the next enemy's turn
                    if not self.counter_triggered:
                        self.enemy_attacking = False
                        self.enemy_turn_processed = False
        
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
                    
    def _perform_player_attack(self, target_enemy):
        """
        Execute the player's attack on a specific enemy.
        
        Args:
            target_enemy: The enemy to attack
        """
        # Start player attack animation
        self.player_attacking = True
        self.animation_timer = 0
        
        # Calculate hit chance and determine if attack hits
        hit_chance = self.calculate_hit_chance(self.player, target_enemy)
        attack_hits = random.random() < hit_chance
        
        if attack_hits:
            # Calculate damage
            damage = self.calculate_damage(self.player, target_enemy)
            target_enemy.take_damage(damage)
            
            # Store the message for later display after animation
            enemy_name = target_enemy.character_class.name if hasattr(target_enemy, 'character_class') and target_enemy.character_class else "Enemy"
            
            if target_enemy.is_defeated():
                self.pending_message = f"You attacked {enemy_name} for {damage} damage! Enemy defeated!"
                
                # Check if all enemies are defeated
                self.pending_victory = self._check_all_enemies_defeated()
            else:
                self.pending_message = f"You attacked {enemy_name} for {damage} damage!"
        else:
            # Attack missed
            enemy_name = target_enemy.character_class.name if hasattr(target_enemy, 'character_class') and target_enemy.character_class else "Enemy"
            self.pending_message = f"Your attack missed {enemy_name}!"
    
    def process_enemy_turn(self):
        """Process the enemy's turn in battle."""
        # Only proceed if it's enemy turn and no animation is active
        if self.turn != 1 or self.enemy_attacking or self.enemy_turn_processed:
            return
                
        # Check if we need to move to the next enemy
        if self.current_enemy_index < len(self.enemies):
            current_enemy = self.enemies[self.current_enemy_index]
            # All enemies have acted, reset for next round
            self.current_enemy_index = 0
            self.turn = 0  # Back to player turn
            self.enemy_turn_processed = True
            return
        else:
            # Reset enemy index or handle end of enemy turns
            self.current_enemy_index = 0
            self.turn = 0
                
        # Get the current enemy
        current_enemy = self.enemies[self.current_enemy_index]
            
        # Skip defeated enemies
        if current_enemy.is_defeated():
            self.current_enemy_index += 1
            return
                
        # Start enemy attack animation
        self.enemy_attacking = True
        self.animation_timer = 0

        # Calculate hit chance and determine if attack hits
        hit_chance = self.calculate_hit_chance(current_enemy, self.player)
        attack_hits = random.random() < hit_chance

        if attack_hits:
            # Calculate damage values
            self.pending_damage = self.calculate_damage(current_enemy, self.player)
            
            # For display purposes, calculate what damage would be without defending
            if self.player.defending:
                import math
                self.original_damage = self.pending_damage * 2
            else:
                self.original_damage = self.pending_damage
            
            # Prepare message based on player's defending status
            enemy_name = current_enemy.character_class.name if hasattr(current_enemy, 'character_class') and current_enemy.character_class else "Enemy"
            if self.player.defending:
                self.pending_message = f"{enemy_name} attacked! Your defense reduced damage from {self.original_damage} to {self.pending_damage}!"
            else:
                self.pending_message = f"{enemy_name} attacked for {self.pending_damage} damage!"
                
            # Store whether a counter passive might trigger
            self.counter_may_trigger = True
        else:
            # Attack missed
            enemy_name = current_enemy.character_class.name if hasattr(current_enemy, 'character_class') and current_enemy.character_class else "Enemy"
            self.pending_damage = 0
            self.counter_may_trigger = False
            # Prepare message based on why it might have missed
            if self.player.defending:
                self.pending_message = f"{enemy_name}'s attack missed! Your defensive stance helped you evade!"
            else:
                self.pending_message = f"{enemy_name}'s attack missed!"
                    
    def draw(self, screen):
        """
        Draw the battle scene with all enemies.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Import utils here to avoid circular imports
        from utils import scale_position, scale_dimensions
        from systems.battle_ui_helpers import draw_enemy_name_tags, draw_enemy_health_bars, draw_turn_order_indicator
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Draw background
        from systems.battle_visualizer import draw_battle_background
        draw_battle_background(screen)
        
        # Calculate animation offsets for player
        player_offset_x = 0
        
        if self.player_attacking or self.player_countering:
            # Move player toward active enemy during first half, then back
            # Player moves left (-) toward enemy
            animation_timer = self.animation_timer if self.player_attacking else self.counter_animation_timer
            current_enemy = self.targeting_system.get_selected_target() if self.targeting_system.active else \
                        (self.enemies[self.current_enemy_index] if self.current_enemy_index < len(self.enemies) else self.enemies[0])
                        
            target_offset = -20  # Base movement amount
            
            # Adjust movement direction based on enemy position
            if current_enemy and current_enemy.rect.centerx > self.player.rect.centerx:
                # Enemy is to the right, move right
                movement_dir = 1
            else:
                # Enemy is to the left, move left
                movement_dir = -1
                
            if animation_timer < self.animation_duration / 2:
                player_offset_x = int(target_offset * movement_dir * (animation_timer / (self.animation_duration / 2)))
            else:
                player_offset_x = int(target_offset * movement_dir * (1 - (animation_timer - self.animation_duration / 2) / (self.animation_duration / 2)))
        
        elif self.player_fleeing:
            # Move player off the right side of the screen
            player_offset_x = int(300 * (self.animation_timer / self.flee_animation_duration))
        
        elif self.player_casting:
            # For spell casting, add a subtle effect
            if self.animation_timer < self.spell_animation_duration / 2:
                player_offset_x = int(-10 * (self.animation_timer / (self.spell_animation_duration / 2)))
            else:
                player_offset_x = int(-10 * (1 - (self.animation_timer - self.spell_animation_duration / 2) / (self.spell_animation_duration / 2)))
        
        # Scale positions and dimensions
        player_pos_scaled = scale_position(self.player_pos[0], self.player_pos[1], 
                                        original_width, original_height, 
                                        current_width, current_height)
        
        player_size = scale_dimensions(50, 75, original_width, original_height, 
                                    current_width, current_height)
        
        # Scale offset values
        player_offset_x = int(player_offset_x * (current_width / original_width))
        
        # Draw player unless player has fled
        if not self.fled:
            # Draw player character
            pygame.draw.rect(screen, GREEN, 
                            (player_pos_scaled[0] + player_offset_x, 
                            player_pos_scaled[1], 
                            player_size[0], player_size[1]))
        
        # Draw all enemies
        for i, enemy in enumerate(self.enemies):
            if not enemy.is_defeated():  # Only draw active enemies
                # Calculate animation offsets for current enemy
                enemy_offset_x = 0
                if self.enemy_attacking and self.current_enemy_index == i:
                    # Only animate the currently attacking enemy
                    if self.animation_timer < self.animation_duration / 2:
                        # Move enemy toward player
                        if enemy.rect.centerx < self.player.rect.centerx:
                            # Enemy is to the left, move right
                            enemy_offset_x = int(30 * (self.animation_timer / (self.animation_duration / 2)))
                        else:
                            # Enemy is to the right, move left
                            enemy_offset_x = int(-30 * (self.animation_timer / (self.animation_duration / 2)))
                    else:
                        # Move enemy back to original position
                        if enemy.rect.centerx < self.player.rect.centerx:
                            # Enemy is to the left, move left
                            enemy_offset_x = int(30 * (1 - (self.animation_timer - self.animation_duration / 2) / (self.animation_duration / 2)))
                        else:
                            # Enemy is to the right, move right
                            enemy_offset_x = int(-30 * (1 - (self.animation_timer - self.animation_duration / 2) / (self.animation_duration / 2)))
                
                # Draw enemy with offset
                pygame.draw.rect(screen, enemy.color, 
                            (enemy.rect.x + enemy_offset_x, 
                                enemy.rect.y, 
                                enemy.rect.width, enemy.rect.height))
        
        # Draw enemy names and health bars
        draw_enemy_name_tags(screen, self.enemies)
        draw_enemy_health_bars(screen, self.enemies)
        
        # Draw turn order indicator at the top of the screen
        draw_turn_order_indicator(screen, self)
        
        # Draw any active battle effects
        if hasattr(self, 'visualizer'):
            self.visualizer.draw(screen)
        
        # Draw targeting system if active
        if self.in_targeting_mode:
            self.targeting_system.draw(screen)
        
        # Draw the battle UI
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
        
        # Draw battle options or spell/skill menu
        if self.turn == 0 and not self.battle_over and not self.player_attacking and not self.enemy_attacking and not self.player_fleeing and not self.player_casting and not self.player_using_skill and not self.player_using_ultimate and self.action_delay == 0:
            # Only display UI when the text is fully displayed
            if self.message_index >= len(self.full_message):
                if self.in_spell_menu:
                    self._draw_spell_menu(screen, font, small_font)
                elif self.in_skill_menu:
                    self._draw_skill_menu(screen, font, small_font)
                elif self.in_ultimate_menu:
                    self._draw_ultimate_menu(screen, font, small_font)
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
                
    def _draw_skill_menu(self, screen, font, small_font):
        """
        Draw the skill selection menu with scaling support.
        
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
        skill_box_width, skill_box_height = scale_dimensions(
            250, 150, original_width, original_height, current_width, current_height
        )
        skill_box_x, skill_box_y = scale_position(
            20, SCREEN_HEIGHT - 150 - 5, original_width, original_height, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, BLACK, (skill_box_x, skill_box_y, skill_box_width, skill_box_height))
        border_width = max(1, int(2 * (current_width / original_width)))
        pygame.draw.rect(screen, YELLOW, (skill_box_x, skill_box_y, skill_box_width, skill_box_height), border_width)
        
        # Draw "Skills" header
        skills_text = font.render("Skills", True, YELLOW)
        header_x = skill_box_x + (skill_box_width // 2) - (skills_text.get_width() // 2)
        header_y = skill_box_y + int(10 * (current_height / original_height))
        screen.blit(skills_text, (header_x, header_y))
        
        # Get skill list from player's skillset
        skill_names = self.player.skillset.get_skill_names()
        # Add "BACK" option at the end
        options = skill_names + ["BACK"]
        
        # Scale text positions
        option_x = skill_box_x + int(30 * (current_width / original_width))
        option_y_base = skill_box_y + int(40 * (current_height / original_height))
        option_line_height = int(25 * (current_height / original_height))
        cost_x = skill_box_x + int(150 * (current_width / original_width))
        
        # Draw each skill with cost
        for i, skill_name in enumerate(options):
            option_y = option_y_base + i * option_line_height
            
            if skill_name == "BACK":
                # Draw BACK option
                if i == self.selected_skill_option:
                    option_text = font.render(f"> {skill_name}", True, WHITE)
                else:
                    option_text = font.render(f"  {skill_name}", True, GRAY)
                screen.blit(option_text, (option_x, option_y))
            else:
                # Get the skill data
                skill = self.player.skillset.get_skill(skill_name)
                
                # Determine text color based on whether player has enough resources
                has_resources = True
                if skill.cost_type == "sp" and self.player.sp < skill.sp_cost:
                    has_resources = False
                elif skill.cost_type == "hp" and self.player.hp <= skill.hp_cost:
                    has_resources = False
                elif skill.cost_type == "both" and (self.player.sp < skill.sp_cost or self.player.hp <= skill.hp_cost):
                    has_resources = False
                
                if i == self.selected_skill_option:
                    # Selected skill
                    if has_resources:
                        name_color = WHITE  # Can use
                    else:
                        name_color = RED    # Can't use (not enough resources)
                    option_text = font.render(f"> {skill_name}", True, name_color)
                else:
                    # Unselected skill
                    if has_resources:
                        name_color = GRAY   # Can use
                    else:
                        name_color = RED    # Can't use (not enough resources)
                    option_text = font.render(f"  {skill_name}", True, name_color)
                
                # Draw skill name
                screen.blit(option_text, (option_x, option_y))
                
                # Draw cost if applicable
                if skill.cost_type != "none":
                    if skill.cost_type == "sp":
                        cost_text = small_font.render(f"{skill.sp_cost} SP", True, BLUE)
                    elif skill.cost_type == "hp":
                        cost_text = small_font.render(f"{skill.hp_cost} HP", True, ORANGE)
                    elif skill.cost_type == "both":
                        cost_text = small_font.render(f"{skill.hp_cost}HP/{skill.sp_cost}SP", True, PURPLE)
                    screen.blit(cost_text, (cost_x, option_y))
        
        # Draw skill description for selected skill
        if self.selected_skill_option < len(skill_names):
            skill = self.player.skillset.get_skill(options[self.selected_skill_option])
            if skill:
                desc_y = option_y_base + len(options) * option_line_height
                desc_text = small_font.render(skill.description, True, WHITE)
                screen.blit(desc_text, (option_x, desc_y))
    
    def _draw_battle_options(self, screen, font):
        """
        Draw the main battle options menu in a two-column layout.
        
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
            300, 160, original_width, original_height, current_width, current_height
        )
        options_box_x, options_box_y = scale_position(
            20, SCREEN_HEIGHT - 160 - 5, original_width, original_height, current_width, current_height
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
        left_column_x = options_box_x + int(30 * (current_width / original_width))
        right_column_x = options_box_x + int(160 * (current_width / original_width))
        option_y_base = options_box_y + int(40 * (current_height / original_height))
        option_line_height = int(25 * (current_height / original_height))
        
        # Draw battle options in two columns
        # Left column (first 4 options)
        for i in range(4):
            option_y = option_y_base + i * option_line_height
            option = self.battle_options[i]
            
            if i == self.selected_option:
                # Highlight selected option
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
            screen.blit(option_text, (left_column_x, option_y))
        
        # Right column (next 4 options)
        for i in range(4, 8):
            option_y = option_y_base + (i - 4) * option_line_height
            option = self.battle_options[i]
            
            if i == self.selected_option:
                # Highlight selected option
                option_text = font.render(f"> {option}", True, WHITE)
            else:
                option_text = font.render(f"  {option}", True, GRAY)
            screen.blit(option_text, (right_column_x, option_y))
                
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
    
    def check_battle_over(self):
        """
        Check if the battle is over (all enemies defeated).
        
        Returns:
            bool: True if battle is over, False otherwise
        """
        return all(enemy.is_defeated() for enemy in self.enemies)

    def award_experience(self):
        """
        Award experience to the player for defeated enemies.
        
        Returns:
            int: Total XP awarded
        """
        total_xp = sum(enemy.xp for enemy in self.enemies if enemy.is_defeated())
        self.player.gain_experience(total_xp)
        return total_xp