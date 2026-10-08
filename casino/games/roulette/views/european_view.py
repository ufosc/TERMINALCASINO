import time
from casino.types import GameContext

from ..base import (
    COLS,
    ROWS,
    ROULETTE_GRID,
    SEC_BTWN_SPIN,
    cprint_ansi_center,
    clear_screen,
    display_roulette_topbar,
)
from ..variants.european import (
    render_cell,
)
from .view import RouletteView


class EuropeanRouletteView(RouletteView):
    def print_wheel(self, highlighted_num=None) -> None:
        # clear current grid
        for row in range(ROWS):
            for col in range(COLS):
                ROULETTE_GRID[row][col] = ' '  # each empty spot is 2 spaces

        for (num_str, color, row, col) in self.wheel:
            if int(num_str.strip()) < 10:
                num_str = " " + num_str
            if highlighted_num is not None and num_str.strip() == highlighted_num.strip():
                # the spot in the column before and column after the number become *'s
                ROULETTE_GRID[row][col - 1] = "*"
                ROULETTE_GRID[row][col + 1] = "*"
            ROULETTE_GRID[row][col] = render_cell(num_str, color)

        wheel_lines = ["".join(row) for row in ROULETTE_GRID]
        # Center the wheel in the terminal
        for line in wheel_lines:
            cprint_ansi_center(line)


    def wheel_animation(self, ctx: GameContext, sequence, sec_btwn_spins: float = SEC_BTWN_SPIN) -> None:
        for num in sequence:
            clear_screen()
            display_roulette_topbar(ctx)
            self.print_wheel(highlighted_num=num)
            time.sleep(sec_btwn_spins)

