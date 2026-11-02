import unittest

from casino.games.roulette.variants.european import EuropeanRoulette


class EuropeanRouletteTests(unittest.TestCase):
    def setUp(self):
        self.roulette = EuropeanRoulette([])

    def test_wheel_has_single_zero(self):
        self.assertIn("0", self.roulette.valid_numbers)
        self.assertNotIn("00", self.roulette.valid_numbers)

    def test_inside_bet_pays_thirty_five_to_one_plus_stake(self):
        self.assertEqual(
            self.roulette.compute_win_multiplier("inside_number", "17", "17"),
            36,
        )

    def test_outside_bets_lose_on_zero(self):
        for bet_type, value in (
            ("outside_color", "red"),
            ("outside_parity", "even"),
            ("outside_highlow", "low"),
            ("outside_dozen", "1"),
            ("outside_column", "1"),
        ):
            with self.subTest(bet_type=bet_type):
                self.assertEqual(
                    self.roulette.compute_win_multiplier(bet_type, value, "0"),
                    1,
                )

    def test_dozen_and_column_pay_two_to_one_plus_stake(self):
        self.assertEqual(
            self.roulette.compute_win_multiplier("outside_dozen", "2", "17"),
            3,
        )
        self.assertEqual(
            self.roulette.compute_win_multiplier("outside_column", "2", "17"),
            3,
        )

    def test_outside_color_pays_even_money(self):
        self.assertEqual(
            self.roulette.compute_win_multiplier("outside_color", "red", "1"),
            2,
        )