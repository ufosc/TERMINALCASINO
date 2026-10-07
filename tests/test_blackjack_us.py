from unittest.mock import patch

from casino.accounts import Account
from casino.cards import StandardCard
from casino.config import Config
from casino.games.blackjack.hand import Hand
from casino.games.blackjack.variants.standard import StandardBlackjack
from casino.types import GameContext


def make_blackjack(balance: int = 90) -> StandardBlackjack:
    context = GameContext(
        account=Account.generate("test", balance),
        config=Config.default(),
    )
    return StandardBlackjack(context)


def add_cards(hand: Hand, *ranks: str) -> None:
    hand.cards.extend(StandardCard(rank=rank, suit="hearts") for rank in ranks)


def test_aces() -> None:
    hand = Hand()
    add_cards(hand, "A", "A")
    assert hand.total == 12

    add_cards(hand, "A")
    assert hand.total == 13

    hand.cards[0].rank = "6"
    assert hand.total == 18

    hand.cards.pop(1)
    assert hand.total == 17


def test_bust() -> None:
    player_bust_game = make_blackjack()
    player_hand = Hand(bet=10)
    add_cards(player_hand, "10", "9", "4")
    player_bust_game.player.hands = [player_hand]
    add_cards(player_bust_game.dealer_hand, "10", "7")

    player_bust_game.check_win()
    player_bust_game.payout()

    assert player_hand.result_key == "player_bust"
    assert player_bust_game.context.account.balance == 90
    assert player_bust_game.stats.losses == 1

    dealer_bust_game = make_blackjack()
    player_hand = Hand(bet=10)
    add_cards(player_hand, "10", "8")
    dealer_bust_game.player.hands = [player_hand]
    add_cards(dealer_bust_game.dealer_hand, "10", "8", "5")

    dealer_bust_game.check_win()
    dealer_bust_game.payout()

    assert player_hand.result_key == "dealer_bust"
    assert dealer_bust_game.context.account.balance == 110
    assert dealer_bust_game.stats.wins == 1


def test_payout() -> None:
    winning_game = make_blackjack()
    winning_hand = Hand(bet=10)
    add_cards(winning_hand, "10", "8")
    winning_game.player.hands = [winning_hand]
    add_cards(winning_game.dealer_hand, "10", "7")
    winning_game.check_win()
    winning_game.payout()

    assert winning_hand.result_key == "player_wins"
    assert winning_game.context.account.balance == 110

    losing_game = make_blackjack()
    losing_hand = Hand(bet=10)
    add_cards(losing_hand, "10", "8")
    losing_game.player.hands = [losing_hand]
    add_cards(losing_game.dealer_hand, "10", "K")
    losing_game.check_win()
    losing_game.payout()

    assert losing_hand.result_key == "dealer_wins"
    assert losing_game.context.account.balance == 90

    push_game = make_blackjack()
    push_hand = Hand(bet=10)
    add_cards(push_hand, "10", "8")
    push_game.player.hands = [push_hand]
    add_cards(push_game.dealer_hand, "9", "9")
    push_game.check_win()
    push_game.payout()

    assert push_hand.result_key == "tie"
    assert push_game.context.account.balance == 100


def test_blackjack_payout() -> None:
    push_game = make_blackjack()
    push_hand = Hand(bet=10)
    add_cards(push_hand, "A", "K")
    push_game.player.hands = [push_hand]
    add_cards(push_game.dealer_hand, "A", "10")
    push_game.blackjack_check()
    push_game.check_win()
    push_game.payout()

    assert push_hand.result_key == "blackjack_tie"
    assert push_game.context.account.balance == 100

    win_game = make_blackjack()
    win_hand = Hand(bet=10)
    add_cards(win_hand, "A", "K")
    win_game.player.hands = [win_hand]
    add_cards(win_game.dealer_hand, "10", "8", "3")
    win_game.blackjack_check()
    win_game.check_win()
    win_game.payout()

    assert win_hand.result_key == "player_blackjack"
    assert win_game.context.account.balance == 115


def test_dealer_decision() -> None:
    game = make_blackjack()
    player_hand = Hand(bet=10)
    add_cards(player_hand, "10", "8")
    game.player.hands = [player_hand]

    add_cards(game.dealer_hand, "10", "6")
    game.deck.cards = [StandardCard("2", "clubs")]
    with (
        patch.object(game.view, "render_table"),
        patch("casino.games.blackjack.variants.standard.sleep"),
    ):
        game.dealer_draw()
    assert game.dealer_hand.total == 18

    game.dealer_hand = Hand()
    add_cards(game.dealer_hand, "A", "6")
    with (
        patch.object(game.view, "render_table"),
        patch("casino.games.blackjack.variants.standard.sleep"),
    ):
        game.dealer_draw()
    assert game.dealer_hand.total == 17
    assert len(game.dealer_hand.cards) == 2


def main() -> None:
    test_aces()
    test_bust()
    test_payout()
    test_blackjack_payout()
    test_dealer_decision()
    print("U.S. blackjack checks passed.")


if __name__ == "__main__":
    main()
