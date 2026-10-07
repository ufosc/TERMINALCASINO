import re
import shutil

from . import games
from .accounts import Account
from .config import Config
from .types import GameContext
from .utils import cprint, cinput, clear_screen, display_topbar, get_theme
from typing import Callable
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Label, Input

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


def game_id(game: str) -> str:
    """Sanitize a game name into a valid Textual widget id."""
    return re.sub(r"[^a-z0-9]+", "-", game.lower()).strip("-")

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


class NameSelect(App):
    
    CSS = """
    #title {
        text-align: center;
        width: 100%;
        color: gold;
        text-style: bold;
        margin-top: 2;

    }
    """
    def compose(self) -> ComposeResult:
        self.title = "Terminal Casino"
        yield Header()
        yield Footer()
        yield Static("♦ T E R M I N A L  C A S I N O ♦", id="title")


        yield Input(placeholder="Enter Your Name",type="text", id="name-input")



    def on_input_submitted(self, event: Input.Submitted) -> None:
        name = event.value.strip()
        if name:
            self.notify(f"Welcome, {name}")
            self.query_one("#name-input").remove()
            self.exit(name)

       


class GameSelect(App):
    CSS = """
    #title {
        text-align: center;
        width: 100%;
        color: gold;
        text-style: bold;
        margin-top: 2;

    }
    #subtitle {
        text-align: center;
        width: 100%;
        color: cyan;
        text-style: bold;
    }
    #enter{

        text-align: center;
        color:white;
        background:black;

    }
    Horizontal{
    
    align: center middle;
    }
    
    """
    def __init__(self, username: str):
        super().__init__()
        self.username = username
    
    def compose(self) -> ComposeResult:
        self.title = "Terminal Casino"
        yield Header()
        yield Static("♦ T E R M I N A L  C A S I N O ♦", id="title")
        yield Static(f"Welcome {self.username}!",id="subtitle")
        with Horizontal():
            for i, name in enumerate(ALL_GAMES, start=1):
                yield Button(name.title(), id=f"g{i}")
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(str(event.button.id))

class MenuSelect(App):
    CSS = """
    #title {
        text-align: center;
        width: 100%;
        color: gold;
        text-style: bold;
        margin-top: 2;

    }
    #subtitle {
        text-align: center;
        width: 100%;
        color: cyan;
        text-style: bold;
    }
    #enter{

        text-align: center;
        color:white;
        background:green;

    }
    #exit{

        text-align: center;
        color:white;
        background:red;

    }
    Horizontal{
        align: center middle;
    }
    
    """
    def __init__(self, username: str):
        super().__init__()
        self.username = username
    
    def compose(self) -> ComposeResult:
        self.title = "Terminal Casino"
        yield Header()
        yield Static("♦ T E R M I N A L  C A S I N O ♦", id="title")
        yield Static(f"Welcome {self.username}!",id="subtitle")
        with Horizontal():
            yield Button("Enter", id="enter")
            yield Button("Exit", id="exit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(str(event.button.id))







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


def main(name: str):

    clear_screen()
    display_topbar(account=None, **CASINO_HEADER_OPTIONS)

    
    name =name
    # theme selection
    clear_screen()
    display_topbar(account=None, **CASINO_HEADER_OPTIONS)
    get_theme()


    account = Account.generate(name, ACCOUNT_STARTING_BALANCE)
    config = Config.default()
    ctx = GameContext(account=account, config=config)
    main_menu(ctx)


class HomeScreen(Screen):
    """Homepage: Terminal Casino header and name input."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Label(CASINO_HEADER)
        yield Label("Welcome to Terminal Casino!")
        yield Center(
            Vertical(
                Input(placeholder="Enter your name", id="name-input"),
                Button("Start Playing", id="start-btn"),
            )
        )

    def on_mount(self) -> None:
        """Focus the name input when the screen is shown."""
        self.query_one("#name-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Pressing Enter in the name field starts playing, same as the button."""
        if event.input.id == "name-input":
            event.stop()
            self.query_one("#start-btn", Button).press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Start playing: create the account and open the game selection screen."""
        if event.button.id == "start-btn":
            name_input = self.query_one("#name-input", Input)
            name = name_input.value.strip()
            if not name:
                name_input.notify("Please enter a valid name.", severity="warning")
                return
            account = Account.generate(name, ACCOUNT_STARTING_BALANCE)
            self.app.home_account = account
            self.app.push_screen(GameSelectionScreen(account))


class GameSelectionScreen(Screen):
    """Games selection screen: a clickable button for each game."""

    def __init__(self, account: Account) -> None:
        super().__init__()
        self.account = account
        self._game_by_id = {game_id(name): name for name in ALL_GAMES}

    # Uniform button width so the selection list looks tidy. Longest label
    # ("European Roulette", 17 chars) + 2 padding = 19; a little slack.
    BUTTON_WIDTH = 21

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Label(CASINO_HEADER)
        yield Label(f"Welcome, {self.account.name}!  Balance: {self.account.balance}")
        yield Label("Choose a game to play:")
        buttons = []
        for name in ALL_GAMES:
            btn = Button(name.title(), id=game_id(name))
            btn.set_styles(width=self.BUTTON_WIDTH)
            buttons.append(btn)
        back = Button("< Back to Homepage", id="back-btn")
        back.set_styles(width=self.BUTTON_WIDTH)
        yield Center(Vertical(*buttons, back))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle back navigation and game selection."""
        if event.button.id == "back-btn":
            self.app.pop_screen()
            return
        game = self._game_by_id.get(event.button.id)
        if game not in GAME_HANDLERS:
            return
        # Remember the choice, then exit Textual. __main__ runs the game's
        # original terminal UI once the app has fully stopped.
        self.app.selected_game = game
        self.app.exit()


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


class CasinoApp(App):
    """Textual app for Terminal Casino."""

    TITLE = "Terminal Casino"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"),
                ("e", "exit_app", "Exit App"),
                Binding("ctrl+c", "exit_popup", "Exit Popup", show=False)]

    def __init__(self) -> None:
        super().__init__()
        # Account created on the homepage; None until the player enters a name
        self.home_account: Account | None = None
        # Game chosen on the selection screen; None if the player backed out
        self.selected_game: str | None = None

    def on_mount(self) -> None:
        """Open the homepage when the app starts."""
        self.push_screen(HomeScreen())

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


if __name__ == "__main__":
    app = CasinoApp()
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        pass

    # If a game was chosen, exit Textual and open its original terminal UI.
    if app.selected_game and app.home_account:
        handler = GAME_HANDLERS[app.selected_game]
        clear_screen()
        ctx = GameContext(account=app.home_account, config=Config.default())
        handler(ctx)  # returns when the game finishes
        clear_screen()
        display_topbar(app.home_account, **CASINO_HEADER_OPTIONS)
        cprint("\nThanks for playing! Goodbye!\n")
    """ -- OLD MAIN --
    try:

        name = ""
        app = NameSelect() #username select
        name = app.run()
        account = Account.generate(name, ACCOUNT_STARTING_BALANCE)
        config = Config.default()
        ctx = GameContext(account=account, config=config)
        while True:
        
            app = MenuSelect(username=name) #Quit or Enter the Casino

            step = app.run()

            if(step == "exit"):
                exit()


            app = GameSelect(username=name) #Select Game Mode
            
            iden = app.run()

            print(f"selected {iden}")
            choice = int(iden[1:])

            selected_game = ALL_GAMES[int(choice) - 1] #Go to Desired Game
            handler = GAME_HANDLERS.get(selected_game)
            clear_screen()
            handler(ctx)  # returns to loop after game finishes



    except (KeyboardInterrupt, EOFError):
        clear_screen()
        display_topbar(account=None, **CASINO_HEADER_OPTIONS)
        cprint("\nGoodbye! (Interrupted)\n")
    """