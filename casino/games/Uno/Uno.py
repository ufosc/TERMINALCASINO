import random
from enum import nonmember

from casino.types import Card
from casino.utils import clear_screen, cprint, cinput

UNO_HEADER = """
┌───────────────────────────────┐
│             UNO!              │
└───────────────────────────────┘
"""

DRAW_PROMPT = "🤡: Would you like to draw a card or play a card?"
WHICH_CARD_PROMPT = "🤡: Which card would you like to play?"
INVALID_CARD_MSG = "You can't play that card! Would you like to draw a card instead?"


FULL_DECK: list[Card] = [
    # reds, two of each except zero
    (0, "red"), (1, "red"), (1, "red"), (2, "red"), (2, "red"), (3, "red"), (3, "red"), (4, "red"), (4, "red"),
    (5, "red"), (5, "red"), (6, "red"), (6, "red"), (7, "red"), (7, "red"), (8, "red"), (8, "red"), (9,"red"),
    (9, "red"), ("reverse","red"), ("reverse", "red"), ("+2", "red"), ("+2","red"), ("skip","red"), ("skip","red"),
    # blues, two of each except zero
    (0, "blue"), (1, "blue"), (1, "blue"), (2, "blue"), (2, "blue"), (3, "blue"), (3, "blue"), (4, "blue"), (4, "blue"),
    (5, "blue"), (5, "blue"), (6, "blue"), (6, "blue"), (7, "blue"), (7, "blue"), (8, "blue"), (8, "blue"), (9, "blue"),
    (9, "blue"), ("reverse", "blue"), ("reverse", "blue"), ("+2", "blue"), ("+2", "blue"), ("skip", "blue"), ("skip", "blue"),
    # greens, two of each except zero
    (0, "green"), (1, "green"), (1, "green"), (2, "green"), (2, "green"), (3, "green"), (3, "green"), (4, "green"), (4, "green"),
    (5, "green"), (5, "green"), (6, "green"), (6, "green"), (7, "green"), (7, "green"), (8, "green"), (8, "green"), (9, "green"),
    (9, "green"), ("reverse", "green"), ("reverse", "green"), ("+2", "green"), ("+2", "green"), ("skip", "green"), ("skip", "green"),
    # yellows, two of each except zero
    (0, "yellows"), (1, "yellows"), (1, "yellows"), (2, "yellows"), (2, "yellows"), (3, "yellows"), (3, "yellows"), (4, "yellows"), (4, "yellows"),
    (5, "yellows"), (5, "yellows"), (6, "yellows"), (6, "yellows"), (7, "yellows"), (7, "yellows"), (8, "yellows"), (8, "yellows"), (9, "yellows"),
    (9, "yellows"), ("reverse", "yellows"), ("reverse", "yellows"), ("+2", "yellows"), ("+2", "yellows"), ("skip", "yellows"), ("skip", "yellows"),
    # black/special cards
    ("+4","black"), ("+4","black"), ("+4","black"), ("+4","black"),
    ("wild", "black"), ("wild", "black"), ("wild", "black"), ("wild", "black"),
]

def draw(hand : list[Card], deck: list[Card]) -> None:
    c = random.choice(deck)
    hand.append(c)
    deck.remove(c)

def begin_uno() -> None:
    cprint("Implement Here")