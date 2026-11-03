"""Compatibility exports for the European roulette variant."""

from .base import Roulette
from .variants.european import EuropeanRoulette, play_european_roulette

__all__ = ["Roulette", "EuropeanRoulette", "play_european_roulette"]
