import random
import time

from casino.card_assets import assign_card_art
from casino.types import Card
from casino.utils import clear_screen, cprint, cinput, display_topbar

SLOTS_HEADER = """
┌───────────────────────────────┐
│         ♠ S L O T S ♠         │
└───────────────────────────────┘
"""
HEADER_OPTIONS = {"header": SLOTS_HEADER,
                  "margin": 1,}

ITEMS = "abc"
BET_PROMPT = "🤵: How much would you like to bet?"
INVALID_BET_MSG = "🤵: That's not a valid bet."
MIN_BET_AMT = 10
MIN_BET_MSG = f"🤵: Each pay line requires at least ${MIN_BET_AMT}."

SEC_BTWN_SPIN = 0.1
TOTAL_SPINS = 10
WIN_PROB = 0.1

# Currently 1 pay line, goal is to have several and:
# - implement pattern patching for wins across lines
# - be able to bet across lines independently
# then maybe special lines
def play_slots(account) -> None:
    while True:
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)

        bet_amount = get_bet_amount(account)
        spin_animation()
        clear_screen()

        # Result spin
        if random.random() <= WIN_PROB:
            win_item = ITEMS[random.randint(0, len(ITEMS) - 1)]
            print_spin(win_item, win_item, win_item)
            cinput("WIN!!! :D")
            clear_screen()
            return
        else:
            final_items = get_rand_items()
            while are_items_equal(final_items):
                final_items = get_rand_items()
            print_spin(*final_items)

        # Choose what to do after spin
        player_input = ""
        while player_input not in "rRqQ" or player_input == "":
            player_input = cinput("[R]espin [Q]uit")
            
        if player_input in "qQ": 
            clear_screen()
            return

def get_bet_amount(account):
    while True:
        bet_str = cinput(BET_PROMPT).strip()
        try:
            bet = int(bet_str)
            if bet < MIN_BET_AMT:
                clear_screen()
                display_topbar(account, **HEADER_OPTIONS)
                cprint(MIN_BET_MSG)
            else:
                account.withdraw(bet)
                break
        except ValueError:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            cprint(INVALID_BET_MSG)
    
def get_player_respin_or_quit():
    prompt = "[R]espin [Q]uit"
    valid_inputs = {'r', 'q'}
    player_input = ""

    while player_input.lower().strip() not in valid_inputs:
        player_input = cinput(prompt)
    
    return player_input

def spin_animation(total_spins = TOTAL_SPINS, sec_btwn_spins = SEC_BTWN_SPIN) -> None:
    for _ in range(total_spins):
        clear_screen() 
        print_spin(*get_rand_items())
        time.sleep(sec_btwn_spins)

def are_items_equal(items) -> bool:
    return len(set(items)) == 1

def get_rand_items() -> str:
    return (get_rand_item(), get_rand_item(), get_rand_item())

def get_rand_item() -> str:
    return ITEMS[random.randint(0, len(ITEMS) - 1)];

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