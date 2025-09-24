from casino.accounts import Account
from casino.games.blackjack import play_blackjack
from casino.utils import cprint, cinput, clear_screen, display_topbar
from casino.games.slots import play_slots
from casino.utils import cprint, cinput, clear_screen

CASINO_HEADER = """
┌──────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦   │
└──────────────────────────────────────┘
"""

CASINO_HEADER_OPTIONS = {
    "header": CASINO_HEADER,
    "margin": 3,
}

ACCOUNT_STARTING_BALANCE = 100

ENTER_OR_QUIT_PROMPT = "[E]nter   [Q]uit: \n"
INVALID_CHOICE_PROMPT = "\nInvalid input. Please try again. \n\n"
GAME_CHOICE_PROMPT = "Please choose a game to play:\n"

games = ["blackjack", "slots"]


def welcome(account: Account) -> None:
    clear_screen()
    display_topbar(account, **CASINO_HEADER_OPTIONS)
    action = cinput(ENTER_OR_QUIT_PROMPT).lower()

    while action not in {"e", "q"}:
        clear_screen()
        display_topbar(account, **CASINO_HEADER_OPTIONS)
        cprint(INVALID_CHOICE_PROMPT)
        action = cinput(ENTER_OR_QUIT_PROMPT).strip().lower()

    if action == "q":
        clear_screen()
        display_topbar(account, **CASINO_HEADER_OPTIONS)
        cprint("\nGoodbye!")
        return
    elif action == "e":
        clear_screen()
        choose_game(account)


def choose_game(account: Account) -> None:
    game_names = []

    for i, game in enumerate(games):
        game_names.append(f"[{i + 1}] {game.title()}\n")

    display_topbar(account, **CASINO_HEADER_OPTIONS)
    for game_name in game_names:
        cprint(game_name)

    action = cinput(GAME_CHOICE_PROMPT).strip()

    while not action.isdigit() or not (1 <= int(action) <= len(games)):
        clear_screen()

        display_topbar(account, **CASINO_HEADER_OPTIONS)
        for game_name in game_names:
            cprint(game_name)
        cprint(INVALID_CHOICE_PROMPT)

        action = cinput(GAME_CHOICE_PROMPT).strip()

    clear_screen()
    game = games[int(action) - 1]


    match game:
        case "blackjack":
            play_blackjack(account)
        case _:
            print("No such game!")
            welcome(account)

    welcome(account)


def main():
    clear_screen()
    display_topbar(account=None, **CASINO_HEADER_OPTIONS)
    name = cinput("Enter your name: ").strip()
    while not name:
        clear_screen()
        name = cinput("Enter your name: ").strip()
    account = Account.generate(name, ACCOUNT_STARTING_BALANCE)
    welcome(account)


if __name__ == "__main__":
    main()
