import random
import time
from typing import Literal
from casino.accounts import Account
from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar

SlotsMenuChoice = Literal["respin", "change_bet", "quit"]

SLOTS_HEADER = """
┌───────────────────────────────┐
│         ♠ S L O T S ♠         │
└───────────────────────────────┘
"""
HEADER_OPTIONS = {
    "header": SLOTS_HEADER,
    "margin": 1,
}

BET_PROMPT = "How much would you like to bet on each row? (top,mid,bottom) e.g. 10,15,20"
INVALID_BET_MSG = "That's not a valid bet. Example: 10,15,20"
INVALID_INPUT_MSG = "Invalid input. Please try again."

SEC_BTWN_SPIN = 0.1
TOTAL_SPINS = 10
PAYLINES = 3

def get_slots_menu_prompt(ctx: GameContext, total_bet: int) -> str:
    """Generate slots menu prompt."""
    if ctx.account.balance < ctx.config.slots_min_line_bet:
        return f"[Q]uit"
    if ctx.account.balance < total_bet:
        return f"[C]hange Bet [Q]uit"
    else:
        return f"[R]espin [C]hange Bet [Q]uit"


def generate_payout_legend(
        low_items: list[str],
        high_items: list[str],
) -> str:
    """Generate payout legend."""
    low_items_str = " | ".join(low_items)
    high_items_str = " | ".join(high_items)
    max_len = max(len(low_items_str), len(high_items_str))
    low_str = f"Matching {low_items_str.ljust(max_len)}  | x1.5"
    high_str = f"Matching {high_items_str.ljust(max_len)}  | x5.0"
    return f"{low_str}\n{high_str}"


LOW_ITEMS = ["A", "B", "C"]
HIGH_ITEMS = ["D"]
ALL_ITEMS = LOW_ITEMS + HIGH_ITEMS
PAYOUT_LEGEND = generate_payout_legend(LOW_ITEMS, HIGH_ITEMS)


# Currently 3 horizontal pay lines, goal is to have several and:
# - implement pattern patching for wins across columns and diagonals
# - then maybe special lines

def get_rand_item() -> str:
    return random.choice(ALL_ITEMS)

def get_rand_grid():
    return (
        (get_rand_item(), get_rand_item(), get_rand_item()),
        (get_rand_item(), get_rand_item(), get_rand_item()),
        (get_rand_item(), get_rand_item(), get_rand_item()),
    )

def print_spin(grid, frame: int) -> None:
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

def get_line_bets(ctx: GameContext) -> tuple[int, int, int]:
    """Prompt user for bet amount per row."""
    account = ctx.account
    min_bet = ctx.config.slots_min_line_bet
    while True:
        cprint(PAYOUT_LEGEND + "\n\n")
        raw = cinput(BET_PROMPT).strip()
        parts = [p.strip() for p in raw.split(",")]
        if len(parts) != PAYLINES:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            cprint(INVALID_BET_MSG)
            continue
        try:
            bets = tuple(int(p) for p in parts)
        except ValueError:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            cprint(INVALID_BET_MSG)
            continue
        if any(b < 0 for b in bets):
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            cprint("Bets cannot be negative.")
            continue
        if sum(bets) < min_bet:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            cprint(f"You must bet at least {min_bet} chips.")
            continue
        total_bet = sum(bets)
        if total_bet > account.balance:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            cprint(f"You need {total_bet} chips total. You have {account.balance}.")
            continue
        return bets


def get_player_choice(ctx: GameContext, grid, total_bet: int) -> SlotsMenuChoice:
    """Prompt user for slots menu choice."""
    account = ctx.account
    min_bet = ctx.config.slots_min_line_bet
    first_iter = True

    while True:
        if not first_iter:
            clear_screen()
            display_topbar(account, **HEADER_OPTIONS)
            print_spin(grid, 0)
            cprint(INVALID_INPUT_MSG)
        first_iter = False
        menu_prompt = get_slots_menu_prompt(ctx, total_bet)
        player_input = cinput(menu_prompt).strip()
        if player_input == "":
            continue
        if player_input in "qQ":
            return "quit"
        elif player_input in "rR":
            if account.balance < total_bet:
                continue
            return "respin"
        elif player_input in "cC":
            if account.balance < min_bet:
                continue
            return "change_bet"


def spin_animation(
        account: Account,
        total_spins: int = TOTAL_SPINS,
        sec_btwn_spins: float = SEC_BTWN_SPIN,
) -> None:
    """Animate the spin of the slot machine."""
    # Animate pulling the arm
    for i in range(5):
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)
        print_spin(get_rand_grid(), i)
        time.sleep(sec_btwn_spins)
    # Animate the slots spinning
    for _ in range(total_spins):
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)
        print_spin(get_rand_grid(), 0)
        time.sleep(sec_btwn_spins)

def payout_for_row(row: tuple[str, str, str], bet_per_line: int) -> int:
    """Return payout for one horizontal payline."""
    a, b, c = row
    if not (a == b == c):
        return 0
    # High item match
    if a in HIGH_ITEMS:
        return bet_per_line * 5
    # Low item match
    return int(bet_per_line * 1.5)

def score_lines(grid, line_bets: tuple[int, int, int]) -> tuple[int, list[int]]:
    """ Returns the total_payout and winning_rows """
    total = 0
    winners: list[int] = []
    for i, row in enumerate(grid):
        bet_for_this_row = line_bets[i]
        p = payout_for_row(row, bet_for_this_row)
        if p > 0:
            total += p
            winners.append(i)
    return total, winners

def play_slots_expanded(ctx: GameContext) -> None:
    """Play slots game."""
    account = ctx.account
    min_bet = ctx.config.slots_min_line_bet
    take_new_bet = True
    line_bets: tuple[int, int, int] = (min_bet, min_bet, min_bet)
    while True:
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)
        if take_new_bet:
            if account.balance < (min_bet):
                cprint("You don't have enough money to make a bet.\n\n")
                cinput("Press Enter to continue...")
                return
            line_bets = get_line_bets(ctx)
            take_new_bet = False

        total_bet = sum(line_bets)
        if total_bet > account.balance:
            take_new_bet = True
            continue

        spin_animation(account)
        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)

        # Display final spin result
        grid = get_rand_grid()

        account.withdraw(total_bet)
        payout, winning_rows = score_lines(grid, line_bets)
        if payout > 0:
            account.deposit(payout)

        clear_screen()
        display_topbar(account, **HEADER_OPTIONS)
        print_spin(grid, 0)

        if payout > 0:
            rows_str = ",".join(str(r + 1) for r in winning_rows)
            cprint(f"ROWS {rows_str} MATCH: -{total_bet} +{payout} chips")
        else:
            cprint(f"NO MATCH: -{total_bet} chips")

        # Choose what to do after spin
        choice = get_player_choice(ctx, grid, total_bet)
        match choice:
            case "quit":
                return
            case "change_bet":
                take_new_bet = True
            case "respin":
                continue
