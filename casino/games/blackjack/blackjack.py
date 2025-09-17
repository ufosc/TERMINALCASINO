import random
import os
import shutil

from casino.card_assets import assign_card_art
from casino.types import Card

BLACKJACK_HEADER = """
┌───────────────────────────────┐
│     ♠ B L A C K J A C K ♠     │
└───────────────────────────────┘

"""

SECURITY_GUARD = "👮‍♂️"
SECURITY_MSG = f"""
{SECURITY_GUARD}: Time for you to go.
You have been removed from the casino

"""
YES_OR_NO_PROMPT       = "[Y]es   [N]o"
INVALID_YES_OR_NO_MSG  = "🤵: It's a yes or no, pal. You staying?"
STAY_AT_TABLE_PROMPT   = "🤵: Would you like to stay at the table?"
INVALID_CHOICE_MSG     = "🤵: That's not a choice in this game."

FULL_DECK: list[Card] = [
    # Clubs
    (2, "c2"), (3, "c3"), (4, "c4"), (5, "c5"), (6, "c6"), (7, "c7"), (8, "c8"), (9, "c9"), (10, "c10"),
    ("J", "cJ"), ("Q", "cQ"), ("K", "cK"), ("A", "cA"),
    # Diamonds
    (2, "d2"), (3, "d3"), (4, "d4"), (5, "d5"), (6, "d6"), (7, "d7"), (8, "d8"), (9, "d9"), (10, "d10"),
    ("J", "dJ"), ("Q", "dQ"), ("K", "dK"), ("A", "dA"),
    # Hearts
    (2, "h2"), (3, "h3"), (4, "h4"), (5, "h5"), (6, "h6"), (7, "h7"), (8, "h8"), (9, "h9"), (10, "h10"),
    ("J", "hJ"), ("Q", "hQ"), ("K", "hK"), ("A", "hA"),
    # Spades
    (2, "s2"), (3, "s3"), (4, "s4"), (5, "s5"), (6, "s6"), (7, "s7"), (8, "s8"), (9, "s9"), (10, "s10"),
    ("J", "sJ"), ("Q", "sQ"), ("K", "sK"), ("A", "sA"),
]


def deal_card(turn: list[Card], deck: list[Card]) -> None:
    """Deal a card to the player."""
    card = random.choice(deck)
    turn.append(card)
    deck.remove(card)


def hand_total(turn: list[Card]) -> int:
    """Calculate the total of each hand."""
    total = 0
    aces = 0
    for card, _ in turn:
        if isinstance(card, int):
            # 1-10
            total += card
        elif card in {"J", "Q", "K"}:
            # face card
            total += 10
        elif card == "A":
            # A special case
            total += 11
            aces += 1
        else:
            raise ValueError(f"Invalid card: {card}")
    # aces adjustment
    while aces > 0 and total > 21:
        total -= 10
        aces -= 1
    return total


def print_dealer_cards(dealer_hand: list[Card]) -> None:
    """Print the dealer's cards side by side."""
    if len(dealer_hand) == 0:
        cprint("")
    # first card shown, rest hidden
    first_card = assign_card_art(dealer_hand[0])
    hidden_card = assign_card_art((0, "flipped"))
    hand_string = "\n".join([
        "  ".join(lines)
        for lines in zip(first_card.strip("\n").splitlines(),
                         hidden_card.strip("\n").splitlines())
    ])
    cprint(hand_string)


def print_cards(hand: list[Card]) -> None:
    """Print the cards side by side."""
    card_lines = [
        assign_card_art(card).strip("\n").splitlines()
        for card in hand
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
            "  ".join(card_lines[j][i] for j in range(len(hand)))
        )
    
    hand_string = "\n".join(combined_lines)
    cprint(hand_string)


def print_hand_total(hand: list[Card], label: str = "Total") -> None:
    """Print the total of the hand."""
    total = hand_total(hand)
    total_string = "Blackjack" if total == 21 else f"{total}"
    cprint(f"{label}: {total_string}")


def print_hand(hand: list[Card], hidden: bool = False) -> None:
    """Print a blackjack hand."""
    if hidden:
        print_dealer_cards(hand)
    else:
        print_cards(hand)
        print_hand_total(hand)


def clear_screen() -> None:
    """Clear the screen."""
    if os.name == "nt":  # Windows
        os.system("cls")
    else:  # Unix
        # clear screen + clear scrollback buffer
        os.system("clear && printf \"\\033[3J\"")


def cprint(*args, sep: str = " ", end: str = "\n") -> None:
    """Print text in the center of the screen."""
    terminal_width = shutil.get_terminal_size().columns
    text = sep.join(map(str, args))

    # split lines and print each one centered
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            print(line.center(terminal_width))
        else:
            print(line.center(terminal_width), end=end)


def cinput(prompt: str = "") -> str:
    """Get input from the user in the center of the screen."""
    terminal_width = shutil.get_terminal_size().columns
    centered_prompt = prompt.center(terminal_width)
    print(centered_prompt)
    
    # move cursor to the center for input
    cursor_padding = (terminal_width // 2) + 1
    print(" " * cursor_padding, end="")
    return input().strip()


def play_blackjack() -> None:
    """Play a blackjack game."""
    continue_game = True
    stubborn = 0 # gets to 7 and you're out

    while continue_game:
        clear_screen()
        cprint(BLACKJACK_HEADER)
        
        # local variables
        player_status = True
        dealer_status = True
        player_bj = False
        dealer_bj = False

        # two decks of cards (values + string IDs)
        deck = FULL_DECK * 2

        # hands
        player_hand = []
        dealer_hand = []

        # initial deal (player first)
        for _ in range(2):
            deal_card(player_hand, deck)
            deal_card(dealer_hand, deck)

        # player BJ check
        if hand_total(player_hand) == 21:
            player_bj = True
            player_status = False

        # dealer BJ check
        if hand_total(dealer_hand) == 21:
            # dealer blackjack in initial deal
            dealer_bj = True
            player_status = False
            dealer_status = False
            cprint("Your hand:")
            print_hand(dealer_hand)
            cprint("Your hand:")
            print_hand(player_hand)

        # player turn
        while player_status:
            # display hands
            cprint("Dealer hand:")
            print_hand(dealer_hand, hidden=True)
            cprint("Your hand:")
            print_hand(player_hand)

            # action choice input
            action = cinput(f"[S]tay   [H]it")
            print()

            # check valid answer
            while action not in "SsHh" or action == "":
                stubborn += 1
                if stubborn >= 13:
                    clear_screen()
                    cprint(SECURITY_MSG)
                    return
                clear_screen()
                cprint(BLACKJACK_HEADER)
                cprint(INVALID_CHOICE_MSG + "\n")
                print_dealer_cards(dealer_hand)
                cprint("Your hand:")
                print_hand(player_hand)
                action = cinput("[S]tay   [H]it")

            clear_screen()
            cprint(BLACKJACK_HEADER)

            # handle action
            if action.lower() == "s":
                player_status = False
            elif action.lower() == "h":
                deal_card(player_hand, deck)
            else:
                raise ValueError(f"Invalid choice: {action}")

            # player bust condition
            if hand_total(player_hand) > 21:
                player_status = False
                dealer_status = False
                # display hands
                cprint("Dealer hand:")
                print_hand(dealer_hand)
                cprint("Your hand:")
                print_hand(player_hand)

            # player 21 end condition
            if hand_total(player_hand) == 21:
                player_status = False

        # dealer turn
        while dealer_status == True:
            # dealer status check/update
            if hand_total(dealer_hand) > 21:
                # display hands
                cprint("Dealer hand:")
                print_hand(dealer_hand)
                cprint("Your hand:")
                print_hand(player_hand)
                dealer_status = False
            elif hand_total(dealer_hand) > 16:
                # display hands
                cprint("Dealer hand:")
                print_hand(dealer_hand)
                cprint("Your hand:")
                print_hand(player_hand)
                dealer_status = False
            else:
                deal_card(dealer_hand, deck)

        ############## WIN CHECKS ##############
        print()
        if player_bj == True and dealer_bj == True:
            cprint(f"Player and dealer have a blackjack")
            cprint(f"Push")
            # player gets back bet, +1 draw
        elif player_bj == False and dealer_bj == True:
            cprint(f"Dealer has a blackjack")
            cprint(f"You lose")
            # player loses bet, +1 loss
        elif player_bj == True and dealer_bj == False:
            cprint(f"Player has a blackjack")
            cprint(f"You win")
            # player gets back 2x bet, +1 win, +1 bj counter
        elif hand_total(player_hand) > 21:
            cprint(f"You busted")
            cprint(f"Dealer wins")
            # player loses bet, +1 loss
        elif hand_total(player_hand) <= 21 and hand_total(dealer_hand) > 21:
            cprint(f"Dealer busted")
            cprint(f"You win")
            # player gets back 2x bet, +1 win
        elif hand_total(player_hand) == hand_total(dealer_hand):
            cprint(f"Player and dealer have same number")
            cprint(f"Push")
            # player gets back bet, +1 draw
        elif hand_total(player_hand) < hand_total(dealer_hand):
            cprint(f"Dealer wins")
            # player loses bet, +1 loss
        elif hand_total(player_hand) > hand_total(dealer_hand):
            cprint(f"Player wins")
            # player gets back 2x bet, +1 win
        else:
            raise ValueError(
                "Unaccounted for win condition!\n"
                f"Player: {hand_total(player_hand)}   "
                f"Dealer: {hand_total(dealer_hand)}"
            )

        # game restart?
        cprint(STAY_AT_TABLE_PROMPT)
        play_again = cinput(YES_OR_NO_PROMPT)
        # check valid answer
        while play_again not in "YyNn" or play_again == "":
            stubborn += 1
            if stubborn >= 13:
                clear_screen()
                cprint(SECURITY_MSG)
                return
            clear_screen()
            cprint(BLACKJACK_HEADER)
            cprint(INVALID_YES_OR_NO_MSG)
            play_again = cinput(YES_OR_NO_PROMPT)

        # play / leave
        if play_again in "Nn":
            clear_screen()
            cprint(f"\nThanks for playing.\n\n")
            continue_game = False
