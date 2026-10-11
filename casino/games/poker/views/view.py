from casino.cards import StandardCard
from casino.utils import clear_screen, cprint, display_topbar

from ..constants import HEADER_OPTIONS
from ..hand import hand_score, hand_name


class PokerView:
    def __init__(self, ctx):
        self.ctx = ctx

    def display_topbar(self) -> None:
        display_topbar(self.ctx.account, **HEADER_OPTIONS)

    def print_cards(self, hand: list[StandardCard]) -> None:
        if not hand:
            return

        card_lines = [
            card.front.strip("\n").splitlines()
            for card in hand
        ]

        max_lines = max(len(lines) for lines in card_lines)

        for lines in card_lines:
            while len(lines) < max_lines:
                lines.append(" " * len(lines[0]))

        hand_string = "\n".join(
            "  ".join(
                card_lines[j][i]
                for j in range(len(hand))
            )
            for i in range(max_lines)
        )

        cprint(hand_string)

    def print_opponent_cards(
        self,
        opponent_hand: list[StandardCard]
    ) -> None:

        if not opponent_hand:
            cprint("")
            return

        hidden_cards = [
            card.back
            for card in opponent_hand
        ]

        hand_string = "\n".join(
            "  ".join(lines)
            for lines in zip(
                *[
                    card.strip("\n").splitlines()
                    for card in hidden_cards
                ]
            )
        )

        cprint(hand_string)

    def print_hand(
        self,
        hand: list[StandardCard],
        hidden: bool = False
    ) -> None:

        if hidden:
            self.print_opponent_cards(hand)
        else:
            self.print_cards(hand)

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
        self.print_hand(
            opponent_hand,
            hidden=(stage != "SHOWDOWN")
        )

        cprint("Board:")

        if not board:
            cprint("No cards on the board yet.")
        else:
            self.print_hand(board)

        cprint("Your hand:")
        self.print_hand(player_hand)

        cprint(
            f"Your current hand type: "
            f"{hand_name(hand_score(player_hand, board))}"
        )

        cprint(f"Pot: {pot} chips")
        cprint(
            f"Your balance: "
            f"{self.ctx.account.balance} chips\n"
        )
