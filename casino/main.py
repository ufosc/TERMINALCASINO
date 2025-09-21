from casino.games.blackjack import play_blackjack
from casino.games.poker import play_poker
from casino.utils import cprint, cinput, clear_screen

CASINO_HEADER = """
┌──────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦   │
└──────────────────────────────────────┘



"""

ENTER_OR_QUIT_PROMPT = "[E]nter   [Q]uit: \n"
INVALID_CHOICE_PROMPT = "\nInvalid input. Please try again. \n\n"
GAME_CHOICE_PROMPT = "Please choose a game to play:\n"

games = ["blackjack", "poker"]


def welcome():
    clear_screen()
    cprint(CASINO_HEADER)
    action = cinput(ENTER_OR_QUIT_PROMPT).lower()

    while action not in {"e", "q"}:
        clear_screen()
        cprint(CASINO_HEADER)
        cprint(INVALID_CHOICE_PROMPT)
        action = cinput(ENTER_OR_QUIT_PROMPT).strip().lower()

    if action == "q":
        clear_screen()
        cprint(CASINO_HEADER)
        cprint("\nGoodbye!")
        return
    elif action == "e":
        clear_screen()
        choose_game()


def choose_game():
    game_names = []

    for i, game in enumerate(games):
        game_names.append(f"[{i + 1}] {game.title()}\n")

    cprint(CASINO_HEADER)
    for game_name in game_names:
        cprint(game_name)

    action = cinput(GAME_CHOICE_PROMPT).strip()

    while not action.isdigit() or not (1 <= int(action) <= len(games)):
        clear_screen()

        cprint(CASINO_HEADER)
        for game_name in game_names:
            cprint(game_name)
        cprint(INVALID_CHOICE_PROMPT)

        action = cinput(GAME_CHOICE_PROMPT).strip()

    clear_screen()
    game = games[int(action) - 1]

    func = f"play_{game}"

    if func in globals():
        globals()[func]()
    else:
        print("No such game!")

    welcome()


def main():
    welcome()


if __name__ == "__main__":
    main()
