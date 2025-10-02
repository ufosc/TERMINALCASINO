import random
from typing import Optional

from casino.card_assets import assign_card_art
from casino.types import Card, GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar

BLACKJACK_HEADER = """
┌───────────────────────────────┐
│     ♠ B L A C K J A C K ♠     │
└───────────────────────────────┘
"""

BLACKJACK_HEADER_OPTIONS = {
    "header": BLACKJACK_HEADER,
    "margin": 1,
}

SECURITY_GUARD = "👮‍♂️"
SECURITY_MSG = f"""
{SECURITY_GUARD}: Time for you to go.
You have been removed from the casino

"""
YES_OR_NO_PROMPT       = "[Y]es   [N]o"
DECK_NUMBER_SELECTION  = "🤵: How many decks would you like to play with?"
DECK_NUMBER_BOUNDS_MSG = "🤵: That won't work, please be serious. Try again."
INVALID_NUMBER_MSG     = "🤵: Invalid number. Try again."
INVALID_YES_OR_NO      = "🤵: It's a yes or no, pal. You staying?"
STAY_AT_TABLE_PROMPT   = "🤵: Would you like to stay at the table?"
INVALID_CHOICE_MSG     = "🤵: That's not a choice in this game."
BET_PROMPT             = "🤵: How much would you like to bet?"
INVALID_BET_MSG        = "🤵: That's not a valid bet."
NO_FUNDS_MSG           = "🤵: You don't have enough chips to play. Goodbye."

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


def display_blackjack_topbar(ctx: GameContext, bet: Optional[int]) -> None:
    display_topbar(ctx.account, **BLACKJACK_HEADER_OPTIONS)
    if bet is not None:
        cprint(f"Bet: {bet}")


def play_blackjack(ctx: GameContext) -> None:
    """Play a blackjack game."""
    account = ctx.account
    min_bet = ctx.config.blackjack_min_bet
    if account.balance < min_bet:
        clear_screen()
        display_blackjack_topbar(ctx, None)
        cprint(NO_FUNDS_MSG)
        cinput("Press enter to continue.")
        return
    continue_game = True
    stubborn = 0 # gets to 7 and you're out
    err_msg = None
    while (True):
        clear_screen()
        display_blackjack_topbar(ctx, None)
        # let user choose number of decks being dealt
        if err_msg is not None:
            cprint(err_msg)
        decks_str = cinput(DECK_NUMBER_SELECTION).strip()
        try:
            decks = int(decks_str)
        except ValueError:
            err_msg = INVALID_NUMBER_MSG
            continue
        if decks <= 0:
            err_msg = DECK_NUMBER_BOUNDS_MSG
            continue
        break

    while continue_game:
        # determine the bet amount
        err_msg = None
        while True:
            clear_screen()
            display_blackjack_topbar(ctx, None)
            if err_msg is not None:
                cprint(err_msg)
            bet_str = cinput(BET_PROMPT).strip()
            try:
                bet = int(bet_str)
                if bet < min_bet:
                    err_msg = f"The minimum bet is {min_bet} chips."
                    continue
            except ValueError:
                err_msg = INVALID_BET_MSG
                continue
            try:
                account.withdraw(bet)
            except ValueError:
                err_msg = \
                    "Insufficient funds. You only have {account.balance} chips."
                continue
            break

        clear_screen()
        display_blackjack_topbar(ctx, bet)

        # local variables
        player_status = True
        dealer_status = True
        player_bj = False
        dealer_bj = False

        # two decks of cards (values + string IDs)
        deck = FULL_DECK * decks

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
                display_blackjack_topbar(ctx, bet)
                cprint(INVALID_CHOICE_MSG + "\n")
                print_dealer_cards(dealer_hand)
                cprint("Your hand:")
                print_hand(player_hand)
                action = cinput("[S]tay   [H]it")

            clear_screen()
            display_blackjack_topbar(ctx, bet)

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
        while dealer_status:
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
        player_won = False
        dealer_won = False
        win_msgs = []
        if player_bj and dealer_bj:
            win_msgs.append("Player and dealer have a blackjack\n")
            win_msgs.append("Push\n")
            # player gets back bet, +1 draw
        elif not player_bj and dealer_bj:
            win_msgs.append("Dealer has a blackjack\n")
            win_msgs.append(f"You lose: -{bet} chips\n")
            dealer_won = True
            # player loses bet, +1 loss
        elif player_bj and not dealer_bj:
            win_msgs.append("Player has a blackjack\n")
            win_msgs.append(f"You win: +{bet} chips\n")
            player_won = True
            # player gets back 2x bet, +1 win, +1 bj counter
        elif hand_total(player_hand) > 21:
            win_msgs.append("You busted\n")
            win_msgs.append(f"Dealer wins: -{bet} chips\n")
            dealer_won = True
            # player loses bet, +1 loss
        elif hand_total(player_hand) <= 21 and hand_total(dealer_hand) > 21:
            win_msgs.append("Dealer busted\n")
            win_msgs.append(f"You win: +{bet} chips\n")
            player_won = True
            # player gets back 2x bet, +1 win
        elif hand_total(player_hand) == hand_total(dealer_hand):
            win_msgs.append("Player and dealer have same number\n")
            win_msgs.append("Push\n")
            # player gets back bet, +1 draw
        elif hand_total(player_hand) < hand_total(dealer_hand):
            win_msgs.append(f"Dealer wins: -{bet} chips\n")
            dealer_won = True
            # player loses bet, +1 loss
        elif hand_total(player_hand) > hand_total(dealer_hand):
            win_msgs.append(f"Player wins: +{bet} chips\n")
            player_won = True
            # player gets back 2x bet, +1 win
        else:
            raise ValueError(
                "Unaccounted for win condition!\n"
                f"Player: {hand_total(player_hand)}   "
                f"Dealer: {hand_total(dealer_hand)}"
            )

        # update account balance and redisplay
        if player_won:
            account.deposit(bet * 2)
        elif not dealer_won: # tie
            account.deposit(bet)
        clear_screen()
        display_blackjack_topbar(ctx, bet)
        cprint("Dealer hand:")
        print_hand(dealer_hand)
        cprint("Your hand:")
        print_hand(player_hand)
        for msg in win_msgs:
            cprint(msg)

        # game restart?
        if account.balance < min_bet:
            cprint(NO_FUNDS_MSG)
            cinput("Press enter to continue.")
            continue_game = False
            continue
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
            display_blackjack_topbar(ctx, bet)
            cprint(INVALID_YES_OR_NO)
            play_again = cinput(YES_OR_NO_PROMPT)

        # play / leave
        if play_again in "Nn":
            clear_screen()
            cprint(f"\nThanks for playing.\n\n")
            continue_game = False
