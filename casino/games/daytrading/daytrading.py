import sys
import shutil
import threading
import ctypes
from typing import Callable

from casino.types import GameContext
from casino.utils import clear_screen, cprint, cinput, display_topbar

from .market import MarketProvider, create_market
from .portfolio import Portfolio

DAYTRADING_HEADER = """
┌───────────────────────────────────┐
│     $ D A Y  T R A D I N G $      │
└───────────────────────────────────┘
"""
HEADER_OPTIONS = {
    "header": DAYTRADING_HEADER,
    "margin": 1,
}

CHIP_TO_DOLLAR = 10
TICKER_REFRESH = 1.0

MENU_PROMPT = "[V]iew  [B]uy  [S]ell  [L]ookup  [H]istory  [D]eposit  [W]ithdraw  [Q]uit: "


# ---------------------------------------------------------------------------
#  Cursor position detection (Windows API)
# ---------------------------------------------------------------------------

def _get_cursor_row() -> int:
    """Return the current cursor row (1-based, relative to viewport).

    Uses the Windows console API to read the actual cursor position so we
    never have to guess/hardcode terminal row numbers.
    """
    if sys.platform != "win32":
        return 1
    try:
        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class SMALL_RECT(ctypes.Structure):
            _fields_ = [
                ("Left", ctypes.c_short), ("Top", ctypes.c_short),
                ("Right", ctypes.c_short), ("Bottom", ctypes.c_short),
            ]

        class CSBI(ctypes.Structure):
            _fields_ = [
                ("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", ctypes.c_ushort),
                ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", COORD),
            ]

        handle = ctypes.windll.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        csbi = CSBI()
        if ctypes.windll.kernel32.GetConsoleScreenBufferInfo(
            handle, ctypes.byref(csbi)
        ):
            # dwCursorPosition.Y is 0-based buffer row
            # srWindow.Top is the first visible row in the viewport
            # ANSI \033[row;colH is 1-based relative to viewport
            return csbi.dwCursorPosition.Y - csbi.srWindow.Top + 1
    except Exception:
        pass
    return 1


# ---------------------------------------------------------------------------
#  ANSI live-update helpers
# ---------------------------------------------------------------------------

def _ansi_update_rows(rows: list[str], start_row: int) -> None:
    """Overwrite terminal rows in-place, preserving user cursor."""
    try:
        width = shutil.get_terminal_size().columns
        from casino.utils import theme
        c, r = theme["color"], theme["reset"]

        buf = "\033[s"  # save cursor
        for i, text in enumerate(rows):
            buf += f"\033[{start_row + i};1H\033[2K{c}{text.center(width)}{r}"
        buf += "\033[u"  # restore cursor
        sys.stdout.write(buf)
        sys.stdout.flush()
    except Exception:
        pass


def _build_ticker_rows(market: MarketProvider) -> list[str]:
    entries = []
    for sym in market.list_all():
        quote = market.get_quote(sym)
        if quote:
            sign = "+" if quote.change >= 0 else ""
            entries.append(f"{sym} ${quote.price:,.2f}({sign}{quote.change:.2f})")
    mid = len(entries) // 2
    return ["  ".join(entries[:mid]), "  ".join(entries[mid:])]


def _build_table_rows(market: MarketProvider) -> list[str]:
    rows = []
    for sym in market.list_all():
        quote = market.get_quote(sym)
        if quote:
            sign = "+" if quote.change >= 0 else ""
            rows.append(f"  {sym:<8}  ${quote.price:>9,.2f}  ({sign}{quote.change:.2f})")
        else:
            rows.append(f"  {sym}")
    return rows


class _LiveUpdater:
    """Background thread that refreshes terminal rows via ANSI escapes.

    A single instance is reused — call start(row, builder) each time the
    screen is redrawn so it always targets the correct rows.
    """

    def __init__(self, market: MarketProvider) -> None:
        self._market = market
        self._start_row = 0
        self._builder: Callable[[MarketProvider], list[str]] | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(
        self,
        start_row: int,
        builder: Callable[[MarketProvider], list[str]],
    ) -> None:
        self.stop()
        self._start_row = start_row
        self._builder = builder
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _run(self) -> None:
        while not self._stop.wait(TICKER_REFRESH):
            if self._builder:
                rows = self._builder(self._market)
                _ansi_update_rows(rows, self._start_row)


# ---------------------------------------------------------------------------
#  Screen helpers
# ---------------------------------------------------------------------------

def _display_header(ctx: GameContext) -> None:
    clear_screen()
    display_topbar(ctx.account, **HEADER_OPTIONS)


def _display_main_screen(
    ctx: GameContext, market: MarketProvider, portfolio: Portfolio,
) -> int:
    """Draw main menu screen. Returns the row where the ticker starts."""
    clear_screen()
    display_topbar(ctx.account, **HEADER_OPTIONS)
    cprint(f"{market.provider_name()}  |  Trading Cash: ${portfolio.cash:,.2f}")
    # Detect the actual cursor row — this is where the ticker will be drawn
    ticker_row = _get_cursor_row()
    for line in _build_ticker_rows(market):
        cprint(line)
    print()  # blank after ticker
    return ticker_row


def _display_lookup_screen(ctx: GameContext, market: MarketProvider) -> int:
    """Draw lookup screen. Returns the row where the stock table starts."""
    clear_screen()
    display_topbar(ctx.account, **HEADER_OPTIONS)
    cprint("Available stocks:")
    cprint("  " + "-" * 40)
    # Detect the actual cursor row — this is where the table will be drawn
    table_row = _get_cursor_row()
    for line in _build_table_rows(market):
        cprint(line)
    print()  # blank after table
    return table_row


# ---------------------------------------------------------------------------
#  Deposit / withdraw
# ---------------------------------------------------------------------------

def _deposit_chips(ctx: GameContext, portfolio: Portfolio) -> None:
    account = ctx.account
    _display_header(ctx)
    cprint(f"Casino balance: {account.balance} chips")
    cprint(f"Exchange rate:  1 chip = ${CHIP_TO_DOLLAR} trading dollars")
    cprint(f"Trading balance: ${portfolio.cash:,.2f}")
    cprint("")

    while True:
        raw = cinput("Chips to deposit (0 to skip): ").strip()
        try:
            chips = int(raw)
        except ValueError:
            cprint("Enter a valid number.")
            continue
        if chips < 0:
            cprint("Cannot deposit a negative amount.")
            continue
        if chips > account.balance:
            cprint(f"You only have {account.balance} chips.")
            continue
        if chips > 0:
            account.withdraw(chips)
            dollars = chips * CHIP_TO_DOLLAR
            portfolio.cash += dollars
            portfolio.save()
            cprint(f"\nDeposited {chips} chips -> +${dollars:,.2f} trading dollars")
            cprint(f"Trading balance: ${portfolio.cash:,.2f}")
        break


def _withdraw_cash(ctx: GameContext, portfolio: Portfolio) -> None:
    account = ctx.account
    _display_header(ctx)
    cprint(f"Trading balance: ${portfolio.cash:,.2f}")
    cprint(f"Exchange rate:  ${CHIP_TO_DOLLAR} trading dollars = 1 chip")
    max_chips = int(portfolio.cash // CHIP_TO_DOLLAR)
    cprint(f"Maximum withdrawal: {max_chips} chips (${max_chips * CHIP_TO_DOLLAR:,.2f})")
    cprint("")

    if max_chips == 0:
        cprint("Not enough trading cash to withdraw even 1 chip.\n")
        return

    while True:
        raw = cinput(f"Chips to withdraw (0 to skip, max {max_chips}): ").strip()
        try:
            chips = int(raw)
        except ValueError:
            cprint("Enter a valid number.")
            continue
        if chips < 0:
            cprint("Cannot withdraw a negative amount.")
            continue
        if chips > max_chips:
            cprint(f"Maximum is {max_chips} chips.")
            continue
        if chips > 0:
            dollars = chips * CHIP_TO_DOLLAR
            portfolio.cash -= dollars
            account.deposit(chips)
            portfolio.save()
            cprint(f"\nWithdrew ${dollars:,.2f} -> +{chips} chips")
            cprint(f"Casino balance: {account.balance} chips")
            cprint(f"Trading balance: ${portfolio.cash:,.2f}")
        break


def _auto_withdraw_on_exit(ctx: GameContext, portfolio: Portfolio) -> None:
    chips_back = int(portfolio.cash // CHIP_TO_DOLLAR)
    if chips_back > 0:
        dollars = chips_back * CHIP_TO_DOLLAR
        portfolio.cash -= dollars
        ctx.account.deposit(chips_back)
        portfolio.save()
        cprint(f"Auto-converted ${dollars:,.2f} -> +{chips_back} chips returned")
    if portfolio.cash > 0:
        cprint(f"${portfolio.cash:,.2f} remains in trading account for next visit")


# ---------------------------------------------------------------------------
#  Game actions
# ---------------------------------------------------------------------------

def _show_portfolio(portfolio: Portfolio, market: MarketProvider) -> None:
    cprint(f"Trading Cash: ${portfolio.cash:,.2f}\n")

    if not portfolio.holdings:
        cprint("No stocks held.\n")
        return

    cprint("  Symbol     Qty     Price       Value")
    cprint("  " + "-" * 42)
    prices: dict[str, float] = {}
    for symbol, qty in sorted(portfolio.holdings.items()):
        quote = market.get_quote(symbol)
        price = quote.price if quote else 0.0
        prices[symbol] = price
        value = price * qty
        change_str = ""
        if quote and quote.change != 0:
            sign = "+" if quote.change > 0 else ""
            change_str = f" ({sign}{quote.change:.2f})"
        cprint(f"  {symbol:<8}  {qty:>4}   ${price:>9,.2f}  ${value:>10,.2f}{change_str}")

    cprint("  " + "-" * 42)
    sv = portfolio.stock_value(prices)
    cprint(f"  Stock Value:  ${sv:,.2f}")
    cprint(f"  Total Value:  ${portfolio.cash + sv:,.2f}\n")


def _buy_stock(portfolio: Portfolio, market: MarketProvider) -> None:
    symbol = cinput("Symbol to buy: ").strip().upper()
    if not symbol:
        return

    quote = market.get_quote(symbol)
    if not quote:
        cprint(f"\nSymbol '{symbol}' not found.\n")
        return

    if quote.price <= 0:
        cprint(f"\nInvalid quote for '{symbol}': non-positive price received. Please try again later.\n")
        return

    cprint(f"\n  {quote.symbol}: ${quote.price:,.2f}")
    max_qty = int(portfolio.cash // quote.price)
    cprint(f"  Trading cash: ${portfolio.cash:,.2f} (max {max_qty} shares)\n")

    qty_str = cinput("Quantity: ").strip()
    try:
        qty = int(qty_str)
    except ValueError:
        cprint("\nInvalid quantity.\n")
        return

    if qty <= 0:
        cprint("\nQuantity must be positive.\n")
        return

    cost = qty * quote.price
    if cost > portfolio.cash:
        cprint(f"\nInsufficient funds. Need ${cost:,.2f}, have ${portfolio.cash:,.2f}.\n")
        return

    portfolio.buy(symbol, qty, quote.price)
    portfolio.save()
    cprint(f"\nBought {qty} x {symbol} @ ${quote.price:,.2f} = ${cost:,.2f}\n")


def _sell_stock(portfolio: Portfolio, market: MarketProvider) -> None:
    if not portfolio.holdings:
        cprint("\nNo stocks to sell.\n")
        return

    cprint("\nYour holdings:")
    for sym, qty in sorted(portfolio.holdings.items()):
        cprint(f"  {sym}: {qty} shares")
    cprint("")

    symbol = cinput("Symbol to sell: ").strip().upper()
    if not symbol:
        return

    held = portfolio.holdings.get(symbol, 0)
    if held == 0:
        cprint(f"\nYou don't hold any {symbol}.\n")
        return

    quote = market.get_quote(symbol)
    if not quote:
        cprint(f"\nCannot get price for '{symbol}'.\n")
        return

    cprint(f"\n  {symbol}: ${quote.price:,.2f} (you hold {held} shares)\n")

    qty_str = cinput(f"Quantity (max {held}): ").strip()
    try:
        qty = int(qty_str)
    except ValueError:
        cprint("\nInvalid quantity.\n")
        return

    if qty <= 0 or qty > held:
        cprint(f"\nInvalid quantity. You hold {held} shares.\n")
        return

    revenue = qty * quote.price
    portfolio.sell(symbol, qty, quote.price)
    portfolio.save()
    cprint(f"\nSold {qty} x {symbol} @ ${quote.price:,.2f} = +${revenue:,.2f}\n")


def _show_history(portfolio: Portfolio) -> None:
    if not portfolio.history:
        cprint("\nNo transaction history.\n")
        return

    cprint("\n  Side   Symbol     Qty       Price       Time")
    cprint("  " + "-" * 55)
    for tx in portfolio.history[-20:]:
        side_str = "BUY " if tx.side == "buy" else "SELL"
        cprint(
            f"  {side_str}   {tx.symbol:<8}  {tx.qty:>4}   ${tx.price:>9,.2f}   {tx.timestamp}"
        )
    if len(portfolio.history) > 20:
        cprint(f"\n  (showing last 20 of {len(portfolio.history)} transactions)")
    cprint("")


# ---------------------------------------------------------------------------
#  Main game loop
# ---------------------------------------------------------------------------

def play_daytrading(ctx: GameContext) -> None:
    market = create_market()
    portfolio = Portfolio.load_or_create(ctx.account.name)

    updater = _LiveUpdater(market)

    try:
        _deposit_chips(ctx, portfolio)
        cinput("Press Enter to start trading...")

        while True:
            ticker_row = _display_main_screen(ctx, market, portfolio)
            updater.start(ticker_row, _build_ticker_rows)
            choice = cinput(MENU_PROMPT).strip().lower()
            updater.stop()

            match choice:
                case "v":
                    _display_header(ctx)
                    _show_portfolio(portfolio, market)
                    cinput("Press Enter to continue...")

                case "b":
                    _display_header(ctx)
                    _buy_stock(portfolio, market)
                    cinput("Press Enter to continue...")

                case "s":
                    _display_header(ctx)
                    _sell_stock(portfolio, market)
                    cinput("Press Enter to continue...")

                case "l":
                    table_row = _display_lookup_screen(ctx, market)
                    updater.start(table_row, _build_table_rows)
                    cinput("Press Enter to go back...")
                    updater.stop()

                case "h":
                    _display_header(ctx)
                    _show_history(portfolio)
                    cinput("Press Enter to continue...")

                case "d":
                    _deposit_chips(ctx, portfolio)
                    cinput("Press Enter to continue...")

                case "w":
                    _withdraw_cash(ctx, portfolio)
                    cinput("Press Enter to continue...")

                case "q":
                    _display_header(ctx)
                    _auto_withdraw_on_exit(ctx, portfolio)
                    portfolio.save()
                    cinput("Press Enter to return to casino...")
                    return

                case _:
                    cprint("\nInvalid input. Please try again.\n")
                    cinput("Press Enter to continue...")
    finally:
        portfolio.save()
        updater.stop()
