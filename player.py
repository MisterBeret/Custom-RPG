"""
Player class for the RPG game.
"""
import pygame
from entities.entity import Entity
from constants import GREEN, SCREEN_WIDTH, SCREEN_HEIGHT

class Player(Entity):
    """
    Player character controllable by the user.
    """
    def __init__(self, x, y):
        """
        Initialize the player.
        
        Args:
            x (int): Initial x coordinate
            y (int): Initial y coordinate
        """
        super().__init__(x, y, 32, 48, GREEN)
        
        # Movement speed
        self.speed = 5
        
        # RPG Stats
        self.level = 1
        self.experience = 0
        self.max_level = 100
        
        # Battle stats
        self.max_hp = 10
        self.hp = 10
        self.attack = 1
        self.spd = 5  # Speed determines turn order
        self.defending = False
        
    def update(self, enemies=None):
        """
        Update the player's state and position.
        
        Args:
            enemies: Optional group of enemies to check for collisions
            
        Returns:
            The enemy collided with, or None if no collision
        """
        # Store the current position to revert if there's a collision
        previous_x = self.rect.x
        previous_y = self.rect.y
        
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Move the character based on key presses
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            
        # Keep player within screen bounds
        self.keep_on_screen()
            
        # Check for collision with enemies
        if enemies:
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    return enemy  # Return the enemy we collided with
    
        return None  # No collision with enemies

    def reset_position(self):
        """
        Reset to center of screen after battle.
        """
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT // 2
        
    def take_damage(self, amount):
        """
        Apply damage to the player, with reduction if defending.
        
        Args:
            amount (int): Amount of damage to take
        """
        # Apply damage reduction if defending
        if self.defending:
            amount = max(0, amount - 1)
            self.defending = False  # Reset defending status
        
        # Call the parent class method
        super().take_damage(amount)
        
    def defend(self):
        """
        Enter defensive stance to reduce incoming damage.
        """
        self.defending = True
        
    def gain_experience(self, amount):
        """
        Add experience to the player and check for level up.
        
        Args:
            amount (int): Amount of experience to add
            
        Returns:
            bool: True if player leveled up, False otherwise
        """
        self.experience += amount
        
        # Simple level up condition (can be made more complex)
        if self.experience >= self.level * 10 and self.level < self.max_level:
            self.level_up()
            return True
            
        return False
            
    def level_up(self):
        """
        Increase player level and stats.
        """
        self.level += 1
        self.max_hp += 2
        self.hp = self.max_hp  # Restore HP on level up
        self.attack += 1
        
        # Every 3 levels, increase speed
        if self.level % 3 == 0:
            self.spd += 1
