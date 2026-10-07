from time import sleep

from casino.stats import GameStats, display_stats
from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput
from ..constants import *
from ..hand import Hand
from ..base import Blackjack


class EuropeanBlackjack(Blackjack):
    """
    European Blackjack (ENHC - European No Hole Card).

    Differs from Standard Blackjack:
    - The dealer is dealt only one card up front. The second card is
      drawn just before the dealer's turn, or immediately if a player
      has a natural blackjack, to check for a push.
    - Double down is only offered on a first-turn hard total of 9, 10, or 11.
    - Splitting is not offered.
    """

    def __init__(self, ctx: GameContext) -> None:
        super().__init__(ctx)
        self.stats = GameStats("Blackjack (E.U.)", ctx.account.balance)

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
        Deals two cards to the player and a single card to the dealer.

        European rules use no hole card: the dealer's second card isn't
        drawn until after the player has finished acting.
        """
        for hand in self.player.hands:
            self.deal_card(hand)
            self.deal_card(hand)

        self.dealer_hand = Hand()
        self.deal_card(self.dealer_hand)

    def blackjack_check(self) -> bool:
        any_player_blackjack = any(
            hand.is_blackjack for hand in self.player.hands
        )

        dealer_bj = False
        if any_player_blackjack:
            # Draw the dealer's second card early so a player's natural
            # blackjack can be checked against a dealer blackjack (push)
            # instead of paying out before the dealer's hand is known.
            self.deal_card(self.dealer_hand)
            dealer_bj = self.dealer_hand.is_blackjack

        all_hands_done = True
        for hand in self.player.hands:
            if hand.is_blackjack:
                if dealer_bj:
                    self.update_hand_results(hand, "blackjack_tie")
                else:
                    self.update_hand_results(hand, "player_blackjack")
            elif dealer_bj:
                self.update_hand_results(hand, "dealer_blackjack")
            else:
                all_hands_done = False

        if dealer_bj:
            cprint("Dealer has a BLACKJACK! Checking hands...")
            sleep(1.0)

        return all_hands_done

    def player_decision(self) -> None | str:
        """
        Phase where the player makes decisions.

        Handles Hit, Stand, and Double Down. European rules only allow
        doubling on a first-turn hard total of 9, 10, or 11, and do not
        offer splitting.
        """
        player = self.player
        stubborn = 0

        for hand in player.hands:
            if hand.is_blackjack:
                continue

            first_turn = True
            while not hand.is_bust and hand.total < 21:
                self.view.render_table(self.player, self.dealer_hand)

                allowed_actions = {"S", "STAND", "H", "HIT"}
                options_str = "[S]tand   [H]it"

                can_double = (
                    first_turn
                    and hand.total in {9, 10, 11}
                    and player.account.balance >= hand.bet
                )
                if can_double:
                    allowed_actions.update({"D", "DOUBLE"})
                    options_str += "   [D]ouble"

                action = cinput(options_str).strip().upper()
                if action not in allowed_actions:
                    stubborn += 1
                    if stubborn >= 13:
                        return "kicked"
                    if first_turn and player.account.balance >= hand.bet and hand.total not in {9, 10, 11}:
                        cprint(MSG_EUROPEAN_DOUBLE)
                    else:
                        cprint(INVALID_CHOICE_MSG)
                    continue

                # Player action stage
                if action in {"S", "STAND"}:
                    break

                elif action in {"H", "HIT"}:
                    self.deal_card(hand)
                    cprint("Player drawing...")
                    sleep(0.8)
                    first_turn = False
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

    def dealer_draw(self) -> None:
        """
        Draws the dealer's second (no-hole) card if it wasn't already drawn
        during blackjack_check, then draws to a total of 17 or higher.
        """
        dealer_can_draw = any(
            not h.is_bust and not h.is_blackjack
            for h in self.player.hands
        )
        if dealer_can_draw:
            if len(self.dealer_hand.cards) == 1:
                self.deal_card(self.dealer_hand)

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
                raise ValueError(
                    f"Invalid game result for hand total {hand.total} vs dealer total {dealer_total}."
                )

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
        self.view.render_table(self.player, self.dealer_hand)
        cprint("=" * 40)
        cprint(" ROUND FINISHED - RESULTS AS SHOWN ABOVE ".center(45, "#"))
        cinput("Press [Enter] to continue ... ")

    #combining the 8 steps
    def play_round(self) -> str:
        """
        Plays a single round of European Blackjack
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


def play_european_blackjack(context: GameContext):
    blackjack = EuropeanBlackjack(context)

    while True:
        end_of_round_status = blackjack.play_round()

        if end_of_round_status.upper() == "EXIT":
            blackjack.stats.ending_balance = context.account.balance
            display_stats(blackjack.stats)
            cprint("Exiting Blackjack...")
            sleep(1.0)
            break
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
