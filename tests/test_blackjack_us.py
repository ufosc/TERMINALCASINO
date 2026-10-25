"""
Unit tests for U.S. (standard) Blackjack.

Blackjack is single-player: the table has one `Player` (`blackjack.player`)
who owns a list of `Hand` objects, and the dealer has a single `Hand`
(`blackjack.dealer_hand`). The game stores each round's outcome on the hand
itself (`hand.result_key`, `hand.outcome_msg`, `hand.payout_amount`).
"""

import pytest

from casino.accounts import Account
from casino.cards import StandardCard
from casino.config import Config
from casino.types import GameContext
from casino.games.blackjack.constants import BLACKJACK_MULTIPLIER
from casino.games.blackjack.hand import Hand
from casino.games.blackjack.variants.standard import StandardBlackjack

BET = 10


def make_hand(*ranks, bet=BET) -> Hand:
    """Builds a hand of hearts with the given ranks, e.g. make_hand("K", "A")."""
    hand = Hand(bet=bet)
    for rank in ranks:
        hand.cards.append(StandardCard(suit="hearts", rank=str(rank)))
    return hand


@pytest.fixture
def blackjack(monkeypatch):
    """A fresh game with 100 chips. Skips the dramatic pauses so tests stay fast."""
    monkeypatch.setattr("casino.games.blackjack.variants.standard.sleep", lambda *_: None)
    ctx = GameContext(account=Account.generate("test", 100), config=Config.default())
    return StandardBlackjack(ctx)


def settle(blackjack, player_ranks, dealer_ranks) -> Hand:
    """
    Gives the player and dealer the given cards, then decides who won.
    Returns the player's hand, which holds the result.
    """
    hand = make_hand(*player_ranks)
    blackjack.player.hands = [hand]
    blackjack.dealer_hand = make_hand(*dealer_ranks, bet=0)
    blackjack.blackjack_check()
    blackjack.check_win()
    return hand


def paid(blackjack) -> int:
    """Runs payout() and returns how many chips the player received."""
    before = blackjack.player.account.balance
    blackjack.payout()
    return blackjack.player.account.balance - before


def test_aces():
    """
    Tests extreme cases for having aces in your hand to ensure calculation is correct
    """
    hand = make_hand("A", "A")
    assert hand.total == 12
    hand.cards.append(StandardCard(suit="hearts", rank="A"))
    hand.cards[0].rank = "6"
    assert hand.total == 18
    hand.cards.pop(1)
    assert hand.total == 17
    hand.cards[0].rank = "A"
    total = 12
    while total < 21:
        hand.cards.append(StandardCard(suit="hearts", rank="A"))
        total += 1
        assert hand.total == total
    while len(hand.cards) > 3:
        hand.cards.pop()
    hand.cards[0].rank = "10"
    hand.cards[1].rank = "10"
    assert hand.total == 21
    hand.cards.pop(0)
    assert hand.total == 21


def test_bust(blackjack):
    """
    tests scenarios in which the dealer or player busts
    """
    # Player busts and loses (K + K + K = 30)
    hand = settle(blackjack, ["K", "K", "K"], ["K", "7"])
    assert hand.result_key == "player_bust"
    assert "BUSTED" in hand.outcome_msg
    assert paid(blackjack) == 0

    # Dealer busts and loses (K + 6 + K = 26)
    hand = settle(blackjack, ["K", "8"], ["K", "6", "K"])
    assert hand.result_key == "dealer_bust"
    assert "BUSTED" in hand.outcome_msg
    assert paid(blackjack) == BET * 2

    # Player has K-K-A (21, but not a blackjack) and the dealer busts
    hand = settle(blackjack, ["K", "K", "A"], ["K", "K", "K"])
    assert hand.result_key == "dealer_bust"
    assert "BUSTED" in hand.outcome_msg
    # We will test the payout in this scenario as well
    assert paid(blackjack) == BET * 2


def test_payout(blackjack):
    """
    Tests the changes in the user's account for every standard scenario
    Normal win: profit = amount bet
    Push: profit = 0
    Loss: profit = -bet
    """
    # Case 1: the player beats the dealer normally (20 vs 19)
    hand = settle(blackjack, ["K", "K"], ["K", "9"])
    assert hand.result_key == "player_wins"
    # You get back the original money you bet plus the profit
    assert paid(blackjack) == BET * 2

    # Case 2: the dealer beats the player normally (20 vs 21)
    hand = settle(blackjack, ["10", "10"], ["10", "9", "2"])
    assert hand.result_key == "dealer_wins"
    # You lost the amount you bet already, so nothing comes back
    assert paid(blackjack) == 0

    # Case 3: Ties (20 vs 20)
    hand = settle(blackjack, ["K", "K"], ["K", "K"])
    assert hand.result_key == "tie"
    # The bet is returned in the case of a tie
    assert paid(blackjack) == BET


def test_blackjack_payout(blackjack):
    """
    Tests the wins/payouts for every blackjack scenario
    Both get blackjack round 1: Tie
    Player gets blackjack and dealer does not: Blackjack win (profit = 1.5*amount bet)
    Player gets blackjack round 1 and dealer has 21 in round 2: Blackjack win
    Player gets 21 in round 2 and dealer has blackjack: Loss
    Both player and dealer have 21 but neither have blackjack: Tie
    """
    # Case 1: Both the dealer and the player get blackjack
    hand = settle(blackjack, ["A", "K"], ["A", "10"])
    assert hand.is_blackjack and blackjack.dealer_hand.is_blackjack
    assert hand.result_key == "blackjack_tie"
    assert paid(blackjack) == BET

    # Case 2: The player gets blackjack and the dealer does not (10 + A + A = 12)
    hand = settle(blackjack, ["A", "K"], ["10", "A", "A"])
    assert hand.is_blackjack and not blackjack.dealer_hand.is_blackjack
    assert hand.result_key == "player_blackjack"
    assert paid(blackjack) == BET * (1 + BLACKJACK_MULTIPLIER)

    # Case 3: Player has blackjack, dealer 21 with more than 2 cards
    hand = settle(blackjack, ["A", "K"], ["10", "10", "A"])
    assert hand.is_blackjack and not blackjack.dealer_hand.is_blackjack
    assert hand.result_key == "player_blackjack"
    assert paid(blackjack) == BET * (1 + BLACKJACK_MULTIPLIER)

    # Case 4: Both dealer and player have 21 but more than 2 cards
    hand = settle(blackjack, ["K", "K", "A"], ["10", "10", "A"])
    assert not (hand.is_blackjack or blackjack.dealer_hand.is_blackjack)
    assert hand.result_key == "tie"
    assert paid(blackjack) == BET

    # Case 5: Player has 21 but dealer has blackjack
    hand = settle(blackjack, ["K", "K", "A"], ["A", "Q"])
    assert not hand.is_blackjack and blackjack.dealer_hand.is_blackjack
    assert hand.result_key == "dealer_blackjack"
    assert paid(blackjack) == 0


def test_dealer_decision(blackjack):
    """
    Tests the dealer's decisions in certain situations
    Dealer total is less than or equal to 16: Hit
    Dealer total is greater than or equal to 17: Stand
    Edge case: Dealer stands on Ace + 6
    """
    # The dealer only draws while the player still has a live hand
    blackjack.player.hands = [make_hand("10", "8")]
    dealer = blackjack.dealer_hand
    dealer.cards.append(StandardCard(suit="hearts", rank="K"))
    dealer.cards.append(StandardCard(suit="hearts", rank="8"))
    blackjack.dealer_draw()
    assert len(dealer.cards) == 2
    dealer.cards[1].rank = "6"
    blackjack.dealer_draw()
    assert len(dealer.cards) == 3
    dealer.cards.pop()
    dealer.cards[0].rank = "A"
    blackjack.dealer_draw()
    assert len(dealer.cards) == 2
