"""
Unit tests for casino/games/poker/poker.py
"""

from unittest.mock import patch

import pytest

from casino.accounts import Account
from casino.cards import StandardCard
from casino.config import Config
from casino.types import GameContext
from casino.games.poker.poker import (
    FULL_DECK,
    INVALID_YES_OR_NO_MSG,
    NO_FUNDS_MSG,
    PokerGame,
    SECURITY_MSG,
    evaluate_hand,
    get_and_validate_raise_amount,
    get_card_value,
    get_partial_hand_score,
    hand_name,
    hand_score,
)


MOD = "casino.games.poker.poker"
SUITS = {"C": "clubs", "D": "diamonds", "H": "hearts", "S": "spades"}


def cards(spec: str) -> list[StandardCard]:
    """
    Build cards from shorthand: rank followed by suit letter.
    Example: cards("AH 10S 2C") -> [A of hearts, 10 of spades, 2 of clubs]
    """
    return [StandardCard(token[:-1], SUITS[token[-1]]) for token in spec.split()]


# ---------------------------------------------------------------------------
# get_card_value
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rank, expected", [
    ("J", 11), ("Q", 12), ("K", 13), ("A", 14),
])
def test_card_value_face_cards(rank, expected):
    assert get_card_value(rank) == expected


@pytest.mark.parametrize("rank, expected", [("2", 2), ("9", 9), ("10", 10)])
def test_card_value_numeric_strings(rank, expected):
    assert get_card_value(rank) == expected


def test_card_value_int_passthrough():
    assert get_card_value(7) == 7


# ---------------------------------------------------------------------------
# evaluate_hand: one clear example per category
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("spec, expected", [
    ("9H 8H 7H 6H 5H",  9),  # Straight Flush
    ("KS KH KD KC 3H",  8),  # Four of a Kind
    ("QS QH QD 4C 4H",  7),  # Full House
    ("2D 7D 9D JD KD",  6),  # Flush
    ("5C 6D 7H 8S 9C",  5),  # Straight
    ("8S 8H 8D KC 2H",  4),  # Three of a Kind
    ("JS JH 4D 4C AH",  3),  # Two Pair
    ("10S 10H 3D 7C KH", 2), # One Pair
    ("2S 5H 9D JC KH",  1),  # High Card
])
def test_evaluate_hand_each_category(spec, expected):
    assert evaluate_hand(cards(spec)) == expected


def test_evaluate_hand_order_independent():
    """Card order must not change the result."""
    assert evaluate_hand(cards("9C 5D 7H 6S 8C")) == 5
    assert evaluate_hand(cards("4H QS 4C QH QD")) == 7


# ---------------------------------------------------------------------------
# evaluate_hand: straight edge cases
# ---------------------------------------------------------------------------

def test_wheel_is_straight():
    """A-2-3-4-5: the ace plays low."""
    assert evaluate_hand(cards("AS 2D 3H 4C 5S")) == 5


def test_broadway_is_straight():
    """10-J-Q-K-A: the ace plays high."""
    assert evaluate_hand(cards("10S JD QH KC AS")) == 5


def test_wraparound_is_not_straight():
    """Q-K-A-2-3 wraps around the ace and is not a straight."""
    assert evaluate_hand(cards("QS KD AH 2C 3S")) == 1


@pytest.mark.parametrize("spec", ["2S 3D 4H 5C 7S", "AS 2D 3H 4C 6S"])
def test_gap_is_not_straight(spec):
    assert evaluate_hand(cards(spec)) == 1


def test_royal_flush_is_straight_flush():
    assert evaluate_hand(cards("10H JH QH KH AH")) == 9


def test_wheel_straight_flush():
    assert evaluate_hand(cards("AC 2C 3C 4C 5C")) == 9


# ---------------------------------------------------------------------------
# evaluate_hand: category precedence
# ---------------------------------------------------------------------------

def test_flush_beats_straight():
    flush = evaluate_hand(cards("2H 6H 9H JH KH"))
    straight = evaluate_hand(cards("5C 6D 7H 8S 9C"))
    assert flush > straight


def test_full_house_beats_flush():
    full_house = evaluate_hand(cards("3S 3H 3D 9C 9H"))
    flush = evaluate_hand(cards("2H 6H 9H JH KH"))
    assert full_house > flush


def test_straight_flush_beats_four_of_a_kind():
    straight_flush = evaluate_hand(cards("5S 6S 7S 8S 9S"))
    quads = evaluate_hand(cards("AS AH AD AC KH"))
    assert straight_flush > quads


# ---------------------------------------------------------------------------
# hand_score: best 5 of 6 or 7 cards
# ---------------------------------------------------------------------------

def test_hand_score_straight_spans_hand_and_board():
    hand = cards("9S 10D")
    board = cards("JH QC KS 2D 3H")
    assert hand_score(hand, board) == 5


def test_hand_score_plays_the_board():
    """A royal flush on the board beats anything the hole cards add."""
    hand = cards("2C 7D")
    board = cards("AS KS QS JS 10S")
    assert hand_score(hand, board) == 9


def test_hand_score_prefers_flush_over_pair():
    hand = cards("AH 2H")
    board = cards("2C 9H JH KH 5S")
    assert hand_score(hand, board) == 6


def test_hand_score_two_trips_make_full_house():
    """Seven cards with two sets of trips should score as a full house."""
    hand = cards("KH KD")
    board = cards("KS QH QD QC 2S")
    assert hand_score(hand, board) == 7


def test_hand_score_three_pair_is_two_pair():
    """Three pairs across seven cards is still only two pair."""
    hand = cards("AH AD")
    board = cards("KS KH 7D 7C 2S")
    assert hand_score(hand, board) == 3


def test_hand_score_six_cards_on_turn():
    hand = cards("8H 8D")
    board = cards("8S 8C 2D 5H")
    assert hand_score(hand, board) == 8


def test_hand_score_exactly_five_cards_matches_evaluate_hand():
    hand = cards("JS JH")
    board = cards("4D 4C AH")
    assert hand_score(hand, board) == evaluate_hand(hand + board) == 3


# ---------------------------------------------------------------------------
# get_partial_hand_score / hand_score pre-flop
# ---------------------------------------------------------------------------

def test_preflop_pocket_pair():
    assert hand_score(cards("AH AS"), []) == 2


def test_preflop_unpaired():
    assert hand_score(cards("AH KS"), []) == 1


@pytest.mark.parametrize("spec", ["", "AH"])
def test_partial_fewer_than_two_cards_is_high_card(spec):
    assert get_partial_hand_score(cards(spec)) == 1


@pytest.mark.parametrize("spec, expected", [
    ("7H 7S 7D",    4),  # Three of a Kind
    ("7H 7S 2D 2C", 3),  # Two Pair
    ("7H 7S 7D 7C", 8),  # Four of a Kind
    ("7H 7S 2D 9C", 2),  # One Pair
])
def test_partial_three_and_four_cards(spec, expected):
    assert get_partial_hand_score(cards(spec)) == expected


# ---------------------------------------------------------------------------
# hand_name
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score, name", [
    (9, "Straight Flush"),
    (8, "Four of a Kind"),
    (7, "Full House"),
    (6, "Flush"),
    (5, "Straight"),
    (4, "Three of a Kind"),
    (3, "Two Pair"),
    (2, "One Pair"),
    (1, "High Card"),
])
def test_hand_name(score, name):
    assert hand_name(score) == name


@pytest.mark.parametrize("score", [0, 10, -1])
def test_hand_name_unknown(score):
    assert hand_name(score) == "Unknown Hand"


# ---------------------------------------------------------------------------
# get_and_validate_raise_amount
# ---------------------------------------------------------------------------

def raise_with(user_input: str, min_raise: int = 10, balance: int = 100, current_bet: int = 0):
    """Call get_and_validate_raise_amount with `user_input` typed at the prompt."""
    with patch("casino.games.poker.poker.cinput", return_value=user_input) as mock_input:
        result = get_and_validate_raise_amount(min_raise, balance, current_bet)
    mock_input.assert_called_once_with("Raise amount:")
    return result


def test_raise_valid_amount():
    assert raise_with("25") == (25, "")


def test_raise_exactly_min_raise_is_accepted():
    assert raise_with("10", min_raise=10) == (10, "")


def test_raise_below_min_raise_is_rejected():
    amount, msg = raise_with("9", min_raise=10)
    assert amount is None
    assert "at least 10" in msg


def test_raise_respects_configured_min_raise():
    amount, msg = raise_with("40", min_raise=50)
    assert amount is None
    assert "at least 50" in msg


@pytest.mark.parametrize("user_input", ["0", "-5"])
def test_raise_zero_or_negative_is_rejected(user_input):
    amount, msg = raise_with(user_input)
    assert amount is None
    assert "positive" in msg


def test_raise_all_in_is_accepted():
    """Raising exactly the balance left after covering the current bet is allowed."""
    assert raise_with("80", balance=100, current_bet=20) == (80, "")


def test_raise_one_over_balance_is_rejected():
    amount, msg = raise_with("81", balance=100, current_bet=20)
    assert amount is None
    assert "enough chips" in msg


def test_raise_affordability_includes_current_bet():
    """A 60 raise would be affordable on its own, but not on top of a 50 bet."""
    assert raise_with("60", balance=100, current_bet=0) == (60, "")
    amount, msg = raise_with("60", balance=100, current_bet=50)
    assert amount is None
    assert "enough chips" in msg


def test_raise_min_raise_unaffordable():
    """With fewer chips than the minimum raise, the minimum is still rejected."""
    amount, msg = raise_with("10", min_raise=10, balance=5)
    assert amount is None
    assert "enough chips" in msg


@pytest.mark.parametrize("user_input", ["abc", "10.5", "", "ten", "1e2"])
def test_raise_non_integer_is_rejected(user_input):
    amount, msg = raise_with(user_input)
    assert amount is None
    assert "must be number" in msg


def test_raise_surrounding_whitespace_is_accepted():
    """int() strips whitespace, so ' 25 ' is accepted as 25."""
    assert raise_with(" 25 ") == (25, "")


# ---------------------------------------------------------------------------
# Fixtures and helpers for PokerGame tests
# ---------------------------------------------------------------------------

@pytest.fixture
def screen():
    """Silence all terminal output; yields the cprint mock for inspecting messages."""
    with patch(f"{MOD}.cprint") as mock_cprint, \
         patch(f"{MOD}.clear_screen"), \
         patch(f"{MOD}.display_topbar"):
        yield mock_cprint


def printed(mock_cprint) -> str:
    """Everything sent to cprint, joined into one string."""
    return "\n".join(str(c.args[0]) for c in mock_cprint.call_args_list if c.args)


@pytest.fixture
def game(screen):
    """A PokerGame for a player with 100 chips and the default config (min raise 10)."""
    ctx = GameContext(account=Account.generate("test", 100), config=Config.default())
    return PokerGame(ctx)


def bet(game, inputs, *, current_bet=0, pot=10, opponent_chips=1000, allow_call=False):
    """
    Run one betting round with scripted inputs.
    Fails if the round doesn't consume every input, so a test can't pass by accident.
    Returns (player_folded, pot, current_bet, opponent_chips).
    """
    stage = "PRE-FLOP" if allow_call else "FLOP"
    board = [] if allow_call else cards("3S 8D JC")
    with patch(f"{MOD}.cinput", side_effect=inputs) as mock_input:
        result = game._betting_round(
            stage=stage,
            player_hand=cards("AH KH"),
            opponent_hand=cards("2C 7D"),
            board=board,
            pot=pot,
            current_bet=current_bet,
            opponent_chips=opponent_chips,
            allow_call=allow_call,
        )
    assert mock_input.call_count == len(inputs)
    return result


# ---------------------------------------------------------------------------
# _betting_round: valid actions
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("action", ["f", "F"])
def test_fold_preflop(game, action):
    assert bet(game, [action], current_bet=20, allow_call=True) == (True, 10, 20, 1000)
    assert game.account.balance == 100


def test_fold_postflop(game):
    assert bet(game, ["f"]) == (True, 10, 0, 1000)
    assert game.account.balance == 100


@pytest.mark.parametrize("action", ["c", "C"])
def test_call_preflop(game, action):
    """Calling the big blind moves 20 chips from the player into the pot."""
    assert bet(game, [action], current_bet=20, allow_call=True) == (False, 30, 20, 1000)
    assert game.account.balance == 80


def test_check_postflop_costs_nothing(game):
    assert bet(game, ["c"]) == (False, 10, 0, 1000)
    assert game.account.balance == 100


def test_raise_postflop(game):
    """Player raises 15; the opponent always calls, so the pot grows by 30."""
    assert bet(game, ["r", "15"]) == (False, 40, 15, 985)
    assert game.account.balance == 85


def test_raise_preflop_adds_to_big_blind(game):
    """Raising 10 over a 20 bet makes it 30; player and opponent each put in 30."""
    assert bet(game, ["R", "10"], current_bet=20, allow_call=True) == (False, 70, 30, 970)
    assert game.account.balance == 70


def test_raise_all_in(game):
    assert bet(game, ["r", "80"], current_bet=20, allow_call=True) == (False, 210, 100, 900)
    assert game.account.balance == 0


def test_preflop_prompt_shows_call_amount(game):
    with patch(f"{MOD}.cinput", return_value="f") as mock_input:
        game._betting_round("PRE-FLOP", cards("AH KH"), cards("2C 7D"), [], 10, 20, 1000, allow_call=True)
    assert "[C]all 20" in mock_input.call_args.args[0]


def test_postflop_prompt_shows_check(game):
    with patch(f"{MOD}.cinput", return_value="f") as mock_input:
        game._betting_round("FLOP", cards("AH KH"), cards("2C 7D"), cards("3S 8D JC"), 10, 0, 1000)
    assert "[C]heck" in mock_input.call_args.args[0]


# ---------------------------------------------------------------------------
# _betting_round: invalid input and re-prompting
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad", ["x", "", "fold", "1"])
def test_invalid_action_reprompts(game, screen, bad):
    assert bet(game, [bad, "c"]) == (False, 10, 0, 1000)
    assert "not a choice" in printed(screen)
    assert game.stubborn == 1


def test_invalid_raise_amount_returns_to_action_prompt(game, screen):
    """A bad raise amount sends the player back to Fold/Check/Raise, not to the amount prompt."""
    assert bet(game, ["r", "abc", "c"]) == (False, 10, 0, 1000)
    assert "must be number" in printed(screen)
    assert game.account.balance == 100


def test_raise_retry_after_unaffordable_amount(game, screen):
    assert bet(game, ["r", "500", "r", "20"]) == (False, 50, 20, 980)
    assert "enough chips" in printed(screen)
    assert game.account.balance == 80


def test_cannot_call_without_enough_chips(game, screen):
    game.account.balance = 10
    assert bet(game, ["c", "f"], current_bet=20, allow_call=True) == (True, 10, 20, 1000)
    assert "enough chips to call 20" in printed(screen)
    assert game.account.balance == 10


def test_seven_invalid_inputs_removes_player(game, screen):
    """The 7th invalid input triggers security, which counts as a fold."""
    assert bet(game, ["x"] * 7) == (True, 10, 0, 1000)
    assert SECURITY_MSG in printed(screen)
    assert game.account.balance == 100


def test_six_invalid_inputs_is_still_allowed(game, screen):
    assert bet(game, ["x"] * 6 + ["c"]) == (False, 10, 0, 1000)
    assert SECURITY_MSG not in printed(screen)


# ---------------------------------------------------------------------------
# _betting_round: known bugs
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True, raises=ValueError,
    reason="'Ff'/'Cc'/'Rr' pass the substring check `action in 'FfCcRr'` "
           "but match no branch, so the code hits `raise ValueError`",
)
@pytest.mark.parametrize("bad", ["Ff", "Cc", "Rr", "fC"])
def test_doubled_letters_are_rejected_not_crash(game, bad):
    assert bet(game, [bad, "f"]) == (True, 10, 0, 1000)


@pytest.mark.xfail(
    strict=True,
    reason="game.stubborn is never reset, so invalid inputs from earlier "
           "betting rounds count toward the 7-strike limit",
)
def test_invalid_input_count_resets_between_betting_rounds(game):
    bet(game, ["x"] * 6 + ["c"])            # 6 strikes, still in the game
    assert bet(game, ["x", "c"]) == (False, 10, 0, 1000)  # 1 new strike shouldn't remove the player


# ---------------------------------------------------------------------------
# _showdown
# ---------------------------------------------------------------------------

def test_showdown_fold_is_loss(game, screen):
    game._showdown(cards("AH AD"), cards("2C 7D"), [], pot=30, opponent_chips=1000, player_folded=True)
    assert game.account.balance == 100
    assert (game.stats.wins, game.stats.losses, game.stats.pushes) == (0, 1, 0)
    assert "You folded" in printed(screen)


def test_showdown_player_wins_pot(game, screen):
    board = cards("KS 7C 2D 9H 4S")
    game._showdown(cards("AH AD"), cards("3C 8D"), board, pot=60, opponent_chips=1000, player_folded=False)
    assert game.account.balance == 160
    assert (game.stats.wins, game.stats.losses, game.stats.pushes) == (1, 0, 0)
    assert "You win with a One Pair!" in printed(screen)


def test_showdown_opponent_wins(game, screen):
    board = cards("KS 7C 2D 9H 4S")
    game._showdown(cards("3C 8D"), cards("AH AD"), board, pot=60, opponent_chips=1000, player_folded=False)
    assert game.account.balance == 100
    assert (game.stats.wins, game.stats.losses, game.stats.pushes) == (0, 1, 0)
    assert "Opponent wins with a One Pair." in printed(screen)


def test_showdown_tie_splits_pot(game, screen):
    """Both players play the royal flush on the board."""
    board = cards("AS KS QS JS 10S")
    game._showdown(cards("2C 3D"), cards("4H 5C"), board, pot=60, opponent_chips=1000, player_folded=False)
    assert game.account.balance == 130
    assert (game.stats.wins, game.stats.losses, game.stats.pushes) == (0, 0, 1)
    assert "tie" in printed(screen)


def test_showdown_reveals_opponent_hand(game):
    """Opponent cards are face-down during betting but face-up at showdown."""
    board = cards("KS 7C 2D 9H 4S")
    with patch(f"{MOD}.print_hand") as mock_print_hand:
        game._showdown(cards("AH AD"), cards("3C 8D"), board, 60, 1000, False)
    opponent_call = mock_print_hand.call_args_list[0]
    assert opponent_call.kwargs["hidden"] is False


def test_betting_hides_opponent_hand(game):
    with patch(f"{MOD}.print_hand") as mock_print_hand:
        bet(game, ["f"])
    opponent_call = mock_print_hand.call_args_list[0]
    assert opponent_call.kwargs["hidden"] is True


# ---------------------------------------------------------------------------
# Known bug: no tiebreakers within a category.
# These are strict xfails, so they will start failing (XPASS) once
# tiebreakers are implemented, as a reminder to remove the marker.
# ---------------------------------------------------------------------------

TIEBREAK_BUG = "evaluate_hand only scores the category; no kicker/rank tiebreakers"


@pytest.mark.xfail(strict=True, reason=TIEBREAK_BUG)
def test_higher_pair_beats_lower_pair():
    aces = evaluate_hand(cards("AS AH 3D 7C 9H"))
    twos = evaluate_hand(cards("2S 2H 3C 7D 9S"))
    assert aces > twos


@pytest.mark.xfail(strict=True, reason=TIEBREAK_BUG)
def test_higher_straight_beats_lower_straight():
    ace_high = evaluate_hand(cards("10S JD QH KC AS"))
    six_high = evaluate_hand(cards("2S 3D 4H 5C 6S"))
    assert ace_high > six_high


@pytest.mark.xfail(strict=True, reason=TIEBREAK_BUG)
def test_kicker_breaks_tie():
    ace_kicker = evaluate_hand(cards("KS KH AD 7C 2H"))
    queen_kicker = evaluate_hand(cards("KD KC QS 7H 2D"))
    assert ace_kicker > queen_kicker


# ---------------------------------------------------------------------------
# _play_round: full rounds with a stacked deck
# ---------------------------------------------------------------------------

def stack_deck(player: str, opponent: str, board: str, burns: str = "5C 6C JD") -> None:
    """
    Arrange FULL_DECK so a round deals exactly these cards.
    Deal order: player, opponent, player, opponent, burn, flop x3, burn, turn, burn, river.
    Deck.draw() pops from the end, so the list is reversed.
    """
    p, o, b, burn = cards(player), cards(opponent), cards(board), cards(burns)
    order = [p[0], o[0], p[1], o[1], burn[0], *b[:3], burn[1], b[3], burn[2], b[4]]
    FULL_DECK.cards = list(reversed(order))


def play_round(game, inputs) -> None:
    with patch(f"{MOD}.cinput", side_effect=inputs) as mock_input:
        game._play_round()
    assert mock_input.call_count == len(inputs)


def as_tuples(card_list) -> list[tuple[str, str]]:
    return [(c.rank, c.suit) for c in card_list]


WINNING_DEAL = dict(player="AH AD", opponent="3C 8D", board="KS 7C 2D 9H 4S")
LOSING_DEAL  = dict(player="3C 8D", opponent="AH AD", board="KS 7C 2D 9H 4S")


def test_round_deals_hands_and_burns_before_each_street(game):
    """Hole cards alternate player/opponent; one card is burned before the flop, turn and river."""
    stack_deck(**WINNING_DEAL)
    with patch.object(game, "_showdown") as mock_showdown:
        play_round(game, ["c", "c", "c", "c"])
    player_hand, opponent_hand, board, pot, _, folded = mock_showdown.call_args.args
    assert as_tuples(player_hand) == as_tuples(cards("AH AD"))
    assert as_tuples(opponent_hand) == as_tuples(cards("3C 8D"))
    assert as_tuples(board) == as_tuples(cards("KS 7C 2D 9H 4S"))
    assert pot == 30
    assert folded is False


def test_round_call_and_check_to_showdown_win(game):
    """Call 20 pre-flop, check every street, win the 30 pot: net +10."""
    stack_deck(**WINNING_DEAL)
    play_round(game, ["c", "c", "c", "c"])
    assert game.account.balance == 110
    assert (game.stats.rounds_played, game.stats.wins, game.stats.losses) == (1, 1, 0)


def test_round_call_and_check_to_showdown_loss(game):
    stack_deck(**LOSING_DEAL)
    play_round(game, ["c", "c", "c", "c"])
    assert game.account.balance == 80
    assert (game.stats.rounds_played, game.stats.wins, game.stats.losses) == (1, 0, 1)


def test_round_raise_preflop_then_win(game):
    """Raise 10 over the big blind (pay 30), opponent matches, win the 70 pot."""
    stack_deck(**WINNING_DEAL)
    play_round(game, ["r", "10", "c", "c", "c"])
    assert game.account.balance == 140


def test_round_fold_preflop_ends_round_immediately(game):
    """Only one prompt is shown, and the player is not charged a blind."""
    stack_deck(**WINNING_DEAL)
    play_round(game, ["f"])
    assert game.account.balance == 100
    assert (game.stats.rounds_played, game.stats.losses) == (1, 1)


def test_round_fold_on_turn_loses_called_chips(game):
    stack_deck(**WINNING_DEAL)
    play_round(game, ["c", "c", "f"])
    assert game.account.balance == 80
    assert (game.stats.rounds_played, game.stats.losses) == (1, 1)


def test_round_resets_deck_afterwards(game):
    stack_deck(**WINNING_DEAL)
    play_round(game, ["f"])
    assert len(FULL_DECK.cards) == 52
    assert len(set(as_tuples(FULL_DECK.cards))) == 52


# ---------------------------------------------------------------------------
# play(): the session loop
# ---------------------------------------------------------------------------

def run_session(game, inputs, round_effect=None):
    """
    Run play() with _play_round and display_stats mocked out.
    `round_effect` runs in place of each round (e.g. to change the balance).
    Returns (round_mock, stats_mock).
    """
    with patch(f"{MOD}.cinput", side_effect=inputs) as mock_input, \
         patch.object(game, "_play_round", side_effect=round_effect) as mock_round, \
         patch(f"{MOD}.display_stats") as mock_stats:
        game.play()
    assert mock_input.call_count == len(inputs)
    return mock_round, mock_stats


def test_session_refuses_player_below_minimum(game, screen):
    game.account.balance = 19
    mock_round, mock_stats = run_session(game, [""])
    mock_round.assert_not_called()
    mock_stats.assert_not_called()
    assert NO_FUNDS_MSG in printed(screen)


def test_session_allows_exactly_minimum(game):
    game.account.balance = 20
    mock_round, _ = run_session(game, ["n"])
    assert mock_round.call_count == 1


@pytest.mark.parametrize("answer", ["n", "N"])
def test_session_no_ends_and_shows_stats(game, answer):
    mock_round, mock_stats = run_session(game, [answer])
    assert mock_round.call_count == 1
    mock_stats.assert_called_once_with(game.stats)
    assert game.stats.ending_balance == game.account.balance


@pytest.mark.parametrize("answer", ["y", "Y"])
def test_session_yes_plays_another_round(game, answer):
    mock_round, mock_stats = run_session(game, [answer, "n"])
    assert mock_round.call_count == 2
    mock_stats.assert_called_once()


def test_session_ending_balance_reflects_winnings(game):
    def win_50():
        game.account.deposit(50)

    run_session(game, ["y", "n"], round_effect=win_50)
    assert game.stats.ending_balance == 200
    assert game.stats.net == 100


def test_session_ends_when_player_runs_out_of_chips(game, screen):
    """No 'stay at the table?' prompt; just the goodbye and stats."""
    def lose_most_chips():
        game.account.balance = 5

    mock_round, mock_stats = run_session(game, [""], round_effect=lose_most_chips)
    assert mock_round.call_count == 1
    mock_stats.assert_called_once()
    assert game.stats.ending_balance == 5
    assert NO_FUNDS_MSG in printed(screen)


@pytest.mark.parametrize("bad", ["x", "", "maybe"])
def test_session_invalid_answer_reprompts(game, screen, bad):
    mock_round, _ = run_session(game, [bad, "n"])
    assert mock_round.call_count == 1
    assert INVALID_YES_OR_NO_MSG in printed(screen)


def test_session_thirteen_invalid_answers_removes_player(game, screen):
    mock_round, mock_stats = run_session(game, ["x"] * 13)
    assert mock_round.call_count == 1
    mock_stats.assert_called_once()
    assert SECURITY_MSG in printed(screen)


def test_session_twelve_invalid_answers_is_still_allowed(game, screen):
    mock_round, _ = run_session(game, ["x"] * 12 + ["n"])
    assert mock_round.call_count == 1
    assert SECURITY_MSG not in printed(screen)


@pytest.mark.xfail(
    strict=True,
    reason="`play_again not in 'YyNn'` is a substring check, so 'yN' and 'YyNn' "
           "count as valid answers and are then treated as 'yes'",
)
@pytest.mark.parametrize("bad", ["yN", "YyNn"])
def test_session_multi_letter_answer_is_rejected(game, bad):
    mock_round, _ = run_session(game, [bad, "n"])
    assert mock_round.call_count == 1
