"""
Enemy class for the RPG game.
"""
import pygame
import random
from entities.entity import Entity
from constants import RED, ORIGINAL_WIDTH, ORIGINAL_HEIGHT
from utils import scale_position, scale_dimensions
from systems.passive_system import PassiveSet

class Enemy(Entity):
    """
    Enemy entity that can battle with the player.
    """
    def __init__(self, x, y, character_class=None, level=1, color=RED, unique_id=None):
        """
        Initialize an enemy.
        
        Args:
            x (int): Initial x coordinate (only used for positioning in battle)
            y (int): Initial y coordinate (only used for positioning in battle)
            character_class: The enemy's character class (determines stats)
            level (int): The enemy's level
            color (tuple): RGB color tuple for the enemy
            unique_id (int): Unique identifier for this enemy instance
        """
        # Generate a name based on class and unique_id
        name = None
        if character_class:
            if unique_id is not None:
                name = f"{character_class.name} #{unique_id}"
            else:
                name = character_class.name
                
        super().__init__(x, y, 32, 32, color, character_class, level, name)
        
        # If no character class was provided, set default stats
        if not character_class:
            # Battle stats
            self.max_hp = 1
            self.hp = 1
            self.max_sp = 1
            self.sp = 1
            self.attack = 1
            self.defense = 1
            self.intelligence = 1
            self.resilience = 1
            self.acc = 1
            self.spd = 1
            self.xp = 1
        else:
            # Set XP based on level - more advanced calculation could be used
            self.xp = level * 5
        
        self.defending = False
        self.defense_multiplier = 1  # Property to track defense multiplier

        # Initialize passive abilities (empty by default for enemies)
        self.passives = PassiveSet(add_defaults=False)
        
        # Add unique identifier for targeting in multi-enemy battles
        self.entity_id = f"enemy_{id(self)}"
        
        # Position in battle formation (for multi-enemy battles)
        self.battle_position = 0
        
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
    def create_from_spec(cls, enemy_spec, x, y, unique_id=None):
        """
        Create an enemy based on an enemy specification.
        
        Args:
            enemy_spec: The enemy specification from the encounter system
            x (int): Initial x coordinate
            y (int): Initial y coordinate
            unique_id (int): Optional unique identifier for this enemy
            
        Returns:
            Enemy: The created enemy instance
        """
        from data.character_classes import (
            rat, snake, slime, turtle, hermit_crab  # Import monster classes
        )
        
        # Map the class IDs to actual class objects
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
            # Create the enemy with the specified class, level, and unique ID
            return cls(x, y, character_class, enemy_spec.level, color, unique_id)
        else:
            # Fallback to default enemy if class not found
            return cls(x, y, None, 1, RED, unique_id)