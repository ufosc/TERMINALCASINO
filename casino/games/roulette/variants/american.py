from casino.types import GameContext
from ..base import Roulette
from ..constants import MULTIPLIER_EVEN_MONEY, MULTIPLIER_LOSS, MULTIPLIER_STRAIGHT_UP
from ..views import RouletteView

STANDARD_AMERICAN_ROULETTE_WHEEL = [
    ("0", "green", 0, 13), ("28", "black", 0, 16), ("9", "red", 0, 19),
    ("26", "black", 1, 24), ("30", "red", 2, 26), ("11", "black", 3, 27),
    ("7", "red", 4, 29), ("20", "black", 5, 29), ("32", "red", 6, 30),
    ("17", "black", 7, 30), ("5", "red", 8, 30), ("22", "black", 9, 30),
    ("34", "red", 10, 30), ("15", "black", 11, 29), ("3", "red", 12, 29),
    ("24", "black", 13, 27), ("36", "red", 14, 26), ("13", "black", 15, 24),
    ("1", "red", 16, 19), ("00", "green", 16, 16), ("27", "red", 16, 13),
    ("10", "black", 16, 10), ("25", "red", 15, 7), ("29", "black", 14, 6),
    ("12", "red", 13, 4), ("8", "black", 12, 3), ("19", "red", 11, 3),
    ("31", "black", 10, 2), ("18", "red", 9, 2), ("6", "black", 8, 2),
    ("21", "red", 7, 2), ("33", "black", 6, 2), ("16", "red", 5, 3),
    ("4", "black", 4, 3), ("23", "red", 3, 5), ("35", "black", 2, 6),
    ("14", "red", 1, 8), ("2", "black", 0, 10),
]


class AmericanRoulette(Roulette):
    """American roulette uses a 38-pocket wheel and simple color/number bets."""

    wheel = STANDARD_AMERICAN_ROULETTE_WHEEL

    def __init__(self, accounts, view: RouletteView | None = None) -> None:
        super().__init__(accounts, view or RouletteView())

    def compute_win_multiplier(self, bet_type: str, bet_value: str, winning_number: str) -> int:
        if bet_type == "number" and bet_value == winning_number:
            return MULTIPLIER_STRAIGHT_UP
        winning_color = next(
            color for number, color, _, _ in self.wheel if number == winning_number
        )
        if bet_type == "color" and bet_value == winning_color:
            if winning_color == "green":
                return MULTIPLIER_STRAIGHT_UP
            return MULTIPLIER_EVEN_MONEY
        return MULTIPLIER_LOSS


def play_roulette(context: GameContext) -> None:
    roulette = AmericanRoulette([context.account], RouletteView(context))
    roulette.play(context, "American Roulette")
