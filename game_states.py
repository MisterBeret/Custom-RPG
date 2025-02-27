"""
Game state management for the RPG game.
"""
from constants import WORLD_MAP, BATTLE, PAUSE, SETTINGS, INVENTORY

class GameStateManager:
    """
    Manages transitions between different game states.
    """
    def __init__(self):
        self.current_state = WORLD_MAP
        self.previous_state = WORLD_MAP
        self.state_stack = [WORLD_MAP]  # Stack for tracking state navigation
        
    def change_state(self, new_state):
        """
        Change to a new game state, storing the previous state.
        
        Args:
            new_state: The new state to transition to.
        """
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Push new state onto stack
        self.state_stack.append(new_state)
        
    def return_to_previous(self):
        """
        Return to the previous game state using the state stack.
        """
        # Pop current state
        if len(self.state_stack) > 1:
            self.state_stack.pop()
            # Set current state to what's now on top of stack
            self.current_state = self.state_stack[-1]
            
            # Update previous state reference
            if len(self.state_stack) > 1:
                self.previous_state = self.state_stack[-2]
            else:
                self.previous_state = self.current_state
        
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
        
    @property
    def is_inventory(self):
        """Returns True if current state is inventory menu."""
        return self.current_state == INVENTORY