#TODO: Add test cases for Uno


from types import SimpleNamespace
from unittest.mock import patch
from casino.accounts import Account
from casino.cards import UnoCard
from casino.config import Config
from casino.games.uno.uno import Uno
from casino.types import GameContext
import pytest


# (starting player hand, discard card, choices, played cards, wild color, stats)
VARIANTS = [
    (
        [("red", str(rank)) for rank in range(1, 8)],
        ("blue", "1"),
        ["p"] * 7,
        [f"red {rank}" for rank in range(1, 8)],
        None,
        (7, 7, 0),
    ),
    (
        [("red", str(rank)) for rank in range(1, 7)] + [("wild", "wild")],
        ("blue", "1"),
        ["p"] * 7,
        [f"red {rank}" for rank in range(1, 7)] + ["wild"],
        "green",
        (7, 7, 1),
    ),
    (
        [("green", str(rank)) for rank in range(1, 8)],
        ("blue", "1"),
        ["p"] * 7,
        [f"green {rank}" for rank in range(1, 8)],
        None,
        (7, 7, 0),
    ),
    (
        [("blue", str(rank)) for rank in range(1, 8)],
        ("yellow", "1"),
        ["p"] * 7,
        [f"blue {rank}" for rank in range(1, 8)],
        None,
        (7, 7, 0),
    ),
    (
        [("blue", str(rank)) for rank in range(1, 7)] + [("wild", "wild")],
        ("green", "1"),
        ["p"] * 7,
        [f"blue {rank}" for rank in range(1, 7)] + ["wild"],
        "red",
        (7, 7, 1),
    ),
    (
        [("yellow", str(rank)) for rank in range(1, 7)] + [("wild", "wild")],
        ("red", "1"),
        ["p"] * 7,
        [f"yellow {rank}" for rank in range(1, 7)] + ["wild"],
        "blue",
        (7, 7, 1),
    ),
]


@pytest.mark.parametrize(
    "player_card_data, discard_data, actions, played_cards, wild_color, expected_stats",
    VARIANTS,
)
def test_uno(
    player_card_data,
    discard_data,
    actions,
    played_cards,
    wild_color,
    expected_stats,
):

    ctx = GameContext(
        account=Account.generate("test", 100),
        config=Config.default(),
    )

    uno = Uno(ctx)

    player_cards = [UnoCard(color, rank) for color, rank in player_card_data]
    starting_discard = UnoCard(*discard_data)
    deck_cards = player_cards + [starting_discard]
    winner_calls = []

    def record_winner(winner, players):
        winner_calls.append((winner, players))

    patches = [
        patch(
            "casino.games.uno.uno.UnoDeck",
            return_value=SimpleNamespace(cards=deck_cards.copy()),
        ),
        patch(
            "casino.games.uno.uno.random.choice",
            side_effect=player_cards + [starting_discard],
        ),
        patch.object(uno.view, "display_topbar"),
        patch.object(uno.view, "prompt_num_players", return_value=1),
        patch.object(uno.view, "prompt_player_name", return_value="Test"),
        patch.object(uno.view, "player_switch_warning"),
        patch.object(uno.view, "show_turn"),
        patch.object(uno.view, "prompt_draw_or_play", side_effect=actions),
        patch.object(
            uno.view,
            "prompt_which_card",
            side_effect=played_cards,
        ),
        patch.object(uno.view, "show_winner", side_effect=record_winner),
        patch.object(uno.view, "prompt_next_player"),
    ]
    if wild_color is not None:
        patches.append(patch.object(uno.view, "prompt_wild_color", return_value=wild_color))

    for p in patches:
        p.start()

    try:
        uno.play_uno()
    finally:
        for p in reversed(patches):
            p.stop()

    assert len(winner_calls) == 1
    winner, players = winner_calls[0]
    assert winner is players[0]
    assert winner.name == "TEST"
    assert winner.hand == []
    assert winner.cards_played == expected_stats[0]
    assert winner.draws_taken == expected_stats[1]
    assert winner.wilds_played == expected_stats[2]