"""
Data for all character classes
"""
from systems.class_system import CharacterClass

#------------------------------------------------------------------------------------------------------------------------------------

"""
Human Classes
"""
# Commoner (starting class)
commoner = CharacterClass(
    class_id="commoner",
    name="Commoner",
    category="Human",
    base_stats={
        "hp": 20,           # Low stats, 20 across the board
        "sp": 20,           
        "attack": 20,       
        "defense": 20,      
        "intelligence": 20, 
        "resilience": 20,   
        "acc": 20,          
        "spd": 20           
    },
    learnable_abilities=[
        (1, "ATTACK", "skill"),
        (1, "DEFEND", "skill"),
    ]
)

# Example: Warrior class
warrior = CharacterClass(
    class_id="warrior",
    name="Warrior",
    category="Human",
    base_stats={
        "hp": 80,           # High HP
        "sp": 30,           # Low SP
        "attack": 75,       # High Attack
        "defense": 65,      # Good Defense
        "intelligence": 25, # Low Intelligence
        "resilience": 45,   # Average Resilience
        "acc": 60,          # Average Accuracy
        "spd": 40           # Below average Speed
    },
    learnable_abilities=[
        (1, "ATTACK", "skill"),
        (1, "DEFEND", "skill"),
        (3, "POWER_SLASH", "skill"),
        (7, "COUNTER", "passive"),
        (10, "INTIMIDATE", "skill"),
        (15, "BLITZ_BURST", "ultimate")
    ]
)

# Example: Mage class
mage = CharacterClass(
    class_id="mage",
    name="Mage",
    category="Human",
    base_stats={
        "hp": 50,           # Low HP
        "sp": 85,           # High SP
        "attack": 30,       # Low Attack
        "defense": 35,      # Low Defense
        "intelligence": 80, # High Intelligence
        "resilience": 70,   # Good Resilience
        "acc": 65,          # Good Accuracy
        "spd": 45           # Average Speed
    },
    learnable_abilities=[
        (1, "ATTACK", "skill"),
        (1, "DEFEND", "skill"),
        (1, "FIRE", "spell"),
        (3, "HEAL", "spell"),
        (6, "ICE", "spell"),
        (10, "ANALYZE", "skill"),
        (12, "MANA_SHIELD", "passive"),
        (15, "METEOR", "ultimate")
    ]
)

# Example: Wolf monster class
wolf = CharacterClass(
    class_id="wolf",
    name="Wolf",
    category="Monster",
    base_stats={
        "hp": 60,           # Average HP
        "sp": 20,           # Low SP
        "attack": 65,       # Good Attack
        "defense": 40,      # Below average Defense
        "intelligence": 15, # Very low Intelligence
        "resilience": 20,   # Low Resilience
        "acc": 55,          # Average Accuracy
        "spd": 75           # High Speed
    },
    learnable_abilities=[
        (1, "ATTACK", "skill"),
        (3, "GROWL", "skill"),
        (5, "PACK_TACTICS", "passive"),
        (8, "HOWL", "skill")
    ]
)

#------------------------------------------------------------------------------------------------------------------------------------

"""
Monster Classes
"""
# Rat 
rat = CharacterClass(
    class_id="rat",
    name="Rat",
    category="Monster",
    base_stats={
        "hp": 10,
        "sp": 10,
        "attack": 10,
        "defense": 10,
        "intelligence": 10,
        "resilience": 10,
        "acc": 20,
        "spd": 30
    },
    learnable_abilities=[
        (1, "ATTACK", "skill"),
        (2, "NIBBLE", "skill"),        # Small damage but high accuracy
        (4, "SKITTER", "passive"),     # Chance to dodge attacks
        (7, "DISEASE_BITE", "skill")   # Potential status effect in the future
    ]
)

# Snake 
snake = CharacterClass(
    class_id="snake",
    name="Snake",
    category="Monster",
    base_stats={
        "hp": 10,
        "sp": 10,
        "attack": 10,
        "defense": 10,
        "intelligence": 10,
        "resilience": 10,
        "acc": 30,
        "spd": 20
    },
    learnable_abilities=[
        (1, "ATTACK", "skill"),
        (1, "VENOM", "passive"),       # Chance to poison on hit (for future implementation)
        (3, "CONSTRICT", "skill"),     # Reduces target's speed
        (8, "STRIKE", "skill")         # Higher damage but needs to charge up
    ]
)

# Slime 
slime = CharacterClass(
    class_id="slime",
    name="Slime",
    category="Monster",
    base_stats={
        "hp": 10,
        "sp": 10,
        "attack": 10,
        "defense": 10,
        "intelligence": 10,
        "resilience": 20,
        "acc": 10,
        "spd": 5
    },
    learnable_abilities=[
        (1, "ATTACK", "skill"),
        (4, "SPLIT", "passive"),       # Chance to survive a fatal blow with 1 HP
        (6, "ENGULF", "skill"),        # Moderate damage plus defense reduction
        (9, "ACID_SPRAY", "skill"),    # AoE damage when implemented
        (10, "ABSORB", "skill")        # Small HP recovery
    ]
)

# Turtle
turtle = CharacterClass(
    class_id="turtle",
    name="Turtle",
    category="Monster",
    base_stats={
        "hp": 20,
        "sp": 10,
        "attack": 10,
        "defense": 20,
        "intelligence": 10,
        "resilience": 5,
        "acc": 10,
        "spd": 5
    },
    learnable_abilities=[
        (1, "ATTACK", "skill"),
        (1, "DEFEND", "skill"),        # Turtles start with defend ability
        (3, "SHELL_PROTECTION", "passive"), # Reduces physical damage
        (6, "SNAP", "skill"),          # Higher damage but lower accuracy
        (9, "WITHDRAW", "skill")       # Greatly increases defense for one turn
    ]
)

# Hermit Crab
hermit_crab = CharacterClass(
    class_id="hermit_crab",
    name="Hermit Crab",
    category="Monster",
    base_stats={
        "hp": 10,
        "sp": 10,
        "attack": 10,
        "defense": 20,
        "intelligence": 10,
        "resilience": 10,
        "acc": 10,
        "spd": 10
    },
    learnable_abilities=[
        (1, "ATTACK", "skill"),
        (2, "PINCH", "skill"),         # Low damage but reduces target's attack
        (4, "SHELL_SWITCH", "skill"),  # Trades attack and defense values for 3 turns
        (7, "SCAVENGE", "passive"),    # Chance to heal when attacking
        (10, "BUBBLE_BLAST", "skill")  # Water-based attack (for future elemental system)
    ]
)