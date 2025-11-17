import random
from typing import List, Optional
from time import sleep
import time

from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar
from casino.accounts import Account

ROULETTE_HEADER = """
┌─────────────────────────────┐
│     ♠ R O U L E T T E ♠     │
└─────────────────────────────┘
"""

STANDARD_AMERICAN_ROULETTE_WHEEL = [
    ("0", "green", 0, 13),
    ("28", "black", 0, 16),
    ("9", "red", 0, 19),
    ("26", "black", 1, 24),
    ("30", "red", 2, 26),
    ("11", "black", 3, 27),
    ("7", "red", 4, 28),
    ("20", "black", 5, 29),
    ("32", "red", 6, 30),
    ("17", "black", 7, 30),
    ("5", "red", 8, 30),
    ("22", "black", 9, 30),
    ("34", "red", 10, 30),
    ("15", "black", 11, 29),
    ("3", "red", 12, 28),
    ("24", "black", 13, 27),
    ("36", "red", 14, 26),
    ("13", "black", 15, 24),
    ("1", "red", 16, 19),
    ("00", "green", 16, 16),
    ("27", "red", 16, 13),
    ("10", "black", 16, 10),
    ("25", "red", 15, 7),
    ("29", "black", 14, 6),
    ("12", "red", 13, 4),
    ("8", "black", 12, 3),
    ("19", "red", 11, 2),
    ("31", "black", 10, 2),
    ("18", "red", 9, 2),
    ("6", "black", 8, 1),
    ("21", "red", 7, 2),
    ("33", "black", 6, 2),
    ("16", "red", 5, 3),
    ("4", "black", 4, 3),
    ("23", "red", 3, 5),
    ("35", "black", 2, 6),
    ("14", "red", 1, 8),
    ("2", "black", 0, 10)
]

TOTAL_ROTATIONS = 2
SEC_BTWN_SPIN = 0.03

ROWS, COLS= 17, 32
ROULETTE_GRID = [['  ' for _ in range(COLS)] for _ in range(ROWS)]

class Roulette:
    """
    Abstract base class to play roulette.

    Only contains base functions to run roulette.

    Attributes:
        wheel (list[tuple[str, str]]): The roulette wheel, where each entry is
            a tuple like ("0", "green").
        accounts (list[Account]): List of all player accounts.
        bets (dict[str, dict[str, str, int]]): Maps each account UUID to a bet record.

        Each key is a unique account UUID, and each value is a dictionary with the fields:
            {
                "type": bet_type,
                "value": bet_value,
                "amount": bet_amount
            }

        Example:
            {
                "uuid_1": {"type": "color", "value": "red", "amount": 100},
                "uuid_2": {"type": "number", "value": "00", "amount": 50}
            }
    """
    
    def __init__(self, accounts: List[Account]) -> None:
        """
        Initializes roulette
        """
        # Will be populated with numbers and colors
        self.wheel = list[tuple[str, str, int, int]]()

        # Colors on wheel. Includes initials
        self.valid_colors = ["red", "green", "black", "r", "g", "b"]
        self.valid_numbers = []

        self.accounts = accounts

        # Current round's bets
        self.bets = {}
        self.winning_value: Optional[tuple[str, str]] = None

    @staticmethod
    def normalize_color(input_value: str) -> str:
        """
        Standardize color input from user.

        The `Roulette` class permits the user to input a shorthand version of the color,
        or the name of the color itself. This function standardizes all colors to:

            "red", "green", "black"
        """
        color_map = {
            "r": "red",
            "red": "red",
            "g": "green",
            "green": "green",
            "b": "black",
            "black": "black"
        }
        return color_map.get(input_value.lower(), input_value)

    @staticmethod
    def normalize_type(input_value: str) -> str:
        """
        Standardize bet type from user.

        The `Roulette` class permits the user to input a shorthand version of the type of bet they want,
        or the name of the bet type itself. This function standardizes all bet types to:

            "color", "number"
        """
        type_map = {
            "c" : "color",
            "color" : "color",
            "n" : "number",
            "number" : "number"
        }
        return type_map.get(input_value.lower(), input_value)

    @staticmethod
    def roulette_sort_key(value : str) -> int:
        """
        Sorts values in roulette. Used as a key in the `sorted()` function.
        """
        if value == "0":
            return -1
        elif value == "00":
            return 0
        return int(value)

    def print_wheel(self, highlighted_num = None) -> None:
        # clear current grid
        for row in range(len(ROULETTE_GRID)):
            for col in range(len(ROULETTE_GRID[0])):
                ROULETTE_GRID[row][col] = ' ' # each empty spot is 2 spaces

        for (num_str, color, row, col) in STANDARD_AMERICAN_ROULETTE_WHEEL:
            if num_str != "00" and int(num_str.strip()) < 10:
                num_str = " " + num_str
            if num_str.strip() == highlighted_num.strip():
                # the spot in the column before and column after the number become *'s
                ROULETTE_GRID[row][col-1] = "*"
                ROULETTE_GRID[row][col+1] = "*"

            if color == "green":
                ROULETTE_GRID[row][col] = f"\x1b[32m{num_str}\x1b[0m"
            elif color == "black":
                ROULETTE_GRID[row][col] = f"\x1b[30m{num_str}\x1b[0m"
            else:
                ROULETTE_GRID[row][col] = f"\x1b[31m{num_str}\x1b[0m"

        # printing the wheel
        for row in ROULETTE_GRID:
            print("".join(row))

    def wheel_animation(self, sequence, sec_btwn_spins: float = SEC_BTWN_SPIN) -> None:
        for num in sequence:
            clear_screen()
            cprint(ROULETTE_HEADER)
            self.print_wheel(highlighted_num = num)
            time.sleep(sec_btwn_spins)

    def spin_wheel(self) -> tuple[str, str]:
        """
        Pick a winning color and number.

        Returns:
            tuple[str, str]: A tuple containing:
                - str: The winning number (e.g., "28", "00", "0")
                - str: The winning color (either "red", "green", or "black")
        """

        print("Spinning wheel...")

        random_index = random.randint(0, len(self.wheel))
        self.winning_value = self.wheel[random_index]

        wheel_sequence = [num for num, _, _, _ in self.wheel]

        # do 3 full rotations before landing on winner
        sequence = (wheel_sequence * TOTAL_ROTATIONS) + wheel_sequence[:random_index + 1]
        self.wheel_animation(sequence)

        winning_number = self.winning_value[0]
        winning_color  = self.winning_value[1]

        print(f"Winning values:")
        print(f"\tWinning number: {winning_number}")
        print(f"\tWinning color:  {winning_color}")

        return self.winning_value

    def submit_bets(self) -> None | str:
        """
        Instruct users to submit bets.

        This function will ask users if they would like to submit a bet
        on a color or a number.

        - If users pick color, they can pick either red, green, or black
        - If users pick number, they can pick a number to bet on.
        """

        # Loop over all users
        i = 0
        while (i < len(self.accounts)):
            player_balances = 0
            for account in self.accounts:
                player_balances += account.balance
            
            if player_balances == 0:
                print("ERROR: All players have gone bankrupt. "
                      "You cannot play any more roulette.")
                sleep(3)
                return "BANKRUPT"

            if (self.accounts[i].balance == 0):
                print(f"Skipping player {i+1} because of empty balance...")
                continue

            will_bet = input(f"Would you like to bet, Player {i+1} (y/N): ")

            if will_bet == "" or will_bet.lower() in {"n", "no"}:
                print("User skipped betting. Moving to next user...", end="\n\n")
                i += 1
                continue
            elif will_bet.upper() == "Y" or will_bet.upper() == "YES":
                pass
            else:
                print("Invalid input. Enter either 'Y' for yes or 'N' for no.")
                continue

            # Input bet amount
            bet_amount = input(f"Player {i+1}'s Bet: ")

            # Check bet_amount is a positive integer
            try:
                bet_amount = int(bet_amount)

                if (bet_amount < 0):
                    raise ValueError
            except ValueError:
                print(f"ERROR: '{bet_amount}' is not a valid number. "
                      "Please enter a positive integer.", end="\n\n")
                continue

            # Check that account has enough money to bet
            try:
                self.accounts[i].withdraw(bet_amount)
            except ValueError as error:
                if error.args and error.args[0] == "Insufficient balance":
                    print("Insufficient balance to place bet. Please enter a "
                          f"bet less thanor equal to {self.accounts[i].balance}")
                continue

            print(f"Successfully withdrew {bet_amount} coins from Player {i+1}.")
            print(f"\tPlayer {i+1} remaining balance: "
                  f"{self.accounts[i].balance} coins.")

            # Ask for desired bet type
            bet_type = ""
            valid_bet_types = ["C", "COLOR", "N", "NUMBER"]

            while True:
                bet_type = input(
                    "Would you like to bet on a color or a number? (C or N): "
                ).strip()

                if (bet_type.upper() in valid_bet_types):
                    break
                else:
                    print("Error: Invalid bet type. "
                          "Choose either 'color' or 'number'.")

            ############################################################

            # Ask for user's specific bet
            bet_value = ""

            # Color betting
            if bet_type.lower() in {"c", "color"}:
                while True:
                    bet_value = input(
                        "Enter color you want to bet on (red, black, green): "
                    )
                    if bet_value.lower() in self.valid_colors:
                        break
                    else:
                        print("Error: Chosen color is not red, green, or black.")
            
            # Number betting
            elif bet_type.lower() in {"n", "number"}:
                while True:
                    bet_value = input("Enter number you would like to bet on: ")

                    if bet_value in self.valid_numbers:
                        break
                    else:
                        print("Error: You may only enter one of the following "
                              "numbers.")
                        sorted_numbers = sorted(self.valid_numbers,
                                                key=self.roulette_sort_key)
                        valid_numbers_str = ", ".join(sorted_numbers)
                        print("\t" + valid_numbers_str)
         
            # Once values are successfully chosen, save to dictionary
            account_id = str(self.accounts[i].aid)
            self.bets[account_id] = {
                "type"   : Roulette.normalize_type(bet_type.lower()),
                "value"  : Roulette.normalize_color(bet_value.lower()),
                "amount" : bet_amount
            }
            i += 1  # Move to next user

    def payout(self) -> None:
        """
        Pay out all players who picked the right color or number.
        """
        assert self.winning_value is not None
        winning_number = self.winning_value[0]
        winning_color  = self.winning_value[1]

        print("Paying out all winners...")
        i = 0
        for _, bet in self.bets.items():
            bet_type   = bet["type"]
            bet_value  = bet["value"]
            bet_amount = bet["amount"]

            win_multiplier = 1
            # Check if user won
            if bet_type == "color" and bet_value == winning_color:
                if bet_type == "green":
                    win_multiplier += 35
                else:
                    # Find account and pay back two times original bet
                    win_multiplier += 1
            elif bet_type == "number" and bet_value == winning_number:
                # Find account and pay back 36 times original amount
                win_multiplier += 35

            if win_multiplier > 1:
                win_amount = bet_amount * win_multiplier
                self.accounts[i].deposit(win_amount)
                print(f"\tPlayer {i+1}: Won {win_amount} coins.")
            else:
                print(f"\tPlayer {i+1}: Lost {bet_amount} coins.")
            
            i += 1

        print("Finished payout.")


class AmericanRoulette(Roulette):
    """Plays roulette using American rules."""

    def __init__(self, accounts: List[Account]):
        super().__init__(accounts)
        self.wheel = STANDARD_AMERICAN_ROULETTE_WHEEL
        self.valid_numbers = [number for (number, _, _, _) in self.wheel]


def play_roulette(context: GameContext) -> None:
    continue_game = True

    # Temporary fix
    # TODO: fix argument in play_roulette to only except `List[GameContext]`
    # and not `GameContext`
    contexts = [context]

    # Access account data
    accounts = [account.account for account in contexts]

    if not isinstance(accounts, list):
        raise ValueError("accounts is not a list. "
                         f"accounts is a {type(accounts)}")

    roulette = AmericanRoulette(accounts)
    while continue_game:
        clear_screen()
        cprint(ROULETTE_HEADER)

        # Input to stop loop from running constantly
        choice = cinput("Press [Enter] to start a new round and [q] to quit: ")

        if choice.lower() in {"q", "quit"}:
            continue_game = False
            break

        status = roulette.submit_bets()
        if status == "BANKRUPT":
            break

        roulette.spin_wheel()
        roulette.payout()

        play_again = None

        while True:
            valid_choices = ["N", "NO", "Y", "YES", ""]
            play_again = input("Would you like to play another round (Y/n): ")

            if play_again.upper() not in valid_choices:
                print("Please enter 'Yes' or 'No'.")
                continue
            if play_again.lower() in {"n", "no"}:
                print("Quitting roulette...")
                continue_game = False
                break
            elif play_again == "" or play_again.lower() in {"y", "yes"}:
                continue_game = True
                break

    print("Exiting roulette...")
    sleep(0.5)
