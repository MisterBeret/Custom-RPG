"""
Character creation system for the RPG game.
"""
from entities.player import Player
from data.character_classes import commoner, warrior, mage  # Import available classes
from systems.spell_system import SpellBook
from systems.skill_system import SkillSet
from systems.ultimate_system import UltimateSet
from systems.passive_system import PassiveSet

class CharacterCreator:
    """
    Handles creation and customization of player characters.
    """
    def __init__(self, party=None):
        """
        Initialize the character creator.
        
        Args:
            party: The party to add new characters to
        """
        self.party = party
        self.available_classes = {
            "commoner": commoner,
            "warrior": warrior,
            "mage": mage
        }
    
    def create_character(self, name, class_id, level=1, active=True):
        """
        Create a new character and add to the party if provided.
        
        Args:
            name: Character name
            class_id: ID of the character class to use
            level: Starting level (default: 1)
            active: Whether to add to active party (True) or reserve (False)
            
        Returns:
            Player: The created character, or None if creation failed
        """
        if class_id not in self.available_classes:
            return None
            
        # Create character with the specified class
        character_class = self.available_classes[class_id]
        character = Player(0, 0, character_class, level, name)
        
        # Add to party if provided
        if self.party:
            self.party.add_member(character, active)
            
        return character
    
    def edit_character(self, character, new_name=None, new_class_id=None):
        """
        Edit an existing character.
        
        Args:
            character: The character to edit
            new_name: New name (or None to keep current)
            new_class_id: New class ID (or None to keep current)
            
        Returns:
            bool: True if edit was successful
        """
        if new_name:
            character.name = new_name
            
        if new_class_id and new_class_id in self.available_classes:
            # Store current level and stats
            current_level = character.level
            
            # Update character class
            character.character_class = self.available_classes[new_class_id]
            
            # Recalculate stats based on new class and current level
            stats = character.character_class.get_stat_block(current_level)
            character.max_hp = stats["hp"]
            character.hp = character.max_hp  # Heal to full when changing class
            character.max_sp = stats["sp"]
            character.sp = character.max_sp  # Restore SP to full
            character.attack = stats["attack"]
            character.defense = stats["defense"]
            character.intelligence = stats["intelligence"]
            character.resilience = stats["resilience"]
            character.acc = stats["acc"]
            character.spd = stats["spd"]
            
            # Learn abilities for new class at current level
            self._update_character_abilities(character)
            
            return True
            
        return False
    
    def _update_character_abilities(self, character):
        """
        Update a character's abilities based on their class and level.
        
        Args:
            character: The character to update
        """
        if not character.character_class:
            return
            
        # Get abilities for the current level
        abilities = character.character_class.get_abilities_for_level(character.level)
        
        # Reset ability containers
        character.spellbook = SpellBook()
        character.skillset = SkillSet()
        character.ultimates = UltimateSet()
        character.passives = PassiveSet(add_defaults=False)
        
        # Add all abilities the character should have
        for spell_name in abilities["spells"]:
            character.spellbook.add_spell(spell_name)
            
        for skill_name in abilities["skills"]:
            character.skillset.add_skill(skill_name)
            
        for ultimate_name in abilities["ultimates"]:
            character.ultimates.add_ultimate(ultimate_name)
            
        for passive_name in abilities["passives"]:
            character.passives.add_passive(passive_name)