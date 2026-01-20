from enum import Enum, auto
from casino.types import GameContext
from .constants import *
from .core import BlackjackCore
from .ui import BlackjackUI

# --- ENUMS & RULES STRATEGY ---

class RoundResult(Enum):
    PLAYER_BUST = auto()
    DEALER_BUST = auto()
    PLAYER_BJ = auto()
    DEALER_BJ = auto()
    PUSH = auto()
    PLAYER_WIN = auto()
    DEALER_WIN = auto()

class EuropeanRules:
    """
    Encapsulates logic specific to European Blackjack (ENHC).
    """
    @staticmethod
    def can_double(hand_total: int) -> bool:
        """Rule: Double down only allowed on hard totals of 9, 10, or 11."""
        return hand_total in {9, 10, 11}

    @staticmethod
    def get_payout(result: RoundResult) -> float:
        if result == RoundResult.PLAYER_BJ:
            return 2.5  # 3:2 Payout
        elif result in {RoundResult.PLAYER_WIN, RoundResult.DEALER_BUST}:
            return 2.0  # 1:1 Payout
        elif result == RoundResult.PUSH:
            return 1.0  # Push
        return 0.0

# --- GAME CONTROLLER ---

class EuropeanBlackjackGame:
    STUBBORN_LIMIT = 13

    def __init__(self, ctx: GameContext):
        self.ctx = ctx
        self.ui = BlackjackUI(ctx)
        self.core: BlackjackCore = None 
        self.bet = 0
        self.stubborn_counter = 0

    def run(self):
        if not self._check_funds(): return

        num_decks = self.ui.prompt_deck_count()
        self.core = BlackjackCore(num_decks)
        
        while True:
            self.play_round()
            if not self._check_funds(): break
            if not self.ask_play_again(): break
        
        self.ui.clear()
        self.ui.print_simple_message("\nThanks for playing.\n\n")

    def _check_funds(self) -> bool:
        if self.ctx.account.balance < self.ctx.config.blackjack_min_bet:
            self.ui.clear()
            self.ui.print_simple_message(MSG_NO_FUNDS)
            self.ui.get_input("Press enter to exit.")
            return False
        return True

    def play_round(self):
        # Betting
        self.bet = self.ui.prompt_bet(self.ctx.config.blackjack_min_bet, self.ctx.account.balance)
        self.ctx.account.withdraw(self.bet)
        
        # Dealing
        self.core.reset_hands()
        self.core.deal_card_to_player()
        self.core.deal_card_to_player()
        self.core.deal_card_to_dealer() # Dealer gets 1 card in EU ruleset

        # Check Natural Blackjack
        if self.core.is_blackjack(self.core.player_hand):
            self.core.deal_card_to_dealer() # Draw 2nd card to check tie
            self.refresh_table(message="Checking dealer hand...")
            
            if self.core.is_blackjack(self.core.dealer_hand):
                self._handle_resolution(RoundResult.PUSH)
            else:
                self._handle_resolution(RoundResult.PLAYER_BJ)
            return

        # Player Turn
        if not self.player_turn_loop():
            self._handle_resolution(RoundResult.PLAYER_BUST)
            return

        # Dealer Turn
        self.dealer_turn_loop()
        
        # Determine Winner
        result = self._determine_winner()
        self._handle_resolution(result)

    def player_turn_loop(self) -> bool:
        first_turn = True
        msg = None
        
        while True:
            self.refresh_table(message=msg)
            msg = None

            can_afford = self.ctx.account.balance >= self.bet
            can_double = (first_turn 
                          and can_afford 
                          and EuropeanRules.can_double(self.core.player_total))

            options = "[S]tay   [H]it" + ("   [D]ouble" if can_double else "")
            action = self.ui.get_input(options).lower().strip()
            
            if action == 's':
                return True
            
            elif action == 'h':
                self.core.deal_card_to_player()
                if self.core.is_busted(self.core.player_hand):
                    return False
                first_turn = False 
            
            elif action == 'd':
                if can_double:
                    self.ctx.account.withdraw(self.bet)
                    self.bet *= 2
                    self.core.deal_card_to_player()
                    return not self.core.is_busted(self.core.player_hand)
                else:
                    if first_turn and can_afford and not EuropeanRules.can_double(self.core.player_total):
                        msg = MSG_EUROPEAN_DOUBLE
                    else:
                        msg = MSG_INVALID_CHOICE
                        self._check_stubbornness()
            else:
                msg = MSG_INVALID_CHOICE
                self._check_stubbornness()

    def dealer_turn_loop(self):
        while self.core.dealer_should_hit():
             self.ui.print_simple_message("Dealer draws...")
             self.core.deal_card_to_dealer()

    def _determine_winner(self) -> RoundResult:
        if self.core.is_busted(self.core.dealer_hand):
            return RoundResult.DEALER_BUST
        
        p_tot = self.core.player_total
        d_tot = self.core.dealer_total
        
        if p_tot > d_tot:
            return RoundResult.PLAYER_WIN
        elif p_tot < d_tot:
            return RoundResult.DEALER_WIN
        else:
            return RoundResult.PUSH

    def _handle_resolution(self, result: RoundResult):
        msg = ""
        payout_mult = EuropeanRules.get_payout(result)

        if result == RoundResult.PLAYER_BUST:
            msg = MSG_PLAYER_BUST
        elif result == RoundResult.DEALER_BUST:
            msg = MSG_DEALER_BUST
        elif result == RoundResult.PLAYER_BJ:
            msg = MSG_PLAYER_BJ
        elif result == RoundResult.DEALER_WIN:
            msg = MSG_DEALER_WIN + f" {self.core.dealer_total} vs {self.core.player_total}"
        elif result == RoundResult.PLAYER_WIN:
            msg = MSG_PLAYER_WIN + f" {self.core.player_total} vs {self.core.dealer_total}"
        elif result == RoundResult.PUSH:
            msg = MSG_PUSH

        # Payout Execution
        if payout_mult > 0:
            winnings = int(self.bet * payout_mult)
            self.ctx.account.deposit(winnings)
            msg += f" (+{winnings})"
        else:
            msg += f" (-{self.bet})"

        self.refresh_table(message=msg)
        self.ui.get_input("Press Enter to continue...")

    def _check_stubbornness(self):
        self.stubborn_counter += 1
        if self.stubborn_counter >= self.STUBBORN_LIMIT:
            self.ui.clear()
            self.ui.print_simple_message(MSG_SECURITY)
            exit()

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