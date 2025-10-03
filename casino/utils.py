import os
import shutil
import json

from typing import Optional
from casino.accounts import Account
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
THEME_DIR = BASE_DIR / "themes"

#default fallback so theme is always defined
theme = {"color": "", "reset": ""}

# loads theme from json file
def load_theme(name: str) -> dict[str, str]:
    """Load a theme by name from themes folder"""
    theme_path = THEME_DIR / f"{name}.json"
    with open(theme_path, "r", encoding="utf-8") as f:
        return json.load(f)

# gets chosen theme
def get_theme():
    global theme
    cprint(f"Please choose a theme number below")
    choice = cinput(f"1.Black   2.Blue   3.Cyan")
    if choice == '1':
        cprint(f"Would you like the bright version?")
        choice_bright = cinput(f"[Y]es   [N]o")
        if choice_bright == 'Y' or choice_bright == 'y':
            theme = load_theme("bright_black_theme")
        else:
            theme = load_theme("black_theme")
    elif choice == '2':
        cprint(f"Would you like the bright version?")
        choice_bright = cinput(f"[Y]es   [N]o")
        if choice_bright == 'Y' or choice_bright == 'y':
            theme = load_theme("bright_blue_theme")
        else:
            theme = load_theme("blue_theme")
    else:
        # doesn't print because screen immediately cleared
        cprint(f"Invalid choice. Default theme chosen.")

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
        colored_line = f"{theme['color']}{line}{theme['reset']}"
        if i < len(lines) - 1:
            print(colored_line.center(terminal_width))
        else:
            print(colored_line.center(terminal_width), end=end)


def cinput(prompt: str = "") -> str:
    """Get input from the user in the center of the screen."""
    terminal_width = shutil.get_terminal_size().columns
    colored_prompt = f"{theme['color']}{prompt}{theme['reset']}"
    colored_center_prompt = colored_prompt.center(terminal_width)
    print(colored_center_prompt)

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
