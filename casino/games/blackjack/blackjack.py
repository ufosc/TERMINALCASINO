
# simple playable blackjack logic
# SINGLE PLAYER



############## IMPORTS ##############
import random
import sys # force exit program
import os # terminal commands
import shutil # center printing



############## VARIABLES ##############
# global variables
game = True
stubborn = 0 # gets to 7 and you're out



############## FUNCTIONS ##############
# deal cards
def dealCard(turn):
    card = random.choice(deck)
    turn.append(card)
    deck.remove(card)

# calculate the total of each hand
def total(turn):
    total = 0
    aces = 0
    for card in turn:
        if card in range(1, 11):
            # 1-10
            total += card
        elif card in ['J', 'Q', 'K']:
            # face card
            total += 10
        elif card == 'A':
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

# show dealer hand
def showDealer():
    if len(dealerHand) == 2:
        return dealerHand[0]
    elif len(dealerHand) > 2:
        return dealerHand[0, len(dealerHand) - 1]

# invalid response consequence
def callSecurity():
    if stubborn >= 13:
        clearScreen(0)
        print(f"")
        cprint(f"👮‍♂️: Time for you to go.")
        cprint(f"You have been removed from the casino")
        print(f"")
        sys.exit()

# clear screen
def clearScreen(headerPrint):
    # Windows
    if os.name == 'nt':
        os.system('cls')
    # macOS/Linux
    else:
        os.system('clear')
    
    # header
    if headerPrint == 1:
        header = """
┌───────────────────────────────┐
│     ♠ B L A C K J A C K ♠     │
└───────────────────────────────┘
"""
        for line in header.splitlines():
            cprint(line)
        print(f"")

# center print
def cprint(*args, sep=' ', end='\n'):
    # gets center
    terminal_width = shutil.get_terminal_size().columns
    # join args like print does
    text = sep.join(map(str, args))
    # print centered
    print(text.center(terminal_width), end=end)

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




############## GAME LOOP ##############
while game == True:
    # inital clear
    clearScreen(1)
    
    # local variables
    playerStatus = True
    dealerStatus = True
    playerBJ = False
    dealerBJ = False

    # two decks of cards
    deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
            2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
            'J', 'Q', 'K', 'A', 'J', 'Q', 'K', 'A', 'J', 'Q', 'K', 'A', 'J', 'Q', 'K', 'A',
            2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
            2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10, 
            'J', 'Q', 'K', 'A', 'J', 'Q', 'K', 'A', 'J', 'Q', 'K', 'A', 'J', 'Q', 'K', 'A']

    # hands
    playerHand = []
    dealerHand = []

    # initial deal (player first)
    for _ in range(2):
        dealCard(playerHand)
        dealCard(dealerHand)

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
        cprint(f"Dealer hand: {dealerHand}   Total: Blackjack")
        cprint(f"Your hand: {playerHand}   Total: {total(playerHand)}")   

    # player turn
    while playerStatus:
        # display hands
        cprint(f"Dealer hand: {showDealer()}, ?")
        cprint(f"Your hand: {playerHand}   Total: {total(playerHand)}")

        # action choice input
        action = cinput(f"[S]tay   [H]it")
        print(f"")

        # check valid answer
        while action not in 'SsHh' or action == '':
            stubborn += 1
            callSecurity()
            clearScreen(1)
            cprint(f"🤵: That's not a choice in this game.\n")
            cprint(f"Dealer hand: {showDealer()}, ?")
            cprint(f"Your hand: {playerHand}   Total: {total(playerHand)}")
            action = cinput("[S]tay   [H]it")

        # clear terminal
        clearScreen(1)

        # do action
        if action == 'S' or action == 's':
            playerStatus = False
        elif action == 'H' or action == 'h':
            dealCard(playerHand)
        else:
            raise ValueError(f"Invalid choice: {action}")
        
        # player bust condition
        if total(playerHand) > 21:
            playerStatus = False
            dealerStatus = False
            # display hands
            cprint(f"Dealer hand: {showDealer()}, ?")
            cprint(f"Your hand: {playerHand}   Total: {total(playerHand)}")

        # player 21 end condition
        if total(playerHand) == 21:
            playerStatus = False

    # dealer turn
    while dealerStatus == True:
        # dealer status check/update
        if total(dealerHand) > 21:
            #display hands
            cprint(f"Dealer hand: {dealerHand}   Total: {total(dealerHand)}")
            if playerBJ == False:
                cprint(f"Your hand: {playerHand}   Total: {total(playerHand)}")
            else:
                cprint(f"Your hand: {playerHand}   Total: Blackjack")  
            dealerStatus = False
        elif total(dealerHand) > 16:
            # display hands
            cprint(f"Dealer hand: {dealerHand}   Total: {total(dealerHand)}")
            if playerBJ == False:
                cprint(f"Your hand: {playerHand}   Total: {total(playerHand)}")
            else:
                cprint(f"Your hand: {playerHand}   Total: Blackjack")
            dealerStatus = False
        else:
            dealCard(dealerHand)

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
        raise ValueError(f"Unaccounted for win condition!\nPlayer: {total(playerHand)}   Dealer: {total(dealerHand)}")

    # game restart?
    print(f"")
    cprint(f"🤵: Would you like to stay at the table?")
    playAgain = cinput(f"[Y]es   [N]o")
    # check valid answer
    while playAgain not in 'YyNn' or playAgain == '':
        stubborn += 1
        callSecurity()
        clearScreen(1)
        cprint(f"🤵: It's a yes or no, pal. You staying?")
        playAgain = cinput("[Y]es   [N]o\n")
    
    # clear line
    cprint(f"")
    
    # play / leave
    if playAgain in 'Nn':
        clearScreen(0)
        print(f"")
        cprint(f"Thanks for playing.\n")
        game = False