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

    def display_topbar(self) -> None:
        display_topbar(self.context.account, **BLACKJACK_HEADER_OPTIONS)

    def render_table(self, player, dealer_hand,
                      active_hand_idx: int | None = None) -> None:
        clear_screen()
        self.display_topbar()
        dealer_hand.print_hand(label="Dealer's Hand")
        cprint("=" * 40)
        num_hands = len(player.hands)
        for idx, hand in enumerate(player.hands):
            is_active = (idx == active_hand_idx)
            label = f"{player.name} - Hand {idx + 1}" if num_hands > 1 else player.name
            hand.print_hand(label=label, is_active=is_active)
            print()

    def prompt_bet(self, player, error_msg: str = "") -> str:
        clear_screen()
        self.display_topbar()
        if error_msg:
            cprint(error_msg)
        return cinput(f"🤵 : {player.name}, how much would you like to bet? ").strip()

    def show_no_funds(self) -> None:
        clear_screen()
        self.display_topbar()
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
