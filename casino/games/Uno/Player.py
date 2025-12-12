import random
from casino.cards import UnoCard
from casino.utils import cprint

class Player:
    def __init__(self, id, name) :
        self.id = id
        self.name = name.upper()
        self.hand = []
    
    def draw(self, deck: list[UnoCard]) -> UnoCard:
        c = random.choice(deck)
        self.hand.append(c)
        deck.remove(c)
        return c
    
    def play_card(self) -> UnoCard:
        c = random.choice(self.hand)
        self.hand.remove(c)
        return c
    
    def playable_cards(self, currentCard : UnoCard) -> list[UnoCard]:
        valid_cards = []
        for i in self.hand : 
            if (i.rank == currentCard.rank or i.color == currentCard.color or i.color == "wild") :
                valid_cards.append(i)
        return valid_cards