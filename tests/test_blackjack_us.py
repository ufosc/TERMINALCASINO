from casino.games.blackjack.base import *
from casino.games.blackjack.variants.standard import *
from casino.game_types import *

#Add more tests as needed, potentially testing user inputs

def test_aces():
    """
    Tests extreme cases for having aces in your hand to ensure calculation is correct
    """
    hand = Hand()
    hand.cards.append(StandardCard(suit="hearts", rank="A"))
    hand.cards.append(StandardCard(suit="hearts", rank="A"))
    assert hand.total == 12

    hand.cards.append(StandardCard(suit="hearts", rank="A"))
    hand.cards[0].rank = 6
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

    hand.cards[0].rank = 10
    hand.cards[1].rank = 10
    assert hand.total == 21

    hand.cards.pop(0)
    assert hand.total == 21

def test_bust():
    """
    Tests scenarios in which the dealer or player busts.
    """
    ctx = GameContext(
        account=Account.generate('test', 100),
        config=Config.default()
    )
    blackjack = StandardBlackjack(ctx)
    player = blackjack.player

    # Case 1: Player busts and loses
    hand = Hand(bet=10)
    player.hands = [hand]
    blackjack.deal_cards()

    while hand.total <= 21:
        hand.cards.append(StandardCard(suit="hearts", rank="K"))

    blackjack.check_win()

    assert hand.result_key == "player_bust"
    assert hand.payout_amount == 0

    # Case 2: Dealer busts and player wins
    hand = Hand(bet=10)
    player.hands = [hand]
    blackjack.deal_cards()

    hand.cards = [
        StandardCard(suit="hearts", rank="10"),
        StandardCard(suit="hearts", rank="9")
    ]
    blackjack.dealer_hand.cards = [
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank="K")
    ]

    blackjack.check_win()

    assert hand.result_key == "dealer_bust"
    assert hand.payout_amount == 20

    # Case 3: Player has 10-10-A and dealer busts
    hand = Hand(bet=10)
    player.hands = [hand]
    blackjack.deal_cards()

    hand.cards = [
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank="A")
    ]
    blackjack.dealer_hand.cards = [
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank="K")
    ]

    blackjack.check_win()

    assert hand.total == 21
    assert hand.result_key == "dealer_bust"

    balance = player.account.balance
    blackjack.payout()

    assert player.account.balance == balance + hand.bet * 2

def test_payout():
    """
    Tests payouts for normal wins, losses, and ties.
    """
    ctx = GameContext(
        account=Account.generate('test', 100),
        config=Config.default()
    )
    blackjack = StandardBlackjack(ctx)
    player = blackjack.player

    # Case 1: Player wins (20 vs 19)
    hand = Hand(bet=10)
    player.hands = [hand]
    hand.cards = [
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank="K")
    ]
    blackjack.dealer_hand.cards = [
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank=9)
    ]

    blackjack.check_win()
    assert hand.result_key == "player_wins"

    balance = player.account.balance
    blackjack.payout()
    assert player.account.balance == balance + 20

    # Case 2: Dealer wins (21 vs 20)
    hand = Hand(bet=10)
    player.hands = [hand]
    hand.cards = [
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank="K")
    ]
    blackjack.dealer_hand.cards = [
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank=9),
        StandardCard(suit="hearts", rank=2)
    ]

    blackjack.check_win()
    assert hand.result_key == "dealer_wins"

    balance = player.account.balance
    blackjack.payout()
    assert player.account.balance == balance

    # Case 3: Tie (20 vs 20)
    hand = Hand(bet=10)
    player.hands = [hand]
    hand.cards = [
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank="K")
    ]
    blackjack.dealer_hand.cards = [
        StandardCard(suit="hearts", rank="Q"),
        StandardCard(suit="hearts", rank="Q")
    ]

    blackjack.check_win()
    assert hand.result_key == "tie"

    balance = player.account.balance
    blackjack.payout()
    assert player.account.balance == balance + 10

def test_blackjack_payout():
    """
    Tests blackjack payouts and comparisons against regular 21.
    """
    ctx = GameContext(
        account=Account.generate("test", 100),
        config=Config.default()
    )
    blackjack = StandardBlackjack(ctx)
    player = blackjack.player

    def check_case(player_ranks, dealer_ranks, expected_result, expected_payout):
        hand = Hand(bet=10)
        player.hands = [hand]

        hand.cards = [
            StandardCard(suit="hearts", rank=rank)
            for rank in player_ranks
        ]
        blackjack.dealer_hand.cards = [
            StandardCard(suit="hearts", rank=rank)
            for rank in dealer_ranks
        ]

        blackjack.check_win()

        assert hand.result_key == expected_result
        assert hand.payout_amount == expected_payout

        balance = player.account.balance
        blackjack.payout()
        assert player.account.balance == balance + expected_payout

    # Case 1: Both have blackjack -> tie
    check_case(
        ["A", "K"], ["A", "Q"],
        "blackjack_tie", 10
    )

    # Case 2: Player blackjack, dealer below 21 -> blackjack win
    check_case(
        ["A", "K"], ["K", "9"],
        "player_blackjack", 25
    )

    # Case 3: Player blackjack, dealer has 21 with 3 cards
    check_case(
        ["A", "K"], ["K", "5", "6"],
        "player_blackjack", 25
    )

    # Case 4: Both have regular 21 -> tie
    check_case(
        ["K", "5", "6"], ["K", "5", "6"],
        "tie", 10
    )

    # Case 5: Player regular 21, dealer blackjack -> loss
    check_case(
        ["K", "5", "6"], ["A", "K"],
        "dealer_blackjack", 0
    )

def test_dealer_decision():
    """
    Tests the dealer's decisions in certain situations
    Dealer total is less than or equal to 16: Hit
    Dealer total is greater than or equal to 17: Stand
    Edge case: Dealer stands on Ace + 6
    """
    ctx = GameContext(
        account=Account.generate("test", 100),
        config=Config.default()
    )
    blackjack = StandardBlackjack(ctx)
    dealer = blackjack.dealer_hand

    player_hand = Hand()
    player_hand.cards = [
        StandardCard(suit="spades", rank="10"),
        StandardCard(suit="spades", rank="8")
    ]

    blackjack.player.hands = [player_hand]

    # Case 1: Dealer has 18 -> Stand
    dealer.cards = [
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank=8)
    ]
    blackjack.dealer_draw()
    assert len(dealer.cards) == 2

    # Case 2: Dealer has 16 -> Hit
    dealer.cards = [
        StandardCard(suit="hearts", rank="K"),
        StandardCard(suit="hearts", rank=6)
    ]
    blackjack.dealer_draw()
    assert len(dealer.cards) >= 3

    # Case 3: Dealer has 17(A + 6) -> Stand
    dealer.cards = [
        StandardCard(suit="hearts", rank="A"),
        StandardCard(suit="hearts", rank=6)
    ]
    blackjack.dealer_draw()
    assert len(dealer.cards) == 2
