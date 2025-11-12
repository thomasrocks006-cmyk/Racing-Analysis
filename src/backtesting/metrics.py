"""
Backtesting Performance Metrics

Comprehensive metrics for evaluating betting strategy performance:
- ROI (Return on Investment)
- Profit/Loss curves
- Sharpe ratio
- Maximum drawdown
- Win rate and average odds
"""

from __future__ import annotations

from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class BacktestMetrics:
    """
    Calculate and visualize backtesting performance metrics.
    """

    def __init__(self, results: pd.DataFrame, initial_bankroll: float):
        """
        Initialize metrics calculator.

        Args:
            results: DataFrame with bet-level results from Backtester
            initial_bankroll: Starting bankroll amount
        """
        self.results = results
        self.initial_bankroll = initial_bankroll

    def roi(self) -> float:
        """
        Calculate Return on Investment.

        Returns:
            ROI as decimal (e.g., 0.15 = 15%)
        """
        total_staked = self.results["stake"].sum()

        if total_staked == 0:
            return 0.0

        total_profit = self.results["profit"].sum()
        return total_profit / total_staked

    def total_profit(self) -> float:
        """Calculate total profit/loss."""
        return self.results["profit"].sum()

    def final_bankroll(self) -> float:
        """Get final bankroll value."""
        return (
            self.results["bankroll"].iloc[-1]
            if len(self.results) > 0
            else self.initial_bankroll
        )

    def total_bets(self) -> int:
        """Count total number of bets placed."""
        return len(self.results)

    def win_rate(self) -> float:
        """
        Calculate win rate (percentage of winning bets).

        Returns:
            Win rate as decimal (e.g., 0.25 = 25%)
        """
        if len(self.results) == 0:
            return 0.0

        wins = (self.results["outcome"] == 1).sum()
        return wins / len(self.results)

    def average_odds(self) -> float:
        """Calculate average odds of bets placed."""
        return self.results["odds"].mean() if len(self.results) > 0 else 0.0

    def average_stake(self) -> float:
        """Calculate average stake size."""
        return self.results["stake"].mean() if len(self.results) > 0 else 0.0

    def sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio (risk-adjusted returns).

        Args:
            risk_free_rate: Risk-free rate of return

        Returns:
            Sharpe ratio
        """
        if len(self.results) == 0:
            return 0.0

        # Calculate returns per bet as percentage of stake
        returns = self.results["profit"] / self.results["stake"]

        mean_return = returns.mean()
        std_return = returns.std()

        if std_return == 0:
            return 0.0

        return (mean_return - risk_free_rate) / std_return

    def max_drawdown(self) -> dict[str, float]:
        """
        Calculate maximum drawdown.

        Returns:
            Dictionary with max_drawdown (absolute) and max_drawdown_pct
        """
        if len(self.results) == 0:
            return {"max_drawdown": 0.0, "max_drawdown_pct": 0.0}

        # Calculate running maximum
        bankroll = self.results["bankroll"].values
        running_max = np.maximum.accumulate(bankroll)

        # Drawdown = current value - running max
        drawdown = bankroll - running_max

        max_dd = drawdown.min()  # Most negative value
        max_dd_pct = (
            max_dd / running_max[np.argmin(drawdown)]
            if running_max[np.argmin(drawdown)] > 0
            else 0.0
        )

        return {"max_drawdown": max_dd, "max_drawdown_pct": max_dd_pct}

    def profit_factor(self) -> float:
        """
        Calculate profit factor (gross wins / gross losses).

        Returns:
            Profit factor (> 1 = profitable)
        """
        wins = self.results[self.results["profit"] > 0]["profit"].sum()
        losses = abs(self.results[self.results["profit"] < 0]["profit"].sum())

        if losses == 0:
            return float("inf") if wins > 0 else 0.0

        return wins / losses

    def expectancy(self) -> float:
        """
        Calculate expectancy (average profit per bet).

        Returns:
            Average profit per bet
        """
        return self.results["profit"].mean() if len(self.results) > 0 else 0.0

    def get_summary(self) -> dict[str, Union[float, int]]:
        """
        Get comprehensive summary of all metrics.

        Returns:
            Dictionary with all performance metrics
        """
        dd = self.max_drawdown()

        return {
            "total_bets": self.total_bets(),
            "total_profit": self.total_profit(),
            "roi": self.roi(),
            "win_rate": self.win_rate(),
            "average_odds": self.average_odds(),
            "average_stake": self.average_stake(),
            "sharpe_ratio": self.sharpe_ratio(),
            "max_drawdown": dd["max_drawdown"],
            "max_drawdown_pct": dd["max_drawdown_pct"],
            "profit_factor": self.profit_factor(),
            "expectancy": self.expectancy(),
            "initial_bankroll": self.initial_bankroll,
            "final_bankroll": self.final_bankroll(),
        }

    def plot_equity_curve(self, figsize: tuple[int, int] = (12, 6), **kwargs):
        """
        Plot bankroll over time.

        Args:
            figsize: Figure size
            **kwargs: Additional matplotlib arguments

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        ax.plot(self.results.index, self.results["bankroll"], **kwargs)
        ax.axhline(
            y=self.initial_bankroll,
            color="r",
            linestyle="--",
            alpha=0.5,
            label="Initial Bankroll",
        )

        ax.set_xlabel("Bet Number")
        ax.set_ylabel("Bankroll ($)")
        ax.set_title("Equity Curve")
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig

    def plot_profit_curve(self, figsize: tuple[int, int] = (12, 6), **kwargs):
        """
        Plot cumulative profit over time.

        Args:
            figsize: Figure size
            **kwargs: Additional matplotlib arguments

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        cumulative_profit = self.results["profit"].cumsum()
        ax.plot(self.results.index, cumulative_profit, **kwargs)
        ax.axhline(y=0, color="r", linestyle="--", alpha=0.5, label="Break Even")

        ax.set_xlabel("Bet Number")
        ax.set_ylabel("Cumulative Profit ($)")
        ax.set_title("Profit Curve")
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig

    def plot_rolling_roi(
        self, window: int = 100, figsize: tuple[int, int] = (12, 6), **kwargs
    ):
        """
        Plot rolling ROI over time.

        Args:
            window: Rolling window size
            figsize: Figure size
            **kwargs: Additional matplotlib arguments

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        rolling_profit = self.results["profit"].rolling(window=window).sum()
        rolling_stake = self.results["stake"].rolling(window=window).sum()
        rolling_roi = rolling_profit / rolling_stake

        ax.plot(
            self.results.index, rolling_roi * 100, **kwargs
        )  # Convert to percentage
        ax.axhline(y=0, color="r", linestyle="--", alpha=0.5, label="Break Even")

        ax.set_xlabel("Bet Number")
        ax.set_ylabel(f"Rolling ROI (%, {window} bets)")
        ax.set_title(f"Rolling ROI ({window} bet window)")
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig

    def plot_drawdown(self, figsize: tuple[int, int] = (12, 6), **kwargs):
        """
        Plot drawdown over time.

        Args:
            figsize: Figure size
            **kwargs: Additional matplotlib arguments

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        bankroll = self.results["bankroll"].values
        running_max = np.maximum.accumulate(bankroll)
        drawdown = bankroll - running_max

        ax.fill_between(self.results.index, drawdown, 0, alpha=0.3, **kwargs)
        ax.plot(self.results.index, drawdown, **kwargs)

        ax.set_xlabel("Bet Number")
        ax.set_ylabel("Drawdown ($)")
        ax.set_title("Drawdown Over Time")
        ax.grid(True, alpha=0.3)

        return fig
