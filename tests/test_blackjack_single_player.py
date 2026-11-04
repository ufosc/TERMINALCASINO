from unittest.mock import patch
import pytest

from casino.accounts import Account
from casino.cards import StandardCard
from casino.config import Config
from casino.types import GameContext
from casino.games.blackjack.variants.standard import StandardBlackjack, play_blackjack
from casino.games.blackjack.variants.european import (
    EuropeanBlackjack,
    play_european_blackjack,
)

# Blackjack is single-player only.
VARIANTS = [StandardBlackjack, EuropeanBlackjack]
BLACKJACK_MODULES = [
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
def test_main_menu_choice_leaves_blackjack(variant):
    blackjack = variant(make_context())

    with patch("casino.games.blackjack.views.view.cinput", return_value="m"), \
         patch("casino.games.blackjack.base.clear_screen"), \
         patch("casino.games.blackjack.views.view.display_topbar"):
        assert blackjack.play_again() == "MENU"


@pytest.mark.parametrize(
    ("handler", "module", "game_class"),
    [
        (play_blackjack, "standard", StandardBlackjack),
        (play_european_blackjack, "european", EuropeanBlackjack),
    ],
)
def test_main_menu_choice_exits_the_whole_blackjack_session(handler, module, game_class):
    context = make_context()
    second_player = Account.generate("second", 100)

    with patch.object(game_class, "play_round", return_value="MENU") as play_round, \
         patch(
             f"casino.games.blackjack.variants.{module}.seat_second_player",
             return_value=second_player,
         ), \
         patch(f"casino.games.blackjack.variants.{module}.display_stats"), \
         patch(f"casino.games.blackjack.variants.{module}.cprint"), \
         patch(f"casino.games.blackjack.variants.{module}.sleep"):
        assert handler(context) == "MENU"

    play_round.assert_called_once()


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
    patches.append(patch("casino.games.blackjack.base.clear_screen"))
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
