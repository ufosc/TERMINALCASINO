"""
Classes for cards that will be used in all card games.
"""

from abc import ABC, abstractmethod
import random
from typing import List
import os
from pathlib import Path


class Card(ABC):
    def __init__(self, category : str, identifier):
        self.category   = category
        self.identifier = identifier

    @abstractmethod
    def __repr__(self):
        # What the Card object will return when `print()` is called on it
        return ""


class Deck(ABC):
    def __init__(self, cards):
        self.cards : List[Card] = cards

    @abstractmethod
    def generate_deck() -> List[Card]:
        return self.cards

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()


class StandardCard(Card):
    def __init__(self, rank: str, suit: str):
        super().__init__(suit, rank)

        self.string = ""
        self.load_art()

    def load_art(self) -> None:
        """
        Loads ASCII art of `StandardCard`
        """
        # Get file of card containing display of card
        FOLDER = "./casino/assets/cards/standard/"
        FILE = FOLDER + f"{self.identifier}_of_{self.category}.txt"

        # Resolve absolute file path (cross-platform)
        FILE = Path(FILE).resolve()
        FILE = str(FILE)

        with open(FILE, "r", encoding="utf-8") as file:
            self.string = file.read()

    def __repr__(self):
        return self.string


class StandardDeck(Deck):
    SUITS = ["clubs", "diamonds", "hearts", "spades"]
    RANKS = [str(n) for n in range(2, 11)] + ["J", "Q", "K", "A"]

    def __init__(self):
        self.cards = []
        self.generate_deck()

        super().__init__(self.cards)

    def generate_deck(self) -> List[Card]:
        self.cards = [
            StandardCard(suit, rank)
            for suit in __class__.SUITS
            for rank in __class__.RANKS
        ]

        return self.cards


