import random
from typing import List, Optional
from time import sleep
import time
import sys
import shutil
import re
import casino.utils as utils

from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar
from casino.accounts import Account

ROULETTE_HEADER = """
┌────────────────────────────────────────────────┐
│     ♠ E U R O P E A N    R O U L E T T E ♠     │
└────────────────────────────────────────────────┘
"""

HEADER_OPTIONS = {
    "header": ROULETTE_HEADER,
    "margin": 1,
}

STANDARD_EUROPEAN_ROULETTE_WHEEL = [
    ('0', 'green', 0, 14),
    ('32', 'red', 0, 17),
    ('15', 'black', 0, 20),
    ('19', 'red', 1, 24),
    ('4', 'black', 2, 27),
    ('21', 'red', 3, 28),
    ('2', 'black', 4, 30),
    ('25', 'red', 5, 30),
    ('17', 'black', 6, 31),
    ('34', 'red', 7, 31),
    ('6', 'black', 8, 31),
    ('27', 'red', 9, 31),
    ('13', 'black', 10, 31),
    ('36', 'red', 11, 30),
    ('11', 'black', 12, 30),
    ('30', 'red', 13, 28),
    ('8', 'black', 14, 26),
    ('23', 'red', 15, 24),
    ('10', 'black', 16, 19),
    ('5', 'red', 16, 16),
    ('24', 'black', 16, 13),
    ('16', 'red', 15, 8),
    ('33', 'black', 14, 6),
    ('1', 'red', 13, 4),
    ('20', 'black', 12, 2),
    ('14', 'red', 11, 2),
    ('31', 'black', 10, 1),
    ('9', 'red', 9, 1),
    ('22', 'black', 8, 1),
    ('18', 'red', 7, 1),
    ('29', 'black', 6, 1),
    ('7', 'red', 5, 2),
    ('28', 'black', 4, 2),
    ('12', 'red', 3, 4),
    ('35', 'black', 2, 5),
    ('3', 'red', 1, 8),
    ('26', 'black', 0, 11)
]

ROULETTE_TABLE = """
      ┌───────────────────────────────────────────────────────────┐
      │         [L]ow = 1-18        │        [H]igh = 19-36       │
┌─────────────────────────────────────────────────────────────────┐───────────┐ C
│     │  3 │  6 │  9 │ 12 │ 15 │ 18 │ 21 │ 24 │ 27 │ 30 │ 33 │ 36 │ [3] = 3rd │ O
│     │────│────│────│────│────│────│────│────│────│────│────│────│───────────│ L
│  0  │  2 │  5 │  8 │ 11 │ 14 │ 17 │ 20 │ 23 │ 26 │ 29 │ 32 │ 35 │ [2] = 2nd │ U
│     │────│────│────│────│────│────│────│────│────│────│────│────│───────────│ M
│     │  1 │  4 │  7 │ 10 │ 13 │ 16 │ 19 │ 22 │ 25 │ 28 │ 31 │ 34 │ [1] = 1st │ N
└─────────────────────────────────────────────────────────────────┘───────────┘ S
      │     [1] = 1-12    │    [2] = 13-24    │    [3] = 25-36    │
      └───────────────────────────────────────────────────────────┘
                          D   O   Z   E   N   S                   
"""

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

DOZENS = {
    "1": set(range(1, 13)),
    "2": set(range(13, 25)),
    "3": set(range(25, 37)),
}

COLUMNS = {
    "1": set(range(1, 37, 3)),  # 1,4,7,...,34
    "2": set(range(2, 37, 3)),  # 2,5,8,...,35
    "3": set(range(3, 37, 3)),  # 3,6,9,...,36
}

MULTIPLIER_LOSS = 1          # no payout
MULTIPLIER_EVEN_MONEY = 2    # 1:1 payout
MULTIPLIER_TWO_TO_ONE = 3    # 2:1 payout
MULTIPLIER_STRAIGHT_UP = 36  # 35:1 payout

TOTAL_ROTATIONS = 2
SEC_BTWN_SPIN = 0.04

ROWS, COLS = 17, 33
ROULETTE_GRID = [['  ' for _ in range(COLS)] for _ in range(ROWS)]

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def display_roulette_topbar(ctx: GameContext) -> None:
    display_topbar(ctx.account, **HEADER_OPTIONS)


def refresh_roulette_topbar(ctx: GameContext) -> None:
    # Number of lines occupied by the topbar: header (3 lines) + user/balance line + margin
    header_lines = len(ROULETTE_HEADER.strip("\n").splitlines())
    margin = HEADER_OPTIONS.get("margin", 1)
    total_lines = header_lines + 1 + margin

    sys.stdout.write("\x1b[s")  # Save current cursor position
    sys.stdout.write("\x1b[H")  # Move cursor to top-left corner

    # Clear all topbar lines
    for _ in range(total_lines):
        sys.stdout.write("\x1b[2K")  # clear line
        sys.stdout.write("\x1b[1B")  # down 1 line

    # Move back to top-left and redraw the topbar
    sys.stdout.write("\x1b[H")
    display_roulette_topbar(ctx)

    # Restore cursor position so the rest of the screen stays intact
    sys.stdout.write("\x1b[u")
    sys.stdout.flush()


def _visible_len(s: str) -> int:
    return len(ANSI_RE.sub("", s))


def cprint_ansi_center(line: str, end: str = "\n") -> None:
    """Center a string that may contain ANSI escape codes."""
    width = shutil.get_terminal_size().columns
    vis = _visible_len(line)
    pad_left = max(0, (width - vis) // 2)
    print((" " * pad_left) + line, end=end)


def cprint_table_center(block: str) -> None:
    lines = block.strip("\n").splitlines()
    term_width = shutil.get_terminal_size().columns

    max_len = max(_visible_len(line) for line in lines)
    pad_left = max(0, (term_width - max_len) // 2)

    for line in lines:
        padded_line = " " * pad_left + line
        print(f"{utils.theme['color']}{padded_line}{utils.theme['reset']}")


def render_outside_bets_menu(ctx: GameContext) -> None:
    render_header(ctx)
    title = "Outside bets:"
    options = [
        "[1] Red / Black",
        "[2] Odd / Even",
        "[3] High / Low",
        "[4] Dozen",
        "[5] Column",
    ]

    content_width = max(len(title), *(len(o) for o in options))
    left_pad = 2
    right_pad = 2
    box_width = content_width + left_pad + right_pad

    cprint("┌" + "─" * box_width + "┐")
    cprint("│" + title.center(box_width) + "│")
    cprint("│" + " " * box_width + "│")

    for opt in options:
        line = " " * left_pad + opt.ljust(content_width) + " " * right_pad
        cprint("│" + line + "│")

    cprint("└" + "─" * box_width + "┘")


def render_header(ctx: GameContext) -> None:
    clear_screen()
    display_roulette_topbar(ctx)


def render_cell(num_str: str, color: str) -> str:
    bg = {"black": "40",
          "red": "41",
          "green": "42"}
    return f"\x1b[{bg[color]}m\x1b[97m{num_str}\x1b[0m"


def prompt_with_error(ctx: GameContext, prompt: str, validator, error_text: str, render_table: bool = False,
                      transform=lambda s: s.strip().lower(),):
    last_error = ""
    while True:
        render_header(ctx)
        if render_table:
            cprint_table_center(ROULETTE_TABLE)
        if last_error:
            cprint(f"🤵: {last_error}")

        answer = transform(cinput(prompt))
        if validator(answer):
            return answer
        last_error = error_text


class Roulette:
    """
    Abstract base class to play roulette.

    Only contains base functions to run roulette.

    Attributes:
        wheel (list[tuple[str, str]]): The roulette wheel, where each entry is
            a tuple like ("0", "green").
        accounts (list[Account]): List of all player accounts.
        bets (dict[str, dict[str, str, int]]): Maps each account UUID to a bet record.

        Each key is a unique account UUID, and each value is a dictionary with the fields:
            {
                "type": bet_type,
                "value": bet_value,
                "amount": bet_amount
            }

        Example:
            {
                "uuid_1": {"type": "color", "value": "red", "amount": 100},
                "uuid_2": {"type": "number", "value": "0", "amount": 50}
            }
    """

    def __init__(self, accounts: List[Account]) -> None:
        """
        Initializes roulette
        """
        # Will be populated with numbers and colors
        self.wheel = list[tuple[str, str, int, int]]()

        # Colors on wheel. Includes initials
        self.valid_colors = ["red", "black", "r", "b"]
        self.valid_numbers = []

        self.accounts = accounts

        # Current round's bets
        self.bets = {}
        self.winning_value: Optional[tuple[str, str]] = None

    def print_wheel(self, highlighted_num=None) -> None:
        # clear current grid
        for row in range(ROWS):
            for col in range(COLS):
                ROULETTE_GRID[row][col] = ' '  # each empty spot is 2 spaces

        for (num_str, color, row, col) in self.wheel:
            if int(num_str.strip()) < 10:
                num_str = " " + num_str
            if highlighted_num is not None and num_str.strip() == highlighted_num.strip():
                # the spot in the column before and column after the number become *'s
                ROULETTE_GRID[row][col - 1] = "*"
                ROULETTE_GRID[row][col + 1] = "*"
            ROULETTE_GRID[row][col] = render_cell(num_str, color)

        wheel_lines = ["".join(row) for row in ROULETTE_GRID]
        # Center the wheel in the terminal
        for line in wheel_lines:
            cprint_ansi_center(line)

    def wheel_animation(self, ctx: GameContext, sequence, sec_btwn_spins: float = SEC_BTWN_SPIN) -> None:
        clear_screen()
        display_roulette_topbar(ctx)

        # Show each number multiple times to reduce strobing
        frames_per_number = 7
        frame_delay = sec_btwn_spins / frames_per_number

        for num in sequence:
            for _ in range(frames_per_number):
                sys.stdout.write("\x1b[6;1H")
                self.print_wheel(highlighted_num=num)
                sys.stdout.flush()
                time.sleep(frame_delay)

    def spin_wheel(self, ctx: GameContext) -> tuple[str, str, int, int]:
        """
        Pick a winning color and number.

        Returns:
            tuple[str, str]: A tuple containing:
                - str: The winning number (e.g., "28", "5", "0")
                - str: The winning color (either "red", "green" or "black")
        """

        # cprint("Spinning wheel...")

        random_index = random.randint(0, len(self.wheel) - 1)
        self.winning_value = self.wheel[random_index]

        wheel_sequence = [num for num, _, _, _ in self.wheel]

        # do TOTAL_ROTATIONS number of rotations before landing on number
        sequence = (wheel_sequence * TOTAL_ROTATIONS) + wheel_sequence[:random_index + 1]
        self.wheel_animation(ctx, sequence)

        winning_number = self.winning_value[0]
        winning_color = self.winning_value[1]

        cprint(f"Winning number: {winning_number}")
        cprint(f"Winning color: {winning_color}")

        account_id = str(ctx.account.aid)
        bet = self.bets.get(account_id)
        if bet is None:
            cprint("Your bet: (none)")
        else:
            cprint(f"Your bet: {self._format_bet(bet)}")

        return self.winning_value

    def reset_round(self) -> None:
        self.bets.clear()
        self.winning_value = None

    def submit_bets(self, ctx: GameContext) -> None | str:
        """
        Instruct users to submit bets.

        This function will ask users if they would like to submit a bet
        on a color or a number.

        - If users pick color, they can pick either red or black
        - If users pick number, they can pick a number to bet on.
        """

        # Loop over all users
        player_index = 0
        while player_index < len(self.accounts):
            if self._all_players_bankrupt():
                cprint("🤵: All players have gone bankrupt. "
                       "You cannot play any more roulette.")
                sleep(3)
                return "BANKRUPT"

            if self.accounts[player_index].balance == 0:
                cprint(f"Skipping player {player_index + 1} because of empty balance...")
                player_index += 1
                continue

            will_bet = prompt_with_error(
                ctx=ctx,
                prompt=f"🤵: Would you like to bet, Player {player_index + 1} (y/N): ",
                validator=lambda a: a in {"", "y", "yes", "n", "no"},
                error_text="Invalid input. Enter either 'Y' for yes or 'N' for no.",
                render_table=False,
                transform=lambda s: s.strip().lower(),
            )

            if will_bet in {"", "n", "no"}:
                cprint("User skipped betting. Moving to next user...", end="\n\n")
                player_index += 1
                continue
            else:
                pass

            bet_amount = self._prompt_bet_amount(ctx, player_index)

            # Ask for desired bet type
            area = self._prompt_bet_area(ctx)

            clear_screen()
            display_roulette_topbar(ctx)

            # Color or number betting
            if area == "inside":
                bet_type = "inside_number"
                bet_value = self._prompt_inside_number(ctx)
            else:
                bet_type = self._prompt_outside_type(ctx)
                bet_value = self._prompt_outside_value(ctx, bet_type)

            # Once values are successfully chosen, save to dictionary
            self._save_bet(player_index, bet_type, bet_value, bet_amount)
            player_index += 1  # Move to next user

    def _all_players_bankrupt(self) -> bool:
        return sum(a.balance for a in self.accounts) == 0

    def _prompt_bet_amount(self, ctx: GameContext, player_index: int) -> int:
        """Ask for bet amount, validate it, withdraw it, and return the amount (or None on error)."""
        balance = self.accounts[player_index].balance

        raw = prompt_with_error(
            ctx=ctx,
            prompt=f"Player {player_index + 1}'s Bet: ",
            validator=lambda s: s.isdigit() and 0 < int(s) <= balance,
            error_text=f"Please enter a positive integer up to {balance}.",
            render_table=False,
            transform=lambda s: s.strip(),
        )

        bet_amount = int(raw)
        self.accounts[player_index].withdraw(bet_amount)

        render_header(ctx)
        return bet_amount

    def _prompt_bet_area(self, ctx: GameContext) -> str:
        """Return 'inside' or 'outside'."""
        ans = prompt_with_error(
            ctx=ctx,
            prompt="🤵: Choose your bet area: [I]nside (single number) / [O]utside: ",
            validator=lambda a: a in {"i", "inside", "o", "outside"},
            error_text="Choose 'I' for inside or 'O' for outside.",
            render_table=False,
            transform=lambda s: s.strip().lower(),
        )
        if ans in {"i", "inside"}:
            return "inside"
        else:
            return "outside"

    def _prompt_inside_number(self, ctx: GameContext) -> str:
        """Inside bet: straight-up number (0-36)."""
        return prompt_with_error(
            ctx=ctx,
            prompt="🤵: Enter number you would like to bet on: ",
            validator=lambda a: a in self.valid_numbers,
            error_text="Invalid number. Choose from 0-36",
            render_table=True,
            transform=lambda s: s.strip(),
        )

    def _prompt_outside_type(self, ctx: GameContext) -> str:
        """Return outside bet type identifier."""
        mapping = {
            "1": "outside_color",
            "2": "outside_parity",
            "3": "outside_highlow",
            "4": "outside_dozen",
            "5": "outside_column",
        }

        last_error = ""
        while True:
            render_outside_bets_menu(ctx)
            if last_error:
                cprint(last_error)

            choice = cinput("🤵: Choose option (1-5): ").strip()
            if choice in mapping:
                return mapping[choice]
            last_error = "Choose a number from 1 to 5."

    def _prompt_outside_value(self, ctx: GameContext, bet_type: str) -> str:
        """Prompt for the value of an outside bet."""
        if bet_type == "outside_color":
            ans = prompt_with_error(
                ctx=ctx,
                prompt="🤵: Choose color [R]ed / [B]lack: ",
                validator=lambda a: a in {"r", "red", "b", "black"},
                error_text="Choose red or black.",
                render_table=False,
                transform=lambda s: s.strip().lower(),
            )
            if ans in {"r", "red"}:
                return "red"
            else:
                return "black"

        if bet_type == "outside_parity":
            ans = prompt_with_error(
                ctx=ctx,
                prompt="🤵: Choose [O]dd / [E]ven: ",
                validator=lambda a: a in {"o", "odd", "e", "even"},
                error_text="Choose odd or even.",
                render_table=False,
                transform=lambda s: s.strip().lower(),
            )
            if ans in {"o", "odd"}:
                return "odd"
            else:
                return "even"

        if bet_type == "outside_highlow":
            ans = prompt_with_error(
                ctx=ctx,
                prompt="🤵: Choose [L]ow (1-18) / [H]igh (19-36): ",
                validator=lambda a: a in {"l", "low", "h", "high"},
                error_text="Choose low or high.",
                render_table=True,
                transform=lambda s: s.strip().lower(),
            )
            if ans in {"l", "low"}:
                return "low"
            else:
                return "high"

        if bet_type == "outside_column":
            ans = prompt_with_error(
                ctx=ctx,
                prompt="🤵: Choose column: [1]=1st [2]=2nd [3]=3rd: ",
                validator=lambda a: a in {"1", "2", "3"},
                error_text="Choose 1, 2, or 3.",
                render_table=True,
                transform=lambda s: s.strip().lower(),
            )
            return ans

        if bet_type == "outside_dozen":
            ans = prompt_with_error(
                ctx=ctx,
                prompt="🤵: Choose dozen: [1]=1-12 [2]=13-24 [3]=25-36: ",
                validator=lambda a: a in {"1", "2", "3"},
                error_text="Choose 1, 2, or 3.",
                render_table=True,
                transform=lambda s: s.strip().lower(),
            )
            return ans

        raise ValueError(f"Unknown outside bet type: {bet_type}")

    def _save_bet(self, player_index: int, bet_type: str, bet_value: str, bet_amount: int) -> None:
        account_id = str(self.accounts[player_index].aid)
        self.bets[account_id] = {
            "type": bet_type,
            "value": bet_value,
            "amount": bet_amount
        }

    def _format_bet(self, bet: dict) -> str:
        t = bet["type"]
        v = bet["value"]
        a = bet["amount"]

        if t == "inside_number":
            return f"{a} on number {v}"

        if t == "outside_color":
            return f"{a} on {v} (color)"

        if t == "outside_parity":
            return f"{a} on {v} (parity)"

        if t == "outside_highlow":
            return f"{a} on {v} (high/low)"

        if t == "outside_dozen":
            label = {"1": "1-12", "2": "13-24", "3": "25-36"}[v]
            return f"{a} on dozen {v} ({label})"

        if t == "outside_column":
            return f"{a} on column {v}"

        return f"{a} on {t}:{v}"

    def payout(self) -> None:
        assert self.winning_value is not None
        winning_number = self.winning_value[0]

        accounts_by_id = {
            str(a.aid): (a, index + 1)
            for index, a in enumerate(self.accounts)}

        cprint("Paying out all winners...")
        is_zero = (winning_number == "0")
        winning_int = None if is_zero else int(winning_number)
        for account_id, bet in self.bets.items():
            entry = accounts_by_id.get(account_id)
            if entry is None:
                continue

            account, player_number = entry
            bet_type = bet["type"]
            bet_value = bet["value"]
            bet_amount = bet["amount"]

            win_multiplier = self._compute_win_multiplier(
                bet_type=bet_type,
                bet_value=bet_value,
                winning_number=winning_number,
                winning_int=winning_int,
                is_zero=is_zero
            )

            if win_multiplier > 1:
                win_amount = bet_amount * win_multiplier
                account.deposit(win_amount)
                cprint(f"Player {player_number}: Won {win_amount} coins.")
            else:
                cprint(f"Player {player_number}: Lost {bet_amount} coins.")

        cprint("Finished payout.")

    def _compute_win_multiplier(self, bet_type: str, bet_value: str, winning_number: str,
                                winning_int: Optional[int], is_zero: bool) -> int:
        """
        Return total payout multiplier including stake return.
        - 1 means loss (stake not returned; it was already withdrawn)
        - 2 means even-money win (1:1 payout + stake)
        - 3 means 2:1 payout + stake
        - 36 means 35:1 payout + stake
        """
        # Inside: straight-up (35:1 payout)
        if bet_type == "inside_number":
            if bet_value == winning_number:
                return MULTIPLIER_STRAIGHT_UP
            return MULTIPLIER_LOSS

        # Outside bets lose on zero
        if is_zero or winning_int is None:
            return MULTIPLIER_LOSS

        n = winning_int

        if bet_type == "outside_color":
            if (bet_value == "red" and n in RED_NUMBERS) or (bet_value == "black" and n not in RED_NUMBERS):
                return MULTIPLIER_EVEN_MONEY
        elif bet_type == "outside_parity":
            if (bet_value == "odd" and n % 2 == 1) or (bet_value == "even" and n % 2 == 0):
                return MULTIPLIER_EVEN_MONEY
        elif bet_type == "outside_highlow":
            if (bet_value == "low" and 1 <= n <= 18) or (bet_value == "high" and 19 <= n <= 36):
                return MULTIPLIER_EVEN_MONEY
        elif bet_type == "outside_column":
            if n in COLUMNS[bet_value]:
                return MULTIPLIER_TWO_TO_ONE
        elif bet_type == "outside_dozen":
            if n in DOZENS[bet_value]:
                return MULTIPLIER_TWO_TO_ONE

        return MULTIPLIER_LOSS    # Unknown bet type (treat as loss)


class EuropeanRoulette(Roulette):
    """Plays roulette using European rules."""

    def __init__(self, accounts: List[Account]):
        super().__init__(accounts)
        self.wheel = STANDARD_EUROPEAN_ROULETTE_WHEEL
        self.valid_numbers = [number for (number, _, _, _) in self.wheel]


def play_european_roulette(context: GameContext) -> None:
    # Temporary fix
    # TODO: fix argument in play_roulette to only except `List[GameContext]`
    # and not `GameContext`

    # Access account data
    accounts = [context.account]

    roulette = EuropeanRoulette(accounts)
    while True:
        roulette.reset_round()
        render_header(context)

        # Input to stop loop from running constantly
        choice = cinput("Press [Enter] to start a new round and [q] to quit: ").strip().lower()

        if choice in {"q", "quit"}:
            return

        status = roulette.submit_bets(context)
        if status == "BANKRUPT":
            return

        roulette.spin_wheel(context)
        roulette.payout()
        refresh_roulette_topbar(context)

        # play again?
        play_again = cinput("🤵: Would you like to play another round (Y/n): ").strip().lower()
        if play_again in {"", "y", "yes"}:
            pass  # next round
        elif play_again in {"n", "no"}:
            return
        else:
            play_again = prompt_with_error(
                ctx=context,
                prompt="🤵: Would you like to play another round (Y/n): ",
                validator=lambda a: a in {"", "y", "yes", "n", "no"},
                error_text="Please enter 'Yes' or 'No'.",
                render_table=False,
                transform=lambda s: s.strip().lower(),
            )
            if play_again in {"n", "no"}:
                return
