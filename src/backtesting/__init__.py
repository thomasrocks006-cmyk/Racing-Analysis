"""
Backtesting Module

Provides historical performance evaluation and betting strategy simulation.
"""

from .backtester import Backtester
from .metrics import BacktestMetrics
from .strategies import BettingStrategy, FixedStake, ProportionalStake, KellyCriterion

__all__ = [
    'Backtester',
    'BacktestMetrics',
    'BettingStrategy',
    'FixedStake',
    'ProportionalStake',
    'KellyCriterion'
]
