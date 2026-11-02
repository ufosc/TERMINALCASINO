import unittest

from casino.games.roulette.variants.american import AmericanRoulette


class AmericanRouletteTests(unittest.TestCase):
    def setUp(self):
        self.roulette = AmericanRoulette([])

    def test_wheel_contains_both_zero_pockets(self):
        self.assertIn("0", self.roulette.valid_numbers)
        self.assertIn("00", self.roulette.valid_numbers)

    def test_number_bet_pays_thirty_five_to_one_plus_stake(self):
        self.assertEqual(
            self.roulette.compute_win_multiplier("number", "17", "17"),
            36,
        )

    def test_color_bet_wins_even_money(self):
        self.assertEqual(
            self.roulette.compute_win_multiplier("color", "red", "9"),
            2,
        )

    def test_green_color_bet_pays_straight_up(self):
        self.assertEqual(
            self.roulette.compute_win_multiplier("color", "green", "0"),
            36,
        )

    def test_losing_bet_does_not_return_stake(self):
        self.assertEqual(
            self.roulette.compute_win_multiplier("color", "red", "28"),
            1,
        )