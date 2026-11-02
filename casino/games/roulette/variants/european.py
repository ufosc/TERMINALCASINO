from casino.types import GameContext
from ..base import Roulette
from ..constants import (
    COLUMNS,
    DOZENS,
    MULTIPLIER_EVEN_MONEY,
    MULTIPLIER_LOSS,
    MULTIPLIER_STRAIGHT_UP,
    MULTIPLIER_TWO_TO_ONE,
    RED_NUMBERS,
)
from ..views import RouletteView

STANDARD_EUROPEAN_ROULETTE_WHEEL = [
    ("0", "green", 0, 14), ("32", "red", 0, 17), ("15", "black", 0, 20),
    ("19", "red", 1, 24), ("4", "black", 2, 27), ("21", "red", 3, 28),
    ("2", "black", 4, 30), ("25", "red", 5, 30), ("17", "black", 6, 31),
    ("34", "red", 7, 31), ("6", "black", 8, 31), ("27", "red", 9, 31),
    ("13", "black", 10, 31), ("36", "red", 11, 30), ("11", "black", 12, 30),
    ("30", "red", 13, 28), ("8", "black", 14, 26), ("23", "red", 15, 24),
    ("10", "black", 16, 19), ("5", "red", 16, 16), ("24", "black", 16, 13),
    ("16", "red", 15, 8), ("33", "black", 14, 6), ("1", "red", 13, 4),
    ("20", "black", 12, 2), ("14", "red", 11, 2), ("31", "black", 10, 1),
    ("9", "red", 9, 1), ("22", "black", 8, 1), ("18", "red", 7, 1),
    ("29", "black", 6, 1), ("7", "red", 5, 2), ("28", "black", 4, 2),
    ("12", "red", 3, 4), ("35", "black", 2, 5), ("3", "red", 1, 8),
    ("26", "black", 0, 11),
]


class EuropeanRoulette(Roulette):
    """European roulette offers inside and outside bets on a single-zero wheel."""

    wheel = STANDARD_EUROPEAN_ROULETTE_WHEEL
    outside_bets = True

    def __init__(self, accounts, view: RouletteView | None = None) -> None:
        super().__init__(accounts, view or RouletteView(european=True))

    def compute_win_multiplier(self, bet_type: str, bet_value: str, winning_number: str) -> int:
        if bet_type == "inside_number":
            return MULTIPLIER_STRAIGHT_UP if bet_value == winning_number else MULTIPLIER_LOSS
        if winning_number == "0":
            return MULTIPLIER_LOSS

        number = int(winning_number)
        if bet_type == "outside_color":
            won = (bet_value == "red" and number in RED_NUMBERS) or (
                bet_value == "black" and number not in RED_NUMBERS
            )
            return MULTIPLIER_EVEN_MONEY if won else MULTIPLIER_LOSS
        if bet_type == "outside_parity":
            won = (bet_value == "odd" and number % 2 == 1) or (
                bet_value == "even" and number % 2 == 0
            )
            return MULTIPLIER_EVEN_MONEY if won else MULTIPLIER_LOSS
        if bet_type == "outside_highlow":
            won = (bet_value == "low" and 1 <= number <= 18) or (
                bet_value == "high" and 19 <= number <= 36
            )
            return MULTIPLIER_EVEN_MONEY if won else MULTIPLIER_LOSS
        if bet_type == "outside_column" and number in COLUMNS[bet_value]:
            return MULTIPLIER_TWO_TO_ONE
        if bet_type == "outside_dozen" and number in DOZENS[bet_value]:
            return MULTIPLIER_TWO_TO_ONE
        return MULTIPLIER_LOSS


def play_european_roulette(context: GameContext) -> None:
    roulette = EuropeanRoulette([context.account], RouletteView(context, european=True))
    roulette.play(context, "European Roulette")
