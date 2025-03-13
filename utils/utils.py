"""
Utility functions for the RPG game.
"""

def scale_position(x, y, orig_width, orig_height, current_width, current_height):
    """
    Scale a position from the original resolution to the current resolution.
    
    Args:
        x (int): Original x coordinate
        y (int): Original y coordinate
        orig_width (int): Original screen width
        orig_height (int): Original screen height
        current_width (int): Current screen width
        current_height (int): Current screen height
        
    Returns:
        tuple: Scaled (x, y) coordinates
    """
    scaled_x = int(x * (current_width / orig_width))
    scaled_y = int(y * (current_height / orig_height))
    return scaled_x, scaled_y

def scale_dimensions(width, height, orig_width, orig_height, current_width, current_height):
    """
    Scale dimensions from the original resolution to the current resolution.
    
    Args:
        width (int): Original width
        height (int): Original height
        orig_width (int): Original screen width
        orig_height (int): Original screen height
        current_width (int): Current screen width
        current_height (int): Current screen height
        
    Returns:
        tuple: Scaled (width, height)
    """
    scaled_width = int(width * (current_width / orig_width))
    scaled_height = int(height * (current_height / orig_height))
    return scaled_width, scaled_height

def scale_font_size(size, orig_width, orig_height, current_width, current_height):
    """
    Scale a font size based on the current resolution.
    
    Args:
        size (int): Original font size
        orig_width (int): Original screen width
        orig_height (int): Original screen height
        current_width (int): Current screen width
        current_height (int): Current screen height
        
    Returns:
        int: Scaled font size
    """
    # Use the smaller scaling factor to ensure text remains readable
    scale_x = current_width / orig_width
    scale_y = current_height / orig_height
    scale_factor = min(scale_x, scale_y)
    
    return max(int(size * scale_factor), 10)  # Minimum font size of 10