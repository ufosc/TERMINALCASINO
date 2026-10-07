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


#TerminalCasino Textual Homepage Class
class MenuSelect(App):

    TITLE = "Terminal Casino"
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
    #exit {
        text-align: center;
        color:white;
        background:red;
    }
    Horizontal{
        align: center middle;
        height: 3;
    }
    """

    def __init__(self, ctx=None):
        super().__init__()
        self.ctx = ctx  #ctx holds the player's account and game settings.
        self.username = ""


        #If player is returning
        if ctx is not None:
            self.username = ctx.account.name

    def compose(self):
        yield Header()
        yield Footer()
        yield Static("♦ T E R M I N A L  C A S I N O ♦", id="title")

        if self.ctx is not None:
            yield Static(f"Welcome {self.username}!", id="subtitle", markup=False)
        else:
            yield Input(placeholder="Enter Your Name", type="text", id="name-input")
            yield Static("", id="name-error")

        #Game Buttons - four per row so they fit in the terminal.
        for start in range(0, len(ALL_GAMES), 4):
            with Horizontal():
                for index in range(start, min(start + 4, len(ALL_GAMES))):
                    name = ALL_GAMES[index]
                    yield Button(name.title(), id=f"game-{index}")

        with Horizontal():
            yield Button("Exit", id="exit")

    #Check Name
    def accept_name(self):
        if self.ctx is not None:
            return True

        name_input = self.query_one("#name-input", Input)
        error_message = self.query_one("#name-error", Static)
        self.username = name_input.value.strip()

        if self.username == "":
            error_message.update("Please enter your name to play.")
            name_input.focus()
            return False

        else:
            error_message.update("")
            return True

    #Button Actions
    def on_button_pressed(self, event):
        button_id = event.button.id

        if button_id == "exit":
            self.exit()
        elif self.accept_name():
            #Get Game Number
            index = int(button_id.split("-")[1])
            selected_game = ALL_GAMES[index]
            self.exit(selected_game)

# def main_menu(ctx: GameContext) -> None:
#     """
#     Main loop: show welcome, then (if chosen) show game menu, call handler,
#     then return to top-level menu. No recursion used.
#     """
#     account = ctx.account
#     while True:
#         def render_welcome():
#             clear_screen()
#             display_topbar(account, **CASINO_HEADER_OPTIONS)
#             cprint("")  # spacing
#
#         action = prompt_with_refresh(
#             render_fn = render_welcome,
#             prompt = ENTER_OR_QUIT_PROMPT.center(term_width()),
#             error_message = INVALID_CHOICE_PROMPT,
#             validator = lambda x: x.lower() in {"e", "q"},
#             transform = lambda s: s.strip().lower(),
#         )
#
#         if action == "q":
#             clear_screen()
#             display_topbar(account, **CASINO_HEADER_OPTIONS)
#             cprint("\nGoodbye!\n")
#             break  # exit loop -> program ends
#
#         # --- choose game ---
#         def render_choose_game():
#             clear_screen()
#             display_topbar(account, **CASINO_HEADER_OPTIONS)
#             cprint("")  # spacing
#             width = term_width()
#             max_length = max(map(len, ALL_GAMES))
#             cprint("┌" + "─" * 30 + "┐")
#             cprint("│" + " " * 30 + "│")
#             for i, name in enumerate(ALL_GAMES, start=1):
#                 cprint(
#                     f"│{('[{}] {}'.format(i, name.title()) + ' ' * (max_length - len(name))).center(30)}│".center(width)
#                 )
#             cprint("│" + " " * 30 + "│")
#             cprint("└" + "─" * 30 + "┘")
#
#
#
#         choice = prompt_with_refresh(
#             render_fn = render_choose_game,
#             prompt = GAME_CHOICE_PROMPT.center(term_width()),
#             error_message = INVALID_CHOICE_PROMPT,
#             validator = lambda x: x.isdigit() and 1 <= int(x) <= len(ALL_GAMES),
#         )
#
#         selected_game = ALL_GAMES[int(choice) - 1]
#         handler = GAME_HANDLERS.get(selected_game)
#         if handler:
#             clear_screen()
#             handler(ctx)  # returns to loop after game finishes
#         else:
#             clear_screen()
#             display_topbar(account, **CASINO_HEADER_OPTIONS)
#             cprint("\nNo such game!\n")

#Start Casino
def main():
    ctx = None

    while True:
        app = MenuSelect(ctx)
        selected_game = app.run()

        #To quit the game
        if selected_game is None:
            break

        #To create a player account
        if ctx is None:
            account = Account.generate(app.username, ACCOUNT_STARTING_BALANCE)
            config = Config.default()
            ctx = GameContext(account=account, config=config)

        clear_screen()
        handler = GAME_HANDLERS[selected_game]
        handler(ctx)

    clear_screen()
    cprint("\nGoodbye!\n")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        clear_screen()
        display_topbar(account=None, **CASINO_HEADER_OPTIONS)
        cprint("\nGoodbye! (Interrupted)\n")
