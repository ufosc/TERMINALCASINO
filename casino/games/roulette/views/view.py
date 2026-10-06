import time
from casino.types import GameContext

from ..base import (
    COLS,
    ROWS,
    ROULETTE_GRID,
    SEC_BTWN_SPIN,
    STANDARD_AMERICAN_ROULETTE_WHEEL,
    clear_screen,
    cprint_ansi_center,
    cprint_table_center,
    display_roulette_topbar,
    refresh_roulette_topbar,
)


class RouletteView:
    cprint_ansi_center = staticmethod(cprint_ansi_center)
    cprint_table_center = staticmethod(cprint_table_center)
    display_roulette_topbar = staticmethod(display_roulette_topbar)
    refresh_roulette_topbar = staticmethod(refresh_roulette_topbar)

    def __init__(self, roulette):
        self.roulette = roulette

    def __getattr__(self, name):
        return getattr(self.roulette, name)

    def print_wheel(self, highlighted_num = None) -> None:
        # clear current grid
        for row in range(len(ROULETTE_GRID)):
            for col in range(len(ROULETTE_GRID[0])):
                ROULETTE_GRID[row][col] = ' ' # each empty spot is 2 spaces

        for (num_str, color, row, col) in STANDARD_AMERICAN_ROULETTE_WHEEL:
            # col += 29
            if num_str != "00" and int(num_str.strip()) < 10:
                num_str = " " + num_str
            if num_str.strip() == highlighted_num.strip():
                # the spot in the column before and column after the number become *'s
                ROULETTE_GRID[row][col-1] = "*"
                ROULETTE_GRID[row][col+1] = "*"

            if color == "green":
                ROULETTE_GRID[row][col] = f"\x1b[42m\x1b[97m{num_str}\x1b[0m"
            elif color == "black":
                ROULETTE_GRID[row][col] = f"\x1b[40m\x1b[97m{num_str}\x1b[0m"
            else:
                ROULETTE_GRID[row][col] = f"\x1b[41m\x1b[97m{num_str}\x1b[0m"

        wheel_lines = ["".join(row) for row in ROULETTE_GRID]
        for line in wheel_lines:
            cprint_ansi_center(line)


    def wheel_animation(self, ctx: GameContext, sequence, sec_btwn_spins: float = SEC_BTWN_SPIN) -> None:
        for num in sequence:
            clear_screen()
            display_roulette_topbar(ctx)
            self.print_wheel(highlighted_num = num)
            time.sleep(sec_btwn_spins)


    def _format_bet(self, bet: dict) -> str:
        t = bet["type"]
        v = bet["value"]
        a = bet["amount"]

        if t == "inside_number":
            return f"{a} on number {v}"

        if t == "outside_color":
            return f"{a} on {v} (color)"

        if t == "outside_parity":
            return f"{a} on {v} (parity)"

        if t == "outside_highlow":
            return f"{a} on {v} (high/low)"

        if t == "outside_dozen":
            label = {"1": "1-12", "2": "13-24", "3": "25-36"}[v]
            return f"{a} on dozen {v} ({label})"

        if t == "outside_column":
            return f"{a} on column {v}"

        return f"{a} on {t}:{v}"

