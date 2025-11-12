"""
Backtesting Framework

Walk-forward validation for racing prediction models with realistic betting simulation.
"""

from __future__ import annotations

from typing import Union

import numpy as np
import pandas as pd

from .metrics import BacktestMetrics
from .strategies import BettingStrategy


class Backtester:
    """
    Walk-forward backtesting framework.

    Simulates realistic betting with:
    - Walk-forward validation (expanding or rolling window)
    - Multiple betting strategies
    - Commission/takeout modeling
    - Comprehensive performance metrics
    """

    def __init__(
        self,
        strategy: BettingStrategy,
        min_train_size: int = 1000,
        test_size: int = 200,
        window_type: str = "expanding",
        commission: float = 0.0,
        min_odds: float = 1.01,
        max_odds: float = 100.0,
    ):
        """
        Initialize backtester.

        Args:
            strategy: Betting strategy to evaluate
            min_train_size: Minimum training samples for first fold
            test_size: Number of samples per test fold
            window_type: 'expanding' (growing) or 'rolling' (fixed size)
            commission: Commission/takeout rate (e.g., 0.15 for 15%)
            min_odds: Minimum acceptable odds
            max_odds: Maximum acceptable odds
        """
        self.strategy = strategy
        self.min_train_size = min_train_size
        self.test_size = test_size
        self.window_type = window_type
        self.commission = commission
        self.min_odds = min_odds
        self.max_odds = max_odds

        self.results_: Union[pd.DataFrame, None] = None
        self.metrics_: Union[BacktestMetrics, None] = None

    def _create_folds(self, n_samples: int) -> list[tuple[np.ndarray, np.ndarray]]:
        """
        Create walk-forward validation folds.

        Args:
            n_samples: Total number of samples

        Returns:
            List of (train_indices, test_indices) tuples
        """
        if n_samples < self.min_train_size + self.test_size:
            raise ValueError(
                f"Not enough samples ({n_samples}) for min_train_size "
                f"({self.min_train_size}) + test_size ({self.test_size})"
            )

        folds = []
        current_train_end = self.min_train_size

        while current_train_end + self.test_size <= n_samples:
            if self.window_type == "expanding":
                train_idx = np.arange(0, current_train_end)
            else:  # rolling
                train_start = max(0, current_train_end - self.min_train_size)
                train_idx = np.arange(train_start, current_train_end)

            test_idx = np.arange(current_train_end, current_train_end + self.test_size)
            folds.append((train_idx, test_idx))

            current_train_end += self.test_size

        return folds

    def run(
        self,
        model,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        odds: Union[np.ndarray, pd.Series],
        race_ids: Union[np.ndarray, pd.Series, None] = None,
        dates: Union[np.ndarray, pd.Series, None] = None,
        initial_bankroll: float = 1000.0,
        verbose: bool = True,
    ) -> pd.DataFrame:
        """
        Run walk-forward backtesting.

        Args:
            model: Scikit-learn compatible model with fit/predict_proba
            X: Feature matrix
            y: True labels (1 = win, 0 = loss)
            odds: Bookmaker odds for each runner
            race_ids: Race identifier for each sample
            dates: Date for each sample
            initial_bankroll: Starting bankroll
            verbose: Whether to print progress

        Returns:
            DataFrame with bet-level results
        """
        # Convert to numpy arrays
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values
        if isinstance(odds, pd.Series):
            odds = odds.values

        # Create folds
        folds = self._create_folds(len(X))

        if verbose:
            print(f"Running {self.window_type} walk-forward validation")
            print(
                f"Folds: {len(folds)}, Min train: {self.min_train_size}, Test: {self.test_size}"
            )

        # Track results
        all_results = []
        current_bankroll = initial_bankroll

        for fold_idx, (train_idx, test_idx) in enumerate(folds):
            if verbose:
                print(f"\nFold {fold_idx + 1}/{len(folds)}")
                print(
                    f"  Train: {len(train_idx)} samples, Test: {len(test_idx)} samples"
                )

            # Train model
            X_train, y_train = X[train_idx], y[train_idx]
            X_test, y_test = X[test_idx], y[test_idx]

            model.fit(X_train, y_train)

            # Get predictions
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X_test)[:, 1]
            else:
                probs = model.predict(X_test)

            # Get test odds
            test_odds = odds[test_idx]

            # Filter by odds range
            valid_mask = (test_odds >= self.min_odds) & (test_odds <= self.max_odds)

            # Calculate stakes for each bet
            stakes = self.strategy.calculate_stakes(
                probabilities=probs[valid_mask],
                odds=test_odds[valid_mask],
                bankroll=current_bankroll,
            )

            # Simulate bets
            for i, (prob, odd, stake) in enumerate(
                zip(probs[valid_mask], test_odds[valid_mask], stakes)
            ):
                original_idx = test_idx[np.where(valid_mask)[0][i]]
                outcome = y_test[np.where(valid_mask)[0][i]]

                # Calculate returns
                if outcome == 1:  # Win
                    gross_return = stake * odd
                    net_return = gross_return * (1 - self.commission)
                    profit = net_return - stake
                else:  # Loss
                    profit = -stake

                current_bankroll += profit

                # Store result
                result = {
                    "fold": fold_idx,
                    "sample_idx": original_idx,
                    "predicted_prob": prob,
                    "odds": odd,
                    "stake": stake,
                    "outcome": outcome,
                    "profit": profit,
                    "bankroll": current_bankroll,
                }

                if race_ids is not None:
                    result["race_id"] = race_ids[original_idx]
                if dates is not None:
                    result["date"] = dates[original_idx]

                all_results.append(result)

            if verbose:
                fold_profit = sum(
                    r["profit"] for r in all_results if r["fold"] == fold_idx
                )
                print(
                    f"  Fold profit: ${fold_profit:.2f}, Bankroll: ${current_bankroll:.2f}"
                )

        # Convert to DataFrame
        self.results_ = pd.DataFrame(all_results)

        # Calculate metrics
        self.metrics_ = BacktestMetrics(self.results_, initial_bankroll)

        if verbose:
            print("\n" + "=" * 60)
            print("BACKTEST SUMMARY")
            print("=" * 60)
            summary = self.metrics_.get_summary()
            for key, value in summary.items():
                if isinstance(value, float):
                    print(f"{key}: {value:.4f}")
                else:
                    print(f"{key}: {value}")

        return self.results_

    def get_results(self) -> pd.DataFrame:
        """Get detailed bet-level results."""
        if self.results_ is None:
            raise ValueError("Must run backtest first")
        return self.results_

    def get_metrics(self) -> BacktestMetrics:
        """Get performance metrics."""
        if self.metrics_ is None:
            raise ValueError("Must run backtest first")
        return self.metrics_

    def plot_equity_curve(self, **kwargs):
        """Plot bankroll over time."""
        if self.metrics_ is None:
            raise ValueError("Must run backtest first")
        return self.metrics_.plot_equity_curve(**kwargs)

    def plot_profit_curve(self, **kwargs):
        """Plot cumulative profit over time."""
        if self.metrics_ is None:
            raise ValueError("Must run backtest first")
        return self.metrics_.plot_profit_curve(**kwargs)

    def plot_rolling_roi(self, window: int = 100, **kwargs):
        """Plot rolling ROI over time."""
        if self.metrics_ is None:
            raise ValueError("Must run backtest first")
        return self.metrics_.plot_rolling_roi(window=window, **kwargs)
