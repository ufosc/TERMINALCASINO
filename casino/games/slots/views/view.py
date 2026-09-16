from casino.utils import clear_screen, cprint, cinput, display_topbar
from ..constants import HEADER_OPTIONS, PAYOUT_LEGEND


class SlotsView:
    """
    Owns all terminal rendering and user input for Slots games.

    Game/round logic should never call cinput/cprint/clear_screen directly —
    it should ask this class to do it.
    """

    def __init__(self, context) -> None:
        self.context = context

    def display_topbar(self) -> None:
        display_topbar(self.context.account, **HEADER_OPTIONS)

    def clear_and_topbar(self) -> None:
        clear_screen()
        self.display_topbar()

    def show_payout_legend(self) -> None:
        cprint(PAYOUT_LEGEND + "\n\n")

    def prompt(self, prompt_str: str) -> str:
        return cinput(prompt_str).strip()

    def announce(self, message: str) -> None:
        cprint(message)

    def render_row(self, items: tuple[str, str, str], frame: int = 0) -> None:
        """Draw the base game's single payline at the given animation frame."""
        legend_lines = PAYOUT_LEGEND.splitlines()
        low_line = legend_lines[0] if len(legend_lines) > 0 else ""
        high_line = legend_lines[1] if len(legend_lines) > 1 else ""

        def pad_line(line: str, width: int = 38) -> str:
            return line.ljust(width)

        low_line = pad_line(low_line)
        high_line = pad_line(high_line)

        match frame:
            case 0 | 5:
                cprint(f"""
┌───────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦    │
│───────────────────────────────────────│
    │                                       │┌───┐
    │   ┌───────┐   ┌───────┐   ┌───────┐   ││   │
    │   │       │   │       │   │       │   │└───┘
    │   └───────┘   └───────┘   └───────┘   │ │ │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │ │ │
    │ - │{items[0].center(7)}│   │{items[1].center(7)}│   │{items[2].center(7)}│ - │ │ │
    │   └───────┘   └───────┘   └───────┘   │ │ │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │ │ │
    │   │       │   │       │   │       │   │─┘ │
    │   └───────┘   └───────┘   └───────┘   │───┘
│                                       │
│───────────────────────────────────────│
│                PAYOUTS                │
│                                       │
│ {low_line}│
│ {high_line}│
│                                       │
└───────────────────────────────────────┘
                """.strip())

            case 1 | 4:
                cprint(f"""
┌───────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦    │
│───────────────────────────────────────│
│                                       │
│   ┌───────┐   ┌───────┐   ┌───────┐   │
    │   │       │   │       │   │       │   │┌───┐
    │   └───────┘   └───────┘   └───────┘   ││   │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │└───┘
    │ - │{items[0].center(7)}│   │{items[1].center(7)}│   │{items[2].center(7)}│ - │ │ │
    │   └───────┘   └───────┘   └───────┘   │ │ │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │ │ │
    │   │       │   │       │   │       │   │─┘ │
    │   └───────┘   └───────┘   └───────┘   │───┘
│                                       │
│───────────────────────────────────────│
│                PAYOUTS                │
│                                       │
│ {low_line}│
│ {high_line}│
│                                       │
└───────────────────────────────────────┘
                """.strip())

            case 2 | 3:
                cprint(f"""
┌───────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦    │
│───────────────────────────────────────│
│                                       │
│   ┌───────┐   ┌───────┐   ┌───────┐   │
│   │       │   │       │   │       │   │
│   └───────┘   └───────┘   └───────┘   │
│   ┌───────┐   ┌───────┐   ┌───────┐   │
    │ - │{items[0].center(7)}│   │{items[1].center(7)}│   │{items[2].center(7)}│ - │┌───┐
    │   └───────┘   └───────┘   └───────┘   ││   │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │└───┘
    │   │       │   │       │   │       │   │─┘ │
    │   └───────┘   └───────┘   └───────┘   │───┘
│                                       │
│───────────────────────────────────────│
│                PAYOUTS                │
│                                       │
│ {low_line}│
│ {high_line}│
│                                       │
└───────────────────────────────────────┘
                """.strip())

    def render_grid(self, grid, frame: int = 0) -> None:
        """Draw the expanded game's 3x3 payline grid at the given animation frame."""
        legend_lines = PAYOUT_LEGEND.splitlines()
        low_line = legend_lines[0] if len(legend_lines) > 0 else ""
        high_line = legend_lines[1] if len(legend_lines) > 1 else ""

        def pad_line(line: str, width: int = 38) -> str:
            return line.ljust(width)

        low_line = pad_line(low_line)
        high_line = pad_line(high_line)

        match frame:
            case 0 | 5:
                cprint(f"""
┌───────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦    │
│───────────────────────────────────────│
    │                                       │┌───┐
    │   ┌───────┐   ┌───────┐   ┌───────┐   ││   │
    │   │{grid[0][0].center(7)}│   │{grid[0][1].center(7)}│   │{grid[0][2].center(7)}│   │└───┘
    │   └───────┘   └───────┘   └───────┘   │ │ │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │ │ │
    │ - │{grid[1][0].center(7)}│   │{grid[1][1].center(7)}│   │{grid[1][2].center(7)}│ - │ │ │
    │   └───────┘   └───────┘   └───────┘   │ │ │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │ │ │
    │   │{grid[2][0].center(7)}│   │{grid[2][1].center(7)}│   │{grid[2][2].center(7)}│   │─┘ │
    │   └───────┘   └───────┘   └───────┘   │───┘
│                                       │
│───────────────────────────────────────│
│                PAYOUTS                │
│                                       │
│ {low_line}│
│ {high_line}│
│                                       │
└───────────────────────────────────────┘
                """.strip())

            case 1 | 4:
                cprint(f"""
┌───────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦    │
│───────────────────────────────────────│
│                                       │
│   ┌───────┐   ┌───────┐   ┌───────┐   │
    │   │{grid[0][0].center(7)}│   │{grid[0][1].center(7)}│   │{grid[0][2].center(7)}│   │┌───┐
    │   └───────┘   └───────┘   └───────┘   ││   │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │└───┘
    │ - │{grid[1][0].center(7)}│   │{grid[1][1].center(7)}│   │{grid[1][2].center(7)}│ - │ │ │
    │   └───────┘   └───────┘   └───────┘   │ │ │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │ │ │
    │   │{grid[2][0].center(7)}│   │{grid[2][1].center(7)}│   │{grid[2][2].center(7)}│   │─┘ │
    │   └───────┘   └───────┘   └───────┘   │───┘
│                                       │
│───────────────────────────────────────│
│                PAYOUTS                │
│                                       │
│ {low_line}│
│ {high_line}│
│                                       │
└───────────────────────────────────────┘
                """.strip())

            case 2 | 3:
                cprint(f"""
┌───────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦    │
│───────────────────────────────────────│
│                                       │
│   ┌───────┐   ┌───────┐   ┌───────┐   │
│   │{grid[0][0].center(7)}│   │{grid[0][1].center(7)}│   │{grid[0][2].center(7)}│   │
│   └───────┘   └───────┘   └───────┘   │
│   ┌───────┐   ┌───────┐   ┌───────┐   │
    │ - │{grid[1][0].center(7)}│   │{grid[1][1].center(7)}│   │{grid[1][2].center(7)}│ - │┌───┐
    │   └───────┘   └───────┘   └───────┘   ││   │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │└───┘
    │   │{grid[2][0].center(7)}│   │{grid[2][1].center(7)}│   │{grid[2][2].center(7)}│   │─┘ │
    │   └───────┘   └───────┘   └───────┘   │───┘
│                                       │
│───────────────────────────────────────│
│                PAYOUTS                │
│                                       │
│ {low_line}│
│ {high_line}│
│                                       │
└───────────────────────────────────────┘
                """.strip())
