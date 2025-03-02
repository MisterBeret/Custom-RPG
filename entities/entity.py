"""
Base entity class for game objects.
"""
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, ORIGINAL_WIDTH, ORIGINAL_HEIGHT
from utils import scale_position, scale_dimensions

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
        
        # Store original (design-time) dimensions
        self.original_x = x
        self.original_y = y
        self.original_width = width
        self.original_height = height
        self.color = color
        
        # Create a simple rectangle for the entity
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        
        # Set the position
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Battle stats
        self.max_hp = 1 # Maximum Health Points
        self.hp = 1 # Current Health Points
        self.max_sp = 0  # Maximum Special Points
        self.sp = 0      # Current Special Points
        self.attack = 2  # ATK determines damage of physical attacks, default value is 2
        self.defense = 1  # DEf reduces incoming physical damage
        self.intelligence = 0  # INT determines magic damage
        self.resilience = 1    # RES reduces incoming magic damage
        self.acc = 2  # ACC determines chance to land hit
        self.spd = 1  # SPD determines turn order and chance to dodge incoming hits
    
    def update_scale(self, current_width, current_height):
        """
        Update entity dimensions and position based on current screen resolution.
        
        Args:
            current_width (int): Current screen width
            current_height (int): Current screen height
        """
        # Scale dimensions and position
        scaled_pos = scale_position(
            self.original_x, self.original_y, 
            ORIGINAL_WIDTH, ORIGINAL_HEIGHT, 
            current_width, current_height
        )
        
        scaled_size = scale_dimensions(
            self.original_width, self.original_height,
            ORIGINAL_WIDTH, ORIGINAL_HEIGHT,
            current_width, current_height
        )
        
        # Create new image with scaled dimensions
        self.image = pygame.Surface([scaled_size[0], scaled_size[1]])
        self.image.fill(self.color)
        
        # Update rect
        self.rect = self.image.get_rect()
        self.rect.x = scaled_pos[0]
        self.rect.y = scaled_pos[1]
        
    def take_damage(self, amount, damage_type="physical", attacker=None, battle_system=None):
        """
        Apply damage to the entity.
        
        Args:
            amount (int): Amount of damage to take
            damage_type (str): Type of damage (physical, magical, etc.)
            attacker: The entity that caused the damage (for passives)
            battle_system: The battle system reference (for passives)
            
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
    
    def use_sp(self, amount):
        """
        Use SP for casting spells.
    
        Args:
            amount (int): Amount of SP to use
        
        Returns:
            bool: True if entity had enough SP and it was used, False otherwise
        """

        if self.sp >= amount:
            self.sp -= amount
            return True
        return False
        
    def keep_on_screen(self):
        """
        Keep the entity within the screen boundaries.
        """
        current_width, current_height = pygame.display.get_surface().get_size()
        
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > current_width - self.rect.width:
            self.rect.x = current_width - self.rect.width
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > current_height - self.rect.height:
            self.rect.y = current_height - self.rect.height