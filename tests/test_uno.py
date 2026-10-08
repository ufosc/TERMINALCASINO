from casino.games.uno.uno import *
from casino.game_types import *
import pytest

def test_playable_cards():
    """
    Tests that player can play a card of the same color
    """
    ctx = GameContext(account=Account.generate('test', 100), config=Config.default())
    uno = Uno(ctx)
    player = Player(0, "Test Player")

    # Digits
    player.draw([UnoCard("blue", "0")])
    player.draw([UnoCard("green", "3")])
    player.draw([UnoCard("red", "9")])
    player.draw([UnoCard("yellow", "2")])

    # Tests
    assert(player.playable_cards(UnoCard("red", "8")) == [UnoCard("red", "9")]) # Same color different digit
    assert(player.playable_cards(UnoCard("red", "9")) == [UnoCard("red", "9")]) # Same color same digit
    assert(player.playable_cards(UnoCard("red", "3")) == [UnoCard("green", "3"), UnoCard("red", "9")]) # Matching digits
    assert(player.playable_cards(UnoCard("yellow", "9")) == [UnoCard("red", "9"), UnoCard("yellow", "2")])

    # Test Wilds
    player.draw([UnoCard("wild", "wild")])
    assert(player.playable_cards(UnoCard("red", "8")) == [UnoCard("red", "9"), UnoCard("wild", "wild")]) # Can play wild on red
    assert(player.playable_cards(UnoCard("blue", "8")) == [UnoCard("blue", "0"), UnoCard("wild", "wild")]) # Can play wild on blue
    assert(player.playable_cards(UnoCard("green", "8")) == [UnoCard("green", "3"), UnoCard("wild", "wild")]) # Can play wild on green
    assert(player.playable_cards(UnoCard("yellow", "8")) == [UnoCard("yellow", "2"), UnoCard("wild", "wild")]) # Can play wild on yellow
    assert(player.playable_cards(UnoCard("red", "wild")) == [UnoCard("red", "9"), UnoCard("wild", "wild")]) # Can play red on red wild (needs fixing)
    assert(player.playable_cards(UnoCard("blue", "wild")) == [UnoCard("blue", "0"), UnoCard("wild", "wild")]) # Can play blue on blue wild (needs fixing)
    assert(player.playable_cards(UnoCard("green", "wild")) == [UnoCard("green", "3"), UnoCard("wild", "wild")]) # Can play green on green wild (needs fixing)
    assert(player.playable_cards(UnoCard("yellow", "wild")) == [UnoCard("yellow", "2"), UnoCard("wild", "wild")]) # Can play yellow on yellow wild (needs fixing)

def test_player_draw():
    """
    Tests that players drawing is correctly handled
    """
    ctx = GameContext(account=Account.generate('test', 100), config=Config.default())
    uno = Uno(ctx)
    player = Player(0, "Test Player")
    deck = [
        UnoCard("red", "9"),
        UnoCard("blue", "2"),
        UnoCard("green", "0"),
        UnoCard("wild", "wild"),
        UnoCard("wild", "wild_draw_4"),
        UnoCard("red", "draw_2"),
        UnoCard("blue", "draw_2"),
        UnoCard("yellow", "3")
    ]

    # Draw cards as the player and ensure properly subtracted
    assert (len(deck) == 8)

    while len(deck):
        # Ensure subtraction
        og_deck = deck.copy()
        og_hand = player.hand.copy()
        drawn = player.draw(deck)
        assert (len(deck) == len(og_deck) - 1)
        assert (og_deck.count(drawn) == deck.count(drawn) + 1)

        # Ensure player received said card
        assert (og_hand.count(drawn) == player.hand.count(drawn) - 1)
        