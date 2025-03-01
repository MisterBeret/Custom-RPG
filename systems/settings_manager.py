"""
Settings manager for the RPG game.
"""
import os
import json
from constants import (
    TEXT_SPEED_FAST, DEFAULT_RESOLUTION, DEFAULT_DISPLAY_MODE,
    RESOLUTION_OPTIONS, DISPLAY_MODE_OPTIONS
)

class SettingsManager:
    """
    Manages game settings and persistence.
    """
    def __init__(self):
        """Initialize the settings manager with default values."""
        self.settings_file = "game_settings.json"
        self.settings = {
            "text_speed": TEXT_SPEED_FAST,
            "resolution": DEFAULT_RESOLUTION,
            "display_mode": DEFAULT_DISPLAY_MODE
        }
        
        # Load settings if file exists
        self.load_settings()
        
    def load_settings(self):
        """Load settings from file if it exists."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    self.settings.update(loaded_settings)
                    
                    # Validate settings
                    self._validate_settings()
            except (json.JSONDecodeError, IOError):
                # If file is corrupted or can't be read, use defaults
                print("Error loading settings file. Using defaults.")
                
    def save_settings(self):
        """Save current settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except IOError:
            print("Error saving settings file.")
    
    def _validate_settings(self):
        """Ensure settings are valid, reset to defaults if not."""
        # Validate resolution
        if self.settings["resolution"] not in RESOLUTION_OPTIONS:
            self.settings["resolution"] = DEFAULT_RESOLUTION
            
        # Validate display mode
        if self.settings["display_mode"] not in DISPLAY_MODE_OPTIONS:
            self.settings["display_mode"] = DEFAULT_DISPLAY_MODE
    
    def get_resolution(self):
        """
        Get the current resolution setting.
        
        Returns:
            tuple: (width, height) in pixels
        """
        resolution_str = self.settings["resolution"]
        width, height = map(int, resolution_str.split('x'))
        return width, height
    
    def set_resolution(self, resolution_str):
        """
        Set the resolution.
        
        Args:
            resolution_str: String in format "WIDTHxHEIGHT" (e.g., "800x600")
            
        Returns:
            bool: True if setting was changed, False if invalid
        """
        if resolution_str in RESOLUTION_OPTIONS:
            self.settings["resolution"] = resolution_str
            self.save_settings()
            return True
        return False
    
    def get_display_mode(self):
        """
        Get the current display mode.
        
        Returns:
            str: Display mode setting
        """
        return self.settings["display_mode"]
    
    def set_display_mode(self, mode):
        """
        Set the display mode.
        
        Args:
            mode: Display mode (WINDOWED, BORDERLESS, FULLSCREEN)
            
        Returns:
            bool: True if setting was changed, False if invalid
        """
        if mode in DISPLAY_MODE_OPTIONS:
            self.settings["display_mode"] = mode
            self.save_settings()
            return True
        return False
    
    def get_text_speed(self):
        """
        Get the current text speed setting.
        
        Returns:
            str: Text speed setting
        """
        return self.settings["text_speed"]
    
    def set_text_speed(self, speed):
        """
        Set the text speed.
        
        Args:
            speed: Text speed setting
            
        Returns:
            bool: True if setting was changed
        """
        self.settings["text_speed"] = speed
        self.save_settings()
        return True