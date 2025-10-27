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
    
    def draw(self, deck: list[Card]) -> None:
        c = random.choice(deck)
        self.hand.append(c)
        deck.remove(c)