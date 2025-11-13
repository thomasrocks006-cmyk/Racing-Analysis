"""
Performance Tracker

Real-time monitoring of model predictions and system performance.
"""

from __future__ import annotations

import time
from collections import deque
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from prometheus_client import Counter, Gauge, Histogram


class PerformanceTracker:
    """
    Track and monitor model performance in production.

    Features:
    - Prediction latency tracking
    - Accuracy monitoring
    - Data drift detection
    - Prometheus metrics export
    - Performance degradation alerts
    """

    def __init__(self, window_size: int = 1000):
        """
        Initialize performance tracker.

        Args:
            window_size: Number of recent predictions to track
        """
        self.window_size = window_size

        # Recent predictions buffer
        self.predictions = deque(maxlen=window_size)
        self.actuals = deque(maxlen=window_size)
        self.probabilities = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
        self.latencies = deque(maxlen=window_size)

        # Prometheus metrics
        self.prediction_counter = Counter(
            "racing_predictions_total", "Total number of predictions made"
        )
        self.prediction_latency = Histogram(
            "racing_prediction_latency_seconds",
            "Prediction latency in seconds",
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
        )
        self.accuracy_gauge = Gauge("racing_model_accuracy", "Current model accuracy")
        self.calibration_gauge = Gauge(
            "racing_model_calibration_error", "Current calibration error (ECE)"
        )

        # Baseline statistics for drift detection
        self.baseline_mean: np.ndarray | None = None
        self.baseline_std: np.ndarray | None = None

    def track_prediction(
        self,
        prediction: int,
        probability: float,
        latency: float,
        features: np.ndarray | None = None,
        actual: int | None = None,
    ):
        """
        Track a single prediction.

        Args:
            prediction: Predicted class
            probability: Prediction probability
            latency: Prediction latency in seconds
            features: Input features (for drift detection)
            actual: Actual outcome (if known)
        """
        timestamp = datetime.now()

        self.predictions.append(prediction)
        self.probabilities.append(probability)
        self.timestamps.append(timestamp)
        self.latencies.append(latency)

        if actual is not None:
            self.actuals.append(actual)

        # Update Prometheus metrics
        self.prediction_counter.inc()
        self.prediction_latency.observe(latency)

        # Update accuracy if we have actuals
        if len(self.actuals) > 0:
            recent_accuracy = self._calculate_accuracy()
            self.accuracy_gauge.set(recent_accuracy)

        # Update calibration
        if len(self.actuals) > 10:
            ece = self._calculate_ece()
            self.calibration_gauge.set(ece)

    def _calculate_accuracy(self) -> float:
        """Calculate recent accuracy."""
        if len(self.actuals) == 0:
            return 0.0

        # Match predictions with actuals (same length)
        n = min(len(self.predictions), len(self.actuals))
        preds = list(self.predictions)[-n:]
        acts = list(self.actuals)[-n:]

        correct = sum(p == a for p, a in zip(preds, acts, strict=True))
        return correct / n if n > 0 else 0.0

    def _calculate_ece(self, n_bins: int = 10) -> float:
        """Calculate Expected Calibration Error."""
        if len(self.actuals) < 10:
            return 0.0

        n = min(len(self.probabilities), len(self.actuals))
        probs = np.array(list(self.probabilities)[-n:])
        acts = np.array(list(self.actuals)[-n:])

        bin_edges = np.linspace(0, 1, n_bins + 1)
        ece = 0.0

        for i in range(n_bins):
            mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
            if mask.sum() > 0:
                bin_acc = acts[mask].mean()
                bin_conf = probs[mask].mean()
                bin_weight = mask.sum() / len(probs)
                ece += bin_weight * abs(bin_acc - bin_conf)

        return ece

    def get_metrics(self) -> dict[str, Any]:
        """
        Get current performance metrics.

        Returns:
            Dictionary of metrics
        """
        metrics = {
            "total_predictions": len(self.predictions),
            "predictions_with_actuals": len(self.actuals),
            "mean_latency_ms": np.mean(self.latencies) * 1000 if self.latencies else 0,
            "p95_latency_ms": np.percentile(self.latencies, 95) * 1000
            if self.latencies
            else 0,
            "p99_latency_ms": np.percentile(self.latencies, 99) * 1000
            if self.latencies
            else 0,
        }

        if len(self.actuals) > 0:
            metrics.update(
                {
                    "accuracy": self._calculate_accuracy(),
                    "win_rate": np.mean(list(self.actuals)),
                }
            )

        if len(self.actuals) > 10:
            metrics["calibration_error"] = self._calculate_ece()

        return metrics

    def get_recent_performance(self, n: int = 100) -> pd.DataFrame:
        """
        Get recent prediction history.

        Args:
            n: Number of recent predictions to return

        Returns:
            DataFrame with prediction history
        """
        n = min(n, len(self.predictions))

        data = {
            "timestamp": list(self.timestamps)[-n:],
            "prediction": list(self.predictions)[-n:],
            "probability": list(self.probabilities)[-n:],
            "latency_ms": [lat * 1000 for lat in list(self.latencies)[-n:]],
        }

        if len(self.actuals) >= n:
            data["actual"] = list(self.actuals)[-n:]
            data["correct"] = [
                p == a
                for p, a in zip(
                    list(self.predictions)[-n:], list(self.actuals)[-n:], strict=True
                )
            ]

        return pd.DataFrame(data)

    def detect_drift(
        self, features: np.ndarray, threshold: float = 3.0
    ) -> dict[str, Any]:
        """
        Detect data drift using Z-score method.

        Args:
            features: Current feature values
            threshold: Z-score threshold for drift detection

        Returns:
            Drift detection results
        """
        if self.baseline_mean is None or self.baseline_std is None:
            return {
                "drift_detected": False,
                "message": "No baseline set for drift detection",
            }

        # Calculate Z-scores
        z_scores = np.abs((features - self.baseline_mean) / (self.baseline_std + 1e-10))
        max_z_score = np.max(z_scores)
        drift_features = np.where(z_scores > threshold)[0]

        return {
            "drift_detected": len(drift_features) > 0,
            "max_z_score": float(max_z_score),
            "drift_features": drift_features.tolist(),
            "threshold": threshold,
        }

    def set_baseline(self, features: np.ndarray):
        """
        Set baseline statistics for drift detection.

        Args:
            features: Historical feature matrix (n_samples, n_features)
        """
        self.baseline_mean = np.mean(features, axis=0)
        self.baseline_std = np.std(features, axis=0)

    def check_degradation(self, accuracy_threshold: float = 0.1) -> dict[str, Any]:
        """
        Check for performance degradation.

        Args:
            accuracy_threshold: Minimum acceptable accuracy drop

        Returns:
            Degradation check results
        """
        if len(self.actuals) < 50:
            return {
                "degradation_detected": False,
                "message": "Insufficient data for degradation check",
            }

        # Compare recent vs historical accuracy
        mid_point = len(self.actuals) // 2
        acts = list(self.actuals)
        preds = list(self.predictions)[-len(acts) :]

        historical_accuracy = (
            sum(
                p == a for p, a in zip(preds[:mid_point], acts[:mid_point], strict=True)
            )
            / mid_point
        )

        recent_accuracy = sum(
            p == a for p, a in zip(preds[mid_point:], acts[mid_point:], strict=True)
        ) / (len(acts) - mid_point)

        accuracy_drop = historical_accuracy - recent_accuracy

        return {
            "degradation_detected": accuracy_drop > accuracy_threshold,
            "historical_accuracy": historical_accuracy,
            "recent_accuracy": recent_accuracy,
            "accuracy_drop": accuracy_drop,
            "threshold": accuracy_threshold,
        }

    def export_metrics_summary(self) -> str:
        """
        Export metrics in Prometheus format.

        Returns:
            Prometheus-formatted metrics string
        """
        metrics = self.get_metrics()
        lines = []

        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                metric_name = f"racing_{key}"
                lines.append(f"# TYPE {metric_name} gauge")
                lines.append(f"{metric_name} {value}")

        return "\n".join(lines)

    def reset(self):
        """Clear all tracked data."""
        self.predictions.clear()
        self.actuals.clear()
        self.probabilities.clear()
        self.timestamps.clear()
        self.latencies.clear()
