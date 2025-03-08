"""
Game initialization functions for the RPG game.
"""
from systems.party_system import Party
from systems.character_creator import CharacterCreator
from entities.party_recruiter import PartyRecruiter
from data.character_classes import commoner, warrior, mage
from constants import ORIGINAL_WIDTH, ORIGINAL_HEIGHT

def initialize_party():
    """
    Initialize the party with a default character.
    
    Returns:
        tuple: (Party, str) - The party and the leader's name
    """
    # Create the party
    party = Party()
    
    # Create character creator
    creator = CharacterCreator(party)
    
    # Create initial character with commoner class
    initial_character = creator.create_character("Hero", "commoner", 1, True)
    
    # Return the party and the leader character's name
    return party, initial_character.name

def create_party_recruiter(party, x, y, current_width, current_height):
    """
    Create a party recruiter NPC.
    
    Args:
        party: The player's party
        x: The x coordinate
        y: The y coordinate
        current_width: Current screen width
        current_height: Current screen height
        
    Returns:
        PartyRecruiter: The created recruiter
    """
    recruiter = PartyRecruiter(x, y, party=party)
    
    # Scale the recruiter to match the current resolution
    recruiter.update_scale(current_width, current_height)
    
    return recruiter