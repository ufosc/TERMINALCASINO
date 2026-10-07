"""Saves alternate players' chip balances so they carry over between games."""

import json
from pathlib import Path

SAVE_FILE = Path.home() / ".terminal_casino" / "players.json"


def load_balances() -> dict[str, int]:
    """Return saved balances as {name: balance}. Empty if there is no save yet."""
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return {name: int(balance) for name, balance in json.load(f).items()}
    except (OSError, ValueError, AttributeError):
        return {}


def save_balances(accounts) -> None:
    """Save each account's balance under its name, keeping other saved players."""
    balances = load_balances()
    for account in accounts:
        balances[account.name.lower()] = account.balance
    SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(balances, f, indent=2)
