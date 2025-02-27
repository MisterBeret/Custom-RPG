"""
Inventory system for the RPG game.
"""
from dataclasses import dataclass

@dataclass
class Item:
    """Class representing a game item."""
    name: str
    description: str
    effect_type: str  # 'healing', 'scan', etc.
    effect_value: int  # Amount healed, etc.

class Inventory:
    """
    Manages the player's inventory of items.
    """
    def __init__(self):
        """Initialize the inventory with default items."""
        self.items = {}
        self.max_quantity = 99  # Maximum amount of each item type
        
        # Add default items
        self.add_item("POTION", 10)
        self.add_item("SCAN LENS", 10)
        
    def add_item(self, item_name, quantity=1):
        """
        Add an item to the inventory.
        
        Args:
            item_name: The name of the item to add
            quantity: The quantity to add (default: 1)
            
        Returns:
            int: The actual amount added (may be less if hitting max limit)
        """
        # Initialize the item if it doesn't exist
        if item_name not in self.items:
            self.items[item_name] = 0
            
        # Calculate how many we can actually add
        current = self.items[item_name]
        space_left = self.max_quantity - current
        amount_to_add = min(quantity, space_left)
        
        # Add the items
        self.items[item_name] += amount_to_add
        
        return amount_to_add
        
    def use_item(self, item_name):
        """
        Use an item from the inventory.
        
        Args:
            item_name: The name of the item to use
            
        Returns:
            bool: True if the item was used, False if not available
        """
        if item_name in self.items and self.items[item_name] > 0:
            self.items[item_name] -= 1
            return True
        return False
        
    def get_quantity(self, item_name):
        """
        Get the quantity of a specific item.
        
        Args:
            item_name: The name of the item to check
            
        Returns:
            int: The quantity of the item, or 0 if not in inventory
        """
        return self.items.get(item_name, 0)
        
    def get_item_names(self):
        """
        Get a list of all item names in the inventory.
        
        Returns:
            list: List of item names with at least one in inventory
        """
        return [name for name, qty in self.items.items() if qty > 0]

# Define item effects
def get_item_effect(item_name):
    """
    Get the effect information for an item.
    
    Args:
        item_name: The name of the item
        
    Returns:
        Item: An Item object with effect information, or None if item not recognized
    """
    if item_name == "POTION":
        return Item(
            name="POTION",
            description="Heals the user's HP by 10",
            effect_type="healing",
            effect_value=10
        )
    elif item_name == "SCAN LENS":
        return Item(
            name="SCAN LENS",
            description="Displays the stats of a target enemy",
            effect_type="scan",
            effect_value=0
        )
    return None