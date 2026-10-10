
from types import SimpleNamespace
from unittest.mock import patch

from casino.games.uno.player import Player


def make_card(color, rank):
    return SimpleNamespace(color=color, rank=rank)


def test_draw_card():
    player = Player(1, "Alex")
    card = make_card("red", "5")
    deck = [card]

    with patch("casino.games.uno.player.random.choice", return_value=card):
        drawn = player.draw(deck)

    assert drawn is card
    assert player.hand == [card]
    assert deck == []
    assert player.draws_taken == 1


def test_play_card():
    player = Player(1, "Alex")
    card = make_card("blue", "skip")
    player.hand.append(card)

    result = player.play_card(card)

    assert result is card
    assert player.hand == []
    assert player.cards_played == 1
    assert player.skips_played == 1


def test_play_wild_draw_four():
    player = Player(1, "Alex")
    card = make_card("wild", "wild_draw_4")
    player.hand.append(card)

    player.play_card(card)

    assert player.draw4_played == 1
    assert player.cards_played == 1


def test_playable_cards():
    player = Player(1, "Alex")
    red_card = make_card("red", "3")
    matching_rank = make_card("blue", "5")
    matching_color = make_card("red", "8")
    wild = make_card("wild", "wild")
    invalid = make_card("green", "9")

    player.hand = [
        red_card, matching_rank, matching_color, wild, invalid
    ]

    current_card = make_card("red", "5")
    result = player.playable_cards(current_card)

    assert result == [red_card, matching_rank, matching_color, wild]
