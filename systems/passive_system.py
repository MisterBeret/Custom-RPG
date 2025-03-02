"""
Passive ability system for the RPG game.
Passive abilities provide automatic effects that don't require manual activation.
"""
from dataclasses import dataclass
import random
import sys
import os

# Add path to allow imports from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# For type annotations
from typing import Optional, List, Tuple, Any, Dict, Union

@dataclass
class Passive:
    """Class representing a passive ability."""
    name: str
    description: str
    effect_type: str  # 'counter', 'regen', 'thorns', etc.
    trigger_type: str  # 'on_hit', 'turn_start', 'turn_end', etc.
    chance: float  # Probability of triggering (0.0 to 1.0)
    power: float  # Effect power/multiplier

class PassiveSet:
    """
    Manages the character's passive abilities.
    Provides methods to add, retrieve, and trigger passive effects.
    """
    def __init__(self, add_defaults=True):
        """
        Initialize the passives.
        
        Args:
            add_defaults: Whether to add default passives. Set to False when using for enemies.
        """
        self.passives = {}
        
        # Add default passives if requested
        if add_defaults:
            self.add_passive("COUNTER")
        
    def add_passive(self, passive_name):
        """
        Add a passive to the character's set.
        
        Args:
            passive_name: The name of the passive to add
            
        Returns:
            bool: True if passive was added, False if already known
        """
        # Don't add if already known
        if passive_name in self.passives:
            return False
            
        # Add the passive
        passive = get_passive_data(passive_name)
        if passive:
            self.passives[passive_name] = passive
            return True
        
        return False
        
    def get_passive(self, passive_name):
        """
        Get a passive from the set.
        
        Args:
            passive_name: The name of the passive to retrieve
            
        Returns:
            Passive: The passive object, or None if not in set
        """
        return self.passives.get(passive_name)
        
    def get_passive_names(self):
        """
        Get a list of all passive names in the set.
        
        Returns:
            list: List of passive names known by the character
        """
        return list(self.passives.keys())
    
    def has_passive_of_type(self, effect_type, trigger_type=None):
        """
        Check if the character has a passive of a specific type.
        
        Args:
            effect_type: The effect type to check for
            trigger_type: Optional trigger type to also check for
            
        Returns:
            list: List of matching passives, empty if none found
        """
        matching_passives = []
        
        for name, passive in self.passives.items():
            if passive.effect_type == effect_type:
                if trigger_type is None or passive.trigger_type == trigger_type:
                    matching_passives.append(passive)
                    
        return matching_passives
    
    def trigger_passive(self, trigger_type, battle_system=None, entity=None, target=None):
        """
        Attempt to trigger passives based on a specific trigger.
        
        Args:
            trigger_type: The trigger type that occurred
            battle_system: The battle system instance (for applying effects)
            entity: The entity with the passives
            target: The target of any effects
            
        Returns:
            tuple: (bool, str) - Whether any passive was triggered and resulting message
        """
        triggered = False
        message = ""
        
        for name, passive in self.passives.items():
            if passive.trigger_type == trigger_type:
                # Check random chance to trigger
                if random.random() < passive.chance:
                    # Handle specific passive types
                    if passive.effect_type == "counter" and battle_system and entity and target:
                        # Calculate counter-attack damage
                        hit_chance = battle_system.calculate_hit_chance(entity, target)
                        counter_hits = random.random() < hit_chance
                        
                        if counter_hits:
                            damage = battle_system.calculate_damage(entity, target)
                            target.take_damage(damage)
                            
                            if target.is_defeated():
                                message = f"{passive.name} triggered! Counter-attack dealt {damage} damage! {target.__class__.__name__} defeated!"
                            else:
                                message = f"{passive.name} triggered! Counter-attack dealt {damage} damage!"
                        else:
                            message = f"{passive.name} triggered, but the counter-attack missed!"
                            
                        triggered = True
                    
                    # Add handlers for other passive types here
        
        return triggered, message

# Define passive data
def get_passive_data(passive_name: str) -> Optional['Passive']:
    """
    Get the data for a specific passive.
    
    Args:
        passive_name: The name of the passive
        
    Returns:
        Passive: A Passive object with the ability data, or None if not recognized
    """
    if passive_name == "COUNTER":
        return Passive(
            name="COUNTER",
            description="50% chance to counter-attack when hit by a physical attack",
            effect_type="counter",
            trigger_type="on_hit",
            chance=0.5,  # 50% chance to trigger
            power=1.0    # Normal attack power
        )
    # Add more passives here as needed
    return None