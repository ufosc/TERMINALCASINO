from casino.types import GameContext

from .base import PokerGame


def play_poker(ctx: GameContext) -> None:
    """Play a poker game."""
    PokerGame(ctx).play()
