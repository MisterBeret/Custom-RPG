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
from systems.battle_formation import BattleFormation
from systems.targeting_system_updated import EnhancedTargetingSystem
from systems.turn_order import TurnOrder
from systems.battle_ui_party import draw_party_status, draw_turn_order_indicator
from entities.player import Player

class BattleSystem:
    """
    Manages turn-based battles between player party and enemies.
    """
    def __init__(self, party, enemies, text_speed_setting):
        """
        Initialize the battle system.
        
        Args:
            party: The player's party
            enemies: A list of enemy entities or a single enemy
            text_speed_setting: The current text speed setting
        """
        self.party = party
        
        # Ensure enemies is a list
        if not isinstance(enemies, list):
            self.enemies = [enemies]
        else:
            self.enemies = enemies
        
        # Initialize battle formation system
        current_width, current_height = pygame.display.get_surface().get_size()
        self.formation = BattleFormation(current_width, current_height)
        
        # Position party members and enemies
        self.formation.position_party_members(party)
        self.formation.position_enemies(self.enemies)
        
        # Action processing flag
        self.action_processing = False
        
        # Create enhanced targeting system
        self.targeting_system = EnhancedTargetingSystem(party, self.enemies)
        self.in_targeting_mode = False
        
        # Set up turn order
        self.turn_order = TurnOrder(party.active_members, self.enemies)
        
        # Get the first character to act
        current_combatant = self.turn_order.get_current()
        
        # Determine message based on who goes first
        if current_combatant in party.active_members:
            self.turn = 0  # Player's turn
            self.first_message = f"Battle started! {current_combatant.name} moves first!"
        else:
            self.turn = 1  # Enemy's turn
            self.first_message = f"Battle started! {current_combatant.name} moves first!"
            
        # Battle UI state
        self.full_message = self.first_message
        self.displayed_message = ""
        self.message_index = 0
        self.text_timer = 0
        self.message_log = [self.first_message]
        self.max_log_size = MAX_LOG_SIZE
        
        # Set text speed based on global setting
        self.set_text_speed(text_speed_setting)
        
        # Battle state variables
        self.battle_over = False
        self.victory = False
        self.pending_victory = False
        self.fled = False
        
        # Action delay timer
        self.action_delay = 0
        self.action_delay_duration = ACTION_DELAY_DURATION
        
        # Animation variables
        self.animation_timer = 0
        self.animation_duration = ATTACK_ANIMATION_DURATION
        self.flee_animation_duration = FLEE_ANIMATION_DURATION
        self.spell_animation_duration = SPELL_ANIMATION_DURATION
        
        # Character action states
        self.active_character = None  # Current character taking action
        self.character_attacking = False
        self.character_defending = False
        self.character_casting = False
        self.character_using_skill = False
        self.character_using_ultimate = False
        self.character_fleeing = False
        
        # Enemy action states
        self.enemy_attacking = False
        self.current_enemy = None
        
        # Battle options menu state
        self.battle_options = BATTLE_OPTIONS
        self.selected_option = 0
        
        # Menu state for special actions
        self.in_spell_menu = False
        self.selected_spell_option = 0
        self.current_spell = None
        
        self.in_skill_menu = False
        self.selected_skill_option = 0
        self.current_skill = None
        
        self.in_ultimate_menu = False
        self.selected_ultimate_option = 0
        self.current_ultimate = None
        
        # Passive ability trackers
        self.counter_triggered = False
        self.counter_message = ""
        self.character_countering = False
        self.counter_animation_timer = 0
        
        # Pending effects to apply after animation
        self.pending_damage = 0
        self.pending_message = ""
        self.target = None

    def get_current_character(self):
        """
        Get the character whose turn it currently is.
        
        Returns:
            The current character, or None if it's an enemy's turn
        """
        current = self.turn_order.get_current()
        if current in self.party.active_members:
            return current
        return None
    
    def get_current_enemy(self):
        """
        Get the enemy whose turn it currently is.
        
        Returns:
            The current enemy, or None if it's a player's turn
        """
        current = self.turn_order.get_current()
        if current in self.enemies:
            return current
        return None
    
    def is_player_turn(self):
        """
        Check if it's a player character's turn.
        
        Returns:
            bool: True if it's a player's turn, False if enemy
        """
        return self.turn_order.is_player_turn()
        
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
    
    def _calculate_hit_chance(self, attacker, defender):
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
    
    def _calculate_damage(self, attacker, defender):
        """
        Calculate damage based on attacker's ATK and defender's DEF stats.
        
        Args:
            attacker: The attacking entity
            defender: The defending entity
        
        Returns:
            int: The calculated damage amount (minimum 0)
        """
        # Calculate base damage as attacker's attack minus defender's defense
        damage = max(1, attacker.attack - defender.defense)
    
        # If defender is defending, reduce all damage by 50% (rounded up)
        if defender.defending:
            import math
            damage = math.ceil(damage / 2)
    
        return damage
    
    def _calculate_magic_damage(self, caster, target, base_power):
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
        damage = max(1, (caster.intelligence + base_power) - target.resilience)

        # If target is defending, reduce all damage by 50% (rounded up)
        if target.defending:
            import math
            damage = math.ceil(damage / 2)
    
        return damage
        
    def process_action(self, action, character=None):
        """
        Process a player action.
        
        Args:
            action: The action to process ("ATTACK", "DEFEND", "MOVE", etc.)
            character: The character performing the action (uses active character if None)
        """
        # Use the active character if none is provided
        if character is None:
            character = self.get_current_character()
            
        if not character or self.action_processing:
            return
            
        self.action_processing = True
        self.active_character = character
        
        if action == "ATTACK":
            # In multi-enemy battles, enter targeting mode
            if len(self.enemies) > 1:
                self.in_targeting_mode = True
                self.targeting_system.start_targeting(character, EnhancedTargetingSystem.ENEMIES)
                self.set_message(f"{character.name} is targeting an enemy")
                self.action_processing = False  # Allow targeting input
            else:
                # With just one enemy, attack it directly
                self._perform_attack(character, self.enemies[0])
                
        elif action == "DEFEND":
            character.defend()
            self.character_defending = True
            self.set_message(f"{character.name} is defending! Incoming damage reduced and evasion increased!")
            
            # Reset the action delay timer
            self.action_delay = 0
            
        elif action == "MOVE":
            # Start flee animation
            self.character_fleeing = True
            self.animation_timer = 0
            self.set_message(f"{character.name} tried to flee!")
            
        elif action == "ITEM":
            # Enter inventory selection mode (handled externally)
            # This will set action_processing to False when returning to battle
            self.active_character = character
            
        elif action == "SKILL":
            # Enter skill selection mode if character has any skills
            skill_names = character.skillset.get_skill_names()
            if skill_names:
                self.in_skill_menu = True
                self.selected_skill_option = 0
                self.active_character = character
                self.action_processing = False  # Allow skill selection
            else:
                self.set_message(f"{character.name} doesn't know any skills!")
                self.action_processing = False
                
        elif action == "MAGIC":
            # Enter spell selection mode if character has any spells
            spell_names = character.spellbook.get_spell_names()
            if spell_names:
                self.in_spell_menu = True
                self.selected_spell_option = 0
                self.active_character = character
                self.action_processing = False  # Allow spell selection
            else:
                self.set_message(f"{character.name} doesn't know any spells!")
                self.action_processing = False
                
        elif action == "ULTIMATE":
            # Enter ultimate selection mode if character has any ultimates
            ultimate_names = character.ultimates.get_ultimate_names()
            if ultimate_names:
                self.in_ultimate_menu = True
                self.selected_ultimate_option = 0
                self.active_character = character
                self.action_processing = False  # Allow ultimate selection
            else:
                self.set_message(f"{character.name} doesn't have any ultimate abilities!")
                self.action_processing = False
                
        elif action == "STATUS":
            # Show character status (not yet implemented)
            self.set_message(f"{character.name} STATUS - HP: {character.hp}/{character.max_hp}, SP: {character.sp}/{character.max_sp}")
            self.action_processing = False

    def handle_player_input(self, event):
        """
        Handle player input during battle.
        
        Args:
            event: The pygame event
            
        Returns:
            bool: True if input was handled, False otherwise
        """
        # Handle targeting mode input
        if self.in_targeting_mode and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                # Navigate between targets
                if event.key == pygame.K_LEFT:
                    self.targeting_system.previous_target()
                else:
                    self.targeting_system.next_target()
                return True
                
            elif event.key == pygame.K_TAB:
                # Switch between targeting enemies and allies
                self.targeting_system.switch_target_group()
                
                # Update message based on target group
                if self.targeting_system.target_group == EnhancedTargetingSystem.ENEMIES:
                    self.set_message(f"{self.active_character.name} is targeting an enemy")
                else:
                    self.set_message(f"{self.active_character.name} is targeting an ally")
                return True
                
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Select the current target
                target = self.targeting_system.get_selected_target()
                if target:
                    # Get the current action type
                    if self.in_spell_menu and self.current_spell:
                        # Cast spell on target
                        self._cast_spell(self.active_character, target, self.current_spell)
                        self.in_spell_menu = False
                    elif self.in_skill_menu and self.current_skill:
                        # Use skill on target
                        self._use_skill(self.active_character, target, self.current_skill)
                        self.in_skill_menu = False
                    elif self.in_ultimate_menu and self.current_ultimate:
                        # Use ultimate on target
                        self._use_ultimate(self.active_character, target, self.current_ultimate)
                        self.in_ultimate_menu = False
                    else:
                        # Regular attack
                        self._perform_attack(self.active_character, target)
                    
                    # Disable targeting mode
                    self.in_targeting_mode = False
                    self.targeting_system.stop_targeting()
                return True
                
            elif event.key == pygame.K_ESCAPE:
                # Cancel targeting and return to battle menu
                self.in_targeting_mode = False
                self.targeting_system.stop_targeting()
                self.action_processing = False  # Reset to allow new actions
                
                # Reset any special menu states
                self.in_spell_menu = False
                self.in_skill_menu = False
                self.in_ultimate_menu = False
                
                # Restore the previous message from log
                if len(self.message_log) > 0:
                    self.full_message = self.message_log[-1]
                    self.displayed_message = self.full_message
                    self.message_index = len(self.full_message)
                return True
                
        # Handle spell menu navigation
        elif self.in_spell_menu and event.type == pygame.KEYDOWN:
            character = self.active_character
            if not character:
                return False
                
            spell_options = character.spellbook.get_spell_names() + ["BACK"]
            
            if event.key == pygame.K_UP:
                self.selected_spell_option = (self.selected_spell_option - 1) % len(spell_options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_spell_option = (self.selected_spell_option + 1) % len(spell_options)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected_spell = spell_options[self.selected_spell_option]
                
                if selected_spell == "BACK":
                    # Return to main battle menu
                    self.in_spell_menu = False
                    self.action_processing = False
                else:
                    # Try to cast the spell
                    spell = character.spellbook.get_spell(selected_spell)
                    
                    # Check if player has enough SP
                    if character.sp < spell.sp_cost:
                        self.set_message(f"Not enough SP to cast {selected_spell}!")
                        return True
                    
                    # Determine if this spell needs a target
                    if spell.effect_type == "damage":
                        # Enter targeting mode
                        self.in_targeting_mode = True
                        self.targeting_system.start_targeting(character, EnhancedTargetingSystem.ENEMIES)
                        self.current_spell = spell
                        self.set_message(f"Select a target for {spell.name}")
                    elif spell.effect_type == "healing":
                        # Enter targeting mode for allies
                        self.in_targeting_mode = True
                        self.targeting_system.start_targeting(character, EnhancedTargetingSystem.ALLIES)
                        self.current_spell = spell
                        self.set_message(f"Select a target for {spell.name}")
                    else:
                        # Non-targeted spell
                        self._cast_spell(character, character, spell)  # Self-target
                        self.in_spell_menu = False
                return True
            elif event.key == pygame.K_ESCAPE:
                # Exit spell menu
                self.in_spell_menu = False
                self.action_processing = False
                return True
        
        # Handle skill menu navigation
        elif self.in_skill_menu and event.type == pygame.KEYDOWN:
            character = self.active_character
            if not character:
                return False
                
            skill_options = character.skillset.get_skill_names() + ["BACK"]
            
            if event.key == pygame.K_UP:
                self.selected_skill_option = (self.selected_skill_option - 1) % len(skill_options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_skill_option = (self.selected_skill_option + 1) % len(skill_options)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected_skill = skill_options[self.selected_skill_option]
                
                if selected_skill == "BACK":
                    # Return to main battle menu
                    self.in_skill_menu = False
                    self.action_processing = False
                else:
                    # Try to use the skill
                    skill = character.skillset.get_skill(selected_skill)
                    
                    # Check resource requirements
                    if skill.cost_type == "sp" and character.sp < skill.sp_cost:
                        self.set_message(f"Not enough SP to use {selected_skill}!")
                        return True
                    elif skill.cost_type == "hp" and character.hp <= skill.hp_cost:
                        self.set_message(f"Not enough HP to use {selected_skill}!")
                        return True
                    elif skill.cost_type == "both" and (character.sp < skill.sp_cost or character.hp <= skill.hp_cost):
                        self.set_message(f"Not enough resources to use {selected_skill}!")
                        return True
                    
                    # Determine if this skill needs a target
                    if skill.effect_type == "analyze":
                        # Enter targeting mode for enemies
                        self.in_targeting_mode = True
                        self.targeting_system.start_targeting(character, EnhancedTargetingSystem.ENEMIES)
                        self.current_skill = skill
                        self.set_message(f"Select a target for {skill.name}")
                    else:
                        # Self-targeting skill for now
                        self._use_skill(character, character, skill)
                        self.in_skill_menu = False
                return True
            elif event.key == pygame.K_ESCAPE:
                # Exit skill menu
                self.in_skill_menu = False
                self.action_processing = False
                return True
        
        # Handle ultimate menu navigation
        elif self.in_ultimate_menu and event.type == pygame.KEYDOWN:
            character = self.active_character
            if not character:
                return False
                
            ultimate_options = character.ultimates.get_ultimate_names() + ["BACK"]
            
            if event.key == pygame.K_UP:
                self.selected_ultimate_option = (self.selected_ultimate_option - 1) % len(ultimate_options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_ultimate_option = (self.selected_ultimate_option + 1) % len(ultimate_options)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected_ultimate = ultimate_options[self.selected_ultimate_option]
                
                if selected_ultimate == "BACK":
                    # Return to main battle menu
                    self.in_ultimate_menu = False
                    self.action_processing = False
                else:
                    # Try to use the ultimate
                    ultimate = character.ultimates.get_ultimate(selected_ultimate)
                    
                    # Check if the ultimate is available
                    if not ultimate.available:
                        self.set_message(f"{selected_ultimate} has already been used! Rest to restore it.")
                        return True
                    
                    # Determine if this ultimate needs a target
                    if ultimate.effect_type == "damage":
                        # Enter targeting mode
                        self.in_targeting_mode = True
                        self.targeting_system.start_targeting(character, EnhancedTargetingSystem.ENEMIES)
                        self.current_ultimate = ultimate
                        self.set_message(f"Select a target for {ultimate.name}")
                    else:
                        # Self-targeting ultimate for now
                        self._use_ultimate(character, character, ultimate)
                        self.in_ultimate_menu = False
                return True
            elif event.key == pygame.K_ESCAPE:
                # Exit ultimate menu
                self.in_ultimate_menu = False
                self.action_processing = False
                return True
        
        # Handle regular battle menu navigation
        elif self.is_player_turn() and event.type == pygame.KEYDOWN:
            # Only handle input during player's turn and when no animation is in progress
            if (self.character_attacking or self.character_defending or self.character_casting or 
                self.character_using_skill or self.character_using_ultimate or self.character_fleeing or
                self.action_delay > 0 or self.action_processing):
                return False
                
            # Only accept inputs when text is fully displayed
            if self.message_index < len(self.full_message):
                # If message is still scrolling, pressing any key will display it immediately
                self.displayed_message = self.full_message
                self.message_index = len(self.full_message)
                return True
                
            # Get the current character whose turn it is
            character = self.get_current_character()
            if not character:
                return False
                
            # Handle navigation and selection
            if event.key == pygame.K_UP:
                # Move up in the same column with wrap-around
                if self.selected_option >= 4:  # Right column
                    # Move up in right column (wrap to bottom if at top)
                    current_position = self.selected_option - 4
                    new_position = (current_position - 1) % 4
                    self.selected_option = 4 + new_position
                else:  # Left column
                    # Move up in left column (wrap to bottom if at top)
                    self.selected_option = (self.selected_option - 1) % 4
                return True
            elif event.key == pygame.K_DOWN:
                # Move down in the same column with wrap-around
                if self.selected_option >= 4:  # Right column
                    # Move down in right column
                    current_position = self.selected_option - 4
                    new_position = (current_position + 1) % 4
                    self.selected_option = 4 + new_position
                else:  # Left column
                    # Move down in left column
                    self.selected_option = (self.selected_option + 1) % 4
                return True
            elif event.key == pygame.K_LEFT:
                # Move to left column from right, or wrap around to right column from left
                if self.selected_option >= 4:  # Right column to left
                    self.selected_option -= 4
                else:  # Left column to right (wrap around)
                    self.selected_option += 4
                return True
            elif event.key == pygame.K_RIGHT:
                # Move to right column from left, or wrap around to left column from right
                if self.selected_option < 4:  # Left column to right
                    self.selected_option += 4
                else:  # Right column to left (wrap around)
                    self.selected_option -= 4
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected_action = self.battle_options[self.selected_option]
                self.process_action(selected_action, character)
                return True
            
        # Check if battle has ended and player pressed ENTER to continue
        elif self.battle_over and self.message_index >= len(self.full_message):
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE):
                # Signal that battle is ended (handled by main game loop)
                return True
                
        return False
    
    def _perform_attack(self, attacker, target):
        """
        Execute an attack from one character to a target.
        
        Args:
            attacker: The attacking character/enemy
            target: The target of the attack
        """
        # Start attack animation
        self.character_attacking = True
        self.animation_timer = 0
        self.action_processing = True
        self.active_character = attacker
        self.target = target
        
        # Calculate and use hit chance
        hit_chance = self._calculate_hit_chance(attacker, target)
        attack_hits = random.random() < hit_chance
        
        if attack_hits:
            # Calculate damage
            damage = self._calculate_damage(attacker, target)
            
            # Store damage for application after animation
            self.pending_damage = damage
            
            # Set message based on attacker and target
            attacker_name = attacker.name
            target_name = target.name
            
            self.pending_message = f"{attacker_name} attacked {target_name} for {damage} damage!"
        else:
            # Attack missed
            attacker_name = attacker.name
            target_name = target.name
            self.pending_message = f"{attacker_name}'s attack on {target_name} missed!"
            self.pending_damage = 0
    
    def _cast_spell(self, caster, target, spell):
        """
        Cast a spell from a character to a target.
        
        Args:
            caster: The character casting the spell
            target: The target of the spell
            spell: The spell being cast
        """
        # Start spell casting animation
        self.character_casting = True
        self.animation_timer = 0
        self.action_processing = True
        self.active_character = caster
        self.target = target
        self.current_spell = spell
        
        # Apply SP cost
        caster.use_sp(spell.sp_cost)
        
        # Handle spell effects based on type
        if spell.effect_type == "damage":
            # Calculate magic damage
            damage = self._calculate_magic_damage(caster, target, spell.base_power)
            
            # Store damage for application after animation
            self.pending_damage = damage
            
            # Set message
            caster_name = caster.name
            target_name = target.name
            self.pending_message = f"{caster_name} cast {spell.name} on {target_name} for {damage} magic damage!"
        
        elif spell.effect_type == "healing":
            # Calculate healing amount (add intelligence to base power)
            healing_amount = spell.base_power + caster.intelligence
            
            # Store original HP to calculate actual healing
            original_hp = target.hp
            
            # Store healing info for application after animation
            self.pending_damage = -healing_amount  # Negative indicates healing
            
            # Set message
            caster_name = caster.name
            target_name = target.name
            self.pending_message = f"{caster_name} cast {spell.name} on {target_name} to restore HP!"
    
    def _use_skill(self, user, target, skill):
        """
        Use a skill from a character on a target.
        
        Args:
            user: The character using the skill
            target: The target of the skill
            skill: The skill being used
        """
        # Start skill animation
        self.character_using_skill = True
        self.animation_timer = 0
        self.action_processing = True
        self.active_character = user
        self.target = target
        self.current_skill = skill
        
        # Apply resource costs
        if skill.cost_type == "sp" or skill.cost_type == "both":
            user.use_sp(skill.sp_cost)
            
        if skill.cost_type == "hp" or skill.cost_type == "both":
            user.take_damage(skill.hp_cost)
        
        # Handle skill effects based on type
        if skill.effect_type == "analyze":
            # Get target stats
            target_stats = (
                f"{target.name} stats:\n"
                f"HP: {target.hp}/{target.max_hp}\n"
                f"ATK: {target.attack}\n"
                f"DEF: {target.defense}\n"
                f"SPD: {target.spd}\n"
                f"ACC: {target.acc}\n"
                f"RES: {target.resilience}"
            )
            
            # Set message
            user_name = user.name
            target_name = target.name
            self.pending_message = f"{user_name} used {skill.name} on {target_name}! {target_stats}"
            self.pending_damage = 0
    
    def _use_ultimate(self, user, target, ultimate):
        """
        Use an ultimate ability from a character on a target.
        
        Args:
            user: The character using the ultimate
            target: The target of the ultimate
            ultimate: The ultimate ability being used
        """
        # Start ultimate animation
        self.character_using_ultimate = True
        self.animation_timer = 0
        self.action_processing = True
        self.active_character = user
        self.target = target
        self.current_ultimate = ultimate
        
        # Mark ultimate as used
        ultimate.available = False
        
        # Handle ultimate effects based on type
        if ultimate.effect_type == "damage":
            # Calculate damage with power multiplier
            damage = int(user.attack * ultimate.power_multiplier)
            
            # Store damage for application after animation
            self.pending_damage = damage
            
            # Set message
            user_name = user.name
            target_name = target.name
            self.pending_message = f"{user_name} used {ultimate.name} on {target_name} for a massive {damage} damage!"

    # Helper method to check if all enemies are defeated:
    def _check_all_enemies_defeated(self):
        """
        Check if all enemies are defeated.
        
        Returns:
            bool: True if all enemies are defeated, False otherwise
        """
        return all(enemy.is_defeated() for enemy in self.enemies)
    
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
            
        # Get the current combatant
        current_combatant = self.turn_order.get_current()
        
        # Handle counter passive effect after enemy attack message is shown
        if self.counter_triggered and not isinstance(current_combatant, Player):
            # Handle counter attack
            character = self.active_character
            
            # Start counter-attack animation
            self.character_countering = True
            self.counter_animation_timer = 0
            self.counter_triggered = False
        
        # Handle counter-attack animation
        elif self.character_countering:
            self.counter_animation_timer += 1
            if self.counter_animation_timer >= self.animation_duration:
                self.character_countering = False
                self.counter_animation_timer = 0
                
                # Now that counter animation is complete, display the message
                self.set_message(self.counter_message)
                
                # Check if enemy was defeated by the counter
                if self.target and self.target.is_defeated():
                    # Check if all enemies are defeated
                    if self._check_all_enemies_defeated():
                        self.victory = True
                        self.battle_over = True
                        self.set_message("Victory! All enemies defeated!")
                    else:
                        # Remove the defeated enemy from turn order
                        self.turn_order.remove_combatant(self.target)
                else:
                    # Only advance turn if counter didn't defeat target
                    current_combatant = self.turn_order.advance()
                    self.action_processing = False
        
        # Handle player attack animation
        elif self.character_attacking:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_duration:
                self.character_attacking = False
                self.animation_timer = 0
                
                # Apply damage to target
                if self.target and self.pending_damage > 0:
                    # Check for passive triggers when taking damage
                    passive_triggered, passive_message = self.target.take_damage(
                        self.pending_damage, 
                        damage_type="physical", 
                        attacker=self.active_character
                    )
                    
                    # Store counter information if passive was triggered
                    if passive_triggered:
                        self.counter_triggered = True
                        self.counter_message = passive_message
                
                # Display the attack message
                self.set_message(self.pending_message)
                
                # Check if target was defeated
                if self.target and self.target.is_defeated():
                    # Award XP to attacker
                    if hasattr(self.target, 'xp'):
                        xp_gained = self.target.xp
                        self.active_character.gain_experience(xp_gained)
                        self.message_log.append(f"{self.active_character.name} gained {xp_gained} XP!")
                    
                    # Check if all enemies are defeated
                    if self._check_all_enemies_defeated():
                        self.victory = True
                        self.battle_over = True
                        self.set_message("Victory! All enemies defeated!")
                        return
                    else:
                        # Remove the defeated enemy from turn order
                        self.turn_order.remove_combatant(self.target)
                
                # End current character's turn if not already done
                if self.active_character:
                    self.active_character.end_turn()
                
                # Advance to next combatant if battle is not over
                if not self.battle_over:
                    current_combatant = self.turn_order.advance()
                    self.action_processing = False
        
        # Handle player skill usage animation
        elif self.character_using_skill:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_duration:
                self.character_using_skill = False
                self.animation_timer = 0
                
                # Display the skill message
                self.set_message(self.pending_message)
                
                # End current character's turn
                if self.active_character:
                    self.active_character.end_turn()
                
                # Advance to next combatant
                current_combatant = self.turn_order.advance()
                self.action_processing = False
        
        # Handle player ultimate usage animation
        elif self.character_using_ultimate:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_duration:
                self.character_using_ultimate = False
                self.animation_timer = 0
                
                # Apply ultimate effect to target
                if self.target and self.pending_damage > 0:
                    self.target.take_damage(self.pending_damage)
                
                # Display the ultimate message
                self.set_message(self.pending_message)
                
                # Check if target was defeated
                if self.target and self.target.is_defeated():
                    # Award XP to character
                    if hasattr(self.target, 'xp'):
                        xp_gained = self.target.xp
                        self.active_character.gain_experience(xp_gained)
                        self.message_log.append(f"{self.active_character.name} gained {xp_gained} XP!")
                    
                    # Check if all enemies are defeated
                    if self._check_all_enemies_defeated():
                        self.victory = True
                        self.battle_over = True
                        self.set_message("Victory! All enemies defeated!")
                        return
                    else:
                        # Remove the defeated enemy from turn order
                        self.turn_order.remove_combatant(self.target)
                
                # End current character's turn
                if self.active_character:
                    self.active_character.end_turn()
                
                # Advance to next combatant if battle is not over
                if not self.battle_over:
                    current_combatant = self.turn_order.advance()
                    self.action_processing = False
        
        # Handle enemy attack animation
        elif self.enemy_attacking:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_duration:
                self.enemy_attacking = False
                self.animation_timer = 0
                
                # Apply damage to target (only if attack didn't miss)
                if "missed" not in self.pending_message and self.target and self.pending_damage > 0:
                    # We pass the battle system and current enemy for potential passive triggers
                    passive_triggered, passive_message = self.target.take_damage(
                        self.pending_damage, 
                        damage_type="physical", 
                        attacker=self.current_enemy,
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
                
                # Check if target was defeated
                if self.target and self.target.is_defeated():
                    # Check if all party members are defeated
                    if self._check_all_party_defeated():
                        self.battle_over = True
                        self.victory = False
                        self.set_message("Defeat! All party members have fallen!")
                        return
                    else:
                        # Remove the defeated character from turn order
                        self.turn_order.remove_combatant(self.target)
                
                # End current enemy's turn
                if self.current_enemy:
                    self.current_enemy.end_turn()
                
                # Advance to next combatant if battle is not over
                if not self.battle_over and not self.counter_triggered:
                    current_combatant = self.turn_order.advance()
                    self.action_processing = False
        
        # Handle fleeing animation
        elif self.character_fleeing:
            self.animation_timer += 1
            if self.animation_timer >= self.flee_animation_duration:
                self.character_fleeing = False
                self.animation_timer = 0
                self.set_message(f"{self.active_character.name} fled from battle!")
                self.battle_over = True
                self.fled = True
                self.action_processing = False
        
        # Handle delay for the defend action
        elif self.character_defending:
            self.action_delay += 1
            if self.action_delay >= self.action_delay_duration:
                self.action_delay = 0
                self.character_defending = False
                
                # End current character's turn
                if self.active_character:
                    self.active_character.end_turn()
                
                # Advance to next combatant
                current_combatant = self.turn_order.advance()
                self.action_processing = False
        
        # Process enemy turn if it's enemy's turn and no animation is active
        elif not self.is_player_turn() and not self.enemy_attacking and not self.action_processing:
            self.process_enemy_turn()
        
        # Ensure battle flow consistency
        self._ensure_battle_flow_consistency()
    
    def process_enemy_turn(self):
        """Process the current enemy's turn in battle."""
        # Get the current enemy
        self.current_enemy = self.get_current_enemy()
        if not self.current_enemy:
            return
        
        # Start enemy attack animation
        self.enemy_attacking = True
        self.animation_timer = 0
        self.action_processing = True
        
        # Choose a random target from active party members
        valid_targets = [c for c in self.party.active_members if not c.is_defeated()]
        if not valid_targets:
            # No valid targets, end battle
            self.battle_over = True
            self.victory = False
            self.set_message("Defeat! All party members have fallen!")
            return
        
        # Select random target for now (could be more strategic in the future)
        target = random.choice(valid_targets)
        self.target = target
        
        # Calculate hit chance and determine if attack hits
        hit_chance = self._calculate_hit_chance(self.current_enemy, target)
        attack_hits = random.random() < hit_chance
        
        if attack_hits:
            # Calculate damage
            damage = self._calculate_damage(self.current_enemy, target)
            self.pending_damage = damage
            
            # Prepare message
            enemy_name = self.current_enemy.name
            target_name = target.name
            
            if target.defending:
                original_damage = damage * 2  # Approximate original damage
                self.pending_message = f"{enemy_name} attacked {target_name}! Defense reduced damage from {original_damage} to {damage}!"
            else:
                self.pending_message = f"{enemy_name} attacked {target_name} for {damage} damage!"
        else:
            # Attack missed
            enemy_name = self.current_enemy.name
            target_name = target.name
            
            if target.defending:
                self.pending_message = f"{enemy_name}'s attack on {target_name} missed! Their defensive stance helped them evade!"
            else:
                self.pending_message = f"{enemy_name}'s attack on {target_name} missed!"
                
            self.pending_damage = 0
    
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
    
    def _check_all_enemies_defeated(self):
        """
        Check if all enemies are defeated.
        
        Returns:
            bool: True if all enemies are defeated, False otherwise
        """
        return all(enemy.is_defeated() for enemy in self.enemies)
    
    def _check_all_party_defeated(self):
        """
        Check if all party members are defeated.
        
        Returns:
            bool: True if all party members are defeated, False otherwise
        """
        return all(character.is_defeated() for character in self.party.active_members)
    
    def _ensure_battle_flow_consistency(self):
        """Helper method to ensure battle flow remains consistent."""
        # Check for impossible states and fix them
        if self.battle_over:
            # If battle is over, ensure action processing is False
            self.action_processing = False
            return
            
        # Check if there are any valid combatants left
        if not self.turn_order.turn_queue:
            # Regenerate turn order
            self.turn_order.generate_turn_order()
            
            # If still no valid combatants, end the battle
            if not self.turn_order.turn_queue:
                self.battle_over = True
                
                # Determine victory/defeat based on remaining characters
                if self._check_all_enemies_defeated():
                    self.victory = True
                    self.set_message("Victory! All enemies defeated!")
                elif self._check_all_party_defeated():
                    self.victory = False
                    self.set_message("Defeat! All party members have fallen!")
                return
            
        # Check if the current character is defeated
        current = self.turn_order.get_current()
        if current and current.is_defeated():
            # Advance to the next non-defeated combatant
            self.turn_order.advance()
            self.action_processing = False
                    self.active_character.end_turn()
                
                # Advance to next combatant if battle is not over
                if not self.battle_over:
                    current_combatant = self.turn_order.advance()
                    self.action_processing = False
        
        # Handle player spell casting animation
        elif self.character_casting:
            self.animation_timer += 1
            if self.animation_timer >= self.spell_animation_duration:
                self.character_casting = False
                self.animation_timer = 0
                
                # Apply spell effect to target
                if self.target:
                    if self.pending_damage > 0:
                        # Damage spell
                        self.target.take_damage(self.pending_damage)
                    elif self.pending_damage < 0:
                        # Healing spell (negative damage)
                        original_hp = self.target.hp
                        self.target.hp = min(self.target.hp - self.pending_damage, self.target.max_hp)
                        actual_healing = self.target.hp - original_hp
                        
                        # Update the message with actual healing amount
                        self.pending_message = self.pending_message.replace("to restore HP", f"restoring {actual_healing} HP")
                
                # Display the spell message
                self.set_message(self.pending_message)
                
                # Check if target was defeated (for damage spells)
                if self.target and self.target.is_defeated():
                    # Award XP to caster
                    if hasattr(self.target, 'xp'):
                        xp_gained = self.target.xp
                        self.active_character.gain_experience(xp_gained)
                        self.message_log.append(f"{self.active_character.name} gained {xp_gained} XP!")
                    
                    # Check if all enemies are defeated
                    if self._check_all_enemies_defeated():
                        self.victory = True
                        self.battle_over = True
                        self.set_message("Victory! All enemies defeated!")
                        return
                    else:
                        # Remove the defeated enemy from turn order
                        self.turn_order.remove_combatant(self.target)
                
                # End current character's turn
                if self.active_character:
                    self.active_character.end_turn()
                
                # Advance to next combatant if battle is not over
                if not self.battle_over:
                    current_combatant = self.turn_order.advance()
                    self.action_processing = False
        
        # Handle player skill usage animation
        elif self.character_using_skill:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_duration:
                self.character_using_skill = False
                self.animation_timer = 0
                
                # Display the skill message
                self.set_message(self.pending_message)
                
                # End current character's turn
                if self.active_character:
                    self.active_character.end_turn()
                
                # Advance to next combatant
                current_combatant = self.turn_order.advance()
                self.action_processing = False
        
        # Handle player ultimate usage animation
        elif self.character_using_ultimate:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_duration:
                self.character_using_ultimate = False
                self.animation_timer = 0
                
                # Apply ultimate effect to target
                if self.target and self.pending_damage > 0:
                    self.target.take_damage(self.pending_damage)
                
                # Display the ultimate message
                self.set_message(self.pending_message)
                
                # Check if target was defeated
                if self.target and self.target.is_defeated():
                    # Award XP to character
                    if hasattr(self.target, 'xp'):
                        xp_gained = self.target.xp
                        self.active_character.gain_experience(xp_gained)
                        self.message_log.append(f"{self.active_character.name} gained {xp_gained} XP!")
                    
                    # Check if all enemies are defeated
                    if self._check_all_enemies_defeated():
                        self.victory = True
                        self.battle_over = True
                        self.set_message("Victory! All enemies defeated!")
                        return
                    else:
                        # Remove the defeated enemy from turn order
                        self.turn_order.remove_combatant(self.target)
                
                # End current character's turn
                if self.active_character:
                    self.active_character.end_turn()
                
                # Advance to next combatant if battle is not over
                if not self.battle_over:
                    current_combatant = self.turn_order.advance()
                    self.action_processing = False
        
        # Handle enemy attack animation
        elif self.enemy_attacking:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_duration:
                self.enemy_attacking = False
                self.animation_timer = 0
                
                # Apply damage to target (only if attack didn't miss)
                if "missed" not in self.pending_message and self.target and self.pending_damage > 0:
                    # We pass the battle system and current enemy for potential passive triggers
                    passive_triggered, passive_message = self.target.take_damage(
                        self.pending_damage, 
                        damage_type="physical", 
                        attacker=self.current_enemy,
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
                
                # Check if target was defeated
                if self.target and self.target.is_defeated():
                    # Check if all party members are defeated
                    if self._check_all_party_defeated():
                        self.battle_over = True
                        self.victory = False
                        self.set_message("Defeat! All party members have fallen!")
                        return
                    else:
                        # Remove the defeated character from turn order
                        self.turn_order.remove_combatant(self.target)
                
                # End current enemy's turn
                if self.current_enemy:
                    self.current_enemy.end_turn()
                
                # Advance to next combatant if battle is not over and no counter was triggered
                if not self.battle_over and not self.counter_triggered:
                    current_combatant = self.turn_order.advance()
                    self.action_processing = False
        
        # Handle fleeing animation
        elif self.character_fleeing:
            self.animation_timer += 1
            if self.animation_timer >= self.flee_animation_duration:
                self.character_fleeing = False
                self.animation_timer = 0
                self.set_message(f"{self.active_character.name} fled from battle!")
                self.battle_over = True
                self.fled = True
                self.action_processing = False
        
        # Handle delay for the defend action
        elif self.character_defending:
            self.action_delay += 1
            if self.action_delay >= self.action_delay_duration:
                self.action_delay = 0
                self.character_defending = False
                
                # End current character's turn
                if self.active_character:
                    self.active_character.end_turn()
                
                # Advance to next combatant
                current_combatant = self.turn_order.advance()
                self.action_processing = False
        
        # Process enemy turn if it's enemy's turn and no animation is active
        elif not self.is_player_turn() and not self.enemy_attacking and not self.action_processing:
            self.process_enemy_turn()
        
        # Check if it's a player's turn but no action is being taken
        elif self.is_player_turn() and not self.action_processing:
            # Get the current character
            current_character = self.get_current_character()
            
            # If character is defeated, move to next turn
            if current_character and current_character.is_defeated():
                current_combatant = self.turn_order.advance()
        
        # Ensure battle flow consistency
        self._ensure_battle_flow_consistency()
    
    def process_enemy_turn(self):
        """Process the enemy's turn in battle."""
        # Only proceed if it's enemy turn and no animation is active
        if self.turn != 1 or self.enemy_attacking or self.enemy_turn_processed:
            return
                
        # Check if we've gone through all enemies
        if self.current_enemy_index >= len(self.enemies):
            # All enemies have acted, reset for next round
            self.current_enemy_index = 0
            self.turn = 0  # Back to player turn
            self.enemy_turn_processed = True
            self.action_processing = False  # Ensure flag is reset
            return
                
        # Get the current enemy
        current_enemy = self.enemies[self.current_enemy_index]
            
        # Skip defeated enemies
        if current_enemy.is_defeated():
            self.current_enemy_index += 1
            # Recursively call this method to process the next enemy
            self.process_enemy_turn()
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
        Draw the battle scene with all characters and enemies.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Import utils here to avoid circular imports
        from utils import scale_position, scale_dimensions
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Draw background
        from systems.battle_visualizer import draw_battle_background
        draw_battle_background(screen)
        
        # Draw all party members
        for character in self.party.active_members:
            if not character.is_defeated():
                # Calculate animation offsets
                offset_x = 0
                offset_y = 0
                
                if self.character_attacking and character == self.active_character:
                    # Move character toward enemy during attack
                    if self.animation_timer < self.animation_duration / 2:
                        # Move toward target
                        if hasattr(self.target, 'battle_pos_x'):
                            # Direction vector
                            dx = self.target.battle_pos_x - character.battle_pos_x
                            move_dist = int(30 * (current_width / original_width))
                            # Move in the direction of the target
                            offset_x = int(move_dist * (dx / abs(dx) if dx != 0 else 0) * 
                                         (self.animation_timer / (self.animation_duration / 2)))
                    else:
                        # Move back to position
                        if hasattr(self.target, 'battle_pos_x'):
                            dx = self.target.battle_pos_x - character.battle_pos_x
                            move_dist = int(30 * (current_width / original_width))
                            # Return from the direction of the target
                            offset_x = int(move_dist * (dx / abs(dx) if dx != 0 else 0) * 
                                         (1 - (self.animation_timer - self.animation_duration / 2) / 
                                          (self.animation_duration / 2)))
                
                # Draw character with offset
                pygame.draw.rect(screen, character.color,
                                (character.rect.x + offset_x,
                                 character.rect.y + offset_y,
                                 character.rect.width,
                                 character.rect.height))
                                 
                # Draw character name above them
                name_font = pygame.font.SysFont('Arial', 14)
                name_text = name_font.render(character.name, True, WHITE)
                name_x = character.rect.centerx - name_text.get_width() // 2
                name_y = character.rect.top - name_text.get_height() - 5
                screen.blit(name_text, (name_x, name_y))
        
        # Draw all enemies
        for enemy in self.enemies:
            if not enemy.is_defeated():
                # Calculate animation offsets
                offset_x = 0
                offset_y = 0
                
                if self.enemy_attacking and enemy == self.current_enemy:
                    # Move enemy toward character during attack
                    if self.animation_timer < self.animation_duration / 2:
                        # Move toward target
                        if hasattr(self.target, 'battle_pos_x'):
                            # Direction vector
                            dx = self.target.battle_pos_x - enemy.battle_pos_x
                            move_dist = int(30 * (current_width / original_width))
                            # Move in the direction of the target
                            offset_x = int(move_dist * (dx / abs(dx) if dx != 0 else 0) * 
                                         (self.animation_timer / (self.animation_duration / 2)))
                    else:
                        # Move back to position
                        if hasattr(self.target, 'battle_pos_x'):
                            dx = self.target.battle_pos_x - enemy.battle_pos_x
                            move_dist = int(30 * (current_width / original_width))
                            # Return from the direction of the target
                            offset_x = int(move_dist * (dx / abs(dx) if dx != 0 else 0) * 
                                         (1 - (self.animation_timer - self.animation_duration / 2) / 
                                          (self.animation_duration / 2)))
                
                # Draw enemy with offset
                pygame.draw.rect(screen, enemy.color,
                                (enemy.rect.x + offset_x,
                                 enemy.rect.y + offset_y,
                                 enemy.rect.width,
                                 enemy.rect.height))
        
        # Draw enemy names and health bars
        from systems.battle_ui_helpers import draw_enemy_name_tags, draw_enemy_health_bars
        draw_enemy_name_tags(screen, self.enemies)
        draw_enemy_health_bars(screen, self.enemies)
        
        # Draw targeting system if active
        if self.in_targeting_mode:
            self.targeting_system.draw(screen)
        
        # Draw turn order indicator
        draw_turn_order_indicator(screen, self)
        
        # Draw party status
        from systems.battle_ui_party import draw_party_status
        # Create fonts for status display
        font_size = scale_font_size(24, original_width, original_height, current_width, current_height)
        small_font_size = scale_font_size(16, original_width, original_height, current_width, current_height)
        font = pygame.font.SysFont('Arial', font_size)
        small_font = pygame.font.SysFont('Arial', small_font_size)
        
        draw_party_status(screen, self.party, self.turn_order, font, small_font)
        
        # Draw the battle UI
        self._draw_battle_ui(screen)
    
    def _draw_battle_ui(self, screen):
        """
        Draw the battle UI elements.
        
        Args:
            screen: The pygame surface to draw on
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
        pygame.draw.rect(screen, (0, 0, 0, 200), message_box_rect)
        pygame.draw.rect(screen, WHITE, message_box_rect, max(1, int(2 * (current_width / original_width))))
        
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
        
        # Draw battle options or special menus
        current_character = self.get_current_character()
        
        if (current_character and not self.battle_over and 
            not self.character_attacking and not self.enemy_attacking and 
            not self.character_fleeing and not self.character_casting and 
            not self.character_using_skill and not self.character_using_ultimate and 
            self.action_delay == 0):
            
            # Only display UI when the text is fully displayed AND not currently processing an action
            if self.message_index >= len(self.full_message) and not self.action_processing:
                if self.in_spell_menu:
                    self._draw_spell_menu(screen, font, small_font, current_character)
                elif self.in_skill_menu:
                    self._draw_skill_menu(screen, font, small_font, current_character)
                elif self.in_ultimate_menu:
                    self._draw_ultimate_menu(screen, font, small_font, current_character)
                else:
                    self._draw_battle_options(screen, font, current_character)
        
        # Display continue message if battle is over
        if self.battle_over:
            # Only display the continue message when the text is fully displayed
            if self.message_index >= len(self.full_message):
                continue_text = font.render("Press ENTER to continue", True, WHITE)
                continue_x = (current_width // 2) - (continue_text.get_width() // 2)
                continue_y = int(500 * (current_height / original_height))
                screen.blit(continue_text, (continue_x, continue_y))
    
    def _draw_battle_options(self, screen, font, character):
        """
        Draw the main battle options menu in a two-column layout.
        
        Args:
            screen: The pygame surface to draw on
            font: The font to use
            character: The current character whose turn it is
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
        pygame.draw.rect(screen, (0, 0, 0, 200), (options_box_x, options_box_y, options_box_width, options_box_height))
        border_width = max(1, int(2 * (current_width / original_width)))
        pygame.draw.rect(screen, WHITE, (options_box_x, options_box_y, options_box_width, options_box_height), border_width)
        
        # Draw character name
        char_text = font.render(f"{character.name}'s Turn", True, GREEN)
        header_x = options_box_x + (options_box_width // 2) - (char_text.get_width() // 2)
        header_y = options_box_y + int(10 * (current_height / original_height))
        screen.blit(char_text, (header_x, header_y))
        
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
    
    def _draw_spell_menu(self, screen, font, small_font, character):
        """
        Draw the spell selection menu.
        
        Args:
            screen: The pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for details
            character: The character casting spells
        """
        from utils import scale_position, scale_dimensions
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Scale menu dimensions and position
        spell_box_width, spell_box_height = scale_dimensions(
            250, 200, original_width, original_height, current_width, current_height
        )
        spell_box_x, spell_box_y = scale_position(
            20, SCREEN_HEIGHT - 200 - 5, original_width, original_height, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, (0, 0, 0, 200), (spell_box_x, spell_box_y, spell_box_width, spell_box_height))
        border_width = max(1, int(2 * (current_width / original_width)))
        pygame.draw.rect(screen, PURPLE, (spell_box_x, spell_box_y, spell_box_width, spell_box_height), border_width)
        
        # Draw "Magic" header
        magic_text = font.render(f"{character.name}'s Magic", True, PURPLE)
        header_x = spell_box_x + (spell_box_width // 2) - (magic_text.get_width() // 2)
        header_y = spell_box_y + int(10 * (current_height / original_height))
        screen.blit(magic_text, (header_x, header_y))
        
        # Get spell list from character's spellbook
        spell_names = character.spellbook.get_spell_names()
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
                spell = character.spellbook.get_spell(spell_name)
                
                # Determine text color based on whether character has enough SP
                has_sp = character.sp >= spell.sp_cost
                
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
            spell = character.spellbook.get_spell(options[self.selected_spell_option])
            if spell:
                desc_y = option_y_base + len(options) * option_line_height + int(10 * (current_height / original_height))
                desc_text = small_font.render(spell.description, True, WHITE)
                screen.blit(desc_text, (option_x, desc_y))
    
    def _draw_skill_menu(self, screen, font, small_font, character):
        """
        Draw the skill selection menu.
        
        Args:
            screen: The pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for details
            character: The character using skills
        """
        from utils import scale_position, scale_dimensions
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Scale menu dimensions and position
        skill_box_width, skill_box_height = scale_dimensions(
            250, 200, original_width, original_height, current_width, current_height
        )
        skill_box_x, skill_box_y = scale_position(
            20, SCREEN_HEIGHT - 200 - 5, original_width, original_height, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, (0, 0, 0, 200), (skill_box_x, skill_box_y, skill_box_width, skill_box_height))
        border_width = max(1, int(2 * (current_width / original_width)))
        pygame.draw.rect(screen, YELLOW, (skill_box_x, skill_box_y, skill_box_width, skill_box_height), border_width)
        
        # Draw "Skills" header
        skills_text = font.render(f"{character.name}'s Skills", True, YELLOW)
        header_x = skill_box_x + (skill_box_width // 2) - (skills_text.get_width() // 2)
        header_y = skill_box_y + int(10 * (current_height / original_height))
        screen.blit(skills_text, (header_x, header_y))
        
        # Get skill list from character's skillset
        skill_names = character.skillset.get_skill_names()
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
                skill = character.skillset.get_skill(skill_name)
                
                # Determine text color based on whether character has enough resources
                has_resources = True
                if skill.cost_type == "sp" and character.sp < skill.sp_cost:
                    has_resources = False
                elif skill.cost_type == "hp" and character.hp <= skill.hp_cost:
                    has_resources = False
                elif skill.cost_type == "both" and (character.sp < skill.sp_cost or character.hp <= skill.hp_cost):
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
            skill = character.skillset.get_skill(options[self.selected_skill_option])
            if skill:
                desc_y = option_y_base + len(options) * option_line_height + int(10 * (current_height / original_height))
                desc_text = small_font.render(skill.description, True, WHITE)
                screen.blit(desc_text, (option_x, desc_y))
    
    def _draw_ultimate_menu(self, screen, font, small_font, character):
        """
        Draw the ultimate ability selection menu.
        
        Args:
            screen: The pygame surface to draw on
            font: The main font to use
            small_font: The smaller font for details
            character: The character using ultimates
        """
        from utils import scale_position, scale_dimensions
        
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        original_width, original_height = 800, 600  # Original design resolution
        
        # Scale menu dimensions and position
        ultimate_box_width, ultimate_box_height = scale_dimensions(
            250, 200, original_width, original_height, current_width, current_height
        )
        ultimate_box_x, ultimate_box_y = scale_position(
            20, SCREEN_HEIGHT - 200 - 5, original_width, original_height, current_width, current_height
        )
        
        # Draw box background and border
        pygame.draw.rect(screen, (0, 0, 0, 200), (ultimate_box_x, ultimate_box_y, ultimate_box_width, ultimate_box_height))
        border_width = max(1, int(2 * (current_width / original_width)))
        pygame.draw.rect(screen, RED, (ultimate_box_x, ultimate_box_y, ultimate_box_width, ultimate_box_height), border_width)
        
        # Draw "Ultimate" header
        ultimate_text = font.render(f"{character.name}'s Ultimates", True, RED)
        header_x = ultimate_box_x + (ultimate_box_width // 2) - (ultimate_text.get_width() // 2)
        header_y = ultimate_box_y + int(10 * (current_height / original_height))
        screen.blit(ultimate_text, (header_x, header_y))
        
        # Get ultimate list from character's ultimates
        ultimate_names = character.ultimates.get_ultimate_names()
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
                ultimate = character.ultimates.get_ultimate(ultimate_name)
                
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
            ultimate = character.ultimates.get_ultimate(options[self.selected_ultimate_option])
            if ultimate:
                desc_y = option_y_base + len(options) * option_line_height + int(10 * (current_height / original_height))
                desc_text = small_font.render(ultimate.description, True, WHITE)
                screen.blit(desc_text, (option_x, desc_y))
                
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
    
    def _ensure_battle_flow_consistency(self):
        """Helper method to ensure battle flow remains consistent."""
        # Check for impossible states and fix them
        if self.battle_over:
            # If battle is over, ensure action processing is False
            self.action_processing = False
            return
            
        # Check for player's turn with no active animations but action_processing is true
        if (self.turn == 0 and 
            not self.player_attacking and 
            not self.player_casting and 
            not self.player_using_skill and 
            not self.player_using_ultimate and 
            not self.player_fleeing and
            self.action_delay == 0 and
            self.action_processing and
            self.message_index >= len(self.full_message)):
            # This is a stuck state, reset action_processing
            self.action_processing = False
            
        # Ensure enemy turn consistency
        if self.turn == 1 and not self.enemy_attacking and not self.enemy_turn_processed:
            # Enemy turn should be processed
            self.process_enemy_turn()
    
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