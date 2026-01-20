from typing import Optional
from casino.types import GameContext
from casino.cards import Card
from casino.utils import clear_screen, cprint, cinput, display_topbar
from .constants import *

class BlackjackUI:
    """
    Handles all visual output and user input.
    """
    def __init__(self, ctx: GameContext):
        self.ctx = ctx

    def clear(self):
        clear_screen()

    def get_input(self, prompt: str) -> str:
        return cinput(prompt)

    def _render_cards_ascii(self, hand: list[Card]) -> str:
        if not hand: 
            return ""
        card_lines = [card.front.strip("\n").splitlines() for card in hand]
        max_lines = max(len(lines) for lines in card_lines)
        
        # Pad shorter cards if necessary
        for lines in card_lines:
            while len(lines) < max_lines:
                lines.append(" " * len(lines[0]))

        combined_lines = []
        for i in range(max_lines):
            combined_lines.append("  ".join(card_lines[j][i] for j in range(len(hand))))
        
        return "\n".join(combined_lines)

    def render_game_state(self, 
                          player_hand: list[Card], 
                          dealer_hand: list[Card], 
                          player_total: int, 
                          dealer_total: int, 
                          bet: int,
                          hide_dealer_total: bool = False,
                          message: Optional[str] = None):
        """
        Main render function. 
        Layout:
        1. Header
        2. Bet Info
        3. SYSTEM/ERROR MESSAGES (Requested Location)
        4. Cards
        """
        self.clear()
        
        # 1. Header
        display_topbar(self.ctx.account, **HEADER_OPTIONS)
        
        # 2. Bet Info
        cprint(f"Bet: {bet}")
        
        # 3. Message Area (The requested change)
        if message:
            cprint(f"\n{message}\n")
        else:
            cprint("\n") # Empty space to keep layout stable

        # 4. Dealer Area
        cprint("Dealer hand:")
        cprint(self._render_cards_ascii(dealer_hand))
        if not hide_dealer_total:
             cprint(f"Total: {dealer_total}")
        else:
             cprint("Total: ?")
        
        # 5. Player Area
        cprint("-" * 20)
        cprint("Your hand:")
        cprint(self._render_cards_ascii(player_hand))
        cprint(f"Total: {player_total}")

    def prompt_bet(self, min_bet: int, balance: int) -> int:
        """Loops until a valid bet is entered."""
        error = None
        while True:
            self.clear()
            display_topbar(self.ctx.account, **HEADER_OPTIONS)
            
            # Message area for betting screen
            if error:
                cprint(f"\n{error}\n")
            else:
                cprint("\n")

            val = self.get_input(MSG_BET_PROMPT).strip()
            try:
                bet = int(val)
                if bet < min_bet:
                    error = f"The minimum bet is {min_bet} chips."
                elif bet > balance:
                    error = f"Insufficient funds. Balance: {balance} chips."
                else:
                    return bet
            except ValueError:
                error = MSG_INVALID_BET

    def prompt_deck_count(self) -> int:
        error = None
        while True:
            self.clear()
            display_topbar(self.ctx.account, **HEADER_OPTIONS)
            
            if error: 
                cprint(f"\n{error}\n")
            else:
                cprint("\n")
            
            val = self.get_input(MSG_DECK_COUNT).strip()
            try:
                count = int(val)
                if count > 0: return count
                error = MSG_INVALID_DECK
            except ValueError:
                error = MSG_INVALID_NUMBER

    def print_simple_message(self, msg: str):
        """For end of game messages or blocking alerts."""
        cprint(msg)