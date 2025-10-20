"""
Classes for cards that will be used in all card games.
"""

from abc import ABC, abstractmethod
import random
from typing import List
import os
from pathlib import Path


class Card(ABC):
    def __init__(self, category: str, identifier: int | str):
        self.category   = category
        self.identifier = identifier

        self.front = ""  # Face/value side. Shows value of card
        self.back  = ""  # Hidden side. Does not show value of card

        self.hidden: bool = True

    def load_art(self, FILE_PATH: str):
        """
        Loads ASCII art for all cards.

        Arguments:
            - FILE_PATH: file path to file containing ASCII art. Must be
                relative to the project root directory `TERMINALCASINO`.
        """
        # Resolve absolute file path (cross-platform)
        FILE_PATH = Path(FILE_PATH).resolve()

        # Get front contents
        with open(str(FILE_PATH), "r", encoding="utf-8") as file:
            self.front = file.read()

        # Get back contents
        folder = FILE_PATH.parent
        flipped_card_file = "flipped.txt"

        # In pathlib.Path, `/` is overloaded to join paths
        flipped_card_path = str(folder / flipped_card_file)

        with open(flipped_card_path, "r", encoding="utf-8") as file:
            self.back = file.read()

    def __repr__(self) -> str:
        # Developer-friendly information for Card object
        return (
            f"{self.__class__.__name__}("
            f"rank={self.rank!r}, suit={self.suit!r}, hidden={self.hidden!r})"
        )

    def __str__(self) -> str:
        # What the Card object will return when `print()` is called on it
        if self.hidden:
            return self.back
        else:
            return self.front


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


class UnoCard(Card):
    def __init__(self, color: str, rank: str):
        super().__init__(color, rank)
        self.color = color
        self.rank  = rank

        self.get_file()

    def get_file(self, FOLDER = "./casino/assets/cards/uno/"):
        """
        Loads ASCII art of `UnoCard`
        """

        # Get file of card containing display of card
        if self.color != "wild":
            FILE = FOLDER + f"{self.category}_{self.identifier}.txt"
        else:
            FILE = FOLDER + f"{self.rank}.txt"

        self.load_art(FILE)


class UnoDeck(Deck):
    COLORS = ["red", "green", "blue", "yellow"]
    RANKS  = [str(n) for n in range(0, 11)] + ["draw_2", "skip", "reverse"]
    SPECIAL_CARDS = ["wild", "wild_draw_4"]

    def __init__(self):
        self.cards = []
        self.generate_deck()

        super().__init__(self.cards)

    def generate_deck(self) -> List[Card]:
        self.cards = [
            UnoCard(color, rank)
            for color in __class__.COLORS
            for rank  in __class__.RANKS
        ]
        
        for card in SPECIAL_CARDS:
            self.cards.append(UnoCard("wild", card))

        return self.cards
