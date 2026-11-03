from casino.accounts import Account
from casino.stats import GameStats, display_stats
from casino.types import GameContext
from casino.utils import cinput, clear_screen, cprint

from ..base import Roulette
from ..constants import STANDARD_EUROPEAN_ROULETTE_WHEEL
from ..views import RouletteView


class EuropeanRoulette(Roulette):
    """Roulette using the European wheel."""

    def __init__(self, accounts: list[Account]) -> None:
        super().__init__(accounts, view=RouletteView(european=True))
        self.wheel = STANDARD_EUROPEAN_ROULETTE_WHEEL
        self.valid_numbers = [number for number, _, _, _ in self.wheel]


def play_european_roulette(context: GameContext) -> None:
    roulette = EuropeanRoulette([context.account])
    stats = GameStats("European Roulette", context.account.balance)
    while True:
        roulette.reset_round()
        roulette.view.render_header(context)
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
        if choice in {"", "y", "yes"}:
            continue
        if choice not in {"n", "no"}:
            cprint("Please enter 'Yes' or 'No'.")
        break
    stats.ending_balance = context.account.balance
    display_stats(stats)
