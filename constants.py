"""
Constants used throughout the RPG game.
"""

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
ORANGE = (255, 165, 0)  # Added orange color for HP bars

# Game states
WORLD_MAP = 0
BATTLE = 1
PAUSE = 2
SETTINGS = 3

# Text speed options
TEXT_SPEED_SLOW = "SLOW"
TEXT_SPEED_MEDIUM = "MEDIUM"
TEXT_SPEED_FAST = "FAST"

# Animation durations (in frames)
ATTACK_ANIMATION_DURATION = 20
FLEE_ANIMATION_DURATION = 40
ACTION_DELAY_DURATION = 30  # Delay between turns (0.5 seconds at 60fps)

# Menu options
PAUSE_OPTIONS = ["SETTINGS", "CLOSE"]
SETTINGS_OPTIONS = ["TEXT SPEED", "BACK"]
BATTLE_OPTIONS = ["ATTACK", "DEFEND", "RUN"]

# Message log size
MAX_LOG_SIZE = 3  # Number of messages to keep in the battle log