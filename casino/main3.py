from casino.games.blackjack import play_blackjack
from casino.games.slots import play_slots
from casino.utils import cprint, cinput, clear_screen

CASINO_HEADER = """
┌──────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦   │
└──────────────────────────────────────┘
"""

ENTER_OR_QUIT_PROMPT = "[E]nter   [Q]uit: \n"
INVALID_CHOICE_PROMPT = "\nInvalid input. Please try again. \n\n"
GAME_CHOICE_PROMPT = "Please choose a game to play:\n"

games = ["blackjack", "slots"]


def main():
    play_slots()


if __name__ == "__main__":
    main()
