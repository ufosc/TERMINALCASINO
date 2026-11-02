import random
import time
from typing import Optional

from casino.accounts import Account
from casino.stats import GameStats, display_stats
from casino.types import GameContext
from casino.utils import cprint
from .constants import (
    MULTIPLIER_EVEN_MONEY,
    MULTIPLIER_LOSS,
    MULTIPLIER_STRAIGHT_UP,
    SEC_BTWN_SPIN,
    TOTAL_ROTATIONS,
)
from .views import RouletteView

WheelEntry = tuple[str, str, int, int]
Bet = dict[str, str | int]


class Roulette:
    """Shared roulette round logic. Variants supply their wheel and bet rules."""

    wheel: list[WheelEntry] = []
    outside_bets = False

    def __init__(self, accounts: list[Account], view: Optional[RouletteView] = None) -> None:
        self.accounts = accounts
        self.view = view or RouletteView()
        self.valid_numbers = [number for number, _, _, _ in self.wheel]
        self.valid_colors = ["red", "green", "black"]
        self.bets: dict[str, Bet] = {}
        self.winning_value: Optional[WheelEntry] = None

    @staticmethod
    def normalize_color(input_value: str) -> str:
        return {
            "r": "red",
            "red": "red",
            "g": "green",
            "green": "green",
            "b": "black",
            "black": "black",
        }.get(input_value.lower(), input_value)

    @staticmethod
    def normalize_type(input_value: str) -> str:
        return {
            "c": "color",
            "color": "color",
            "n": "number",
            "number": "number",
        }.get(input_value.lower(), input_value)

    @staticmethod
    def roulette_sort_key(value: str) -> int:
        if value == "0":
            return -1
        if value == "00":
            return 0
        return int(value)

    def reset_round(self) -> None:
        self.bets.clear()
        self.winning_value = None

    def submit_bets(self, ctx: GameContext) -> Optional[str]:
        self.view.bind(ctx)
        for player_index, account in enumerate(self.accounts):
            if self._all_players_bankrupt():
                self.view.announce(
                    "🤵: All players have gone bankrupt. "
                    "You cannot play any more roulette.",
                    pause=3,
                )
                return "BANKRUPT"
            if account.balance == 0:
                self.view.announce(
                    f"Skipping player {player_index + 1} because of empty balance..."
                )
                continue

            bet = self.view.prompt_bet(
                player_index,
                account.balance,
                self.valid_numbers,
                self.outside_bets,
            )
            if bet is None:
                continue
            bet_type, bet_value, bet_amount = bet
            account.withdraw(bet_amount)
            self.bets[str(account.aid)] = {
                "type": bet_type,
                "value": bet_value,
                "amount": bet_amount,
            }
        return None

    def _all_players_bankrupt(self) -> bool:
        return sum(account.balance for account in self.accounts) == 0

    def spin_wheel(
        self, ctx: GameContext, sec_btwn_spins: float = SEC_BTWN_SPIN
    ) -> WheelEntry:
        self.view.bind(ctx)
        random_index = random.randint(0, len(self.wheel) - 1)
        self.winning_value = self.wheel[random_index]
        wheel_sequence = [number for number, _, _, _ in self.wheel]
        sequence = (wheel_sequence * TOTAL_ROTATIONS) + wheel_sequence[:random_index + 1]

        for number in sequence:
            self.view.clear_and_topbar()
            self.view.render_wheel(self.wheel, number)
            time.sleep(sec_btwn_spins)

        self.view.show_result(self.winning_value, self.bets)
        return self.winning_value

    def payout(self) -> None:
        if self.winning_value is None:
            raise RuntimeError("Cannot pay out before the roulette wheel has been spun.")

        winning_number, _, _, _ = self.winning_value
        accounts_by_id = {
            str(account.aid): (account, index + 1)
            for index, account in enumerate(self.accounts)
        }
        self.view.announce("Paying out all winners...")
        for account_id, bet in self.bets.items():
            account_info = accounts_by_id.get(account_id)
            if account_info is None:
                continue
            account, player_number = account_info
            bet_type = str(bet["type"])
            bet_value = str(bet["value"])
            bet_amount = int(bet["amount"])
            multiplier = self.compute_win_multiplier(bet_type, bet_value, winning_number)
            if multiplier > 1:
                win_amount = bet_amount * multiplier
                account.deposit(win_amount)
                self.view.announce(f"Player {player_number}: Won {win_amount} coins.")
            else:
                self.view.announce(f"Player {player_number}: Lost {bet_amount} coins.")
        self.view.announce("Finished payout.")

    def compute_win_multiplier(self, bet_type: str, bet_value: str, winning_number: str) -> int:
        """Return the total payout multiplier, including return of the original stake."""
        winning_color = next(
            color for number, color, _, _ in self.wheel if number == winning_number
        )
        if bet_type == "number" and bet_value == winning_number:
            return MULTIPLIER_STRAIGHT_UP
        if bet_type == "color" and bet_value == winning_color:
            return MULTIPLIER_EVEN_MONEY
        return MULTIPLIER_LOSS

    def play(self, ctx: GameContext, game_name: str) -> None:
        self.view.bind(ctx)
        stats = GameStats(game_name, ctx.account.balance)
        while True:
            self.reset_round()
            self.view.render_header()
            if self.view.prompt_round_start() in {"q", "quit"}:
                break

            previous_balance = ctx.account.balance
            if self.submit_bets(ctx) == "BANKRUPT":
                break

            self.spin_wheel(ctx)
            self.payout()
            if ctx.account.balance != previous_balance:
                stats.rounds_played += 1
                if ctx.account.balance > previous_balance:
                    stats.wins += 1
                else:
                    stats.losses += 1
            self.view.refresh_topbar()
            if not self.view.prompt_play_again():
                break

        stats.ending_balance = ctx.account.balance
        display_stats(stats)
