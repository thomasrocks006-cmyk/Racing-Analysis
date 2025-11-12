"""
Betting Strategies

Implementation of various betting strategies for racing:
- Fixed stake
- Proportional (percentage of bankroll)
- Kelly Criterion (optimal growth)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class BettingStrategy(ABC):
    """
    Abstract base class for betting strategies.

    All strategies must implement calculate_stakes method.
    """

    @abstractmethod
    def calculate_stakes(
        self,
        probabilities: np.ndarray,
        odds: np.ndarray,
        bankroll: float
    ) -> np.ndarray:
        """
        Calculate stake amounts for each bet.

        Args:
            probabilities: Predicted win probabilities
            odds: Bookmaker odds
            bankroll: Current bankroll

        Returns:
            Array of stake amounts
        """
        pass


class FixedStake(BettingStrategy):
    """
    Fixed stake betting strategy.

    Bets the same amount on every selection.
    """

    def __init__(self, stake_amount: float = 10.0, min_edge: float = 0.0):
        """
        Initialize fixed stake strategy.

        Args:
            stake_amount: Fixed amount to bet per selection
            min_edge: Minimum edge required to place bet (e.g., 0.05 = 5%)
        """
        self.stake_amount = stake_amount
        self.min_edge = min_edge

    def calculate_stakes(
        self,
        probabilities: np.ndarray,
        odds: np.ndarray,
        bankroll: float
    ) -> np.ndarray:
        """Calculate fixed stakes."""
        # Calculate edge: expected value - 1
        expected_values = probabilities * odds
        edges = expected_values - 1

        # Only bet where edge meets threshold
        stakes = np.where(edges >= self.min_edge, self.stake_amount, 0.0)

        return stakes


class ProportionalStake(BettingStrategy):
    """
    Proportional (percentage) betting strategy.

    Bets a fixed percentage of current bankroll.
    """

    def __init__(self, percentage: float = 0.02, min_edge: float = 0.0):
        """
        Initialize proportional stake strategy.

        Args:
            percentage: Percentage of bankroll to bet (e.g., 0.02 = 2%)
            min_edge: Minimum edge required to place bet
        """
        if not 0 < percentage <= 1:
            raise ValueError("percentage must be between 0 and 1")

        self.percentage = percentage
        self.min_edge = min_edge

    def calculate_stakes(
        self,
        probabilities: np.ndarray,
        odds: np.ndarray,
        bankroll: float
    ) -> np.ndarray:
        """Calculate proportional stakes."""
        # Calculate edge
        expected_values = probabilities * odds
        edges = expected_values - 1

        # Only bet where edge meets threshold
        stake_per_bet = bankroll * self.percentage
        stakes = np.where(edges >= self.min_edge, stake_per_bet, 0.0)

        return stakes


class KellyCriterion(BettingStrategy):
    """
    Kelly Criterion betting strategy.

    Optimal bet sizing for logarithmic utility maximization.
    Formula: f* = (bp - q) / b
    where:
        f* = fraction of bankroll to bet
        b = odds - 1 (net odds)
        p = probability of winning
        q = 1 - p (probability of losing)
    """

    def __init__(
        self,
        fraction: float = 1.0,
        min_edge: float = 0.0,
        max_stake_pct: float = 0.25
    ):
        """
        Initialize Kelly Criterion strategy.

        Args:
            fraction: Kelly fraction (e.g., 0.5 = half Kelly for safety)
            min_edge: Minimum edge required to place bet
            max_stake_pct: Maximum stake as percentage of bankroll
        """
        if fraction <= 0:
            raise ValueError("fraction must be positive")

        self.fraction = fraction
        self.min_edge = min_edge
        self.max_stake_pct = max_stake_pct

    def calculate_stakes(
        self,
        probabilities: np.ndarray,
        odds: np.ndarray,
        bankroll: float
    ) -> np.ndarray:
        """Calculate Kelly stakes."""
        # Net odds (what you win per unit)
        b = odds - 1

        # Win/loss probabilities
        p = probabilities
        q = 1 - p

        # Kelly formula: (bp - q) / b
        kelly_fractions = (b * p - q) / b

        # Apply Kelly fraction modifier (e.g., half Kelly)
        kelly_fractions = kelly_fractions * self.fraction

        # Calculate edge for filtering
        expected_values = probabilities * odds
        edges = expected_values - 1

        # Only bet where:
        # 1. Edge meets threshold
        # 2. Kelly fraction is positive
        # 3. Odds are valid (> 1)
        valid_mask = (edges >= self.min_edge) & (kelly_fractions > 0) & (b > 0)

        # Calculate stakes
        stakes = np.where(
            valid_mask,
            np.minimum(kelly_fractions * bankroll, self.max_stake_pct * bankroll),
            0.0
        )

        return stakes


class ValueBetting(BettingStrategy):
    """
    Value betting strategy.

    Only bets when the model's probability exceeds the implied probability
    from the odds by a minimum threshold.
    """

    def __init__(
        self,
        stake_calculator: BettingStrategy,
        min_value_threshold: float = 0.1
    ):
        """
        Initialize value betting strategy.

        Args:
            stake_calculator: Underlying strategy to calculate stakes (Kelly, Fixed, etc.)
            min_value_threshold: Minimum value ratio (model_prob / implied_prob - 1)
        """
        self.stake_calculator = stake_calculator
        self.min_value_threshold = min_value_threshold

    def calculate_stakes(
        self,
        probabilities: np.ndarray,
        odds: np.ndarray,
        bankroll: float
    ) -> np.ndarray:
        """Calculate value-based stakes."""
        # Implied probability from odds
        implied_probs = 1.0 / odds

        # Value ratio: how much better is our probability vs market
        value_ratios = probabilities / implied_probs - 1

        # Only bet where value threshold is met
        value_mask = value_ratios >= self.min_value_threshold

        # Calculate stakes using underlying strategy
        stakes = self.stake_calculator.calculate_stakes(probabilities, odds, bankroll)

        # Apply value filter
        stakes = np.where(value_mask, stakes, 0.0)

        return stakes
