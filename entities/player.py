"""
Player class for the RPG game.
"""
import pygame
from entities.entity import Entity
from constants import GREEN, SCREEN_WIDTH, SCREEN_HEIGHT, ORIGINAL_WIDTH, ORIGINAL_HEIGHT
from systems.inventory import Inventory
from systems.spell_system import SpellBook
from systems.skill_system import SkillSet
from systems.ultimate_system import UltimateSet
from systems.passive_system import PassiveSet
from utils import scale_position, scale_dimensions

class Player(Entity):
    """
    Player character controllable by the user.
    """
    def __init__(self, x, y, character_class=None, level=1):
        """
        Initialize the player.
        
        Args:
            x (int): Initial x coordinate
            y (int): Initial y coordinate
        """
        super().__init__(x, y, 32, 48, GREEN, character_class, level)
        
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
        self.acc = 2  # Accuracy stat
        self.spd = 5  # Speed determines turn order
        self.defending = False
        
        # Inventory
        self.inventory = Inventory()
        
        if character_class:
            abilities = character_class.get_abilities_for_level(level)
            
            # Add spells
            self.spellbook = SpellBook()
            for spell_name in abilities["spells"]:
                self.spellbook.add_spell(spell_name)
            
            # Add skills
            self.skillset = SkillSet()
            for skill_name in abilities["skills"]:
                self.skillset.add_skill(skill_name)
            
            # Add ultimates
            self.ultimates = UltimateSet()
            for ultimate_name in abilities["ultimates"]:
                self.ultimates.add_ultimate(ultimate_name)
            
            # Add passives
            self.passives = PassiveSet(add_defaults=False)
            for passive_name in abilities["passives"]:
                self.passives.add_passive(passive_name)
        else:
            # Initialize with default abilities if no class is provided
            self.spellbook = SpellBook()
            self.skillset = SkillSet()
            self.ultimates = UltimateSet()
            self.passives = PassiveSet()
    
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
        
    def update(self, enemies=None, current_map=None):
        """
        Update the player's state and position with buffer zones for walls.
        
        Args:
            enemies: Optional group of enemies to check for collisions
            current_map: The current map for boundary checking
            
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
        
        # Calculate boundary line thickness and buffer zone
        line_thickness = max(1, int(5 * (current_width / ORIGINAL_WIDTH)))
        buffer_zone = line_thickness + self.speed # Extra pixels to prevent jitter
        
        # Handle horizontal movement
        if keys[pygame.K_LEFT] and (not current_map or self.rect.left > buffer_zone or current_map.connections["west"]):
            # Only move left if not at boundary or if there's a connection
            self.rect.x -= self.speed
            
            # If we've crossed a solid boundary, snap to exactly the boundary
            if current_map and self.rect.left < line_thickness and not current_map.connections["west"]:
                self.rect.left = line_thickness
                
        elif keys[pygame.K_RIGHT] and (not current_map or self.rect.right < current_width - buffer_zone or current_map.connections["east"]):
            # Only move right if not at boundary or if there's a connection
            self.rect.x += self.speed
            
            # If we've crossed a solid boundary, snap to exactly the boundary
            if current_map and self.rect.right > current_width - line_thickness and not current_map.connections["east"]:
                self.rect.right = current_width - line_thickness
        
        # Handle vertical movement
        if keys[pygame.K_UP] and (not current_map or self.rect.top > buffer_zone or current_map.connections["north"]):
            # Only move up if not at boundary or if there's a connection
            self.rect.y -= self.speed
            
            # If we've crossed a solid boundary, snap to exactly the boundary
            if current_map and self.rect.top < line_thickness and not current_map.connections["north"]:
                self.rect.top = line_thickness
                
        elif keys[pygame.K_DOWN] and (not current_map or self.rect.bottom < current_height - buffer_zone or current_map.connections["south"]):
            # Only move down if not at boundary or if there's a connection
            self.rect.y += self.speed
            
            # If we've crossed a solid boundary, snap to exactly the boundary
            if current_map and self.rect.bottom > current_height - line_thickness and not current_map.connections["south"]:
                self.rect.bottom = current_height - line_thickness
        
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
        
    def take_damage(self, amount, damage_type="physical", attacker=None, battle_system=None):
        """
        Apply damage to the player, accounting for defense and potentially triggering passives.
        
        Args:
            amount (int): Amount of damage to take
            damage_type (str): Type of damage (physical, magical, etc.)
            attacker: The entity that caused the damage (for passives)
            battle_system: The battle system reference (for passives)
            
        Returns:
            tuple: (bool, str) - Whether a passive was triggered and any resulting message
        """
        # Apply damage using parent method
        super().take_damage(amount)
        
        # Check if we should trigger any passives
        passive_triggered = False
        passive_message = ""
        
        # Only try to trigger "on_hit" passives if we were actually hit (damage > 0)
        # and if we have necessary context (attacker and battle_system)
        if amount > 0 and damage_type == "physical" and attacker and battle_system:
            passive_triggered, passive_message = self.passives.trigger_passive(
                trigger_type="on_hit",
                battle_system=battle_system,
                entity=self,
                target=attacker
            )
            
        return passive_triggered, passive_message
        
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
    
    def use_skill(self, skill_name, target=None):
        """
        Use a skill from the skillset.
        
        Args:
            skill_name: The name of the skill to use
            target: The target of the skill effect (if applicable)
            
        Returns:
            tuple: (bool, str) - Success flag and result message
        """
        # Get the skill data
        skill = self.skillset.get_skill(skill_name)
        if not skill:
            return False, f"You don't know the skill {skill_name}!"
        
        # Check if player has enough resources to use the skill
        if skill.cost_type == "sp" and self.sp < skill.sp_cost:
            return False, f"Not enough SP to use {skill_name}!"
        elif skill.cost_type == "hp" and self.hp <= skill.hp_cost:  # Don't allow HP to reach 0
            return False, f"Not enough HP to use {skill_name}!"
        elif skill.cost_type == "both" and (self.sp < skill.sp_cost or self.hp <= skill.hp_cost):
            return False, f"Not enough resources to use {skill_name}!"
        
        # Apply resource costs
        if skill.sp_cost > 0:
            self.use_sp(skill.sp_cost)
        if skill.hp_cost > 0:
            self.take_damage(skill.hp_cost)
        
        # Apply the skill effect based on type
        if skill.effect_type == "analyze" and target:
            return True, f"Used {skill_name}! {target.__class__.__name__} stats:\nHP: {target.hp}/{target.max_hp}\nATK: {target.attack}\nDEF: {target.defense}\nSPD: {target.spd}\nACC: {target.acc}\nRES: {target.resilience}"
            
        # Add more skill effect types here
        
        return False, f"Couldn't use {skill_name} effectively."
    
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
        
    def use_ultimate(self, ultimate_name, target=None):
        """
        Use an ultimate ability.
        
        Args:
            ultimate_name: The name of the ultimate to use
            target: The target of the ultimate (if applicable)
            
        Returns:
            tuple: (bool, str) - Success flag and result message
        """
        # Get the ultimate data
        ultimate = self.ultimates.get_ultimate(ultimate_name)
        if not ultimate:
            return False, f"You don't know the ultimate {ultimate_name}!"
        
        # Check if the ultimate is available for use
        if not ultimate.available:
            return False, f"{ultimate_name} has already been used! Rest to restore it."
        
        # Apply the ultimate effect based on type
        if ultimate.effect_type == "damage" and target:
            # Calculate damage with power multiplier
            damage = int(self.attack * ultimate.power_multiplier)
            
            # Apply damage to target
            target.take_damage(damage)
            
            # Mark as used
            ultimate.available = False
            
            # Return result
            if target.is_defeated():
                return True, f"Used {ultimate_name}! Dealt a massive {damage} damage! Enemy defeated!"
            else:
                return True, f"Used {ultimate_name}! Dealt a massive {damage} damage!"
        
        # Add more ultimate effect types here as needed
        
        return False, f"Couldn't use {ultimate_name} effectively."
        
    def rest(self):
        """
        Rest to restore ultimate abilities and potentially other resources.
        """
        # Restore all ultimates
        self.ultimates.rest()
    
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
        Increase player level and stats based on character class.
        """
        self.level += 1
        
        if self.character_class:
            # Get updated stats from class
            stats = self.character_class.get_stat_block(self.level)
            
            # Store old values to calculate differences
            old_max_hp = self.max_hp
            old_max_sp = self.max_sp
            
            # Update stats
            self.max_hp = stats["hp"]
            self.max_sp = stats["sp"]
            self.attack = stats["attack"]
            self.defense = stats["defense"]
            self.intelligence = stats["intelligence"]
            self.resilience = stats["resilience"]
            self.acc = stats["acc"]
            self.spd = stats["spd"]
            
            # Check for new abilities
            new_abilities = self.character_class.get_abilities_for_level(self.level)
            
            # Add any new spells
            for spell_name in new_abilities["spells"]:
                if spell_name not in self.spellbook.get_spell_names():
                    self.spellbook.add_spell(spell_name)
                    print(f"Learned new spell: {spell_name}")
            
            # Add any new skills
            for skill_name in new_abilities["skills"]:
                if skill_name not in self.skillset.get_skill_names():
                    self.skillset.add_skill(skill_name)
                    print(f"Learned new skill: {skill_name}")
            
            # Add any new ultimates
            for ultimate_name in new_abilities["ultimates"]:
                if ultimate_name not in self.ultimates.get_ultimate_names():
                    self.ultimates.add_ultimate(ultimate_name)
                    print(f"Learned new ultimate: {ultimate_name}")
            
            # Add any new passives
            for passive_name in new_abilities["passives"]:
                if passive_name not in self.passives.get_passive_names():
                    self.passives.add_passive(passive_name)
                    print(f"Learned new passive: {passive_name}")
        else:
            # If no class is provided, fall back on increasing every stat by 1
            self.max_hp += 1
            self.max_sp += 1
            self.attack += 1
            self.defense += 1
            self.intelligence += 1
            self.resilience += 1
            self.acc += 1
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