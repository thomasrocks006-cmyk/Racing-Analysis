"""
Probability Calibration Methods

Implements calibration techniques using scikit-learn:
- Isotonic Regression (non-parametric)
- Platt Scaling (logistic regression)
"""

import logging

import numpy as np
from sklearn.isotonic import IsotonicRegression as SklearnIsotonic
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def calculate_ece(
    probabilities: np.ndarray, labels: np.ndarray, n_bins: int = 10
) -> float:
    """Calculate Expected Calibration Error (ECE)."""
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(probabilities, bin_edges[1:-1])

    ece = 0.0
    for i in range(n_bins):
        mask = bin_indices == i
        if mask.sum() > 0:
            bin_prob = probabilities[mask].mean()
            bin_freq = labels[mask].mean()
            bin_weight = mask.sum() / len(probabilities)
            ece += bin_weight * abs(bin_prob - bin_freq)

    return ece


class ProbabilityCalibrator:
    """Probability calibrator for racing predictions."""

    def __init__(self, method: str = "isotonic"):
        self.method = method
        self.calibrator = None
        self.is_fitted = False

        if method == "isotonic":
            self.calibrator = SklearnIsotonic(out_of_bounds="clip")
        elif method == "platt":
            self.calibrator = LogisticRegression()
        elif method == "identity":
            self.calibrator = None
        else:
            raise ValueError(f"Unknown calibration method: {method}")

        logger.info(f"Initialized {method} calibrator")

    def fit(self, probabilities: np.ndarray, labels: np.ndarray):
        logger.info(f"Fitting {self.method} calibrator on {len(probabilities)} samples")

        if self.method == "identity":
            self.is_fitted = True
            return

        probabilities = np.clip(probabilities, 1e-7, 1 - 1e-7)

        if self.method == "isotonic":
            self.calibrator.fit(probabilities, labels)
        elif self.method == "platt":
            logits = np.log(probabilities / (1 - probabilities))
            self.calibrator.fit(logits.reshape(-1, 1), labels)

        self.is_fitted = True
        logger.info(f"{self.method} calibrator fitted successfully")

    def transform(self, probabilities: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Calibrator must be fitted before transform")

        if self.method == "identity":
            return probabilities

        probabilities = np.clip(probabilities, 1e-7, 1 - 1e-7)

        if self.method == "isotonic":
            calibrated = self.calibrator.predict(probabilities)
        elif self.method == "platt":
            logits = np.log(probabilities / (1 - probabilities))
            calibrated = self.calibrator.predict_proba(logits.reshape(-1, 1))[:, 1]

        return np.clip(calibrated, 0, 1)

    def fit_transform(
        self, probabilities: np.ndarray, labels: np.ndarray
    ) -> np.ndarray:
        self.fit(probabilities, labels)
        return self.transform(probabilities)

    def evaluate(
        self, probabilities: np.ndarray, labels: np.ndarray, n_bins: int = 10
    ) -> dict:
        probabilities = np.clip(probabilities, 1e-7, 1 - 1e-7)
        ece_score = calculate_ece(probabilities, labels, n_bins)

        bin_edges = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(probabilities, bin_edges[1:-1])

        bin_stats = []
        for i in range(n_bins):
            mask = bin_indices == i
            if mask.sum() > 0:
                bin_prob = probabilities[mask].mean()
                bin_freq = labels[mask].mean()
                bin_count = mask.sum()
                bin_stats.append(
                    {
                        "bin": i,
                        "count": int(bin_count),
                        "avg_predicted": float(bin_prob),
                        "avg_observed": float(bin_freq),
                        "gap": abs(bin_prob - bin_freq),
                    }
                )

        return {
            "ece": float(ece_score),
            "n_bins": n_bins,
            "n_samples": len(probabilities),
            "bin_statistics": bin_stats,
            "method": self.method,
        }


class MultiCalibrator:
    """Ensemble of multiple calibration methods."""

    def __init__(self, methods: list | None = None):
        self.methods = methods or ["isotonic", "platt", "identity"]
        self.calibrators = {
            method: ProbabilityCalibrator(method) for method in self.methods
        }
        self.best_method = None
        self.best_calibrator = None
        self.validation_scores = {}

    def fit(
        self,
        probabilities: np.ndarray,
        labels: np.ndarray,
        validation_split: float = 0.2,
    ):
        probs_train, probs_val, labels_train, labels_val = train_test_split(
            probabilities,
            labels,
            test_size=validation_split,
            random_state=42,
            stratify=labels,
        )

        logger.info(f"Training {len(self.methods)} calibrators...")

        for method in self.methods:
            try:
                calibrator = self.calibrators[method]
                calibrator.fit(probs_train, labels_train)
                calibrated_val = calibrator.transform(probs_val)
                ece = calculate_ece(calibrated_val, labels_val)
                self.validation_scores[method] = ece
                logger.info(f"  {method}: ECE = {ece:.4f}")
            except Exception as e:
                logger.warning(f"  {method}: Failed - {e}")
                self.validation_scores[method] = float("inf")

        self.best_method = min(self.validation_scores, key=self.validation_scores.get)
        self.best_calibrator = self.calibrators[self.best_method]
        self.best_calibrator.fit(probabilities, labels)

        logger.info(
            f"Best method: {self.best_method} (ECE={self.validation_scores[self.best_method]:.4f})"
        )

    def transform(self, probabilities: np.ndarray) -> np.ndarray:
        if self.best_calibrator is None:
            raise ValueError("MultiCalibrator must be fitted before transform")
        return self.best_calibrator.transform(probabilities)

    def get_best_method(self) -> str:
        return self.best_method


if __name__ == "__main__":
    np.random.seed(42)
    n_samples = 2000

    true_probs = np.random.beta(2, 8, n_samples)
    predicted_probs = np.clip(true_probs**0.7, 0.01, 0.99)
    labels = (np.random.rand(n_samples) < true_probs).astype(int)

    print("Testing Probability Calibration")
    print("=" * 50)

    probs_train, probs_test, labels_train, labels_test = train_test_split(
        predicted_probs, labels, test_size=0.3, random_state=42, stratify=labels
    )

    print(f"\nDataset: {len(probs_train)} train, {len(probs_test)} test")
    print(f"Win rate: {labels_train.mean():.1%}\n")

    for method in ["isotonic", "platt"]:
        print(f"{method.upper()}:")
        calibrator = ProbabilityCalibrator(method=method)
        calibrator.fit(probs_train, labels_train)

        ece_before = calculate_ece(probs_test, labels_test)
        calibrated = calibrator.transform(probs_test)
        ece_after = calculate_ece(calibrated, labels_test)

        print(
            f"  Before: {ece_before:.4f} | After: {ece_after:.4f} | Improvement: {ece_before - ece_after:.4f}\n"
        )

    print("MULTI-CALIBRATOR:")
    multi = MultiCalibrator()
    multi.fit(probs_train, labels_train)
    print(f"Best: {multi.get_best_method()}")
    print("✓ Complete!")
