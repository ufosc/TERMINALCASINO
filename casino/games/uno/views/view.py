from casino.utils import clear_screen, cprint, cinput, display_topbar

UNO_HEADER = """
┌───────────────────────────────┐
│             UNO!              │
└───────────────────────────────┘
"""

DRAW_PROMPT = "Would you like to: [D]raw a card or [P]lay a card?"
WHICH_CARD_PROMPT1 = "Which card would you like to play?\n"
WHICH_CARD_PROMPT2 = "Enter card suite and number. Ex: \"red 2\", \"red skip\", \"red reverse\", \"red +2\""
WHICH_CARD_PROMPT3 = "For special cards, only enter \"+4\" or \"wild\""
INVALID_CARD_MSG = "You can't play that card! Enter 'draw' if you would like to draw a card, otherwise press enter to select another card."

# postgame menus: letter + enter
WINNER_MENU_PROMPT = "[S] View stats   [Enter] Exit: "
STATS_NAV_PROMPT = "[N] Next   [P] Prev   [Q] Back: "
INVALID_OPTION_MSG = "Invalid option, try again."

class UnoView:
    """
    Owns all terminal rendering and user input for a game of Uno.

    Game/round logic should never call cinput/cprint/sleep directly —
    it should ask this class to do it.
    """

    def __init__(self, context) -> None:
        self.context = context

    def display_topbar(self, margin=None) -> None:
        clear_screen()
        display_topbar(self.context.account, UNO_HEADER)

    # warning to look away when cards switch
    def player_switch_warning(self, current_player) -> None:
        self.display_topbar()
        cinput(f"Press enter to reveal {current_player.name}'s cards.")
        self.display_topbar()

    def print_hand(self, cards) -> None:
        """Print the cards side by side."""
        card_lines = [
            card.front.strip("\n").splitlines()
            for card in cards
        ]
        max_lines = max(len(lines) for lines in card_lines)

        # pad cards
        for lines in card_lines:
            while len(lines) < max_lines:
                lines.append(" " * len(lines[0]))

        # combine lines horizontally
        combined_lines = []
        for i in range(max_lines):
            combined_lines.append(
                "  ".join(card_lines[j][i] for j in range(len(cards)))
            )

        hand_string = "\n".join(combined_lines)
        cprint(hand_string)

    def prompt_num_players(self) -> int:
        return int(cinput("Input number of players (2-6):"))

    def prompt_player_name(self, i: int) -> str:
        return cinput("Player " + str(i + 1) + " Name: ")

    def show_turn(self, player, current_card) -> None:
        cprint("Player: " + player.name + "\n\nTop card of the Discard pile: \n" + str(current_card) + "\nYour hand:")
        self.print_hand(player.hand)
        cprint("\nCards from your hand that can be played:")
        if (bool(player.playable_cards(current_card))):
            self.print_hand(player.playable_cards(current_card))
        else:
            cprint("\nNONE\n")

    def prompt_draw_or_play(self) -> str:
        answer = cinput(DRAW_PROMPT).lower()
        while (answer != "d" and answer != "p" and answer != "draw" and answer != "play"):
            cprint("Please input either P or D!")
            answer = cinput(DRAW_PROMPT).lower()
        return answer

    def show_drawn_card(self, new_card) -> None:
        cprint("You drew \n" + str(new_card) + " from the pile.")

    def prompt_which_card(self) -> str:
        cprint(WHICH_CARD_PROMPT1)
        cprint(WHICH_CARD_PROMPT2)
        return cinput(WHICH_CARD_PROMPT3)

    def prompt_invalid_card(self) -> str:
        return cinput(INVALID_CARD_MSG).lower()

    def show_winner(self, winner, players) -> None:
        """Winner screen, the user can open the stats or exit."""
        message = ""
        while True:
            self.display_topbar()
            cprint(f"{winner.name} is the winner!\n")
            if message:
                cprint(message)
            choice = cinput(WINNER_MENU_PROMPT).lower()

            if choice == "":
                return
            elif choice == "s":
                self.show_stats_pages(winner, players)
                message = ""
            else:
                message = INVALID_OPTION_MSG

    def show_stats_pages(self, winner, players) -> None:
        """Show stats one player per page, N/P flip the page and Q goes back."""
        # start on the winner page
        index = players.index(winner)
        message = ""
        while True:
            self.display_topbar()
            self.print_player_stats(players[index], index, len(players), winner)
            if message:
                cprint(message)
            choice = cinput(STATS_NAV_PROMPT).lower()

            if choice == "n":
                # modulo so after the last player it goes back to the first one
                index = (index + 1) % len(players)
                message = ""
            elif choice == "p":
                index = (index - 1) % len(players)
                message = ""
            elif choice == "q":
                return
            else:
                message = INVALID_OPTION_MSG

    def print_player_stats(self, player, index, total, winner) -> None:
        """Print the stat page of one player."""
        title = f"{player.name}  (Player {index + 1}/{total})"
        if player is winner:
            title += "  WINNER"

        cprint("═" * 34)
        cprint(title)
        cprint("═" * 34)
        cprint(f"{'Cards left':<20}{len(player.hand):>6}")
        cprint(f"{'Cards played':<20}{player.cards_played:>6}")
        cprint(f"{'Cards drawn':<20}{player.draws_taken:>6}")
        cprint(f"{'Wilds played':<20}{player.wilds_played:>6}")
        cprint(f"{'+4 played':<20}{player.draw4_played:>6}")
        cprint(f"{'+2 played':<20}{player.draw2_played:>6}")
        cprint(f"{'Skips played':<20}{player.skips_played:>6}")
        cprint(f"{'Reverses played':<20}{player.reverses_played:>6}")
        cprint("═" * 34 + "\n")


    def prompt_wild_color(self) -> str:
        new_color = cinput("Choose a color for the wild card (green, yellow, red, or blue)!").lower()
        while (new_color != "green" and
               new_color != "red" and
               new_color != "yellow" and
               new_color != "blue"):
            new_color = cinput("Choose a valid color please (green, yellow, red, or blue).").lower()
        return new_color

    def prompt_wild_color_draw_4(self) -> str:
        new_color = cinput("Choose a color for the +4 card (green, yellow, red, or blue)!").lower()
        while (new_color != "green" and
               new_color != "red" and
               new_color != "yellow" and
               new_color != "blue"):
            new_color = cinput("Choose a valid color please (green, yellow, red, or blue).").lower()
        return new_color

    def prompt_next_player(self) -> None:
        cinput("Press enter when ready to switch to the next player")
