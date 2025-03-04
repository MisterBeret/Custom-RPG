"""
Data for all character classes
"""
from systems.class_system import CharacterClass

# Commoner (starting class)
commoner = CharacterClass(
    class_id="commoner",
    name="Commoner",
    category="Human",
    base_stats={
        "hp": 20,            # Low stats, 20 across the board
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
        "hp": 80,         # High HP
        "sp": 30,         # Low SP
        "attack": 75,     # High Attack
        "defense": 65,    # Good Defense
        "intelligence": 25, # Low Intelligence
        "resilience": 45,  # Average Resilience
        "acc": 60,        # Average Accuracy
        "spd": 40         # Below average Speed
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
        "hp": 50,         # Low HP
        "sp": 85,         # High SP
        "attack": 30,     # Low Attack
        "defense": 35,    # Low Defense
        "intelligence": 80, # High Intelligence
        "resilience": 70,  # Good Resilience
        "acc": 65,        # Good Accuracy
        "spd": 45         # Average Speed
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
        "hp": 60,         # Average HP
        "sp": 20,         # Low SP
        "attack": 65,     # Good Attack
        "defense": 40,    # Below average Defense
        "intelligence": 15, # Very low Intelligence
        "resilience": 20,  # Low Resilience
        "acc": 55,        # Average Accuracy
        "spd": 75         # High Speed
    },
    learnable_abilities=[
        (1, "ATTACK", "skill"),
        (3, "GROWL", "skill"),
        (5, "PACK_TACTICS", "passive"),
        (8, "HOWL", "skill")
    ]
)