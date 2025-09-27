from dataclasses import dataclass

from .accounts import Account
from .config import Config

type Card = tuple[int | str, str]


@dataclass
class GameContext:
    account: Account
    config: Config
