"""
Dialogue system for the RPG game.
"""
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, BLACK, WHITE
from utils import scale_position, scale_dimensions, scale_font_size

class DialogueSystem:
    """
    Manages dialogue between characters, NPCs, or with the environment.
    """
    def __init__(self):
        """Initialize the dialogue system."""
        self.active = False
        self.current_dialogue = []
        self.current_dialogue_index = 0
        self.displayed_text = ""
        self.text_index = 0
        self.text_speed = 2  # Characters per frame
        self.text_timer = 0
        
    def start_dialogue(self, dialogue_list):
        """
        Start a new dialogue sequence.
        
        Args:
            dialogue_list: List of dialogue strings to display in sequence
        """
        if dialogue_list and len(dialogue_list) > 0:
            self.active = True
            self.current_dialogue = dialogue_list
            self.current_dialogue_index = 0
            initial_chars = min(10, len(self.current_dialogue[0]))  # Show at least a few characters
            self.displayed_text = self.current_dialogue[0][:initial_chars]
            self.text_index = initial_chars
            self.text_timer = 0
    
    def advance_dialogue(self):
        """
        Advance to the next dialogue box or end the dialogue if at the end.
        
        Returns:
            bool: True if dialogue is still active, False if it ended
        """
        # If text is still being revealed, show it all immediately
        if self.text_index < len(self.current_dialogue[self.current_dialogue_index]):
            self.displayed_text = self.current_dialogue[self.current_dialogue_index]
            self.text_index = len(self.displayed_text)
            return True
        
        # Otherwise, advance to next dialogue
        self.current_dialogue_index += 1
        
        # Check if we've reached the end of the dialogue
        if self.current_dialogue_index >= len(self.current_dialogue):
            self.active = False
            return False
        
        # Start displaying the next dialogue
        self.displayed_text = ""
        self.text_index = 0
        
        # Skip any empty dialogue entries
        while (self.current_dialogue_index < len(self.current_dialogue) and 
            not self.current_dialogue[self.current_dialogue_index].strip()):
            self.current_dialogue_index += 1
            if self.current_dialogue_index >= len(self.current_dialogue):
                self.active = False
                return False
        
        return True
    
    def update(self):
        """Update dialogue animation."""
        if not self.active:
            return
            
        # Only update text if we haven't displayed the full message yet
        if self.text_index < len(self.current_dialogue[self.current_dialogue_index]):
            self.text_timer += 1
            
            # Add characters at the rate determined by text_speed
            while self.text_timer >= 1 and self.text_index < len(self.current_dialogue[self.current_dialogue_index]):
                self.text_timer -= 1
                self.displayed_text += self.current_dialogue[self.current_dialogue_index][self.text_index]
                self.text_index += 1
    
    def draw(self, screen):
        """
        Draw the dialogue box and text.
        
        Args:
            screen: The pygame surface to draw on
        """
        if not self.active:
            return
            
        # Get current screen dimensions
        current_width, current_height = screen.get_size()
        
        # Scale dialogue box dimensions and position
        box_width = int(current_width * 0.8)
        box_height = int(current_height * 0.2)
        box_x = (current_width - box_width) // 2
        box_y = current_height - box_height - int(20 * (current_height / ORIGINAL_HEIGHT))
        
        # Scale font size
        font_size = scale_font_size(24, ORIGINAL_WIDTH, ORIGINAL_HEIGHT, current_width, current_height)
        font = pygame.font.SysFont('Arial', font_size)
        
        # Draw dialogue box background
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height))
        border_width = max(1, int(2 * (current_width / ORIGINAL_WIDTH)))
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), border_width)
        
        # Calculate text rendering position and maximum width
        text_x = box_x + int(20 * (current_width / ORIGINAL_WIDTH))
        text_y = box_y + int(15 * (current_height / ORIGINAL_HEIGHT))
        max_width = box_width - int(40 * (current_width / ORIGINAL_WIDTH))
        
        # Split text into lines to fit in the box (simple word wrapping)
        words = self.displayed_text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            # Check if adding this word would exceed the max width
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                # Add the current line to lines and start a new line
                lines.append(current_line)
                current_line = word + " "
        
        # Add the last line
        if current_line:
            lines.append(current_line)
        
        # Draw each line of text
        line_height = int(font_size * 1.2)
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, WHITE)
            screen.blit(text_surface, (text_x, text_y + i * line_height))
        
        # Draw indicator that there's more dialogue (when text is fully displayed)
        if self.text_index >= len(self.current_dialogue[self.current_dialogue_index]):
            indicator_x = box_x + box_width - int(30 * (current_width / ORIGINAL_WIDTH))
            indicator_y = box_y + box_height - int(30 * (current_height / ORIGINAL_HEIGHT))
            indicator_text = font.render("▼", True, WHITE)
            screen.blit(indicator_text, (indicator_x, indicator_y))
    
    def set_text_speed(self, text_speed_setting):
        """
        Set the text speed based on the given setting.
        
        Args:
            text_speed_setting: The text speed setting ("SLOW", "MEDIUM", or "FAST")
        """
        if text_speed_setting == "SLOW":
            self.text_speed = 1
        elif text_speed_setting == "MEDIUM":
            self.text_speed = 2
        else:  # FAST
            self.text_speed = 4