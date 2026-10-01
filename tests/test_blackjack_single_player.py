from unittest.mock import patch
import pytest

from casino.accounts import Account
from casino.cards import StandardCard
from casino.config import Config
from casino.types import GameContext
from casino.games.blackjack.variants.standard import StandardBlackjack
from casino.games.blackjack.variants.european import EuropeanBlackjack

# Blackjack is single-player only.
VARIANTS = [StandardBlackjack, EuropeanBlackjack]
BLACKJACK_MODULES = [
    "casino.games.blackjack.base",
    "casino.games.blackjack.views.view",
    "casino.games.blackjack.variants.standard",
    "casino.games.blackjack.variants.european",
]


def make_context(balance: int = 100) -> GameContext:
    return GameContext(account=Account.generate("test", balance), config=Config.default())


@pytest.mark.parametrize("variant", VARIANTS)
def test_no_player_count_prompt(variant):
    """
    Starting a game must not ask for any input (no "Enter number of Players").
    """
    with patch("builtins.input") as mock_input:
        variant(make_context())
    mock_input.assert_not_called()


@pytest.mark.parametrize("variant", VARIANTS)
def test_single_player_uses_logged_in_account(variant):
    """
    The only player at the table is the logged-in user.
    """
    ctx = make_context()
    blackjack = variant(ctx)
    assert blackjack.player.account is ctx.account
    assert not hasattr(blackjack, "players")


@pytest.mark.parametrize("variant", VARIANTS)
def test_single_player_round(variant):
    """
    Plays one full round: bet 10, stand on 18, dealer busts, player leaves.
    """
    ctx = make_context(100)
    blackjack = variant(ctx)
    # Cards are drawn from the end of the list: player 10, 8, then dealer 10, 6, K
    draw_order = ["10", "8", "10", "6", "K"]
    blackjack.deck.cards = [StandardCard(rank, "spades") for rank in reversed(draw_order)]

    inputs = iter(["10", "s", "", "n"])  # bet, stand, continue, leave table
    patches = []
    for module in BLACKJACK_MODULES:
        patches.append(patch(f"{module}.cinput", side_effect=lambda *_: next(inputs)))
        patches.append(patch(f"{module}.clear_screen"))
    patches += [
        patch("casino.games.blackjack.variants.standard.sleep"),
        patch("casino.games.blackjack.variants.european.sleep"),
    ]
    for p in patches:
        p.start()
    try:
        status = blackjack.play_round()
    finally:
        for p in patches:
            p.stop()

    assert status == "EXIT"
    assert [hand.result_key for hand in blackjack.player.hands] == ["dealer_bust"]
    assert ctx.account.balance == 110
    assert blackjack.stats.rounds_played == 1
    assert blackjack.stats.wins == 1
