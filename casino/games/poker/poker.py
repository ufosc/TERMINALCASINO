import random
import os
import shutil

from casino.card_assets import assign_card_art
from casino.cards import Deck, StandardDeck, StandardCard
from casino.stats import GameStats, display_stats
from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar

from itertools import combinations
from collections import Counter


POKER_HEADER = """
┌───────────────────────────────┐
│         ♥ P O K E R ♥         │
└───────────────────────────────┘
"""

HEADER_OPTIONS = {
    "header": POKER_HEADER,
    "margin": 1,
}

SECURITY_GUARD = "👮‍♂️"
SECURITY_MSG = f"""
{SECURITY_GUARD}: Time for you to go.
You have been removed from the casino

"""
YES_OR_NO_PROMPT       = "[Y]es   [N]o"
INVALID_YES_OR_NO_MSG  = "🤵: It's a yes or no, pal. You staying?"
STAY_AT_TABLE_PROMPT   = "🤵: Would you like to stay at the table?"
INVALID_CHOICE_MSG     = "🤵: That's not a choice in this game."
NO_FUNDS_MSG           = "🤵: You don't have enough chips to play. Goodbye."

FULL_DECK: StandardDeck = StandardDeck()


# ---------------------------------------------------------------------------
# Hand evaluation utilities
# ---------------------------------------------------------------------------

def get_card_value(rank: int | str) -> int:
    """Get the numeric value of a card rank."""
    if isinstance(rank, int):
        return rank
    face_values = {"J": 11, "Q": 12, "K": 13, "A": 14}
    if rank in face_values:
        return face_values[rank]
    return int(rank)


def evaluate_hand(cards: list[StandardCard]) -> int:
    """Score a 5-card hand. Returns an integer 1–9."""
    ranks = [get_card_value(card.rank) for card in cards]
    suits = [card.suit for card in cards]

    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    is_flush = 5 in suit_counts.values()
    is_straight = (
        len(rank_counts) == 5 and
        (max(ranks) - min(ranks) == 4 or set(ranks) == {14, 2, 3, 4, 5})
    )

    count_values = sorted(rank_counts.values(), reverse=True)

    if is_straight and is_flush:
        return 9   # Straight Flush
    elif count_values == [4, 1]:
        return 8   # Four of a Kind
    elif count_values == [3, 2]:
        return 7   # Full House
    elif is_flush:
        return 6   # Flush
    elif is_straight:
        return 5   # Straight
    elif count_values == [3, 1, 1]:
        return 4   # Three of a Kind
    elif count_values == [2, 2, 1]:
        return 3   # Two Pair
    elif count_values == [2, 1, 1, 1]:
        return 2   # One Pair
    else:
        return 1   # High Card


def get_partial_hand_score(hand: list[StandardCard]) -> int:
    """Evaluate hands with fewer than 5 cards."""
    if len(hand) < 2:
        return 1

    rank_counts = Counter(card.rank for card in hand)
    count_values = sorted(rank_counts.values(), reverse=True)

    if 4 in count_values:
        return 8   # Four of a Kind
    elif 3 in count_values:
        return 4   # Three of a Kind
    elif count_values.count(2) == 2:
        return 3   # Two Pair
    elif 2 in count_values:
        return 2   # One Pair
    return 1       # High Card


def hand_score(hand: list[StandardCard], board: list[StandardCard]) -> int:
    """Return the best score achievable from hand + board cards."""
    all_cards = hand + board
    if len(all_cards) < 5:
        return get_partial_hand_score(all_cards)

    return max(evaluate_hand(list(combo)) for combo in combinations(all_cards, 5))


def hand_name(score: int) -> str:
    """Human-readable name for a hand score."""
    names = {
        9: "Straight Flush",
        8: "Four of a Kind",
        7: "Full House",
        6: "Flush",
        5: "Straight",
        4: "Three of a Kind",
        3: "Two Pair",
        2: "One Pair",
        1: "High Card",
    }
    return names.get(score, "Unknown Hand")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def display_poker_topbar(ctx: GameContext) -> None:
    display_topbar(ctx.account, **HEADER_OPTIONS)


def print_cards(hand: list[StandardCard]) -> None:
    """Print cards side by side (face-up)."""
    if not hand:
        return
    card_lines = [card.front.strip("\n").splitlines() for card in hand]
    max_lines = max(len(lines) for lines in card_lines)
    for lines in card_lines:
        while len(lines) < max_lines:
            lines.append(" " * len(lines[0]))
    hand_string = "\n".join(
        "  ".join(card_lines[j][i] for j in range(len(hand)))
        for i in range(max_lines)
    )
    cprint(hand_string)


def print_opponent_cards(opponent_hand: list[StandardCard]) -> None:
    """Print opponent's cards face-down."""
    if not opponent_hand:
        cprint("")
        return
    hidden_cards = [card.back for card in opponent_hand]
    hand_string = "\n".join(
        "  ".join(lines)
        for lines in zip(*[card.strip("\n").splitlines() for card in hidden_cards])
    )
    cprint(hand_string)


def print_hand(hand: list[StandardCard], hidden: bool = False) -> None:
    if hidden:
        print_opponent_cards(hand)
    else:
        print_cards(hand)


# ---------------------------------------------------------------------------
# PokerGame class
# ---------------------------------------------------------------------------

class PokerGame:
    """Encapsulates a single session of Texas Hold'em Poker."""

    MIN_BALANCE = 20   # minimum chips required to start a round
    SMALL_BLIND = 10
    BIG_BLIND = 20

    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx
        self.account = ctx.account
        self.min_raise: int = ctx.config.poker_min_raise
        self.stats = GameStats("Poker", self.account.balance)
        self.stubborn = 0

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def play(self) -> None:
        """Run the full poker session (multiple rounds) until the player leaves."""
        if self.account.balance < self.MIN_BALANCE:
            clear_screen()
            display_poker_topbar(self.ctx)
            cprint(NO_FUNDS_MSG)
            cinput("Press enter to continue.")
            return

        while True:
            self._play_round()

            if self.account.balance < self.MIN_BALANCE:
                cprint(NO_FUNDS_MSG)
                cinput("Press enter to continue.")
                self.stats.ending_balance = self.account.balance
                display_stats(self.stats)
                return

            cprint(STAY_AT_TABLE_PROMPT)
            play_again = cinput(YES_OR_NO_PROMPT)

            while play_again not in "YyNn" or play_again == "":
                self.stubborn += 1
                if self.stubborn >= 13:
                    clear_screen()
                    cprint(SECURITY_MSG)
                    self.stats.ending_balance = self.account.balance
                    display_stats(self.stats)
                    return
                clear_screen()
                display_poker_topbar(self.ctx)
                cprint(INVALID_YES_OR_NO_MSG)
                play_again = cinput(YES_OR_NO_PROMPT)

            if play_again in "Nn":
                self.stats.ending_balance = self.account.balance
                display_stats(self.stats)
                return

    # ------------------------------------------------------------------
    # Round lifecycle
    # ------------------------------------------------------------------

    def _play_round(self) -> None:
        """Play a single round of poker."""
        clear_screen()
        display_poker_topbar(self.ctx)

        deck = FULL_DECK
        player_hand: list[StandardCard] = []
        opponent_hand: list[StandardCard] = []
        board: list[StandardCard] = []

        pot = self.SMALL_BLIND
        current_bet = self.BIG_BLIND
        opponent_chips = 1000
        player_folded = False

        # Initial deal
        for _ in range(2):
            player_hand.append(deck.draw())
            opponent_hand.append(deck.draw())

        # --- PRE-FLOP ---
        player_folded, pot, current_bet, opponent_chips = self._betting_round(
            stage="PRE-FLOP",
            player_hand=player_hand,
            opponent_hand=opponent_hand,
            board=board,
            pot=pot,
            current_bet=current_bet,
            opponent_chips=opponent_chips,
            allow_call=True,
        )

        # --- FLOP ---
        if not player_folded:
            deck.draw()  # burn
            for _ in range(3):
                board.append(deck.draw())

            player_folded, pot, current_bet, opponent_chips = self._betting_round(
                stage="FLOP",
                player_hand=player_hand,
                opponent_hand=opponent_hand,
                board=board,
                pot=pot,
                current_bet=0,
                opponent_chips=opponent_chips,
            )

        # --- TURN ---
        if not player_folded:
            deck.draw()  # burn
            board.append(deck.draw())

            player_folded, pot, current_bet, opponent_chips = self._betting_round(
                stage="TURN",
                player_hand=player_hand,
                opponent_hand=opponent_hand,
                board=board,
                pot=pot,
                current_bet=0,
                opponent_chips=opponent_chips,
            )

        # --- RIVER ---
        if not player_folded:
            deck.draw()  # burn
            board.append(deck.draw())

            player_folded, pot, current_bet, opponent_chips = self._betting_round(
                stage="RIVER",
                player_hand=player_hand,
                opponent_hand=opponent_hand,
                board=board,
                pot=pot,
                current_bet=0,
                opponent_chips=opponent_chips,
            )

        # --- SHOWDOWN ---
        self.stats.rounds_played += 1
        self._showdown(player_hand, opponent_hand, board, pot, opponent_chips, player_folded)

        # Reset deck for next round
        deck.generate_deck()

    # ------------------------------------------------------------------
    # Betting
    # ------------------------------------------------------------------

    def _betting_round(
        self,
        stage: str,
        player_hand: list[StandardCard],
        opponent_hand: list[StandardCard],
        board: list[StandardCard],
        pot: int,
        current_bet: int,
        opponent_chips: int,
        allow_call: bool = False,
    ) -> tuple[bool, int, int, int]:
        """
        Handle one betting round.

        Returns (player_folded, new_pot, new_current_bet, new_opponent_chips).
        """
        if allow_call:
            prompt = f"[F]old   [C]all {current_bet}   [R]aise\n"
        else:
            prompt = "[F]old   [C]heck   [R]aise\n"

        self._print_game(stage, player_hand, opponent_hand, board, pot)
        action = cinput(prompt)
        raise_amount = 0

        while True:
            valid = action in "FfCcRr" and action != ""
            needs_raise_input = action.lower() == "r"
            cant_call = allow_call and action.lower() == "c" and self.account.balance < current_bet

            if valid and not needs_raise_input and not cant_call:
                break

            if needs_raise_input:
                raise_amount, validation_msg = get_and_validate_raise_amount(
                    self.min_raise, self.account.balance, current_bet
                )
                if not validation_msg:
                    break
                self._print_game(stage, player_hand, opponent_hand, board, pot, validation_msg)
            elif cant_call:
                self._print_game(
                    stage, player_hand, opponent_hand, board, pot,
                    f"🤵: You don't have enough chips to call {current_bet}."
                )
            else:
                self._print_game(stage, player_hand, opponent_hand, board, pot, INVALID_CHOICE_MSG)

            self.stubborn += 1
            if self.stubborn >= 7:
                clear_screen()
                cprint(SECURITY_MSG)
                # signal fold by returning immediately
                return True, pot, current_bet, opponent_chips

            action = cinput(prompt)

        player_folded = False
        if action.lower() == "f":
            player_folded = True
        elif action.lower() == "c":
            self.account.withdraw(current_bet)
            pot += current_bet
        elif action.lower() == "r":
            current_bet += raise_amount
            self.account.withdraw(current_bet)
            pot += current_bet
            # Opponent always calls a raise
            opponent_chips -= current_bet
            pot += current_bet
        else:
            raise ValueError(f"Invalid action: {action}")

        return player_folded, pot, current_bet, opponent_chips

    # ------------------------------------------------------------------
    # Showdown
    # ------------------------------------------------------------------

    def _showdown(
        self,
        player_hand: list[StandardCard],
        opponent_hand: list[StandardCard],
        board: list[StandardCard],
        pot: int,
        opponent_chips: int,
        player_folded: bool,
    ) -> None:
        """Resolve the round and update balances/stats."""
        if player_folded:
            clear_screen()
            display_poker_topbar(self.ctx)
            cprint("You folded. Opponent wins the pot.")
            opponent_chips += pot
            self.stats.losses += 1
            cprint(f"Your balance: {self.account.balance} chips\n")
            return

        self._print_game("SHOWDOWN", player_hand, opponent_hand, board, pot)

        player_score = hand_score(player_hand, board)
        opponent_score = hand_score(opponent_hand, board)

        if player_score > opponent_score:
            cprint(f"You win with a {hand_name(player_score)}!")
            self.account.deposit(pot)
            self.stats.wins += 1
        elif opponent_score > player_score:
            cprint(f"Opponent wins with a {hand_name(opponent_score)}.")
            opponent_chips += pot
            self.stats.losses += 1
        else:
            cprint(f"It's a tie with both players having a {hand_name(player_score)}.")
            self.account.deposit(pot // 2)
            opponent_chips += pot // 2
            self.stats.pushes += 1

        cprint(f"Your balance: {self.account.balance} chips\n")

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def _print_game(
        self,
        stage: str,
        player_hand: list[StandardCard],
        opponent_hand: list[StandardCard],
        board: list[StandardCard],
        pot: int,
        message: str = "",
    ) -> None:
        clear_screen()
        display_poker_topbar(self.ctx)
        if message:
            cprint(message + "\n")
        cprint(f"=== {stage.upper()} ===\n")
        cprint("Opponent hand:")
        print_hand(opponent_hand, hidden=(stage != "SHOWDOWN"))
        cprint("Board:")
        if not board:
            cprint("No cards on the board yet.")
        else:
            print_hand(board)
        cprint("Your hand:")
        print_hand(player_hand)
        cprint(f"Your current hand type: {hand_name(hand_score(player_hand, board))}")
        cprint(f"Pot: {pot} chips")
        cprint(f"Your balance: {self.account.balance} chips\n")


# ---------------------------------------------------------------------------
# Input validation helper (module-level, reusable by subclasses / variants)
# ---------------------------------------------------------------------------

def get_and_validate_raise_amount(
    min_raise: int, account_balance: int, current_bet: int = 0
) -> tuple[int | None, str]:
    raise_amount = cinput("Raise amount:")
    try:
        raise_amount_int = int(raise_amount)
        if raise_amount_int <= 0:
            return None, "🤵: Raise must be positive number"
        if raise_amount_int < min_raise:
            return None, f"🤵: Raise must be at least {min_raise}"
        if account_balance < current_bet + raise_amount_int:
            return None, "🤵: You don't have enough chips to raise that much."
        return raise_amount_int, ""
    except ValueError:
        return None, "🤵: Raise amount must be number"


# ---------------------------------------------------------------------------
# Public entry point (preserves original interface)
# ---------------------------------------------------------------------------

def play_poker(ctx: GameContext) -> None:
    """Play a poker game."""
    PokerGame(ctx).play()