# Quantitative Pipeline Architecture - Part 3: Integration & Deployment
**Created:** November 9, 2025
**Status:** Production-Ready Design
**Purpose:** Production deployment and integration with qualitative pipeline

**Related Documents:**
- Part 1: Overview & Categories
- Part 2: Feature Engineering & ML Models
- FUSION_MODEL_ARCHITECTURE.md (for full integration details)

---

## 📋 Table of Contents

1. [Integration with Qualitative Pipeline](#integration)
2. [Backtesting Framework](#backtesting)
3. [API Endpoints](#api)
4. [Deployment Architecture](#deployment)
5. [Monitoring & Drift Detection](#monitoring)

---

## 🔗 1. Integration with Qualitative Pipeline {#integration}

### **Architecture Overview**

```
Master Taxonomy (Categories 1-21)
        ↓
        ├─→ Qualitative Pipeline (Cats 1-17)
        │   ├─ GPT-5 Deep Reasoning
        │   ├─ Claude Sonnet 4.5 Synthesis
        │   └─ Gemini 2.5 Flash Extraction
        │   → Likelihood Ratios (LRs)
        │
        └─→ Quantitative Pipeline (Cats 18-21)
            ├─ Speed Ratings
            ├─ Class Ratings
            ├─ Sectional Data
            └─ Pedigree Analysis
            → Base Probabilities (P_base)

            ↓

    Fusion Model (Bayesian Integration)
    P_final = P_base × LR_product (normalized)
            ↓
    Final Predictions + Confidence Intervals
```

### **Interface Specification**

#### **Quantitative Pipeline Output Format**

```python
QUANTITATIVE_OUTPUT_SCHEMA = {
    "race_id": "string (unique identifier)",
    "horse_id": "string",
    "horse_name": "string",

    # Base probabilities (calibrated)
    "win_prob_base": "float (0-1)",
    "place_prob_base": "float (0-1)",

    # Probability intervals (conformal prediction)
    "win_prob_lower": "float (0-1)",
    "win_prob_upper": "float (0-1)",
    "place_prob_lower": "float (0-1)",
    "place_prob_upper": "float (0-1)",

    # Model contributions
    "catboost_win": "float (0-1)",
    "lightgbm_win": "float (0-1)",
    "xgboost_win": "float (0-1)",

    # Feature importance (top 10)
    "top_features": [
        {"feature": "speed_class_ratio", "importance": 0.142},
        {"feature": "quant_triple_score", "importance": 0.128},
        # ... up to 10
    ],

    # Integration signals (for fusion)
    "speed_rating": "float (80-120)",
    "class_rating": "float (70-120)",
    "sectional_l200": "float (10.5-12.5)",
    "quant_triple_scenario": "elite|over_rated|under_rated|questionable|mixed",

    # Metadata
    "model_version": "string (e.g., 'v1.2.0')",
    "feature_version": "string (e.g., 'v1.0')",
    "calibration_group": "string (e.g., 'Flemington')",
    "prediction_timestamp": "ISO 8601 timestamp"
}
```

#### **Qualitative Pipeline Output Format**

```python
QUALITATIVE_OUTPUT_SCHEMA = {
    "race_id": "string",
    "horse_id": "string",
    "horse_name": "string",

    # Likelihood Ratios by category group
    "lr_form_fitness": "float (0.1-10.0)",  # Cats 1-3
    "lr_conditions": "float (0.1-10.0)",    # Cats 4-7
    "lr_tactics": "float (0.1-10.0)",       # Cats 8-14
    "lr_context": "float (0.1-10.0)",       # Cats 15-17

    # Combined LR (product)
    "lr_product": "float (0.01-100.0)",

    # Qualitative insights
    "key_strengths": ["string"],
    "key_concerns": ["string"],
    "race_narrative": "string (150-300 chars)",

    # Confidence
    "qualitative_confidence": "float (0-1)",

    # Metadata
    "model_chain": "GPT-5 → Claude Sonnet 4.5 → Gemini Flash",
    "prediction_timestamp": "ISO 8601 timestamp"
}
```

### **Fusion Interface**

```python
class FusionInterface:
    """
    Interface between quantitative and qualitative pipelines.
    """

    def __init__(self):
        self.quantitative_pipeline = QuantitativePredictorEnsemble()
        self.qualitative_pipeline = None  # Placeholder (see qual docs)

    async def predict_race(self, race_data: dict) -> dict:
        """
        Run both pipelines and return structured output for fusion.

        Args:
            race_data: {
                'race_id': 'FLE_20251109_R7',
                'horses': [...],
                'conditions': {...}
            }

        Returns:
            {
                'quantitative': [...],  # One entry per horse
                'qualitative': [...]    # One entry per horse
            }
        """
        # Run pipelines in parallel
        quant_task = asyncio.create_task(
            self._run_quantitative_pipeline(race_data)
        )
        qual_task = asyncio.create_task(
            self._run_qualitative_pipeline(race_data)
        )

        quant_predictions, qual_predictions = await asyncio.gather(
            quant_task, qual_task
        )

        return {
            'quantitative': quant_predictions,
            'qualitative': qual_predictions,
            'ready_for_fusion': True,
            'race_id': race_data['race_id']
        }

    async def _run_quantitative_pipeline(self, race_data: dict) -> list:
        """
        Execute quantitative pipeline for all horses in race.
        """
        predictions = []

        for horse in race_data['horses']:
            # Engineer features
            features = self.quantitative_pipeline.feature_engineer.engineer_all_features(
                horse_history=horse['history'],
                race_context=race_data['conditions']
            )

            # Predict with ensemble
            pred = self.quantitative_pipeline.predict(features.to_frame().T)

            # Add metadata
            pred.update({
                'race_id': race_data['race_id'],
                'horse_id': horse['id'],
                'horse_name': horse['name'],
                'speed_rating': features['speed_last_3_avg'],
                'class_rating': features['class_current'],
                'sectional_l200': features['sectional_l200_avg_l5'],
                'quant_triple_scenario': self._get_triple_scenario(features),
                'model_version': 'v1.0.0',
                'feature_version': 'v1.0',
                'calibration_group': race_data['conditions']['track'],
                'prediction_timestamp': datetime.utcnow().isoformat()
            })

            predictions.append(pred)

        return predictions

    async def _run_qualitative_pipeline(self, race_data: dict) -> list:
        """
        Execute qualitative pipeline (delegated to qual system).
        """
        # This would call the qualitative pipeline API
        # For now, placeholder
        return []

    def validate_for_fusion(self, quant_output: dict, qual_output: dict) -> bool:
        """
        Validate that both outputs are ready for fusion.
        """
        required_quant = ['win_prob_base', 'place_prob_base', 'horse_id']
        required_qual = ['lr_product', 'horse_id']

        quant_valid = all(k in quant_output for k in required_quant)
        qual_valid = all(k in qual_output for k in required_qual)

        # Match horse IDs
        ids_match = quant_output['horse_id'] == qual_output['horse_id']

        return quant_valid and qual_valid and ids_match
```

---

## 🧪 2. Backtesting Framework {#backtesting}

### **Walk-Forward Validation**

```python
class QuantitativeBacktester:
    """
    Backtest quantitative pipeline with walk-forward validation.
    """

    def __init__(
        self,
        model: QuantitativePredictorEnsemble,
        feature_store: QuantitativeFeatureStore
    ):
        self.model = model
        self.feature_store = feature_store
        self.results = []

    def run_backtest(
        self,
        start_date: str,
        end_date: str,
        train_window_days: int = 365,
        test_window_days: int = 30,
        retrain_frequency_days: int = 30
    ) -> dict:
        """
        Walk-forward validation with periodic retraining.

        Process:
        1. Train on last 365 days
        2. Test on next 30 days
        3. Move forward 30 days
        4. Retrain and repeat

        Returns:
            {
                'overall_metrics': {...},
                'by_track': {...},
                'by_class': {...},
                'predictions': [...]
            }
        """
        print(f"Starting backtest: {start_date} to {end_date}")
        print(f"Train window: {train_window_days} days, Test window: {test_window_days} days")

        current_date = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        iteration = 0

        while current_date < end:
            iteration += 1

            # Define train/test periods
            train_start = current_date - pd.Timedelta(days=train_window_days)
            train_end = current_date
            test_start = current_date
            test_end = current_date + pd.Timedelta(days=test_window_days)

            print(f"\nIteration {iteration}:")
            print(f"  Train: {train_start.date()} to {train_end.date()}")
            print(f"  Test: {test_start.date()} to {test_end.date()}")

            # Load data
            train_data = self.feature_store.load_features(
                train_start.strftime('%Y-%m-%d'),
                train_end.strftime('%Y-%m-%d')
            )
            test_data = self.feature_store.load_features(
                test_start.strftime('%Y-%m-%d'),
                test_end.strftime('%Y-%m-%d')
            )

            if len(test_data) == 0:
                print("  No test data available, skipping...")
                current_date += pd.Timedelta(days=retrain_frequency_days)
                continue

            # Train model
            X_train = train_data.drop(['race_id', 'horse_id', 'win', 'place'], axis=1)
            y_train_win = train_data['win']
            y_train_place = train_data['place']

            self.model.train(
                X_train, y_train_win, y_train_place,
                X_train, y_train_win, y_train_place  # Using same for simplicity
            )

            # Test model
            X_test = test_data.drop(['race_id', 'horse_id', 'win', 'place'], axis=1)
            y_test_win = test_data['win']
            y_test_place = test_data['place']

            predictions = self.model.predict(X_test)

            # Evaluate
            metrics = self._evaluate_predictions(
                predictions['win_prob'],
                predictions['place_prob'],
                y_test_win,
                y_test_place,
                test_data
            )

            self.results.append({
                'iteration': iteration,
                'test_start': test_start,
                'test_end': test_end,
                'n_races': len(test_data),
                'metrics': metrics
            })

            print(f"  Metrics: Win AUC={metrics['win_auc']:.3f}, Place AUC={metrics['place_auc']:.3f}")

            # Move to next window
            current_date += pd.Timedelta(days=retrain_frequency_days)

        # Aggregate results
        return self._aggregate_results()

    def _evaluate_predictions(
        self,
        win_preds: np.array,
        place_preds: np.array,
        win_actual: np.array,
        place_actual: np.array,
        test_data: pd.DataFrame
    ) -> dict:
        """
        Calculate comprehensive evaluation metrics.
        """
        from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss

        metrics = {
            # Win metrics
            'win_auc': roc_auc_score(win_actual, win_preds),
            'win_brier': brier_score_loss(win_actual, win_preds),
            'win_logloss': log_loss(win_actual, win_preds),
            'win_accuracy': ((win_preds > 0.5) == win_actual).mean(),

            # Place metrics
            'place_auc': roc_auc_score(place_actual, place_preds),
            'place_brier': brier_score_loss(place_actual, place_preds),
            'place_logloss': log_loss(place_actual, place_preds),
            'place_accuracy': ((place_preds > 0.5) == place_actual).mean(),

            # Calibration
            'calibration_error': self._calculate_calibration_error(
                win_preds, win_actual
            ),

            # Betting simulation
            'roi': self._simulate_betting_roi(
                win_preds, win_actual, test_data['win_odds']
            )
        }

        return metrics

    def _calculate_calibration_error(
        self,
        predictions: np.array,
        outcomes: np.array,
        n_bins: int = 10
    ) -> float:
        """
        Expected Calibration Error (ECE).
        """
        bins = np.linspace(0, 1, n_bins + 1)
        ece = 0.0

        for i in range(n_bins):
            mask = (predictions >= bins[i]) & (predictions < bins[i+1])
            if mask.sum() > 0:
                avg_pred = predictions[mask].mean()
                avg_actual = outcomes[mask].mean()
                ece += abs(avg_pred - avg_actual) * mask.sum()

        ece /= len(predictions)
        return ece

    def _simulate_betting_roi(
        self,
        predictions: np.array,
        outcomes: np.array,
        odds: np.array,
        kelly_fraction: float = 0.25
    ) -> float:
        """
        Simulate betting with Kelly criterion.

        Bet when: (odds * p - (1 - p)) / odds > 0
        Stake: kelly_fraction * bankroll * edge
        """
        bankroll = 1000.0
        bets_placed = 0

        for pred, outcome, odd in zip(predictions, outcomes, odds):
            # Calculate edge
            fair_odds = 1 / pred
            edge = (odd * pred - (1 - pred)) / odd

            if edge > 0.05:  # Minimum 5% edge
                # Kelly stake
                stake = kelly_fraction * bankroll * edge
                stake = min(stake, bankroll * 0.1)  # Max 10% per bet

                if outcome == 1:
                    bankroll += stake * (odd - 1)
                else:
                    bankroll -= stake

                bets_placed += 1

        roi = (bankroll - 1000) / 1000 * 100

        return roi if bets_placed > 0 else 0.0

    def _aggregate_results(self) -> dict:
        """
        Aggregate backtest results across all iterations.
        """
        df = pd.DataFrame([r['metrics'] for r in self.results])

        return {
            'overall_metrics': {
                'win_auc_mean': df['win_auc'].mean(),
                'win_auc_std': df['win_auc'].std(),
                'place_auc_mean': df['place_auc'].mean(),
                'place_auc_std': df['place_auc'].std(),
                'win_brier_mean': df['win_brier'].mean(),
                'place_brier_mean': df['place_brier'].mean(),
                'calibration_error_mean': df['calibration_error'].mean(),
                'roi_mean': df['roi'].mean(),
                'roi_std': df['roi'].std()
            },
            'iterations': self.results,
            'n_iterations': len(self.results)
        }
```

---

## 🚀 3. API Endpoints {#api}

### **FastAPI Implementation**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Quantitative Racing Analysis API", version="1.0.0")

# Initialize models (load from disk)
quantitative_pipeline = QuantitativePredictorEnsemble()
quantitative_pipeline.load_models('models/quantitative/v1.0.0')

feature_engineer = QuantitativeFeatureEngineer()


class RaceRequest(BaseModel):
    """Request schema for race prediction."""
    race_id: str
    track: str
    distance: int
    going: int  # 1-10 scale
    race_class: int
    horses: list[dict]  # Each horse has history + metadata


class PredictionResponse(BaseModel):
    """Response schema for predictions."""
    race_id: str
    predictions: list[dict]  # QUANTITATIVE_OUTPUT_SCHEMA format
    metadata: dict


@app.post("/api/v1/quantify", response_model=PredictionResponse)
async def quantify_race(request: RaceRequest):
    """
    **Quantitative Pipeline Endpoint**

    Generate base probabilities for all horses in a race using:
    - Speed ratings (Category 18)
    - Class ratings (Category 19)
    - Sectional data (Category 20)
    - Pedigree analysis (Category 21)
    - ML ensemble (CatBoost + LightGBM + XGBoost)
    - Calibration & uncertainty quantification

    Returns:
        Calibrated win/place probabilities with confidence intervals
    """
    try:
        predictions = []

        for horse in request.horses:
            # Engineer features
            features = feature_engineer.engineer_all_features(
                horse_history=horse['history'],
                race_context={
                    'track': request.track,
                    'distance': request.distance,
                    'going': request.going,
                    'class': request.race_class
                }
            )

            # Predict
            pred = quantitative_pipeline.predict(features.to_frame().T)

            # Format response
            pred.update({
                'race_id': request.race_id,
                'horse_id': horse['id'],
                'horse_name': horse['name'],
                'speed_rating': features['speed_last_3_avg'],
                'class_rating': features['class_current'],
                'sectional_l200': features['sectional_l200_avg_l5'],
                'model_version': 'v1.0.0',
                'prediction_timestamp': datetime.utcnow().isoformat()
            })

            predictions.append(pred)

        return PredictionResponse(
            race_id=request.race_id,
            predictions=predictions,
            metadata={
                'model_version': 'v1.0.0',
                'feature_version': 'v1.0',
                'n_horses': len(predictions)
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/features/{horse_id}")
async def get_horse_features(horse_id: str, race_context: dict):
    """
    **Feature Engineering Endpoint**

    Get engineered features for a specific horse (debugging/inspection).
    """
    try:
        # Load horse history
        horse_history = load_horse_history(horse_id)

        # Engineer features
        features = feature_engineer.engineer_all_features(
            horse_history=horse_history,
            race_context=race_context
        )

        return {
            'horse_id': horse_id,
            'features': features.to_dict(),
            'feature_names': feature_engineer.get_feature_names()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/model/status")
async def model_status():
    """
    **Model Health Check**

    Check model availability and metadata.
    """
    return {
        'status': 'healthy',
        'models_loaded': {
            'catboost_win': quantitative_pipeline.models['catboost_win'] is not None,
            'catboost_place': quantitative_pipeline.models['catboost_place'] is not None,
            'lightgbm_win': quantitative_pipeline.models['lightgbm_win'] is not None,
            'lightgbm_place': quantitative_pipeline.models['lightgbm_place'] is not None,
            'xgboost_win': quantitative_pipeline.models['xgboost_win'] is not None,
            'xgboost_place': quantitative_pipeline.models['xgboost_place'] is not None
        },
        'version': 'v1.0.0',
        'feature_count': len(feature_engineer.get_feature_names())
    }


@app.post("/api/v1/backtest")
async def run_backtest(start_date: str, end_date: str):
    """
    **Backtesting Endpoint**

    Run walk-forward validation on historical data.
    """
    try:
        backtester = QuantitativeBacktester(
            model=quantitative_pipeline,
            feature_store=QuantitativeFeatureStore()
        )

        results = backtester.run_backtest(
            start_date=start_date,
            end_date=end_date,
            train_window_days=365,
            test_window_days=30
        )

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## 🏗️ 4. Deployment Architecture {#deployment}

### **Infrastructure Design**

```
┌─────────────────────────────────────────────────────────────┐
│                     Production System                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Streamlit  │◄────────│   FastAPI    │                 │
│  │   Dashboard  │         │   Backend    │                 │
│  │  (Port 8501) │         │  (Port 8001) │                 │
│  └──────────────┘         └───────┬──────┘                 │
│         │                          │                        │
│         │                          ▼                        │
│         │                 ┌─────────────────┐              │
│         │                 │  Quantitative   │              │
│         │                 │    Pipeline     │              │
│         │                 │  - CatBoost     │              │
│         │                 │  - LightGBM     │              │
│         │                 │  - XGBoost      │              │
│         │                 │  - Calibration  │              │
│         │                 └────────┬────────┘              │
│         │                          │                        │
│         ▼                          ▼                        │
│  ┌──────────────────────────────────────┐                  │
│  │          DuckDB Data Warehouse       │                  │
│  │  - Raw race data                     │                  │
│  │  - Engineered features               │                  │
│  │  - Historical predictions            │                  │
│  │  - Performance metrics               │                  │
│  └──────────────────────────────────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### **Docker Deployment**

```dockerfile
# Dockerfile for Quantitative Pipeline
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY src/ src/
COPY models/ models/
COPY data/ data/

# Expose API port
EXPOSE 8001

# Run API server
CMD ["uvicorn", "src.api.quantitative_api:app", "--host", "0.0.0.0", "--port", "8001"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  quantitative_api:
    build: .
    ports:
      - "8001:8001"
    volumes:
      - ./models:/app/models:ro
      - ./data:/app/data:ro
    environment:
      - MODEL_VERSION=v1.0.0
      - FEATURE_VERSION=v1.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/v1/model/status"]
      interval: 30s
      timeout: 10s
      retries: 3

  dashboard:
    image: streamlit:latest
    ports:
      - "8501:8501"
    volumes:
      - ./dashboard:/app
    depends_on:
      - quantitative_api
```

---

## 📊 5. Monitoring & Drift Detection {#monitoring}

### **Performance Monitoring**

```python
class QuantitativeMonitor:
    """
    Monitor quantitative pipeline performance in production.
    """

    def __init__(self, db_path: str = 'data/monitoring.duckdb'):
        self.db = duckdb.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        """
        Create monitoring tables.
        """
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id VARCHAR PRIMARY KEY,
                race_id VARCHAR,
                horse_id VARCHAR,
                prediction_timestamp TIMESTAMP,
                win_prob FLOAT,
                place_prob FLOAT,
                win_actual BOOLEAN,
                place_actual BOOLEAN,
                model_version VARCHAR,
                latency_ms FLOAT
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS daily_metrics (
                date DATE PRIMARY KEY,
                n_predictions INT,
                win_auc FLOAT,
                place_auc FLOAT,
                win_brier FLOAT,
                place_brier FLOAT,
                calibration_error FLOAT,
                avg_latency_ms FLOAT
            )
        """)

    def log_prediction(self, prediction: dict):
        """
        Log a prediction to monitoring database.
        """
        self.db.execute("""
            INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?)
        """, [
            prediction['prediction_id'],
            prediction['race_id'],
            prediction['horse_id'],
            prediction['prediction_timestamp'],
            prediction['win_prob'],
            prediction['place_prob'],
            prediction['model_version'],
            prediction['latency_ms']
        ])

    def update_actual_outcomes(self, race_id: str, results: list):
        """
        Update predictions with actual outcomes after race.
        """
        for result in results:
            self.db.execute("""
                UPDATE predictions
                SET win_actual = ?, place_actual = ?
                WHERE race_id = ? AND horse_id = ?
            """, [
                result['win'],
                result['place'],
                race_id,
                result['horse_id']
            ])

    def calculate_daily_metrics(self, date: str):
        """
        Calculate and store daily performance metrics.
        """
        metrics = self.db.execute("""
            SELECT
                COUNT(*) as n_predictions,
                AVG(latency_ms) as avg_latency
            FROM predictions
            WHERE DATE(prediction_timestamp) = ?
                AND win_actual IS NOT NULL
        """, [date]).fetchone()

        # Calculate AUC, Brier, etc. (omitted for brevity)
        # ...

        self.db.execute("""
            INSERT INTO daily_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [date, metrics[0], None, None, None, None, None, metrics[1]])

    def detect_drift(self, lookback_days: int = 7) -> dict:
        """
        Detect model drift by comparing recent vs historical performance.
        """
        recent_metrics = self.db.execute("""
            SELECT AVG(win_auc), AVG(place_auc), AVG(calibration_error)
            FROM daily_metrics
            WHERE date >= DATE('now', '-{} days')
        """.format(lookback_days)).fetchone()

        historical_metrics = self.db.execute("""
            SELECT AVG(win_auc), AVG(place_auc), AVG(calibration_error)
            FROM daily_metrics
            WHERE date < DATE('now', '-{} days')
        """.format(lookback_days)).fetchone()

        drift_detected = (
            abs(recent_metrics[0] - historical_metrics[0]) > 0.05 or  # AUC drop > 5%
            abs(recent_metrics[2] - historical_metrics[2]) > 0.03      # Calibration error increase
        )

        return {
            'drift_detected': drift_detected,
            'recent_win_auc': recent_metrics[0],
            'historical_win_auc': historical_metrics[0],
            'recent_calibration_error': recent_metrics[2],
            'historical_calibration_error': historical_metrics[2],
            'recommendation': 'Retrain model' if drift_detected else 'No action needed'
        }
```

### **Alerting System**

```python
class AlertManager:
    """
    Send alerts when issues detected.
    """

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url

    def check_and_alert(self, monitor: QuantitativeMonitor):
        """
        Run daily checks and send alerts if needed.
        """
        # Check 1: Model drift
        drift_status = monitor.detect_drift(lookback_days=7)
        if drift_status['drift_detected']:
            self.send_alert(
                severity='WARNING',
                title='Model Drift Detected',
                message=f"AUC dropped from {drift_status['historical_win_auc']:.3f} to {drift_status['recent_win_auc']:.3f}",
                recommendation=drift_status['recommendation']
            )

        # Check 2: Prediction latency
        avg_latency = monitor.db.execute("""
            SELECT AVG(latency_ms)
            FROM predictions
            WHERE DATE(prediction_timestamp) = DATE('now')
        """).fetchone()[0]

        if avg_latency > 500:  # More than 500ms
            self.send_alert(
                severity='WARNING',
                title='High Latency Detected',
                message=f"Average prediction latency: {avg_latency:.0f}ms",
                recommendation='Check model server resources'
            )

        # Check 3: Calibration quality
        recent_cal_error = monitor.db.execute("""
            SELECT calibration_error
            FROM daily_metrics
            ORDER BY date DESC
            LIMIT 1
        """).fetchone()[0]

        if recent_cal_error > 0.10:
            self.send_alert(
                severity='ERROR',
                title='Calibration Degradation',
                message=f"Calibration error: {recent_cal_error:.3f} (threshold: 0.10)",
                recommendation='Recalibrate models immediately'
            )

    def send_alert(self, severity: str, title: str, message: str, recommendation: str):
        """
        Send alert to monitoring system (Slack, email, etc.)
        """
        if self.webhook_url:
            import requests

            payload = {
                'severity': severity,
                'title': title,
                'message': message,
                'recommendation': recommendation,
                'timestamp': datetime.utcnow().isoformat()
            }

            requests.post(self.webhook_url, json=payload)
        else:
            print(f"[{severity}] {title}: {message} → {recommendation}")
```

---

## 🎯 Success Criteria

### **Production Readiness Checklist**

- [x] Feature engineering pipeline (100+ features)
- [x] ML ensemble (CatBoost + LightGBM + XGBoost)
- [x] Calibration (isotonic regression per track group)
- [x] Uncertainty quantification (conformal prediction)
- [x] Integration interface (structured output for fusion)
- [x] Backtesting framework (walk-forward validation)
- [x] API endpoints (FastAPI with health checks)
- [x] Deployment architecture (Docker + docker-compose)
- [x] Monitoring system (drift detection, alerting)

### **Performance Targets**

| Metric | Target | Production Threshold |
|--------|--------|---------------------|
| Win AUC | >0.75 | >0.72 |
| Place AUC | >0.70 | >0.68 |
| Win Brier Score | <0.20 | <0.22 |
| Calibration Error | <0.05 | <0.08 |
| Prediction Latency | <200ms | <500ms |
| ROI (backtest) | >5% | >3% |

### **Integration Success**

- [ ] Quantitative output format matches fusion model input requirements
- [ ] Base probabilities are well-calibrated (ECE < 0.05)
- [ ] Confidence intervals provide 90%+ coverage
- [ ] Integration Matrix C signals correctly extracted
- [ ] API uptime >99.5% over 30 days

---

**End of Part 3 - Quantitative Pipeline Complete**

**Next Steps:**
1. Implement Fusion Model Architecture (combines qual + quant)
2. Update Phase 1 Roadmap with pipeline assignments
3. Begin implementation (Week 1: Data warehouse setup)
