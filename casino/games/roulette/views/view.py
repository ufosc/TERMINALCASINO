import shutil
import sys
import time
from typing import Callable

from casino.types import GameContext
from casino.utils import cinput, cprint, clear_screen, display_topbar

from ..constants import (
    ANSI_RE,
    EUROPEAN_HEADER_OPTIONS,
    HEADER_OPTIONS,
    ROULETTE_TABLE,
    COLS,
    ROWS,
    SEC_BTWN_SPIN,
)


class RouletteView:
    """Owns roulette rendering and terminal input."""

    def __init__(self, context: GameContext | None = None, european: bool = False) -> None:
        self.context = context
        self.header_options = EUROPEAN_HEADER_OPTIONS if european else HEADER_OPTIONS

    def display_topbar(self, context: GameContext | None = None) -> None:
        context = context or self.context
        if context is None:
            raise ValueError("A game context is required to display the roulette topbar.")
        display_topbar(context.account, **self.header_options)

    def render_header(self, context: GameContext | None = None) -> None:
        clear_screen()
        self.display_topbar(context)

    def refresh_topbar(self, context: GameContext | None = None) -> None:
        context = context or self.context
        if context is None:
            raise ValueError("A game context is required to refresh the roulette topbar.")
        header = self.header_options["header"]
        total_lines = len(header.strip("\n").splitlines()) + 1 + self.header_options.get("margin", 1)
        sys.stdout.write("\x1b[s")
        sys.stdout.write("\x1b[H")
        for _ in range(total_lines):
            sys.stdout.write("\x1b[2K")
            sys.stdout.write("\x1b[1B")
        sys.stdout.write("\x1b[H")
        self.display_topbar(context)
        sys.stdout.write("\x1b[u")
        sys.stdout.flush()

    def prompt(self, context: GameContext, prompt: str, validator: Callable[[str], bool],
               error_text: str, render_table: bool = False,
               transform: Callable[[str], str] = lambda s: s.strip().lower()) -> str:
        last_error = ""
        while True:
            self.render_header(context)
            if render_table:
                self.print_table()
            if last_error:
                cprint(f"🤵: {last_error}")
            answer = transform(cinput(prompt))
            if validator(answer):
                return answer
            last_error = error_text

    def print_table(self) -> None:
        lines = ROULETTE_TABLE.strip("\n").splitlines()
        width = shutil.get_terminal_size().columns
        max_len = max(len(ANSI_RE.sub("", line)) for line in lines)
        padding = max(0, (width - max_len) // 2)
        for line in lines:
            cprint(" " * padding + line)

    def print_wheel(self, wheel: list[tuple[str, str, int, int]],
                    highlighted_num: str | None = None) -> None:
        grid = [[" " for _ in range(COLS)] for _ in range(ROWS)]
        for number, color, row, col in wheel:
            display_number = f" {number}" if number != "00" and int(number) < 10 else number
            if highlighted_num is not None and number == highlighted_num.strip():
                grid[row][col - 1], grid[row][col + 1] = "*", "*"
            background = {"black": "40", "red": "41", "green": "42"}[color]
            grid[row][col] = f"\x1b[{background}m\x1b[97m{display_number}\x1b[0m"
        for line in ("".join(row) for row in grid):
            self.print_centered(line)

    def wheel_animation(self, context: GameContext,
                        wheel: list[tuple[str, str, int, int]],
                        sequence: list[str], seconds: float = SEC_BTWN_SPIN) -> None:
        for number in sequence:
            clear_screen()
            self.display_topbar(context)
            self.print_wheel(wheel, number)
            time.sleep(seconds)

    def render_outside_bets_menu(self, context: GameContext) -> None:
        self.render_header(context)
        options = ["[1] Red / Black", "[2] Odd / Even", "[3] High / Low", "[4] Dozen", "[5] Column"]
        title = "Outside bets:"
        width = max(len(title), *(len(option) for option in options)) + 4
        cprint("┌" + "─" * width + "┐")
        cprint("│" + title.center(width) + "│")
        cprint("│" + " " * width + "│")
        for option in options:
            cprint("│  " + option.ljust(width - 4) + "  │")
        cprint("└" + "─" * width + "┘")

    @staticmethod
    def visible_len(value: str) -> int:
        return len(ANSI_RE.sub("", value))

    def print_centered(self, line: str) -> None:
        width = shutil.get_terminal_size().columns
        print(" " * max(0, (width - self.visible_len(line)) // 2) + line)
