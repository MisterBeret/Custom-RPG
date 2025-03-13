"""
Ultimate system for the RPG game.
Ultimates are powerful special abilities that can only be used once per rest.
"""
from dataclasses import dataclass

@dataclass
class Ultimate:
    """Class representing an ultimate ability."""
    name: str
    description: str
    available: bool  # Whether the ultimate can currently be used
    effect_type: str  # 'damage', 'healing', 'aoe', etc.
    power_multiplier: float  # Multiplier for damage/healing effects
    accuracy_bonus: float  # Bonus to hit chance (1.0 = 100% accuracy)

class UltimateSet:
    """
    Manages the player's ultimate abilities.
    """
    def __init__(self):
        """Initialize the ultimates with default abilities."""
        self.ultimates = {}
        
        # Add default ultimates
        self.add_ultimate("BLITZ BURST")
        
    def add_ultimate(self, ultimate_name):
        """
        Add an ultimate to the player's set.
        
        Args:
            ultimate_name: The name of the ultimate to add
            
        Returns:
            bool: True if ultimate was added, False if already known
        """
        # Don't add if already known
        if ultimate_name in self.ultimates:
            return False
            
        # Add the ultimate
        ultimate = get_ultimate_data(ultimate_name)
        if ultimate:
            self.ultimates[ultimate_name] = ultimate
            return True
        
        return False
        
    def get_ultimate(self, ultimate_name):
        """
        Get an ultimate from the set.
        
        Args:
            ultimate_name: The name of the ultimate to retrieve
            
        Returns:
            Ultimate: The ultimate object, or None if not in set
        """
        return self.ultimates.get(ultimate_name)
        
    def get_ultimate_names(self):
        """
        Get a list of all ultimate names in the set.
        
        Returns:
            list: List of ultimate names known by the player
        """
        return list(self.ultimates.keys())
        
    def rest(self):
        """
        Reset all ultimates to be available again after resting.
        """
        for name, ultimate in self.ultimates.items():
            ultimate.available = True

# Define ultimate data
def get_ultimate_data(ultimate_name):
    """
    Get the data for a specific ultimate.
    
    Args:
        ultimate_name: The name of the ultimate
        
    Returns:
        Ultimate: An Ultimate object with the ability data, or None if not recognized
    """
    if ultimate_name == "BLITZ BURST":
        return Ultimate(
            name="BLITZ BURST",
            description="Unleashes a devastating attack with 5x damage that cannot miss",
            available=True,
            effect_type="damage",
            power_multiplier=5.0,
            accuracy_bonus=1.0  # Always hits
        )
    # Add more ultimates here as needed
    return None