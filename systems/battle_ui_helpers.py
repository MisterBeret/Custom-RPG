"""
Helper functions for drawing battle UI elements.
"""
import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (WHITE, GREEN, RED, GRAY, ORANGE, YELLOW, 
                      ORIGINAL_WIDTH, ORIGINAL_HEIGHT)

def draw_enemy_name_tags(screen, enemies):
    """
    Draw name tags above each enemy.
    
    Args:
        screen: The pygame surface to draw on
        enemies: List of enemies to draw tags for
    """
    font = pygame.font.SysFont('Arial', 14)
    
    for enemy in enemies:
        if not enemy.is_defeated():
            # Create the name tag
            enemy_name = enemy.character_class.name if enemy.character_class else "Enemy"
            name_tag = font.render(f"{enemy_name} Lv{enemy.level}", True, WHITE)
            
            # Position the name tag above the enemy
            tag_x = enemy.rect.centerx - name_tag.get_width() // 2
            tag_y = enemy.rect.top - name_tag.get_height() - 5
            
            # Draw a small background rectangle
            bg_rect = pygame.Rect(tag_x - 2, tag_y - 2, 
                                name_tag.get_width() + 4, 
                                name_tag.get_height() + 4)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, WHITE, bg_rect, 1)
            
            # Draw the name tag
            screen.blit(name_tag, (tag_x, tag_y))

def draw_enemy_health_bars(screen, enemies):
    """
    Draw health bars above each enemy.
    
    Args:
        screen: The pygame surface to draw on
        enemies: List of enemies to draw health bars for
    """
    for enemy in enemies:
        if not enemy.is_defeated():
            # Calculate bar dimensions
            bar_width = enemy.rect.width
            bar_height = 5
            bar_x = enemy.rect.left
            bar_y = enemy.rect.top - bar_height - 15  # Position above name tag
            
            # Draw background (depleted health shown as gray)
            pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Calculate filled portion
            if enemy.max_hp > 0:  # Avoid division by zero
                fill_width = int((enemy.hp / enemy.max_hp) * bar_width)
                pygame.draw.rect(screen, ORANGE, (bar_x, bar_y, fill_width, bar_height))
            
            # Draw border
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

def draw_turn_order_indicator(screen, battle_system):
    """
    Draw an indicator showing the current turn (player or enemy).
    
    Args:
        screen: The pygame surface to draw on
        battle_system: The current battle system
    """
    # Get current screen dimensions
    current_width, current_height = screen.get_size()
    
    # Create the indicator
    font = pygame.font.SysFont('Arial', 18)
    
    if battle_system.turn == 0:
        turn_text = font.render("Player's Turn", True, GREEN)
    else:
        turn_text = font.render("Enemy's Turn", True, RED)
    
    # Position at top center of screen
    indicator_x = (current_width // 2) - (turn_text.get_width() // 2)
    indicator_y = 20
    
    # Draw a small background
    bg_rect = pygame.Rect(indicator_x - 5, indicator_y - 5, 
                          turn_text.get_width() + 10, 
                          turn_text.get_height() + 10)
    pygame.draw.rect(screen, (0, 0, 0), bg_rect)
    pygame.draw.rect(screen, WHITE, bg_rect, 1)
    
    # Draw the text
    screen.blit(turn_text, (indicator_x, indicator_y))