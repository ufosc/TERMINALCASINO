import shutil
import sys
import time
from collections.abc import Callable

from casino.types import GameContext
from casino.utils import clear_screen, cinput, cprint, display_topbar
from ..constants import (
    AMERICAN_ROULETTE_TABLE,
    ANSI_RE,
    COLS,
    EUROPEAN_HEADER_OPTIONS,
    EUROPEAN_ROULETTE_TABLE,
    HEADER_OPTIONS,
    ROWS,
)


class RouletteView:
    """Owns the roulette terminal display and player input."""

    def __init__(self, context: GameContext | None = None, european: bool = False) -> None:
        self.context = context
        self.european = european
        self.header_options = EUROPEAN_HEADER_OPTIONS if european else HEADER_OPTIONS
        self.table = EUROPEAN_ROULETTE_TABLE if european else AMERICAN_ROULETTE_TABLE

    def bind(self, context: GameContext) -> None:
        self.context = context

    def display_topbar(self) -> None:
        if self.context is None:
            raise RuntimeError("Roulette view requires a game context.")
        display_topbar(self.context.account, **self.header_options)

    def render_header(self) -> None:
        clear_screen()
        self.display_topbar()

    def clear_and_topbar(self) -> None:
        self.render_header()

    def refresh_topbar(self) -> None:
        options = self.header_options
        header_lines = len(options["header"].strip("\n").splitlines())
        total_lines = header_lines + 1 + options.get("margin", 1)

        sys.stdout.write("\x1b[s")
        sys.stdout.write("\x1b[H")
        for _ in range(total_lines):
            sys.stdout.write("\x1b[2K")
            sys.stdout.write("\x1b[1B")
        sys.stdout.write("\x1b[H")
        self.display_topbar()
        sys.stdout.write("\x1b[u")
        sys.stdout.flush()

    @staticmethod
    def _visible_len(text: str) -> int:
        return len(ANSI_RE.sub("", text))

    @classmethod
    def _center_line(cls, line: str) -> None:
        width = shutil.get_terminal_size().columns
        padding = max(0, (width - cls._visible_len(line)) // 2)
        print((" " * padding) + line)

    def _center_table(self, block: str) -> None:
        lines = block.strip("\n").splitlines()
        max_length = max(self._visible_len(line) for line in lines)
        padding = max(0, (shutil.get_terminal_size().columns - max_length) // 2)
        for line in lines:
            cprint(f"{' ' * padding}{line}")

    def render_wheel(
        self, wheel: list[tuple[str, str, int, int]], highlighted_number: str | None = None
    ) -> None:
        grid = [["  " for _ in range(COLS)] for _ in range(ROWS)]
        for number, color, row, column in wheel:
            displayed_number = number
            if number != "00" and int(number) < 10:
                displayed_number = " " + number
            if highlighted_number is not None and number == highlighted_number:
                grid[row][column - 1] = "*"
                grid[row][column + 1] = "*"
            background = {"black": "40", "red": "41", "green": "42"}[color]
            grid[row][column] = f"\x1b[{background}m\x1b[97m{displayed_number}\x1b[0m"
        for row in grid:
            self._center_line("".join(row))

    def show_result(
        self,
        winning_value: tuple[str, str, int, int],
        bets: dict[str, dict[str, str | int]],
    ) -> None:
        number, color, _, _ = winning_value
        cprint(f"Winning number: {number}")
        cprint(f"Winning color: {color}")
        if self.context is None:
            return
        bet = bets.get(str(self.context.account.aid))
        if bet is None:
            cprint("Your bet: (none)")
        else:
            cprint(f"Your bet: {self.format_bet(bet)}")

    @staticmethod
    def format_bet(bet: dict[str, str | int]) -> str:
        bet_type = str(bet["type"])
        value = str(bet["value"])
        amount = int(bet["amount"])
        if bet_type == "number":
            return f"{amount} on number {value}"
        if bet_type == "color":
            return f"{amount} on {value} (color)"
        if bet_type == "inside_number":
            return f"{amount} on number {value}"
        if bet_type == "outside_color":
            return f"{amount} on {value} (color)"
        if bet_type == "outside_parity":
            return f"{amount} on {value} (parity)"
        if bet_type == "outside_highlow":
            return f"{amount} on {value} (high/low)"
        if bet_type == "outside_dozen":
            label = {"1": "1-12", "2": "13-24", "3": "25-36"}[value]
            return f"{amount} on dozen {value} ({label})"
        if bet_type == "outside_column":
            return f"{amount} on column {value}"
        return f"{amount} on {bet_type}:{value}"

    def announce(self, message: str, pause: float = 0) -> None:
        cprint(message)
        if pause:
            time.sleep(pause)

    def prompt_round_start(self) -> str:
        return cinput("Press [Enter] to start a new round and [q] to quit: ").strip().lower()

    def prompt_play_again(self) -> bool:
        while True:
            answer = cinput("🤵: Would you like to play another round (Y/n): ").strip().lower()
            if answer in {"", "y", "yes"}:
                return True
            if answer in {"n", "no"}:
                return False
            cprint("Please enter 'Yes' or 'No'.")

    def _prompt_with_error(
        self,
        prompt: str,
        validator: Callable[[str], bool],
        error_text: str,
        render_table: bool = False,
        transform: Callable[[str], str] = lambda answer: answer.strip().lower(),
    ) -> str:
        last_error = ""
        while True:
            self.render_header()
            if render_table:
                self._center_table(self.table)
            if last_error:
                cprint(f"🤵: {last_error}")
            answer = transform(cinput(prompt))
            if validator(answer):
                return answer
            last_error = error_text

    def prompt_bet(
        self,
        player_index: int,
        balance: int,
        valid_numbers: list[str],
        outside_bets: bool,
    ) -> tuple[str, str, int] | None:
        player = player_index + 1
        choice = self._prompt_with_error(
            f"🤵: Would you like to bet, Player {player} (y/N): ",
            lambda answer: answer in {"", "y", "yes", "n", "no"},
            "Invalid input. Enter either 'Y' for yes or 'N' for no.",
        )
        if choice in {"", "n", "no"}:
            cprint("User skipped betting. Moving to next user...", end="\n\n")
            return None

        raw_amount = self._prompt_with_error(
            f"Player {player}'s Bet: ",
            lambda answer: answer.isdigit() and 0 < int(answer) <= balance,
            f"Please enter a positive integer up to {balance}.",
            transform=lambda answer: answer.strip(),
        )
        amount = int(raw_amount)
        self.render_header()
        if outside_bets:
            area = self._prompt_with_error(
                "🤵: Choose your bet area: [I]nside (single number) / [O]utside: ",
                lambda answer: answer in {"i", "inside", "o", "outside"},
                "Choose 'I' for inside or 'O' for outside.",
            )
            if area in {"i", "inside"}:
                bet_type = "inside_number"
                value = self._prompt_with_error(
                    "🤵: Enter number you would like to bet on: ",
                    lambda answer: answer in valid_numbers,
                    "Invalid number. Choose from 0-36.",
                    render_table=True,
                    transform=lambda answer: answer.strip(),
                )
            else:
                bet_type = self._prompt_outside_type()
                value = self._prompt_outside_value(bet_type)
            return bet_type, value, amount

        bet_type = self._prompt_with_error(
            "🤵: Would you like to bet on a color or a number? (C or N): ",
            lambda answer: answer in {"c", "color", "n", "number"},
            "Choose either 'color' or 'number'.",
        )
        if bet_type in {"c", "color"}:
            value = self._prompt_with_error(
                "Enter color you want to bet on (red, black, green): ",
                lambda answer: answer in {"red", "black", "green", "r", "b", "g"},
                "Chosen color must be red, black, or green.",
            )
            return "color", {"r": "red", "b": "black", "g": "green"}.get(value, value), amount

        value = self._prompt_with_error(
            "Enter number you would like to bet on: ",
            lambda answer: answer in valid_numbers,
            "Choose a valid number from the table.",
            render_table=True,
            transform=lambda answer: answer.strip(),
        )
        return "number", value, amount

    def _prompt_outside_type(self) -> str:
        mapping = {
            "1": "outside_color",
            "2": "outside_parity",
            "3": "outside_highlow",
            "4": "outside_dozen",
            "5": "outside_column",
        }
        options = [
            "Outside bets:",
            "[1] Red / Black",
            "[2] Odd / Even",
            "[3] High / Low",
            "[4] Dozen",
            "[5] Column",
        ]
        content_width = max(map(len, options))
        box_width = content_width + 4
        self.render_header()
        cprint("┌" + "─" * box_width + "┐")
        for index, option in enumerate(options):
            cprint("│" + option.center(box_width) + "│" if index == 0 else
                   "│  " + option.ljust(content_width) + "  │")
        cprint("└" + "─" * box_width + "┘")
        while True:
            choice = cinput("🤵: Choose option (1-5): ").strip()
            if choice in mapping:
                return mapping[choice]
            cprint("Choose a number from 1 to 5.")

    def _prompt_outside_value(self, bet_type: str) -> str:
        prompts = {
            "outside_color": (
                "🤵: Choose color [R]ed / [B]lack: ",
                {"r": "red", "red": "red", "b": "black", "black": "black"},
                "Choose red or black.",
                False,
            ),
            "outside_parity": (
                "🤵: Choose [O]dd / [E]ven: ",
                {"o": "odd", "odd": "odd", "e": "even", "even": "even"},
                "Choose odd or even.",
                False,
            ),
            "outside_highlow": (
                "🤵: Choose [L]ow (1-18) / [H]igh (19-36): ",
                {"l": "low", "low": "low", "h": "high", "high": "high"},
                "Choose low or high.",
                True,
            ),
            "outside_column": (
                "🤵: Choose column: [1]=1st [2]=2nd [3]=3rd: ",
                {"1": "1", "2": "2", "3": "3"},
                "Choose 1, 2, or 3.",
                True,
            ),
            "outside_dozen": (
                "🤵: Choose dozen: [1]=1-12 [2]=13-24 [3]=25-36: ",
                {"1": "1", "2": "2", "3": "3"},
                "Choose 1, 2, or 3.",
                True,
            ),
        }
        prompt, values, error, show_table = prompts[bet_type]
        answer = self._prompt_with_error(
            prompt,
            lambda answer: answer in values,
            error,
            render_table=show_table,
        )
        return values[answer]
