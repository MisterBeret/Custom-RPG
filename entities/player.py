"""
Player class for the RPG game.
"""
import pygame
from entities.entity import Entity
from constants import GREEN, SCREEN_WIDTH, SCREEN_HEIGHT
from systems.inventory import Inventory  # Import the inventory system

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
        self.max_mp = 5  # Player starts with 5 MP
        self.mp = 5      # Current MP
        self.attack = 2  # Attack set to 2
        self.defense = 1  # Defense stat set to 1
        self.intelligence = 2  # Intelligence set to 2 for magic damage
        self.resilience = 1    # Resilience set to 1 to reduce magic damage
        self.acc = 2  # New accuracy stat
        self.spd = 5  # Speed determines turn order
        self.defending = False
        self.defense_multiplier = 1  # New property to track defense multiplier
        
        # Inventory
        self.inventory = Inventory()
        
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
        Apply damage to the player, accounting for defense.
        
        Args:
            amount (int): Amount of damage to take
        """
        # Defense multiplier is handled in battle_system calculation now
        # Just call the parent class method
        super().take_damage(amount)
        
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
        self.max_mp += 1
        self.mp = self.max_mp  # Restore MP on level up
        self.attack += 1
        
        # Every 2 levels, increase defense and intelligence
        if self.level % 2 == 0:
            self.defense += 1
            self.intelligence += 1
    
        # Every 4 levels, increase resilience
        if self.level % 4 == 0:
            self.resilience += 1

        # Every 4 levels, increase accuracy
        if self.level % 4 == 0:
            self.acc += 1
            
        # Every 3 levels, increase speed
        if self.level % 3 == 0:
            self.spd += 1
            
    def use_item(self, item_name, target=None):
        """
        Use an item from the inventory.
        
        Args:
            item_name: The name of the item to use
            target: The target of the item effect (if applicable)
            
        Returns:
            tuple: (bool, str) - Success flag and result message
        """
        from systems.inventory import get_item_effect
        
        # Check if we have the item
        if not self.inventory.use_item(item_name):
            return False, f"No {item_name} available!"
            
        # Get the item effect
        item = get_item_effect(item_name)
        if not item:
            return False, f"Unknown item: {item_name}"
            
        # Apply the effect
        if item.effect_type == "healing":
            old_hp = self.hp
            self.hp = min(self.hp + item.effect_value, self.max_hp)
            healed = self.hp - old_hp
            return True, f"Used {item_name}! Restored {healed} HP."
            
        elif item.effect_type == "scan" and target:
            return True, f"Used {item_name}! {target.__class__.__name__} stats:\nHP: {target.hp}/{target.max_hp}\nATK: {target.attack}\nDEF: {target.defense}\nSPD: {target.spd}\nACC: {target.acc}"
            
        return False, f"Couldn't use {item_name} effectively."