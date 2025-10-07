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

        self.string = ""

    def load_art(self, FILE_PATH: str):
        """
        Loads ASCII art for all cards.

        Arguments:
            - FILE_PATH: file path to file containing ASCII art. Must be
                relative to the project root directory `TERMINALCASINO`.
        """
        # Resolve absolute file path (cross-platform)
        FILE_PATH = Path(FILE_PATH).resolve()
        FILE_PATH = str(FILE_PATH)

        with open(FILE_PATH, "r", encoding="utf-8") as file:
            self.string = file.read()

    def __repr__(self) -> str:
        # What the Card object will return when `print()` is called on it
        return self.string


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
        self.rank = rank
        self.suit = suit

        super().__init__(suit, rank)
        self.get_file()

    def get_file(self) -> None:
        """
        Loads ASCII art of `StandardCard`
        """
        # Get file of card containing display of card
        FOLDER = "./casino/assets/cards/standard/"
        FILE = FOLDER + f"{self.identifier}_of_{self.category}.txt"

        self.load_art(FILE)


class StandardDeck(Deck):
    SUITS = ["clubs", "diamonds", "hearts", "spades"]
    RANKS = [str(n) for n in range(2, 11)] + ["J", "Q", "K", "A"]

    def __init__(self):
        self.cards = []
        self.generate_deck()

        super().__init__(self.cards)

    def generate_deck(self) -> List[Card]:
        self.cards = [
            StandardCard(rank, suit)
            for suit in __class__.SUITS
            for rank in __class__.RANKS
        ]

        return self.cards


