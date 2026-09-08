SLOTS_HEADER = """
┌───────────────────────────────┐
│         ♠ S L O T S ♠         │
└───────────────────────────────┘
"""

HEADER_OPTIONS = {
    "header": SLOTS_HEADER,
    "margin": 1,
}

BET_PROMPT_SINGLE = "How much would you like to bet?"
BET_PROMPT_LINES = "How much would you like to bet on each row? (top,mid,bottom) e.g. 10,15,20"
INVALID_BET_MSG_SINGLE = "That's not a valid bet."
INVALID_BET_MSG_LINES = "That's not a valid bet. Example: 10,15,20"
INVALID_INPUT_MSG = "Invalid input. Please try again."
NO_FUNDS_MSG = "You don't have enough money to make a bet.\n\n"

SEC_BTWN_SPIN = 0.1
TOTAL_SPINS = 10
PAYLINES = 3

# Base game (StandardSlots) odds. The expanded variant instead pays out
# per matching payline, so it doesn't use these.
WIN_PROBABILITY = 0.2
HIGH_VALUE_PROBABILITY = 0.05

LOW_ITEMS = ["A", "B", "C"]
HIGH_ITEMS = ["D"]
ALL_ITEMS = LOW_ITEMS + HIGH_ITEMS


def generate_payout_legend(low_items: list[str], high_items: list[str]) -> str:
    """Generate payout legend."""
    low_items_str = " | ".join(low_items)
    high_items_str = " | ".join(high_items)
    max_len = max(len(low_items_str), len(high_items_str))
    low_str = f"Matching {low_items_str.ljust(max_len)}  | x1.5"
    high_str = f"Matching {high_items_str.ljust(max_len)}  | x5.0"
    return f"{low_str}\n{high_str}"


PAYOUT_LEGEND = generate_payout_legend(LOW_ITEMS, HIGH_ITEMS)
