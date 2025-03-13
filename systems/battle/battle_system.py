"""
Core battle system for the RPG game.
Coordinates all battle-related subsystems and manages the overall battle flow.
"""
import pygame

from constants import (BLACK, WHITE, MAX_LOG_SIZE, 
                      ORIGINAL_WIDTH, ORIGINAL_HEIGHT)
from systems.battle.battle_mechanics import BattleMechanics
from systems.battle.battle_actions import BattleActions
from systems.battle.battle_ui import BattleUI
from systems.battle.battle_animations import BattleAnimations
from systems.battle.battle_formation import BattleFormation
from systems.battle.battle_visualizer import draw_battle_background
from systems.battle.turn_order import TurnOrder
from entities.player import Player

class BattleSystem:
    """
    Manages turn-based battles between player party and enemies.
    Coordinates the various battle subsystems.
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
        
        # Initialize turn order
        self.turn_order = TurnOrder(party.active_members, self.enemies)
        
        # Battle state
        self.battle_over = False
        self.victory = False
        self.fled = False
        self.text_speed = 2  # Default, will be set by text_speed_setting
        
        # Starting message
        current_combatant = self.turn_order.get_current()
        self.first_message = f"Battle started! {current_combatant.name} moves first!"
        
        # Set turn based on first combatant
        if current_combatant in party.active_members:
            self.turn = 0  # Player's turn
        else:
            self.turn = 1  # Enemy's turn
        
        # Initialize formation system and position combatants
        current_width, current_height = pygame.display.get_surface().get_size()
        self.formation = BattleFormation(current_width, current_height)
        self.formation.position_party_members(party)
        self.formation.position_enemies(self.enemies)
        
        # Initialize subsystems
        self.mechanics = BattleMechanics()
        self.ui = BattleUI(self)
        self.animations = BattleAnimations(self)
        self.actions = BattleActions(self)
        
        # Set initial message
        self.ui.set_message(self.first_message)
        
        # Set text speed 
        self.set_text_speed(text_speed_setting)
    
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
    
    def set_message(self, message):
        """
        Set a new battle message.
        
        Args:
            message: The message to display
        """
        self.ui.set_message(message)
    
    def handle_input(self, event):
        """
        Handle player input during battle.
        
        Args:
            event: The pygame event
            
        Returns:
            bool: True if input was handled, False otherwise
        """
        # If text is still scrolling, pressing any key will display it immediately
        if not self.ui.is_text_complete():
            if event.type == pygame.KEYDOWN:
                self.ui.complete_text()
                return True
        
        # Handle targeting mode input
        if self.ui.in_targeting_mode:
            return self.ui.handle_targeting_input(event)
        
        # Handle menu navigation
        character = self.get_current_character()
        if character and not self.actions.action_processing:
            return self.ui.handle_menu_navigation(event, character)
        
        # Check if battle has ended and player pressed ENTER to continue
        if self.battle_over and self.ui.is_text_complete():
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE):
                # Signal that battle is ended (handled by main game loop)
                return True
        
        return False
    
    def update(self):
        """Update battle state, animations, and UI."""
        # Update text animation
        self.ui.update_text_animation()
        
        # Update targeting system if active
        if self.ui.in_targeting_mode:
            self.ui.targeting_system.update()
        
        # Update animations if text is fully displayed
        if self.ui.is_text_complete():
            self.animations.update()
            
            # Process enemy turn if it's enemy's turn and no animation is active
            if (not self.is_player_turn() and 
                not self.animations.enemy_attacking and 
                not self.actions.action_processing):
                self.actions.process_enemy_turn()
            
            # Check for battle completion
            self._check_battle_over()
    
    def _check_battle_over(self):
        """Check if the battle is over and set appropriate state."""
        # Skip if battle is already marked as over
        if self.battle_over:
            return
            
        # Check if all enemies are defeated
        if self.mechanics.check_all_enemies_defeated(self.enemies):
            self.battle_over = True
            self.victory = True
            self.set_message("Victory! All enemies defeated!")
            
        # Check if all party members are defeated
        elif self.mechanics.check_all_party_defeated(self.party.active_members):
            self.battle_over = True
            self.victory = False
            self.set_message("Defeat! All party members have fallen!")
    
    def draw(self, screen):
        """
        Draw the battle scene with all components.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Draw background
        draw_battle_background(screen)
        
        # Draw UI components
        self.ui.draw(screen)
        
        # Draw animation effects
        self.animations.draw(screen)