"""
Party system for the RPG game.
"""
from typing import List, Optional
from entities.player import Player
from systems.character.character_inventory import PartyStorage

class Party:
    """
    Manages a group of player-controlled characters.
    """
    def __init__(self, max_active_members=4):
        """
        Initialize the party.
        
        Args:
            max_active_members: Maximum number of characters in the active party
        """
        self.max_active_members = max_active_members  # Limit active members to 4
        self.active_members = []   # Characters in the active party (in battle)
        self.reserve_members = []  # Characters in reserve
        self.leader = None         # The party leader (character shown on map)
        self.storage = PartyStorage()  # Shared storage inventory
    
    def add_member(self, character, active=True):
        """
        Add a character to the party.
        
        Args:
            character: The character to add
            active: Whether to add to active party (True) or reserve (False)
            
        Returns:
            bool: True if character was added, False if party is full
        """
        if active:
            if len(self.active_members) < self.max_active_members:
                self.active_members.append(character)
                # If this is the first active member, make them the leader
                if len(self.active_members) == 1:
                    self.leader = character
                return True
            return False
        else:
            self.reserve_members.append(character)
            return True
    
    def remove_member(self, character):
        """
        Remove a character from the party.
        
        Args:
            character: The character to remove
            
        Returns:
            bool: True if character was removed, False if not found
        """
        # Check active members first
        if character in self.active_members:
            self.active_members.remove(character)
            
            # If we removed the leader, assign a new one if possible
            if character == self.leader and self.active_members:
                self.leader = self.active_members[0]
            elif not self.active_members:
                self.leader = None
                
            return True
            
        # Check reserve members
        if character in self.reserve_members:
            self.reserve_members.remove(character)
            return True
            
        return False
    
    def switch_active(self, active_index, reserve_index):
        """
        Switch a character from active to reserve and vice versa.
        
        Args:
            active_index: Index of the active character to switch
            reserve_index: Index of the reserve character to switch
            
        Returns:
            bool: True if switch was successful
        """
        if (0 <= active_index < len(self.active_members) and 
            0 <= reserve_index < len(self.reserve_members)):
            
            active_char = self.active_members[active_index]
            reserve_char = self.reserve_members[reserve_index]
            
            # Swap the characters
            self.active_members[active_index] = reserve_char
            self.reserve_members[reserve_index] = active_char
            
            # Update leader if necessary
            if active_char == self.leader:
                self.leader = reserve_char
                
            return True
        return False
    
    def set_leader(self, index):
        """
        Set the party leader from an active member.
        
        Args:
            index: Index of the active character to make leader
            
        Returns:
            bool: True if leader was set, False if index invalid
        """
        if 0 <= index < len(self.active_members):
            self.leader = self.active_members[index]
            return True
        return False
    
    def get_all_members(self):
        """
        Get all party members (active and reserve).
        
        Returns:
            list: All party members
        """
        return self.active_members + self.reserve_members
    
    def get_active_members(self):
        """
        Get only active party members.
        
        Returns:
            list: Active party members
        """
        return self.active_members.copy()
    
    def get_reserve_members(self):
        """
        Get only reserve party members.
        
        Returns:
            list: Reserve party members
        """
        return self.reserve_members.copy()