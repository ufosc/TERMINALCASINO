from enum import nonmember
import time
import random

from casino.games.uno.player import Player
from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar
from casino.cards import UnoDeck, UnoCard

UNO_HEADER = """
┌───────────────────────────────┐
│             UNO!              │
└───────────────────────────────┘
"""

DRAW_PROMPT = "Would you like to: [D]raw a card or [P]lay a card?"
WHICH_CARD_PROMPT = "\nWhich card would you like to play?\n\nEnter card suite and number\nEx: \"red 2\", \"red skip\", \"red reverse\", \"red +2\"\nFor special cards, only enter \"+4\" or \"wild\"\n"
INVALID_CARD_MSG = "You can't play that card! Would you like to draw a card instead?"

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
def check_deck(deck, disc) :
    if len(deck) == 0 :
        deck.extend(disc)
        random.shuffle(deck)
        disc.clear()

def draw(deck,disc) -> UnoCard:
    c = random.choice(deck)
    deck.remove(c)
    check_deck(deck,disc)
    return c

def play_uno(ctx: GameContext) -> None:
    unodeck_ = UnoDeck()
    current_deck = unodeck_.cards 
    players: list[Player] = []
    discard = [] # tracked so deck can be reshuffled when it runs out

    display_uno_topbar(ctx)

    # thinking hotseat multiplayer until socket stuff is added
    playernum = 0
    while playernum <= 6 and playernum < 1:
        playernum = int(cinput("Input number of players (2-6):"))
    display_uno_topbar(ctx)

    for i in range(playernum) :  
        name = cinput("Player " + str(i + 1) + " Name: ")
        players.append(Player(i,name))
        display_uno_topbar(ctx)
    
    for i in range(7) :
        for j in players :
            j.draw(current_deck)
    
    #draws until first card on discard pile is regular number/color, not black, or card with special rules 
    current_card = draw(current_deck,discard)
    while not current_card.rank.isdigit():
        current_card = draw(current_deck,discard)        

    continueGame = True
    while(continueGame) :
        for i in players :
            player_switch_warning(ctx, i)
            cprint("Player: " + i.name + "\n\nTop card of the Discard pile: \n" + str(current_card) + "\n\nYour hand:\n")
            i.print_hand()
            cprint("\nCards from your hand that can be played:\n")
            for j in i.playable_cards(current_card):
                cprint(str(j),end="")
            
            answer = cinput(DRAW_PROMPT)
            if (answer == "D" or answer == "d") :
                new_card = i.draw(current_deck)
                cprint("You drew \n" + str(new_card) + " from the pile.")
                cinput("Press enter when ready to switch to the next player")
            elif (answer == "P" or answer == "p") :
                played_card = cinput(WHICH_CARD_PROMPT)
                #not implemented yet
            display_uno_topbar(ctx)
        continueGame = False
        

    