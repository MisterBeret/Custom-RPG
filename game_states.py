"""
Game state management for the RPG game.
"""
from constants import WORLD_MAP, BATTLE, PAUSE, SETTINGS

class GameStateManager:
    """
    Manages transitions between different game states.
    """
    def __init__(self):
        self.current_state = WORLD_MAP
        self.previous_state = WORLD_MAP
        
    def change_state(self, new_state):
        """
        Change to a new game state, storing the previous state.
        
        Args:
            new_state: The new state to transition to.
        """
        self.previous_state = self.current_state
        self.current_state = new_state
        
    def return_to_previous(self):
        """
        Return to the previous game state.
        """
        temp = self.current_state
        self.current_state = self.previous_state
        self.previous_state = temp
        
    @property
    def is_world_map(self):
        """Returns True if current state is the world map."""
        return self.current_state == WORLD_MAP
        
    @property
    def is_battle(self):
        """Returns True if current state is battle."""
        return self.current_state == BATTLE
        
    @property
    def is_pause(self):
        """Returns True if current state is pause menu."""
        return self.current_state == PAUSE
        
    @property
    def is_settings(self):
        """Returns True if current state is settings menu."""
        return self.current_state == SETTINGS