from time import sleep

from casino.stats import GameStats, display_stats
from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput
from ..constants import *
from ..hand import Hand
from ..base import Blackjack


class StandardBlackjack(Blackjack):
    def __init__(self, ctx: GameContext) -> None:
        super().__init__(ctx)
        self.stats = GameStats("Blackjack (U.S.)", ctx.account.balance)

    def bet(self):
        """
        Asks the user to submit a bet.
        """
        error_msg = ""
        player = self.player

        if player.account.balance < self.MINIMUM_BET:
            self.view.show_no_funds()
            return

        # Determine player's bet
        while True:
            bet_str = self.view.prompt_bet(player, error_msg)

            try:
                bet = int(bet_str)
            except ValueError:
                error_msg = "Enter a number."
                continue

            if bet < self.MINIMUM_BET:
                error_msg = f"The minimum bet is {self.MINIMUM_BET} chips."
                continue
            elif bet > player.account.balance:
                error_msg = f"Insufficient funds. You only have {player.account.balance} chips."
                continue

            player.bet = bet
            player.account.balance -= bet
            player.hands = [Hand(bet=bet)]
            error_msg = ""
            break

    def deal_cards(self):
        """
        Deals cards out to the player and dealer.
        """
        for hand in self.player.hands:
            self.deal_card(hand)
            self.deal_card(hand)

        self.dealer_hand = Hand()
        self.deal_card(self.dealer_hand)
        self.deal_card(self.dealer_hand, hidden=True)

    def blackjack_check(self) -> bool:
        dealer_bj = self.dealer_hand.is_blackjack
        all_hands_done = True

        for hand in self.player.hands:
            if hand.is_blackjack:
                if dealer_bj:
                    self.update_hand_results(hand, "blackjack_tie")
                else:
                    self.update_hand_results(hand, "player_blackjack")
            else:
                if dealer_bj:
                    self.update_hand_results(hand, "dealer_blackjack")
                else:
                    all_hands_done = False
        if dealer_bj:
            self.dealer_hand.reveal_all()
            cprint("Dealer has a BLACKJACK! Checking hands...")
            sleep(1.0)
            return True  # Player can not continue if dealer BJ
        return all_hands_done

    def player_decision(self) -> None | str:
        """
        Phase where the player makes decisions.

        Handles Hit, Stand, Double Down, and Double for Less.
        """
        player = self.player
        stubborn = 0
        hand_idx = 0

        # DO NOT USE FOR LOOP DUE TO POSSIBLE SPLITTING
        while hand_idx < len(player.hands):
            hand = player.hands[hand_idx]
            if hand.is_blackjack:
                hand_idx += 1
                continue

            # Decides face card values
            def card_val(card):
                if card.rank in {"J", "Q", "K"}: return 10
                if card.rank == "A": return 11
                return int(card.rank)

            while not hand.is_bust and hand.total < 21:
                self.view.render_table(self.player, self.dealer_hand)

                allowed_actions = {"S", "STAND", "H", "HIT"}
                options_str = "[S]tand   [H]it"

                can_double = len(hand.cards) == 2 and player.account.balance >= hand.bet
                if can_double:
                    allowed_actions.update({"D", "DOUBLE"})
                    options_str += "   [D]ouble"

                can_split = (
                    len(hand.cards) == 2 and
                    card_val(hand.cards[0]) == card_val(hand.cards[1]) and
                    player.account.balance >= hand.bet
                )
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
                        self.view.render_table(self.player, self.dealer_hand)
                        cprint("Player hand reached 21!")
                        sleep(1.0)
                        break

                elif action in {"D", "DOUBLE"}:
                    player.account.balance -= hand.bet
                    hand.bet *= 2

                    self.deal_card(hand)

                    cprint(f"💰 Doubling down! New bet: {hand.bet}")
                    cprint("Dealing your final card...")
                    sleep(1.0)
                    break

                elif action in {"P", "SPLIT"}:
                    # Turn current hand into two new hands, each with two cards
                    player.account.balance -= hand.bet

                    hand.is_split_hand = True
                    new_hand = Hand(bet=hand.bet, is_split_hand=True)
                    new_hand.cards.append(hand.cards.pop())

                    cprint("✂️ Splitting the pair...")

                    sleep(0.8)
                    self.deal_card(hand)
                    self.deal_card(new_hand)

                    player.hands.insert(hand_idx + 1, new_hand)
                    cprint("Dealing new cards to split hands...")
                    sleep(0.8)
                # end of not_busted loop
            hand_idx += 1

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

        # Dealer draws cards when player has not busted or received blackjack
        dealer_can_draw = any(
            not h.is_bust and not h.is_blackjack
            for h in self.player.hands
        )
        if dealer_can_draw:
            while self.dealer_hand.total < 17:
                self.view.render_table(self.player, self.dealer_hand)
                cprint("Dealer drawing...")
                sleep(0.8)
                self.deal_card(self.dealer_hand)

        self.view.render_table(self.player, self.dealer_hand)

    def check_win(self):
        """
        Check who won and pays out to winners
        """
        dealer_total = self.dealer_hand.total
        dealer_bj = self.dealer_hand.is_blackjack
        dealer_bust = self.dealer_hand.is_bust

        for hand in self.player.hands:
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
            elif dealer_total < hand.total:
                result = "player_wins"
            else:
                raise ValueError(f"Invalid game result. result = {result}")

            self.update_hand_results(hand, result)

            self.stats.rounds_played += 1
            if result in {"player_blackjack", "player_wins", "dealer_bust"}:
                self.stats.wins += 1
            elif result in {"tie", "blackjack_tie"}:
                self.stats.pushes += 1
            else:
                self.stats.losses += 1

    def payout(self):
        """
        Phase of blackjack where winners get paid.
        """
        for hand in self.player.hands:
            self.player.account.balance += hand.payout_amount

    def display_results(self) -> None:
        """
        Displays final result of game, including who won or lost.
        """
        self.dealer_hand.reveal_all()
        self.view.render_table(self.player, self.dealer_hand)
        cprint("=" * 40)
        cprint(" ROUND FINISHED - RESULTS AS SHOWN ABOVE ".center(45, "#"))
        cinput("Press [Enter] to continue ... ")

    #combining the 8 steps
    def play_round(self) -> str:
        """
        Plays a single round of Standard Blackjack
        """
        self.bet()
        self.deal_cards()
        is_over = self.blackjack_check()
        if not is_over:
            kicked: str = self.player_decision()
            if kicked == "kicked":
                return "kicked"
            self.dealer_draw()
            self.check_win()
        self.payout()
        self.display_results()

        status: str = self.play_again()
        return status if status else "EXIT"

    def update_hand_results(self, hand: Hand, result_key: str) -> None:
        """
        Picks final message based on win state
        """
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
            pay_ratio = 2
        elif result_key in {"tie", "blackjack_tie"}:
            pay_ratio = 1
        else:
            pay_ratio = 0
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
