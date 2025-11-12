"""
Conformal Prediction for Racing Probabilities

Uses MAPIE (Model Agnostic Prediction Interval Estimator) to provide
uncertainty quantification and prediction intervals for win probabilities.

Conformal prediction provides statistically valid uncertainty estimates
without assumptions about the underlying probability distribution.
"""

import logging

import numpy as np
from mapie.classification import SplitConformalClassifier as MapieClassifier
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class ConformalPredictor:
    """
    Conformal prediction wrapper for racing win probability models.

    Provides:
    - Prediction intervals at specified confidence levels
    - Calibrated uncertainty estimates
    - Set-valued predictions (multiple possible outcomes)

    Uses MAPIE's Adaptive Prediction Sets (APS) method for multi-class
    classification with well-calibrated prediction sets.
    """

    def __init__(
        self, base_estimator, confidence_level: float = 0.9, random_state: int = 42
    ):
        """
        Initialize conformal predictor.

        Args:
            base_estimator: Trained sklearn-compatible classifier
            confidence_level: Confidence level (0.9 = 90% coverage)
            random_state: Random seed for reproducibility
        """
        self.base_estimator = base_estimator
        self.confidence_level = confidence_level
        self.random_state = random_state
        self.mapie_classifier = None
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Fit conformal predictor on calibration data.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Binary labels (0=loss, 1=win)
        """
        logger.info(f"Fitting conformal predictor with {len(X)} samples")

        self.mapie_classifier = MapieClassifier(
            estimator=self.base_estimator,
            confidence_level=self.confidence_level,
            conformity_score="lac",
            prefit=False,  # Let MAPIE fit the estimator
            random_state=self.random_state,
        )

        self.mapie_classifier.fit(X, y)
        self.is_fitted = True

        logger.info("Conformal predictor fitted successfully")

    def predict_with_intervals(
        self, X: np.ndarray, confidence_level: float | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Predict with conformal prediction sets.
        Note: confidence_level parameter is ignored in current implementation.
        Confidence level is set during initialization.
        """
        if not self.is_fitted:
            raise ValueError("Conformal predictor must be fitted before prediction")

        y_pred_sets = self.mapie_classifier.predict(X)
        y_pred = self.base_estimator.predict(X)

        return y_pred, y_pred_sets

    def predict_proba_with_uncertainty(
        self, X: np.ndarray, confidence_level: float | None = None
    ) -> dict[str, np.ndarray]:
        """
        Get probability predictions with uncertainty quantification.
        Note: confidence_level parameter is ignored in current implementation.
        """
        if not self.is_fitted:
            raise ValueError("Conformal predictor must be fitted before prediction")

        confidence_level = confidence_level or self.confidence_level

        # Get probabilities from base estimator
        if hasattr(self.base_estimator, "predict_proba"):
            probabilities = self.base_estimator.predict_proba(X)[:, 1]
        else:
            raise AttributeError("Base estimator must have predict_proba method")

        # Get prediction sets
        y_pred_sets = self.mapie_classifier.predict(X)

        # Calculate set sizes
        set_sizes = y_pred_sets.sum(axis=1)

        return {
            "probabilities": probabilities,
            "prediction_sets": y_pred_sets,
            "set_sizes": set_sizes,
            "confidence": confidence_level,
            "predictions": self.base_estimator.predict(X),
        }

    def evaluate_coverage(
        self, X: np.ndarray, y_true: np.ndarray, confidence_level: float | None = None
    ) -> dict[str, float]:
        """
        Evaluate empirical coverage of conformal prediction sets.
        Note: confidence_level parameter is ignored in current implementation.
        """
        confidence_level = confidence_level or self.confidence_level

        y_pred_sets = self.mapie_classifier.predict(X)

        # Check if true label is in prediction set
        coverage = np.mean([y_pred_sets[i, int(y_true[i])] for i in range(len(y_true))])

        # Average set size
        avg_set_size = np.mean(y_pred_sets.sum(axis=1))

        return {
            "empirical_coverage": coverage,
            "target_coverage": confidence_level,
            "coverage_gap": abs(coverage - confidence_level),
            "average_set_size": avg_set_size,
            "n_samples": len(y_true),
        }


if __name__ == "__main__":
    """Test conformal prediction with synthetic racing data"""
    from sklearn.ensemble import RandomForestClassifier

    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    n_features = 30

    X = np.random.randn(n_samples, n_features)
    # Simulate win probability based on first few features
    win_prob = 1 / (1 + np.exp(-(X[:, 0] + 0.5 * X[:, 1] - 0.3 * X[:, 2])))
    y = (np.random.rand(n_samples) < win_prob).astype(int)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Train base classifier
    print("Training base classifier...")
    base_clf = RandomForestClassifier(n_estimators=100, random_state=42)
    base_clf.fit(X_train, y_train)

    # Fit conformal predictor
    print("\nFitting conformal predictor (90% confidence)...")
    cp = ConformalPredictor(base_estimator=base_clf, confidence_level=0.9)
    cp.fit(X_train, y_train)

    # Make predictions
    print("\nMaking predictions with uncertainty...")
    results = cp.predict_proba_with_uncertainty(X_test[:10])

    print("\nFirst 10 predictions:")
    for i in range(10):
        prob = results["probabilities"][i]
        pred_set = results["prediction_sets"][i]
        set_size = results["set_sizes"][i]

        print(f"Sample {i + 1}:")
        print(f"  Win Probability: {prob:.3f}")
        print(f"  Prediction Set: {pred_set} (size={set_size})")
        print(f"  Interpretation: {'Confident' if set_size == 1 else 'Uncertain'}")

    # Evaluate coverage
    print(f"\nEvaluating coverage on {len(X_test)} test samples...")
    coverage_metrics = cp.evaluate_coverage(X_test, y_test)

    print("\nCoverage Metrics:")
    print(f"  Target Coverage: {coverage_metrics['target_coverage']:.1%}")
    print(f"  Empirical Coverage: {coverage_metrics['empirical_coverage']:.1%}")
    print(f"  Coverage Gap: {coverage_metrics['coverage_gap']:.1%}")
    print(f"  Average Set Size: {coverage_metrics['average_set_size']:.2f}")
    print(f"  Conditional Coverage: {coverage_metrics['conditional_coverage']:.1%}")

    print("\n✓ Conformal prediction test complete!")
