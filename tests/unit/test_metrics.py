"""Tests for metrics calculations"""

import numpy as np
import pytest
from src.utils.metrics import (
    calculate_brier_score,
    calculate_auc,
    calculate_calibration_error,
    calculate_roi,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
)


def test_brier_score(sample_predictions):
    """Test Brier score calculation"""
    y_true = sample_predictions["y_true"]
    y_prob = sample_predictions["y_prob"]
    
    brier = calculate_brier_score(y_true, y_prob)
    
    assert 0 <= brier <= 1
    assert isinstance(brier, float)


def test_auc(sample_predictions):
    """Test AUC calculation"""
    y_true = sample_predictions["y_true"]
    y_prob = sample_predictions["y_prob"]
    
    auc = calculate_auc(y_true, y_prob)
    
    assert 0 <= auc <= 1
    assert isinstance(auc, float)


def test_calibration_error(sample_predictions):
    """Test calibration error calculation"""
    y_true = sample_predictions["y_true"]
    y_prob = sample_predictions["y_prob"]
    
    ece, frac_pos, mean_pred = calculate_calibration_error(y_true, y_prob, n_bins=5)
    
    assert 0 <= ece <= 1
    assert isinstance(ece, float)
    assert len(frac_pos) <= 5
    assert len(mean_pred) <= 5


def test_roi_calculation():
    """Test ROI calculation"""
    stakes = np.array([10, 10, 10, 10, 10])
    returns = np.array([20, 0, 15, 0, 30])  # 3 wins, 2 losses
    
    roi_metrics = calculate_roi(stakes, returns, commission_rate=0.05)
    
    assert "roi_percent" in roi_metrics
    assert "net_profit" in roi_metrics
    assert "win_rate_percent" in roi_metrics
    assert roi_metrics["num_bets"] == 5
    assert roi_metrics["num_wins"] == 3


def test_sharpe_ratio():
    """Test Sharpe ratio calculation"""
    returns = np.array([0.01, 0.02, -0.01, 0.03, 0.00, 0.02])
    
    sharpe = calculate_sharpe_ratio(returns)
    
    assert isinstance(sharpe, float)


def test_max_drawdown():
    """Test maximum drawdown calculation"""
    equity_curve = np.array([100, 110, 105, 120, 115, 90, 100])
    
    dd_metrics = calculate_max_drawdown(equity_curve)
    
    assert "max_drawdown" in dd_metrics
    assert "max_drawdown_percent" in dd_metrics
    assert dd_metrics["max_drawdown"] >= 0
    assert dd_metrics["peak_value"] >= dd_metrics["trough_value"]


def test_max_drawdown_no_drawdown():
    """Test max drawdown with no losses"""
    equity_curve = np.array([100, 110, 120, 130])
    
    dd_metrics = calculate_max_drawdown(equity_curve)
    
    assert dd_metrics["max_drawdown"] == 0
