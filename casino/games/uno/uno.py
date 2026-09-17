from enum import nonmember
import time
import random

from .player import Player
from .views import UnoView
from casino.types import GameContext
from casino.cards import UnoDeck, UnoCard

class Uno:

    def __init__(self, ctx: GameContext) -> None:
        self.context = ctx
        self.view = UnoView(ctx)

    #check if deck is empty and reshuffle from discard
    def check_deck(self, deck, disc) :
        if len(deck) == 0 :
            deck.extend(disc)
            random.shuffle(deck)
            disc.clear()

    def draw(self, deck,disc) -> UnoCard:
        c = random.choice(deck)
        deck.remove(c)
        self.check_deck(deck,disc)
        return c

    def play_uno(self) -> None:
        unodeck_ = UnoDeck()
        current_deck = unodeck_.cards
        players: list[Player] = []
        discard = [] # tracked so deck can be reshuffled when it runs out

        self.view.display_topbar()

        # thinking hotseat multiplayer until socket stuff is implemented
        playernum = 0
        while playernum <= 6 and playernum < 1:
            playernum = self.view.prompt_num_players()
        self.view.display_topbar()

        for i in range(playernum) :
            name = self.view.prompt_player_name(i)
            players.append(Player(i,name))
            self.view.display_topbar()

        for i in range(7) :
            for j in players :
                j.draw(current_deck)

        #draws until first card on discard pile is regular number/color, not black, or card with special rules
        discard.append(self.draw(current_deck,discard))
        while not discard[-1].rank.isdigit():
            discard.append(self.draw(current_deck,discard))

        continueGame = True
        currentPlayerIndex = 0
        direction = 1
        winner = None

        while(continueGame) :
            i = players[currentPlayerIndex]
            current_card = discard[-1]
            self.view.player_switch_warning(i)
            self.view.show_turn(i, current_card)

            answer = self.view.prompt_draw_or_play()

            if (answer == "d" or answer == "draw") :
                new_card = i.draw(current_deck)
                self.view.show_drawn_card(new_card)
                i.draws_taken += 1

            elif (answer == "p" or answer == "play") :
                VALID_COLORS = ["red", "green", "blue", "yellow"]
                VALID_RANKS  = [str(n) for n in range(0, 10)] + ["draw_2", "skip", "reverse"]

                valid_card = False
                while (not valid_card): #checking if Card is in hand and can be played
                    valid_card = True

                    played_card_string = self.view.prompt_which_card()
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
                        answer = self.view.prompt_invalid_card()
                        if (answer == "draw" or answer == "d"):
                            new_card = i.draw(current_deck)
                            i.draws_taken += 1
                            self.view.show_drawn_card(new_card)
                            break
                #If actual valid card is chosen
                if valid_card:
                    i.hand.remove(new_card)
                    i.cards_played += 1

                    if new_card.color == "wild":
                        if new_card.rank == "wild_draw_4":
                            i.draw4_played += 1
                        else:
                            i.wilds_played += 1

                # i.hand.remove(new_card)
                if len(i.hand) == 0:
                    continueGame = False
                    winner = i
                    self.view.show_winner(i, players)
                    break
                match new_card.rank:
                    case "skip":
                        currentPlayerIndex = (currentPlayerIndex + direction) % len(players)
                    case "reverse":
                        if len(players) == 2:
                            currentPlayerIndex = (currentPlayerIndex + direction) % len(players)
                        else:
                            direction *= -1
                    case "draw_2":
                        currentPlayerIndex = (currentPlayerIndex + direction) % len(players)
                        players[currentPlayerIndex].draw(current_deck)
                        players[currentPlayerIndex].draw(current_deck)
                    case "wild":
                        new_color = self.view.prompt_wild_color()
                        new_card.color = new_color.lower()
                    case "wild_draw_4":
                        new_color = self.view.prompt_wild_color_draw_4()
                        new_card.color = new_color
                        currentPlayerIndex = (currentPlayerIndex + direction) % len(players)
                        players[currentPlayerIndex].draw(current_deck)
                        players[currentPlayerIndex].draw(current_deck)
                        players[currentPlayerIndex].draw(current_deck)
                        players[currentPlayerIndex].draw(current_deck)
                discard.append(new_card)
            self.view.prompt_next_player()
            self.view.display_topbar()
            currentPlayerIndex = (currentPlayerIndex + direction) % len(players)


def play_uno(ctx: GameContext) -> None:
    uno = Uno(ctx)
    uno.play_uno()

