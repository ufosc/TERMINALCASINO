from casino.types import GameContext

from .variants import StandardPoker


def play_poker(ctx: GameContext) -> None:
    """Play a poker game."""
    StandardPoker(ctx).play()
