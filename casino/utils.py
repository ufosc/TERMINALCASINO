import os
import shutil
from typing import Optional

from casino.accounts import Account


def clear_screen() -> None:
    """Clear the screen."""
    if os.name == "nt":  # Windows
        os.system("cls")
    else:  # Unix
        # clear screen + clear scrollback buffer
        os.system('clear && printf "\\033[3J"')


def cprint(*args, sep: str = " ", end: str = "\n") -> None:
    """Print text in the center of the screen."""
    terminal_width = shutil.get_terminal_size().columns
    text = sep.join(map(str, args))

    # split lines and print each one centered
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if i < len(lines) - 1:
            print(line.center(terminal_width))
        else:
            print(line.center(terminal_width), end=end)


def cinput(prompt: str = "") -> str:
    """Get input from the user in the center of the screen."""
    terminal_width = shutil.get_terminal_size().columns
    centered_prompt = prompt.center(terminal_width)
    print(centered_prompt)

    # move cursor to the center for input
    cursor_padding = (terminal_width // 2) + 1
    print(" " * cursor_padding, end="")
    return input().strip()


def display_topbar(
    account: Optional[Account],
    header: str,
    margin: int = 1,
) -> None:
    """Display the top bar of the game."""
    cprint(header)
    if account:
        header_lines = header.splitlines()
        header_width = max(len(line) for line in header_lines if line.strip())

        left_text = f"👤 {account.name}"
        right_text = f"💰 {account.balance}"

        # Space available for padding
        inner_width = header_width
        cprint(f"{left_text}{right_text.rjust(inner_width - len(left_text))}")
    # Add margin after
    print("\n" * margin, end="")
