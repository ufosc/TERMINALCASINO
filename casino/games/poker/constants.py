from casino.cards import StandardDeck

POKER_HEADER = """
┌───────────────────────────────┐
│         ♥ P O K E R ♥         │
└───────────────────────────────┘
"""

HEADER_OPTIONS = {
    "header": POKER_HEADER,
    "margin": 1,
}

SECURITY_GUARD = "👮‍♂️"
SECURITY_MSG = f"""
{SECURITY_GUARD}: Time for you to go.
You have been removed from the casino

"""
YES_OR_NO_PROMPT       = "[Y]es   [N]o"
INVALID_YES_OR_NO_MSG  = "🤵: It's a yes or no, pal. You staying?"
STAY_AT_TABLE_PROMPT   = "🤵: Would you like to stay at the table?"
INVALID_CHOICE_MSG     = "🤵: That's not a choice in this game."
NO_FUNDS_MSG           = "🤵: You don't have enough chips to play. Goodbye."

FULL_DECK: StandardDeck = StandardDeck()

MIN_BALANCE = 20  # minimum chips required to start a round
SMALL_BLIND = 10
BIG_BLIND = 20