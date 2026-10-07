from unittest.mock import patch

from casino.accounts import Account
from casino.config import Config
from casino.games.roulette import roulette
from casino.games.roulette.roulette import AmericanRoulette
from casino.types import GameContext
import pytest


# (responses, wheel index, balance, wins, losses)
VARIANTS = [
    (["", "y", "10", "C", "red", "n"], 2, 110, 1, 0),
    (["", "y", "10", "C", "red", "n"], 1, 90, 0, 1),
    (["", "y", "10", "C", "black", "n"], 1, 110, 1, 0),
    (["", "y", "10", "C", "black", "n"], 2, 90, 0, 1),
    (["", "y", "10", "N", "28", "n"], 1, 450, 1, 0),
    (["", "y", "10", "N", "28", "n"], 2, 90, 0, 1),
]


@pytest.mark.parametrize(
    "inputs, winning_index, expected_balance, expected_wins, expected_losses",
    VARIANTS,
)
def test_roulette(
    inputs,
    winning_index,
    expected_balance,
    expected_wins,
    expected_losses,
):
    ctx = GameContext(
        account=Account.generate("test", 100),
        config=Config.default(),
    )
    stats = []
    patches = [
        patch("casino.games.roulette.roulette.cinput", side_effect=inputs),
        patch("casino.games.roulette.roulette.cprint"),
        patch("casino.games.roulette.roulette.clear_screen"),
        patch("casino.games.roulette.roulette.display_roulette_topbar"),
        patch("casino.games.roulette.roulette.refresh_roulette_topbar"),
        patch.object(AmericanRoulette, "wheel_animation"),
        patch.object(AmericanRoulette, "print_wheel"),
        patch(
            "casino.games.roulette.roulette.random.randint",
            return_value=winning_index,
        ),
        patch(
            "casino.games.roulette.roulette.display_stats",
            side_effect=stats.append,
        ),
        patch("casino.stats.cprint"),
        patch("casino.stats.cinput", return_value=""),
    ]

    for p in patches:
        p.start()

    try:
        roulette.play_roulette(ctx)
    finally:
        for p in patches:
            p.stop()

    assert ctx.account.balance == expected_balance
    assert len(stats) == 1
    assert stats[0].starting_balance == 100
    assert stats[0].ending_balance == expected_balance
    assert stats[0].rounds_played == 1
    assert stats[0].wins == expected_wins
    assert stats[0].losses == expected_losses
