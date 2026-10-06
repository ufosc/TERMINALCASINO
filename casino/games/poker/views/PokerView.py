from casino.cards import StandardCard
from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar

from ..constants import (
    HEADER_OPTIONS,
    SECURITY_MSG,
    YES_OR_NO_PROMPT,
    INVALID_YES_OR_NO_MSG,
    STAY_AT_TABLE_PROMPT,
    NO_FUNDS_MSG,
)
from ..hand import hand_score, hand_name


class PokerView:

    def __init__(self, ctx: GameContext) -> None:
        self.ctx = ctx

# ------------------------------------------------------------------
# Display helpers
# ------------------------------------------------------------------

    def display_topbar(self) -> None:
        display_topbar(self.ctx.account, **HEADER_OPTIONS)

    def print_cards(self, hand: list[StandardCard]) -> None:
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

    def print_opponent_cards(self, opponent_hand: list[StandardCard]) -> None:
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

    def print_hand(self, hand: list[StandardCard], hidden: bool = False) -> None:
        if hidden:
            self.print_opponent_cards(hand)
        else:
            self.print_cards(hand)

# ------------------------------------------------------------------
# Message Helper Functions
# ------------------------------------------------------------------

    def start_round(self) -> None:
        clear_screen()
        self.display_topbar()

    def show_no_funds_screen(self) -> None:
        """Used when the player can't even start a session."""
        clear_screen()
        self.display_topbar()
        cprint(NO_FUNDS_MSG)
        cinput("Press enter to continue.")

    def show_no_funds(self) -> None:
        """Used when the player runs out after a round."""
        cprint(NO_FUNDS_MSG)
        cinput("Press enter to continue.")

    def prompt_stay_at_table(self) -> str:
        cprint(STAY_AT_TABLE_PROMPT)
        return cinput(YES_OR_NO_PROMPT)

    def reprompt_invalid_yes_no(self) -> str:
        clear_screen()
        self.display_topbar()
        cprint(INVALID_YES_OR_NO_MSG)
        return cinput(YES_OR_NO_PROMPT)

    def show_security_message(self) -> None:
        clear_screen()
        cprint(SECURITY_MSG)

    def show_fold(self) -> None:
        clear_screen()
        self.display_topbar()
        cprint("You folded. Opponent wins the pot.")
        cprint(f"Your balance: {self.ctx.account.balance} chips\n")


# ------------------------------------------------------------------
# GAME VIEW
# ------------------------------------------------------------------

    def print_game(
        self,
        stage: str,
        player_hand: list[StandardCard],
        opponent_hand: list[StandardCard],
        board: list[StandardCard],
        pot: int,
        message: str = "",
    ) -> None:
        clear_screen()
        self.display_topbar()
        if message:
            cprint(message + "\n")
        cprint(f"=== {stage.upper()} ===\n")
        cprint("Opponent hand:")
        self.print_hand(opponent_hand, hidden=(stage != "SHOWDOWN"))
        cprint("Board:")
        if not board:
            cprint("No cards on the board yet.")
        else:
            self.print_hand(board)
        cprint("Your hand:")
        self.print_hand(player_hand)
        cprint(f"Your current hand type: {hand_name(hand_score(player_hand, board))}")
        cprint(f"Pot: {pot} chips")
        cprint(f"Your balance: {self.ctx.account.balance} chips\n")