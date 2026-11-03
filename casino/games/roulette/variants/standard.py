from casino.accounts import Account
from casino.stats import GameStats, display_stats
from casino.types import GameContext
from casino.utils import cinput, clear_screen, cprint

from ..base import Roulette
from ..constants import STANDARD_AMERICAN_ROULETTE_WHEEL


class AmericanRoulette(Roulette):
    """Roulette using the American wheel, including 00."""

    def __init__(self, accounts: list[Account]) -> None:
        super().__init__(accounts)
        self.wheel = STANDARD_AMERICAN_ROULETTE_WHEEL
        self.valid_numbers = [number for number, _, _, _ in self.wheel]


StandardRoulette = AmericanRoulette


def play_roulette(context: GameContext) -> None:
    roulette = AmericanRoulette([context.account])
    _play(context, roulette, "American Roulette")


def _play(context: GameContext, roulette: Roulette, game_name: str) -> None:
    stats = GameStats(game_name, context.account.balance)
    while True:
        roulette.reset_round()
        clear_screen()
        roulette.view.display_topbar(context)
        if cinput("Press [Enter] to start a new round and [q] to quit: ").lower() in {"q", "quit"}:
            break
        previous_balance = context.account.balance
        if roulette.submit_bets(context) == "BANKRUPT":
            break
        roulette.spin_wheel(context)
        roulette.payout()
        if context.account.balance > previous_balance:
            stats.wins += 1
        elif context.account.balance < previous_balance:
            stats.losses += 1
        stats.rounds_played += 1
        roulette.view.refresh_topbar(context)
        choice = cinput("🤵: Would you like to play another round (Y/n): ").strip().lower()
        if choice not in {"", "y", "yes"}:
            if choice not in {"n", "no"}:
                cprint("Please enter 'Yes' or 'No'.")
            break
    stats.ending_balance = context.account.balance
    display_stats(stats)
