"""
Systems package initialization.
"""
# Make inventory classes available at package level
from .inventory import Inventory, Item, get_item_effect

# Make spell system classes available at package level
from .spell_system import SpellBook, Spell, get_spell_data

# Make map system classes available at package level
from .map_system import MapSystem, MapArea