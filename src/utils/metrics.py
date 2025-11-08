"""
Performance metrics calculation utilities.
Implements Brier score, AUC, calibration error, etc.
"""

import numpy as np
from typing import List, Tuple, Dict
from sklearn.metrics import brier_score_loss, roc_auc_score, log_loss
from sklearn.calibration import calibration_curve


def calculate_brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """
    Calculate Brier score (lower is better, 0 is perfect)
    
    Args:
        y_true: Binary outcomes (0 or 1)
        y_prob: Predicted probabilities
        
    Returns:
        Brier score
    """
    return brier_score_loss(y_true, y_prob)


def calculate_auc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """
    Calculate AUC-ROC (higher is better, 1 is perfect)
    
    Args:
        y_true: Binary outcomes (0 or 1)
        y_prob: Predicted probabilities
        
    Returns:
        AUC score
    """
    return roc_auc_score(y_true, y_prob)


def calculate_log_loss(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """
    Calculate log loss / cross-entropy (lower is better)
    
    Args:
        y_true: Binary outcomes (0 or 1)
        y_prob: Predicted probabilities
        
    Returns:
        Log loss
    """
    return log_loss(y_true, y_prob)


def calculate_calibration_error(
    y_true: np.ndarray, 
    y_prob: np.ndarray, 
    n_bins: int = 10
) -> Tuple[float, np.ndarray, np.ndarray]:
    """
    Calculate expected calibration error (ECE)
    
    Args:
        y_true: Binary outcomes (0 or 1)
        y_prob: Predicted probabilities
        n_bins: Number of bins for calibration curve
        
    Returns:
        Tuple of (ECE, fraction_of_positives, mean_predicted_value)
    """
    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_true, y_prob, n_bins=n_bins, strategy='uniform'
    )
    
    # Calculate ECE
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(y_prob, bin_edges[:-1]) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)
    
    ece = 0.0
    for i in range(n_bins):
        mask = bin_indices == i
        if mask.sum() > 0:
            bin_accuracy = y_true[mask].mean()
            bin_confidence = y_prob[mask].mean()
            bin_weight = mask.sum() / len(y_true)
            ece += bin_weight * abs(bin_accuracy - bin_confidence)
    
    return ece, fraction_of_positives, mean_predicted_value


def calculate_roi(
    stakes: np.ndarray,
    returns: np.ndarray,
    commission_rate: float = 0.05
) -> Dict[str, float]:
    """
    Calculate return on investment metrics
    
    Args:
        stakes: Array of stake amounts
        returns: Array of gross returns (before commission)
        commission_rate: Commission rate (default 5%)
        
    Returns:
        Dict with ROI, profit, turnover, etc.
    """
    total_staked = stakes.sum()
    gross_profit = returns.sum() - total_staked
    commission = np.maximum(returns - stakes, 0).sum() * commission_rate
    net_profit = gross_profit - commission
    roi = (net_profit / total_staked) * 100 if total_staked > 0 else 0
    
    # Win rate
    wins = (returns > stakes).sum()
    win_rate = (wins / len(stakes)) * 100 if len(stakes) > 0 else 0
    
    # Average winning/losing bet
    winning_bets = returns[returns > stakes] - stakes[returns > stakes]
    losing_bets = stakes[returns < stakes] - returns[returns < stakes]
    
    avg_win = winning_bets.mean() if len(winning_bets) > 0 else 0
    avg_loss = losing_bets.mean() if len(losing_bets) > 0 else 0
    
    return {
        "roi_percent": roi,
        "net_profit": net_profit,
        "gross_profit": gross_profit,
        "commission_paid": commission,
        "total_staked": total_staked,
        "win_rate_percent": win_rate,
        "num_bets": len(stakes),
        "num_wins": wins,
        "avg_winning_bet": avg_win,
        "avg_losing_bet": avg_loss,
    }


def calculate_sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: Array of period returns (e.g., daily P&L / capital)
        risk_free_rate: Annual risk-free rate (default 0)
        periods_per_year: Number of periods per year (252 for daily)
        
    Returns:
        Annualized Sharpe ratio
    """
    if len(returns) == 0 or returns.std() == 0:
        return 0.0
    
    excess_returns = returns - (risk_free_rate / periods_per_year)
    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(periods_per_year)


def calculate_max_drawdown(equity_curve: np.ndarray) -> Dict[str, float]:
    """
    Calculate maximum drawdown from equity curve
    
    Args:
        equity_curve: Array of cumulative equity values
        
    Returns:
        Dict with max_drawdown, max_drawdown_percent, peak, trough
    """
    if len(equity_curve) == 0:
        return {
            "max_drawdown": 0.0,
            "max_drawdown_percent": 0.0,
            "peak_value": 0.0,
            "trough_value": 0.0,
        }
    
    running_max = np.maximum.accumulate(equity_curve)
    drawdowns = equity_curve - running_max
    max_drawdown_idx = drawdowns.argmin()
    max_drawdown = drawdowns[max_drawdown_idx]
    
    peak_idx = running_max[:max_drawdown_idx + 1].argmax()
    peak_value = equity_curve[peak_idx]
    trough_value = equity_curve[max_drawdown_idx]
    
    max_drawdown_percent = (max_drawdown / peak_value) * 100 if peak_value > 0 else 0
    
    return {
        "max_drawdown": abs(max_drawdown),
        "max_drawdown_percent": abs(max_drawdown_percent),
        "peak_value": peak_value,
        "trough_value": trough_value,
    }


def brier_skill_score(y_true: np.ndarray, y_prob: np.ndarray, baseline_prob: float = 0.1) -> float:
    """
    Calculate Brier Skill Score (BSS) vs a baseline
    
    Args:
        y_true: Binary outcomes
        y_prob: Predicted probabilities
        baseline_prob: Baseline probability (e.g., market average)
        
    Returns:
        BSS (positive is better than baseline)
    """
    brier_model = calculate_brier_score(y_true, y_prob)
    brier_baseline = calculate_brier_score(y_true, np.full_like(y_prob, baseline_prob))
    
    bss = 1 - (brier_model / brier_baseline) if brier_baseline > 0 else 0
    return bss
