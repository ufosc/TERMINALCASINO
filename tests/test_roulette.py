from unittest.mock import patch

from casino.games.roulette.roulette import Roulette, AmericanRoulette
from casino.accounts import Account
from casino.config import Config
from casino.types import GameContext


def make_roulette(num_players: int = 1, balance: int = 100):
    accounts = [Account.generate(f"player{i}", balance) for i in range(num_players)]
    roulette = AmericanRoulette(accounts)
    return roulette, accounts


def test_normalize_color():
    """Shorthand, full names, and unrecognized input for color normalization."""
    assert Roulette.normalize_color("r") == "red"
    assert Roulette.normalize_color("RED") == "red"
    assert Roulette.normalize_color("g") == "green"
    assert Roulette.normalize_color("Green") == "green"
    assert Roulette.normalize_color("b") == "black"
    assert Roulette.normalize_color("BLACK") == "black"
    # Unrecognized input is passed through unchanged
    assert Roulette.normalize_color("purple") == "purple"


def test_normalize_type():
    """Shorthand, full names, and unrecognized input for bet type normalization."""
    assert Roulette.normalize_type("c") == "color"
    assert Roulette.normalize_type("COLOR") == "color"
    assert Roulette.normalize_type("n") == "number"
    assert Roulette.normalize_type("Number") == "number"
    assert Roulette.normalize_type("garbage") == "garbage"


def test_roulette_sort_key_orders_zero_and_double_zero_first():
    """'0' and '00' should sort before all numbered slots, with '00' just after '0'."""
    values = ["17", "00", "5", "0", "32"]
    ordered = sorted(values, key=Roulette.roulette_sort_key)
    assert ordered == ["0", "00", "5", "17", "32"]


def test_reset_round_clears_bets_and_winning_value():
    roulette, _ = make_roulette(num_players=1)
    roulette.bets["some-account-id"] = {"type": "color", "value": "red", "amount": 10}
    roulette.winning_value = ("14", "red", 1, 8)

    roulette.reset_round()

    assert roulette.bets == {}
    assert roulette.winning_value is None


def test_payout_color_bet_win_pays_even_money():
    """A red/black color bet that hits should return 2x the wager (1:1 profit)."""
    roulette, accounts = make_roulette(num_players=1, balance=100)
    account = accounts[0]
    account.withdraw(20)  # simulate the withdrawal submit_bets() would have done
    roulette.bets[str(account.aid)] = {"type": "color", "value": "red", "amount": 20}
    roulette.winning_value = ("1", "red", 16, 19)

    roulette.payout()

    # Started with 100, withdrew 20 -> 80, won 2x20=40 back -> 120
    assert account.balance == 120


def test_payout_color_bet_loss_pays_nothing():
    roulette, accounts = make_roulette(num_players=1, balance=100)
    account = accounts[0]
    account.withdraw(20)
    roulette.bets[str(account.aid)] = {"type": "color", "value": "black", "amount": 20}
    roulette.winning_value = ("1", "red", 16, 19)

    roulette.payout()

    # Bet already withdrawn and never returned
    assert account.balance == 80


def test_payout_straight_number_bet_pays_35_to_1():
    roulette, accounts = make_roulette(num_players=1, balance=200)
    account = accounts[0]
    account.withdraw(10)
    roulette.bets[str(account.aid)] = {"type": "number", "value": "17", "amount": 10}
    roulette.winning_value = ("17", "black", 7, 30)

    roulette.payout()

    # 190 remaining + 36x10 = 190 + 360 = 550
    assert account.balance == 550


def test_payout_green_color_bet_pays_35_to_1():
    """
    Betting on green (0/00) is a same-odds equivalent of a straight-up number
    bet and should pay 35:1 (36x total return), matching the payout for a
    straight number bet above.
    """
    roulette, accounts = make_roulette(num_players=1, balance=200)
    account = accounts[0]
    account.withdraw(10)
    roulette.bets[str(account.aid)] = {"type": "color", "value": "green", "amount": 10}
    roulette.winning_value = ("00", "green", 16, 16)

    roulette.payout()

    assert account.balance == 550


def test_payout_credits_correct_player_when_an_earlier_player_skips_betting():
    """
    Regression test: if an earlier player declines to bet (so no entry is
    added to `self.bets` for them), payout() must still credit winnings to
    whichever account actually placed the winning bet -- not to whichever
    account happens to occupy that position in `self.accounts`.
    """
    roulette, accounts = make_roulette(num_players=2, balance=100)
    skipping_player, betting_player = accounts

    # skipping_player places no bet at all this round.
    betting_player.withdraw(10)
    roulette.bets[str(betting_player.aid)] = {
        "type": "color", "value": "red", "amount": 10
    }
    roulette.winning_value = ("1", "red", 16, 19)

    roulette.payout()

    assert skipping_player.balance == 100  # untouched
    assert betting_player.balance == 110   # 90 remaining + 2x10 winnings

# ---------------------------------------------------------------------------
# submit_bets() tests -- these use mock inputs to simulate a user typing
# answers into the game, instead of a real person at the keyboard.
# ---------------------------------------------------------------------------

ROULETTE_MODULE = "casino.games.roulette.roulette"


def run_submit_bets(roulette, accounts, inputs):
    """Run submit_bets() with fake user inputs and the screen output silenced."""
    ctx = GameContext(account=accounts[0], config=Config.default())
    with patch(f"{ROULETTE_MODULE}.cinput", side_effect=inputs), \
         patch(f"{ROULETTE_MODULE}.cprint"), \
         patch(f"{ROULETTE_MODULE}.clear_screen"), \
         patch(f"{ROULETTE_MODULE}.display_roulette_topbar"), \
         patch(f"{ROULETTE_MODULE}.sleep"), \
         patch("builtins.print"):
        return roulette.submit_bets(ctx)


def test_submit_bets_color_bet():
    """Player says yes, bets 50 on red. Bet is saved and money is withdrawn."""
    roulette, accounts = make_roulette(num_players=1, balance=100)
    account = accounts[0]

    run_submit_bets(roulette, accounts, ["y", "50", "c", "red"])

    assert roulette.bets[str(account.aid)] == {"type": "color", "value": "red", "amount": 50}
    assert account.balance == 50


def test_submit_bets_number_bet_with_shorthand():
    """Shorthand answers ('yes', 'n') work and a number bet on 00 is saved."""
    roulette, accounts = make_roulette(num_players=1, balance=100)
    account = accounts[0]

    run_submit_bets(roulette, accounts, ["yes", "10", "n", "00"])

    assert roulette.bets[str(account.aid)] == {"type": "number", "value": "00", "amount": 10}
    assert account.balance == 90


def test_submit_bets_player_declines():
    """Player says no, so no bet is saved and their balance doesn't change."""
    roulette, accounts = make_roulette(num_players=1, balance=100)

    run_submit_bets(roulette, accounts, ["n"])

    assert roulette.bets == {}
    assert accounts[0].balance == 100


def test_submit_bets_reprompts_after_invalid_inputs():
    """
    Bad answers are rejected and the player is asked again:
    a bad yes/no, a non-number bet, a bet bigger than their balance,
    a bad bet type, and a color that isn't on the wheel.
    """
    roulette, accounts = make_roulette(num_players=1, balance=100)
    account = accounts[0]
    inputs = [
        "maybe",          # invalid yes/no -> asked again
        "y", "abc",       # not a number -> starts over
        "y", "500",       # more than balance -> starts over
        "y", "10",        # valid bet
        "x", "c",         # invalid bet type, then color
        "purple", "g",    # invalid color, then green
    ]

    run_submit_bets(roulette, accounts, inputs)

    assert roulette.bets[str(account.aid)] == {"type": "color", "value": "green", "amount": 10}
    assert account.balance == 90


def test_submit_bets_skips_broke_player_and_moves_on():
    """
    Regression test: a player with 0 coins should be skipped and the next
    player should still get to bet. Previously the loop never moved past the
    broke player, so the game got stuck forever.
    """
    roulette, accounts = make_roulette(num_players=2, balance=100)
    broke_player, funded_player = accounts
    broke_player.withdraw(100)

    # If the skip message shows up more than once, the loop is stuck on the
    # broke player. Raise an error so the test fails instead of hanging.
    skip_messages = []

    def fake_cprint(message="", *args, **kwargs):
        if str(message).startswith("Skipping"):
            skip_messages.append(message)
            if len(skip_messages) > 1:
                raise RuntimeError("submit_bets() got stuck on the broke player")

    ctx = GameContext(account=accounts[0], config=Config.default())
    with patch(f"{ROULETTE_MODULE}.cinput", side_effect=["y", "10", "c", "red"]), \
         patch(f"{ROULETTE_MODULE}.cprint", side_effect=fake_cprint), \
         patch(f"{ROULETTE_MODULE}.clear_screen"), \
         patch(f"{ROULETTE_MODULE}.display_roulette_topbar"):
        roulette.submit_bets(ctx)

    assert str(broke_player.aid) not in roulette.bets
    assert roulette.bets[str(funded_player.aid)] == {"type": "color", "value": "red", "amount": 10}
    assert funded_player.balance == 90


def test_submit_bets_returns_bankrupt_when_everyone_is_broke():
    """If every player has 0 coins, submit_bets() ends the game with 'BANKRUPT'."""
    roulette, accounts = make_roulette(num_players=2, balance=0)

    result = run_submit_bets(roulette, accounts, [])

    assert result == "BANKRUPT"
    assert roulette.bets == {}
