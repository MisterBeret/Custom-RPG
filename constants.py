"""
Constants used throughout the RPG game.
"""

# Original design resolution
ORIGINAL_WIDTH = 800
ORIGINAL_HEIGHT = 600

# Screen dimensions (default)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Screen resolution options
RESOLUTION_800x600 = "800x600"
RESOLUTION_1024x768 = "1024x768"
RESOLUTION_1280x720 = "1280x720"
RESOLUTION_1920x1080 = "1920x1080"
RESOLUTION_2560x1440 = "2560x1440"

RESOLUTION_OPTIONS = [
    RESOLUTION_800x600,
    RESOLUTION_1024x768, 
    RESOLUTION_1280x720,
    RESOLUTION_1920x1080,
    RESOLUTION_2560x1440
]

# Display mode options
DISPLAY_WINDOWED = "Windowed"
DISPLAY_BORDERLESS = "Borderless"
DISPLAY_FULLSCREEN = "Fullscreen"

DISPLAY_MODE_OPTIONS = [
    DISPLAY_WINDOWED,
    DISPLAY_BORDERLESS,
    DISPLAY_FULLSCREEN
]

# Default settings
DEFAULT_RESOLUTION = RESOLUTION_800x600
DEFAULT_DISPLAY_MODE = DISPLAY_WINDOWED

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (120, 120, 120)  # Darker gray for depleted HP & SP bars
ORANGE = (230, 120, 0)  # Deeper orange for HP bars
YELLOW = (255, 255, 0)  # For highlighting special items/options
BLUE = (30, 144, 255)   # Bright blue for SP bars
DARK_BLUE = (25, 25, 112) 
PURPLE = (128, 0, 128)  # For magic-related UI elements

# Game states
WORLD_MAP = 0
BATTLE = 1
PAUSE = 2
SETTINGS = 3
INVENTORY = 4
DIALOGUE = 5
PARTY_MANAGEMENT = 6

# Text speed options
TEXT_SPEED_SLOW = "Slow"
TEXT_SPEED_MEDIUM = "Medium"
TEXT_SPEED_FAST = "Fast"

# Animation durations (in frames)
ATTACK_ANIMATION_DURATION = 20
FLEE_ANIMATION_DURATION = 40
ACTION_DELAY_DURATION = 30  # Delay between turns (0.5 seconds at 60fps)
SPELL_ANIMATION_DURATION = 30  # Duration for spell casting animations

# Menu options
PAUSE_OPTIONS = ["ITEMS", "SETTINGS", "CLOSE"] 
SETTINGS_OPTIONS = ["TEXT SPEED", "RESOLUTION", "DISPLAY MODE", "BACK"]
BATTLE_OPTIONS = [
    "MOVE", "ATTACK", "DEFEND", "ITEM",     # Left column
    "SKILL", "MAGIC", "ULTIMATE", "STATUS"  # Right column
]

# Message log size
MAX_LOG_SIZE = 3  # Number of messages to keep in the battle log