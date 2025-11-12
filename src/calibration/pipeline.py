"""
Calibration Pipeline

Orchestrates the complete calibration workflow:
1. Train ensemble model
2. Apply conformal prediction for uncertainty
3. Apply probability calibration
4. Visualize calibration quality
5. Generate reliability diagrams

Integrates ConformalPredictor and ProbabilityCalibrator into
a unified pipeline for production use.
"""

import numpy as np
import matplotlib.pyplot as plt
import logging
from pathlib import Path

from .conformal import ConformalPredictor
from .calibrators import ProbabilityCalibrator, MultiCalibrator

logger = logging.getLogger(__name__)


class CalibrationPipeline:
    """
    End-to-end calibration pipeline for racing predictions.
    
    Workflow:
    1. Fit conformal predictor for uncertainty quantification
    2. Fit probability calibrator for well-calibrated probabilities
    3. Combine both for production predictions
    
    Output:
    - Calibrated win probabilities
    - Prediction intervals (confidence sets)
    - Uncertainty estimates
    """
    
    def __init__(
        self,
        base_estimator,
        calibration_method: str = 'auto',
        conformal_confidence: float = 0.9,
        use_conformal: bool = True,
        use_calibration: bool = True
    ):
        """
        Initialize calibration pipeline.
        
        Args:
            base_estimator: Trained ML model (sklearn-compatible)
            calibration_method: 'auto', 'isotonic', 'platt', 'identity'
            conformal_confidence: Confidence level for conformal prediction (default 0.9 = 90%)
            use_conformal: Enable conformal prediction
            use_calibration: Enable probability calibration
        """
        self.base_estimator = base_estimator
        self.calibration_method = calibration_method
        self.conformal_confidence = conformal_confidence
        self.use_conformal = use_conformal
        self.use_calibration = use_calibration
        
        self.conformal_predictor = None
        self.calibrator = None
        self.is_fitted = False
        
    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Fit calibration pipeline on calibration data.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Binary labels (0=loss, 1=win)
        """
        logger.info(f"Fitting calibration pipeline on {len(X)} samples")
        
        # Get base model predictions
        if hasattr(self.base_estimator, 'predict_proba'):
            base_probs = self.base_estimator.predict_proba(X)[:, 1]
        else:
            raise AttributeError("Base estimator must have predict_proba method")
            
        # Fit conformal predictor
        if self.use_conformal:
            logger.info("Fitting conformal predictor...")
            self.conformal_predictor = ConformalPredictor(
                base_estimator=self.base_estimator,
                confidence_level=self.conformal_confidence
            )
            self.conformal_predictor.fit(X, y)
            
        # Fit probability calibrator
        if self.use_calibration:
            logger.info("Fitting probability calibrator...")
            if self.calibration_method == 'auto':
                self.calibrator = MultiCalibrator()
                self.calibrator.fit(base_probs, y, validation_split=0.2)
            else:
                self.calibrator = ProbabilityCalibrator(method=self.calibration_method)
                self.calibrator.fit(base_probs, y)
                
        self.is_fitted = True
        logger.info("Calibration pipeline fitted successfully")
        
    def predict(
        self,
        X: np.ndarray,
        return_uncertainty: bool = False
    ) -> dict:
        """
        Make calibrated predictions with optional uncertainty.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            return_uncertainty: Include conformal prediction sets
            
        Returns:
            Dictionary containing:
                - 'probabilities': Calibrated win probabilities
                - 'uncertainty' (optional): Conformal prediction results
        """
        if not self.is_fitted:
            raise ValueError("Pipeline must be fitted before prediction")
            
        # Get base predictions
        base_probs = self.base_estimator.predict_proba(X)[:, 1]
        
        # Apply calibration
        if self.use_calibration and self.calibrator is not None:
            calibrated_probs = self.calibrator.transform(base_probs)
        else:
            calibrated_probs = base_probs
            
        result = {
            'probabilities': calibrated_probs,
            'uncalibrated_probabilities': base_probs
        }
        
        # Add uncertainty quantification
        if return_uncertainty and self.use_conformal and self.conformal_predictor is not None:
            uncertainty = self.conformal_predictor.predict_proba_with_uncertainty(X)
            result['uncertainty'] = uncertainty
            
        return result
        
    def evaluate_calibration(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_bins: int = 10,
        plot: bool = False,
        save_path: str | None = None
    ) -> dict:
        """
        Evaluate calibration quality and optionally plot reliability diagram.
        
        Args:
            X: Feature matrix
            y: True labels
            n_bins: Number of bins for calibration curve
            plot: Generate reliability diagram
            save_path: Path to save plot (if plot=True)
            
        Returns:
            Dictionary with calibration metrics
        """
        if not self.is_fitted:
            raise ValueError("Pipeline must be fitted before evaluation")
            
        # Get predictions
        predictions = self.predict(X, return_uncertainty=self.use_conformal)
        calibrated_probs = predictions['probabilities']
        uncalibrated_probs = predictions['uncalibrated_probabilities']
        
        # Calculate metrics for uncalibrated probabilities
        if self.calibrator is not None:
            uncalib_metrics = ProbabilityCalibrator('isotonic').evaluate(
                uncalibrated_probs, y, n_bins
            )
        else:
            uncalib_metrics = {'ece': None}
            
        # Calculate metrics for calibrated probabilities
        calib_metrics = ProbabilityCalibrator('isotonic').evaluate(
            calibrated_probs, y, n_bins
        )
        
        metrics = {
            'uncalibrated_ece': uncalib_metrics['ece'],
            'calibrated_ece': calib_metrics['ece'],
            'improvement': uncalib_metrics['ece'] - calib_metrics['ece'] if uncalib_metrics['ece'] else None,
            'n_bins': n_bins,
            'n_samples': len(y),
            'bin_statistics': calib_metrics['bin_statistics']
        }
        
        # Add conformal metrics if available
        if self.use_conformal and 'uncertainty' in predictions:
            conformal_metrics = self.conformal_predictor.evaluate_coverage(X, y)
            metrics['conformal'] = conformal_metrics
            
        # Generate reliability diagram
        if plot:
            self._plot_reliability_diagram(
                uncalibrated_probs,
                calibrated_probs,
                y,
                n_bins,
                save_path
            )
            
        return metrics
        
    def _plot_reliability_diagram(
        self,
        uncalibrated_probs: np.ndarray,
        calibrated_probs: np.ndarray,
        y_true: np.ndarray,
        n_bins: int,
        save_path: str | None
    ):
        """
        Plot reliability diagram comparing calibrated vs uncalibrated probabilities.
        
        A reliability diagram plots predicted probability vs observed frequency.
        Perfect calibration lies on the diagonal (y=x).
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Helper function to calculate bin statistics
        def get_bin_stats(probs, labels, n_bins):
            bin_edges = np.linspace(0, 1, n_bins + 1)
            bin_indices = np.digitize(probs, bin_edges[1:-1])
            
            bin_probs = []
            bin_freqs = []
            bin_counts = []
            
            for i in range(n_bins):
                mask = (bin_indices == i)
                if mask.sum() > 0:
                    bin_probs.append(probs[mask].mean())
                    bin_freqs.append(labels[mask].mean())
                    bin_counts.append(mask.sum())
                    
            return np.array(bin_probs), np.array(bin_freqs), np.array(bin_counts)
        
        # Plot uncalibrated
        bin_probs_uncal, bin_freqs_uncal, bin_counts_uncal = get_bin_stats(
            uncalibrated_probs, y_true, n_bins
        )
        
        ax1.scatter(bin_probs_uncal, bin_freqs_uncal, s=bin_counts_uncal, alpha=0.6, c='red')
        ax1.plot([0, 1], [0, 1], 'k--', label='Perfect calibration')
        ax1.set_xlabel('Predicted Probability')
        ax1.set_ylabel('Observed Frequency')
        ax1.set_title('Uncalibrated Predictions')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([0, 1])
        ax1.set_ylim([0, 1])
        
        # Plot calibrated
        bin_probs_cal, bin_freqs_cal, bin_counts_cal = get_bin_stats(
            calibrated_probs, y_true, n_bins
        )
        
        ax2.scatter(bin_probs_cal, bin_freqs_cal, s=bin_counts_cal, alpha=0.6, c='green')
        ax2.plot([0, 1], [0, 1], 'k--', label='Perfect calibration')
        ax2.set_xlabel('Predicted Probability')
        ax2.set_ylabel('Observed Frequency')
        ax2.set_title('Calibrated Predictions')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 1])
        ax2.set_ylim([0, 1])
        
        plt.tight_layout()
        
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Reliability diagram saved to {save_path}")
        else:
            plt.show()
            
        plt.close()
        
    def predict_race(
        self,
        X_race: np.ndarray,
        normalize: bool = True
    ) -> dict:
        """
        Predict calibrated probabilities for all horses in a race.
        
        Args:
            X_race: Feature matrix for all horses in race (n_horses, n_features)
            normalize: Normalize probabilities to sum to 1.0 (creates proper probability distribution)
            
        Returns:
            Dictionary with:
                - 'probabilities': Calibrated win probabilities
                - 'normalized': Whether probabilities were normalized
                - 'uncertainty': Conformal prediction sets (if enabled)
        """
        predictions = self.predict(X_race, return_uncertainty=self.use_conformal)
        probabilities = predictions['probabilities']
        
        # Normalize to sum to 1.0 (market book)
        if normalize:
            probabilities = probabilities / probabilities.sum()
            
        result = {
            'probabilities': probabilities,
            'normalized': normalize,
            'uncalibrated_probabilities': predictions['uncalibrated_probabilities']
        }
        
        if 'uncertainty' in predictions:
            result['uncertainty'] = predictions['uncertainty']
            
        return result


if __name__ == "__main__":
    """Test complete calibration pipeline"""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    
    # Generate synthetic racing data
    np.random.seed(42)
    n_samples = 2000
    n_features = 30
    
    X = np.random.randn(n_samples, n_features)
    win_prob = 1 / (1 + np.exp(-(X[:, 0] + 0.5 * X[:, 1] - 0.3 * X[:, 2])))
    y = (np.random.rand(n_samples) < win_prob).astype(int)
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.4, random_state=42, stratify=y
    )
    X_cal, X_test, y_cal, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    
    print("CALIBRATION PIPELINE TEST")
    print("=" * 60)
    print(f"Dataset: {len(X_train)} train, {len(X_cal)} calibration, {len(X_test)} test")
    print(f"Win rate: {y_train.mean():.1%}\n")
    
    # Train base model
    print("Training base classifier...")
    base_model = RandomForestClassifier(n_estimators=100, random_state=42)
    base_model.fit(X_train, y_train)
    
    # Create and fit calibration pipeline
    print("\nFitting calibration pipeline...")
    pipeline = CalibrationPipeline(
        base_estimator=base_model,
        calibration_method='auto',
        conformal_confidence=0.9,
        use_conformal=True,
        use_calibration=True
    )
    
    pipeline.fit(X_cal, y_cal)
    
    # Evaluate on test set
    print("\nEvaluating calibration on test set...")
    metrics = pipeline.evaluate_calibration(
        X_test, y_test,
        n_bins=10,
        plot=False  # Set to True to see reliability diagram
    )
    
    print("\nCalibration Metrics:")
    print(f"  Uncalibrated ECE: {metrics['uncalibrated_ece']:.4f}")
    print(f"  Calibrated ECE: {metrics['calibrated_ece']:.4f}")
    print(f"  Improvement: {metrics['improvement']:.4f}")
    
    if 'conformal' in metrics:
        print("\nConformal Prediction Metrics:")
        print(f"  Target Coverage: {metrics['conformal']['target_coverage']:.1%}")
        print(f"  Empirical Coverage: {metrics['conformal']['empirical_coverage']:.1%}")
        print(f"  Average Set Size: {metrics['conformal']['average_set_size']:.2f}")
    
    # Simulate race prediction
    print("\nSimulating race prediction (10 horses)...")
    X_race = X_test[:10]  # First 10 test samples as a "race"
    
    race_predictions = pipeline.predict_race(X_race, normalize=True)
    
    print("\nRace Probabilities (normalized to sum=1.0):")
    for i, prob in enumerate(race_predictions['probabilities']):
        print(f"  Horse {i+1}: {prob:.1%}")
    print(f"\nSum of probabilities: {race_predictions['probabilities'].sum():.4f}")
    
    if 'uncertainty' in race_predictions:
        print("\nUncertainty Estimates:")
        set_sizes = race_predictions['uncertainty']['set_sizes']
        for i, size in enumerate(set_sizes):
            confidence = 'High' if size == 1 else 'Low'
            print(f"  Horse {i+1}: Prediction set size={size} ({confidence} confidence)")
    
    print("\n✓ Calibration pipeline test complete!")
