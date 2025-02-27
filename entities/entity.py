"""
Base entity class for game objects.
"""
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Entity(pygame.sprite.Sprite):
    """
    Base class for all game entities (player, enemies, etc.).
    """
    def __init__(self, x, y, width, height, color):
        """
        Initialize a new entity.
        
        Args:
            x (int): Initial x coordinate
            y (int): Initial y coordinate
            width (int): Entity width
            height (int): Entity height
            color (tuple): RGB color tuple
        """
        super().__init__()
        
        # Create a simple rectangle for the entity
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        
        # Set the position
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Battle stats
        self.max_hp = 1
        self.hp = 1
        self.max_mp = 0  # Maximum magic points
        self.mp = 0      # Current magic points
        self.intelligence = 0  # Intelligence determines magic damage
        self.resilience = 1    # Resilience reduces incoming magic damage
        self.attack = 2  # Default attack value set to 2
        self.defense = 1  # New defense stat, default value is 1
        self.spd = 1  # Speed determines turn order
        
    def take_damage(self, amount):
        """
        Apply damage to the entity.
        
        Args:
            amount (int): Amount of damage to take
            
        Returns:
            bool: True if entity was defeated, False otherwise
        """
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        return self.is_defeated()
        
    def is_defeated(self):
        """
        Check if the entity is defeated.
        
        Returns:
            bool: True if HP is 0 or less, False otherwise
        """
        return self.hp <= 0
    
    def use_mp(self, amount):
        """
        Use MP for casting spells.
    
        Args:
            amount (int): Amount of MP to use
        
        Returns:
            bool: True if entity had enough MP and it was used, False otherwise
        """

        if self.mp >= amount:
            self.mp -= amount
            return True
        return False
        
    def keep_on_screen(self):
        """
        Keep the entity within the screen boundaries.
        """
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > SCREEN_HEIGHT - self.rect.height:
            self.rect.y = SCREEN_HEIGHT - self.rect.height