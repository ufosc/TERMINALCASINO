BLACKJACK_HEADER = """
┌───────────────────────────────┐
│     ♠ B L A C K J A C K ♠     │
└───────────────────────────────┘
"""

BLACKJACK_HEADER_OPTIONS = {
    "header": BLACKJACK_HEADER,
    "margin": 1,
}

SECURITY_GUARD = "👮‍♂️"
SECURITY_MSG = f"""
{SECURITY_GUARD}: Time for you to go.
You have been removed from the casino

"""
YES_OR_NO_PROMPT       = "[Y]es   [N]o"
DECK_NUMBER_SELECTION  = "🤵: How many decks would you like to play with?"
DECK_NUMBER_BOUNDS_MSG = "🤵: That won't work, please be serious. Try again."
INVALID_NUMBER_MSG     = "🤵: Invalid number. Try again."
INVALID_YES_OR_NO      = "🤵: It's a yes or no, pal. You staying?"
STAY_AT_TABLE_PROMPT   = "🤵: Would you like to stay at the table?"
INVALID_CHOICE_MSG     = "🤵: That's not a choice in this game."
BET_PROMPT             = "🤵: How much would you like to bet?"
INVALID_BET_MSG        = "🤵: That's not a valid bet."
NO_FUNDS_MSG           = "🤵: You don't have enough chips to play. Goodbye."

# Pay n times the amount of original player bet
BLACKJACK_MULTIPLIER = 1.5