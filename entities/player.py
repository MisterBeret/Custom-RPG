"""
Player class for the RPG game.
"""
import pygame
from entities.entity import Entity
from constants import GREEN, SCREEN_WIDTH, SCREEN_HEIGHT, ORIGINAL_WIDTH, ORIGINAL_HEIGHT
from systems.inventory import Inventory
from systems.spell_system import SpellBook
from utils import scale_position, scale_dimensions

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
        
        # Base movement speed (will be scaled based on resolution)
        self.base_speed = 5
        self.speed = 5
        
        # RPG Stats
        self.level = 1
        self.experience = 0
        self.max_level = 100
        
        # Battle stats
        self.max_hp = 10
        self.hp = 10
        self.max_sp = 5  # Starting SP
        self.sp = 5      # Current SP
        self.attack = 2  # Attack set to 2
        self.defense = 1  # Defense stat set to 1
        self.intelligence = 2  # Intelligence set to 2 for magic damage
        self.resilience = 1    # Resilience set to 1 to reduce magic damage
        self.acc = 2  # New accuracy stat
        self.spd = 5  # Speed determines turn order
        self.defending = False
        
        # Inventory
        self.inventory = Inventory()
        
        # Spell book
        self.spellbook = SpellBook()
    
    def update_scale(self, current_width, current_height):
        """
        Update player dimensions, position, and speed based on current screen resolution.
        
        Args:
            current_width (int): Current screen width
            current_height (int): Current screen height
        """
        # Call the parent class update_scale method
        super().update_scale(current_width, current_height)
        
        # Scale the movement speed based on resolution
        width_scale = current_width / ORIGINAL_WIDTH
        height_scale = current_height / ORIGINAL_HEIGHT
        scale_factor = (width_scale + height_scale) / 2  # Average scale factor
        
        # Adjust speed proportionally to resolution
        self.speed = max(1, int(self.base_speed * scale_factor))
        
    def update(self, enemies=None):
        """
        Update the player's state and position.
        
        Args:
            enemies: Optional group of enemies to check for collisions
            
        Returns:
            The enemy collided with, or None if no collision
        """
        # Get current screen dimensions
        current_width, current_height = pygame.display.get_surface().get_size()
        
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
        
        # Update original position to track where we are
        scale_factor_x = ORIGINAL_WIDTH / current_width
        scale_factor_y = ORIGINAL_HEIGHT / current_height
        self.original_x = self.rect.x * scale_factor_x
        self.original_y = self.rect.y * scale_factor_y
            
        # Check for collision with enemies
        if enemies:
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    # Return to previous position to avoid movement into enemy
                    self.rect.x = previous_x
                    self.rect.y = previous_y
                    return enemy  # Return the enemy we collided with

        return None  # No collision with enemies

    def reset_position(self):
        """
        Reset to center of screen after battle.
        """
        # Get current screen dimensions
        current_width, current_height = pygame.display.get_surface().get_size()
        
        # Set position to center of current screen
        self.rect.x = current_width // 2
        self.rect.y = current_height // 2
        
        # Update original position to match new position
        scale_factor_x = ORIGINAL_WIDTH / current_width
        scale_factor_y = ORIGINAL_HEIGHT / current_height
        self.original_x = self.rect.x * scale_factor_x
        self.original_y = self.rect.y * scale_factor_y
        
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
        
    def end_turn(self):
        """
        End the turn and reset temporary stat changes.
        """
        if self.defending:
            self.defending = False
    
    def cast_spell(self, spell_name, target=None):
        """
        Cast a spell from the spellbook.
        
        Args:
            spell_name: The name of the spell to cast
            target: The target of the spell effect (if applicable)
            
        Returns:
            tuple: (bool, str) - Success flag and result message
        """
        # Get the spell data
        spell = self.spellbook.get_spell(spell_name)
        if not spell:
            return False, f"You don't know the spell {spell_name}!"
        
        # Check if player has enough SP
        if self.sp < spell.sp_cost:
            return False, f"Not enough SP to cast {spell_name}!"
        
        # Use the SP
        if not self.use_sp(spell.sp_cost):
            return False, f"Failed to use SP for {spell_name}!"
        
        # Apply the spell effect based on type
        if spell.effect_type == "damage" and target:
            # Calculate magic damage using INT and spell power
            from systems.battle_system import BattleSystem
            battle_system = BattleSystem(self, target, "FAST")  # Temporary instance just for calculation
            damage = battle_system.calculate_magic_damage(self, target, spell.base_power)
            
            # Apply damage to target
            target.take_damage(damage)
            
            # Return result
            if target.is_defeated():
                return True, f"Cast {spell_name}! Dealt {damage} magic damage! Enemy defeated!"
            else:
                return True, f"Cast {spell_name}! Dealt {damage} magic damage!"
                
        elif spell.effect_type == "healing":
            # For healing spells, add intelligence to the base power
            healing_amount = spell.base_power + self.intelligence
            
            # Store original HP to calculate actual healing
            original_hp = self.hp
            
            # Apply healing (capped at max_hp)
            self.hp = min(self.hp + healing_amount, self.max_hp)
            
            # Calculate actual healing done
            actual_healing = self.hp - original_hp
            
            return True, f"Cast {spell_name}! Restored {actual_healing} HP!"
        
        return False, f"Couldn't cast {spell_name} effectively."
        
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
        self.max_sp += 1
        self.sp = self.max_sp  # Restore SP on level up
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