"""Constants for UNO game."""

# Card colors
COLORS = ["red", "yellow", "green", "blue"]
COLOR_CODES = {
    "red": "r",
    "yellow": "y",
    "green": "g",
    "blue": "b",
}

# Card values
NUMBER_CARDS = list(range(10))
ACTION_CARDS = ["skip", "reverse", "+2"]
WILD_CARDS = ["wild", "wild+4"]

# Game settings
INITIAL_HAND_SIZE = 7
NUM_AI_PLAYERS = 3

# UNO header
UNO_HEADER = """
┌───────────────────────────────┐
│           ♠ U N O ♠           │
└───────────────────────────────┘
"""

HEADER_OPTIONS = {
    "header": UNO_HEADER,
    "margin": 1,
}
