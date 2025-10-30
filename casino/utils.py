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
def load_theme(folder: str, name: str) -> dict[str, str]:
    """Load a theme by name from a specific folder"""
    theme_path = THEME_DIR / folder / f"{name}.json"
    with open(theme_path, "r", encoding="utf-8") as f:
        return json.load(f)


# gets chosen theme
def get_theme():
    global theme
    
    # choose from original 16 terminal colors or custom colors
    cprint(f"Please choose a theme folder below, or press enter to use default")
    folder = cinput(f"1.Original Terminal   2.Custom Colors")

    # original 16
    if folder == '1':
        ansi_dir = THEME_DIR / "ansi"
        themes = [f.stem for f in ansi_dir.glob("*.json")]

        if not themes:
            cprint("No ANSI themes found.")
            return

        cprint("Please choose an ANSI theme:")
        for i, t_name in enumerate(themes, start=1):
            cprint(f"{i}. {t_name}")

        try:
            choice = int(cinput("Enter number: "))
            if 1 <= choice <= len(themes):
                theme = load_theme("ansi", themes[choice - 1])
                cprint(f"Loaded theme: {themes[choice - 1]}")
            else:
                cprint("Invalid choice. Default theme chosen.")
        except ValueError:
            cprint("Invalid input. Default theme chosen.")
    # custom user added colors
    elif folder == '2':
        custom_dir = THEME_DIR / "custom"
        themes = [f.stem for f in custom_dir.glob("*.json")]

        if not themes:
            cprint("No custom themes found.")
            return

        cprint("Please choose a custom theme:")
        for i, t_name in enumerate(themes, start=1):
            cprint(f"{i}. {t_name}")

        try:
            choice = int(cinput("Enter number: "))
            if 1 <= choice <= len(themes):
                theme = load_theme("custom", themes[choice - 1])
                cprint(f"Loaded theme: {themes[choice - 1]}")
            else:
                cprint("Invalid choice. Default theme chosen.")
        except ValueError:
            cprint("Invalid input. Default theme chosen.")
    # neither chosen, default used
    else:
        cprint("Invalid choice. Default theme chosen.")


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
        # center text then print colored
        line_center = line.center(terminal_width)
        colored_line = f"{theme['color']}{line_center}{theme['reset']}"
        if i < len(lines) - 1:
            print(colored_line)
        else:
            print(colored_line, end=end)


def cinput(prompt: str = "") -> str:
    """Get input from the user in the center of the screen."""
    terminal_width = shutil.get_terminal_size().columns
    # center text then print colored
    prompt_center = prompt.center(terminal_width)
    colored_prompt = f"{theme['color']}{prompt_center}{theme['reset']}"
    print(colored_prompt)

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
