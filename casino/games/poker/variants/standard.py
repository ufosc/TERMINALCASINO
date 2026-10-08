from casino.types import GameContext

from ..base import Poker


class StandardPoker(Poker):
    """Standard Texas Hold'em poker."""

    def __init__(self, ctx: GameContext) -> None:
        super().__init__(ctx)
