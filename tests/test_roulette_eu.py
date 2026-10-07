from unittest.mock import patch

from casino.accounts import Account
from casino.config import Config
from casino.games.roulette import european_roulette
from casino.games.roulette.european_roulette import EuropeanRoulette
from casino.types import GameContext
import pytest


# (responses, wheel index, balance, wins, losses)
VARIANTS = [
    (["", "y", "10", "o", "1", "red", "n"], 1, 110, 1, 0),
    (["", "y", "10", "o", "1", "red", "n"], 2, 90, 0, 1),
]


@pytest.mark.parametrize(
    "inputs, winning_index, expected_balance, expected_wins, expected_losses",
    VARIANTS,
)
def test_eu_roulette(
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
        patch("casino.games.roulette.european_roulette.cinput", side_effect=inputs),
        patch("casino.games.roulette.european_roulette.cprint"),
        patch("casino.games.roulette.european_roulette.clear_screen"),
        patch("casino.games.roulette.european_roulette.display_roulette_topbar"),
        patch("casino.games.roulette.european_roulette.render_header"),
        patch("casino.games.roulette.european_roulette.refresh_roulette_topbar"),
        patch.object(EuropeanRoulette, "wheel_animation"),
        patch.object(EuropeanRoulette, "print_wheel"),
        patch(
            "casino.games.roulette.european_roulette.random.randint",
            return_value=winning_index,
        ),
        patch(
            "casino.games.roulette.european_roulette.display_stats",
            side_effect=stats.append,
        ),
        patch("casino.stats.cprint"),
        patch("casino.stats.cinput", return_value=""),
    ]

    for p in patches:
        p.start()

    try:
        european_roulette.play_european_roulette(ctx)
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
