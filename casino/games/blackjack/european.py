from casino.types import GameContext
from .constants import *
from .core import BlackjackCore
from .ui import BlackjackUI

class EuropeanBlackjackGame:
    def __init__(self, ctx: GameContext):
        self.ctx = ctx
        self.ui = BlackjackUI(ctx)
        self.core: BlackjackCore = None 
        self.bet = 0
        self.stubborn_counter = 0

    def run(self):
        if self.ctx.account.balance < self.ctx.config.blackjack_min_bet:
            self.ui.clear()
            self.ui.print_simple_message(MSG_NO_FUNDS)
            self.ui.get_input("Press enter to exit.")
            return

        # Setup
        num_decks = self.ui.prompt_deck_count()
        self.core = BlackjackCore(num_decks)
        
        # Main Game Loop
        playing = True
        while playing:
            self.play_round()
            
            if self.ctx.account.balance < self.ctx.config.blackjack_min_bet:
                self.ui.print_simple_message(MSG_NO_FUNDS)
                break
                
            if not self.ask_play_again():
                break
        
        self.ui.clear()
        self.ui.print_simple_message("\nThanks for playing.\n\n")

    def play_round(self):
        # 1. Betting
        self.bet = self.ui.prompt_bet(self.ctx.config.blackjack_min_bet, self.ctx.account.balance)
        self.ctx.account.withdraw(self.bet)
        
        # 2. Dealing
        self.core.reset_hands()
        self.core.deal_card_to_player()
        self.core.deal_card_to_player()
        self.core.deal_card_to_dealer() # Only 1 card in EU

        # 3. Check Natural Blackjack
        if self.core.is_blackjack(self.core.player_hand):
            # EU RULE FIX: Dealer must draw their second card now 
            # to check if they also have BJ (Push)
            self.core.deal_card_to_dealer() 
            self.refresh_table(hide_dealer_total=False, message="Checking dealer hand...")
            self.resolve_round(player_bj=True)
            return

        # 4. Player Turn
        if not self.player_turn_loop():
            self.resolve_round(player_busted=True)
            return

        # 5. Dealer Turn
        self.dealer_turn_loop()
        
        # 6. Resolution
        self.resolve_round()

    def player_turn_loop(self) -> bool:
        """
        Manages input loop. Returns False if busted, True if stayed.
        """
        first_turn = True
        message_state = None
        
        while True:
            # Render with current message
            self.refresh_table(hide_dealer_total=False, message=message_state)
            message_state = None 

            options = "[S]tay   [H]it"
            valid = "sh"
            
            # EU RULE FIX: Double down usually restricted to hard 9, 10, or 11
            can_double = (
                first_turn 
                and self.ctx.account.balance >= self.bet 
                and self.core.player_total in [9, 10, 11]
            )

            if can_double:
                options += "   [D]ouble"
                valid += "d"
            
            action = self.ui.get_input(options).lower().strip()
            
            if action not in valid or not action:
                if action == 'd' and not can_double:
                    message_state = "👮: European rules restrict doubling to 9, 10, or 11."
                else:
                    message_state = MSG_INVALID_CHOICE
                    self.stubborn_counter += 1
                
                if self.stubborn_counter >= 13:
                    self.ui.clear()
                    self.ui.print_simple_message(MSG_SECURITY)
                    exit()
                continue 
            
            first_turn = False
            
            if action == 's':
                return True
            elif action == 'h':
                self.core.deal_card_to_player()
                if self.core.is_busted(self.core.player_hand):
                    return False
            elif action == 'd':
                self.ctx.account.withdraw(self.bet)
                self.bet *= 2
                self.core.deal_card_to_player()
                return not self.core.is_busted(self.core.player_hand)

    def dealer_turn_loop(self):
        # In EU, dealer starts with 1 card. Logic is same, but visually distinctive.
        while self.core.dealer_total < 17:
             self.ui.print_simple_message("Dealer draws...") 
             self.core.deal_card_to_dealer()
             # Small delay or refresh could go here for visual effect
             self.refresh_table()

    def resolve_round(self, player_bj=False, player_busted=False):
        p_tot = self.core.player_total
        d_tot = self.core.dealer_total
        d_bj = self.core.is_blackjack(self.core.dealer_hand)
        
        msg = ""
        if player_busted:
            msg = f"You busted. Dealer wins: -{self.bet}"
        elif player_bj:
            if d_bj:
                msg = "Both have Blackjack. Push."
                self.ctx.account.deposit(self.bet)
            else:
                msg = f"Blackjack! You win: +{self.bet}"
                self.ctx.account.deposit(self.bet * 2.5)
        elif self.core.is_busted(self.core.dealer_hand):
            msg = f"Dealer busted. You win: +{self.bet}"
            self.ctx.account.deposit(self.bet * 2)
        elif p_tot > d_tot:
            msg = f"You win: +{self.bet}"
            self.ctx.account.deposit(self.bet * 2)
        elif p_tot < d_tot:
            msg = f"Dealer wins: -{self.bet}"
        else:
            msg = "Push."
            self.ctx.account.deposit(self.bet)
        
        self.refresh_table(hide_dealer_total=False, message=msg)
        self.ui.get_input("Press Enter to continue...")

    def refresh_table(self, hide_dealer_total=False, message=None):
        self.ui.render_game_state(
            player_hand=self.core.player_hand,
            dealer_hand=self.core.dealer_hand,
            player_total=self.core.player_total,
            dealer_total=self.core.dealer_total,
            bet=self.bet,
            hide_dealer_total=hide_dealer_total,
            message=message 
        )

    def ask_play_again(self) -> bool:
        error_msg = None
        while True:
            self.refresh_table(hide_dealer_total=False, message=error_msg or MSG_STAY_TABLE)
            
            choice = self.ui.get_input(PROMPT_YES_NO).lower().strip()
            if choice in ['y', 'yes']: return True
            if choice in ['n', 'no']: return False
            
            error_msg = MSG_INVALID_CHOICE
            self.stubborn_counter += 1

def play_european_blackjack(ctx: GameContext):
    game = EuropeanBlackjackGame(ctx)
    game.run()