"""
Battle turn order system for multiple characters.
"""
import random
from entities.player import Player

class TurnOrder:
    """
    Manages battle turn order for all combatants.
    """
    def __init__(self, party_members, enemies):
        """
        Initialize the turn order system.
        
        Args:
            party_members: List of active party members
            enemies: List of enemies in battle
        """
        self.combatants = party_members + enemies
        self.turn_queue = []
        self.current_turn_index = 0
        
        # Generate initial turn order
        self.generate_turn_order()
        
    def generate_turn_order(self):
        """
        Generate the turn order based on SPD and additional factors.
        """
        # Copy list to avoid modifying the original
        combatants = self.combatants.copy()
        
        # Filter out defeated entities
        combatants = [c for c in combatants if not c.is_defeated()]
        
        # Sort by speed in descending order (faster goes first)
        combatants.sort(key=lambda c: c.spd, reverse=True)
        
        # Resolve ties using additional factors
        # Group combatants by speed
        speed_groups = {}
        for c in combatants:
            if c.spd not in speed_groups:
                speed_groups[c.spd] = []
            speed_groups[c.spd].append(c)
        
        # Sort each group by level (higher level goes first)
        for spd, group in speed_groups.items():
            if len(group) > 1:
                # First sort by level
                group.sort(key=lambda c: c.level, reverse=True)
                
                # For same level, use RNG to break ties
                current_level = None
                level_group = []
                
                for i, c in enumerate(list(group)):
                    if current_level != c.level:
                        # Randomize the previous level group
                        if level_group:
                            random.shuffle(level_group)
                            # Replace the original entries with randomized ones
                            for j, entity in enumerate(level_group):
                                group[i - len(level_group) + j] = entity
                            level_group = []
                        current_level = c.level
                    
                    level_group.append(c)
                
                # Don't forget to randomize the last group
                if level_group:
                    random.shuffle(level_group)
                    for j, entity in enumerate(level_group):
                        group[len(group) - len(level_group) + j] = entity
        
        # Flatten the sorted groups back into a list
        self.turn_queue = []
        for spd in sorted(speed_groups.keys(), reverse=True):
            self.turn_queue.extend(speed_groups[spd])
        
        # Reset turn index
        self.current_turn_index = 0
        
    def get_current(self):
        """
        Get the combatant whose turn it is.
        
        Returns:
            The current combatant or None if queue is empty
        """
        if not self.turn_queue:
            return None
        return self.turn_queue[self.current_turn_index]
    
    def advance(self):
        """
        Advance to the next turn.
        
        Returns:
            The new current combatant or None if queue is empty
        """
        if not self.turn_queue:
            return None
            
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_queue)
        
        # Skip defeated combatants
        while self.current_turn_index < len(self.turn_queue) and self.turn_queue[self.current_turn_index].is_defeated():
            self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_queue)
            
            # Avoid infinite loop if all combatants are defeated
            if self.current_turn_index == 0:
                # Regenerate the turn queue to remove defeated entities
                self.generate_turn_order()
                if not self.turn_queue:
                    return None
                
        return self.get_current()
    
    def remove_combatant(self, combatant):
        """
        Remove a combatant from the turn order (e.g., when defeated).
        
        Args:
            combatant: The combatant to remove
        """
        if combatant in self.turn_queue:
            index = self.turn_queue.index(combatant)
            self.turn_queue.remove(combatant)
            
            # Adjust current index if needed
            if index < self.current_turn_index:
                self.current_turn_index -= 1
            elif index == self.current_turn_index:
                # If we removed the current combatant, 
                # current_turn_index now points to the next one
                if self.current_turn_index >= len(self.turn_queue):
                    self.current_turn_index = 0
                    
        # Also remove from the combatants list
        if combatant in self.combatants:
            self.combatants.remove(combatant)
    
    def is_player_turn(self):
        """
        Check if it's a player character's turn.
        
        Returns:
            bool: True if it's a player's turn, False if enemy
        """
        current = self.get_current()
        if current:
            return isinstance(current, Player)
        return False
        
    def any_enemies_alive(self):
        """
        Check if any enemies are still alive in the turn queue.
        
        Returns:
            bool: True if at least one enemy is alive
        """
        from entities.enemy import Enemy
        return any(isinstance(c, Enemy) and not c.is_defeated() for c in self.turn_queue)
        
    def any_players_alive(self):
        """
        Check if any player characters are still alive in the turn queue.
        
        Returns:
            bool: True if at least one player is alive
        """
        return any(isinstance(c, Player) and not c.is_defeated() for c in self.turn_queue)