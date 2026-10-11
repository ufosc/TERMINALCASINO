from casino.cards import StandardDeck, StandardCard
from casino.stats import GameStats, display_stats
from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput

from .constants import *
from .hand import hand_score, hand_name
from .views import PokerView


FULL_DECK: StandardDeck = StandardDeck()


class Poker:
    """Encapsulates a single session of Texas Hold'em Poker."""

    MIN_BALANCE = 20
    SMALL_BLIND = 10
    BIG_BLIND = 20

    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx
        self.account = ctx.account
        self.min_raise: int = ctx.config.poker_min_raise
        self.stats = GameStats("Poker", self.account.balance)
        self.stubborn = 0
        self.view = PokerView(ctx)

    def play(self) -> None:
        """Run the full poker session until the player leaves."""

        if self.account.balance < self.MIN_BALANCE:
            clear_screen()
            self.view.display_topbar()
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
                self.view.display_topbar()
                cprint(INVALID_YES_OR_NO_MSG)

                play_again = cinput(YES_OR_NO_PROMPT)

            if play_again in "Nn":
                self.stats.ending_balance = self.account.balance
                display_stats(self.stats)
                return

    def _play_round(self) -> None:
        """Play one round of poker."""

        clear_screen()
        self.view.display_topbar()

        deck = FULL_DECK

        player_hand: list[StandardCard] = []
        opponent_hand: list[StandardCard] = []
        board: list[StandardCard] = []

        pot = self.SMALL_BLIND
        current_bet = self.BIG_BLIND
        opponent_chips = 1000

        player_folded = False

        # Deal two cards to each player
        for _ in range(2):
            player_hand.append(deck.draw())
            opponent_hand.append(deck.draw())

        # ---------------------------
        # PRE-FLOP
        # ---------------------------

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

        # ---------------------------
        # FLOP
        # ---------------------------

        if not player_folded:
            deck.draw()  # burn card

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

        # ---------------------------
        # TURN
        # ---------------------------

        if not player_folded:
            deck.draw()  # burn card
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

        # ---------------------------
        # RIVER
        # ---------------------------

        if not player_folded:
            deck.draw()  # burn card
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

        # ---------------------------
        # SHOWDOWN
        # ---------------------------

        self.stats.rounds_played += 1

        self._showdown(
            player_hand,
            opponent_hand,
            board,
            pot,
            opponent_chips,
            player_folded,
        )

        # Reset the deck for the next round
        deck.generate_deck()

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

        Returns:
            player_folded,
            pot,
            current_bet,
            opponent_chips
        """

        if allow_call:
            prompt = f"[F]old   [C]all {current_bet}   [R]aise\n"
        else:
            prompt = "[F]old   [C]heck   [R]aise\n"

        self.view.print_game(
            stage,
            player_hand,
            opponent_hand,
            board,
            pot,
        )

        action = cinput(prompt)

        raise_amount = 0

        while True:
            valid = action in "FfCcRr" and action != ""

            needs_raise_input = action.lower() == "r"

            cant_call = (
                allow_call
                and action.lower() == "c"
                and self.account.balance < current_bet
            )

            if valid and not needs_raise_input and not cant_call:
                break

            if needs_raise_input:
                raise_amount, validation_msg = get_and_validate_raise_amount(
                    self.min_raise,
                    self.account.balance,
                    current_bet,
                )

                if not validation_msg:
                    break

                self.view.print_game(
                    stage,
                    player_hand,
                    opponent_hand,
                    board,
                    pot,
                    validation_msg,
                )

            elif cant_call:
                self.view.print_game(
                    stage,
                    player_hand,
                    opponent_hand,
                    board,
                    pot,
                    f"🤵: You don't have enough chips to call {current_bet}.",
                )

            else:
                self.view.print_game(
                    stage,
                    player_hand,
                    opponent_hand,
                    board,
                    pot,
                    INVALID_CHOICE_MSG,
                )

            self.stubborn += 1

            if self.stubborn >= 7:
                clear_screen()
                cprint(SECURITY_MSG)

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

    def _showdown(
        self,
        player_hand: list[StandardCard],
        opponent_hand: list[StandardCard],
        board: list[StandardCard],
        pot: int,
        opponent_chips: int,
        player_folded: bool,
    ) -> None:
        """Resolve the round and update balances and statistics."""

        if player_folded:
            clear_screen()
            self.view.display_topbar()

            cprint("You folded. Opponent wins the pot.")

            opponent_chips += pot

            self.stats.losses += 1

            cprint(
                f"Your balance: "
                f"{self.account.balance} chips\n"
            )

            return

        self.view.print_game(
            "SHOWDOWN",
            player_hand,
            opponent_hand,
            board,
            pot,
        )

        player_score = hand_score(
            player_hand,
            board,
        )

        opponent_score = hand_score(
            opponent_hand,
            board,
        )

        if player_score > opponent_score:
            cprint(
                f"You win with a "
                f"{hand_name(player_score)}!"
            )

            self.account.deposit(pot)

            self.stats.wins += 1

        elif opponent_score > player_score:
            cprint(
                f"Opponent wins with a "
                f"{hand_name(opponent_score)}."
            )

            opponent_chips += pot

            self.stats.losses += 1

        else:
            cprint(
                f"It's a tie with both players having a "
                f"{hand_name(player_score)}."
            )

            self.account.deposit(pot // 2)

            opponent_chips += pot // 2

            self.stats.pushes += 1

        cprint(
            f"Your balance: "
            f"{self.account.balance} chips\n"
        )


def get_and_validate_raise_amount(
    min_raise: int,
    account_balance: int,
    current_bet: int = 0,
) -> tuple[int | None, str]:
    """Validate the player's raise amount."""

    raise_amount = cinput("Raise amount:")

    try:
        raise_amount_int = int(raise_amount)

        if raise_amount_int <= 0:
            return None, "🤵: Raise must be positive number"

        if raise_amount_int < min_raise:
            return None, f"🤵: Raise must be at least {min_raise}"

        if account_balance < current_bet + raise_amount_int:
            return (
                None,
                "🤵: You don't have enough chips to raise that much.",
            )

        return raise_amount_int, ""

    except ValueError:
        return None, "🤵: Raise amount must be number"
