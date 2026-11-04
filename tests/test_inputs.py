from unittest.mock import patch,ANY,call,Mock
from casino.main import *
from casino.games import *
import pytest

#Add more tests as needed


def test_empty_name_and_quit():
    inputs = ["","TEST","1","8","q"]

    with patch("casino.main.cinput",side_effect=inputs), \
        patch("casino.main.get_theme"), \
        patch("casino.main.Account.generate") as mock_generate, \
        patch("casino.main.cprint") as mock_print, \
        patch("casino.main.clear_screen"), \
        patch("casino.main.display_topbar"):

        main()

    mock_generate.assert_called_with('TEST',ANY)
    mock_print.assert_called_with("\nGoodbye!\n")

def test_interrupt():
    with patch("casino.main.cinput", side_effect=KeyboardInterrupt):
        with pytest.raises(KeyboardInterrupt):
            main()

def test_invalid_game():
    ctx = GameContext(account=Account.generate('test', 100), config=Config.default())
    inputs = ["E","Poker","Blackjack","[1]","20","1.5","Quit","-1",KeyboardInterrupt]
    with patch("casino.main.cinput",side_effect=inputs), \
         patch("casino.main.cprint") as mock_print:
            with pytest.raises(KeyboardInterrupt):
                main_menu(ctx)
    mock_print.assert_called_with("\nInvalid input. Please try again.\n")
    assert mock_print.call_args_list.count(call("\nInvalid input. Please try again.\n"))==len(inputs)-2

@pytest.mark.parametrize("game_index, game_name", [(str(i + 1), name) for i, name in enumerate(ALL_GAMES)])
def test_game_handler_called(game_index, game_name):
    ctx = GameContext(account=Account.generate("test", 100), config=Config.default())
    handlers = {name: Mock() for name in ALL_GAMES}
    with patch("casino.main.prompt_with_refresh", side_effect=["e", game_index, "q"]), \
         patch("casino.main.GAME_HANDLERS", handlers), \
         patch("casino.main.ALL_GAMES", ALL_GAMES), \
         patch("casino.main.cprint"), \
         patch("casino.main.clear_screen"), \
         patch("casino.main.display_topbar"), \
         patch("casino.main.get_theme"), \
         patch("casino.main.cinput", return_value="q"):
          main_menu(ctx)

    handlers[game_name].assert_called_once()

    for other_name, mock_func in handlers.items():
        if other_name != game_name:
            mock_func.assert_not_called()


def test_menu_return_reopens_game_selection_with_existing_account():
    account = Account.generate("test", 100)
    selected_app = Mock(
        selected_game="blackjack (U.S.)",
        home_account=account,
    )
    menu_app = Mock(selected_game=None, home_account=account)
    handler = Mock(return_value="MENU")
    app_factory = Mock(side_effect=[selected_app, menu_app])

    with patch("casino.main.CasinoApp", app_factory), \
         patch("casino.main.GAME_HANDLERS", {"blackjack (U.S.)": handler}), \
         patch("casino.main.Config.default", return_value=Config.default()), \
         patch("casino.main.clear_screen"):
        run_casino_app()

    assert app_factory.call_args_list == [call(), call(account)]
    selected_app.run.assert_called_once()
    menu_app.run.assert_called_once()
    handler.assert_called_once()