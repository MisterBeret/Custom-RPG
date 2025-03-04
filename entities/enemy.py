"""
Enemy class for the RPG game.
"""
import pygame
import random
from entities.entity import Entity
from constants import RED, SCREEN_WIDTH, SCREEN_HEIGHT, ORIGINAL_WIDTH, ORIGINAL_HEIGHT
from utils import scale_position, scale_dimensions
from systems.passive_system import PassiveSet

class Enemy(Entity):
    """
    Enemy entity that can battle with the player.
    """
    def __init__(self, x, y, character_class=None, level=1, color=RED):
        """
        Initialize an enemy.
        
        Args:
            x (int): Initial x coordinate
            y (int): Initial y coordinate
            character_class: The enemy's character class (determines stats)
            level (int): The enemy's level
            color (tuple): RGB color tuple for the enemy
        """
        super().__init__(x, y, 32, 32, color, character_class, level)
        
        # If no character class was provided, set default stats
        if not character_class:
            # Battle stats
            self.max_hp = 3
            self.hp = 3
            self.max_sp = 0  # Enemy's starting SP
            self.sp = 0      # Current SP
            self.attack = 2  # Attack set to 2
            self.defense = 1  # Defense stat set to 1
            self.intelligence = 0  # Intelligence set to 0 (no magic ability)
            self.resilience = 1    # Resilience set to 1 to reduce magic damage
            self.acc = 2  # New accuracy stat
            self.spd = 3  # Speed determines turn order
            self.xp = 5   # XP awarded to player upon defeat
        else:
            # Set XP based on level - more advanced calculation could be used
            self.xp = level * 5
        
        self.defending = False
        self.defense_multiplier = 1  # New property to track defense multiplier

        # Initialize passive abilities (empty by default for enemies)
        self.passives = PassiveSet(add_defaults=False)
        
        # Add unique identifier for targeting in multi-enemy battles
        self.entity_id = f"enemy_{id(self)}"
        
        # Position in battle formation (for multi-enemy battles)
        self.battle_position = 0
        
    def update(self):
        """
        Update enemy state. Can be expanded for movement patterns.
        """
        # Currently no movement or AI, but can be added here
        pass
    
    def defend(self):
        """
        Enter defensive stance to halve incoming damage and increase evasion by 25%.
        """
        self.defending = True
        
    def take_damage(self, amount, damage_type="physical", attacker=None, battle_system=None):
        """
        Apply damage to the enemy, with the potential to trigger passive abilities.
        
        Args:
            amount (int): Amount of damage to take
            damage_type (str): Type of damage (physical, magical, etc.)
            attacker: The entity that caused the damage (for passives)
            battle_system: The battle system reference (for passives)
            
        Returns:
            tuple: (bool, str) - Whether a passive was triggered and any resulting message
        """
        # Apply damage using parent method
        super().take_damage(amount)
        
        # Check if we should trigger any passives
        passive_triggered = False
        passive_message = ""
        
        # Only try to trigger "on_hit" passives if we were actually hit (damage > 0)
        # and if we have necessary context (attacker and battle_system)
        if amount > 0 and damage_type == "physical" and attacker and battle_system:
            passive_triggered, passive_message = self.passives.trigger_passive(
                trigger_type="on_hit",
                battle_system=battle_system,
                entity=self,
                target=attacker
            )
            
        return passive_triggered, passive_message
    
    def end_turn(self):
        """
        End the turn and reset temporary stat changes.
        """
        self.defending = False
        
    @classmethod
    def create_from_spec(cls, enemy_spec, x, y):
        """
        Create an enemy based on an enemy specification.
        
        Args:
            enemy_spec: The enemy specification from the encounter system
            x (int): Initial x coordinate
            y (int): Initial y coordinate
            
        Returns:
            Enemy: The created enemy instance
        """
        from data.character_classes import (
            rat, snake, slime, turtle, hermit_crab  # Import monster classes
        )
        
        # Map class IDs to actual class objects
        class_map = {
            "rat": rat,
            "snake": snake,
            "slime": slime,
            "turtle": turtle,
            "hermit_crab": hermit_crab
        }
        
        # Choose color based on class
        color_map = {
            "rat": (120, 100, 80),     # Brown
            "snake": (70, 130, 70),    # Green
            "slime": (100, 200, 200),  # Light blue
            "turtle": (70, 140, 90),   # Dark green
            "hermit_crab": (180, 120, 100)  # Reddish brown
        }
        
        # Get the character class object
        character_class = class_map.get(enemy_spec.class_id)
        color = color_map.get(enemy_spec.class_id, RED)  # Default to RED if not found
        
        if character_class:
            # Create the enemy with the specified class and level
            return cls(x, y, character_class, enemy_spec.level, color)
        else:
            # Fallback to default enemy if class not found
            return cls(x, y)
        
    @classmethod
    def spawn_random(cls):
        """
        Create an enemy at a random position on the screen.
        
        Returns:
            Enemy: A new enemy at a random position
        """
        # Get current screen dimensions
        current_width, current_height = pygame.display.get_surface().get_size()
        
        # Calculate position in terms of original resolution
        x = random.randint(100, ORIGINAL_WIDTH - 100)
        y = random.randint(100, ORIGINAL_HEIGHT - 100)
        
        # Create enemy instance
        enemy = cls(x, y)
        
        # Scale enemy to match current resolution
        enemy.update_scale(current_width, current_height)
        
        return enemy