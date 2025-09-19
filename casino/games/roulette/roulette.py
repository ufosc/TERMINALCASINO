"""
roulette.py

This file provides a way to play roulette.
This file integrates with the rest of the casino.
"""


import random
import os
import shutil
from typing import List

from casino.card_assets import assign_card_art
from casino.types import Card
from casino.utils import clear_screen, cprint, cinput

import casino.accounts

ROULETTE_HEADER = """
┌─────────────────────────────┐
│     ♠ R O U L E T T E ♠     │
└─────────────────────────────┘
"""
FULL_DECK: list[Card] = [
    # Clubs
    (2, "c2"), (3, "c3"), (4, "c4"), (5, "c5"), (6, "c6"), (7, "c7"), (8, "c8"), (9, "c9"), (10, "c10"),
    ("J", "cJ"), ("Q", "cQ"), ("K", "cK"), ("A", "cA"),
    # Diamonds
    (2, "d2"), (3, "d3"), (4, "d4"), (5, "d5"), (6, "d6"), (7, "d7"), (8, "d8"), (9, "d9"), (10, "d10"),
    ("J", "dJ"), ("Q", "dQ"), ("K", "dK"), ("A", "dA"),
    # Hearts
    (2, "h2"), (3, "h3"), (4, "h4"), (5, "h5"), (6, "h6"), (7, "h7"), (8, "h8"), (9, "h9"), (10, "h10"),
    ("J", "hJ"), ("Q", "hQ"), ("K", "hK"), ("A", "hA"),
    # Spades
    (2, "s2"), (3, "s3"), (4, "s4"), (5, "s5"), (6, "s6"), (7, "s7"), (8, "s8"), (9, "s9"), (10, "s10"),
    ("J", "sJ"), ("Q", "sQ"), ("K", "sK"), ("A", "sA"),
]

class Roulette:
    """
    Abstract base class to play roulette.

    Only contains base functions to run roulette.

    Attributes:
        wheel (list[tuple[str, str]]): The roulette wheel, where each entry is
            a tuple like ("0", "green").
        accounts (list[Account]): List of all player accounts.
        bets (list[tuple[str, str, str]]): Active bets, where each entry is
            (account_uuid, bet_type, bet_value).
    """
    
    def __init__(self, accounts: List[Account]) -> None:
        """
        Initializes roulette
        """

        # Will be populated with numbers and colors
        self.wheel = []

        self.accounts = accounts

        # Current round's bets
        self.bets = []

    def spin_wheel() -> tuple[str, str]:
        """
        Pick a winning color and number.

        Returns:
            tuple[str, str]: A tuple containing:
                - str: The winning number (e.g., "28", "00", "0")
                - str: The winning color (either "red", "green", or "black")
        """

        random_index = random.randint(0, len(self.wheel))
        return self.wheel[random_index]

        """

def play_roulette() -> None:
    continue_game = True
    while continue_game:
        clear_screen()
        cprint(ROULETTE_HEADER)

        # Input to stop loop from running constantly
        cinput("test: ")

if __name__ == "__main__":
    print("Do not run this file as main. Instead, change to root level of `TERMINALCASINO/`," + 
          "and run the following command:", end="\n\n")
    print("\tpython -m casino.main")