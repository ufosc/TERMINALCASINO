import shutil

from . import games
from .accounts import Account
from .config import Config
from .types import GameContext
from .utils import cprint, cinput, clear_screen, display_topbar, get_theme
from typing import Callable
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Label
from textual.widgets import Input
from textual.containers import VerticalScroll

class CasinoApp(App):
    """Textual app for Terminal Casino."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), 
                ("e", "exit_app", "Exit App"),
                Binding("ctrl+c", "exit_popup", "Exit Popup", show=False)]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        #set the title shown in the top bar
        self.title = "Terminal Casino"
        #display the casino heading in the homepage
        yield Label("TERMINAL CASINO", id="casino-title")
        #allow the player to enter their name
        yield Input(placeholder="Enter your name", id="name-input")
        #display a bytton for each game
        with VerticalScroll(id="game-list"):
            for index, game_name in enumerate(ALL_GAMES, start=1):
                yield Button(
                    game_name.title(),
                    id=f"game-{index}"
                )


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""

        #ignora butao que nao e escolha
        if not button_id.startswith("game-"):
            return

        name_input = self.query_one("#name-input", Input)
        name = name_input.value.strip()

        #requer um nome antes do jogo
        if not name:
            self.notify("Please enter your name.", severity="warning")
            name_input.focus()
            return

        game_index = int(button_id.removeprefix("game-")) - 1
        game_name = ALL_GAMES[game_index]

        #return player name/ game selcted
        self.exit((name, game_name))




    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_exit_app(self) -> None:
        """An action to exit the app."""
        self.exit()
    
    def action_exit_popup(self) -> None:
        """Override the native ctrl+c binding popup."""
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
    #receive the player name and game
    result = app.run()

    #start a game only when the player selected one
    if result is not None:
        name, game_name = result

        #create a player using the account system
        account = Account.generate(name, ACCOUNT_STARTING_BALANCE)
        config = Config.default()
        ctx = GameContext(account=account, config=config)

        #open the game outside textual
        handler = GAME_HANDLERS[game_name]
        clear_screen()
        handler(ctx)
    """ -- OLD MAIN --
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        clear_screen()
        display_topbar(account=None, **CASINO_HEADER_OPTIONS)
        cprint("\nGoodbye! (Interrupted)\n")
    """