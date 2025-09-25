import random
import time

from casino.accounts import Account
from casino.utils import clear_screen, cprint, cinput, display_topbar

SLOTS_HEADER = """
┌───────────────────────────────┐
│         ♠ S L O T S ♠         │
└───────────────────────────────┘
"""
HEADER_OPTIONS = {
    "header": SLOTS_HEADER,
    "margin": 1,
}
LOW_ITEMS = ["a", "b", "c"]
HIGH_ITEMS = ["d"]
ALL_ITEMS = LOW_ITEMS + HIGH_ITEMS

PAYOUT_LEGEND = """
Matching a | b | c  : x1.5
Matching d          : x5.0
"""
BET_PROMPT = "How much would you like to bet?"
INVALID_BET_MSG = "That's not a valid bet."
MIN_BET_AMT = 10
MIN_BET_MSG = f"Each pay line requires at least ${MIN_BET_AMT}."

SEC_BTWN_SPIN = 0.1
TOTAL_SPINS = 10
WIN_PROBABILITY = 0.2
HIGH_VALUE_PROBABILITY = 0.05

# Currently 1 pay line, goal is to have several and:
# - implement pattern patching for wins across lines
# - be able to bet across lines independently
# then maybe special lines


def play_slots(account: Account) -> None:
    """Play slots game."""
    take_new_bet = True
    bet_amount = 0
    while True:
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)
        if take_new_bet or bet_amount > account.balance:
            if account.balance < MIN_BET_AMT:
                raise RuntimeError("PLAYER OUT OF MONEY IDK WHAT TO DO")
            bet_amount = get_bet_amount(account)
            take_new_bet = False

        spin_animation(account)
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)

        # Display final spin result
        rng = random.random()
        if rng <= WIN_PROBABILITY:
            money_gain = 0
            if rng <= HIGH_VALUE_PROBABILITY:
                win_item = HIGH_ITEMS[random.randint(0, len(HIGH_ITEMS) - 1)]
                money_gain = bet_amount * 5
            else:
                win_item = LOW_ITEMS[random.randint(0, len(LOW_ITEMS) - 1)]
                money_gain = int(bet_amount * 1.5)

            account.deposit(money_gain)
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            print_spin(win_item, win_item, win_item)
            cprint(f"MATCH: +${money_gain}")
        else:
            final_items = (get_rand_item(), get_rand_item(), get_rand_item())
            while len(set(final_items)) == 1:
                final_items = (get_rand_item(), get_rand_item(), get_rand_item())
            clear_screen()
            account.withdraw(bet_amount)
            display_topbar(account, **HEADER_OPTIONS)
            print_spin(*final_items)
            cprint(f"NO MATCH: -${bet_amount}")

        # Choose what to do after spin
        choice = get_player_choice()
        if choice["quit"]:
            return
        if choice["change_bet"]:
            take_new_bet = True


def get_bet_amount(account: Account) -> int:
    """Prompt user for bet amount."""
    while True:
        bet_str = cinput(BET_PROMPT).strip()
        try:
            bet = int(bet_str)
            if bet < MIN_BET_AMT:
                clear_screen()
                display_topbar(account, **HEADER_OPTIONS)
                cprint(MIN_BET_MSG)
                continue
            return bet
        except ValueError:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            cprint(INVALID_BET_MSG)
    
def get_player_choice() -> dict[str, bool]:
    """Prompt user for slots menu choice."""
    player_input = ""
    while player_input not in "rRqQcC" or player_input == "":
        player_input = cinput("[R]espin [C]hange Bet [Q]uit")
        
    if player_input in "qQ": 
        clear_screen()
        return {"quit": True}
    elif player_input in "rR":
        return {"quit": False, "change_bet": False}
    else:
        return {"quit": False, "change_bet": True}


def spin_animation(
    account: Account,
    total_spins: int = TOTAL_SPINS,
    sec_btwn_spins: float = SEC_BTWN_SPIN,
) -> None:
    """Animate the spin of the slot machine."""
    for _ in range(total_spins):
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)
        print_spin(get_rand_item(), get_rand_item(), get_rand_item())
        time.sleep(sec_btwn_spins)


def get_rand_item() -> str:
    return random.choice(ALL_ITEMS)


def print_spin(item1, item2, item3) -> None:
    cprint(f"""
    ┌────────────────────────┐
    |                        |
    |                        |
    |                        |
    |{item1:^8}{item2:^8}{item3:^8}|
    |                        |
    |                        |
    |                        |
    └────────────────────────┘
    """)
