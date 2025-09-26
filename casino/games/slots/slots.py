import random
import time
from typing import Literal

from casino.accounts import Account
from casino.utils import clear_screen, cprint, cinput, display_topbar

type SlotsMenuChoice = Literal["respin", "change_bet", "quit"]

SLOTS_HEADER = """
┌───────────────────────────────┐
│         ♠ S L O T S ♠         │
└───────────────────────────────┘
"""
HEADER_OPTIONS = {
    "header": SLOTS_HEADER,
    "margin": 1,
}

BET_PROMPT = "How much would you like to bet?"
INVALID_BET_MSG = "That's not a valid bet."
INVALID_INPUT_MSG = "Invalid input. Please try again."
MIN_BET_AMT = 10
MIN_BET_MSG = f"Each pay line requires at least ${MIN_BET_AMT}."

SEC_BTWN_SPIN = 0.1
TOTAL_SPINS = 10
WIN_PROBABILITY = 0.2
HIGH_VALUE_PROBABILITY = 0.05


def get_slots_menu_prompt(bet_amount: int, account: Account) -> str:
    """Generate slots menu prompt."""
    if account.balance < MIN_BET_AMT:
        return f"[Q]uit"
    if account.balance < bet_amount:
        return f"[C]hange Bet [Q]uit"
    else:
        return f"[R]espin [C]hange Bet [Q]uit"


def generate_payout_legend(
    low_items: list[str],
    high_items: list[str],
) -> str:
    """Generate payout legend."""
    low_items_str = " | ".join(low_items)
    high_items_str = " | ".join(high_items)
    max_len = max(len(low_items_str), len(high_items_str))
    low_str  = f"Matching {low_items_str .ljust(max_len)}  | x1.5"
    high_str = f"Matching {high_items_str.ljust(max_len)}  | x5.0"
    return f"{low_str}\n{high_str}"


LOW_ITEMS = ["A", "B", "C"]
HIGH_ITEMS = ["D"]
ALL_ITEMS = LOW_ITEMS + HIGH_ITEMS
PAYOUT_LEGEND = generate_payout_legend(LOW_ITEMS, HIGH_ITEMS)

# Currently 1 pay line, goal is to have several and:
# - implement pattern patching for wins across lines
# - be able to bet across lines independently
# - then maybe special lines


def get_rand_item() -> str:
    return random.choice(ALL_ITEMS)


def print_spin(items: tuple[str, str, str]) -> None:
    cprint(f"""
┌────────────────────────┐
|                        |
|                        |
|                        |
|{items[0]:^8}{items[1]:^8}{items[2]:^8}|
|                        |
|                        |
|                        |
└────────────────────────┘
    """.strip())


def get_bet_amount(account: Account) -> int:
    """Prompt user for bet amount."""
    while True:
        cprint(PAYOUT_LEGEND + "\n\n")
        bet_str = cinput(BET_PROMPT).strip()
        try:
            bet = int(bet_str)
        except ValueError:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            cprint(INVALID_BET_MSG)
            continue
        if bet < MIN_BET_AMT:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            cprint(MIN_BET_MSG)
            continue
        if bet > account.balance:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            cprint(f"You only have ${account.balance}. Please try again.")
            continue
        return bet


def get_player_choice(
    items: tuple[str, str, str],
    bet_amount: int,
    account: Account,
) -> SlotsMenuChoice:
    """Prompt user for slots menu choice."""
    first_iter = True
    while True:
        if not first_iter:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            print_spin(items)
            cprint(INVALID_INPUT_MSG)
        first_iter = False
        menu_prompt = get_slots_menu_prompt(bet_amount, account)
        player_input = cinput(menu_prompt).strip()
        if player_input == "":
            continue
        if player_input in "qQ":
            return "quit"
        elif player_input in "rR":
            if account.balance < bet_amount:
                continue
            return "respin"
        elif player_input in "cC":
            if account.balance < MIN_BET_AMT:
                continue
            return "change_bet"


def spin_animation(
    account: Account,
    total_spins: int = TOTAL_SPINS,
    sec_btwn_spins: float = SEC_BTWN_SPIN,
) -> None:
    """Animate the spin of the slot machine."""
    for _ in range(total_spins):
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)
        print_spin((get_rand_item(), get_rand_item(), get_rand_item()))
        time.sleep(sec_btwn_spins)


def play_slots(account: Account) -> None:
    """Play slots game."""
    take_new_bet = True
    bet_amount = 0
    while True:
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)
        if take_new_bet or bet_amount > account.balance:
            if account.balance < MIN_BET_AMT:
                cprint("You don't have enough money to make a bet.")
                cinput("Press Enter to continue...")
                return
            bet_amount = get_bet_amount(account)
            take_new_bet = False

        spin_animation(account)
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)

        # Display final spin result
        items: tuple[str, str, str]
        rng = random.random()
        if rng <= WIN_PROBABILITY:
            money_gain = 0
            if rng <= HIGH_VALUE_PROBABILITY:
                win_item = HIGH_ITEMS[random.randint(0, len(HIGH_ITEMS) - 1)]
                money_gain = bet_amount * 5
            else:
                win_item = LOW_ITEMS[random.randint(0, len(LOW_ITEMS) - 1)]
                money_gain = int(bet_amount * 1.5)
            items = (win_item, win_item, win_item)
            account.deposit(money_gain)
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            print_spin(items)
            cprint(f"MATCH: +${money_gain}")
        else:
            items = (get_rand_item(), get_rand_item(), get_rand_item())
            while len(set(items)) == 1:
                items = (get_rand_item(), get_rand_item(), get_rand_item())
            clear_screen()
            account.withdraw(bet_amount)
            display_topbar(account, **HEADER_OPTIONS)
            print_spin(items)
            cprint(f"NO MATCH: -${bet_amount}")

        # Choose what to do after spin
        choice = get_player_choice(items, bet_amount, account)
        match choice:
            case "quit":
                return
            case "change_bet":
                take_new_bet = True
            case "respin":
                continue
