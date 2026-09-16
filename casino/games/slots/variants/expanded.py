import random

from casino.stats import display_stats
from casino.types import GameContext
from ..base import Slots
from ..constants import (
    ALL_ITEMS,
    HIGH_ITEMS,
    PAYLINES,
    BET_PROMPT_LINES,
    INVALID_BET_MSG_LINES,
)

Grid = tuple[tuple[str, str, str], tuple[str, str, str], tuple[str, str, str]]
LineBets = tuple[int, int, int]


def get_rand_item() -> str:
    return random.choice(ALL_ITEMS)


def get_rand_grid() -> Grid:
    return (
        (get_rand_item(), get_rand_item(), get_rand_item()),
        (get_rand_item(), get_rand_item(), get_rand_item()),
        (get_rand_item(), get_rand_item(), get_rand_item()),
    )


def payout_for_row(row: tuple[str, str, str], bet_per_line: int) -> int:
    """Return payout for one horizontal payline."""
    a, b, c = row
    if not (a == b == c):
        return 0
    if a in HIGH_ITEMS:
        return bet_per_line * 5
    return int(bet_per_line * 1.5)


def score_lines(grid: Grid, line_bets: LineBets) -> tuple[int, list[int]]:
    """Returns (total_payout, winning_row_indices)."""
    total = 0
    winners: list[int] = []
    for i, row in enumerate(grid):
        p = payout_for_row(row, line_bets[i])
        if p > 0:
            total += p
            winners.append(i)
    return total, winners


class ExpandedSlots(Slots):
    """
    The expanded Slots game: a 3x3 grid with 3 independent horizontal
    paylines, each with its own bet.
    """

    def __init__(self, ctx: GameContext) -> None:
        super().__init__(ctx, "Slots (Expanded)")

    def random_result(self) -> Grid:
        return get_rand_grid()

    def render(self, result: Grid, frame: int = 0) -> None:
        self.view.render_grid(result, frame)

    def prompt_bet(self) -> LineBets:
        """Prompt user for bet amount per row."""
        while True:
            self.view.show_payout_legend()
            raw = self.view.prompt(BET_PROMPT_LINES)
            parts = [p.strip() for p in raw.split(",")]
            if len(parts) != PAYLINES:
                self.view.clear_and_topbar()
                self.view.announce(INVALID_BET_MSG_LINES)
                continue
            try:
                bets = tuple(int(p) for p in parts)
            except ValueError:
                self.view.clear_and_topbar()
                self.view.announce(INVALID_BET_MSG_LINES)
                continue
            if any(b < 0 for b in bets):
                self.view.clear_and_topbar()
                self.view.announce("Bets cannot be negative.")
                continue
            if sum(bets) < self.MINIMUM_BET:
                self.view.clear_and_topbar()
                self.view.announce(f"You must bet at least {self.MINIMUM_BET} chips.")
                continue
            total_bet = sum(bets)
            if total_bet > self.account.balance:
                self.view.clear_and_topbar()
                self.view.announce(f"You need {total_bet} chips total. You have {self.account.balance}.")
                continue
            return bets

    def bet_total(self, bet: LineBets) -> int:
        return sum(bet)

    def settle(self, bet: LineBets):
        grid = self.random_result()
        total_bet = sum(bet)

        self.account.withdraw(total_bet)
        payout, winning_rows = score_lines(grid, bet)
        if payout > 0:
            self.account.deposit(payout)

        if payout > 0:
            rows_str = ",".join(str(r + 1) for r in winning_rows)
            message = f"ROWS {rows_str} MATCH: -{total_bet} +{payout} chips"
        else:
            message = f"NO MATCH: -{total_bet} chips"

        return grid, payout, message, payout > 0


def play_slots_expanded(context: GameContext) -> None:
    """Play the expanded Slots game."""
    slots = ExpandedSlots(context)

    while True:
        status = slots.play_round()
        if status == "EXIT":
            display_stats(slots.stats)
            return
