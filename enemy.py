"""
Enemy class for the RPG game.
"""
import pygame
import random
from entities.entity import Entity
from constants import RED, SCREEN_WIDTH, SCREEN_HEIGHT

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
        self.attack = 1
        self.spd = 3  # Speed determines turn order
        self.xp = 1   # XP awarded to player upon defeat
        
    def update(self):
        """
        Update enemy state. Can be expanded for movement patterns.
        """
        # Currently no movement or AI, but can be added here
        pass
        
    @classmethod
    def spawn_random(cls):
        """
        Create an enemy at a random position on the screen.
        
        Returns:
            Enemy: A new enemy at a random position
        """
        x = random.randint(100, SCREEN_WIDTH - 100)
        y = random.randint(100, SCREEN_HEIGHT - 100)
        return cls(x, y)
