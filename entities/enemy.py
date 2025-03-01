"""
Enemy class for the RPG game.
"""
import pygame
import random
from entities.entity import Entity
from constants import RED, SCREEN_WIDTH, SCREEN_HEIGHT, ORIGINAL_WIDTH, ORIGINAL_HEIGHT
from utils import scale_position, scale_dimensions

class Enemy(Entity):
    """
    Enemy entity that can battle with the player.
    """
    def __init__(self, x, y):
        """
        Initialize an enemy.
        
        Args:
            x (int): Initial x coordinate
            y (int): Initial y coordinate
        """
        super().__init__(x, y, 32, 32, RED)
        
        # Battle stats
        self.max_hp = 3
        self.hp = 3
        self.max_sp = 0  # Enemy's starting SP
        self.sp = 0      # Current SP
        self.attack = 2  # Attack set to 2
        self.defense = 1  # Defense stat set to 1
        self.intelligence = 0  # Intelligence set to 0 (no magic ability)
        self.resilience = 1    # Resilience set to 1 to reduce magic damage
        self.acc = 2  # New accuracy stat
        self.spd = 3  # Speed determines turn order
        self.xp = 5   # XP awarded to player upon defeat
        self.defending = False
        self.defense_multiplier = 1  # New property to track defense multiplier
        
    def update(self):
        """
        Update enemy state. Can be expanded for movement patterns.
        """
        # Currently no movement or AI, but can be added here
        pass
    
    def defend(self):
        """
        Enter defensive stance to halve incoming damage and increase evasion by 25%.
        """
        self.defending = True
        
    def end_turn(self):
        """
        End the turn and reset temporary stat changes.
        """
        self.defending = False
        
    @classmethod
    def spawn_random(cls):
        """
        Create an enemy at a random position on the screen.
        
        Returns:
            Enemy: A new enemy at a random position
        """
        # Get current screen dimensions
        current_width, current_height = pygame.display.get_surface().get_size()
        
        # Calculate position in terms of original resolution
        x = random.randint(100, ORIGINAL_WIDTH - 100)
        y = random.randint(100, ORIGINAL_HEIGHT - 100)
        
        # Create enemy instance
        enemy = cls(x, y)
        
        # Scale enemy to match current resolution
        enemy.update_scale(current_width, current_height)
        
        return enemy