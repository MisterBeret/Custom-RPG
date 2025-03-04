"""
Battle visualizer for RPG game.
Handles visual effects during battle.
"""
import pygame
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import (BLACK, WHITE, GREEN, RED, BLUE, PURPLE, YELLOW, 
                      ORIGINAL_WIDTH, ORIGINAL_HEIGHT)

def draw_battle_background(screen):
    """
    Draw the battle background.
    
    Args:
        screen: The pygame surface to draw on
    """
    # Get current screen dimensions
    current_width, current_height = screen.get_size()
    
    # Fill with dark blue-gray gradient
    screen.fill((20, 20, 30))
    
    # Draw some simple ground
    ground_height = current_height // 4
    ground_y = current_height - ground_height
    
    # Draw gradient for ground
    for y in range(ground_height):
        # Gradient from dark green to lighter brown-green
        color_value = 40 + int(y * 0.6)
        ground_color = (color_value, color_value + 20, color_value // 2)
        pygame.draw.line(screen, ground_color, 
                       (0, ground_y + y), 
                       (current_width, ground_y + y))
    
    # Add some subtle details to make it less plain
    # Draw a few random distant mountains/hills
    for i in range(5):
        # Calculate hill parameters
        hill_width = random.randint(int(current_width // 3), int(current_width // 1.5))
        hill_height = random.randint(int(current_height // 10), int(current_height // 6))
        hill_x = random.randint(-hill_width // 2, current_width - hill_width // 2)
        hill_y = ground_y
        
        # Random dark color for the hill
        hill_color = (
            random.randint(30, 50),
            random.randint(40, 60),
            random.randint(50, 70)
        )
        
        # Draw hill as a simple arc
        points = []
        for x in range(hill_width):
            # Calculate y using a simple parabola
            y_offset = hill_height * (1 - ((x - hill_width/2) / (hill_width/2))**2)
            points.append((hill_x + x, hill_y - y_offset))
        
        # Add bottom points to complete the polygon
        points.append((hill_x + hill_width, hill_y))
        points.append((hill_x, hill_y))
        
        # Draw the hill
        if len(points) >= 3:  # Need at least 3 points for a polygon
            pygame.draw.polygon(screen, hill_color, points)

class BattleVisualizer:
    """
    Handles visual effects during battle.
    """
    def __init__(self, battle_system):
        """
        Initialize the battle visualizer.
        
        Args:
            battle_system: The battle system to visualize
        """
        self.battle_system = battle_system
        self.effects = []
        
    def add_effect(self, effect_type, **kwargs):
        """
        Add a visual effect.
        
        Args:
            effect_type: The type of effect to add
            **kwargs: Additional parameters for the effect
        """
        if effect_type == "hit":
            # Create a hit effect
            target = kwargs.get("target")
            if target:
                self.effects.append({
                    "type": "hit",
                    "position": (target.rect.centerx, target.rect.centery),
                    "size": 20,
                    "duration": 15,
                    "current_frame": 0
                })
        elif effect_type == "spell":
            # Create a spell effect
            spell_name = kwargs.get("spell_name")
            target = kwargs.get("target")
            if spell_name and target:
                if spell_name == "FIRE":
                    self.effects.append({
                        "type": "fire",
                        "position": (target.rect.centerx, target.rect.centery),
                        "size": 30,
                        "duration": 20,
                        "current_frame": 0
                    })
                elif spell_name == "HEAL":
                    self.effects.append({
                        "type": "heal",
                        "position": (target.rect.centerx, target.rect.centery),
                        "size": 40,
                        "duration": 25,
                        "current_frame": 0
                    })
        
    def update(self):
        """Update all visual effects."""
        # Update each effect
        for effect in self.effects[:]:  # Use a copy for safe removal
            effect["current_frame"] += 1
            if effect["current_frame"] >= effect["duration"]:
                self.effects.remove(effect)
        
    def draw(self, screen):
        """
        Draw all visual effects.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Draw each effect
        for effect in self.effects:
            if effect["type"] == "hit":
                self._draw_hit_effect(screen, effect)
            elif effect["type"] == "fire":
                self._draw_fire_effect(screen, effect)
            elif effect["type"] == "heal":
                self._draw_heal_effect(screen, effect)
    
    def _draw_hit_effect(self, screen, effect):
        """
        Draw a hit effect.
        
        Args:
            screen: The pygame surface to draw on
            effect: The effect data
        """
        # Calculate effect parameters
        progress = effect["current_frame"] / effect["duration"]
        size = int(effect["size"] * (1 - progress))
        alpha = int(255 * (1 - progress))
        
        # Create a surface for the effect
        effect_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw the effect (a simple burst)
        pygame.draw.circle(effect_surface, (*RED, alpha), (size, size), size)
        
        # Draw some radiating lines
        for angle in range(0, 360, 45):
            from math import sin, cos, radians
            end_x = size + int(size * 0.8 * cos(radians(angle)))
            end_y = size + int(size * 0.8 * sin(radians(angle)))
            pygame.draw.line(effect_surface, (*WHITE, alpha), 
                           (size, size), (end_x, end_y), 2)
        
        # Draw the effect at the target position
        screen.blit(effect_surface, 
                  (effect["position"][0] - size, 
                   effect["position"][1] - size))
    
    def _draw_fire_effect(self, screen, effect):
        """
        Draw a fire spell effect.
        
        Args:
            screen: The pygame surface to draw on
            effect: The effect data
        """
        # Calculate effect parameters
        progress = effect["current_frame"] / effect["duration"]
        size = int(effect["size"] * (1 - progress * 0.5))  # Maintain size longer
        alpha = int(255 * (1 - progress))
        
        # Create a surface for the effect
        effect_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw multiple overlapping circles for a fire effect
        fire_colors = [
            (255, 50, 0, alpha),     # Orange-red
            (255, 150, 0, alpha),    # Orange
            (255, 220, 0, alpha)     # Yellow
        ]
        
        for i, color in enumerate(fire_colors):
            circle_size = size * (0.8 - i * 0.2)
            offset_y = int(size * 0.1 * i)  # Offset for flame shape
            pygame.draw.circle(effect_surface, color, 
                             (size, size - offset_y), 
                             int(circle_size))
        
        # Add some random sparks
        for _ in range(5):
            spark_x = random.randint(size // 2, size + size // 2)
            spark_y = random.randint(size // 2, size + size // 2)
            spark_size = random.randint(1, 3)
            pygame.draw.circle(effect_surface, (255, 255, 200, alpha),
                             (spark_x, spark_y), spark_size)
        
        # Draw the effect at the target position
        screen.blit(effect_surface, 
                  (effect["position"][0] - size, 
                   effect["position"][1] - size))
    
    def _draw_heal_effect(self, screen, effect):
        """
        Draw a healing spell effect.
        
        Args:
            screen: The pygame surface to draw on
            effect: The effect data
        """
        # Calculate effect parameters
        progress = effect["current_frame"] / effect["duration"]
        size = int(effect["size"] * (1 - progress * 0.3))  # Maintain size longer
        alpha = int(255 * (1 - progress))
        
        # Create a surface for the effect
        effect_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw ascending particles
        num_particles = 12
        for i in range(num_particles):
            angle = (i / num_particles) * 360
            from math import sin, cos, radians
            
            # Particle position (moves upward over time)
            radius = size * 0.7 * (1 - progress * 0.5)
            offset_y = size * progress * 1.5  # Rising effect
            
            x = size + int(radius * cos(radians(angle)))
            y = size + int(radius * sin(radians(angle))) - int(offset_y)
            
            # Particle color (blue/green for healing)
            particle_color = (100, 255, 200, alpha)
            particle_size = int(3 * (1 - progress))
            
            pygame.draw.circle(effect_surface, particle_color, (x, y), particle_size)
        
        # Draw a fading plus sign in the center
        plus_size = int(size * 0.5)
        plus_thickness = max(1, int(3 * (1 - progress)))
        
        # Horizontal line
        pygame.draw.line(effect_surface, (100, 255, 150, alpha),
                       (size - plus_size, size),
                       (size + plus_size, size),
                       plus_thickness)
        
        # Vertical line
        pygame.draw.line(effect_surface, (100, 255, 150, alpha),
                       (size, size - plus_size),
                       (size, size + plus_size),
                       plus_thickness)
        
        # Draw the effect at the target position
        screen.blit(effect_surface, 
                  (effect["position"][0] - size, 
                   effect["position"][1] - size))