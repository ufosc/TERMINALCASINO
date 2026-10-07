#TODO: Add test cases for poker

#Poker tests implemented

from unittest.mock import patch

from casino.accounts import Account
from casino.cards import StandardCard
from casino.types import Config
from casino.types import GameContext
from casino.games.poker import poker as poker_module
from casino.games.poker.poker import PokerGame
import pytest


# (scripted choices, opponent second card, balance, wins, losses, pushes)
VARIANTS = [
    (["C", "C", "C", "C", "N"], "Q", 110, 1, 0, 0),
    (["C", "C", "C", "C", "N"], "K", 95, 0, 0, 1),
    (["C", "C", "C", "C", "N"], "J", 110, 1, 0, 0),
    (["C", "C", "C", "C", "N"], "10", 110, 1, 0, 0),
    (["C", "C", "C", "C", "N"], "9", 95, 0, 0, 1),
    (["F", "N"], "Q", 100, 0, 1, 0),
]


@pytest.mark.parametrize(
    "choices, opponent_card, expected_balance, expected_wins, expected_losses, expected_pushes",
    VARIANTS,
)
def test_poker_game(
    choices,
    opponent_card,
    expected_balance,
    expected_wins,
    expected_losses,
    expected_pushes,
):

    ctx = GameContext(account = Account.generate("text", 100), config = Config.default())

    poker = PokerGame(ctx)

    dealt_cards = [
        StandardCard("A", "hearts"),
        StandardCard("K", "hearts"),
        StandardCard("A", "clubs"),
        StandardCard(opponent_card, "clubs"),
        StandardCard("5", "spades"),
        StandardCard("2", "clubs"),
        StandardCard("3", "diamonds"),
        StandardCard("4", "spades"),
        StandardCard("6", "hearts"),
        StandardCard("8", "hearts"),
        StandardCard("7", "clubs"),
        StandardCard("9", "clubs"),
    ]

    patches = [
        patch("casino.games.poker.poker.cinput", side_effect=choices),
        patch("casino.games.poker.poker.clear_screen"),
        patch("casino.games.poker.poker.display_poker_topbar"),
        patch("casino.games.poker.poker.cprint"),
        patch("casino.stats.cprint"),
        patch("casino.stats.cinput", return_value=""),
        patch.object(poker_module.FULL_DECK, "draw", side_effect=dealt_cards),
        patch.object(poker_module.FULL_DECK, "generate_deck"),
    ]
    for p in patches:
        p.start()

    try:
        poker.play()
    finally:
        for p in patches:
            p.stop()

    assert poker.account.balance == expected_balance
    assert poker.stats.starting_balance == 100
    assert poker.stats.ending_balance == expected_balance
    assert poker.stats.rounds_played == 1
    assert poker.stats.wins == expected_wins
    assert poker.stats.losses == expected_losses
    assert poker.stats.pushes == expected_pushes
