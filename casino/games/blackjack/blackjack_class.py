import random
from typing import Optional, List

from casino.cards import StandardCard, StandardDeck, Card
from casino.types import GameContext
from accounts import Account

from casino.utils import clear_screen, cprint, cinput, display_topbar

from CONSTANTS import *


class Player:
    """
    Defines a player in a blackjack game.
    """

    def __init__(self, account: GameContext.account) -> None:
        self.hand: List[StandardCard] = []

        # Define Player object's attributes in terms of the Account object's attributes
        self.name = account.name
        self.balance = account.balance

        self.bet = 0

        # Special flags
        self.has_blackjack: bool = False
        self.skip: bool = False

    def reveal_hand(self) -> None:
        for card in self.hand:
            print(card)

    def update_account(self) -> GameContext.account:
        """
        Update Account object's balance
        """
        account.balance = self.balance
        return account


class Dealer:
    """
    Defines dealer in blackjack
    """
    
    def __init__(self) -> None:
        self.has_blackjack: bool = False
        self.hand: List[StandardCard] = []


class Blackjack:
    """
    Abstract base class that sets up Blackjack.
    
    To create a variant of blackjack, inherit from this class.
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

    @staticmethod
    def display_topbar(ctx: GameContext, bet: Optional[int]) -> None:
        """
        Prints top bar for player to view how much they bet.
        """
        display_topbar(ctx.account, **BLACKJACK_HEADER_OPTIONS)
        if bet is not None:
            cprint(f"Bet: {bet}")

    @staticmethod
    def calc_hand_total(hand: list[StandardCard]) -> int:
        """
        Calculate the total value of a hand.
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

    def bet(self):
        """
        Asks all users to submit a bet.
        """
        MINIMUM_BET = self.configurations.blackjack_min_bet
        error_msg = ""

        for player in self.players:
            if player.balance < MINIMUM_BET:
                clear_screen()
                display_blackjack_topbar(self.context, None)
                cprint(NO_FUNDS_MSG)
                cinput("Press [Enter] to continue.")
                continue

            # Determine player's bet
            while True:
                clear_screen()
                display_blackjack_topbar(self.context, None)

                if error_msg != "":
                    cprint(error_msg)
                
                # Ask user how much to bet
                bet_str = cinput(BET_PROMPT).strip()

                # Check that input is a number
                try:
                    bet = int(bet_str)
                    if bet < MINIMUM_BET:
                        error_msg = f"The minimum bet is {MINIMUM_BET} chips."
                        continue
                except ValueError:
                    error_msg = INVALID_BET_MSG
                    continue

                # Check that user has enough money in account to bet
                try:
                    account.withdraw(bet)
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
            cards = [deck.draw(), deck.draw()]
            for card in cards:
                card.hidden = False
            
            player.hand = cards

        # Deal cards to dealer
        cards = [deck.draw(), deck.draw()]
        cards[0].hidden = False
        dealer.hand = cards

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
        if len(dealer.hand != 2):
            dealer.has_blackjack = False
            return
        
        face_up = dealer.hand[0]
        hidden  = dealer.hand[1]
        dealer.has_blackjack = face_up.rank == "A" and hidden.rank in [10, "J", "Q", "K"]
        
    def player_decision(self):
        """
        Phase of blackjack where players make decision.
        """
        pass

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

        for card in dealer.hand:
            card.hidden = False

        while dealer_total < 17:
            new_card: StandardCard = deck.draw()
            new_card.hidden = False
            dealer.hand.append(new_card)

    @staticmethod
    def outcome_msg(result: str, bet: int) -> List[str]:
        """
        Returns a message that notifies the player of the game's status,
        and if they won or lost.
        """

        if result == "blackjack_tie":
            return ["Player and dealer have a blackjack", "Push"]
        if result == "dealer_blackjack":
            return ["Dealer has a blackjack", f"You lose: -{bet} chips"]
        if result == "player_blackjack":
            return ["Player has a blackjack", f"You win: +{bet} chips"]
        if result == "player_bust":
            return ["You busted", f"Dealer wins: -{bet} chips"]
        if result == "dealer_bust":
            return ["Dealer busted", f"You win: +{bet} chips"]
        if result == "tie":
            return ["Player and dealer have the same amount!", "Push"]
        if result == "dealer_wins":
            return [f"Dealer wins: -{bet} chips"]
        if result == "player_wins":
            return [f"Player wins: +{bet} chips"]

        raise ValueError("Undefined outcome code")

    def check_win(self):
        """
        Phase of blackjack where game checks who won and pays out to users.
        """
        
        win_msgs: List[str] = []
        dealer_won = False
        dealer_total: int = self.calc_hand_total(dealer.hand)
        # Alias for quickly evaluating totals
        d = dealer_total

        # Tracks which player won, lost, or tied with dealer
        player_win_status: List[bool] = [None] * len(self.players)

        for player in self.players:
            win_msg: List[str] = []
            
            # Player total
            p: int = self.calc_hand_total(player.hand)

            player_won: bool = None
            tie = False

            if player_bj and dealer_bj:
                tie = True
                result = "blackjack_tie"
            elif dealer_bj:
                player_won = False
                result = "dealer_blackjack"
            elif player_bj:
                player_won = True
                result = "player_blackjack"
            elif p > 21:
                player_won = False
                result = "player_bust"
            elif d > 21:
                player_won = True
                result = "dealer_bust"
            elif p == d:
                tie = True
                result = "tie"
            elif p < d:
                player_won = False
                result = "dealer_wins"
            elif p > d:
                player_won = True
                result = "player_wins"

            win_msg: str = result
            win_msg = "\n".join(outcome_msg(result, player.bet))

            if player_won:
                player.balance += player.bet
                player.update_account()
            elif player_won == False:
                player.balance -= player.bet
                player.update_account()
        
            # Print final result to player
            print(win_msg)

    def payout(self):
        """
        Phase of blackjack where winners get paid.
        """
        pass
    
    def display_results(self) -> None:
        """
        Displays final result of game, including who won or lost.
        """
        pass

    def play_again(self) -> bool:
        """
        Asks user if they would like to play again.
        """
        for player in self.players:
            if player.balance < self.MINIMUM_BET:
                cprint(NO_FUNDS_MSG)
                cinput("Press [Enter] to continue")
                return False

            # Ask user if they would like to stay at the table  
            cprint(STAY_AT_TABLE_PROMPT)
            play_again = CINPUT(YES_OR_NO_PROMPT)

            if play_again.upper() == "YES" or play_again == "Y" or play_again == "":
                return True
            elif play_again.upper() == "NO" or play_again == "N":
                clear_screen()
                cprint("\nThanks for playing!\n\n")
                return False
