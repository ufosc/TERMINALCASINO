from typing import List

from casino.types import GameContext
from casino.accounts import Account
from casino.stats import display_stats, GameStats
from casino.utils import clear_screen, cprint, cinput

from ..base import (
    Roulette,
    STANDARD_AMERICAN_ROULETTE_WHEEL,
)
class AmericanRoulette(Roulette):
    """Plays roulette using American rules."""

    def __init__(self, accounts: List[Account]):
        super().__init__(accounts)
        self.wheel = STANDARD_AMERICAN_ROULETTE_WHEEL
        self.valid_numbers = [number for (number, _, _, _) in self.wheel]


def play_roulette(context: GameContext) -> None:
    continue_game = True

    # Temporary fix
    # TODO: fix argument in play_roulette to only except `List[GameContext]`
    # and not `GameContext`
    contexts = [context]

    # Access account data
    accounts = [account.account for account in contexts]

    if not isinstance(accounts, list):
        raise ValueError("accounts is not a list. "
                         f"accounts is a {type(accounts)}")

    roulette = AmericanRoulette(accounts)
    view = roulette.view
    stats = GameStats("American Roulette", context.account.balance)
    while continue_game:
        roulette.reset_round()
        clear_screen()
        view.display_roulette_topbar(context)

        # Input to stop loop from running constantly
        choice = cinput("Press [Enter] to start a new round and [q] to quit: ")

        if choice.lower() in {"q", "quit"}:
            continue_game = False
            break
        prev_balance = context.account.balance
        status = roulette.submit_bets(context)
        if status == "BANKRUPT":
            break

        roulette.spin_wheel(context)
        roulette.payout()
        if context.account.balance > prev_balance:
            stats.wins += 1
            stats.rounds_played += 1
        elif context.account.balance < prev_balance:
            stats.losses += 1
            stats.rounds_played += 1
        view.refresh_roulette_topbar(context)

        play_again = None

        while True:
            valid_choices = ["N", "NO", "Y", "YES", ""]
            play_again = cinput("🤵: Would you like to play another round (Y/n): ")

            if play_again.upper() not in valid_choices:
                cprint("Please enter 'Yes' or 'No'.")
                continue
            if play_again.lower() in {"n", "no"}:
                #cprint("Quitting roulette...")
                continue_game = False
                break
            elif play_again == "" or play_again.lower() in {"y", "yes"}:
                continue_game = True
                break
    stats.ending_balance = context.account.balance
    display_stats(stats)
    #cprint("Exiting roulette...")
    #sleep(0.5)
