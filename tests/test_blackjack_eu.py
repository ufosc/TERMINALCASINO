#TODO: Add test cases for Blackjack EU
from unittest.mock import patch
import pytest

from casino.accounts import Account
from casino.cards import StandardCard
from casino.config import Config
from casino.types import GameContext
from casino.games.blackjack.variants.european import EuropeanBlackjack

VARIANTS = [EuropeanBlackjack]
BLACKJACK_MODULES = [
    "casino.games.blackjack.base",
    "casino.games.blackjack.views.view",
    "casino.games.blackjack.variants.standard",
    "casino.games.blackjack.variants.european",
]

def make_context(balance: int = 100) -> GameContext:
    return GameContext(account=Account.generate("test", balance), config=Config.default())

from casino.games.blackjack.hand import Hand

@pytest.mark.parametrize("cards, double_offered", [
    (["5", "3"], False),   # 8
    (["7", "5"], False),   # 12
    (["5", "4"], True),    # 9
    (["6", "4"], True),    # 10
    (["6", "5"], True),    # 11
])

def test_double_offered_only_9_10_11(cards, double_offered):
    """
    Plays one full round: bet 10, stand on 18, dealer busts, player leaves.
    """
    ctx = make_context(100)
    blackjack = EuropeanBlackjack(ctx)
    # Draw order: Player's two cards, then dealer's single up
    draw_order = cards + ["10"]
    blackjack.deck.cards = [StandardCard(rank, "spades") for rank in reversed(draw_order)]
    blackjack.player.hands = [Hand(bet=10)]
    blackjack.deal_cards()

    # Only require decision choices
    p = patch("casino.games.blackjack.variants.european.cinput", return_value="s")
    mock_cinput = p.start()
    try:
        blackjack.player_decision()
    finally:
        p.stop()

    # mock_cinput[0] holds info about cinput call
    # def cprint(*args...    ->   *args[0] is the string of choices
    menu = mock_cinput.call_args_list[0].args[0]
    assert ("[D]ouble" in menu) == double_offered


@pytest.mark.parametrize("balance_after_bet, double_offered", [
    (9, False),    # not enough to double 10
    (10, True),    # exactly enough to double 10
    (20, True),    # more than enough to double 10
])

def test_european_double_requires_balance(balance_after_bet, double_offered):
    ctx = make_context(balance_after_bet)
    blackjack = EuropeanBlackjack(ctx)

    draw_order = ["6", "4", "10"]   # Player has 10, dealer shows 10
    blackjack.deck.cards = [StandardCard(r, "spades") for r in reversed(draw_order)]
    blackjack.player.hands = [Hand(bet=10)]
    blackjack.deal_cards()

    p = patch("casino.games.blackjack.variants.european.cinput", return_value="s")
    mock_cinput = p.start()
    try:
        blackjack.player_decision()
    finally:
        p.stop()

    menu = mock_cinput.call_args_list[0].args[0]
    assert ("[D]ouble" in menu) == double_offered

EUROPEAN_MODULES = [
    "casino.games.blackjack.base",
    "casino.games.blackjack.views.view",
    "casino.games.blackjack.variants.european",
]

@pytest.mark.parametrize("bet, balance_after_bet, win", [
    (10, 80, False),
    (20, 60, False),
    (50, 0, False),
    (50, 200, True),
])

def test_european_double_balance(bet, balance_after_bet, win):
    ctx = make_context(100)
    blackjack = EuropeanBlackjack(ctx)
    draw_card = "A" if win else "9"
    draw_order = ["6", "4", "10", draw_card, "10", "5"]  # Player wins if win, else loses
    blackjack.deck.cards = [StandardCard(r, "spades") for r in reversed(draw_order)]

    inputs = iter([str(bet), "d", "", "n"])  # bet, double, continue, leave table
    patches = []
    for module in EUROPEAN_MODULES:
        patches.append(patch(f"{module}.cinput", side_effect=lambda *_: next(inputs)))
        patches.append(patch(f"{module}.clear_screen"))
    patches += [
        patch("casino.games.blackjack.variants.european.sleep"),
    ]
    for p in patches:
        p.start()
    try:
        if balance_after_bet == 0:          # Removed from casino
            with pytest.raises(SystemExit): # Does it raise a SystemExit?
                blackjack.play_round()
        else:
            status = blackjack.play_round()
            assert status == "EXIT" # Should not be a system exit

        # Status = blackjack.play_round()
    finally:
        for p in patches:
            p.stop()

    assert ctx.account.balance == balance_after_bet
