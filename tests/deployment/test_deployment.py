"""
Tests for Week 9-10: Deployment and Monitoring

Comprehensive tests for:
- Model registry
- Performance tracking
- Alert management
- API endpoints
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier

from src.deployment.model_registry import ModelRegistry
from src.monitoring.alerting import Alert, AlertManager, LogAlertChannel
from src.monitoring.performance_tracker import PerformanceTracker


class TestModelRegistry:
    """Test model registry functionality."""

    @pytest.fixture
    def temp_registry(self):
        """Create temporary registry directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_model(self):
        """Create a simple trained model."""
        X = np.random.rand(100, 5)
        y = np.random.randint(0, 2, 100)
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        return model

    def test_register_model(self, temp_registry, sample_model):
        """Test model registration."""
        registry = ModelRegistry(temp_registry)

        metrics = {"accuracy": 0.85, "roi": 0.12}
        hyperparameters = {"n_estimators": 10}

        model_id = registry.register_model(
            model=sample_model,
            name="test_model",
            version="v1.0",
            metrics=metrics,
            hyperparameters=hyperparameters,
        )

        assert model_id == "test_model:v1.0"
        assert registry.metadata["active"] == model_id
        assert "test_model:v1.0" in registry.metadata["models"]

    def test_load_model(self, temp_registry, sample_model):
        """Test model loading."""
        registry = ModelRegistry(temp_registry)

        metrics = {"accuracy": 0.85}
        registry.register_model(
            model=sample_model, name="test_model", version="v1.0", metrics=metrics
        )

        loaded_model = registry.load_model("test_model", "v1.0")
        assert loaded_model is not None

        # Test predictions match
        X_test = np.random.rand(10, 5)
        original_pred = sample_model.predict(X_test)
        loaded_pred = loaded_model.predict(X_test)

        np.testing.assert_array_equal(original_pred, loaded_pred)

    def test_get_active_model(self, temp_registry, sample_model):
        """Test getting active model."""
        registry = ModelRegistry(temp_registry)

        metrics = {"accuracy": 0.85}
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="v1.0",
            metrics=metrics,
            set_active=True,
        )

        model, metadata = registry.get_active_model()
        assert model is not None
        assert metadata["name"] == "test_model"
        assert metadata["version"] == "v1.0"

    def test_set_active_model(self, temp_registry, sample_model):
        """Test setting active model."""
        registry = ModelRegistry(temp_registry)

        # Register two versions
        registry.register_model(
            model=sample_model,
            name="test_model",
            version="v1.0",
            metrics={"accuracy": 0.80},
            set_active=True,
        )

        registry.register_model(
            model=sample_model,
            name="test_model",
            version="v2.0",
            metrics={"accuracy": 0.85},
            set_active=False,
        )

        # Switch active version
        registry.set_active_model("test_model", "v2.0")
        assert registry.metadata["active"] == "test_model:v2.0"

    def test_list_models(self, temp_registry, sample_model):
        """Test listing models."""
        registry = ModelRegistry(temp_registry)

        registry.register_model(
            model=sample_model,
            name="model_a",
            version="v1.0",
            metrics={"accuracy": 0.80},
        )

        registry.register_model(
            model=sample_model,
            name="model_b",
            version="v1.0",
            metrics={"accuracy": 0.85},
        )

        # List all models
        all_models = registry.list_models()
        assert len(all_models) == 2

        # List specific model
        model_a_versions = registry.list_models(name="model_a")
        assert len(model_a_versions) == 1
        assert model_a_versions.iloc[0]["name"] == "model_a"

    def test_compare_models(self, temp_registry, sample_model):
        """Test model comparison."""
        registry = ModelRegistry(temp_registry)

        registry.register_model(
            model=sample_model,
            name="test_model",
            version="v1.0",
            metrics={"accuracy": 0.80, "roi": 0.10},
        )

        registry.register_model(
            model=sample_model,
            name="test_model",
            version="v2.0",
            metrics={"accuracy": 0.85, "roi": 0.15},
        )

        comparison = registry.compare_models(
            ["test_model:v1.0", "test_model:v2.0"], metric="accuracy"
        )

        assert len(comparison) == 2
        # Should be sorted by accuracy (descending)
        assert comparison.iloc[0]["version"] == "v2.0"

    def test_delete_model(self, temp_registry, sample_model):
        """Test model deletion."""
        registry = ModelRegistry(temp_registry)

        registry.register_model(
            model=sample_model,
            name="test_model",
            version="v1.0",
            metrics={"accuracy": 0.80},
            set_active=False,
        )

        registry.delete_model("test_model", "v1.0")
        assert "test_model:v1.0" not in registry.metadata["models"]


class TestPerformanceTracker:
    """Test performance tracking functionality."""

    def test_track_prediction(self):
        """Test prediction tracking."""
        tracker = PerformanceTracker(window_size=100)

        tracker.track_prediction(prediction=1, probability=0.75, latency=0.01, actual=1)

        assert len(tracker.predictions) == 1
        assert len(tracker.actuals) == 1
        assert tracker.predictions[0] == 1
        assert tracker.probabilities[0] == 0.75

    def test_get_metrics(self):
        """Test metrics calculation."""
        tracker = PerformanceTracker(window_size=100)

        # Add some predictions
        for i in range(20):
            tracker.track_prediction(
                prediction=i % 2,
                probability=0.6 + (i % 2) * 0.2,
                latency=0.01 + i * 0.001,
                actual=i % 2,
            )

        metrics = tracker.get_metrics()

        assert "total_predictions" in metrics
        assert "mean_latency_ms" in metrics
        assert "accuracy" in metrics
        assert metrics["total_predictions"] == 20
        assert metrics["accuracy"] == 1.0  # All correct

    def test_accuracy_calculation(self):
        """Test accuracy calculation."""
        tracker = PerformanceTracker()

        # Add correct predictions
        for _ in range(7):
            tracker.track_prediction(1, 0.8, 0.01, actual=1)

        # Add incorrect predictions
        for _ in range(3):
            tracker.track_prediction(1, 0.8, 0.01, actual=0)

        accuracy = tracker._calculate_accuracy()
        assert accuracy == 0.7  # 7/10

    def test_calibration_error(self):
        """Test calibration error calculation."""
        tracker = PerformanceTracker()

        # Add perfectly calibrated predictions
        for prob in np.linspace(0.1, 0.9, 50):
            actual = 1 if np.random.random() < prob else 0
            tracker.track_prediction(
                prediction=int(prob > 0.5),
                probability=prob,
                latency=0.01,
                actual=actual,
            )

        ece = tracker._calculate_ece()
        assert isinstance(ece, float)
        assert ece >= 0.0

    def test_drift_detection(self):
        """Test data drift detection."""
        tracker = PerformanceTracker()

        # Set baseline
        baseline_features = np.random.randn(100, 5)
        tracker.set_baseline(baseline_features)

        # Test with similar features (no drift)
        similar_features = np.random.randn(5) * 0.5
        result = tracker.detect_drift(similar_features, threshold=3.0)
        assert isinstance(result["drift_detected"], bool)

        # Test with very different features (drift)
        different_features = np.random.randn(5) * 10 + 50
        result = tracker.detect_drift(different_features, threshold=3.0)
        assert result["drift_detected"] is True

    def test_degradation_check(self):
        """Test performance degradation detection."""
        tracker = PerformanceTracker()

        # Add good historical performance
        for _ in range(50):
            tracker.track_prediction(1, 0.8, 0.01, actual=1)

        # Add poor recent performance
        for _ in range(50):
            tracker.track_prediction(1, 0.8, 0.01, actual=0)

        result = tracker.check_degradation(accuracy_threshold=0.1)
        assert result["degradation_detected"] is True
        assert result["accuracy_drop"] > 0.4


class TestAlertManager:
    """Test alert management functionality."""

    def test_alert_creation(self):
        """Test alert object creation."""
        alert = Alert(
            severity="warning",
            message="Test alert",
            metric="accuracy",
            value=0.65,
            threshold=0.70,
        )

        assert alert.severity == "warning"
        assert alert.metric == "accuracy"
        assert alert.value == 0.65

    def test_set_threshold(self):
        """Test setting alert thresholds."""
        manager = AlertManager()

        manager.set_threshold("custom_metric", warning=0.8, critical=0.6)

        assert "custom_metric" in manager.thresholds
        assert manager.thresholds["custom_metric"]["warning"] == 0.8
        assert manager.thresholds["custom_metric"]["critical"] == 0.6

    def test_check_metric_higher_better(self):
        """Test metric checking (higher is better)."""
        manager = AlertManager()
        manager.set_threshold("accuracy", warning=0.7, critical=0.6)

        # Good value - no alert
        alert = manager.check_metric("accuracy", 0.85, higher_is_better=True)
        assert alert is None

        # Warning threshold
        alert = manager.check_metric("accuracy", 0.65, higher_is_better=True)
        assert alert is not None
        assert alert.severity == "warning"

        # Critical threshold
        alert = manager.check_metric("accuracy", 0.55, higher_is_better=True)
        assert alert is not None
        assert alert.severity == "critical"

    def test_check_metric_lower_better(self):
        """Test metric checking (lower is better)."""
        manager = AlertManager()
        manager.set_threshold("latency", warning=0.5, critical=1.0)

        # Good value - no alert
        alert = manager.check_metric("latency", 0.1, higher_is_better=False)
        assert alert is None

        # Warning threshold
        alert = manager.check_metric("latency", 0.7, higher_is_better=False)
        assert alert is not None
        assert alert.severity == "warning"

        # Critical threshold
        alert = manager.check_metric("latency", 1.5, higher_is_better=False)
        assert alert is not None
        assert alert.severity == "critical"

    def test_trigger_alert(self):
        """Test alert triggering."""
        manager = AlertManager()

        alert = Alert(
            severity="warning",
            message="Test alert",
            metric="accuracy",
            value=0.65,
            threshold=0.70,
        )

        manager.trigger_alert(alert)

        assert len(manager.alert_history) == 1
        assert manager.alert_history[0] == alert

    def test_get_recent_alerts(self):
        """Test getting recent alerts."""
        manager = AlertManager()

        # Add multiple alerts
        for i in range(5):
            alert = Alert(
                severity="warning" if i % 2 == 0 else "critical",
                message=f"Alert {i}",
                metric="test",
                value=0.5,
                threshold=0.7,
            )
            manager.trigger_alert(alert)

        # Get all recent alerts
        recent = manager.get_recent_alerts(n=3)
        assert len(recent) == 3

        # Get only warnings
        warnings = manager.get_recent_alerts(n=10, severity="warning")
        assert all(a.severity == "warning" for a in warnings)

    def test_log_alert_channel(self):
        """Test log alert channel."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "alerts.log"
            channel = LogAlertChannel(str(log_file))

            alert = Alert(
                severity="warning",
                message="Test log alert",
                metric="accuracy",
                value=0.65,
                threshold=0.70,
            )

            channel.send(alert)

            assert log_file.exists()
            content = log_file.read_text()
            assert "Test log alert" in content
            assert "WARNING" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
