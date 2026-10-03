import sys
from abc import ABC, abstractmethod

from casino.cards import StandardDeck
from casino.types import GameContext
from casino.accounts import Account
from casino.utils import clear_screen, cprint, cinput
from .constants import *
from .hand import Hand
from .views import BlackjackView


class Player:
    """
    Defines a player in a blackjack game.
    """

    def __init__(self, account: Account) -> None:
        self.hands: list[Hand] = []

        self.account = account
        self.name = account.name


class Blackjack(ABC):
    """
    Abstract base class that sets up Blackjack.

    To create a variant of blackjack, inherit from this class.
    All inherited classes must only play one round of that variant of Blackjack
    """

    def __init__(self, ctx: GameContext) -> None:
        self.context = ctx
        self.configurations = ctx.config
        self.view = BlackjackView(ctx)
        shoe_size = self.configurations.blackjack_shoe_size
        self.deck: StandardDeck = StandardDeck(shoe_size)
        self.player: Player = Player(ctx.account)
        self.dealer_hand: Hand = Hand()
        self.MINIMUM_BET = self.configurations.blackjack_min_bet

    def play_again(self) -> str:
        """
        Asks user if they would like to play again.
        """
        self.view.display_topbar()

        # Kick from casino if player has 0 chips
        if self.player.account.balance == 0:
            clear_screen()
            cprint("GAME OVER")
            cprint("You have lost all your chips. Security is escorting you out.")
            sys.exit()
        if self.player.account.balance < self.MINIMUM_BET:
            cprint(NO_FUNDS_MSG)
            cinput("Press [Enter] to continue")
            return "EXIT"

        # Ask user if they would like to stay at the table
        while True:# avoid raising error
            cprint(STAY_AT_TABLE_PROMPT)
            play_again: str = cinput(YES_OR_NO_PROMPT)

            status: str = ""
            if play_again.upper() in {"", "Y", "YES"}:
                status = "CONTINUE"
            elif play_again.upper() in {"V", "VARIANT"}:
                status = "VARIANT"
            elif play_again.upper() in {"N", "NO"}:
                clear_screen()
                cprint("\nThanks for playing!\n\n")
                status = "EXIT"
            else:
                cprint(f"{play_again} is not a valid value.")
                continue

            return status

    @abstractmethod
    def play_round(self):
        """
        Plays a single round of the Blackjack variant

        Note that most Blackjack variants will execute the following steps in this exact order:

        self.bet()             # Users place bets. Take placed bet amount from users
        self.deal_cards()      # Deal cards to users
        self.blackjack_check() # Check if players or dealer has blackjack. Offer insurance.
        self.player_decision() # Player chooses desired moves during round
        self.dealer_draw()     # Dealer draws once every player has busted or stands
        self.check_win()       # Check which player has won
        self.payout()          # Pay players who won or tied the appropriate amount
        self.display_results() # Show who won or lost
        """
        pass


    def reset(self, context = None):
        """
        Resets the round state without destroying the player object.
        """
        if context is not None:
            self.context = context
            self.configurations = context.config
        self.dealer_hand = None
        self.player.hands = []

    #deal card method
    def deal_card(self, hand: Hand, hidden: bool = False) -> None:
        card = self.deck.draw()
        card.hidden = hidden
        hand.cards.append(card)
