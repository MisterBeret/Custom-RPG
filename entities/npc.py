"""
NPC class.
"""
import pygame
from entities.entity import Entity
from constants import WHITE, SCREEN_WIDTH, SCREEN_HEIGHT, ORIGINAL_WIDTH, ORIGINAL_HEIGHT
from utils import scale_position, scale_dimensions

class NPC(Entity):
    """
    Non-player character entity that can be interacted with.
    """
    def __init__(self, x, y, width=32, height=48, color=WHITE, name="NPC", dialogue=None):
        """
        Initialize an NPC.
        
        Args:
            x (int): Initial x coordinate
            y (int): Initial y coordinate
            width (int): Entity width
            height (int): Entity height
            color (tuple): RGB color tuple
            name (str): NPC name
            dialogue (list): List of dialogue strings
        """
        super().__init__(x, y, width, height, color)
        self.name = name
        self.dialogue = dialogue or ["Hello!"]
        self.interaction_distance = 50  # Distance in pixels for interaction
        
    def can_interact(self, player):
        """
        Check if player is close enough and facing the NPC to interact.
        
        Args:
            player: The player entity
            
        Returns:
            bool: True if interaction is possible, False otherwise
        """
        # Calculate distance between player and NPC
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = (dx**2 + dy**2)**0.5
        
        # Check if player is close enough
        if distance > self.interaction_distance:
            return False
            
        # Check if player is facing the NPC
        if player.facing == "up" and dy < 0:
            return True
        elif player.facing == "down" and dy > 0:
            return True
        elif player.facing == "left" and dx < 0:
            return True
        elif player.facing == "right" and dx > 0:
            return True
            
        return False
        
    def interact(self, dialogue_system):
        """
        Start interaction with this NPC.
        
        Args:
            dialogue_system: The dialogue system to use
            
        Returns:
            bool: True if interaction started, False otherwise
        """
        dialogue_system.start_dialogue(self.dialogue)
        return True