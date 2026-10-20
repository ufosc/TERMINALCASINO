"""Unit tests for the Slots games (StandardSlots and ExpandedSlots).

Only game mechanics are tested (payouts, bet validation, balance changes,
menu choices). Graphical output is mocked out because it may change.
"""
import unittest
from unittest.mock import patch

from casino.accounts import Account
from casino.config import Config
from casino.types import GameContext
from casino.games.slots.constants import (
    HIGH_ITEMS,
    LOW_ITEMS,
    HIGH_VALUE_PROBABILITY,
    WIN_PROBABILITY,
    NO_FUNDS_MSG,
    generate_payout_legend,
)
from casino.games.slots.variants.expanded import (
    ExpandedSlots,
    payout_for_row,
    score_lines,
)
from casino.games.slots.variants.standard import StandardSlots

STANDARD = "casino.games.slots.variants.standard"


def make_context(balance=100):
    return GameContext(account=Account.generate("test", balance), config=Config.default())


def make_game(cls, balance=100):
    """Create a game whose view prints nothing and never blocks on input."""
    game = cls(make_context(balance))
    for name in ("clear_and_topbar", "announce", "show_payout_legend"):
        patcher = patch.object(game.view, name)
        patcher.start()
        # stop the patch when the calling test finishes
        unittest.TestCase().addCleanup(patcher.stop)
    return game


class PayoutForRowTests(unittest.TestCase):
    def test_low_item_match_pays_one_and_a_half_times(self):
        for item in LOW_ITEMS:
            self.assertEqual(payout_for_row((item, item, item), 10), 15)

    def test_high_item_match_pays_five_times(self):
        for item in HIGH_ITEMS:
            self.assertEqual(payout_for_row((item, item, item), 10), 50)

    def test_low_item_payout_rounds_down(self):
        # 3 * 1.5 = 4.5 -> int() truncates to 4
        self.assertEqual(payout_for_row(("A", "A", "A"), 3), 4)

    def test_no_match_pays_nothing(self):
        self.assertEqual(payout_for_row(("A", "B", "C"), 10), 0)

    def test_two_of_three_pays_nothing(self):
        self.assertEqual(payout_for_row(("A", "A", "B"), 10), 0)

    def test_zero_bet_pays_nothing(self):
        self.assertEqual(payout_for_row(("D", "D", "D"), 0), 0)


class ScoreLinesTests(unittest.TestCase):
    def test_no_winning_rows(self):
        grid = (("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B"))
        self.assertEqual(score_lines(grid, (5, 5, 5)), (0, []))

    def test_single_winning_row(self):
        grid = (("A", "B", "C"), ("D", "D", "D"), ("C", "A", "B"))
        self.assertEqual(score_lines(grid, (5, 10, 5)), (50, [1]))

    def test_multiple_winning_rows_are_summed(self):
        grid = (("A", "A", "A"), ("B", "C", "A"), ("D", "D", "D"))
        total, winners = score_lines(grid, (10, 10, 2))
        self.assertEqual(total, 15 + 10)
        self.assertEqual(winners, [0, 2])

    def test_row_with_zero_bet_does_not_win(self):
        grid = (("A", "A", "A"), ("A", "A", "A"), ("A", "A", "A"))
        total, winners = score_lines(grid, (0, 10, 0))
        self.assertEqual(total, 15)
        self.assertEqual(winners, [1])


class PayoutLegendTests(unittest.TestCase):
    def test_legend_lists_both_multipliers(self):
        legend = generate_payout_legend(["A", "B"], ["D"])
        self.assertIn("x1.5", legend)
        self.assertIn("x5.0", legend)
        self.assertEqual(len(legend.splitlines()), 2)


class StandardSettleTests(unittest.TestCase):
    def test_high_value_win_pays_five_times_bet(self):
        game = make_game(StandardSlots, 100)
        with patch(f"{STANDARD}.random.random", return_value=HIGH_VALUE_PROBABILITY):
            result, payout, message, won = game.settle(10)
        self.assertTrue(won)
        self.assertEqual(payout, 50)
        self.assertEqual(game.account.balance, 150)
        self.assertEqual(len(set(result)), 1)
        self.assertIn(result[0], HIGH_ITEMS)
        self.assertIn("+50", message)

    def test_low_value_win_pays_one_and_a_half_times_bet(self):
        game = make_game(StandardSlots, 100)
        rng = (HIGH_VALUE_PROBABILITY + WIN_PROBABILITY) / 2  # inside the low-win band
        with patch(f"{STANDARD}.random.random", return_value=rng):
            result, payout, message, won = game.settle(10)
        self.assertTrue(won)
        self.assertEqual(payout, 15)
        self.assertEqual(game.account.balance, 115)
        self.assertIn(result[0], LOW_ITEMS)

    def test_loss_withdraws_bet_and_never_shows_a_match(self):
        game = make_game(StandardSlots, 100)
        with patch(f"{STANDARD}.random.random", return_value=0.99):
            for _ in range(50):
                game.account.balance = 100
                result, payout, message, won = game.settle(10)
                self.assertFalse(won)
                self.assertEqual(payout, 0)
                self.assertEqual(game.account.balance, 90)
                self.assertGreater(len(set(result)), 1)
                self.assertIn("-10", message)

    def test_loss_rerolls_until_result_is_not_a_match(self):
        game = make_game(StandardSlots, 100)
        rolls = iter([("A", "A", "A"), ("D", "D", "D"), ("A", "B", "C")])
        with patch(f"{STANDARD}.random.random", return_value=0.99), \
             patch.object(game, "random_result", side_effect=lambda: next(rolls)):
            result, _, _, won = game.settle(10)
        self.assertFalse(won)
        self.assertEqual(result, ("A", "B", "C"))

    def test_win_probability_boundary_is_inclusive(self):
        game = make_game(StandardSlots, 100)
        with patch(f"{STANDARD}.random.random", return_value=WIN_PROBABILITY):
            _, _, _, won = game.settle(10)
        self.assertTrue(won)

    def test_just_above_win_probability_loses(self):
        game = make_game(StandardSlots, 100)
        with patch(f"{STANDARD}.random.random", return_value=WIN_PROBABILITY + 0.0001):
            _, _, _, won = game.settle(10)
        self.assertFalse(won)


class StandardPromptBetTests(unittest.TestCase):
    def prompt_with(self, balance, inputs):
        game = make_game(StandardSlots, balance)
        with patch.object(game.view, "prompt", side_effect=inputs):
            return game, game.prompt_bet()

    def test_valid_bet_is_returned(self):
        _, bet = self.prompt_with(100, ["10"])
        self.assertEqual(bet, 10)

    def test_non_numeric_input_is_rejected_then_retried(self):
        game, bet = self.prompt_with(100, ["abc", "", "5"])
        self.assertEqual(bet, 5)
        game.view.announce.assert_any_call("That's not a valid bet.")

    def test_bet_below_minimum_is_rejected(self):
        game, bet = self.prompt_with(100, ["1", "2"])
        self.assertEqual(bet, 2)  # minimum line bet is 2

    def test_bet_above_balance_is_rejected(self):
        _, bet = self.prompt_with(50, ["51", "50"])
        self.assertEqual(bet, 50)

    def test_negative_bet_is_rejected(self):
        _, bet = self.prompt_with(100, ["-5", "5"])
        self.assertEqual(bet, 5)

    def test_decimal_bet_is_rejected(self):
        _, bet = self.prompt_with(100, ["2.5", "4"])
        self.assertEqual(bet, 4)

    def test_bet_total_is_the_bet(self):
        self.assertEqual(make_game(StandardSlots).bet_total(25), 25)


class ExpandedSettleTests(unittest.TestCase):
    def settle_with_grid(self, grid, bet, balance=100):
        game = make_game(ExpandedSlots, balance)
        with patch.object(game, "random_result", return_value=grid):
            return game, game.settle(bet)

    def test_losing_grid_loses_total_bet(self):
        grid = (("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B"))
        game, (result, payout, message, won) = self.settle_with_grid(grid, (5, 5, 5))
        self.assertFalse(won)
        self.assertEqual(payout, 0)
        self.assertEqual(game.account.balance, 85)
        self.assertEqual(result, grid)
        self.assertIn("NO MATCH", message)

    def test_winning_row_nets_payout_minus_total_bet(self):
        grid = (("A", "B", "C"), ("D", "D", "D"), ("C", "A", "B"))
        game, (_, payout, message, won) = self.settle_with_grid(grid, (5, 10, 5))
        self.assertTrue(won)
        self.assertEqual(payout, 50)
        # 100 - 20 (total bet) + 50 (payout)
        self.assertEqual(game.account.balance, 130)
        self.assertIn("ROWS 2 MATCH", message)

    def test_multiple_winning_rows_listed_in_message(self):
        grid = (("A", "A", "A"), ("B", "C", "A"), ("D", "D", "D"))
        game, (_, payout, message, won) = self.settle_with_grid(grid, (10, 0, 10))
        self.assertTrue(won)
        self.assertEqual(payout, 15 + 50)
        self.assertIn("ROWS 1,3 MATCH", message)

    def test_settle_cannot_overdraw_the_account(self):
        grid = (("A", "B", "C"),) * 3
        game = make_game(ExpandedSlots, 10)
        with patch.object(game, "random_result", return_value=grid):
            with self.assertRaises(ValueError):
                game.settle((10, 10, 10))


class ExpandedPromptBetTests(unittest.TestCase):
    def prompt_with(self, balance, inputs):
        game = make_game(ExpandedSlots, balance)
        with patch.object(game.view, "prompt", side_effect=inputs):
            return game, game.prompt_bet()

    def test_valid_bets_are_returned_as_a_tuple(self):
        _, bets = self.prompt_with(100, ["10,15,20"])
        self.assertEqual(bets, (10, 15, 20))

    def test_whitespace_around_values_is_ignored(self):
        _, bets = self.prompt_with(100, [" 1 , 2 , 3 "])
        self.assertEqual(bets, (1, 2, 3))

    def test_wrong_number_of_values_is_rejected(self):
        for bad in ("10", "10,20", "1,2,3,4"):
            _, bets = self.prompt_with(100, [bad, "5,5,5"])
            self.assertEqual(bets, (5, 5, 5))

    def test_non_numeric_values_are_rejected(self):
        _, bets = self.prompt_with(100, ["a,b,c", "5,5,5"])
        self.assertEqual(bets, (5, 5, 5))

    def test_negative_values_are_rejected(self):
        game, bets = self.prompt_with(100, ["-1,5,5", "5,5,5"])
        self.assertEqual(bets, (5, 5, 5))
        game.view.announce.assert_any_call("Bets cannot be negative.")

    def test_total_below_minimum_is_rejected(self):
        _, bets = self.prompt_with(100, ["1,0,0", "2,0,0"])
        self.assertEqual(bets, (2, 0, 0))

    def test_total_above_balance_is_rejected(self):
        _, bets = self.prompt_with(20, ["10,10,10", "10,5,5"])
        self.assertEqual(bets, (10, 5, 5))

    def test_bet_total_sums_the_lines(self):
        self.assertEqual(make_game(ExpandedSlots).bet_total((1, 2, 3)), 6)


class MenuPromptTests(unittest.TestCase):
    def test_full_menu_when_balance_covers_bet(self):
        game = make_game(StandardSlots, 100)
        self.assertEqual(game.menu_prompt(10), "[R]espin [C]hange Bet [Q]uit")

    def test_no_respin_when_balance_below_bet(self):
        game = make_game(StandardSlots, 5)
        self.assertEqual(game.menu_prompt(10), "[C]hange Bet [Q]uit")

    def test_only_quit_when_balance_below_minimum_bet(self):
        game = make_game(StandardSlots, 1)
        self.assertEqual(game.menu_prompt(10), "[Q]uit")


class PlayerChoiceTests(unittest.TestCase):
    def choose(self, balance, bet_total, inputs):
        game = make_game(StandardSlots, balance)
        with patch.object(game.view, "prompt", side_effect=inputs), \
             patch.object(game, "render"):
            return game.get_player_choice(("A", "B", "C"), bet_total)

    def test_quit_is_case_insensitive(self):
        self.assertEqual(self.choose(100, 10, ["q"]), "quit")
        self.assertEqual(self.choose(100, 10, ["Q"]), "quit")

    def test_respin(self):
        self.assertEqual(self.choose(100, 10, ["r"]), "respin")

    def test_change_bet(self):
        self.assertEqual(self.choose(100, 10, ["C"]), "change_bet")

    def test_invalid_input_reprompts(self):
        self.assertEqual(self.choose(100, 10, ["x", "zzz", "q"]), "quit")

    def test_empty_input_reprompts(self):
        self.assertEqual(self.choose(100, 10, ["", "q"]), "quit")

    def test_respin_refused_when_balance_below_bet(self):
        self.assertEqual(self.choose(5, 10, ["r", "q"]), "quit")

    def test_change_bet_refused_when_below_minimum(self):
        self.assertEqual(self.choose(1, 10, ["c", "q"]), "quit")


class PlayRoundTests(unittest.TestCase):
    def test_exits_when_player_cannot_afford_minimum_bet(self):
        game = make_game(StandardSlots, 1)
        with patch.object(game.view, "prompt", return_value=""):
            status = game.play_round()
        self.assertEqual(status, "EXIT")
        game.view.announce.assert_any_call(NO_FUNDS_MSG)
        self.assertEqual(game.stats.ending_balance, 1)

    def test_round_records_a_win_and_continues_on_respin(self):
        game = make_game(StandardSlots, 100)
        with patch.object(game, "prompt_bet", return_value=10), \
             patch.object(game, "spin_animation"), \
             patch.object(game, "render"), \
             patch.object(game, "settle", return_value=(("A", "A", "A"), 15, "MATCH", True)), \
             patch.object(game, "get_player_choice", return_value="respin"):
            status = game.play_round()
        self.assertEqual(status, "CONTINUE")
        self.assertEqual((game.stats.rounds_played, game.stats.wins, game.stats.losses), (1, 1, 0))
        self.assertFalse(game.take_new_bet)  # standing bet kept for respin

    def test_round_records_a_loss_and_exits_on_quit(self):
        game = make_game(StandardSlots, 100)
        with patch.object(game, "prompt_bet", return_value=10), \
             patch.object(game, "spin_animation"), \
             patch.object(game, "render"), \
             patch.object(game, "settle", return_value=(("A", "B", "C"), 0, "NO MATCH", False)), \
             patch.object(game, "get_player_choice", return_value="quit"):
            status = game.play_round()
        self.assertEqual(status, "EXIT")
        self.assertEqual((game.stats.rounds_played, game.stats.wins, game.stats.losses), (1, 0, 1))
        self.assertEqual(game.stats.ending_balance, game.account.balance)

    def test_change_bet_choice_requests_a_new_bet(self):
        game = make_game(StandardSlots, 100)
        with patch.object(game, "prompt_bet", return_value=10), \
             patch.object(game, "spin_animation"), \
             patch.object(game, "render"), \
             patch.object(game, "settle", return_value=(("A", "B", "C"), 0, "NO MATCH", False)), \
             patch.object(game, "get_player_choice", return_value="change_bet"):
            status = game.play_round()
        self.assertEqual(status, "CONTINUE")
        self.assertTrue(game.take_new_bet)

    def test_standing_bet_larger_than_balance_forces_new_bet(self):
        game = make_game(StandardSlots, 100)
        game.take_new_bet = False
        game.bet = 500
        with patch.object(game, "spin_animation") as spin:
            status = game.play_round()
        self.assertEqual(status, "CONTINUE")
        self.assertTrue(game.take_new_bet)
        spin.assert_not_called()


if __name__ == "__main__":
    unittest.main()
