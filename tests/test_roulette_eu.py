from casino.games.roulette.european_roulette import (
    EuropeanRoulette,
    MULTIPLIER_LOSS,
    MULTIPLIER_EVEN_MONEY,
    MULTIPLIER_TWO_TO_ONE,
    MULTIPLIER_STRAIGHT_UP,
)
from casino.accounts import Account


def make_roulette(num_players: int = 1, balance: int = 100):
    accounts = [Account.generate(f"player{i}", balance) for i in range(num_players)]
    roulette = EuropeanRoulette(accounts)
    return roulette, accounts


# --- _compute_win_multiplier: pure function, exercised directly ------------

def test_inside_number_straight_up_win_and_loss():
    roulette, _ = make_roulette()
    assert roulette._compute_win_multiplier(
        bet_type="inside_number", bet_value="17",
        winning_number="17", winning_int=17, is_zero=False,
    ) == MULTIPLIER_STRAIGHT_UP
    assert roulette._compute_win_multiplier(
        bet_type="inside_number", bet_value="18",
        winning_number="17", winning_int=17, is_zero=False,
    ) == MULTIPLIER_LOSS


def test_outside_bets_lose_on_zero():
    roulette, _ = make_roulette()
    for bet_type, bet_value in [
        ("outside_color", "red"),
        ("outside_parity", "odd"),
        ("outside_highlow", "low"),
        ("outside_dozen", "1"),
        ("outside_column", "1"),
    ]:
        assert roulette._compute_win_multiplier(
            bet_type=bet_type, bet_value=bet_value,
            winning_number="0", winning_int=None, is_zero=True,
        ) == MULTIPLIER_LOSS


def test_outside_color():
    roulette, _ = make_roulette()
    # 32 is red on the European wheel
    assert roulette._compute_win_multiplier(
        bet_type="outside_color", bet_value="red",
        winning_number="32", winning_int=32, is_zero=False,
    ) == MULTIPLIER_EVEN_MONEY
    assert roulette._compute_win_multiplier(
        bet_type="outside_color", bet_value="black",
        winning_number="32", winning_int=32, is_zero=False,
    ) == MULTIPLIER_LOSS


def test_outside_parity():
    roulette, _ = make_roulette()
    assert roulette._compute_win_multiplier(
        bet_type="outside_parity", bet_value="even",
        winning_number="4", winning_int=4, is_zero=False,
    ) == MULTIPLIER_EVEN_MONEY
    assert roulette._compute_win_multiplier(
        bet_type="outside_parity", bet_value="odd",
        winning_number="4", winning_int=4, is_zero=False,
    ) == MULTIPLIER_LOSS


def test_outside_highlow():
    roulette, _ = make_roulette()
    assert roulette._compute_win_multiplier(
        bet_type="outside_highlow", bet_value="low",
        winning_number="18", winning_int=18, is_zero=False,
    ) == MULTIPLIER_EVEN_MONEY
    assert roulette._compute_win_multiplier(
        bet_type="outside_highlow", bet_value="low",
        winning_number="19", winning_int=19, is_zero=False,
    ) == MULTIPLIER_LOSS


def test_outside_dozen_and_column():
    roulette, _ = make_roulette()
    assert roulette._compute_win_multiplier(
        bet_type="outside_dozen", bet_value="2",
        winning_number="13", winning_int=13, is_zero=False,
    ) == MULTIPLIER_TWO_TO_ONE
    assert roulette._compute_win_multiplier(
        bet_type="outside_column", bet_value="1",
        winning_number="4", winning_int=4, is_zero=False,
    ) == MULTIPLIER_TWO_TO_ONE
    assert roulette._compute_win_multiplier(
        bet_type="outside_column", bet_value="2",
        winning_number="4", winning_int=4, is_zero=False,
    ) == MULTIPLIER_LOSS


# --- reset_round -------------------------------------------------------

def test_reset_round_clears_bets_and_winning_value():
    roulette, _ = make_roulette()
    roulette.bets["some-id"] = {"type": "inside_number", "value": "5", "amount": 10}
    roulette.winning_value = ("5", "red", 8, 30)

    roulette.reset_round()

    assert roulette.bets == {}
    assert roulette.winning_value is None


# --- payout(): end-to-end using accounts_by_id lookup -------------------

def test_payout_credits_correct_player_when_an_earlier_player_skips_betting():
    """
    European roulette's payout() already looks accounts up by id rather than
    position, so it should be unaffected by an earlier player skipping their
    bet -- this pins down that correct behavior as a regression test.
    """
    roulette, accounts = make_roulette(num_players=2, balance=100)
    skipping_player, betting_player = accounts

    betting_player.withdraw(10)
    roulette.bets[str(betting_player.aid)] = {
        "type": "outside_color", "value": "red", "amount": 10
    }
    roulette.winning_value = ("32", "red", 0, 17)  # 32 is red

    roulette.payout()

    assert skipping_player.balance == 100
    assert betting_player.balance == 110  # 90 remaining + 2x10 winnings


def test_payout_straight_up_number_pays_35_to_1():
    roulette, accounts = make_roulette(num_players=1, balance=200)
    account = accounts[0]
    account.withdraw(10)
    roulette.bets[str(account.aid)] = {
        "type": "inside_number", "value": "5", "amount": 10
    }
    roulette.winning_value = ("5", "red", 8, 30)

    roulette.payout()

    # 190 remaining + 36x10 = 550
    assert account.balance == 550


def test_payout_bet_on_unplaced_account_id_is_ignored():
    """A stale bet keyed to an id not in self.accounts should be skipped, not error."""
    roulette, accounts = make_roulette(num_players=1, balance=100)
    roulette.bets["not-a-real-account-id"] = {
        "type": "outside_color", "value": "red", "amount": 10
    }
    roulette.winning_value = ("32", "red", 0, 17)

    roulette.payout()  # should not raise

    assert accounts[0].balance == 100