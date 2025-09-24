"""
roulette.py

This file provides a way to play roulette.

WARNING: do not run this file as main. Instead, change to root directory
of `TERMINALCASINO/`, and run the following command:

```
python -m casino.main
```

Then, pick "Roulette" as the game you want to run.
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

    @staticmethod
    def roulette_sort_key(value):
        """
        Sorts values in roulette. Used as a key in the `sorted()` function.
        """
        if value == "0":
            return -1
        elif value == "00":
            return 0
        return int(value)

    def spin_wheel(self) -> tuple[str, str]:
        """
        Pick a winning color and number.

        Returns:
            tuple[str, str]: A tuple containing:
                - str: The winning number (e.g., "28", "00", "0")
                - str: The winning color (either "red", "green", or "black")
        """

        random_index = random.randint(0, len(self.wheel))
        return self.wheel[random_index]

    def submit_bets(self) -> None:
        """
        Instruct users to submit bets.

        This function will ask users if they would like to submit a bet
        on a color or a number.

        - If users pick color, they can pick either red, green, or black
        - If users pick number, they can pick a number to bet on.
        """

        # Loop over all users
        i = 0
        while (i < len(accounts)):
            will_bet = input("Would you like to bet (y/N): ")

            if will_bet == "" or will_bet.upper() == "N" or will_bet.upper() == "NO":
                print("User skipped betting. Moving to next user...", end="\n\n")
                i += 1
                continue
            elif will_bet.upper() == "Y" or will_bet.upper() == "YES":
                pass
            else:
                print("Invalid input. Enter either 'Y' for yes or 'N' for no.")
                continue

            # Input bet amount
            bet_amount = input("Amount to bet: ")

            # Check bet_amount is a positive integer
            try:
                bet_amount = int(bet_amount)

                if (bet_amount < 0):
                    raise ValueError
            except ValueError:
                print(f"ERROR: '{bet_amount}' is not a valid number. Please enter a positive integer.", end="\n\n")
                continue

            # Check that account has enough money to bet
            try:
                accounts[i].withdraw(bet_amount)
            except ValueError as error:
                if error.args and error.args[0] == "Insufficient balance":
                    print(f"Insufficient balance to place bet. Please enter a bet lower than {accounts[i].balance}")
                continue

            # Ask for desired bet type
            bet_type = ""
            valid_bet_types = ["C", "COLOR", "N", "NUMBER"]

            while True:
                bet_type = input("Would you like to bet on a color or a number? (C or N): ")

                if (bet_type.upper() in valid_bet_types):
                    break
                else:
                    print("Error: Invalid bet type. Choose either 'color' or 'number'.")

            ############################################################

            # Ask for user's specific bet
            bet_value = ""

            # Color betting
            if bet_type.upper() == "C" or bet_type.upper() == "COLOR":
                while True:
                    bet_value = input("Enter color you want to bet on (Red, Black, Green): ")

                    if bet_value.upper() in self.valid_colors:
                        break
                    else:
                        print("Error: Chosen color is not red, green, or black.")
            
            # Number betting
            else if bet_type.upper() == "N" or bet_type.upper() = "NUMBER":
                while True:
                    bet_value = input("Enter number you would like to bet on: ")

                    if bet_value in self.valid_numbers:
                        break
                    else:
                        print("Error: You may only enter one of the following numbers.")
                        sorted_numbers = sorted(self.valid_numbers, key=roulette_sort_key)
                        valid_numbers_str = ", ".join(sorted_numbers)
                        print("\t" + valid_numbers_str)
         
            # Once values are successfully chosen, save
            self.bets.append( (accounts[i].aid, bet_type, bet_value, bet_amount) )

            i += 1  # Move to next user

class AmericanRoulette(Roulette):
    """
    Plays roulette using American rules
    """

    def __init__(self, accounts: List[Account]):
        super().__init__(self, accounts)

        # Use the standard American roulette wheel
        self.wheel = [
            ("0", "green"),
            ("28", "black"),
            ("9", "red"),
            ("26", "black"),
            ("30", "red"),
            ("11", "black"),
            ("7", "red"),
            ("20", "black"),
            ("32", "red"),
            ("17", "black"),
            ("5", "red"),
            ("22", "black"),
            ("34", "red"),
            ("15", "black"),
            ("3", "red"),
            ("24", "black"),
            ("36", "red"),
            ("13", "black"),
            ("1", "red"),
            ("00", "green"),
            ("27", "red"),
            ("10", "black"),
            ("25", "red"),
            ("29", "black"),
            ("12", "red"),
            ("8", "black"),
            ("19", "red"),
            ("31", "black"),
            ("18", "red"),
            ("6", "black"),
            ("21", "red"),
            ("33", "black"),
            ("16", "red"),
            ("4", "black"),
            ("23", "red"),
            ("35", "black"),
            ("14", "red"),
            ("2", "black")
        ]


def play_roulette() -> None:
    continue_game = True
    while continue_game:
        clear_screen()
        cprint(ROULETTE_HEADER)

        # Input to stop loop from running constantly
        cinput("test: ")
