from casino.types import Card
from casino.utils import cprint

class player:

    name = ""
    hand = []

    def printHand(self) -> None :
        for c in self.hand:
            cprint(c + " ")