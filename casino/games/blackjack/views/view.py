from time import sleep

from casino.utils import clear_screen, cprint, cinput, display_topbar
from ..constants import *


class BlackjackView:
    """
    Owns all terminal rendering and user input for a Blackjack game.

    Game/round logic should never call cinput/cprint/sleep directly —
    it should ask this class to do it.
    """

    def __init__(self, context) -> None:
        self.context = context

    def display_topbar(self, players: list) -> None:
        if len(players) <= 1:
            account = players[0].account
            display_topbar(account, **BLACKJACK_HEADER_OPTIONS)
            return

        header = BLACKJACK_HEADER_OPTIONS.get("header", "")
        margin = BLACKJACK_HEADER_OPTIONS.get("margin", 1)
        cprint(header)
        header_lines = header.splitlines()
        header_width = max(len(line) for line in header_lines if line.strip())
        info = "  |  ".join(f"👤 {p.name} 💰 {p.account.balance}" for p in players)
        cprint(info.center(header_width))
        print("\n" * margin, end="")

    def render_table(self, players: list, dealer_hand, current_player=None,
                      active_hand_idx: int = 0) -> None:
        clear_screen()
        self.display_topbar(players)
        dealer_hand.print_hand(label="Dealer's Hand")
        cprint("=" * 40)
        for player in players:
            num_hands = len(player.hands)
            for idx, hand in enumerate(player.hands):
                is_active = (player == current_player and idx == active_hand_idx)
                label = f"{player.name} - Hand {idx + 1}" if num_hands > 1 else player.name
                hand.print_hand(label=label, is_active=is_active)
                print()

    def prompt_num_players(self, players_so_far: list) -> int:
        while True:
            try:
                self.view.display_topbar()
                num = int(cinput("Enter number of Players: ").strip())
                if 1 <= num <= 4:
                    return num
                cprint("Please enter a number between 1 and 4.")
            except ValueError:
                cprint("Invalid input. Please enter a number.")

    def prompt_player_name(self, index: int) -> str:
        return cinput(f"Enter name for Player {index}: ").strip()

    def prompt_bet(self, player, error_msg: str = "") -> str:
        clear_screen()
        self.display_topbar([player])
        if error_msg:
            cprint(error_msg)
        return cinput(f"🤵 : {player.name}, how much would you like to bet? ").strip()

    def show_no_funds(self, player) -> None:
        clear_screen()
        self.display_topbar([player])
        cprint(NO_FUNDS_MSG)
        cinput("Press [Enter] to continue.")

    def prompt_action(self, options_str: str) -> str:
        return cinput(options_str).strip().upper()

    def show_invalid_choice(self) -> None:
        cprint(INVALID_CHOICE_MSG)

    def announce(self, message: str, pause: float = 0.8) -> None:
        cprint(message)
        sleep(pause)

    def prompt_play_again(self) -> str:
        cprint(STAY_AT_TABLE_PROMPT)
        return cinput(YES_OR_NO_PROMPT)
