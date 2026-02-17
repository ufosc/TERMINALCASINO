import random
from casino.cards import UnoCard
from casino.utils import cprint

class Player:
    def __init__(self, id, name) :
        self.id = id
        self.name = name.upper()
        self.hand = []

        #Stats
        self.cards_played = 0
        self.draws_taken = 0
        self.wilds_played = 0
        self.draw2_played = 0
        self.draw4_played = 0
        self.skips_played = 0
        self.reverses_played = 0
    
    def draw(self, deck: list[UnoCard]) -> UnoCard:
        c = random.choice(deck)
        self.hand.append(c)
        deck.remove(c)
        #Track the draws taken
        self.draws_taken += 1
        return c
    
    def play_card(self, card:UnoCard) -> UnoCard:
        self.hand.remove(card)
        #Track the cards played
        self.cards_played += 1

        #Add action to stats
        if card.color == "wild":
            if card.rank == "wild_draw_4":
                self.draw4_played += 1
            else:
                self.wilds_played += 1
        elif card.rank == "draw_2":
            self.draw2_played += 1
        elif card.rank == "skip":
            self.skips_played += 1
        elif card.rank == "reverse":
            self.reverses_played += 1

        return card
    
    def playable_cards(self, currentCard : UnoCard) -> list[UnoCard]:
        valid_cards = []
        for i in self.hand : 
            if (i.rank == currentCard.rank or i.color == currentCard.color or i.color == "wild") :
                valid_cards.append(i)
        return valid_cards