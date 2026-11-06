import shutil
import sys
from typing import Callable
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Container
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Label, Input, Static, ListView, ListItem

from . import games
from .accounts import Account
from .config import Config
from .types import GameContext
from .utils import cprint, cinput, clear_screen, display_topbar, get_theme

CASINO_HEADER = """
┌──────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦   │
└──────────────────────────────────────┘
"""

GAME_HANDLERS: dict[str, Callable[[GameContext], None]] = {
    "blackjack (U.S.)": games.blackjack.play_blackjack,
    "blackjack (E.U.)": games.blackjack.play_european_blackjack,
    "slots": games.slots.play_slots,
    "poker": games.poker.play_poker,
    "roulette": games.roulette.play_roulette,
    "uno": games.uno.play_uno,
    "european roulette": games.roulette.play_european_roulette,
}
ALL_GAMES = list(GAME_HANDLERS.keys())
ACCOUNT_STARTING_BALANCE = 100

class CasinoApp(App):
    """Textual app for Terminal Casino Homepage."""

    CSS = """
    Screen {
        align: center middle;
        background: $boost;
    }
    #main-container {
        width: 60;
        height: auto;
        border: solid yellow;
        padding: 1 2;
        background: $surface;
        align: center middle;
    }
    #title-banner {
        text-style: bold;
        color: yellow;
        text-align: center;
        margin-bottom: 1;
    }
    .section-label {
        margin-top: 1;
        margin-bottom: 1;
        text-style: bold;
    }
    Input {
        margin-bottom: 1;
    }
    Button {
        width: 100%;
        margin-top: 1;
    }
    ListView {
        height: 10;
        border: solid green;
        margin-top: 1;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("e", "exit_app", "Exit App"),
        Binding("ctrl+c", "exit_popup", "Exit Popup", show=False)
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            yield Static(CASINO_HEADER.strip(), id="title-banner")
            yield Label("Enter Player Name:", classes="section-label")
            yield Input(placeholder="Player name...", id="player-name", value="Player")
            yield Label("Select a Game:", classes="section-label")
            with ListView(id="game-list"):
                for game_name in ALL_GAMES:
                    safe_id = "game-" + game_name.replace("(", "").replace(")", "").replace(".", "").replace(" ", "-")
                    yield ListItem(Static(game_name.title()), id=safe_id)
            yield Button("Play Selected Game", id="play-btn", variant="success")
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

    def action_exit_app(self) -> None:
        self.exit()

    def action_exit_popup(self) -> None:
        self.push_screen(ExitPopup())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "play-btn":
            name_input = self.query_one("#player-name", Input).value.strip()
            self.player_name = name_input if name_input else "Player"

            game_list = self.query_one("#game-list", ListView)
            selected_index = game_list.index
            if selected_index is not None and 0 <= selected_index < len(ALL_GAMES):
                self.selected_game_name = ALL_GAMES[selected_index]
                self.exit()

class ExitPopup(ModalScreen):
    """A simple exit popup"""
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("If you'd like to exit the app, please press \"e\" or click \"Exit App\" in the footer."),
            Button("Dismiss", id="dismiss")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "dismiss":
            self.app.pop_screen()

if __name__ == "__main__":
    app = CasinoApp()
    app.run()

    if hasattr(app, "selected_game_name") and app.selected_game_name:
        handler = GAME_HANDLERS.get(app.selected_game_name)
        if handler:
            if sys.platform == "win32":
                import msvcrt
                while msvcrt.kbhit():
                    msvcrt.getch()

            account = Account.generate(app.player_name, ACCOUNT_STARTING_BALANCE)
            config = Config.default()
            ctx = GameContext(account=account, config=config)
            clear_screen()
            handler(ctx)