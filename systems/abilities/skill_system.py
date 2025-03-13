"""
Skill system for the RPG game.
"""
from dataclasses import dataclass

@dataclass
class Skill:
    """Class representing a character skill."""
    name: str
    description: str
    cost_type: str  # 'none', 'sp', 'hp', 'both', etc.
    sp_cost: int    # SP cost (0 if none)
    hp_cost: int    # HP cost (0 if none)
    effect_type: str  # 'analyze', 'damage', 'healing', 'buff', etc.
    base_power: int   # Base power/value of the skill (0 if not applicable)

class SkillSet:
    """
    Manages the player's known skills.
    """
    def __init__(self):
        """Initialize the skillset with default skills."""
        self.skills = {}
        
        # Add default skills
        self.add_skill("ANALYZE")
        
    def add_skill(self, skill_name):
        """
        Add a skill to the skillset.
        
        Args:
            skill_name: The name of the skill to add
            
        Returns:
            bool: True if skill was added, False if already known
        """
        # Don't add if already known
        if skill_name in self.skills:
            return False
            
        # Add the skill
        skill = get_skill_data(skill_name)
        if skill:
            self.skills[skill_name] = skill
            return True
        
        return False
        
    def get_skill(self, skill_name):
        """
        Get a skill from the skillset.
        
        Args:
            skill_name: The name of the skill to retrieve
            
        Returns:
            Skill: The skill object, or None if not in skillset
        """
        return self.skills.get(skill_name)
        
    def get_skill_names(self):
        """
        Get a list of all skill names in the skillset.
        
        Returns:
            list: List of skill names known by the player
        """
        return list(self.skills.keys())

# Define skill data
def get_skill_data(skill_name):
    """
    Get the data for a specific skill.
    
    Args:
        skill_name: The name of the skill
        
    Returns:
        Skill: A Skill object with the skill data, or None if skill not recognized
    """
    if skill_name == "ANALYZE":
        return Skill(
            name="ANALYZE",
            description="Reveals enemy stats",
            cost_type="none",
            sp_cost=0,
            hp_cost=0,
            effect_type="analyze",
            base_power=0
        )
    # Add more skills here as needed
    return None