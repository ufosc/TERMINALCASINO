import random
from casino.cards import UnoCard
from casino.utils import cprint

class Player:
    def __init__(self, id, name) :
        self.id = id
        self.name = name.upper()
        self.hand = []
        self.cards_played = 0
        self.cards_drawn = 0
        self.wilds_played = 0
        self.plus2_played = 0
        self.plus4_played = 0
        self.skips_played = 0
        self.reverses_played = 0
        self.reds_played = 0
        self.greens_played = 0
        self.blues_played = 0
        self.yellows_played = 0
        self.color_counts = {"red": 0, "green": 0, "blue": 0, "yellow": 0}
        self.uno_stats = None
    
    def draw(self, deck: list[UnoCard]) -> UnoCard:
        c = random.choice(deck)
        self.cards_drawn += 1
        self.hand.append(c)
        deck.remove(c)
        return c
    
    def play_card(self) -> UnoCard:
        c = random.choice(self.hand)
        self.hand.remove(c)
        return c

    def color_count(self, color : str) -> None:
        if color not in self.color_counts:
            return
        self.color_counts[color] += 1
        match color:
            case "red":
                self.reds_played += 1
            case "green":
                self.greens_played += 1
            case "blue":
                self.blues_played += 1
            case "yellow":
                self.yellows_played += 1
    
    def playable_cards(self, currentCard : UnoCard) -> list[UnoCard]:
        valid_cards = []
        for i in self.hand : 
            if (i.rank == currentCard.rank or i.color == currentCard.color or i.color == "wild") :
                valid_cards.append(i)
        return valid_cards