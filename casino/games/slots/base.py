import time
from abc import ABC, abstractmethod
from typing import Literal

from casino.stats import GameStats
from casino.types import GameContext
from .constants import SEC_BTWN_SPIN, TOTAL_SPINS, INVALID_INPUT_MSG, NO_FUNDS_MSG
from .views import SlotsView

SlotsMenuChoice = Literal["respin", "change_bet", "quit"]


class Slots(ABC):
    """
    Abstract base class that sets up a slot machine game.

    To create a variant of slots, inherit from this class.
    All inherited classes must only play one round (i.e. one spin) at a time.
    """

    def __init__(self, ctx: GameContext, game_name: str) -> None:
        self.context = ctx
        self.configurations = ctx.config
        self.view = SlotsView(ctx)
        self.MINIMUM_BET = self.configurations.slots_min_line_bet
        self.stats = GameStats(game_name, ctx.account.balance)

        self.take_new_bet = True
        self.bet = None

    @property
    def account(self):
        return self.context.account

    @abstractmethod
    def random_result(self):
        """
        Generate a purely random spin result in this variant's shape
        (e.g. a 3-item row, or a 3x3 grid). Used for the spin animation,
        and as a building block for settle().
        """
        ...

    @abstractmethod
    def render(self, result, frame: int = 0) -> None:
        """Draw `result` at the given animation `frame` using self.view."""
        ...

    @abstractmethod
    def prompt_bet(self):
        """Ask the player for a bet, in whatever shape this variant needs."""
        ...

    @abstractmethod
    def bet_total(self, bet) -> int:
        """Total chips wagered for `bet`."""
        ...

    @abstractmethod
    def settle(self, bet):
        """
        Spin, resolve the outcome against `bet`, and update the account balance.

        Returns (result, payout, message, won).
        """
        ...

    def spin_animation(self) -> None:
        """Animate pulling the arm, then spinning through random results."""
        for i in range(5):
            self.view.clear_and_topbar()
            self.render(self.random_result(), i)
            time.sleep(SEC_BTWN_SPIN)
        for _ in range(TOTAL_SPINS):
            self.view.clear_and_topbar()
            self.render(self.random_result(), 0)
            time.sleep(SEC_BTWN_SPIN)

    def menu_prompt(self, bet_total: int) -> str:
        """Return the [R]espin/[C]hange Bet/[Q]uit prompt appropriate to balance."""
        if self.account.balance < self.MINIMUM_BET:
            return "[Q]uit"
        if self.account.balance < bet_total:
            return "[C]hange Bet [Q]uit"
        return "[R]espin [C]hange Bet [Q]uit"

    def get_player_choice(self, result, bet_total: int) -> SlotsMenuChoice:
        """Prompt user for what to do after a spin."""
        first_iter = True
        while True:
            if not first_iter:
                self.view.clear_and_topbar()
                self.render(result)
                self.view.announce(INVALID_INPUT_MSG)
            first_iter = False

            player_input = self.view.prompt(self.menu_prompt(bet_total))
            if player_input == "":
                continue
            if player_input in "qQ":
                return "quit"
            elif player_input in "rR":
                if self.account.balance < bet_total:
                    continue
                return "respin"
            elif player_input in "cC":
                if self.account.balance < self.MINIMUM_BET:
                    continue
                return "change_bet"

    def play_round(self) -> str:
        """
        Plays a single round (one spin) of this Slots variant.

        Returns "CONTINUE" or "EXIT" so the driving loop knows whether
        to play another round.
        """
        self.view.clear_and_topbar()

        if self.take_new_bet:
            if self.account.balance < self.MINIMUM_BET:
                self.view.announce(NO_FUNDS_MSG)
                self.view.prompt("Press Enter to continue...")
                self.stats.ending_balance = self.account.balance
                return "EXIT"
            self.bet = self.prompt_bet()
            self.take_new_bet = False

        bet_total = self.bet_total(self.bet)
        if bet_total > self.account.balance:
            # Balance dropped below the standing bet (e.g. after a loss) —
            # make the player pick a new one before spinning again.
            self.take_new_bet = True
            return "CONTINUE"

        self.spin_animation()

        result, payout, message, won = self.settle(self.bet)

        self.view.clear_and_topbar()
        self.render(result)
        self.view.announce(message)

        self.stats.rounds_played += 1
        if won:
            self.stats.wins += 1
        else:
            self.stats.losses += 1

        choice = self.get_player_choice(result, bet_total)
        if choice == "quit":
            self.stats.ending_balance = self.account.balance
            return "EXIT"
        if choice == "change_bet":
            self.take_new_bet = True
        return "CONTINUE"
