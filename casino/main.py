import shutil
from typing import Callable

from casino.accounts import Account
from casino.games.blackjack import play_blackjack
from casino.utils import cprint, cinput, clear_screen, display_topbar

CASINO_HEADER = """
┌──────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦   │
└──────────────────────────────────────┘
"""

CASINO_HEADER_OPTIONS = {"header": CASINO_HEADER, "margin": 3}
ACCOUNT_STARTING_BALANCE = 100

ENTER_OR_QUIT_PROMPT = "[E]nter   [Q]uit: "
INVALID_CHOICE_PROMPT = "\nInvalid input. Please try again. \n\n"
GAME_CHOICE_PROMPT = "Please choose a game to play: "

games = ["blackjack"]
GAME_HANDLERS = {"blackjack": play_blackjack}


def term_width() -> int:
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def prompt_with_refresh(
    render_fn: Callable[[], None],
    prompt: str,
    validator: Callable[[str], bool],
    error_message: str,
    transform: Callable[[str], str] = lambda s: s,
) -> str:
    """
    Repeatedly render screen, ask for input, validate. On invalid input,
    re-render and show error message.
    """
    while True:
        render_fn()
        answer = transform(cinput(prompt))
        if validator(answer):
            return answer
        render_fn()
        cprint(error_message)


def main_menu(account: Account) -> None:
    """
    Main loop: show welcome, then (if chosen) show game menu, call handler,
    then return to top-level menu. No recursion used.
    """
    while True:
        def render_welcome():
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("")  # blank line for spacing

        action = prompt_with_refresh(
            render_welcome,
            ENTER_OR_QUIT_PROMPT.center(term_width()),
            lambda x: x in {"e", "q"},
            INVALID_CHOICE_PROMPT,
            transform=lambda s: s.strip().lower(),
        )

        if action == "q":
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("\nGoodbye!")
            break  # exit loop -> program ends

        # --- choose game ---
        def render_choose_game():
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("")  # spacing
            width = term_width()
            for i, name in enumerate(games, start=1):
                cprint(f"[{i}] {name.title()}".center(width) + "\n")

        choice = prompt_with_refresh(
            render_choose_game,
            GAME_CHOICE_PROMPT.center(term_width()),
            lambda x: x.isdigit() and 1 <= int(x) <= len(games),
            INVALID_CHOICE_PROMPT,
            transform=lambda s: s.strip(),
        )

        selected_game = games[int(choice) - 1]
        handler = GAME_HANDLERS.get(selected_game)
        if handler:
            clear_screen()
            handler(account)  # returns to loop after game finishes
        else:
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("\nNo such game!")


def main():
    clear_screen()
    display_topbar(account=None, **CASINO_HEADER_OPTIONS)
    name = cinput("Enter your name: ").strip()
    while not name:
        clear_screen()
        display_topbar(account=None, **CASINO_HEADER_OPTIONS)
        name = cinput("Enter your name: ").strip()
    account = Account.generate(name, ACCOUNT_STARTING_BALANCE)
    main_menu(account)


if __name__ == "__main__":
    main()
