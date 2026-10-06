from textual.app import App, ComposeResult
from textual.containers import Vertical, Center
from textual.widgets import Button, Input, Static

# import from actual games like "from blackjack import play_blackjack"
from casino import games
from casino.accounts import Account
from casino.config import Config
from casino.types import GameContext
from casino.utils import clear_screen

GAME_HANDLERS = {
    "blackjack (U.S.)": games.blackjack.play_blackjack,
    "blackjack (EU)": games.blackjack.play_european_blackjack,
    "poker": games.poker.play_poker,
    "roulette": games.roulette.play_roulette,
    "slots": games.slots.play_slots,
    "slots (expanded)": games.slots.play_slots_expanded,
    "uno": games.uno.play_uno,
}

class CasinoHomepage(App):
    # Basic header
    CSS = """
    Screen {
        align: center middle;
    }
    #header-text {
        text-style: bold;
        padding: 2;
        content-align: center middle;
    }
    Button {
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            with Center():
                # Terminal Casino Header
                yield Static("=== TERMINAL CASINO ===", id="header-text")

                # Player Name Input
                yield Input(placeholder="Enter your name here...", id="player-name")

                # Game Selection Buttons
                yield Button("Play Blackjack", id="btn_blackjack", variant="primary")
                yield Button("Play EU Blackjack", id="btn_eublackjack", variant="primary")
                yield Button("Play Poker", id="btn_poker", variant="primary")
                yield Button("Play Roulette", id="btn_roulette", variant="primary")
                yield Button("Play Slots", id="btn_slots", variant="primary")
                yield Button("Play Expanded Slots", id="btn_exslots", variant="primary")
                yield Button("Play Uno", id="btn_uno", variant="primary")
                yield Button("Quit", id="btn_quit", variant="error")

    def on_mount(self) -> None:
        # Automatically focus the input box when the app starts
        self.query_one("#player-name", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        #button gets pressed
        button_id = event.button.id

        if button_id == "btn_quit":
            self.exit("quit")
        else:
            # Grab the text from the input box
            player_name = self.query_one("#player-name", Input).value
            if not player_name:
                player_name = "Anonymous Player"

            # Exit Textual and pass back a dictionary with the chosen game and name
            self.exit({"game": button_id, "player_name": player_name})


#runs after homepage exits
if __name__ == "__main__":
    app = CasinoHomepage()
    result = app.run()

    if result and result != "quit":
        game_choice = result["game"]
        player_name = result["player_name"]

        # Can change starting balance if needed
        ACCOUNT_STARTING_BALANCE = 1000
        account = Account.generate(player_name, ACCOUNT_STARTING_BALANCE)
        config = Config.default()
        ctx = GameContext(account=account, config=config)

        clear_screen()
        print(f"\nWelcome to the floor, {player_name}!")
        print("Switching to standard terminal mode...\n")

        # Launch the game
        if game_choice == "btn_blackjack":
            games.blackjack.play_blackjack(ctx)

        elif game_choice == "btn_eublackjack":
            games.blackjack.play_european_blackjack(ctx)

        elif game_choice == "btn_poker":
            games.poker.play_poker(ctx)

        elif game_choice == "btn_roulette":
            games.roulette.play_roulette(ctx)

        elif game_choice == "btn_slots":
            games.slots.play_slots(ctx)

        elif game_choice == "btn_exslots":
            games.slots.play_slots_expanded(ctx)

        elif game_choice == "btn_uno":
            games.uno.play_uno(ctx)