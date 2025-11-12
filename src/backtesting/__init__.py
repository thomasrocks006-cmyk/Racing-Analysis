"""
Backtesting Module

Provides historical performance evaluation and betting strategy simulation.
"""

from .backtester import Backtester
from .metrics import BacktestMetrics
from .strategies import BettingStrategy, FixedStake, KellyCriterion, ProportionalStake

__all__ = [
    "Backtester",
    "BacktestMetrics",
    "BettingStrategy",
    "FixedStake",
    "ProportionalStake",
    "KellyCriterion",
]
