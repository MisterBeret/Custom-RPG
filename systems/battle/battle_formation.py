"""
Battle formation system for positioning characters in battle.
"""
import pygame
from constants import ORIGINAL_WIDTH, ORIGINAL_HEIGHT

class BattleFormation:
    """
    Manages the positioning of characters and enemies in battle.
    """
    def __init__(self, screen_width, screen_height):
        """
        Initialize the battle formation system.
        
        Args:
            screen_width: The current screen width
            screen_height: The current screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
    def position_party_members(self, party):
        """
        Calculate and assign positions for party members in battle.
        
        Args:
            party: The player's party
        """
        # Position party members on the right side of the screen
        active_members = party.active_members
        member_count = len(active_members)
        
        # Scale factors
        scale_x = self.screen_width / ORIGINAL_WIDTH
        scale_y = self.screen_height / ORIGINAL_HEIGHT
        
        # Base positions for party members (right side of screen, in formation)
        if member_count == 1:
            # Single character
            positions = [(int(ORIGINAL_WIDTH * 0.8), int(ORIGINAL_HEIGHT * 0.5))]
        elif member_count == 2:
            # Two characters side by side
            positions = [
                (int(ORIGINAL_WIDTH * 0.8), int(ORIGINAL_HEIGHT * 0.4)),
                (int(ORIGINAL_WIDTH * 0.8), int(ORIGINAL_HEIGHT * 0.6))
            ]
        elif member_count == 3:
            # Three characters in triangle formation
            positions = [
                (int(ORIGINAL_WIDTH * 0.8), int(ORIGINAL_HEIGHT * 0.3)),
                (int(ORIGINAL_WIDTH * 0.8), int(ORIGINAL_HEIGHT * 0.5)),
                (int(ORIGINAL_WIDTH * 0.8), int(ORIGINAL_HEIGHT * 0.7))
            ]
        elif member_count >= 4:
            # Four characters in square formation
            positions = [
                (int(ORIGINAL_WIDTH * 0.8), int(ORIGINAL_HEIGHT * 0.3)),
                (int(ORIGINAL_WIDTH * 0.8), int(ORIGINAL_HEIGHT * 0.5)),
                (int(ORIGINAL_WIDTH * 0.8), int(ORIGINAL_HEIGHT * 0.7)),
                (int(ORIGINAL_WIDTH * 0.7), int(ORIGINAL_HEIGHT * 0.5))
            ]
        
        # Apply positions to party members
        for i, character in enumerate(active_members):
            if i < len(positions):
                # Scale the position based on current screen size
                pos_x = int(positions[i][0] * scale_x)
                pos_y = int(positions[i][1] * scale_y)
                
                # Store battle position coordinates
                character.battle_pos_x = pos_x
                character.battle_pos_y = pos_y
                
                # Update character rectangle for rendering
                character.rect.centerx = pos_x
                character.rect.centery = pos_y
                
    def position_enemies(self, enemies):
        """
        Calculate and assign positions for enemies in battle.
        
        Args:
            enemies: List of enemy entities
        """
        enemy_count = len(enemies)
        
        # Scale factors
        scale_x = self.screen_width / ORIGINAL_WIDTH
        scale_y = self.screen_height / ORIGINAL_HEIGHT
        
        # Determine positions based on enemy count
        if enemy_count == 1:
            # Single enemy centered
            positions = [(int(ORIGINAL_WIDTH * 0.25), int(ORIGINAL_HEIGHT * 0.5))]
        elif enemy_count == 2:
            # Two enemies side by side
            positions = [
                (int(ORIGINAL_WIDTH * 0.2), int(ORIGINAL_HEIGHT * 0.4)),
                (int(ORIGINAL_WIDTH * 0.3), int(ORIGINAL_HEIGHT * 0.6))
            ]
        elif enemy_count == 3:
            # Three enemies in triangle formation
            positions = [
                (int(ORIGINAL_WIDTH * 0.15), int(ORIGINAL_HEIGHT * 0.3)),
                (int(ORIGINAL_WIDTH * 0.25), int(ORIGINAL_HEIGHT * 0.5)),
                (int(ORIGINAL_WIDTH * 0.35), int(ORIGINAL_HEIGHT * 0.7))
            ]
        elif enemy_count == 4:
            # Four enemies in square formation
            positions = [
                (int(ORIGINAL_WIDTH * 0.15), int(ORIGINAL_HEIGHT * 0.3)),
                (int(ORIGINAL_WIDTH * 0.25), int(ORIGINAL_HEIGHT * 0.3)),
                (int(ORIGINAL_WIDTH * 0.15), int(ORIGINAL_HEIGHT * 0.6)),
                (int(ORIGINAL_WIDTH * 0.25), int(ORIGINAL_HEIGHT * 0.6))
            ]
        else:
            # More than 4 enemies in array formation (max 2 rows)
            positions = []
            row1_count = min(4, enemy_count)
            row2_count = enemy_count - row1_count
            
            # First row
            for i in range(row1_count):
                x = int(ORIGINAL_WIDTH * (0.15 + 0.07 * i))
                y = int(ORIGINAL_HEIGHT * 0.3)
                positions.append((x, y))
                
            # Second row
            for i in range(row2_count):
                x = int(ORIGINAL_WIDTH * (0.15 + 0.07 * i))
                y = int(ORIGINAL_HEIGHT * 0.6)
                positions.append((x, y))
        
        # Apply positions to enemies
        for i, enemy in enumerate(enemies):
            if i < len(positions):
                # Scale the position based on current screen size
                pos_x = int(positions[i][0] * scale_x)
                pos_y = int(positions[i][1] * scale_y)
                
                # Store battle position coordinates
                enemy.battle_pos_x = pos_x
                enemy.battle_pos_y = pos_y
                
                # Update enemy rectangle for rendering
                enemy.rect.centerx = pos_x
                enemy.rect.centery = pos_y
                
                # Store the battle position index
                enemy.battle_position = i