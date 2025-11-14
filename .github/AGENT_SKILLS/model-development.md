# Agent Skill: Model Development

## Purpose
Handle machine learning tasks: feature engineering, model training, evaluation, and optimization.

## When to Use
- "Use model-development skill: Create features for..."
- "Use model-development skill: Train a model for..."
- "Use model-development skill: Evaluate model performance..."
- "Use model-development skill: Optimize hyperparameters..."

## Typical Workflow

1. **Exploration Phase**
   - Review existing features in `src/features/`
   - Check trained models in `models/trained/`
   - Examine `docs/quantitative-pipeline/` for design
   - Look at CatBoost configs in `catboost_info/`

2. **Feature Engineering**
   - Create features following existing patterns
   - Use DuckDB for efficient aggregations
   - Document feature rationale and calculations
   - Add feature validation tests

3. **Model Training**
   - Use CatBoost as primary model (already configured)
   - Set up proper train/val/test splits
   - Log training metrics and losses
   - Save trained models with metadata

4. **Evaluation**
   - Calculate relevant metrics (ROI, accuracy, calibration)
   - Create visualizations (confusion matrix, learning curves)
   - Compare against baseline models
   - Document assumptions and limitations

5. **Deployment**
   - Version trained models with git/DVC
   - Create prediction interfaces
   - Test edge cases and data drift
   - Monitor performance in production

## Code Patterns to Follow

```python
# Feature creation with DuckDB
import duckdb
conn = duckdb.connect('data/racing.duckdb')
features = conn.execute("""
    SELECT 
        race_id,
        AVG(barrier) as avg_barrier,
        MAX(weight) as max_weight
    FROM races
    GROUP BY race_id
""").fetchall()

# Model training
from catboost import CatBoostClassifier
model = CatBoostClassifier(
    iterations=100,
    depth=6,
    learning_rate=0.1,
    verbose=True
)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)])

# Evaluation
from sklearn.metrics import accuracy_score, roc_auc_score
preds = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, preds)}")
```

## Key Files
- `src/features/` - Feature engineering modules
- `src/models/` - Model training and prediction
- `models/trained/` - Saved model artifacts
- `docs/quantitative-pipeline/` - Design documentation
- `data/racing.duckdb` - Main data warehouse

## Common Tasks

### Create New Feature
- [ ] Write feature calculation in `src/features/`
- [ ] Add validation tests
- [ ] Document calculation and rationale
- [ ] Update feature manifest if needed
- [ ] Test on full dataset

### Train New Model
- [ ] Prepare train/val/test splits
- [ ] Configure CatBoost parameters
- [ ] Train with eval set for early stopping
- [ ] Evaluate on test set
- [ ] Save model with metadata (date, metrics, params)

### Optimize Model
- [ ] Run hyperparameter grid search
- [ ] Compare model variants
- [ ] Analyze feature importance
- [ ] Document changes and rationale
- [ ] Update model documentation

## Success Criteria
- ✅ Features are well-documented and validated
- ✅ Model metrics meet or exceed baseline
- ✅ Code is reproducible (seeded RNG, documented params)
- ✅ Edge cases are handled gracefully
- ✅ Performance is monitored and logged
- ✅ Results are interpretable and explainable
