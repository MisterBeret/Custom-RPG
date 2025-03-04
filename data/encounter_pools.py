"""
Predefined encounter pools for the RPG game.
"""
from systems.encounter_system import EncounterPool, EnemySpec, EncounterManager

def initialize_encounter_pools():
    """
    Initialize all predefined encounter pools.
    
    Returns:
        EncounterManager: The initialized encounter manager
    """
    manager = EncounterManager()
    
    # Create the test pool
    test_pool = EncounterPool("test_pool", "Test Encounters")
    
    # 30%: 1 LV1 Slime, 1 LV1 Rat
    test_pool.add_encounter(30, [
        EnemySpec("slime", 1),
        EnemySpec("rat", 1)
    ])
    
    # 30%: 1 LV1 Hermit Crab, 1 LV1 Rat
    test_pool.add_encounter(30, [
        EnemySpec("hermit_crab", 1),
        EnemySpec("rat", 1)
    ])
    
    # 30%: 1 LV1 Turtle, 1 LV1 Rat
    test_pool.add_encounter(30, [
        EnemySpec("turtle", 1),
        EnemySpec("rat", 1)
    ])
    
    # 5%: 2 LV1 Rats, 1 LV2 Rat
    test_pool.add_encounter(5, [
        EnemySpec("rat", 1),
        EnemySpec("rat", 1),
        EnemySpec("rat", 2)
    ])
    
    # 5%: 1 LV1 Slime, 1 LV1 Turtle, 1 LV1 Hermit Crab, 1 LV2 Rat
    test_pool.add_encounter(5, [
        EnemySpec("slime", 1),
        EnemySpec("turtle", 1),
        EnemySpec("hermit_crab", 1),
        EnemySpec("rat", 2)
    ])
    
    # Add the pool to the manager
    manager.add_pool(test_pool)
    
    # Create a second pool as an example - rat infested area
    rat_pool = EncounterPool("rat_pool", "Rat Infestation")
    
    # 60%: 1-2 LV1 Rats
    rat_pool.add_encounter(30, [EnemySpec("rat", 1)])
    rat_pool.add_encounter(30, [EnemySpec("rat", 1), EnemySpec("rat", 1)])
    
    # 30%: 2-3 LV1 Rats
    rat_pool.add_encounter(20, [EnemySpec("rat", 1), EnemySpec("rat", 1), EnemySpec("rat", 1)])
    rat_pool.add_encounter(10, [EnemySpec("rat", 1), EnemySpec("rat", 1), EnemySpec("rat", 1)])
    
    # 10%: 1-2 LV2 Rats
    rat_pool.add_encounter(7, [EnemySpec("rat", 2)])
    rat_pool.add_encounter(3, [EnemySpec("rat", 2), EnemySpec("rat", 2)])
    
    # Add the pool to the manager
    manager.add_pool(rat_pool)
    
    # Assign pools to maps (examples)
    manager.assign_pool_to_map("center", "test_pool")
    manager.assign_pool_to_map("east", "rat_pool")
    manager.assign_pool_to_map("west", "test_pool")
    
    return manager