from dataclasses import dataclass

from .accounts import Account
from .config import Config
from typing import Tuple
from .cards import *

Card = Tuple[int | str, str]


@dataclass
class GameContext:
    account: Account
    config: Config
