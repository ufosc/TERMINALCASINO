"""
Unit testing for TERMINALCASINO/cards.py
"""

import unittest
from casino.cards import *


class TestStandardCardClass(unittest.TestCase):
    def test_cards(self):
        card = StandardCard("9", "diamonds")

        comparison = """
┌─────────┐
|9        |
|  ♦ ♦ ♦  |
|  ♦ ♦ ♦  |
|  ♦ ♦ ♦  |
|        9|
└─────────┘
""".lstrip("\n")

        self.assertEqual(str(card), comparison)

    def test_deck(self):
        deck = StandardDeck()

class TestUnoCardClass(unittest.TestCase):
    def test_cards(self):
        card = UnoCard("yellow", "3")
        comparison = """
┌─────────┐
|3        |
|    3    |
| (YELLO) |
|    3    |
|        3|
└─────────┘
""".lstrip("\n")

        self.assertEqual(str(card), comparison)