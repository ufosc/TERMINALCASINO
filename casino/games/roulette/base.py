import random
from time import sleep
from typing import Optional

from casino.accounts import Account
from casino.types import GameContext
from casino.utils import cprint, clear_screen

from .constants import (
    COLUMNS,
    DOZENS,
    MULTIPLIER_EVEN_MONEY,
    MULTIPLIER_LOSS,
    MULTIPLIER_STRAIGHT_UP,
    MULTIPLIER_TWO_TO_ONE,
    RED_NUMBERS,
    TOTAL_ROTATIONS,
)
from .views import RouletteView


class Roulette:
    """Base roulette game logic shared by all roulette variants."""

    def __init__(self, accounts: list[Account], view: RouletteView | None = None) -> None:
        self.wheel: list[tuple[str, str, int, int]] = []
        self.valid_colors = ["red", "green", "black", "r", "g", "b"]
        self.valid_numbers: list[str] = []
        self.accounts = accounts
        self.bets: dict[str, dict[str, str | int]] = {}
        self.winning_value: Optional[tuple[str, str, int, int]] = None
        self.view = view or RouletteView()

    @staticmethod
    def normalize_color(value: str) -> str:
        return {"r": "red", "red": "red", "g": "green", "green": "green",
                "b": "black", "black": "black"}.get(value.lower(), value)

    @staticmethod
    def normalize_type(value: str) -> str:
        return {"c": "color", "color": "color", "n": "number", "number": "number"}.get(
            value.lower(), value
        )

    @staticmethod
    def roulette_sort_key(value: str) -> int:
        if value == "0":
            return -1
        if value == "00":
            return 0
        return int(value)

    def spin_wheel(self, context: GameContext) -> tuple[str, str, int, int]:
        index = random.randint(0, len(self.wheel) - 1)
        self.winning_value = self.wheel[index]
        sequence = [number for number, _, _, _ in self.wheel]
        self.view.wheel_animation(
            context, self.wheel, sequence * TOTAL_ROTATIONS + sequence[:index + 1]
        )
        cprint(f"Winning number: {self.winning_value[0]}")
        cprint(f"Winning color: {self.winning_value[1]}")
        bet = self.bets.get(str(context.account.aid))
        cprint("Your bet: (none)" if bet is None else f"Your bet: {self._format_bet(bet)}")
        return self.winning_value

    def reset_round(self) -> None:
        self.bets.clear()
        self.winning_value = None

    def submit_bets(self, context: GameContext) -> str | None:
        player_index = 0
        while player_index < len(self.accounts):
            if self._all_players_bankrupt():
                cprint("🤵: All players have gone bankrupt. You cannot play any more roulette.")
                sleep(3)
                return "BANKRUPT"
            if self.accounts[player_index].balance == 0:
                cprint(f"Skipping player {player_index + 1} because of empty balance...")
                player_index += 1
                continue
            will_bet = self.view.prompt(
                context, f"🤵: Would you like to bet, Player {player_index + 1} (y/N): ",
                lambda value: value in {"", "y", "yes", "n", "no"},
                "Invalid input. Enter either 'Y' for yes or 'N' for no.",
            )
            if will_bet in {"", "n", "no"}:
                cprint("User skipped betting. Moving to next user...", end="\n\n")
                player_index += 1
                continue
            amount = self._prompt_bet_amount(context, player_index)
            area = self.view.prompt(
                context, "🤵: Choose your bet area: [I]nside (single number) / [O]utside: ",
                lambda value: value in {"i", "inside", "o", "outside"},
                "Choose 'I' for inside or 'O' for outside.",
            )
            if area in {"i", "inside"}:
                bet_type = "inside_number"
                bet_value = self.view.prompt(
                    context, "🤵: Enter number you would like to bet on: ",
                    lambda value: value in self.valid_numbers, "Invalid number. Choose from 0-36.",
                    render_table=True, transform=lambda value: value.strip(),
                )
            else:
                bet_type, bet_value = self._prompt_outside_bet(context)
            self._save_bet(player_index, bet_type, bet_value, amount)
            player_index += 1
        return None

    def _prompt_bet_amount(self, context: GameContext, player_index: int) -> int:
        balance = self.accounts[player_index].balance
        raw = self.view.prompt(
            context, f"Player {player_index + 1}'s Bet: ",
            lambda value: value.isdigit() and 0 < int(value) <= balance,
            f"Please enter a positive integer up to {balance}.", transform=lambda value: value.strip(),
        )
        amount = int(raw)
        self.accounts[player_index].withdraw(amount)
        self.view.render_header(context)
        return amount

    def _prompt_outside_bet(self, context: GameContext) -> tuple[str, str]:
        mapping = {"1": "outside_color", "2": "outside_parity", "3": "outside_highlow",
                   "4": "outside_dozen", "5": "outside_column"}
        choice = self.view.prompt(
            context, "🤵: Choose option (1-5): ", lambda value: value in mapping,
            "Choose a number from 1 to 5.",
        )
        bet_type = mapping[choice]
        options = {
            "outside_color": ("🤵: Choose color [R]ed / [B]lack: ", {"r", "red", "b", "black"},
                              "Choose red or black."),
            "outside_parity": ("🤵: Choose [O]dd / [E]ven: ", {"o", "odd", "e", "even"},
                               "Choose odd or even."),
            "outside_highlow": ("🤵: Choose [L]ow (1-18) / [H]igh (19-36): ",
                                {"l", "low", "h", "high"}, "Choose low or high."),
            "outside_column": ("🤵: Choose column: [1]=1st [2]=2nd [3]=3rd: ",
                               {"1", "2", "3"}, "Choose 1, 2, or 3."),
            "outside_dozen": ("🤵: Choose dozen: [1]=1-12 [2]=13-24 [3]=25-36: ",
                              {"1", "2", "3"}, "Choose 1, 2, or 3."),
        }
        prompt, valid, error = options[bet_type]
        value = self.view.prompt(context, prompt, lambda answer: answer in valid, error,
                                 render_table=bet_type in {"outside_highlow", "outside_column", "outside_dozen"})
        if bet_type == "outside_color":
            value = "red" if value in {"r", "red"} else "black"
        elif bet_type == "outside_parity":
            value = "odd" if value in {"o", "odd"} else "even"
        elif bet_type == "outside_highlow":
            value = "low" if value in {"l", "low"} else "high"
        return bet_type, value

    def _all_players_bankrupt(self) -> bool:
        return sum(account.balance for account in self.accounts) == 0

    def _save_bet(self, player_index: int, bet_type: str, bet_value: str, amount: int) -> None:
        self.bets[str(self.accounts[player_index].aid)] = {
            "type": bet_type, "value": bet_value, "amount": amount
        }

    def _format_bet(self, bet: dict[str, str | int]) -> str:
        return f"{bet['amount']} on {bet['value']} ({bet['type'].removeprefix('outside_')})"

    def payout(self) -> None:
        if self.winning_value is None:
            raise RuntimeError("Cannot pay out before the wheel has been spun.")
        winning_number = self.winning_value[0]
        winning_int = None if winning_number in {"0", "00"} else int(winning_number)
        accounts = {str(account.aid): (account, index + 1) for index, account in enumerate(self.accounts)}
        cprint("Paying out all winners...")
        for account_id, bet in self.bets.items():
            if account_id not in accounts:
                continue
            account, player = accounts[account_id]
            multiplier = self._compute_win_multiplier(
                str(bet["type"]), str(bet["value"]), winning_number, winning_int
            )
            amount = int(bet["amount"])
            if multiplier > 1:
                account.deposit(amount * multiplier)
                cprint(f"Player {player}: Won {amount * multiplier} coins.")
            else:
                cprint(f"Player {player}: Lost {amount} coins.")
        cprint("Finished payout.")

    def _compute_win_multiplier(self, bet_type: str, bet_value: str,
                                winning_number: str, winning_int: int | None) -> int:
        if bet_type == "inside_number":
            return MULTIPLIER_STRAIGHT_UP if bet_value == winning_number else MULTIPLIER_LOSS
        if winning_int is None:
            return MULTIPLIER_LOSS
        if bet_type == "outside_color" and (
            (bet_value == "red" and winning_int in RED_NUMBERS)
            or (bet_value == "black" and winning_int not in RED_NUMBERS)
        ):
            return MULTIPLIER_EVEN_MONEY
        if bet_type == "outside_parity" and (
            (bet_value == "odd" and winning_int % 2)
            or (bet_value == "even" and winning_int % 2 == 0)
        ):
            return MULTIPLIER_EVEN_MONEY
        if bet_type == "outside_highlow" and (
            (bet_value == "low" and 1 <= winning_int <= 18)
            or (bet_value == "high" and 19 <= winning_int <= 36)
        ):
            return MULTIPLIER_EVEN_MONEY
        if bet_type == "outside_column" and winning_int in COLUMNS.get(bet_value, set()):
            return MULTIPLIER_TWO_TO_ONE
        if bet_type == "outside_dozen" and winning_int in DOZENS.get(bet_value, set()):
            return MULTIPLIER_TWO_TO_ONE
        return MULTIPLIER_LOSS
