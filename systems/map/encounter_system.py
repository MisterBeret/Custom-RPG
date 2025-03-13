"""
Encounter system for the RPG game.
Handles the generation of enemy groups based on encounter pools.
"""
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

@dataclass
class EnemySpec:
    """Specification for a single enemy in an encounter."""
    class_id: str
    level: int

@dataclass
class EncounterDefinition:
    """Definition of a single possible encounter within a pool."""
    weight: int  # Relative probability weight
    enemies: List[EnemySpec]  # List of enemies that appear in this encounter

class EncounterPool:
    """
    Represents a collection of possible encounters with relative weights.
    """
    def __init__(self, pool_id: str, name: str):
        """
        Initialize an encounter pool.
        
        Args:
            pool_id: Unique identifier for this pool
            name: Display name of the pool
        """
        self.pool_id = pool_id
        self.name = name
        self.encounters: List[EncounterDefinition] = []
        self._total_weight = 0
        
    def add_encounter(self, weight: int, enemies: List[EnemySpec]) -> None:
        """
        Add a possible encounter to this pool.
        
        Args:
            weight: Relative probability weight for this encounter
            enemies: List of enemy specifications in this encounter
        """
        self.encounters.append(EncounterDefinition(weight, enemies))
        self._total_weight += weight
        
    def generate_encounter(self) -> Optional[List[EnemySpec]]:
        """
        Generate a random encounter based on the defined weights.
        
        Returns:
            List of enemy specifications, or None if pool is empty
        """
        if not self.encounters:
            return None
            
        # Generate a random number between 0 and total weight
        roll = random.randint(1, self._total_weight)
        
        # Find the selected encounter
        current_weight = 0
        for encounter in self.encounters:
            current_weight += encounter.weight
            if roll <= current_weight:
                return encounter.enemies
                
        # Fallback (shouldn't happen with proper weights)
        return self.encounters[0].enemies


class EncounterManager:
    """
    Manages all encounter pools and their assignment to map areas.
    """
    def __init__(self):
        """Initialize the encounter manager."""
        self.pools: Dict[str, EncounterPool] = {}
        self.map_assignments: Dict[str, str] = {}  # Map ID -> Pool ID
        
    def add_pool(self, pool: EncounterPool) -> None:
        """
        Add an encounter pool to the manager.
        
        Args:
            pool: The encounter pool to add
        """
        self.pools[pool.pool_id] = pool
        
    def assign_pool_to_map(self, map_id: str, pool_id: str) -> bool:
        """
        Assign an encounter pool to a map area.
        
        Args:
            map_id: ID of the map area
            pool_id: ID of the encounter pool
            
        Returns:
            bool: True if assignment was successful
        """
        if pool_id in self.pools:
            self.map_assignments[map_id] = pool_id
            return True
        return False
        
    def get_pool_for_map(self, map_id: str) -> Optional[EncounterPool]:
        """
        Get the encounter pool assigned to a map area.
        
        Args:
            map_id: ID of the map area
            
        Returns:
            The assigned encounter pool, or None if no assignment
        """
        pool_id = self.map_assignments.get(map_id)
        if pool_id:
            return self.pools.get(pool_id)
        return None
        
    def generate_encounter_for_map(self, map_id: str) -> Optional[List[EnemySpec]]:
        """
        Generate a random encounter for a specific map.
        
        Args:
            map_id: ID of the map area
            
        Returns:
            List of enemy specifications, or None if no pool assigned
        """
        pool = self.get_pool_for_map(map_id)
        if pool:
            return pool.generate_encounter()
        return None