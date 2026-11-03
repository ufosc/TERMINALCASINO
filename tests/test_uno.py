from unittest.mock import patch, call

from casino.accounts import Account
from casino.config import Config
from casino.types import GameContext
from casino.games.uno.player import Player
from casino.games.uno.views.view import (
    UnoView,
    WINNER_MENU_PROMPT,
    STATS_NAV_PROMPT,
    INVALID_OPTION_MSG,
)

VIEW = "casino.games.uno.views.view"


def make_view():
    ctx = GameContext(account=Account.generate("test", 100), config=Config.default())
    return UnoView(ctx)


def make_players():
    # 3 players, the second one wins
    players = [Player(0, "ana"), Player(1, "bob"), Player(2, "cal")]
    players[1].cards_played = 7
    return players


def run_winner_screen(inputs):
    """Run show_winner with fake inputs, returns the mocks for cinput and print_player_stats"""
    view = make_view()
    players = make_players()
    with patch(f"{VIEW}.cinput", side_effect=inputs) as mock_input, \
         patch(f"{VIEW}.cprint") as mock_print, \
         patch(f"{VIEW}.clear_screen"), \
         patch(f"{VIEW}.display_topbar"), \
         patch.object(UnoView, "print_player_stats") as mock_stats:
        view.show_winner(players[1], players)
    return players, mock_input, mock_print, mock_stats


def test_enter_exits_without_stats():
    players, mock_input, _, mock_stats = run_winner_screen([""])
    mock_input.assert_called_once_with(WINNER_MENU_PROMPT)
    mock_stats.assert_not_called()


def test_stats_start_on_winner_page():
    players, _, _, mock_stats = run_winner_screen(["s", "q", ""])
    # first page shown is the winner (index 1)
    mock_stats.assert_called_once_with(players[1], 1, 3, players[1])


def test_next_and_prev_wrap_around():
    # winner is index 1 -> n:2 -> n:0 (wraps) -> p:2 (wraps back) -> q -> exit
    players, _, _, mock_stats = run_winner_screen(["s", "n", "n", "p", "q", ""])
    pages = [c.args[1] for c in mock_stats.call_args_list]
    assert pages == [1, 2, 0, 2]


def test_lowercase_and_uppercase_work():
    players, _, _, mock_stats = run_winner_screen(["S", "N", "Q", ""])
    pages = [c.args[1] for c in mock_stats.call_args_list]
    assert pages == [1, 2]


def test_back_returns_to_winner_menu():
    players, mock_input, _, _ = run_winner_screen(["s", "q", ""])
    assert mock_input.call_args_list == [
        call(WINNER_MENU_PROMPT),
        call(STATS_NAV_PROMPT),
        call(WINNER_MENU_PROMPT),
    ]


def test_invalid_option_shows_message():
    players, _, mock_print, mock_stats = run_winner_screen(["x", "s", "z", "q", ""])
    assert mock_print.call_args_list.count(call(INVALID_OPTION_MSG)) == 2
    # invalid key in stats screen should not change the page
    pages = [c.args[1] for c in mock_stats.call_args_list]
    assert pages == [1, 1]


def test_stat_page_shows_player_stats():
    view = make_view()
    players = make_players()
    with patch(f"{VIEW}.cprint") as mock_print:
        view.print_player_stats(players[1], 1, 3, players[1])
    printed = "\n".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "BOB" in printed
    assert "Player 2/3" in printed
    assert "WINNER" in printed
    assert "7" in printed


def test_stat_page_no_winner_tag_for_loser():
    view = make_view()
    players = make_players()
    with patch(f"{VIEW}.cprint") as mock_print:
        view.print_player_stats(players[0], 0, 3, players[1])
    printed = "\n".join(str(c.args[0]) for c in mock_print.call_args_list)
    assert "ANA" in printed
    assert "WINNER" not in printed