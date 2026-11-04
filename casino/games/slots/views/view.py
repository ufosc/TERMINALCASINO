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

    def render_slot_machine(self, data: tuple, frame: int) -> str:
        """Renders and returns the formatted slot machine output string at the given animation frame."""
        
        legend_lines = PAYOUT_LEGEND.splitlines()
        low_line = legend_lines[0] if len(legend_lines) > 0 else ""
        high_line = legend_lines[1] if len(legend_lines) > 1 else ""

        def pad_line(line: str, width: int = 38) -> str:
            return line.ljust(width)

        low_line = pad_line(low_line)
        high_line = pad_line(high_line)

        if isinstance(data[0], tuple):
            # 3x3 grid
            row0 = [item.center(7) for item in data[0]]
            row1 = [item.center(7) for item in data[1]]
            row2 = [item.center(7) for item in data[2]]
        else:
            # Middle slot row only
            row0 = ["       ", "       ", "       "]
            row1 = [item.center(7) for item in data]
            row2 = ["       ", "       ", "       "]

        match frame:
            case 0 | 5:
                return f"""
┌───────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦    │
│───────────────────────────────────────│
    │                                       │┌───┐
    │   ┌───────┐   ┌───────┐   ┌───────┐   ││   │
    │   │{row0[0]}│   │{row0[1]}│   │{row0[2]}│   │└───┘
    │   └───────┘   └───────┘   └───────┘   │ │ │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │ │ │
    │ - │{row1[0]}│   │{row1[1]}│   │{row1[2]}│ - │ │ │
    │   └───────┘   └───────┘   └───────┘   │ │ │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │ │ │
    │   │{row2[0]}│   │{row2[1]}│   │{row2[2]}│   │─┘ │
    │   └───────┘   └───────┘   └───────┘   │───┘
│                                       │
│───────────────────────────────────────│
│                PAYOUTS                │
│                                       │
│ {low_line}│
│ {high_line}│
│                                       │
└───────────────────────────────────────┘
                """.strip()
            
            case 1 | 4:
                return f"""
┌───────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦    │
│───────────────────────────────────────│
│                                       │
│   ┌───────┐   ┌───────┐   ┌───────┐   │
    │   │{row0[0]}│   │{row0[1]}│   │{row0[2]}│   │┌───┐
    │   └───────┘   └───────┘   └───────┘   ││   │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │└───┘
    │ - │{row1[0]}│   │{row1[1]}│   │{row1[2]}│ - │ │ │
    │   └───────┘   └───────┘   └───────┘   │ │ │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │ │ │
    │   │{row2[0]}│   │{row2[1]}│   │{row2[2]}│   │─┘ │
    │   └───────┘   └───────┘   └───────┘   │───┘
│                                       │
│───────────────────────────────────────│
│                PAYOUTS                │
│                                       │
│ {low_line}│
│ {high_line}│
│                                       │
└───────────────────────────────────────┘
                """.strip()

            case 2 | 3:
                return f"""
┌───────────────────────────────────────┐
│   ♦ T E R M I N A L  C A S I N O ♦    │
│───────────────────────────────────────│
│                                       │
│   ┌───────┐   ┌───────┐   ┌───────┐   │
│   │{row0[0]}│   │{row0[1]}│   │{row0[2]}│   │
│   └───────┘   └───────┘   └───────┘   │
│   ┌───────┐   ┌───────┐   ┌───────┐   │
    │ - │{row1[0]}│   │{row1[1]}│   │{row1[2]}│ - │┌───┐
    │   └───────┘   └───────┘   └───────┘   ││   │
    │   ┌───────┐   ┌───────┐   ┌───────┐   │└───┘
    │   │{row2[0]}│   │{row2[1]}│   │{row2[2]}│   │─┘ │
    │   └───────┘   └───────┘   └───────┘   │───┘
│                                       │
│───────────────────────────────────────│
│                PAYOUTS                │
│                                       │
│ {low_line}│
│ {high_line}│
│                                       │
└───────────────────────────────────────┘
                """.strip()

        return "" 

    def render_row(self, items: tuple[str, str, str], frame: int = 0) -> None:
        """Draw the base game's single payline at the given animation frame."""
        cprint(self.render_slot_machine(items, frame))

    def render_grid(self, grid, frame: int = 0) -> None:
        """Draw the expanded game's 3x3 payline grid at the given animation frame."""
        cprint(self.render_slot_machine(grid, frame))
