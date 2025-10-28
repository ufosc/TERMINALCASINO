from enum import nonmember
import time
import random

from casino.games.uno.player import Player
from casino.types import Card, GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar

UNO_HEADER = """
┌───────────────────────────────┐
│             UNO!              │
└───────────────────────────────┘
"""

DRAW_PROMPT = "Would you like to: [D]raw a card or [P]lay a card?"
WHICH_CARD_PROMPT = "\nWhich card would you like to play?\n\nEnter card suite and number\nEx: \"red 2\", \"red skip\", \"red reverse\", \"red +2\"\nFor special cards, only enter \"+4\" or \"wild\"\n"
INVALID_CARD_MSG = "You can't play that card! Would you like to draw a card instead?"

FULL_DECK: list[Card] = [
    # reds, two of each except zero
    (0, "red"), (1, "red"), (1, "red"), (2, "red"), (2, "red"), (3, "red"), (3, "red"), (4, "red"), (4, "red"),
    (5, "red"), (5, "red"), (6, "red"), (6, "red"), (7, "red"), (7, "red"), (8, "red"), (8, "red"), (9,"red"),
    (9, "red"), ("reverse","red"), ("reverse", "red"), ("+2", "red"), ("+2","red"), ("skip","red"), ("skip","red"),
    # blues, two of each except zero
    (0, "blue"), (1, "blue"), (1, "blue"), (2, "blue"), (2, "blue"), (3, "blue"), (3, "blue"), (4, "blue"), (4, "blue"),
    (5, "blue"), (5, "blue"), (6, "blue"), (6, "blue"), (7, "blue"), (7, "blue"), (8, "blue"), (8, "blue"), (9, "blue"),
    (9, "blue"), ("reverse", "blue"), ("reverse", "blue"), ("+2", "blue"), ("+2", "blue"), ("skip", "blue"), ("skip", "blue"),
    # greens, two of each except zero
    (0, "green"), (1, "green"), (1, "green"), (2, "green"), (2, "green"), (3, "green"), (3, "green"), (4, "green"), (4, "green"),
    (5, "green"), (5, "green"), (6, "green"), (6, "green"), (7, "green"), (7, "green"), (8, "green"), (8, "green"), (9, "green"),
    (9, "green"), ("reverse", "green"), ("reverse", "green"), ("+2", "green"), ("+2", "green"), ("skip", "green"), ("skip", "green"),
    # yellows, two of each except zero
    (0, "yellow"), (1, "yellow"), (1, "yellow"), (2, "yellow"), (2, "yellow"), (3, "yellow"), (3, "yellow"), (4, "yellow"), (4, "yellow"),
    (5, "yellow"), (5, "yellow"), (6, "yellow"), (6, "yellow"), (7, "yellow"), (7, "yellow"), (8, "yellow"), (8, "yellow"), (9, "yellow"),
    (9, "yellow"), ("reverse", "yellow"), ("reverse", "yellow"), ("+2", "yellow"), ("+2", "yellow"), ("skip", "yellow"), ("skip", "yellow"),
    # black/special cards
    ("+4","black"), ("+4","black"), ("+4","black"), ("+4","black"),
    ("wild", "black"), ("wild", "black"), ("wild", "black"), ("wild", "black"),
]

players: list[Player] = []
current_deck = FULL_DECK 
discard = [] # tracked so deck can be reshuffled when it runs out


def display_uno_topbar(ctx: GameContext, margin = None) :
    clear_screen()
    display_topbar(ctx.account, UNO_HEADER)    

#warning to look away when cards switch
def player_switch_warning(ctx: GameContext, current_player) : 
    for i in range(5) :
        cprint("SWITCHING TO PLAYER " + current_player.name + " IN " + str(5-i) + " SECONDS")
        time.sleep(1)
        display_uno_topbar(ctx)

#check if deck is empty and reshuffle from discard
def check_deck(deck = current_deck, disc = discard) :
    if len(deck) == 0 :
        deck = disc
        random.shuffle(deck)
        disc = []

def draw() -> Card:
    c = random.choice(current_deck)
    current_deck.remove(c)
    check_deck()
    return c

def play_uno(ctx: GameContext) -> None:
    display_uno_topbar(ctx)

    # thinking hotseat multiplayer until socket stuff is added
    playernum = int(cinput("Input number of players:"))
    display_uno_topbar(ctx)

    for i in range(playernum) :  
        name = cinput("Player " + str(i + 1) + " Name: ")
        players.append(Player(i,name))
        display_uno_topbar(ctx)
    
    for i in range(7) :
        for j in players :
            j.draw(current_deck)
            check_deck()
    
    #draws until first card on discard pile is regular number/color, not black, or card with special rules 
    while True :
        current_card = draw()
        if (isinstance(current_card, tuple) and list(map(type, current_card)) == [int, str]) :
            break


    continueGame = True
    while(continueGame) :
        for i in players :
            player_switch_warning(ctx, i)
            cprint("Player: " + i.name + "\n\nTop card of the Discard pile: " + str(current_card) + "\n\nYour hand:\n")
            i.print_hand()
            cprint("\nCards from your hand that can be played:\n" + str(i.playable_cards(current_card)) + "\n")
            
            answer = cinput(DRAW_PROMPT)
            if (answer == "D" or answer == "d") :
                new_card = i.draw(current_deck)
                cprint("You drew " + str(new_card) + " from the pile.")
                cinput("Press enter when ready to switch to the next player")
            elif (answer == "P" or answer == "p") :
                played_card = cinput(WHICH_CARD_PROMPT)
                #not implemented yet
            display_uno_topbar(ctx)
        continueGame = False
        

    