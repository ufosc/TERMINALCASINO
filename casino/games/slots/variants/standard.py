import random

from casino.stats import display_stats
from casino.types import GameContext
from ..base import Slots
from ..constants import (
    ALL_ITEMS,
    LOW_ITEMS,
    HIGH_ITEMS,
    WIN_PROBABILITY,
    HIGH_VALUE_PROBABILITY,
    BET_PROMPT_SINGLE,
    INVALID_BET_MSG_SINGLE,
)


def get_rand_item() -> str:
    return random.choice(ALL_ITEMS)


class StandardSlots(Slots):
    """
    The base Slots game: a single payline, bet as one lump amount.
    """

    def __init__(self, ctx: GameContext) -> None:
        super().__init__(ctx, "Slots")

    def random_result(self) -> tuple[str, str, str]:
        return (get_rand_item(), get_rand_item(), get_rand_item())

    def render(self, result: tuple[str, str, str], frame: int = 0) -> None:
        self.view.render_row(result, frame)

    def prompt_bet(self) -> int:
        """Prompt user for bet amount."""
        while True:
            self.view.show_payout_legend()
            bet_str = self.view.prompt(BET_PROMPT_SINGLE)
            try:
                bet = int(bet_str)
            except ValueError:
                self.view.clear_and_topbar()
                self.view.announce(INVALID_BET_MSG_SINGLE)
                continue
            if bet < self.MINIMUM_BET:
                self.view.clear_and_topbar()
                self.view.announce(f"Each pay line requires at least {self.MINIMUM_BET} chips.")
                continue
            if bet > self.account.balance:
                self.view.clear_and_topbar()
                self.view.announce(f"You only have {self.account.balance} chips. Please try again.")
                continue
            return bet

    def bet_total(self, bet: int) -> int:
        return bet

    def settle(self, bet: int):
        rng = random.random()
        if rng <= WIN_PROBABILITY:
            if rng <= HIGH_VALUE_PROBABILITY:
                win_item = HIGH_ITEMS[random.randint(0, len(HIGH_ITEMS) - 1)]
                money_gain = bet * 5
            else:
                win_item = LOW_ITEMS[random.randint(0, len(LOW_ITEMS) - 1)]
                money_gain = int(bet * 1.5)
            result = (win_item, win_item, win_item)
            self.account.deposit(money_gain)
            message = f"MATCH: +{money_gain} chips"
            return result, money_gain, message, True

        result = self.random_result()
        while len(set(result)) == 1:
            result = self.random_result()
        self.account.withdraw(bet)
        message = f"NO MATCH: -{bet} chips"
        return result, 0, message, False


def play_slots(context: GameContext) -> None:
    """Play the base Slots game."""
    slots = StandardSlots(context)

    while True:
        status = slots.play_round()
        if status == "EXIT":
            display_stats(slots.stats)
            return
