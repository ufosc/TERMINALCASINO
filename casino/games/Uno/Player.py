import random
from casino.types import Card
from casino.utils import cprint

class Player:
    def __init__(self, id, name) :
        self.id = id
        self.name = name
        self.hand = []

    def print_hand(self) -> None :
        for c in self.hand:
            cprint(str(c) + " ")
    
    def draw(self, deck: list[Card]) -> Card:
        c = random.choice(deck)
        self.hand.append(c)
        deck.remove(c)
        return c
    
    def play_card(self) -> Card:
        c = random.choice(self.hand)
        self.hand.remove(c)
        return c
    
    def playable_cards(self, currentCard : Card) -> list[Card]:
        valid_cards = []
        for i in self.hand : 
            if (i[1] == currentCard[1] or i[0] == currentCard[0]) :
                valid_cards.append(i)
        return valid_cards