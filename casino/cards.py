"""
Classes for cards that will be used in all card games.
"""

from abc import ABC, abstractmethod
import random
from typing import List


class Card(ABC):
    def __init__(self, category : str, identifier):
        self.category   = category
        self.identifier = identifier

    @abstractmethod
    def __repr__(self):
        # What the Card object will return when `print()` is called on it
        return ""


class Deck:
    def __init__(self, cards):
        self.cards : List[Card] = cards

    @abstractmethod
    def generate_deck() -> List[Card]:
        return self.cards

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()


