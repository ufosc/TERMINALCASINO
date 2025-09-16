import random
import sys
import os
import shutil

from casino.card_assets import assignCardArt


def dealCard(turn, deck):
    """Deal a card to the player."""
    card = random.choice(deck)
    turn.append(card)
    deck.remove(card)


def total(turn):
    """Calculate the total of each hand."""
    total = 0
    aces = 0
    for card, _ in turn:
        if card in range(1, 11):
            # 1-10
            total += card
        elif card in ["J", "Q", "K"]:
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


def showDealer(dealerHand):
    """Return a string of the dealer's hand."""
    if len(dealerHand) == 0:
        return ""
    # first card shown, rest hidden
    first_card = assignCardArt(*dealerHand[0])
    hidden_card = assignCardArt(0, "flipped")
    return "\n".join([
        "  ".join(lines)
        for lines in zip(first_card.strip("\n").splitlines(),
                         hidden_card.strip("\n").splitlines())
    ])


def display(hand):
    """Return a string of cards side by side."""
    card_lines = [
        assignCardArt(0, card_id).strip("\n").splitlines()
        for _, card_id in hand
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
    
    return "\n".join(combined_lines)


def callSecurity(stubborn):
    """Call the security guard if the player gets too stubborn."""
    if stubborn >= 13:
        clearScreen(0)
        print(f"")
        cprint(f"👮‍♂️: Time for you to go.")
        cprint(f"You have been removed from the casino")
        print(f"")
        sys.exit()


def clearScreen(headerPrint):
    """Clear the screen."""
    if os.name == "nt":
        os.system("cls")
    else:
        # clear screen + clear scrollback buffer (Linux/macOS)
        os.system("clear && printf \"\\033[3J\"")
    
        # header
    if headerPrint == 1:
        header = """
┌───────────────────────────────┐
│     ♠ B L A C K J A C K ♠     │
└───────────────────────────────┘
"""
        for line in header.splitlines():
            hprint(line)
        print(f"")

# header print
def hprint(*args, sep=" ", end="\n"):
    # gets center
    terminal_width = shutil.get_terminal_size().columns
    # join args like print does
    text = sep.join(map(str, args))
    # print centered
    print(text.center(terminal_width), end=end)

# center print
def cprint(*args, sep=" ", end="\n"):
    terminal_width = shutil.get_terminal_size().columns
    text = sep.join(map(str, args))

    # splitlines only if there are multiple lines, otherwise just center once
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            print(line.center(terminal_width))  # add newline for all but last line
        else:
            print(line.center(terminal_width), end=end)


# center input
def cinput(prompt=""):
    terminal_width = shutil.get_terminal_size().columns
    
    # center the whole prompt string
    prompt_text = prompt.center(terminal_width)
    
    # figure out where the "middle" of the prompt is
    cursor_padding = (terminal_width // 2) + 1  # +1 to fine-tune alignment
    
    # print the centered prompt
    print(prompt_text)
    
    # move cursor to the center for input
    print(" " * cursor_padding, end="")
    
    return input().strip()


def play_blackjack() -> None:
    game = True
    stubborn = 0 # gets to 7 and you're out


    while game == True:
        # inital clear
        clearScreen(1)
        
        # local variables
        playerStatus = True
        dealerStatus = True
        playerBJ = False
        dealerBJ = False

        # two decks of cards (values + string IDs)
        deck = [
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
        ] * 2  # duplicate for two decks


        # hands
        playerHand = []
        dealerHand = []

        # initial deal (player first)
        for _ in range(2):
            dealCard(playerHand, deck)
            dealCard(dealerHand, deck)

        # player BJ check
        if total(playerHand) == 21:
            playerBJ = True
            playerStatus = False

        # dealer BJ check
        if total(dealerHand) == 21:
            # dealer blackjack in initial deal
            dealerBJ = True
            playerStatus = False
            dealerStatus = False
            cprint("Your hand:")
            cprint(showDealer(dealerHand)) # ASCII cards printed side by side
            cprint(f"Total: Blackjack")
            cprint("Your hand:")
            cprint(display(playerHand)) # ASCII cards printed side by side
            cprint(f"Total: {total(playerHand)}")
        # player turn
        while playerStatus:
            # display hands
            cprint("Dealer hand:")
            cprint(showDealer(dealerHand)) # ASCII cards printed side by side
            cprint("Your hand:")
            cprint(display(playerHand)) # ASCII cards printed side by side
            cprint(f"Total: {total(playerHand)}")

            # action choice input
            action = cinput(f"[S]tay   [H]it")
            print(f"")

            # check valid answer
            while action not in "SsHh" or action == "":
                stubborn += 1
                callSecurity(stubborn)
                clearScreen(1)
                cprint(f"🤵: That's not a choice in this game.\n")
                cprint(showDealer(dealerHand))
                cprint("Your hand:")
                cprint(display(playerHand)) # ASCII cards printed side by side
                cprint(f"Total: {total(playerHand)}")
                action = cinput("[S]tay   [H]it")

            # clear terminal
            clearScreen(1)

            # do action
            if action == "S" or action == "s":
                playerStatus = False
            elif action == "H" or action == "h":
                dealCard(playerHand, deck)
            else:
                raise ValueError(f"Invalid choice: {action}")

            # player bust condition
            if total(playerHand) > 21:
                playerStatus = False
                dealerStatus = False
                # display hands
                cprint("Dealer hand:")
                cprint(display(dealerHand))
                cprint(f"Total: {total(dealerHand)}")
                cprint("Your hand:")
                cprint(display(playerHand))
                cprint(f"Total: {total(playerHand)}")

            # player 21 end condition
            if total(playerHand) == 21:
                playerStatus = False

        # dealer turn
        while dealerStatus == True:
            # dealer status check/update
            if total(dealerHand) > 21:
                #display hands
                cprint("Dealer hand:")
                cprint(display(dealerHand))
                cprint(f"Total: {total(dealerHand)}")
                if playerBJ == False:
                    cprint("Your hand:")
                    cprint(display(playerHand))
                    cprint(f"Total: {total(playerHand)}")
                else:
                    cprint("Your hand:")
                    cprint(display(playerHand))
                    cprint(f"Total: Blackjack")
                dealerStatus = False
            elif total(dealerHand) > 16:
                # display hands
                cprint("Dealer hand:")
                cprint(display(dealerHand))
                cprint(f"Total: {total(dealerHand)}")
                if playerBJ == False:
                    cprint("Your hand:")
                    cprint(display(playerHand))
                    cprint(f"Total: {total(playerHand)}")
                else:
                    cprint("Your hand:")
                    cprint(display(playerHand))
                    cprint(f"Total: Blackjack")
                dealerStatus = False
            else:
                dealCard(dealerHand, deck)

        ############## WIN CHECKS ##############
        print(f"")
        if playerBJ == True and dealerBJ == True:
            cprint(f"Player and dealer have a blackjack")
            cprint(f"Push")
            # player gets back bet, +1 draw
        elif playerBJ == False and dealerBJ == True:
            cprint(f"Dealer has a blackjack")
            cprint(f"You lose")
            # player loses bet, +1 loss
        elif playerBJ == True and dealerBJ == False:
            cprint(f"Player has a blackjack")
            cprint(f"You win")
            # player gets back 2x bet, +1 win, +1 bj counter
        elif total(playerHand) > 21:
            cprint(f"You busted")
            cprint(f"Dealer wins")
            # player loses bet, +1 loss
        elif total(playerHand) <= 21 and total(dealerHand) > 21:
            cprint(f"Dealer busted")
            cprint(f"You win")
            # player gets back 2x bet, +1 win
        elif total(playerHand) == total(dealerHand):
            cprint(f"Player and dealer have same number")
            cprint(f"Push")
            # player gets back bet, +1 draw
        elif total(playerHand) < total(dealerHand):
            cprint(f"Dealer wins")
            # player loses bet, +1 loss
        elif total(playerHand) > total(dealerHand):
            cprint(f"Player wins")
            # player gets back 2x bet, +1 win
        else:
            raise ValueError(
                "Unaccounted for win condition!\n"
                f"Player: {total(playerHand)}   Dealer: {total(dealerHand)}"
            )

        # game restart?
        cprint(f"🤵: Would you like to stay at the table?")
        playAgain = cinput(f"[Y]es   [N]o")
        # check valid answer
        while playAgain not in "YyNn" or playAgain == "":
            stubborn += 1
            callSecurity(stubborn)
            clearScreen(1)
            cprint(f"🤵: It's a yes or no, pal. You staying?")
            playAgain = cinput("[Y]es   [N]o\n")

        cprint(f"") # clear line

        # play / leave
        if playAgain in "Nn":
            clearScreen(0)
            print(f"")
            cprint(f"Thanks for playing.\n")
            game = False
