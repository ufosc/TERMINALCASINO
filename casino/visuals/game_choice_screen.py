import shutil
import sys
from typing import Callable

from ..types import GameContext
from ..utils import cprint, cinput, clear_screen, display_topbar


# dynamically spacing UI
def term_width() -> int:
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


# dynamically spacing typed input (this can also be moved to utils)
def move_cursor(row: int, col: int) -> None:
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()


def prompt_with_refresh(
    render_fn: Callable[[], None], #draws the screen
    prompt: str, #asks for input
    error_message: str,
    validator: Callable[[str], bool], #validates the input
    transform: Callable[[str], str] = lambda s: s.strip(),
) -> str:

    last_error = ""
    while True:
        render_fn() #redrawing the screen each loop
        if last_error:
            cprint(last_error)
        try:
            answer = transform(cinput(prompt).strip())
        except (EOFError, KeyboardInterrupt):
            return "q"
        if validator(answer):
            return answer
        last_error = error_message


def choose_game_screen(
    ctx: GameContext,
    game_names: list[str],
    header_options: dict,
) -> int | None:


    account = ctx.account

    def render_choose_game():  # just draws the screen
        clear_screen()
        display_topbar(account, **header_options)
        cprint("")  # spacing

        width = term_width()
        box_inner_width = 30

        TL, TR, BL, BR = "♦", "♣", "♠", "♥"
        top_border = f"┌{TL}{'─' * (box_inner_width - 2)}{TR}┐"
        bottom_border = f"└{BL}{'─' * (box_inner_width - 2)}{BR}┘"

        cprint(top_border.center(width))
        cprint(("│" + " " * box_inner_width + "│").center(width))

        for i, name in enumerate(game_names, start=1):
            label = f"[{i}] {name.title()}"
            line = label[:box_inner_width].ljust(box_inner_width)
            cprint((f"│{line}│").center(width))

        cprint(("│" + " " * box_inner_width + "│").center(width))

        cprint(bottom_border.center(width))

        cprint("")  # spacing
        cprint("Enter a number to play, or press Q to go back.".center(width))


    def prompt_game_choice_dynamic() -> str:
        """
        Draws the screen, prints a centered prompt, then places the cursor at a
        fixed column so user input grows to the right (input won't drift off-center).
        """
        render_choose_game()

        width = term_width()
        prompt_text = "Select a game to play:"

        # prints the centered prompt line
        cprint(prompt_text.center(width))

        # prints a blank line where the user will type
        cprint(" " * width)

        # moves cursor up one line to the blank line, then chooses a fixed start column
        # slightly left of center so it looks centered
        start_col = max(1, (width // 2) - 6)

        # moves up one line
        sys.stdout.write("\033[1A")
        # moves to absolute column start_col (ANSI 'G' sets column)
        sys.stdout.write(f"\033[{start_col}G")
        sys.stdout.flush()

        try:
            return cinput("").strip()
        except (EOFError, KeyboardInterrupt):
            return "q"

        # looping until valid input

    last_error = ""
    while True:
        if last_error:
            # shows the error above the prompt on next redraw
            render_choose_game()
            cprint(last_error)

        raw = prompt_game_choice_dynamic().strip().lower()

        if raw == "q":
            choice = "q"
            break

        if raw.isdigit() and 1 <= int(raw) <= len(game_names):
            choice = raw
            break

        last_error = "\nInvalid input. Please try again.\n"

    if choice == "q":
        return None

    return int(choice) - 1