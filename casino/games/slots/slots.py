import random
import os
import shutil
import time

from casino.card_assets import assign_card_art
from casino.types import Card
from casino.utils import clear_screen, cprint, cinput

SLOTS_HEADER = """
┌───────────────────────────────┐
│         ♠ S L O T S ♠         │
└───────────────────────────────┘
"""

ITEMS = "abc"

SEC_BTWN_SPIN = 0.1
TOTAL_SPINS = 10
WIN_PROB = 0.1

def play_slots() -> None:
    while True:
        clear_screen()
        cprint(SLOTS_HEADER)

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

def spin_animation(total_spins = TOTAL_SPINS, sec_btwn_spins = SEC_BTWN_SPIN) -> None:
    spin_n = 0

    while spin_n < total_spins:
        clear_screen()
        print_spin(*get_rand_items())

        time.sleep(sec_btwn_spins)
        spin_n += 1

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