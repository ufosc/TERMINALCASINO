from dataclasses import dataclass

from .accounts import Account
from .config import Config
from typing import Tuple
# from .cards import Card

# Card = tuple[int | str, str]


@dataclass
class GameContext:
    account: Account
    config: Config
    # below added for 2nd player functionality in blackjack
    alt_player: Account | None = None