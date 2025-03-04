"""
Targeting system for the RPG game.
Handles target selection in multi-enemy battles.
"""
import pygame
from constants import WHITE, YELLOW, RED, GREEN

class TargetingSystem:
    """
    Manages target selection in battle.
    """
    def __init__(self, enemies=None):
        """
        Initialize the targeting system.
        
        Args:
            enemies: List of enemies that can be targeted
        """
        self.active = False
        self.enemies = enemies or []
        self.selected_target_index = 0
        self.cursor_blink_timer = 0
        self.cursor_visible = True
    
    def get_valid_targets(self):
        """
        Get the list of valid targets (non-defeated enemies).
        
        Returns:
            List of valid enemy targets
        """
        return [enemy for enemy in self.enemies if not enemy.is_defeated()]
        
    def start_targeting(self, enemies):
        """
        Start the target selection process.
        
        Args:
            enemies: List of enemies that can be targeted
        """
        self.enemies = enemies
        self.active = True
        self.selected_target_index = 0
        
    def stop_targeting(self):
        """Stop the target selection process."""
        self.active = False
        
    def get_selected_target(self):
        """
        Get the currently selected target.
        
        Returns:
            The selected enemy, or None if no enemies
        """
        valid_targets = self.get_valid_targets()
        if not valid_targets:
            return None
            
        # Make sure the index is valid
        if self.selected_target_index >= len(valid_targets):
            self.selected_target_index = 0
            
        return valid_targets[self.selected_target_index]
        
    def next_target(self):
        """Select the next target in the list."""
        valid_targets = self.get_valid_targets()
        if valid_targets:
            self.selected_target_index = (self.selected_target_index + 1) % len(valid_targets)
            
    def previous_target(self):
        """Select the previous target in the list."""
        valid_targets = self.get_valid_targets()
        if valid_targets:
            self.selected_target_index = (self.selected_target_index - 1) % len(valid_targets)
            
    def update(self):
        """Update the targeting system animations."""
        if self.active:
            # Blink the cursor
            self.cursor_blink_timer += 1
            if self.cursor_blink_timer >= 30:  # Toggle every half second at 60 FPS
                self.cursor_visible = not self.cursor_visible
                self.cursor_blink_timer = 0
                
    def draw(self, screen):
        """
        Draw the targeting system UI.
        
        Args:
            screen: The pygame surface to draw on
        """
        if not self.active or not self.enemies:
            return
            
        # Get current selected enemy
        selected_enemy = self.get_selected_target()
        if not selected_enemy:
            return
            
        # Only draw when cursor is visible (for blinking effect)
        if self.cursor_visible:
            # Draw selection indicator (triangle pointing at the enemy)
            # Calculate triangle points relative to the enemy position
            enemy_rect = selected_enemy.rect
            
            # Draw triangle pointing at the enemy
            triangle_points = [
                (enemy_rect.centerx, enemy_rect.top - 10),  # Top point
                (enemy_rect.centerx - 5, enemy_rect.top - 5),  # Bottom left
                (enemy_rect.centerx + 5, enemy_rect.top - 5)   # Bottom right
            ]
            
            # Draw the triangle in yellow
            pygame.draw.polygon(screen, YELLOW, triangle_points)
            
        # Highlight the selected enemy
        pygame.draw.rect(screen, YELLOW, selected_enemy.rect, 2)
        
        # Create a small info panel showing enemy stats
        panel_width = 120
        panel_height = 50
        panel_x = selected_enemy.rect.right + 5
        panel_y = selected_enemy.rect.top
        
        # Adjust panel position if it would go off screen
        screen_width, screen_height = screen.get_size()
        if panel_x + panel_width > screen_width:
            panel_x = selected_enemy.rect.left - panel_width - 5
            
        # Draw panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 200))  # Semi-transparent black
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw enemy info
        font = pygame.font.SysFont('Arial', 12)
        name_text = font.render(f"{selected_enemy.character_class.name if selected_enemy.character_class else 'Enemy'} Lv{selected_enemy.level}", True, WHITE)
        hp_text = font.render(f"HP: {selected_enemy.hp}/{selected_enemy.max_hp}", True, GREEN)
        
        screen.blit(name_text, (panel_x + 5, panel_y + 5))
        screen.blit(hp_text, (panel_x + 5, panel_y + 20))