from enum import nonmember
import time
import random

from .player import Player
from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar
from casino.cards import UnoDeck, UnoCard

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

def display_uno_topbar(ctx: GameContext, margin = None) :
    clear_screen()
    display_topbar(ctx.account, UNO_HEADER)    

#warning to look away when cards switch
def player_switch_warning(ctx: GameContext, current_player) : 
    display_uno_topbar(ctx)
    cinput(f"Press enter to reveal {current_player.name}'s cards.")
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

def print_hand(cards) :
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

def play_uno(ctx: GameContext) -> None:
    unodeck_ = UnoDeck()
    current_deck = unodeck_.cards 
    players: list[Player] = []
    discard = [] # tracked so deck can be reshuffled when it runs out

    display_uno_topbar(ctx)

    # thinking hotseat multiplayer until socket stuff is implemented
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
    discard.append(draw(current_deck,discard))
    while not discard[-1].rank.isdigit():
        discard.append(draw(current_deck,discard))       

    continueGame = True
    currentPlayerIndex = 0
    direction = 1
    while(continueGame) :
        i = players[currentPlayerIndex]
        current_card = discard[-1]
        player_switch_warning(ctx, i)
        cprint("Player: " + i.name + "\n\nTop card of the Discard pile: \n" + str(current_card) + "\nYour hand:")
        print_hand(i.hand)
        cprint("\nCards from your hand that can be played:")
        if(bool(i.playable_cards(current_card))):
            print_hand(i.playable_cards(current_card))
        else:
            cprint("\nNONE\n")
        
        answer = cinput(DRAW_PROMPT).lower()
        while (answer != "d" and answer != "p" and answer != "draw" and answer != "play"):
            cprint("Please input either P or D!")
            answer = cinput(DRAW_PROMPT).lower()

        if (answer == "d" or answer == "draw") :
            new_card = i.draw(current_deck)
            cprint("You drew \n" + str(new_card) + " from the pile.")
        elif (answer == "p" or answer == "play") :
            VALID_COLORS = ["red", "green", "blue", "yellow"]
            VALID_RANKS  = [str(n) for n in range(0, 10)] + ["draw_2", "skip", "reverse"]

            valid_card = False
            while (not valid_card): #checking if Card is in hand and can be played
                valid_card = True

                cprint(WHICH_CARD_PROMPT1)
                cprint(WHICH_CARD_PROMPT2)
                played_card_string = cinput(WHICH_CARD_PROMPT3)
                played_card_words = played_card_string.split()

                if len(played_card_words) == 2 and played_card_words[1] == "+2":
                    played_card_words[1] = "draw_2"

                if ((not ((len(played_card_words) == 1) and
                    played_card_words[0] in ["wild", "+4"])) and 
                    (not ((len(played_card_words) == 2) and
                    played_card_words[0] in VALID_COLORS and 
                    played_card_words[1] in VALID_RANKS))):

                    valid_card = False
                if valid_card:
                    if len(played_card_words) == 1:
                        if played_card_words[0] == "+4":
                            new_card = UnoCard("wild","wild_draw_4")
                        else:
                            new_card = UnoCard("wild","wild")
                    else: 
                        new_card = UnoCard(played_card_words[0],played_card_words[1])

                    if not (new_card in i.playable_cards(current_card)):
                        valid_card = False

                if not valid_card:             
                    answer = cinput(INVALID_CARD_MSG).lower()
                    if (answer == "draw" or answer == "d"):
                        new_card = i.draw(current_deck)
                        cprint("You drew \n" + str(new_card) + " from the pile.")
                        break

            i.hand.remove(new_card)
            if len(i.hand) == 0:
                continueGame = False
                display_uno_topbar(ctx)
                cprint(f"{i.name} is the winner!")
                cinput("Press enter when ready to exit")
                break
            match new_card.rank:
                case "skip":
                    currentPlayerIndex = (currentPlayerIndex + direction) % len(players)
                case "reverse":
                    if len(players) == 2:
                        currentPlayerIndex = (currentPlayerIndex + direction) % len(players)
                    else:
                        direction *= -1
                case "+2":
                    currentPlayerIndex = (currentPlayerIndex + direction) % len(players)
                    players[currentPlayerIndex].draw(current_deck)
                    players[currentPlayerIndex].draw(current_deck)
                case "wild":
                    new_color = cinput("Choose a color for the wild card (green, yellow, red, or blue)!").lower()
                    while (new_color != "green" and  
                           new_color != "red" and 
                           new_color != "yellow" and 
                           new_color != "blue"):
                        new_color = cinput("Choose a valid color please (green, yellow, red, or blue).")
                    new_card.color = new_color.lower()
                case "wild_draw_4":
                    new_color = cinput("Choose a color for the +4 card (green, yellow, red, or blue)!").lower()
                    while (new_color != "green" and 
                           new_color != "red" and
                           new_color != "yellow" and
                           new_color != "blue"):
                        new_color = cinput("Choose a valid color please (green, yellow, red, or blue).").lower()
                    new_card.color = new_color
                    currentPlayerIndex = (currentPlayerIndex + direction) % len(players)
                    players[currentPlayerIndex].draw(current_deck)
                    players[currentPlayerIndex].draw(current_deck)
                    players[currentPlayerIndex].draw(current_deck)
                    players[currentPlayerIndex].draw(current_deck)
            discard.append(new_card)
        cinput("Press enter when ready to switch to the next player")
        display_uno_topbar(ctx)
        currentPlayerIndex = (currentPlayerIndex + direction) % len(players)
        

        

    