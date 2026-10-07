#TODO: Add test cases for slots
from unittest.mock import patch
from casino.accounts import Account
from casino.config import Config
from casino.games.slots.variants.standard import StandardSlots
from casino.games.slots.variants.expanded import ExpandedSlots
from casino.types import GameContext
import pytest

# (game class, scripted input, deterministic result, RNG outcome, balance, bet)
VARIANTS = [
    (StandardSlots, ["10", "q"], ("A", "A", "A"), 0.1, 115, 10),
    (StandardSlots, ["10", "q"], ("A", "B", "C"), 0.9, 90, 10),
    (StandardSlots, ["10", "q"], ("D", "D", "D"), 0.01, 150, 10),
    (
        ExpandedSlots,
        ["2,2,2", "q"],
        (("D", "D", "D"), ("A", "B", "C"), ("B", "C", "D")),
        None,
        104,
        (2, 2, 2),
    ),
    (
        ExpandedSlots,
        ["2,2,2", "q"],
        (("A", "B", "C"), ("B", "C", "D"), ("C", "D", "A")),
        None,
        94,
        (2, 2, 2),
    ),
    (
        ExpandedSlots,
        ["1,1,1", "q"],
        (("D", "D", "D"), ("A", "B", "C"), ("B", "C", "D")),
        None,
        102,
        (1, 1, 1),
    ),
]

@pytest.mark.parametrize(
    "variant, inputs, result, random_outcome, expected_balance, expected_bet",
    VARIANTS,
)
def test_slot(variant, inputs, result, random_outcome, expected_balance, expected_bet):

    ctx = GameContext(
        account=Account.generate("test", 100),
        config=Config.default(),
    )

    var_inst = variant(ctx)

    patches = [
        patch.object(var_inst.view, "clear_and_topbar"),
        patch.object(var_inst.view, "show_payout_legend"),
        patch.object(var_inst.view, "announce"),
        patch.object(var_inst.view, "prompt"),
        patch.object(var_inst, "spin_animation"),
        patch.object(var_inst, "render"),
    ]

    patches[3] = patch.object(var_inst.view, "prompt", side_effect=inputs)
    patches[5] = patch.object(var_inst, "random_result", return_value=result)

    if isinstance(var_inst, StandardSlots):
        patches.extend([
            patch("casino.games.slots.variants.standard.random.random", return_value=random_outcome),
            patch("casino.games.slots.variants.standard.random.randint", return_value=0),
        ])

    for p in patches:
        p.start()

    try:
        status = var_inst.play_round()

    finally:
        for p in reversed(patches):
            p.stop()

    assert status == "EXIT"
    assert ctx.account.balance == expected_balance
    assert var_inst.bet == expected_bet
    assert var_inst.stats.starting_balance == 100
    assert var_inst.stats.ending_balance == ctx.account.balance
    assert var_inst.stats.rounds_played == 1
    expected_won = expected_balance > var_inst.stats.starting_balance
    assert var_inst.stats.wins == int(expected_won)
    assert var_inst.stats.losses == int(not expected_won)