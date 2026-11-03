from collections.abc import Iterable
from unittest.mock import patch

import pytest

from casino.accounts import Account
from casino.cards import StandardCard
from casino.config import Config
from casino.games.blackjack.hand import Hand
from casino.games.blackjack.variants.standard import StandardBlackjack
from casino.types import GameContext


BET = 10
POST_BET_BALANCE = 90


def make_blackjack(
    player_ranks: Iterable[str] = (),
    dealer_ranks: Iterable[str] = (),
) -> StandardBlackjack:
    account = Account.generate("test", POST_BET_BALANCE)
    blackjack = StandardBlackjack(
        GameContext(account=account, config=Config.default())
    )
    player_hand = Hand(bet=BET)
    player_hand.cards.extend(
        StandardCard(rank, "hearts") for rank in player_ranks
    )
    blackjack.player.hands = [player_hand]
    blackjack.dealer_hand = Hand()
    blackjack.dealer_hand.cards.extend(
        StandardCard(rank, "spades") for rank in dealer_ranks
    )
    return blackjack


def test_aces():
    """Cover the original ace-total edge cases."""
    hand = Hand()
    hand.cards.extend(
        [StandardCard("A", "hearts"), StandardCard("A", "hearts")]
    )
    assert hand.total == 12

    hand.cards.append(StandardCard("A", "hearts"))
    hand.cards[0].rank = "6"
    assert hand.total == 18
    hand.cards.pop(1)
    assert hand.total == 17

    hand.cards[0].rank = "A"
    total = 12
    while total < 21:
        hand.cards.append(StandardCard("A", "hearts"))
        total += 1
        assert hand.total == total

    while len(hand.cards) > 3:
        hand.cards.pop()
    hand.cards[0].rank = "10"
    hand.cards[1].rank = "10"
    assert hand.total == 21
    hand.cards.pop(0)
    assert hand.total == 21


@pytest.mark.parametrize(
    ("player_ranks", "dealer_ranks", "result", "balance"),
    [
        (["10", "8", "4"], ["10", "8"], "player_bust", POST_BET_BALANCE),
        (["10", "8"], ["K", "8", "5"], "dealer_bust", 110),
        (["7", "7", "7"], ["K", "8", "5"], "dealer_bust", 110),
    ],
    ids=["player-busts", "dealer-busts", "three-card-21-beats-dealer-bust"],
)
def test_bust_outcomes_and_payouts(player_ranks, dealer_ranks, result, balance):
    blackjack = make_blackjack(player_ranks, dealer_ranks)

    blackjack.check_win()
    hand = blackjack.player.hands[0]
    assert hand.result_key == result
    assert "bust" in hand.outcome_msg.lower()

    blackjack.payout()
    assert blackjack.player.account.balance == balance


@pytest.mark.parametrize(
    ("player_ranks", "dealer_ranks", "result", "balance"),
    [
        (["10", "10"], ["10", "9"], "player_wins", 110),
        (["10", "9"], ["10", "10"], "dealer_wins", POST_BET_BALANCE),
        (["10", "8"], ["10", "8"], "tie", 100),
    ],
    ids=["regular-win", "regular-loss", "regular-tie"],
)
def test_payout(player_ranks, dealer_ranks, result, balance):
    blackjack = make_blackjack(player_ranks, dealer_ranks)

    blackjack.check_win()
    hand = blackjack.player.hands[0]
    assert hand.result_key == result

    blackjack.payout()
    assert blackjack.player.account.balance == balance


@pytest.mark.parametrize(
    ("player_ranks", "dealer_ranks", "result", "player_bj", "dealer_bj", "balance"),
    [
        (["A", "K"], ["A", "10"], "blackjack_tie", True, True, 100),
        (["A", "K"], ["10", "A", "A"], "player_blackjack", True, False, 115),
        (["A", "K"], ["7", "7", "7"], "player_blackjack", True, False, 115),
        (["7", "7", "7"], ["10", "5", "6"], "tie", False, False, 100),
        (["7", "7", "7"], ["A", "K"], "dealer_blackjack", False, True, POST_BET_BALANCE),
    ],
    ids=[
        "both-natural-blackjack",
        "player-natural-dealer-non-blackjack",
        "player-natural-dealer-three-card-21",
        "both-three-card-21",
        "dealer-natural-player-three-card-21",
    ],
)
def test_blackjack_payout(
    player_ranks, dealer_ranks, result, player_bj, dealer_bj, balance
):
    blackjack = make_blackjack(player_ranks, dealer_ranks)

    with patch("casino.games.blackjack.variants.standard.sleep"), patch(
        "casino.games.blackjack.variants.standard.cprint"
    ):
        blackjack.blackjack_check()

    hand = blackjack.player.hands[0]
    assert hand.is_blackjack is player_bj
    assert blackjack.dealer_hand.is_blackjack is dealer_bj

    blackjack.check_win()
    assert hand.result_key == result

    blackjack.payout()
    assert blackjack.player.account.balance == balance


@pytest.mark.parametrize(
    ("dealer_ranks", "draw_rank", "expected_ranks"),
    [
        (["10", "6"], "2", ["10", "6", "2"]),
        (["10", "7"], "5", ["10", "7"]),
        (["A", "6"], "5", ["A", "6"]),
    ],
    ids=["hits-below-17", "stands-on-hard-17", "stands-on-soft-17"],
)
def test_dealer_decision(dealer_ranks, draw_rank, expected_ranks):
    blackjack = make_blackjack(["10", "8"], dealer_ranks)
    blackjack.deck.cards = [StandardCard(draw_rank, "clubs")]

    with patch.object(blackjack.view, "render_table"), patch(
        "casino.games.blackjack.variants.standard.sleep"
    ), patch("casino.games.blackjack.variants.standard.cprint"):
        blackjack.dealer_draw()

    assert [card.rank for card in blackjack.dealer_hand.cards] == expected_ranks
