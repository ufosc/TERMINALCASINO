import shutil

from . import games
from .accounts import Account
from .config import Config
from .types import GameContext
from .utils import cprint, cinput, clear_screen, display_topbar, get_theme
from typing import Callable
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Label, Input

class CasinoApp(App):
    """Textual homepage for Terminal Casino."""

    CSS = """
    Screen {
        align: center middle;
    }

    #homepage {
        width: 70;
        height: auto;
        padding: 1 3;
        border: round $accent;
    }

    #casino-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #name-input {
        margin-bottom: 1;
    }

    #game-label {
        width: 100%;
        text-align: center;
        text-style: bold;
        margin: 1 0;
    }

    .game-row {
        width: 100%;
        height: auto;
        align: center middle;
    }

    .game-button {
        margin: 0 1;
        min-width: 20;
    }

    #message {
        width: 100%;
        text-align: center;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("e", "exit_app", "Exit App"),
        Binding("ctrl+c", "exit_popup", "Exit Popup", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Create the Terminal Casino homepage."""
        yield Header()

        yield Vertical(
            Label(
                "♦ T E R M I N A L   C A S I N O ♦",
                id="casino-title",
            ),

            Label("Enter your player name:"),

            Input(
                placeholder="Player name",
                id="name-input",
            ),

            Label("Select a Game", id="game-label"),

            Horizontal(
                Button(
                    "Blackjack (U.S.)",
                    id="blackjack-us",
                    classes="game-button",
                ),
                Button(
                    "Blackjack (E.U.)",
                    id="blackjack-eu",
                    classes="game-button",
                ),
                classes="game-row",
            ),

            Horizontal(
                Button(
                    "Slots",
                    id="slots",
                    classes="game-button",
                ),
                Button(
                    "Poker",
                    id="poker",
                    classes="game-button",
                ),
                classes="game-row",
            ),

            Horizontal(
                Button(
                    "Roulette",
                    id="roulette",
                    classes="game-button",
                ),
                Button(
                    "European Roulette",
                    id="european-roulette",
                    classes="game-button",
                ),
                classes="game-row",
            ),

            Horizontal(
                Button(
                    "UNO",
                    id="uno",
                    classes="game-button",
                ),
                classes="game-row",
            ),

            Label("", id="message"),

            id="homepage",
        )

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle game-selection buttons."""

        game_map = {
            "blackjack-us": "blackjack (U.S.)",
            "blackjack-eu": "blackjack (E.U.)",
            "slots": "slots",
            "poker": "poker",
            "roulette": "roulette",
            "european-roulette": "european roulette",
            "uno": "uno",
        }

        button_id = event.button.id

        if button_id not in game_map:
            return

        name_input = self.query_one("#name-input", Input)
        message = self.query_one("#message", Label)

        player_name = name_input.value.strip()

        if not player_name:
            message.update("Please enter a valid player name before selecting a game.")
            name_input.focus()
            return

        selected_game = game_map[button_id]

        self.exit((player_name, selected_game))

    def action_toggle_dark(self) -> None:
        """Toggle between Textual light and dark themes."""
        self.theme = (
            "textual-dark"
            if self.theme == "textual-light"
            else "textual-light"
        )

    def action_exit_app(self) -> None:
        """Exit Terminal Casino."""
        self.exit()

    def action_exit_popup(self) -> None:
        """Override the native Ctrl+C binding popup."""
        self.push_screen(ExitPopup())

# TODO: clean up the UI, currently extremely rough
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

CASINO_HEADER = """
┌──────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦   │
└──────────────────────────────────────┘
"""

CASINO_HEADER_OPTIONS = {
    "header": CASINO_HEADER,
    "margin": 3,
}
ACCOUNT_STARTING_BALANCE = 100

ENTER_OR_QUIT_PROMPT = "[E]nter   [Q]uit: "
INVALID_CHOICE_PROMPT = "\nInvalid input. Please try again.\n"
GAME_CHOICE_PROMPT = "Please choose a game to play: "

# To add a new game, just add a handler function to GAME_HANDLERS

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

def term_width() -> int:
    """Safe terminal width fallback."""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def prompt_with_refresh(
    render_fn: Callable[[], None],
    prompt: str,
    error_message: str,
    validator: Callable[[str], bool],
    transform: Callable[[str], str] = lambda s: s.strip(),
) -> str:
    """
    Repeatedly render screen, show last error (if any), ask for input and validate.
    On EOF/KeyboardInterrupt return 'q' so caller can decide how to exit.
    """
    last_error = ""
    while True:
        render_fn()
        if last_error:
            cprint(last_error)
        answer = transform(cinput(prompt).strip())
        if validator(answer):
            return answer
        last_error = error_message



def main_menu(ctx: GameContext) -> None:
    """
    Main loop: show welcome, then (if chosen) show game menu, call handler,
    then return to top-level menu. No recursion used.
    """
    account = ctx.account
    while True:
        def render_welcome():
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("")  # spacing

        action = prompt_with_refresh(
            render_fn = render_welcome,
            prompt = ENTER_OR_QUIT_PROMPT.center(term_width()),
            error_message = INVALID_CHOICE_PROMPT,
            validator = lambda x: x.lower() in {"e", "q"},
            transform = lambda s: s.strip().lower(),
        )

        if action == "q":
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("\nGoodbye!\n")
            break  # exit loop -> program ends

        # --- choose game ---
        def render_choose_game():
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("")  # spacing
            width = term_width()
            max_length = max(map(len, ALL_GAMES))
            cprint("┌" + "─" * 30 + "┐")
            cprint("│" + " " * 30 + "│")
            for i, name in enumerate(ALL_GAMES, start=1):
                cprint(
                    f"│{('[{}] {}'.format(i, name.title()) + ' ' * (max_length - len(name))).center(30)}│".center(width)
                )
            cprint("│" + " " * 30 + "│")
            cprint("└" + "─" * 30 + "┘")



        choice = prompt_with_refresh(
            render_fn = render_choose_game,
            prompt = GAME_CHOICE_PROMPT.center(term_width()),
            error_message = INVALID_CHOICE_PROMPT,
            validator = lambda x: x.isdigit() and 1 <= int(x) <= len(ALL_GAMES),
        )

        selected_game = ALL_GAMES[int(choice) - 1]
        handler = GAME_HANDLERS.get(selected_game)
        if handler:
            clear_screen()
            handler(ctx)  # returns to loop after game finishes
        else:
            clear_screen()
            display_topbar(account, **CASINO_HEADER_OPTIONS)
            cprint("\nNo such game!\n")


def main():
    clear_screen()
    display_topbar(account=None, **CASINO_HEADER_OPTIONS)

    name = cinput("Enter your name: ").strip()
    while not name:
        clear_screen()
        display_topbar(account=None, **CASINO_HEADER_OPTIONS)
        cprint("\nInvalid input. Please enter a valid name.\n")
        name = cinput("Enter your name: ").strip()
    
    # theme selection
    clear_screen()
    display_topbar(account=None, **CASINO_HEADER_OPTIONS)
    get_theme()


    account = Account.generate(name, ACCOUNT_STARTING_BALANCE)
    config = Config.default()
    ctx = GameContext(account=account, config=config)
    main_menu(ctx)

if __name__ == "__main__":
    app = CasinoApp()
    result = app.run()

    if result is not None:
        player_name, selected_game = result

        account = Account.generate(
            player_name,
            ACCOUNT_STARTING_BALANCE,
        )

        config = Config.default()

        ctx = GameContext(
            account=account,
            config=config,
        )

        handler = GAME_HANDLERS.get(selected_game)

        if handler:
            clear_screen()
            handler(ctx)