"""
Helper functions for drawing party status in battle.
"""
import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (WHITE, GREEN, RED, GRAY, BLUE, DARK_BLUE, SCREEN_WIDTH, SCREEN_HEIGHT, 
                      ORIGINAL_WIDTH, ORIGINAL_HEIGHT, ORANGE, YELLOW)
from utils import scale_position, scale_dimensions, scale_font_size

def draw_party_status(screen, party, turn_order, font, small_font):
    """
    Draw the status of all active party members.
    
    Args:
        screen: The pygame surface to draw on
        party: The player's party
        turn_order: The turn order system
        font: The main font to use
        small_font: The smaller font for detailed stats
    """
    # Get current screen dimensions
    current_width, current_height = screen.get_size()
    
    # Scale dimensions and position
    window_width, window_height = scale_dimensions(
        300, 20 * (len(party.active_members) + 1) + 30 * len(party.active_members), 
        ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height
    )
    window_x, window_y = scale_position(
        SCREEN_WIDTH - 300 - 20, SCREEN_HEIGHT - window_height - 5, 
        ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height
    )
    
    # Draw window background and border
    pygame.draw.rect(screen, (0, 0, 0, 200), (window_x, window_y, window_width, window_height))
    border_width = max(1, int(2 * (current_width / ORIGINAL_WIDTH)))
    pygame.draw.rect(screen, WHITE, (window_x, window_y, window_width, window_height), border_width)
    
    # Draw party header
    party_text = font.render("Party", True, WHITE)
    header_x = window_x + int(10 * (current_width / ORIGINAL_WIDTH))
    header_y = window_y + int(5 * (current_height / ORIGINAL_HEIGHT))
    screen.blit(party_text, (header_x, header_y))
    
    # Draw divider line
    divider_y = header_y + int(25 * (current_height / ORIGINAL_HEIGHT))
    pygame.draw.line(
        screen, WHITE, 
        (window_x + border_width, divider_y), 
        (window_x + window_width - border_width, divider_y),
        1
    )
    
    # Scale parameters for character stats
    char_y_base = divider_y + int(10 * (current_height / ORIGINAL_HEIGHT))
    char_height = int(30 * (current_height / ORIGINAL_HEIGHT))
    char_spacing = int(10 * (current_height / ORIGINAL_HEIGHT))
    bar_width = int(150 * (current_width / ORIGINAL_WIDTH))
    bar_height = int(10 * (current_height / ORIGINAL_HEIGHT))
    
    # Draw each character's status
    for i, character in enumerate(party.active_members):
        char_y = char_y_base + i * (char_height + char_spacing)
        
        # Highlight current character's turn
        current_combatant = turn_order.get_current() if turn_order else None
        is_current = (current_combatant == character)
        
        # Draw character name and level
        name_color = YELLOW if is_current else WHITE
        name_text = f"{character.name} Lv{character.level}"
        name_surface = small_font.render(name_text, True, name_color)
        screen.blit(name_surface, (header_x, char_y))
        
        # Draw HP bar
        hp_bar_y = char_y + int(15 * (current_height / ORIGINAL_HEIGHT))
        bar_x = header_x + int(100 * (current_width / ORIGINAL_WIDTH))
        
        # Background (gray)
        pygame.draw.rect(screen, GRAY, (bar_x, hp_bar_y, bar_width, bar_height))
        
        # Fill with current HP (orange)
        if character.max_hp > 0:
            hp_fill_width = int((character.hp / character.max_hp) * bar_width)
            pygame.draw.rect(screen, ORANGE, (bar_x, hp_bar_y, hp_fill_width, bar_height))
        
        # HP text
        hp_text = small_font.render(f"HP: {character.hp}/{character.max_hp}", True, WHITE)
        hp_text_x = header_x
        hp_text_y = hp_bar_y - int(2 * (current_height / ORIGINAL_HEIGHT))
        screen.blit(hp_text, (hp_text_x, hp_text_y))
        
        # Draw SP bar
        sp_bar_y = hp_bar_y + bar_height + int(5 * (current_height / ORIGINAL_HEIGHT))
        
        # Background (gray)
        pygame.draw.rect(screen, GRAY, (bar_x, sp_bar_y, bar_width, bar_height))
        
        # Fill with current SP (blue)
        if character.max_sp > 0:
            sp_fill_width = int((character.sp / character.max_sp) * bar_width)
            pygame.draw.rect(screen, BLUE, (bar_x, sp_bar_y, sp_fill_width, bar_height))
        
        # SP text
        sp_text = small_font.render(f"SP: {character.sp}/{character.max_sp}", True, WHITE)
        sp_text_x = header_x
        sp_text_y = sp_bar_y - int(2 * (current_height / ORIGINAL_HEIGHT))
        screen.blit(sp_text, (sp_text_x, sp_text_y))

def draw_turn_order_indicator(screen, battle_system):
    """
    Draw an indicator showing whose turn it is.
    
    Args:
        screen: The pygame surface to draw on
        battle_system: The battle system
    """
    # Get current screen dimensions
    current_width, current_height = screen.get_size()
    
    # Get the current combatant
    current_combatant = battle_system.turn_order.get_current()
    if not current_combatant:
        return
    
    # Create the indicator text
    font = pygame.font.SysFont('Arial', scale_font_size(18, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height))
    
    if current_combatant in battle_system.party.active_members:
        turn_text = font.render(f"{current_combatant.name}'s Turn", True, GREEN)
    else:
        turn_text = font.render(f"{current_combatant.name}'s Turn", True, RED)
    
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