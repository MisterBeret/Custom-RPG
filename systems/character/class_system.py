"""
Class system for the RPG game.
Every character has a class that determines their base stats and abilities.
"""

import math

class CharacterClass:
    """
    Defines a character class with base stats and learnable abilities.
    """
    def __init__(self, class_id, name, category, base_stats, learnable_abilities):
        self.class_id = class_id          # Unique identifier
        self.name = name                  # Display name 
        self.category = category          # "Human" or "Monster"
        
        # Base stats (values, typically 1-100, that determine stat growth)
        self.base_stats = {
            "hp": base_stats.get("hp", 20),
            "sp": base_stats.get("sp", 20),
            "attack": base_stats.get("attack", 20),
            "defense": base_stats.get("defense", 20),
            "intelligence": base_stats.get("intelligence", 20),
            "resilience": base_stats.get("resilience", 20),
            "acc": base_stats.get("acc", 20),
            "spd": base_stats.get("spd", 20)
        }
        
        # Abilities learned at specific levels: [(level, ability_name, ability_type), ...]
        # ability_type can be "spell", "skill", "ultimate", or "passive"
        self.learnable_abilities = learnable_abilities
    
    def calculate_stat(self, stat_name, level):
        """
        Calculate the actual value of a stat at a given level using the provided formulas.
        
        Args:
            stat_name (str): Name of the stat to calculate
            level (int): Character level
            
        Returns:
            int: The calculated stat value
        """
        base_stat = self.base_stats.get(stat_name, 1)
        
        if stat_name == "hp":
            # HP = floor(BaseStat + (BaseStat * Level^1.55 / 28) + Level^1 / 0.15)
            value = (base_stat + 
                    (base_stat * pow(level, 1.55) / 28) + 
                    (pow(level, 1) / 0.15))
        else:
            # Other stats = floor((BaseStat/10) + (BaseStat * Level^1.55 / 280) + Level^1 / 1.5) + 1
            value = ((base_stat / 10) + 
                    (base_stat * pow(level, 1.55) / 280) + 
                    (pow(level, 1) / 1.5)) + 1
        
        return math.floor(value)
    
    def get_stat_block(self, level):
        """
        Get a complete stat block for this class at the given level.
        
        Args:
            level (int): Character level
            
        Returns:
            dict: All calculated stats
        """
        return {
            stat_name: self.calculate_stat(stat_name, level)
            for stat_name in self.base_stats.keys()
        }
    
    def get_abilities_for_level(self, level):
        """
        Get all abilities this character should have at the given level.
        
        Args:
            level (int): Character level
            
        Returns:
            dict: Dictionary of abilities by type
        """
        abilities = {
            "spells": [],
            "skills": [],
            "ultimates": [],
            "passives": []
        }
        
        for level_req, ability_name, ability_type in self.learnable_abilities:
            if level >= level_req:
                if ability_type == "spell":
                    abilities["spells"].append(ability_name)
                elif ability_type == "skill":
                    abilities["skills"].append(ability_name)
                elif ability_type == "ultimate":
                    abilities["ultimates"].append(ability_name)
                elif ability_type == "passive":
                    abilities["passives"].append(ability_name)
        
        return abilities