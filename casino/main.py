import shutil
from typing import Callable

from . import games
from .accounts import Account
from .config import Config
from .types import GameContext
from .utils import cprint, cinput, clear_screen, display_topbar, get_theme
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Input, Label,SelectionList, Static, ContentSwitcher, Button
from textual import on
from textual.containers import Horizontal
from textual.widgets.selection_list import Selection




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
    "slots (Expanded)": games.slots.play_slots_expanded,
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

   # name = cinput("Enter your name: ").strip()
   # while not name:
    #    clear_screen()
    #    display_topbar(account=None, **CASINO_HEADER_OPTIONS)
    #    cprint("\nInvalid input. Please enter a valid name.\n")
     #   name = cinput("Enter your name: ").strip()
    
    name =name
    # theme selection
    clear_screen()
    display_topbar(account=None, **CASINO_HEADER_OPTIONS)
    get_theme()


    account = Account.generate(name, ACCOUNT_STARTING_BALANCE)
    config = Config.default()
    ctx = GameContext(account=account, config=config)
    main_menu(ctx)


if __name__ == "__main__":
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

