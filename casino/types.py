from dataclasses import dataclass
from .accounts import Account

type Card = tuple[int | str, str]

@dataclass
class GameContext:
    account: Account
