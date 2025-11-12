"""
Tests for Week 7-8: Hyperparameter Optimization and Backtesting

Comprehensive tests for:
- Optuna hyperparameter tuning
- Betting strategies
- Backtesting framework
- Performance metrics
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

from src.backtesting.backtester import Backtester
from src.backtesting.metrics import BacktestMetrics
from src.backtesting.strategies import (
    FixedStake,
    KellyCriterion,
    ProportionalStake,
    ValueBetting,
)
from src.optimization.hyperparameter_tuner import HyperparameterTuner


class TestHyperparameterOptimization:
    """Test Optuna-based hyperparameter optimization."""

    @pytest.fixture
    def sample_data(self):
        """Generate sample classification data."""
        X, y = make_classification(
            n_samples=500,
            n_features=10,
            n_informative=5,
            n_redundant=2,
            random_state=42
        )
        return X, y

    def test_lightgbm_optimization(self, sample_data):
        """Test LightGBM hyperparameter tuning."""
        X, y = sample_data

        tuner = HyperparameterTuner(
            model_type='lightgbm',
            n_trials=5,  # Small number for testing
            cv_folds=3,
            random_state=42
        )

        best_params = tuner.optimize(X, y, verbose=False)

        assert best_params is not None
        assert 'learning_rate' in best_params
        assert 'n_estimators' in best_params
        assert tuner.best_score is not None
        assert tuner.study is not None

    def test_xgboost_optimization(self, sample_data):
        """Test XGBoost hyperparameter tuning."""
        X, y = sample_data

        tuner = HyperparameterTuner(
            model_type='xgboost',
            n_trials=5,
            cv_folds=3,
            random_state=42
        )

        best_params = tuner.optimize(X, y, verbose=False)

        assert best_params is not None
        assert 'learning_rate' in best_params
        assert 'n_estimators' in best_params

    def test_catboost_optimization(self, sample_data):
        """Test CatBoost hyperparameter tuning."""
        X, y = sample_data

        tuner = HyperparameterTuner(
            model_type='catboost',
            n_trials=5,
            cv_folds=3,
            random_state=42
        )

        best_params = tuner.optimize(X, y, verbose=False)

        assert best_params is not None
        assert 'learning_rate' in best_params
        assert 'iterations' in best_params

    def test_get_best_model(self, sample_data):
        """Test getting model with best parameters."""
        X, y = sample_data

        tuner = HyperparameterTuner(
            model_type='lightgbm',
            n_trials=3,
            cv_folds=2,
            random_state=42
        )

        tuner.optimize(X, y, verbose=False)
        model = tuner.get_best_model()

        assert model is not None
        model.fit(X, y)
        predictions = model.predict(X)
        assert len(predictions) == len(y)

    def test_optimization_summary(self, sample_data):
        """Test optimization summary generation."""
        X, y = sample_data

        tuner = HyperparameterTuner(
            model_type='lightgbm',
            n_trials=3,
            random_state=42
        )

        tuner.optimize(X, y, verbose=False)
        summary = tuner.get_optimization_summary()

        assert 'best_score' in summary
        assert 'best_params' in summary
        assert 'n_trials' in summary
        assert summary['n_trials'] == 3


class TestBettingStrategies:
    """Test betting strategy implementations."""

    @pytest.fixture
    def sample_bets(self):
        """Generate sample betting scenarios."""
        probs = np.array([0.25, 0.40, 0.15, 0.30])
        odds = np.array([5.0, 3.0, 8.0, 4.0])
        bankroll = 1000.0
        return probs, odds, bankroll

    def test_fixed_stake(self, sample_bets):
        """Test fixed stake strategy."""
        probs, odds, bankroll = sample_bets

        strategy = FixedStake(stake_amount=10.0, min_edge=0.0)
        stakes = strategy.calculate_stakes(probs, odds, bankroll)

        assert len(stakes) == len(probs)
        assert all(stakes >= 0)

        # All bets with positive edge should have fixed stake
        expected_values = probs * odds
        positive_edge = expected_values > 1.0
        assert all(stakes[positive_edge] == 10.0)

    def test_proportional_stake(self, sample_bets):
        """Test proportional stake strategy."""
        probs, odds, bankroll = sample_bets

        strategy = ProportionalStake(percentage=0.02, min_edge=0.0)
        stakes = strategy.calculate_stakes(probs, odds, bankroll)

        assert len(stakes) == len(probs)
        assert all(stakes >= 0)

        # Stakes should be 2% of bankroll where edge is positive
        expected_values = probs * odds
        positive_edge = expected_values > 1.0
        expected_stake = bankroll * 0.02
        assert all(stakes[positive_edge] == expected_stake)

    def test_kelly_criterion(self, sample_bets):
        """Test Kelly criterion strategy."""
        probs, odds, bankroll = sample_bets

        strategy = KellyCriterion(fraction=1.0, min_edge=0.0)
        stakes = strategy.calculate_stakes(probs, odds, bankroll)

        assert len(stakes) == len(probs)
        assert all(stakes >= 0)

        # Kelly stakes should be positive for positive edge bets
        expected_values = probs * odds
        positive_edge = expected_values > 1.0
        assert all(stakes[positive_edge] > 0)

    def test_kelly_half_fraction(self, sample_bets):
        """Test half-Kelly for conservative betting."""
        probs, odds, bankroll = sample_bets

        full_kelly = KellyCriterion(fraction=1.0)
        half_kelly = KellyCriterion(fraction=0.5)

        full_stakes = full_kelly.calculate_stakes(probs, odds, bankroll)
        half_stakes = half_kelly.calculate_stakes(probs, odds, bankroll)

        # Half-Kelly should stake approximately half of full Kelly
        np.testing.assert_array_almost_equal(half_stakes, full_stakes * 0.5)

    def test_value_betting(self, sample_bets):
        """Test value betting filter."""
        probs, odds, bankroll = sample_bets

        base_strategy = FixedStake(stake_amount=10.0)
        value_strategy = ValueBetting(
            stake_calculator=base_strategy,
            min_value_threshold=0.2  # 20% value required
        )

        stakes = value_strategy.calculate_stakes(probs, odds, bankroll)

        # Only high-value bets should be placed
        implied_probs = 1.0 / odds
        value_ratios = probs / implied_probs - 1
        high_value = value_ratios >= 0.2

        assert all(stakes[high_value] > 0)
        assert all(stakes[~high_value] == 0)


class TestBacktesting:
    """Test backtesting framework."""

    @pytest.fixture
    def backtest_data(self):
        """Generate sample backtesting data."""
        np.random.seed(42)

        n_samples = 500
        X, y = make_classification(
            n_samples=n_samples,
            n_features=10,
            n_informative=5,
            random_state=42
        )

        # Generate realistic odds (inversely related to win probability)
        base_probs = np.random.beta(2, 5, n_samples)  # Skewed toward favorites
        odds = 1.0 / base_probs * 0.85  # Include overround
        odds = np.clip(odds, 1.5, 50.0)

        return X, y, odds

    def test_fixed_stake_backtest(self, backtest_data):
        """Test backtesting with fixed stake strategy."""
        X, y, odds = backtest_data

        strategy = FixedStake(stake_amount=10.0, min_edge=0.05)
        backtester = Backtester(
            strategy=strategy,
            min_train_size=200,
            test_size=50,
            window_type='expanding'
        )

        model = RandomForestClassifier(n_estimators=50, random_state=42)
        results = backtester.run(
            model=model,
            X=X,
            y=y,
            odds=odds,
            initial_bankroll=1000.0,
            verbose=False
        )

        assert len(results) > 0
        assert 'stake' in results.columns
        assert 'profit' in results.columns
        assert 'bankroll' in results.columns
        assert all(results['stake'] >= 0)

    def test_kelly_backtest(self, backtest_data):
        """Test backtesting with Kelly criterion."""
        X, y, odds = backtest_data

        strategy = KellyCriterion(fraction=0.25, min_edge=0.05)
        backtester = Backtester(
            strategy=strategy,
            min_train_size=200,
            test_size=50
        )

        model = RandomForestClassifier(n_estimators=50, random_state=42)
        results = backtester.run(
            model=model,
            X=X,
            y=y,
            odds=odds,
            initial_bankroll=1000.0,
            verbose=False
        )

        assert len(results) > 0
        # Kelly stakes should vary based on edge
        assert results['stake'].std() > 0

    def test_walk_forward_folds(self, backtest_data):
        """Test walk-forward fold creation."""
        X, y, odds = backtest_data

        strategy = FixedStake(stake_amount=10.0)
        backtester = Backtester(
            strategy=strategy,
            min_train_size=200,
            test_size=50
        )

        folds = backtester._create_folds(len(X))

        assert len(folds) > 0

        # Check fold structure
        for train_idx, test_idx in folds:
            assert len(train_idx) >= 200
            assert len(test_idx) == 50
            assert max(train_idx) < min(test_idx)  # No overlap

    def test_rolling_window(self, backtest_data):
        """Test rolling window backtesting."""
        X, y, odds = backtest_data

        strategy = FixedStake(stake_amount=10.0)
        backtester = Backtester(
            strategy=strategy,
            min_train_size=200,
            test_size=50,
            window_type='rolling'
        )

        model = RandomForestClassifier(n_estimators=50, random_state=42)
        results = backtester.run(
            model=model,
            X=X,
            y=y,
            odds=odds,
            initial_bankroll=1000.0,
            verbose=False
        )

        assert len(results) > 0


class TestBacktestMetrics:
    """Test performance metrics calculation."""

    @pytest.fixture
    def sample_results(self):
        """Generate sample backtest results."""
        results = pd.DataFrame({
            'stake': [10, 10, 10, 10, 10] * 10,
            'profit': [5, -10, 15, -10, 8] * 10,
            'outcome': [1, 0, 1, 0, 1] * 10,
            'odds': [2.5, 3.0, 4.0, 2.0, 3.5] * 10,
            'bankroll': np.cumsum([5, -10, 15, -10, 8] * 10) + 1000
        })
        return results

    def test_roi_calculation(self, sample_results):
        """Test ROI calculation."""
        metrics = BacktestMetrics(sample_results, initial_bankroll=1000.0)
        roi = metrics.roi()

        total_staked = sample_results['stake'].sum()
        total_profit = sample_results['profit'].sum()
        expected_roi = total_profit / total_staked

        assert roi == expected_roi

    def test_win_rate(self, sample_results):
        """Test win rate calculation."""
        metrics = BacktestMetrics(sample_results, initial_bankroll=1000.0)
        win_rate = metrics.win_rate()

        expected_win_rate = (sample_results['outcome'] == 1).sum() / len(sample_results)
        assert win_rate == expected_win_rate

    def test_sharpe_ratio(self, sample_results):
        """Test Sharpe ratio calculation."""
        metrics = BacktestMetrics(sample_results, initial_bankroll=1000.0)
        sharpe = metrics.sharpe_ratio()

        assert isinstance(sharpe, float)
        assert not np.isnan(sharpe)

    def test_max_drawdown(self, sample_results):
        """Test maximum drawdown calculation."""
        metrics = BacktestMetrics(sample_results, initial_bankroll=1000.0)
        dd = metrics.max_drawdown()

        assert 'max_drawdown' in dd
        assert 'max_drawdown_pct' in dd
        assert dd['max_drawdown'] <= 0  # Drawdown is negative

    def test_profit_factor(self, sample_results):
        """Test profit factor calculation."""
        metrics = BacktestMetrics(sample_results, initial_bankroll=1000.0)
        pf = metrics.profit_factor()

        wins = sample_results[sample_results['profit'] > 0]['profit'].sum()
        losses = abs(sample_results[sample_results['profit'] < 0]['profit'].sum())
        expected_pf = wins / losses if losses > 0 else float('inf')

        assert pf == expected_pf

    def test_expectancy(self, sample_results):
        """Test expectancy calculation."""
        metrics = BacktestMetrics(sample_results, initial_bankroll=1000.0)
        expectancy = metrics.expectancy()

        expected_expectancy = sample_results['profit'].mean()
        assert expectancy == expected_expectancy

    def test_summary(self, sample_results):
        """Test comprehensive metrics summary."""
        metrics = BacktestMetrics(sample_results, initial_bankroll=1000.0)
        summary = metrics.get_summary()

        required_keys = [
            'total_bets', 'total_profit', 'roi', 'win_rate',
            'sharpe_ratio', 'max_drawdown', 'profit_factor',
            'expectancy', 'final_bankroll'
        ]

        for key in required_keys:
            assert key in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
