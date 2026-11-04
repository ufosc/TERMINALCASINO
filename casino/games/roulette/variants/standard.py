from casino.accounts import Account
from casino.stats import GameStats, display_stats
from casino.types import GameContext
from time import sleep

from casino.utils import cinput, clear_screen, cprint

from ..base import Roulette
from ..constants import STANDARD_AMERICAN_ROULETTE_WHEEL


class AmericanRoulette(Roulette):
    """Roulette using the American wheel, including 00."""

    def __init__(self, accounts: list[Account]) -> None:
        super().__init__(accounts)
        self.wheel = STANDARD_AMERICAN_ROULETTE_WHEEL
        self.valid_numbers = [number for number, _, _, _ in self.wheel]

    def submit_bets(self, context: GameContext) -> str | None:
        player_index = 0
        while player_index < len(self.accounts):
            if self._all_players_bankrupt():
                cprint("ERROR: All players have gone bankrupt. You cannot play any more roulette.")
                sleep(3)
                return "BANKRUPT"
            account = self.accounts[player_index]
            if account.balance == 0:
                cprint(f"Skipping player {player_index + 1} because of empty balance...")
                player_index += 1
                continue

            will_bet = self.view.prompt(
                context, f"🤵: Would you like to bet, Player {player_index + 1} (y/N): ",
                lambda value: value in {"", "y", "yes", "n", "no"},
                "Invalid input. Enter either 'Y' for yes or 'N' for no.",
            )
            if will_bet in {"", "n", "no"}:
                cprint("User skipped betting. Moving to next user...", end="\n\n")
                player_index += 1
                continue

            amount = self.view.prompt(
                context, f"Player {player_index + 1}'s Bet: ",
                lambda value: value.isdigit() and int(value) <= account.balance,
                "Please enter a positive integer within your balance.",
                transform=lambda value: value.strip(),
            )
            bet_type = self.view.prompt(
                context, "🤵: Would you like to bet on a color or a number? (C or N): ",
                lambda value: value in {"c", "color", "n", "number"},
                "Error: Invalid bet type. Choose either 'color' or 'number'.",
            )
            if bet_type in {"c", "color"}:
                bet_value = self.view.prompt(
                    context, "Enter color you want to bet on (red, black, green): ",
                    lambda value: value in self.valid_colors,
                    "Error: Chosen color is not red, green, or black.",
                )
                normalized_type = "color"
            else:
                bet_value = self.view.prompt(
                    context, "Enter number you would like to bet on: ",
                    lambda value: value in self.valid_numbers,
                    "Error: Invalid roulette number.",
                    render_table=True,
                    transform=lambda value: value.strip(),
                )
                normalized_type = "number"

            account.withdraw(int(amount))
            self.bets[str(account.aid)] = {
                "type": normalized_type,
                "value": self.normalize_color(bet_value),
                "amount": int(amount),
            }
            player_index += 1
        return None


StandardRoulette = AmericanRoulette


def play_roulette(context: GameContext) -> None:
    roulette = AmericanRoulette([context.account])
    _play(context, roulette, "American Roulette")


def _play(context: GameContext, roulette: Roulette, game_name: str) -> None:
    stats = GameStats(game_name, context.account.balance)
    while True:
        roulette.reset_round()
        clear_screen()
        roulette.view.display_topbar(context)
        if cinput("Press [Enter] to start a new round and [q] to quit: ").lower() in {"q", "quit"}:
            break
        previous_balance = context.account.balance
        if roulette.submit_bets(context) == "BANKRUPT":
            break
        roulette.spin_wheel(context)
        roulette.payout()
        if context.account.balance > previous_balance:
            stats.wins += 1
            stats.rounds_played += 1
        elif context.account.balance < previous_balance:
            stats.losses += 1
            stats.rounds_played += 1
        roulette.view.refresh_topbar(context)
        choice = cinput("🤵: Would you like to play another round (Y/n): ").strip().lower()
        if choice in {"", "y", "yes"}:
            continue
        if choice in {"n", "no"}:
            break
        while choice not in {"", "y", "yes", "n", "no"}:
            choice = roulette.view.prompt(
                context,
                "🤵: Would you like to play another round (Y/n): ",
                lambda value: value in {"", "y", "yes", "n", "no"},
                "Please enter 'Yes' or 'No'.",
            )
        if choice in {"n", "no"}:
            break
    stats.ending_balance = context.account.balance
    display_stats(stats)
