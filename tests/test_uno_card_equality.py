
from casino.cards import UnoCard


def test_uno_card_equality():
    assert UnoCard("red", "5") == UnoCard("red", "5")
    assert UnoCard("red", "5") != UnoCard("blue", "5")
    assert UnoCard("red", "5") != UnoCard("red", "7")


def test_uno_card_invalid_comparison():
    card = UnoCard("red", "5")

    assert card != None
    assert card != "red"
    assert card != 5
