from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from .utils import cprint, cinput, clear_screen
if TYPE_CHECKING:
    from .games.uno.player import Player


@dataclass
class GameStats:
    game_name: str
    starting_balance: int
    ending_balance: int = 0
    rounds_played: int = 0
    wins: int = 0
    losses: int = 0
    pushes: int = 0

    @property
    def net(self) -> int:
        return self.ending_balance - self.starting_balance

    @property
    def win_rate(self) -> str:
        if self.rounds_played == 0:
            return "N/A"
        return f"{self.wins / self.rounds_played * 100:.1f}%"

@dataclass
class UnoGameStats:
    game_name: str
    player: Player

    @property
    def most_common_color(self)-> str:
        return max(self.player.color_counts, key=self.player.color_counts.get)

def display_stats(stats: GameStats | UnoGameStats, game_name: str = "poker", player: Player = None, rounds_played: int = 0) -> None:
    """Display a post-game session summary."""
    clear_screen()
    rows = []
    if game_name != "uno":
        net = stats.net
        net_str = f"+{net}" if net > 0 else str(net)

        rows = [
            ["Game", stats.game_name],
            ["Hands Played", str(stats.rounds_played)],
            ["Wins", str(stats.wins)],
            ["Losses", str(stats.losses)],
            ["Pushes", str(stats.pushes)],
            ["Win Rate", stats.win_rate],
            ["", ""],
            ["Starting Balance", str(stats.starting_balance)],
            ["Ending Balance", str(stats.ending_balance)],
            ["Net Profit/Loss", net_str],
        ]
    elif game_name == "uno":
        rows = [
            ["Game", game_name],
            ["Rounds Played", str(rounds_played)],
            ["Player Name", stats.player.name],
            ["Cards Drawn", str(stats.player.cards_drawn)],
            ["Cards Played", str(stats.player.cards_played)],
            ["Wilds Played", str(stats.player.wilds_played)],
            ["Plus2 Played", str(stats.player.plus2_played)],
            ["Plus4 Played", str(stats.player.plus4_played)],
            ["Skips Played", str(stats.player.skips_played)],
            ["Reverses Played", str(stats.player.reverses_played)],
            ["Red Cards Played", str(stats.player.reds_played)],
            ["Green Cards Played", str(stats.player.greens_played)],
            ["Blue Cards Played", str(stats.player.blues_played)],
            ["Yellow Cards Played", str(stats.player.yellows_played)],
            ["Most Common Color", stats.most_common_color],
        ]
        if stats.player.winner:
            rows[3][0] = "Cards Drawn/Played"
            rows.remove(rows[4])
    label_width = max(len(r[0]) for r in rows)
    value_width = max(len(r[1]) for r in rows)
    inner_width = label_width + value_width + 6  # padding + colon + spaces
    box_width = inner_width + 4  # borders + margin

    title = " Session Summary "
    if game_name == "uno": title += f"for {player.name}" 
    side = (box_width - 2 - len(title)) // 2
    top_border = f"┌{'─' * side}{title}{'─' * (box_width - 2 - side - len(title))}┐"
    bot_border = f"└{'─' * (box_width - 2)}┘"

    cprint(top_border)
    for label, value in rows:
        if label == "":
            cprint(f"│{' ' * (box_width - 2)}│")
        else:
            line = f"  {label + ':':<{label_width + 1}}  {value:>{value_width}}  "
            cprint(f"│{line}│")
    cprint(bot_border)
    if game_name != "uno":
        cprint("")
        cinput("Press Enter to return to menu...")
