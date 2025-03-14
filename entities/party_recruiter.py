"""
Party recruiter NPC for managing the player's party.
"""
import pygame
from entities.npc import NPC
from constants import WHITE
from systems.ui.party_ui import PartyManagementUI
from systems.character.character_creator import CharacterCreator
from systems.character.party_system import Party

class PartyRecruiter(NPC):
    """
    Special NPC for recruiting and managing party members.
    """
    def __init__(self, x, y, width=32, height=48, color=WHITE, party=None):
        """
        Initialize the party recruiter.
        
        Args:
            x (int): Initial x coordinate
            y (int): Initial y coordinate
            width (int): Entity width
            height (int): Entity height
            color (tuple): RGB color tuple
            party: The player's party
        """
        # Basic dialogue to introduce the recruiter
        dialogue = [
            "Welcome to the Character Recruitment Center!",
            "I can help you manage your party members.",
            "Would you like to recruit new characters or manage your current party?",
            "Press ENTER to continue."
        ]
        
        super().__init__(x, y, width, height, color, "Party Recruiter", dialogue)
        
        # Create a new party if None was provided
        self.party = party if party is not None else Party()
        
        # Create the character creator and UI with the party (either provided or new)
        self.character_creator = CharacterCreator(self.party)
        self.ui = PartyManagementUI(self.party, self.character_creator)
        self.show_party_ui = False
        
    def interact(self, dialogue_system):
        """
        Interact with this NPC.
        
        Args:
            dialogue_system: The dialogue system to use
            
        Returns:
            bool: True if interaction started, False otherwise
        """
        # First show the introduction dialogue
        if not self.show_party_ui:
            super().interact(dialogue_system)
            return True
        else:
            # If we're already showing the party UI, do nothing
            # (This shouldn't happen normally as the UI should be handled separately)
            return False
    
    def finish_dialogue(self):
        """
        Called when dialogue with this NPC is finished.
        
        Returns:
            bool: True if party UI should be shown
        """
        self.show_party_ui = True
        return True
        
    def update(self, event=None):
        """
        Update the recruiter and handle party UI events.
        
        Args:
            event: Pygame event to process
            
        Returns:
            bool: True if party UI should be closed
        """
        if not self.show_party_ui or not event:
            return False
            
        # Pass event to the party UI
        close_ui = self.ui.handle_input(event)
        
        if close_ui:
            self.show_party_ui = False
            return True
            
        return False
        
    def draw_ui(self, screen):
        """
        Draw the party management UI.
        
        Args:
            screen: The pygame surface to draw on
        """
        if self.show_party_ui:
            self.ui.draw(screen)