"""Compatibility exports for American roulette."""

from .base import Roulette
from .variants.american import AmericanRoulette, play_roulette

__all__ = ["Roulette", "AmericanRoulette", "play_roulette"]
