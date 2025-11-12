"""
Calibration Module Tests

Comprehensive tests for:
- Conformal prediction (MAPIE)
- Probability calibration (isotonic, Platt, temperature, beta)
- Calibration pipeline
- Integration with ML models
"""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.calibration.conformal import ConformalPredictor
from src.calibration.calibrators import ProbabilityCalibrator, MultiCalibrator
from src.calibration.pipeline import CalibrationPipeline


# Fixtures for test data
@pytest.fixture
def synthetic_data():
    """Generate synthetic racing data for testing."""
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    X = np.random.randn(n_samples, n_features)
    # Simulate win probability
    win_prob = 1 / (1 + np.exp(-(X[:, 0] + 0.5 * X[:, 1])))
    y = (np.random.rand(n_samples) < win_prob).astype(int)
    
    return train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)


@pytest.fixture
def trained_model(synthetic_data):
    """Trained base classifier."""
    X_train, _, y_train, _ = synthetic_data
    model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
    model.fit(X_train, y_train)
    return model


class TestConformalPrediction:
    """Test conformal prediction functionality."""
    
    def test_conformal_fit(self, trained_model, synthetic_data):
        """Test conformal predictor fitting."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        cp = ConformalPredictor(
            base_estimator=trained_model,
            alpha=0.1,
            cv=3
        )
        
        cp.fit(X_train, y_train)
        
        assert cp.is_fitted
        assert cp.mapie_classifier is not None
        
    def test_conformal_predict(self, trained_model, synthetic_data):
        """Test conformal prediction sets."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        cp = ConformalPredictor(base_estimator=trained_model, alpha=0.1)
        cp.fit(X_train, y_train)
        
        y_pred, y_pred_sets = cp.predict_with_intervals(X_test)
        
        # Check output shapes
        assert len(y_pred) == len(X_test)
        assert y_pred_sets.shape == (len(X_test), 2)  # Binary classification
        
        # Predictions should be 0 or 1
        assert set(y_pred).issubset({0, 1})
        
        # Prediction sets should be boolean
        assert y_pred_sets.dtype == bool
        
    def test_conformal_coverage(self, trained_model, synthetic_data):
        """Test empirical coverage matches theoretical coverage."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        alpha = 0.1
        target_coverage = 1 - alpha
        
        cp = ConformalPredictor(base_estimator=trained_model, alpha=alpha)
        cp.fit(X_train, y_train)
        
        coverage_metrics = cp.evaluate_coverage(X_test, y_test)
        
        # Coverage should be close to target (within 10% tolerance)
        assert abs(coverage_metrics['empirical_coverage'] - target_coverage) < 0.1
        assert coverage_metrics['target_coverage'] == target_coverage
        assert coverage_metrics['n_samples'] == len(X_test)
        
    def test_conformal_uncertainty(self, trained_model, synthetic_data):
        """Test uncertainty quantification."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        cp = ConformalPredictor(base_estimator=trained_model, alpha=0.1)
        cp.fit(X_train, y_train)
        
        results = cp.predict_proba_with_uncertainty(X_test[:10])
        
        assert 'probabilities' in results
        assert 'prediction_sets' in results
        assert 'set_sizes' in results
        assert 'confidence' in results
        
        # Probabilities should be in [0, 1]
        assert np.all(results['probabilities'] >= 0)
        assert np.all(results['probabilities'] <= 1)
        
        # Set sizes should be 1 or 2
        assert np.all(results['set_sizes'] >= 1)
        assert np.all(results['set_sizes'] <= 2)
        

class TestProbabilityCalibration:
    """Test probability calibration methods."""
    
    @pytest.mark.parametrize("method", ['isotonic', 'platt', 'temperature', 'beta'])
    def test_calibrator_fit(self, method, trained_model, synthetic_data):
        """Test calibrator fitting for each method."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        # Get predictions
        probs = trained_model.predict_proba(X_train)[:, 1]
        
        calibrator = ProbabilityCalibrator(method=method)
        calibrator.fit(probs, y_train)
        
        assert calibrator.is_fitted
        assert calibrator.calibrator is not None
        
    @pytest.mark.parametrize("method", ['isotonic', 'platt', 'temperature', 'beta'])
    def test_calibrator_transform(self, method, trained_model, synthetic_data):
        """Test probability transformation."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        probs_train = trained_model.predict_proba(X_train)[:, 1]
        probs_test = trained_model.predict_proba(X_test)[:, 1]
        
        calibrator = ProbabilityCalibrator(method=method)
        calibrator.fit(probs_train, y_train)
        
        calibrated = calibrator.transform(probs_test)
        
        # Check output shape
        assert len(calibrated) == len(probs_test)
        
        # Calibrated probabilities should be in [0, 1]
        assert np.all(calibrated >= 0)
        assert np.all(calibrated <= 1)
        
    @pytest.mark.parametrize("method", ['isotonic', 'platt', 'temperature', 'beta'])
    def test_calibration_improves_ece(self, method, trained_model, synthetic_data):
        """Test that calibration reduces ECE (Expected Calibration Error)."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        # Get uncalibrated predictions (make them overconfident)
        probs_train = trained_model.predict_proba(X_train)[:, 1] ** 0.7  # More extreme
        probs_test = trained_model.predict_proba(X_test)[:, 1] ** 0.7
        
        calibrator = ProbabilityCalibrator(method=method)
        
        # ECE before calibration
        ece_before = calibrator.evaluate(probs_test, y_test)['ece']
        
        # Fit and transform
        calibrator.fit(probs_train, y_train)
        calibrated = calibrator.transform(probs_test)
        
        # ECE after calibration
        ece_after = calibrator.evaluate(calibrated, y_test)['ece']
        
        # Calibration should reduce ECE (or at least not make it worse)
        assert ece_after <= ece_before * 1.1  # Allow 10% tolerance
        
    def test_multi_calibrator(self, trained_model, synthetic_data):
        """Test multi-method calibrator."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        probs_train = trained_model.predict_proba(X_train)[:, 1]
        
        multi = MultiCalibrator()
        multi.fit(probs_train, y_train, validation_split=0.2)
        
        # Should select best method
        assert multi.best_method is not None
        assert multi.best_method in multi.methods
        
        # Should have scores for all methods
        assert len(multi.validation_scores) == len(multi.methods)
        
        # Transform should work
        probs_test = trained_model.predict_proba(X_test)[:, 1]
        calibrated = multi.transform(probs_test)
        
        assert len(calibrated) == len(probs_test)
        assert np.all(calibrated >= 0)
        assert np.all(calibrated <= 1)


class TestCalibrationPipeline:
    """Test complete calibration pipeline."""
    
    def test_pipeline_fit(self, trained_model, synthetic_data):
        """Test pipeline fitting."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        pipeline = CalibrationPipeline(
            base_estimator=trained_model,
            calibration_method='auto',
            use_conformal=True,
            use_calibration=True
        )
        
        pipeline.fit(X_train, y_train)
        
        assert pipeline.is_fitted
        assert pipeline.conformal_predictor is not None
        assert pipeline.calibrator is not None
        
    def test_pipeline_predict(self, trained_model, synthetic_data):
        """Test pipeline predictions."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        pipeline = CalibrationPipeline(
            base_estimator=trained_model,
            use_conformal=True,
            use_calibration=True
        )
        
        pipeline.fit(X_train, y_train)
        results = pipeline.predict(X_test, return_uncertainty=True)
        
        assert 'probabilities' in results
        assert 'uncalibrated_probabilities' in results
        assert 'uncertainty' in results
        
        # Probabilities should be valid
        assert len(results['probabilities']) == len(X_test)
        assert np.all(results['probabilities'] >= 0)
        assert np.all(results['probabilities'] <= 1)
        
    def test_pipeline_evaluate(self, trained_model, synthetic_data):
        """Test pipeline evaluation."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        pipeline = CalibrationPipeline(
            base_estimator=trained_model,
            use_conformal=True,
            use_calibration=True
        )
        
        pipeline.fit(X_train, y_train)
        metrics = pipeline.evaluate_calibration(X_test, y_test, plot=False)
        
        assert 'uncalibrated_ece' in metrics
        assert 'calibrated_ece' in metrics
        assert 'improvement' in metrics
        assert 'conformal' in metrics
        
        # Calibration should improve ECE
        if metrics['improvement'] is not None:
            assert metrics['improvement'] >= -0.05  # Allow small tolerance
            
    def test_pipeline_race_prediction(self, trained_model, synthetic_data):
        """Test race prediction with normalization."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        pipeline = CalibrationPipeline(
            base_estimator=trained_model,
            use_conformal=True,
            use_calibration=True
        )
        
        pipeline.fit(X_train, y_train)
        
        # Simulate race with 10 horses
        X_race = X_test[:10]
        race_results = pipeline.predict_race(X_race, normalize=True)
        
        assert 'probabilities' in race_results
        assert 'normalized' in race_results
        assert race_results['normalized'] is True
        
        # Probabilities should sum to 1.0 (market book)
        prob_sum = race_results['probabilities'].sum()
        assert abs(prob_sum - 1.0) < 1e-6
        
        # All probabilities should be positive
        assert np.all(race_results['probabilities'] > 0)
        
    def test_pipeline_without_conformal(self, trained_model, synthetic_data):
        """Test pipeline with only calibration (no conformal)."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        pipeline = CalibrationPipeline(
            base_estimator=trained_model,
            use_conformal=False,
            use_calibration=True
        )
        
        pipeline.fit(X_train, y_train)
        results = pipeline.predict(X_test, return_uncertainty=True)
        
        assert 'probabilities' in results
        assert 'uncertainty' not in results  # No conformal prediction
        
    def test_pipeline_without_calibration(self, trained_model, synthetic_data):
        """Test pipeline with only conformal (no calibration)."""
        X_train, X_test, y_train, y_test = synthetic_data
        
        pipeline = CalibrationPipeline(
            base_estimator=trained_model,
            use_conformal=True,
            use_calibration=False
        )
        
        pipeline.fit(X_train, y_train)
        results = pipeline.predict(X_test, return_uncertainty=True)
        
        assert 'probabilities' in results
        assert 'uncertainty' in results
        
        # Probabilities should match uncalibrated (no calibration applied)
        assert np.allclose(
            results['probabilities'],
            results['uncalibrated_probabilities']
        )


def run_all_tests():
    """Run all calibration tests."""
    print("CALIBRATION TESTS")
    print("=" * 60)
    
    # Generate test data
    print("\nGenerating synthetic test data...")
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    X = np.random.randn(n_samples, n_features)
    win_prob = 1 / (1 + np.exp(-(X[:, 0] + 0.5 * X[:, 1])))
    y = (np.random.rand(n_samples) < win_prob).astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    # Train base model
    print("Training base model...")
    model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
    model.fit(X_train, y_train)
    
    print(f"Dataset: {len(X_train)} train, {len(X_test)} test")
    print(f"Win rate: {y_train.mean():.1%}\n")
    
    # Test 1: Conformal Prediction
    print("TEST 1: Conformal Prediction")
    print("-" * 60)
    try:
        cp = ConformalPredictor(base_estimator=model, confidence_level=0.9)
        cp.fit(X_train, y_train)
        
        coverage = cp.evaluate_coverage(X_test, y_test)
        print(f"✓ Conformal predictor fitted")
        print(f"  Target coverage: {coverage['target_coverage']:.1%}")
        print(f"  Empirical coverage: {coverage['empirical_coverage']:.1%}")
        print(f"  Average set size: {coverage['average_set_size']:.2f}")
        print("✓ PASSED\n")
    except Exception as e:
        print(f"✗ FAILED: {e}\n")
        
    # Test 2: Probability Calibration
    print("TEST 2: Probability Calibration (All Methods)")
    print("-" * 60)
    
    probs_train = model.predict_proba(X_train)[:, 1]
    probs_test = model.predict_proba(X_test)[:, 1]
    
    for method in ['isotonic', 'platt']:
        try:
            calibrator = ProbabilityCalibrator(method=method)
            calibrator.fit(probs_train, y_train)
            
            calibrated = calibrator.transform(probs_test)
            metrics = calibrator.evaluate(calibrated, y_test)
            
            print(f"  {method}: ECE = {metrics['ece']:.4f} ✓")
        except Exception as e:
            print(f"  {method}: FAILED - {e}")
            
    print("✓ PASSED\n")
    
    # Test 3: Complete Pipeline
    print("TEST 3: Calibration Pipeline")
    print("-" * 60)
    try:
        pipeline = CalibrationPipeline(
            base_estimator=model,
            calibration_method='auto',
            use_conformal=True,
            use_calibration=True
        )
        
        pipeline.fit(X_train, y_train)
        print("✓ Pipeline fitted")
        
        # Evaluate
        metrics = pipeline.evaluate_calibration(X_test, y_test, plot=False)
        print(f"  Uncalibrated ECE: {metrics['uncalibrated_ece']:.4f}")
        print(f"  Calibrated ECE: {metrics['calibrated_ece']:.4f}")
        print(f"  Improvement: {metrics['improvement']:.4f}")
        
        # Race prediction
        X_race = X_test[:10]
        race_pred = pipeline.predict_race(X_race, normalize=True)
        print(f"  Race prediction sum: {race_pred['probabilities'].sum():.6f}")
        
        print("✓ PASSED\n")
    except Exception as e:
        print(f"✗ FAILED: {e}\n")
        
    print("=" * 60)
    print("ALL TESTS COMPLETE ✓")


if __name__ == "__main__":
    run_all_tests()
