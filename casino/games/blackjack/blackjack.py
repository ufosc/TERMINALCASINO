import random
import sys
from typing import Optional, List
from abc import ABC, abstractmethod
from time import sleep

from casino.cards import StandardCard, StandardDeck, Card
from casino.stats import GameStats, display_stats
from casino.types import GameContext
from casino.accounts import Account
from casino.utils import clear_screen, cprint, cinput, display_topbar, print_cards
from .constants import *
from .hand import Hand


class Player:
    """
    Defines a player in a blackjack game.
    """

    def __init__(self, account: Account) -> None:
        self.hands: list[Hand] = [] #player has multiple hands

        # Define Player object's attributes in terms of the Account object's attributes
        self.account = account
        self.name = account.name
        self.balance = account.balance

    def update_account(self) -> None:
        """
        Update Account object's balance
        """
        # Compare Player.balance with Player's account balance
        difference = self.balance - self.account.balance
        if difference < 0:
            self.account.withdraw(abs(difference))
        elif difference > 0:
            self.account.deposit(difference)


class Blackjack(ABC):
    """
    Abstract base class that sets up Blackjack.
    
    To create a variant of blackjack, inherit from this class.
    All inherited classes must only play one round of that variant of Blackjack
    """
    
    def __init__(self, ctx: GameContext) -> None:
        self.context = ctx
        self.configurations = ctx.config
        #added a shoe_size constant in config (6 pairs is used)
        shoe_size = self.configurations.blackjack_shoe_size
        self.deck: StandardDeck = StandardDeck(shoe_size)
        #initialize multiple players
        self.players: list[Player] = self._init_players()
        self.dealer_hand: Hand = Hand()
        self.MINIMUM_BET = self.configurations.blackjack_min_bet

    def _init_players(self) -> list[Player]:
        while True:
            try:
                clear_screen()
                self.display_blackjack_topbar()
                num_str = cinput("Enter number of Players: ").strip()
                num_players = int(num_str)
                if 1 <= num_players <= 4:
                    break
                cprint("Please enter a number between 1 and 4.")
            except ValueError:
                cprint("Invalid input. Please enter a number.")
        players = []
        players.append(Player(self.context.account))
        if num_players > 1:
            for i in range(2, num_players + 1):
                name = cinput(f"Enter name for Player {i}: ").strip()
                if not name:
                    name = f"Guest {i}"
                start_bal = self.context.account.balance
                guest_account = Account.generate(name=name, balance=start_bal)
                players.append(Player(guest_account))
        return players

    #top bar do not print bet size
    #player could have two hands with different bet size
    def display_blackjack_topbar(self) -> None:
        if not hasattr(self, 'players') or len(self.players) <= 1:
            display_topbar(self.context.account, **BLACKJACK_HEADER_OPTIONS)
            return
        #print top bar for multi players
        header = BLACKJACK_HEADER_OPTIONS.get("header", "")
        margin = BLACKJACK_HEADER_OPTIONS.get("margin", 1)
        cprint(header)
        header_lines = header.splitlines()
        header_width = max(len(line) for line in header_lines if line.strip())
        player_info_list = []
        for p in self.players:
            player_info_list.append(f"👤 {p.name} 💰 {p.balance}")
        combined_info = "  |  ".join(player_info_list)
        cprint(combined_info.center(header_width))
        print("\n" * margin, end="")

    #a method to render table
    def render_table(self, current_player:Player = None, active_hand_idx: int = 0)->None:
        clear_screen()
        self.display_blackjack_topbar()
        self.dealer_hand.print_hand(label = "Dealer's Hand")
        cprint("="*40)
        # Print all players' hands
        for player in self.players:
            num_hands = len(player.hands)
            for idx, hand in enumerate(player.hands):
                is_active = (player == current_player and idx == active_hand_idx)
                if num_hands > 1:
                    hand_label = f"{player.name} - Hand {idx + 1}"
                else:
                    hand_label = f"{player.name}"
                hand.print_hand(label=hand_label, is_active=is_active)
                print()

    def play_again(self) -> str:
        """
        Asks user if they would like to play again.
        """
        clear_screen()
        self.display_blackjack_topbar()

        # Done: Refactor so that this function works for multiple players
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
                    # Notify user that they must enter a valid input
                    cprint(f"{play_again} is not a valid value.")
                    continue

                return status

    @abstractmethod
    def play_round(self):
        """
        Plays a single round of the Blackjack variant

        Note that most Blackjack variants will execute the following steps in this exact order:

        self.bet()             # 1Users place bets. Take placed bet amount from users
        self.deal_cards()      # 2Deal cards to users
        self.blackjack_check() # 3Check if players or dealer has blackjack. Offer insurance.
        self.player_decision() # 4Player chooses desired moves during round
        self.dealer_draw()     # 5Dealer draws once every player has busted or stands
        self.check_win()       # 6Check which player has won
        self.payout()          # 7Pay players who won or tied the appropriate amount
        self.display_results() # 8Show who won or lost
        """
        pass


    def reset(self, context = None):
        """
        Resets the round state without destroying player objects.
        """
        if context is not None:
            self.context = context
            self.configurations = context.config
        self.dealer_hand = None
        for player in self.players:
            player.hands = []

    #deal card method
    def deal_card(self, hand: Hand, hidden: bool = False) -> None:
        card = self.deck.draw()
        card.hidden = hidden
        hand.cards.append(card)


class StandardBlackjack(Blackjack):
    def __init__(self, ctx: GameContext) -> None:
        super().__init__(ctx)
        self.stats = GameStats("Blackjack (U.S.)", ctx.account.balance)

    #step 1 of 8
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
                prompt = f"🤵 : {player.name}, how much would you like to bet? "
                bet_str = cinput(prompt).strip()

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
                    player.hands = [Hand(bet=bet)] #initialize player hand
                    player.update_account()
                    error_msg = ""#clear error message

                except ValueError:
                    error_msg = f"Insufficient funds. You only have {player.balance} chips."
                    continue
                break

    #step 2 of 8
    def deal_cards(self):
        """
        Deals cards out to all players and dealer.
        """
        for player in self.players:
            for hand in player.hands:
                self.deal_card(hand)
                self.deal_card(hand)
        self.dealer_hand = Hand()
        self.deal_card(self.dealer_hand)
        self.deal_card(self.dealer_hand, hidden=True)

    #step 3 of 8
    def blackjack_check(self) -> bool:
        dealer_bj = self.dealer_hand.is_blackjack
        all_players_done = True
        for player in self.players:
            for hand in player.hands:
                if hand.is_blackjack:
                    if dealer_bj:
                        self.update_hand_results(hand, "blackjack_tie")
                    else:
                        self.update_hand_results(hand, "player_blackjack")
                else:
                    if dealer_bj:
                        self.update_hand_results(hand, "dealer_blackjack")
                    else:
                        all_players_done = False
        if dealer_bj:
            self.dealer_hand.reveal_all()
            cprint("Dealer has a BLACKJACK! Checking hands...")
            sleep(1.0)
            return True  # Player can not continue if dealer BJ
        return all_players_done

    #step 4 of 8
    def player_decision(self) -> None | str:
        """
        Phase where players make decisions. 
        Handles Hit, Stand, Double Down, and Double for Less.
        """
        for i, player in enumerate(self.players):
            stubborn = 0
            hand_idx = 0
            # DO NOT USE FOR LOOP DUE TO POSSIBLE SPLITTING
            while hand_idx < len(player.hands):
                hand = player.hands[hand_idx]
                if hand.is_blackjack:
                    hand_idx += 1
                    continue

                # local method for deciding card value so "Q""J" pair can be split
                def card_val(card):
                    if card.rank in {"J", "Q", "K"}: return 10
                    if card.rank == "A": return 11
                    return int(card.rank)

                while not hand.is_bust and hand.total < 21:
                    self.render_table(current_player=player, active_hand_idx=hand_idx)
                    #build an option string
                    allowed_actions = {"S", "STAND", "H", "HIT"}
                    options_str = "[S]tand   [H]it"
                    can_double = len(hand.cards) == 2 and player.balance >= hand.bet
                    if can_double:
                        allowed_actions.update({"D", "DOUBLE"})
                        options_str += "   [D]ouble"
                    can_split = (len(hand.cards) == 2 and
                                 card_val(hand.cards[0]) == card_val(hand.cards[1]) and
                                 player.balance >= hand.bet)
                    if can_split:
                        allowed_actions.update({"P", "SPLIT"})
                        options_str += "   s[P]lit"

                    action = cinput(options_str).strip().upper()
                    if action not in allowed_actions:
                        stubborn += 1
                        if stubborn >= 13:
                            return "kicked"
                        cprint(INVALID_CHOICE_MSG)
                        continue

                    # Player action stage
                    if action in {"S", "STAND"}:
                        break
                    elif action in {"H", "HIT"}:
                        self.deal_card(hand)
                        cprint("Player drawing...")
                        sleep(0.8)
                        if hand.total == 21:
                            self.render_table(current_player=player, active_hand_idx=hand_idx)
                            cprint("Player hand reached 21!")
                            sleep(1.0)
                            break
                    elif action in {"D", "DOUBLE"}:
                        player.balance -= hand.bet
                        hand.bet *= 2
                        self.deal_card(hand) 
                        player.update_account()
                        cprint(f"💰 Doubling down! New bet: {hand.bet}")
                        cprint("Dealing your final card...")
                        sleep(1.0)
                        break
                    elif action in {"P", "SPLIT"}:
                        player.balance -= hand.bet
                        hand.is_split_hand = True
                        new_hand = Hand(bet=hand.bet, is_split_hand=True)
                        new_hand.cards.append(hand.cards.pop())
                        cprint("✂️ Splitting the pair...")
                        sleep(0.8)
                        self.deal_card(hand)
                        self.deal_card(new_hand)
                        player.hands.insert(hand_idx + 1, new_hand)
                        player.update_account()
                        cprint("Dealing new cards to split hands...")
                        sleep(0.8)
                    # end of not_busted loop
                hand_idx += 1

    #step 5 of 8
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
        self.dealer_hand.reveal_all()
        #dealer draw cards when at least one player hand not bust or not black jack
        dealer_draw_or_not = any(
            not h.is_bust and not h.is_blackjack
            for p in self.players
            for h in p.hands
        )
        if dealer_draw_or_not:
            while self.dealer_hand.total < 17:
                self.render_table()
                cprint("Dealer drawing...")
                sleep(0.8)
                self.deal_card(self.dealer_hand)
        self.render_table()

    #step 6 of 8
    def check_win(self):
        """
        Phase of blackjack where game checks who won and pays out to users.
        """
        dealer_total = self.dealer_hand.total
        dealer_bj = self.dealer_hand.is_blackjack
        dealer_bust = self.dealer_hand.is_bust

        primary_player = self.players[0]
        for player in self.players:
            for hand in player.hands:
                if hand.is_blackjack and dealer_bj:
                    result = "blackjack_tie"
                elif dealer_bj:
                    result = "dealer_blackjack"
                elif hand.is_blackjack:
                    result = "player_blackjack"
                elif hand.is_bust:
                    result = "player_bust"
                elif dealer_bust:
                    result = "dealer_bust"
                elif dealer_total == hand.total:
                    result = "tie"
                elif hand.total < dealer_total:
                    result = "dealer_wins"
                else:  # dealer_total < hand_total:
                    result = "player_wins"
                self.update_hand_results(hand, result)
                if player == primary_player:
                    self.stats.rounds_played += 1
                    if result in {"player_blackjack", "player_wins", "dealer_bust"}:
                        self.stats.wins += 1
                    elif result in {"tie", "blackjack_tie"}:
                        self.stats.pushes += 1
                    else:
                        self.stats.losses += 1

    #step 7 of 8
    def payout(self):
        """
        Phase of blackjack where winners get paid.
        """
        for player in self.players:
            for hand in player.hands:
                player.balance += hand.payout_amount
            player.update_account()

    #step 8 of 8
    def display_results(self) -> None:
        """
        Displays final result of game, including who won or lost.
        """
        self.dealer_hand.reveal_all()
        self.render_table()
        cprint("=" * 40)
        cprint(" ROUND FINISHED - RESULTS AS SHOWN ABOVE ".center(45, "#"))
        cinput("Press [Enter] to continue ... ") 

    #combining the 8 steps
    def play_round(self) -> str:
        """
        Plays a single round of Standard Blackjack
        """
        self.bet()  # Step 1
        self.deal_cards()  # Step 2
        self.render_table()
        is_over = self.blackjack_check()  # Step 3
        if not is_over:
            kicked: str = self.player_decision()  # Step 4
            if kicked == "kicked":
                return "kicked"
            self.dealer_draw()  # Step 5
            self.check_win()  # Step 6
        self.payout()  # Step 7
        self.display_results()  # Step 8

        status: str = self.play_again()
        return status if status else "EXIT"

    #method to update result recorded by each hand object
    def update_hand_results(self, hand: Hand, result_key: str) -> None:
        templates = {
            "player_blackjack": (
                "Player has a BLACKJACK.", "Player win: +{bj_bonus} chips."),
            "player_wins": ("Player wins.", "Player win: +{bet} chips."),
            "dealer_bust": ("Dealer BUSTED.", "Player win: +{bet} chips."),
            "tie": ("Push.", "Tie: 0 chips."),
            "blackjack_tie": ("Push.", "Tie: 0 chips."),
            "player_bust": ("Player BUSTED.", "Player lose: -{bet} chips."),
            "dealer_blackjack": (
                "Dealer has a BLACKJACK.", "Player lose: -{bet} chips."),
            "dealer_wins": ("Dealer wins.", "Player lose: -{bet} chips."),
        }
        msg, bet_res = templates.get(result_key,
                                     ("Unknown outcome.", "Outcome: Unknown."))
        bet_result_str = bet_res.format(
            bet=hand.bet,
            bj_bonus=int(hand.bet * BLACKJACK_MULTIPLIER)
        )

        if result_key == "player_blackjack":
            pay_ratio = 1 + BLACKJACK_MULTIPLIER
        elif result_key in {"player_wins", "dealer_bust"}:
            pay_ratio = 2.0
        elif result_key in {"tie", "blackjack_tie"}:
            pay_ratio = 1.0
        else:
            pay_ratio = 0.0
        payout_amount = int(hand.bet * pay_ratio)

        hand.set_hand_results(result_key, msg, bet_result_str, payout_amount)

def play_blackjack(context: GameContext):
    VARIANTS: dict[str, type[Blackjack]] = {
        "standard": StandardBlackjack(context),
    }

    choice = "standard"
    blackjack = VARIANTS[choice]

    while True:
        end_of_round_status = blackjack.play_round()

        if end_of_round_status.upper() == "EXIT":
            blackjack.stats.ending_balance = context.account.balance
            display_stats(blackjack.stats)
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
            blackjack.stats.ending_balance = context.account.balance
            display_stats(blackjack.stats)
            action: str = None
            while action != "":
                clear_screen()
                cprint(SECURITY_MSG)
                action = cinput("Press [Enter] to exit.")

            cprint("Exiting Blackjack...")
            sleep(1.0)
        else:
            raise ValueError(f"{end_of_round_status} is not a valid exit status.")
