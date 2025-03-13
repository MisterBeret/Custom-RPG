"""
Enhanced targeting system for the RPG game.
Handles target selection for both enemies and allies.
"""
import pygame
from constants import WHITE, YELLOW, RED, GREEN, BLUE
from entities.player import Player

class TargetingSystem:
    """
    Manages target selection in battle for both enemies and allies.
    """
    # Target groups
    ENEMIES = 0
    ALLIES = 1
    ALL = 2  # Both enemies and allies
    SELF = 3  # Only self
    
    def __init__(self, party=None, enemies=None):
        """
        Initialize the targeting system.
        
        Args:
            party: The player party
            enemies: List of enemies that can be targeted
        """
        self.active = False
        self.party = party or []
        self.enemies = enemies or []
        self.target_group = self.ENEMIES  # Default to targeting enemies
        self.selected_target_index = 0
        self.cursor_blink_timer = 0
        self.cursor_visible = True
        self.current_character = None  # Character who is selecting a target
    
    def get_valid_targets(self):
        """
        Get the list of valid targets based on current target group.
        
        Returns:
            List of valid targets
        """
        if self.target_group == self.ENEMIES:
            return [enemy for enemy in self.enemies if not enemy.is_defeated()]
        elif self.target_group == self.ALLIES:
            return [ally for ally in self.party.active_members if not ally.is_defeated()]
        elif self.target_group == self.ALL:
            valid_enemies = [enemy for enemy in self.enemies if not enemy.is_defeated()]
            valid_allies = [ally for ally in self.party.active_members if not ally.is_defeated()]
            return valid_enemies + valid_allies
        elif self.target_group == self.SELF and self.current_character:
            return [self.current_character]
        
        return []
        
    def start_targeting(self, character, target_group=ENEMIES):
        """
        Start the target selection process.
        
        Args:
            character: The character who is selecting a target
            target_group: The group of targets to select from
        """
        self.current_character = character
        self.target_group = target_group
        self.active = True
        self.selected_target_index = 0
        
    def stop_targeting(self):
        """Stop the target selection process."""
        self.active = False
        
    def get_selected_target(self):
        """
        Get the currently selected target.
        
        Returns:
            The selected target, or None if no targets
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
    
    def switch_target_group(self):
        """
        Toggle between targeting enemies and allies.
        Only works when target_group is not SELF.
        """
        if self.target_group == self.ENEMIES:
            self.target_group = self.ALLIES
        elif self.target_group == self.ALLIES:
            self.target_group = self.ENEMIES
        
        # Reset the target index when switching groups
        self.selected_target_index = 0
            
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
        if not self.active:
            return
            
        # Get current selected target
        selected_target = self.get_selected_target()
        if not selected_target:
            return
            
        # Only draw when cursor is visible (for blinking effect)
        if self.cursor_visible:
            # Draw selection indicator (triangle pointing at the target)
            # Calculate triangle points relative to the target position
            target_rect = selected_target.rect
            
            # Draw triangle pointing at the target
            triangle_points = [
                (target_rect.centerx, target_rect.top - 10),  # Top point
                (target_rect.centerx - 5, target_rect.top - 5),  # Bottom left
                (target_rect.centerx + 5, target_rect.top - 5)   # Bottom right
            ]
            
            # Choose color based on target type
            if isinstance(selected_target, Player):
                # Green for allies
                indicator_color = GREEN
            else:
                # Yellow for enemies
                indicator_color = YELLOW
                
            # Draw the triangle
            pygame.draw.polygon(screen, indicator_color, triangle_points)
            
        # Highlight the selected target
        border_color = GREEN if isinstance(selected_target, Player) else YELLOW
        pygame.draw.rect(screen, border_color, selected_target.rect, 2)
        
        # Create a small info panel showing target stats
        panel_width = 120
        panel_height = 50
        panel_x = selected_target.rect.right + 5
        panel_y = selected_target.rect.top
        
        # Adjust panel position if it would go off screen
        screen_width, screen_height = screen.get_size()
        if panel_x + panel_width > screen_width:
            panel_x = selected_target.rect.left - panel_width - 5
            
        # Draw panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 200))  # Semi-transparent black
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw target info
        font = pygame.font.SysFont('Arial', 12)
        name_text = font.render(f"{selected_target.name} Lv{selected_target.level}", True, WHITE)
        hp_text = font.render(f"HP: {selected_target.hp}/{selected_target.max_hp}", True, GREEN)
        
        screen.blit(name_text, (panel_x + 5, panel_y + 5))
        screen.blit(hp_text, (panel_x + 5, panel_y + 20))
        
        # Draw targeting instructions
        instr_surface = pygame.Surface((200, 30), pygame.SRCALPHA)
        instr_surface.fill((0, 0, 0, 150))  # Semi-transparent black
        
        instr_font = pygame.font.SysFont('Arial', 14)
        
        if self.target_group == self.ENEMIES:
            instr_text = font.render("Targeting Enemies (TAB to switch)", True, YELLOW)
        elif self.target_group == self.ALLIES:
            instr_text = font.render("Targeting Allies (TAB to switch)", True, GREEN)
        else:
            instr_text = font.render("Select a target", True, WHITE)
            
        instr_x = (screen_width - instr_text.get_width()) // 2
        instr_y = screen_height - 40
        
        # Draw instruction background
        pygame.draw.rect(screen, (0, 0, 0, 150), 
                         (instr_x - 5, instr_y - 5, 
                          instr_text.get_width() + 10, 
                          instr_text.get_height() + 10))
        
        # Draw instruction text
        screen.blit(instr_text, (instr_x, instr_y))