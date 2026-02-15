from casino.cards import Card
from casino.utils import cprint, print_cards

class Hand:
    def __init__(self, bet: int = 0, is_split_hand: bool = False):
        self.cards: list[Card] = []
        self.bet = bet
        self.is_split_hand = is_split_hand
        # below status data is to be updated by game engine according to rule
        self.result_key = None
        self.payout_amount = 0
        self.outcome_msg = ""
        self.bet_result_str = ""

    #The original calc_hand_total method
    #Whatever the rule, how to calculate total don't change (right?)
    @property
    def total(self) -> int: #NEW
        total = 0
        aces = 0
        for card in self.cards: #NEW
            if card.rank in {"J", "Q", "K"}:
                total += 10
            elif card.rank == "A":
                total += 11
                aces += 1
            else:
                total += int(card.rank)
        while aces > 0 and total > 21:
            total -= 10
            aces -= 1
        return total

    #NEW: method to evaluate if BLACKJACK
    @property
    def is_blackjack(self) -> bool:
        if self.is_split_hand:
            return False # split hand not allowed BJ
        return len(self.cards) == 2 and self.total == 21

    #NEW: method to evaluate if busted
    @property
    def is_bust(self) -> bool:
        return self.total > 21

    def reveal_all(self) -> None:
        for card in self.cards:
            card.hidden = False

    #NEW: method to print hand cards
    def print_hand(self, label:str = "Hand", is_active: bool = False) -> None:
        prefix = " >>> " if is_active else "     "
        #display total if no cards hidden
        has_hidden = any(card.hidden for card in self.cards)
        display_total = "?" if has_hidden else self.total
        #status postfix
        bj_tag = " [BLACKJACK!]" if self.is_blackjack else ""
        bust_tag = " [BUSTED!]" if self.is_bust else ""

        header = f"{prefix}{label} | Bet: {self.bet} | TOTAL: {display_total}{bj_tag}{bust_tag}"
        cprint(header)

        print_cards(self.cards)
        # if outcome_msg is set, print it
        if self.outcome_msg:
            footer = f"{prefix}OUTCOME: {self.outcome_msg}"
            if self.bet_result_str:
                footer += f" ({self.bet_result_str})"
            cprint(footer)

    def set_hand_results(self, result_key: str, msg: str, bet_res: str, payout: int):
        self.result_key = result_key
        self.outcome_msg = msg
        self.bet_result_str = bet_res
        self.payout_amount = payout

    #best not to include hand settlement logic in hand class
    #different blackjack game rules may yield different outcome