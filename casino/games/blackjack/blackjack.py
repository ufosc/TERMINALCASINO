import random
from typing import Optional, List
from abc import ABC, abstractmethod
from time import sleep

from casino.cards import StandardCard, StandardDeck, Card
from casino.types import GameContext
from casino.accounts import Account

from casino.utils import clear_screen, cprint, cinput, display_topbar, print_cards

from casino.games.blackjack.CONSTANTS import *


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
        self.has_blackjack: bool = False
        self.skip: bool = False

    def reveal_hand(self) -> None:
        for card in self.hand:
            print(card)

    def update_account(self) -> Account:
        """
        Update Account object's balance
        """
        self.account.balance = self.balance
        return self.account


class Dealer:
    """
    Defines dealer in blackjack
    """
    
    def __init__(self) -> None:
        self.has_blackjack: bool = False
        self.hand: List[StandardCard] = []


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

    @staticmethod
    def calc_hand_total(hand: list[StandardCard]) -> int:
        """
        Calculate the total value of a hand.

        Aces count as 11 unless the total exceeds 21, in which case they are reduced to 1
        as many times as needed to avoid busting.

        NOTE: Busting can still occur even after Aces are reduced

        Examples
        --------
        >>> calc_hand_total([A♠, 9♥])      # Ace counted as 11 (default)
        20

        >>> calc_hand_total([A♠, K♥, 9♦])  # Ace reduced from 11 to 1
        20

        >>> calc_hand_total([A♠, A♥, 9♦])  # One Ace reduced from 11 to 1
        21

        >>> calc_hand_total([A♠, A♥, A♦, 9♣])  # Multiple Aces reduced from 11 to 1
        12

        >>> calc_hand_total([A♠, A♥, 10♦, 10♣]) # Multiple Aces reduced from 11 to 1. Results in bust
        22
        """

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

    @abstractmethod
    def bet(self):
        """
        Asks users to submit a bet
        """
        pass

    @abstractmethod
    def deal_cards(self):
        pass

    @abstractmethod
    def player_decision(self):
        pass

    @abstractmethod
    def dealer_draw(self):
        pass

    @abstractmethod
    def check_win(self):
        pass

    @abstractmethod
    def payout(self):
        pass

    @abstractmethod
    def display_results(self):
        pass

    def play_again(self) -> str:
        """
        Asks user if they would like to play again.
        """
        clear_screen()
        self.display_blackjack_topbar()

        # TODO: Refactor so that this function works for multiple players
        for player in self.players:
            if player.balance < self.MINIMUM_BET:
                cprint(NO_FUNDS_MSG)
                cinput("Press [Enter] to continue")
                return

            # Ask user if they would like to stay at the table  
            cprint(STAY_AT_TABLE_PROMPT)
            play_again = cinput(YES_OR_NO_PROMPT)

            status: str = None
            if play_again.upper() in {"", "Y", "YES"}:
                status = "CONTINUE"
            elif play_again.upper() in {"V", "VARIANT"}:
                status = "VARIANT"
            elif play_again.upper() == "NO" or play_again == "N":
                clear_screen()
                cprint("\nThanks for playing!\n\n")
                status = "EXIT"
            else:
                # Notify user that they must enter a valid input
                pass

            return status

    @abstractmethod
    def play_round(self):
        """
        Plays a single round of the Blackjack variant

        Note that most Blackjack setups will execute the following steps in this exact order:

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
                    error_msg = INVALID_BET_MSG
                    continue

                # Check that user has enough money in account to bet
                try:
                    player.account.withdraw(bet)
                    player.bet = bet
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
        
    def player_decision(self) -> None | str:
        """
        Phase of blackjack where players make decision.
        """
        for i, player in enumerate(self.players):
            # Players with win status of None have not won, lost, or drawn yet.
            if self.player_win_status[i] != None:
                continue
            
            while True:
                cprint("Dealer Hand:")
                print_cards(self.dealer.hand)
                cprint("Player Hand:")
                print_cards(player.hand)

                action = cinput(f"[S]tand   [H]it")
                print()

                # Check valid answer. If user surpasses `stubborn` threshold, call security
                # and kick user out
                stubborn = 0
                while action.upper() not in {"S", "STAND", "H", "HIT"}:
                    stubborn += 1
                    if stubborn >= 13:
                        return "kicked"

                    clear_screen()
                    self.display_blackjack_topbar(player.bet)
                    cprint(INVALID_CHOICE_MSG + "\n")

                    cprint("Dealer Hand:")
                    print_cards(self.dealer.hand)
                    cprint("Player Hand:")
                    print_cards(player.hand)
                    action = cinput("[S]tay   [H]it")

                if action.upper() in {"S", "STAND"}:
                    break
                elif action.upper() in {"H", "HIT"}:
                    player.hand += self.deck.draw()

                    if calc_hand_total(player.hand) > 21:
                        self.player_win_status[i] = "lose"
                        break

    def dealer_draw(self) -> None:
        """
        Phase of blackjack where dealer draws cards.

        Note that this function uses "soft 17" as a rule due to the
        implementation of Blackjack.calc_hand_total().
        
        "Soft 17" refers to a situation where the dealer has an
        Ace and a 6.
        In that situation, Ace = 11, which means Ace + 6 = 17. 
        Since the dealer must stand on 17, they will stand in this
        specific situation.
        """
        dealer_total = self.calc_hand_total(self.dealer.hand)

        for card in self.dealer.hand:
            card.hidden = False

        while dealer_total < 17:
            new_card: StandardCard = self.deck.draw()
            new_card.hidden = False
            self.dealer.hand.append(new_card)
            dealer_total = self.calc_hand_total(self.dealer.hand)

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
        
        win_msgs: List[str] = []
        dealer_won = False
        dealer_total: int = self.calc_hand_total(self.dealer.hand)
        # Alias for quickly evaluating totals
        d = dealer_total

        for i, player in enumerate(self.players):
            win_msg: List[str] = []
            
            # Player total
            p: int = self.calc_hand_total(player.hand)

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

            win_msg: str = result
            win_msg = "\n".join(self.outcome_msg(result, player.bet))

            self.player_win_status[i] = win_status
        
            # Print final result to player
            cprint(win_msg)

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
        for player in self.players:
            clear_screen()
            self.display_blackjack_topbar(player.bet)

            cprint("Dealer hand:")
            print_cards(self.dealer.hand)

            cprint("Your hand:")
            print_cards(player.hand)

        display_msg: dict[str, str] = {
            "win": "You win!"
        }

        for msg in self.player_win_status:
            cprint(msg)

            action: str | None = None
            while action != "":
                action = cinput("Press [Enter] to leave Results")

    def play_round(self):
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
        return status


def play_blackjack(context: GameContext):
    VARIANTS: dict[str, type[Blackjack]] = {
        "standard": StandardBlackjack(context),
    }

    blackjack = VARIANTS["standard"]

    while True:
        status = blackjack.play_round()

        if status.upper() == "EXIT":
            cprint("Exiting Blackjack...")
            sleep(0.5)
            break
        elif status.upper() == "NEW_VARIANT":
            # Let user pick a new variant of Blackjack to play
            pass
        elif status.upper() == "CONTINUE":
            continue
        elif status.upper() == "KICKED":
            action: str = None
            while action != "":
                clear_screen()
                cprint(SECURITY_MSG)
                action = cinput("Press [Enter] to exit.")

            cprint("Exiting Blackjack...")
            sleep(0.5)
        else:
            raise ValueError(f"{status} is not a valid status.")
