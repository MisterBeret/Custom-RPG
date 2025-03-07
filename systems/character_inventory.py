"""
Individual character inventory and party storage system for the RPG game.
"""
from systems.inventory import Inventory, Item, get_item_effect

class CharacterInventory(Inventory):
    """
    Extends the base Inventory class with additional functionality for character-specific inventories.
    """
    def __init__(self, owner_name="Unknown"):
        """
        Initialize a character inventory.
        
        Args:
            owner_name: Name of the character who owns this inventory
        """
        super().__init__()
        self.owner_name = owner_name
        
    def transfer_to(self, target_inventory, item_name, quantity=1):
        """
        Transfer items from this inventory to another inventory.
        
        Args:
            target_inventory: The inventory to transfer items to
            item_name: The name of the item to transfer
            quantity: The quantity to transfer
            
        Returns:
            int: The actual amount transferred
        """
        # Calculate how many we can transfer
        available = self.get_quantity(item_name)
        amount_to_transfer = min(quantity, available)
        
        if amount_to_transfer <= 0:
            return 0
            
        # Remove from this inventory
        self.items[item_name] -= amount_to_transfer
        if self.items[item_name] <= 0:
            del self.items[item_name]
            
        # Add to target inventory
        actual_added = target_inventory.add_item(item_name, amount_to_transfer)
        
        # If target inventory couldn't accept all items, return the remainder
        if actual_added < amount_to_transfer:
            remainder = amount_to_transfer - actual_added
            self.add_item(item_name, remainder)
            
        return actual_added

class PartyStorage(Inventory):
    """
    Shared storage inventory for the entire party.
    Items here are not available during battle but can be transferred to characters.
    """
    def __init__(self):
        """Initialize the party storage."""
        super().__init__()
        # Higher capacity for storage
        self.max_quantity = 99
        
    def transfer_to_character(self, character_inventory, item_name, quantity=1):
        """
        Transfer items from storage to a character's inventory.
        
        Args:
            character_inventory: The character's inventory
            item_name: The name of the item to transfer
            quantity: The quantity to transfer
            
        Returns:
            int: The actual amount transferred
        """
        # Calculate how many we can transfer
        available = self.get_quantity(item_name)
        amount_to_transfer = min(quantity, available)
        
        if amount_to_transfer <= 0:
            return 0
            
        # Remove from storage
        self.items[item_name] -= amount_to_transfer
        if self.items[item_name] <= 0:
            del self.items[item_name]
            
        # Add to character inventory
        actual_added = character_inventory.add_item(item_name, amount_to_transfer)
        
        # If character inventory couldn't accept all items, return the remainder to storage
        if actual_added < amount_to_transfer:
            remainder = amount_to_transfer - actual_added
            self.add_item(item_name, remainder)
            
        return actual_added