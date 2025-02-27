"""
Spell system for the RPG game.
"""
from dataclasses import dataclass

@dataclass
class Spell:
    """Class representing a magic spell."""
    name: str
    description: str
    mp_cost: int
    effect_type: str  # 'damage', 'healing', etc.
    base_power: int   # Base power of the spell

class SpellBook:
    """
    Manages the player's known spells.
    """
    def __init__(self):
        """Initialize the spellbook with default spells."""
        self.spells = {}
        
        # Add default spells
        self.add_spell("FIRE")
        self.add_spell("HEAL")
        
    def add_spell(self, spell_name):
        """
        Add a spell to the spellbook.
        
        Args:
            spell_name: The name of the spell to add
            
        Returns:
            bool: True if spell was added, False if already known
        """
        # Don't add if already known
        if spell_name in self.spells:
            return False
            
        # Add the spell
        spell = get_spell_data(spell_name)
        if spell:
            self.spells[spell_name] = spell
            return True
        
        return False
        
    def get_spell(self, spell_name):
        """
        Get a spell from the spellbook.
        
        Args:
            spell_name: The name of the spell to retrieve
            
        Returns:
            Spell: The spell object, or None if not in spellbook
        """
        return self.spells.get(spell_name)
        
    def get_spell_names(self):
        """
        Get a list of all spell names in the spellbook.
        
        Returns:
            list: List of spell names known by the player
        """
        return list(self.spells.keys())

# Define spell data
def get_spell_data(spell_name):
    """
    Get the data for a specific spell.
    
    Args:
        spell_name: The name of the spell
        
    Returns:
        Spell: A Spell object with the spell data, or None if spell not recognized
    """
    if spell_name == "FIRE":
        return Spell(
            name="FIRE",
            description="Deals fire damage to an enemy",
            mp_cost=2,
            effect_type="damage",
            base_power=5
        )
    elif spell_name == "HEAL":
        return Spell(
            name="HEAL",
            description="Restores HP to the caster",
            mp_cost=5,
            effect_type="healing",
            base_power=10
        )
    return None