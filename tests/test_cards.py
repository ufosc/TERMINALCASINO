"""
Unit testing for TERMINALCASINO/cards.py
"""

import unittest
from casino.cards import *


class TestStandardCardClass(unittest.TestCase):
    def test_cards(self):
        card = StandardCard("9", "diamonds")
        card.hidden = False

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

    def test_back(self):
        card = StandardCard("9", "diamonds")

        comparison = """
┌─────────┐
|░░░░░░░░░|
|░░░░░░░░░|
|░░░░░░░░░|
|░░░░░░░░░|
|░░░░░░░░░|
└─────────┘
""".lstrip("\n")

        self.assertEqual(card.back, comparison)

class TestUnoCardClass(unittest.TestCase):
    def test_cards(self):
        card = UnoCard("yellow", "3")
        card.hidden = False
        
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