import random
import sys
from typing import Optional, List
from abc import ABC, abstractmethod
from time import sleep

from casino.cards import StandardCard, StandardDeck, Card
from casino.types import GameContext
from casino.accounts import Account
from casino.utils import clear_screen, cprint, cinput, display_topbar, print_cards
from .constants import *

FULL_DECK: StandardDeck = StandardDeck()

def calc_hand_total(hand: list[StandardCard]) -> int:
    """Calculate the total of each hand."""
    total = 0
    aces  = 0

    for card in hand:
        if not isinstance(card, StandardCard):
            raise ValueError(f"Expected StandardCard, got {type(card)}.")
        if card.rank in {"J", "Q", "K"}:
            # Face card
            total += 10
        elif card.rank == "A":
            # Special case: Ace card
            total += 11
            aces += 1
        else:
            total += int(card.rank)
    
    # Adjust Ace card value if exceeding 21
    while aces > 0 and total > 21:
        total -= 10
        aces  -= 1
    
    return total


class Player:
    """
    Defines a player in a blackjack game.
    """

    def __init__(self, account: Account) -> None:
        self.hand: List[StandardCard] = []

        # Define Player object's attributes in terms of the Account object's attributes
        self.account = account
        self.name = account.name
        self.balance = account.balance

        self.bet = 0

        # Special flags
        self.initial_hand: bool = True
        self.has_blackjack: bool = False
        self.skip: bool = False

    def reveal_hand(self) -> None:
        for card in self.hand:
            print(card)

    def update_account(self) -> Account:
        """
        Update Account object's balance
        """

        # Compare Player.balance with Player's account balance
        difference = self.balance - self.account.balance

        if difference < 0:
            self.account.withdraw(abs(difference))
        elif difference > 0:
            self.account.deposit(difference)
        
        return self.account

    @property
    def hand_total(self):
        """
        Total value of Player's hand

        This attribute holds the sum of the values of all cards in the player's hand.
        It is updated whenever the player's hand changes (e.g., when new cards are drawn).
        """
        return calc_hand_total(self.hand)


class Dealer:
    """
    Defines dealer in blackjack
    """
    
    def __init__(self) -> None:
        self.has_blackjack: bool = False
        self.hand: List[StandardCard] = []

    @property
    def hand_total(self):
        """
        Total value of Dealer's hand

        This attribute holds the sum of the values of all cards in the dealer's hand.
        It is updated whenever the dealer's hand changes (e.g., when new cards are drawn).
        """
        return calc_hand_total(self.hand)

class Blackjack(ABC):
    """
    Abstract base class that sets up Blackjack.
    
    To create a variant of blackjack, inherit from this class.
    All inherited classes must only play one round of that variant of Blackjack
    """
    
    def __init__(self, ctx: GameContext) -> None:
        self.deck: StandardDeck = StandardDeck()
        self.context = ctx
        self.configurations = ctx.config

        self.players: List[Player] = []
        self.dealer: Dealer = Dealer()
        self.round_results: List[str] = []

        # Define a single player
        # NOTE: This must be updated if local multiplayer is added
        player = Player(ctx.account)
        self.players.append(player)

        self.FACE_CARD_VALUES: dict[str, int | List[int]] = {
            "J": 10,
            "Q": 10,
            "K": 10,
            "A": [1, 11]
        }

        self.player_win_status: List[str | None] = [None] * len(self.players)
        
        self.MINIMUM_BET = self.configurations.blackjack_min_bet

    def display_blackjack_topbar(self, bet: Optional[int] = None) -> None:
        """
        Prints top bar for player to view how much they bet.
        """
        display_topbar(self.context.account, **BLACKJACK_HEADER_OPTIONS)
        if bet is not None:
            cprint(f"Bet: {bet}")

    def play_again(self) -> str:
        """
        Asks user if they would like to play again.
        """
        clear_screen()
        self.display_blackjack_topbar()

        # TODO: Refactor so that this function works for multiple players
        for player in self.players:

            # Kick from casino if player has 0 chips
            if player.balance == 0:
                clear_screen()
                cprint("GAME OVER")
                cprint("You have lost all your chips. Security is escorting you out.")
                sys.exit()
            if player.balance < self.MINIMUM_BET:
                cprint(NO_FUNDS_MSG)
                cinput("Press [Enter] to continue")
                return "EXIT"

            # Ask user if they would like to stay at the table  
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
                # Notify user that they must enter a valid input
                cprint(f"{play_again} is not a valid value.")

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


    def reset(self):
        """
        Resets the round state without destroying player objects.
        """
        self.deck = StandardDeck()
        self.dealer.hand = []
        self.dealer.has_blackjack = False
        self.player_win_status = [None] * len(self.players)

        for player in self.players:
            player.hand = []
            player.bet = 0
            player.initial_hand = True
            player.has_blackjack = False
            player.skip = False

class StandardBlackjack(Blackjack):
    def __init__(self, ctx: GameContext) -> None:
        super().__init__(ctx)

    def bet(self):
        """
        Asks all users to submit a bet.
        """
        error_msg = ""

        for player in self.players:
            if player.balance < self.MINIMUM_BET:
                clear_screen()
                self.display_blackjack_topbar()
                cprint(NO_FUNDS_MSG)
                cinput("Press [Enter] to continue.")
                continue

            # Determine player's bet
            while True:
                clear_screen()
                self.display_blackjack_topbar()

                if error_msg != "":
                    cprint(error_msg)
                
                # Ask user how much to bet
                bet_str = cinput(BET_PROMPT).strip()

                # Check that input is a number
                try:
                    bet = int(bet_str)
                    if bet < self.MINIMUM_BET:
                        error_msg = f"The minimum bet is {self.MINIMUM_BET} chips."
                        continue
                except ValueError:
                    error_msg = "Enter a number."
                    continue

                # Check that user has enough money in account to bet
                try:
                    player.bet = bet
                    if player.bet > player.balance:
                        raise ValueError("Player betting more than their balance")

                    player.balance -= bet
                    player.update_account()
                except ValueError:
                    error_msg = f"Insufficient funds. You only have {player.balance} chips."
                    continue
                break

    def deal_cards(self):
        """
        Deals cards out to all players and dealer.
        """
        # Deal cards to players
        for player in self.players:
            cards = [self.deck.draw(), self.deck.draw()]
            for card in cards:
                card.hidden = False
            
            player.hand = cards

        # Deal cards to dealer
        cards = [self.deck.draw(), self.deck.draw()]
        cards[0].hidden = False
        self.dealer.hand = cards

    def blackjack_check(self) -> None:
        """
        Check hands for potential blackjack.

        A blackjack is when:

            - A player has an Ace and a card worth 10 (10, Jack, Queen, King)
            - The dealer has an Ace as its face-up card and a card worth 10 (10, J, Q, K) as its face-down card
        """

        # Check for player blackjacks
        for player in self.players:
            if len(player.hand) != 2:
                player.has_blackjack = False
                continue
            else:
                # Get the name of the cards in the player's hand
                player_ranks = set([card.rank for card in player.hand])

                if "A" in player_ranks:
                    # Check for face card or 10
                    if any(rank in player_ranks for rank in (10, "J", "Q", "K")):
                        player.has_blackjack = True
                
                if player.has_blackjack:
                    continue
        
        # Check for dealer blackjack
        if len(self.dealer.hand) != 2:
            self.dealer.has_blackjack = False
            return
        
        face_up = self.dealer.hand[0]
        hidden  = self.dealer.hand[1]
        self.dealer.has_blackjack = face_up.rank == "A" and hidden.rank in [10, "J", "Q", "K"]
        
    def player_decision(self) -> str:
        """
        Phase where players make decisions. 
        Handles Hit, Stand, Double Down, and Double for Less.
        """
        for i, player in enumerate(self.players):
            if self.player_win_status[i] is not None:
                continue
            
            if player.hand_total == 21:
                self.show_table_state(player)
                if player.has_blackjack:
                    cprint(f"!!! {player.name.upper()} HAS A NATURAL BLACKJACK !!!")
                else:
                    cprint(f"!!! {player.name.upper()} HAS 21 !!!")
                sleep(2.0)
                continue 
                
            while True:
                self.show_table_state(player)
                
                options = "[S]tay   [H]it"
                can_double = player.initial_hand and player.balance > 0
                
                if can_double:
                    if player.balance >= player.bet:
                        options += "   [D]ouble Down"
                    else:
                        options += "   [D]ouble for Less"
                
                action = cinput(options).upper()

                if action in {"S", "STAND", "STAY"}:
                    break

                elif action in {"H", "HIT"}:
                    card = self.deck.draw()
                    card.hidden = False
                    player.hand.append(card)
                    player.initial_hand = False

                    if player.hand_total == 21:
                        self.show_table_state(player)
                        cprint(f"!!! {player.name.upper()} HIT 21 !!!")
                        sleep(2.0)
                        break 
                    elif player.hand_total > 21:
                        self.player_win_status[i] = "lose"
                        break
                
                elif action in {"D", "DOUBLE", "DOUBLE DOWN", "DOUBLE FOR LESS"} and can_double:
                    # Logic to determine how much extra we can actually take
                    if player.balance >= player.bet:
                        extra_bet = player.bet
                        cprint(f"Doubling Down! Adding {extra_bet} to your bet.")
                    else:
                        extra_bet = player.balance
                        cprint(f"Doubling for Less! Adding your remaining {extra_bet} to your bet.")
                    
                    player.balance -= extra_bet
                    player.bet += extra_bet
                    player.update_account()
                    sleep(1.5)

                    card = self.deck.draw()
                    card.hidden = False
                    player.hand.append(card)
                    
                    self.show_table_state(player)
                    if player.hand_total == 21:
                        cprint(f"!!! {player.name.upper()} DOUBLED TO 21 !!!")
                        sleep(2.0)
                    elif player.hand_total > 21:
                        self.player_win_status[i] = "lose"
                    
                    break # Turn always ends after any double action

        return "proceed"

    def show_table_state(self, player: Player):
        """Helper to maintain UI consistency across prompts and pauses."""
        clear_screen()
        self.display_blackjack_topbar(player.bet)
        cprint("Dealer Hand:")
        print_cards(self.dealer.hand)
        cprint(f"Your Hand: {player.hand_total}")
        print_cards(player.hand)

    def dealer_draw(self) -> None:
        """
        Phase of blackjack where dealer draws cards.

        Note that this function uses "soft 17" as a rule due to the
        implementation of calc_hand_total().
        
        "Soft 17" refers to a situation where the dealer has an
        Ace and a 6.
        In that situation, Ace = 11, which means Ace + 6 = 17. 
        Since the dealer must stand on 17, they will stand in this
        specific situation.
        """

        for card in self.dealer.hand:
            card.hidden = False

        while self.dealer.hand_total < 17:
            new_card: StandardCard = self.deck.draw()
            new_card.hidden = False
            self.dealer.hand.append(new_card)

    @staticmethod
    def outcome_msg(result: str, bet: int) -> List[str]:
        """
        Returns a message that notifies the player of the game's status,
        and if they won or lost.
        """

        OUTCOME_MESSAGES = {
            "blackjack_tie": {
                "message": "Player and dealer have a blackjack",
                "bet_result": "Push",
            },
            "tie": {
                "message": "Player and dealer have the same amount!",
                "bet_result": "Push",
            },
            "dealer_blackjack": {
                "message": "Dealer has a blackjack",
                "bet_result": "You lose: -{bet} chips",
            },
            "player_blackjack": {
                "message": "Player has a blackjack",
                "bet_result": "You win: +{bet} chips",
            },
            "player_bust": {
                "message": "You busted.",
                "bet_result": "You lose: -{bet} chips",
            },
            "dealer_bust": {
                "message": "Dealer busted",
                "bet_result": "You win: +{bet} chips",
            },
            "dealer_wins": {
                "message": "Dealer wins",
                "bet_result": "You lose: -{bet} chips",
            },
            "player_wins": {
                "message": "Player wins",
                "bet_result": "You win: +{bet} chips",
            },
        }

        if result not in OUTCOME_MESSAGES:
            raise KeyError(f"Undefined outcome key: {result}")
        if not isinstance(bet, int):
            raise TypeError(f"bet must be `int`. bet data type: {type(bet)}")
        if bet <= 0:
            raise ValueError(f"bet must be greater than 0. bet = {bet}")

        return OUTCOME_MESSAGES[result]

    def check_win(self):
        """
        Phase of blackjack where game checks who won and pays out to users.
        """
        
        self.round_results: List[str] = []
        dealer_won = False

        # Alias for quickly evaluating totals
        d = self.dealer.hand_total

        for i, player in enumerate(self.players):
            win_msg: List[str] = []
            
            # Player total
            p: int = player.hand_total

            # Player's win status
            win_status: str = None

            if player.has_blackjack and self.dealer.has_blackjack:
                win_status = "tie"
                result = "blackjack_tie"
            elif self.dealer.has_blackjack:
                win_status = "lose"
                result = "dealer_blackjack"
            elif player.has_blackjack:
                win_status = "win"
                result = "player_blackjack"
            elif p > 21:
                win_status = "lose"
                result = "player_bust"
            elif d > 21:
                win_status = "win"
                result = "dealer_bust"
            elif p == d:
                win_status = "tie"
                result = "tie"
            elif p < d:
                win_status = "lose"
                result = "dealer_wins"
            elif p > d:
                win_status = "win"
                result = "player_wins"

            outcome_dict = self.outcome_msg(result, player.bet)

            formatted_bet_msg = outcome_dict["bet_result"].format(bet=player.bet)
            full_outcome = f"{outcome_dict['message']}\n{formatted_bet_msg}"

            self.player_win_status[i] = win_status
            self.round_results.append(full_outcome)

    def payout(self):
        """
        Phase of blackjack where winners get paid.
        """

        for i, status in enumerate(self.player_win_status):
            # Determines how much player will get back, relative to their bet
            multiplier = 1

            player = self.players[i]

            if status == "win":
                # Player wins amount they bet
                multiplier = 2

                # Player wins amount they bet PLUS bonus from BLACKJACK_MULTIPLIER
                if player.has_blackjack:
                    multiplier = 1 + BLACKJACK_MULTIPLIER
            elif status == "lose":
                multiplier = 0
            elif status == "tie":
                # Refund bet if tied
                multiplier = 1
            else:
                raise ValueError(f"{status} must be 'win', 'lose', or 'tie' in self.player_win_status")

            # Update account balance
            player.balance += player.bet * multiplier
            player.update_account()
    
    def display_results(self) -> None:
        """
        Displays final result of game, including who won or lost.
        """

        # TODO: rework function so that it works for local multiplayer
        for i, player in enumerate(self.players):
            clear_screen()
            self.display_blackjack_topbar(player.bet)

            cprint(f"Dealer Hand: {self.dealer.hand_total}")
            print_cards(self.dealer.hand)

            cprint(f"Your Hand: {player.hand_total}")
            print_cards(player.hand)

            # Print the detailed message
            cprint("\n" + "="*30)
            cprint(self.round_results[i]) # This is the "Dealer wins / Player lose" text
            cprint("="*30 + "\n")

            # Force the pause here so the user can actually read it
            action = None
            while action != "":
                action = cinput("Press [Enter] to continue...")

    def play_round(self) -> str:
        """
        Plays a single round of Standard Blackjack
        """

        self.bet()
        self.deal_cards()
        self.blackjack_check()

        kicked: str = self.player_decision()
        if kicked == "kicked":
            return "kicked"

        self.dealer_draw()
        self.check_win()
        self.payout()
        self.display_results()

        status: str = self.play_again()
        return status if status else "EXIT"


def play_blackjack(context: GameContext):
    VARIANTS: dict[str, type[Blackjack]] = {
        "standard": StandardBlackjack(context),
    }

    choice = "standard"
    blackjack = VARIANTS[choice]

    while True:
        end_of_round_status = blackjack.play_round()

        if end_of_round_status.upper() == "EXIT":
            cprint("Exiting Blackjack...")
            sleep(1.0)
            break
        elif end_of_round_status.upper() == "NEW_VARIANT":
            # Let user pick a new variant of Blackjack to play
            pass
        elif end_of_round_status.upper() == "CONTINUE":
            blackjack.reset()
            continue
        elif end_of_round_status.upper() == "KICKED":
            action: str = None
            while action != "":
                clear_screen()
                cprint(SECURITY_MSG)
                action = cinput("Press [Enter] to exit.")

            cprint("Exiting Blackjack...")
            sleep(1.0)
        else:
            raise ValueError(f"{end_of_round_status} is not a valid exit status.")
