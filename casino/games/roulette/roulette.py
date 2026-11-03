"""Compatibility exports for the standard roulette variant."""

from .base import Roulette
from .variants.standard import AmericanRoulette, play_roulette

__all__ = ["Roulette", "AmericanRoulette", "play_roulette"]
