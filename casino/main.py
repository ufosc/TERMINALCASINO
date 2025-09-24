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

CASINO_HEADER_OPTIONS = {
    "header": CASINO_HEADER,
    "margin": 3,
}
ACCOUNT_STARTING_BALANCE = 100

ENTER_OR_QUIT_PROMPT = "[E]nter   [Q]uit: "
INVALID_CHOICE_PROMPT = "\nInvalid input. Please try again.\n"
GAME_CHOICE_PROMPT = "Please choose a game to play: "

# To add a new game, just add a handler function to GAME_HANDLERS
GAME_HANDLERS: dict[str, Callable[[Account], None]] = {
    "blackjack": play_blackjack,
}
games = list(GAME_HANDLERS.keys())


def term_width() -> int:
    """Safe terminal width fallback."""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def prompt_with_refresh(
    render_fn: Callable[[], None],
    prompt: str,
    error_message: str,
    validator: Callable[[str], bool],
    transform: Callable[[str], str] = lambda s: s.strip(),
) -> str:
    """
    Repeatedly render screen, show last error (if any), ask for input and validate.
    On EOF/KeyboardInterrupt return 'q' so caller can decide how to exit.
    """
    last_error = ""
    while True:
        render_fn()
        if last_error:
            cprint(last_error)
        answer = transform(cinput(prompt).strip())
        if validator(answer):
            return answer
        last_error = error_message



def main_menu(account: Account) -> None:
    """
    Main loop: show welcome, then (if chosen) show game menu, call handler,
    then return to top-level menu. No recursion used.
    """
    while True:
        def render_welcome():
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("")  # spacing

        action = prompt_with_refresh(
            render_fn = render_welcome,
            prompt = ENTER_OR_QUIT_PROMPT.center(term_width()),
            error_message = INVALID_CHOICE_PROMPT,
            validator = lambda x: x.lower() in {"e", "q"},
            transform = lambda s: s.strip().lower(),
        )

        if action == "q":
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("\nGoodbye!\n")
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
            render_fn = render_choose_game,
            prompt = GAME_CHOICE_PROMPT.center(term_width()),
            error_message = INVALID_CHOICE_PROMPT,
            validator = lambda x: x.isdigit() and 1 <= int(x) <= len(games),
        )

        selected_game = games[int(choice) - 1]
        handler = GAME_HANDLERS.get(selected_game)
        if handler:
            clear_screen()
            handler(account)  # returns to loop after game finishes
        else:
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("\nNo such game!\n")


def main():
    clear_screen()
    display_topbar(account=None, **CASINO_HEADER_OPTIONS)

    name = cinput("Enter your name: ").strip()
    while not name:
        clear_screen()
        display_topbar(account=None, **CASINO_HEADER_OPTIONS)
        cprint("\nInvalid input. Please enter a valid name.\n")
        name = cinput("Enter your name: ").strip()


    account = Account.generate(name, ACCOUNT_STARTING_BALANCE)
    main_menu(account)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        clear_screen()
        display_topbar(account=None, **CASINO_HEADER_OPTIONS)
        cprint("\nGoodbye! (Interrupted)\n")

