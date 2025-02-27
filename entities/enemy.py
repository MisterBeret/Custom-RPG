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
        self.max_mp = 0  # Enemy starts with 0 MP
        self.mp = 0      # Current MP
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
        Enter defensive stance to double defense.
        """
        self.defending = True
        self.defense_multiplier = 2  # Double defense when defending
        
    def end_turn(self):
        """
        End the turn and reset temporary stat changes.
        """
        if self.defending:
            self.defending = False
            self.defense_multiplier = 1  # Reset defense multiplier
        
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