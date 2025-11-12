# Master Taxonomy - Part 25: Common Pitfalls, Troubleshooting & Best Practices

**Document Purpose:** Avoid common mistakes and resolve typical implementation issues
**Usage:** Reference when encountering problems

---

## COMMON PITFALLS & SOLUTIONS

### PITFALL 1: Missing Data / NaN Errors

**Problem:** Categories return `None` or `NaN` values, breaking feature engineering

**Causes:**
- Race scraped before all data available
- Website structure changed
- Authentication failed (barrier trials)
- Horse has no historical data (first start)

**Solutions:**
```python
# 1. Implement defensive coding
def safe_get_feature(data, key, default=0):
    """Safely extract feature with fallback"""
    try:
        value = data.get(key)
        return value if value is not None else default
    except:
        return default

# 2. Handle missing data explicitly
def engineer_features_with_fallback(horse_data):
    """Feature engineering with missing data handling"""

    features = {}

    # Historical performance (can be missing for first-starters)
    if horse_data.get('career_starts', 0) == 0:
        features['form_score'] = 50  # Neutral score for first-starters
        features['career_win_pct'] = 0.10  # Industry average
    else:
        features['form_score'] = calculate_form_score(horse_data)
        features['career_win_pct'] = horse_data['career_wins'] / horse_data['career_starts']

    # Speed ratings (can be missing)
    if horse_data.get('timeform_rating') is None:
        features['timeform_rating'] = estimate_rating_from_form(horse_data)
        features['rating_estimated'] = True
    else:
        features['timeform_rating'] = horse_data['timeform_rating']
        features['rating_estimated'] = False

    return features

# 3. Data quality checks
def validate_data_completeness(race_data):
    """Check data quality before prediction"""

    required_fields = [
        'venue', 'distance', 'track_condition', 'barrier',
        'weight', 'jockey', 'trainer'
    ]

    missing = [f for f in required_fields if race_data.get(f) is None]

    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    return True
```

**Best Practice:**
- Always provide default/fallback values
- Log missing data (track quality issues)
- Never crash on missing data (degrade gracefully)

---

### PITFALL 2: Authentication Failures (Barrier Trials)

**Problem:** Selenium authentication fails, can't access Racing.com trials

**Causes:**
- Cookies expired
- Website anti-bot detection
- Rate limiting
- Login credentials changed

**Solutions:**
```python
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def authenticate_racing_com(driver, max_retries=3):
    """Authenticate with Racing.com (with retries)"""

    for attempt in range(max_retries):
        try:
            # Navigate to login
            driver.get("https://www.racing.com/login")
            time.sleep(2)  # Anti-detection delay

            # Enter credentials
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")

            username_field.send_keys(os.getenv("RACING_COM_USERNAME"))
            password_field.send_keys(os.getenv("RACING_COM_PASSWORD"))

            # Submit
            submit_button = driver.find_element(By.ID, "submit")
            submit_button.click()

            time.sleep(3)

            # Verify login success
            if "logout" in driver.page_source.lower():
                print("Authentication successful")

                # Save cookies for reuse
                cookies = driver.get_cookies()
                save_cookies(cookies)

                return True

        except TimeoutException:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(5)  # Longer delay before retry

    return False

def save_cookies(cookies):
    """Save cookies for future sessions"""
    import pickle
    with open('racing_com_cookies.pkl', 'wb') as f:
        pickle.dump(cookies, f)

def load_cookies(driver):
    """Load saved cookies"""
    import pickle
    try:
        with open('racing_com_cookies.pkl', 'rb') as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        return True
    except FileNotFoundError:
        return False
```

**Best Practice:**
- Save and reuse cookies (reduce authentication frequency)
- Implement exponential backoff retries
- Use residential proxies if blocked
- Monitor authentication success rate (alert if <80%)

---

### PITFALL 3: Overfitting ML Models

**Problem:** Model performs excellently on training data (90%+) but poorly on test data (60%)

**Causes:**
- Too many features relative to data
- Model complexity too high
- Data leakage (future info in training)
- Not enough training data

**Solutions:**
```python
from sklearn.model_selection import cross_val_score, TimeSeriesSplit

def prevent_overfitting(X_train, y_train, X_test, y_test):
    """Strategies to prevent overfitting"""

    # 1. Cross-validation (not just train/test split)
    tscv = TimeSeriesSplit(n_splits=5)  # Respect temporal order
    cv_scores = cross_val_score(model, X_train, y_train, cv=tscv, scoring='accuracy')

    print(f"CV scores: {cv_scores}")
    print(f"CV mean: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

    # 2. Feature selection (reduce dimensionality)
    from sklearn.feature_selection import SelectKBest, f_classif

    selector = SelectKBest(f_classif, k=50)  # Top 50 features
    X_train_selected = selector.fit_transform(X_train, y_train)
    X_test_selected = selector.transform(X_test)

    # 3. Regularization (penalize complexity)
    from sklearn.linear_model import LogisticRegression

    model = LogisticRegression(C=0.1, penalty='l2')  # Strong regularization

    # 4. Early stopping (for neural networks)
    from tensorflow.keras.callbacks import EarlyStopping

    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    # 5. Ensemble with cross-validation
    from sklearn.ensemble import RandomForestClassifier

    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,  # Limit tree depth
        min_samples_split=20,  # Require minimum samples to split
        max_features='sqrt'  # Random feature sampling
    )

    return model

# 6. Check for data leakage
def detect_data_leakage(X_train, X_test):
    """Detect if future information leaked into training"""

    # Check for identical rows (should not happen with time series)
    train_set = set(map(tuple, X_train.values))
    test_set = set(map(tuple, X_test.values))

    overlap = train_set.intersection(test_set)

    if len(overlap) > 0:
        print(f"WARNING: {len(overlap)} identical rows in train and test!")

    return len(overlap) == 0
```

**Best Practice:**
- Use time-series cross-validation (not random splits)
- Monitor train vs validation accuracy gap (<10% difference)
- Feature selection (remove low-importance features)
- Regularization (L1/L2 penalties)
- Ensemble methods (reduce variance)

---

### PITFALL 4: Slow API Response Times

**Problem:** API takes >5 seconds per race prediction

**Causes:**
- Database queries not optimized
- No caching
- Synchronous operations (waiting for each step)
- Feature engineering too slow

**Solutions:**
```python
import redis
from functools import lru_cache
import asyncio

# 1. Database indexing
# Add indexes to PostgreSQL:
"""
CREATE INDEX idx_races_date ON races(race_date);
CREATE INDEX idx_horses_name ON horses(horse_name);
CREATE INDEX idx_jockey ON horses(jockey);
CREATE INDEX idx_trainer ON horses(trainer);
"""

# 2. Caching (Redis)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def predict_race_with_cache(race_id):
    """Predict race with caching"""

    # Check cache first
    cached = redis_client.get(f"prediction:{race_id}")
    if cached:
        return json.loads(cached)

    # Compute prediction
    prediction = predict_race(race_id)

    # Cache result (expire after 1 hour)
    redis_client.setex(
        f"prediction:{race_id}",
        3600,  # 1 hour TTL
        json.dumps(prediction)
    )

    return prediction

# 3. Asynchronous operations
async def fetch_all_data_async(race_id):
    """Fetch all data concurrently"""

    tasks = [
        fetch_race_metadata(race_id),
        fetch_track_conditions(race_id),
        fetch_market_data(race_id),
        fetch_weather_data(race_id)
    ]

    results = await asyncio.gather(*tasks)

    return {
        'metadata': results[0],
        'conditions': results[1],
        'market': results[2],
        'weather': results[3]
    }

# 4. Pre-compute expensive features
@lru_cache(maxsize=1000)
def get_jockey_statistics(jockey_name):
    """Cache jockey stats (rarely change)"""
    return calculate_jockey_stats(jockey_name)

# 5. Vectorized feature engineering
import numpy as np
import pandas as pd

def engineer_features_vectorized(horses_df):
    """Vectorized operations (faster than loops)"""

    # Instead of:
    # for horse in horses:
    #     features['weight_burden'] = (horse['weight'] - 54) * 0.01

    # Use vectorized:
    horses_df['weight_burden'] = (horses_df['weight'] - 54) * 0.01

    return horses_df
```

**Best Practice:**
- Database: Add indexes, use connection pooling
- Caching: Redis for frequent queries
- Async: Fetch data concurrently
- Pre-compute: Cache expensive calculations
- Vectorize: Use pandas/numpy (not Python loops)

**Target:** <2 seconds per race prediction

---

### PITFALL 5: Inconsistent Predictions (Same Race, Different Results)

**Problem:** Running prediction twice on same race gives different results

**Causes:**
- Live data changing (odds, weather)
- Random seed not set (ML models)
- Non-deterministic operations
- Race conditions (concurrent access)

**Solutions:**
```python
import numpy as np
import random
import tensorflow as tf

# 1. Set random seeds
def set_random_seeds(seed=42):
    """Ensure reproducible results"""
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)

set_random_seeds(42)

# 2. Snapshot data at prediction time
def predict_race_snapshot(race_id):
    """Snapshot all data at prediction time"""

    # Capture current state
    snapshot = {
        'race_data': fetch_race_data(race_id),
        'market_data': fetch_market_data(race_id),  # Current odds
        'weather_data': fetch_weather_data(race_id),  # Current weather
        'timestamp': datetime.now()
    }

    # Store snapshot
    save_snapshot(race_id, snapshot)

    # Predict from snapshot (not live data)
    prediction = predict_from_snapshot(snapshot)

    return prediction

# 3. Version predictions
def version_prediction(race_id, prediction):
    """Version predictions for auditability"""

    prediction_record = {
        'race_id': race_id,
        'prediction': prediction,
        'timestamp': datetime.now(),
        'data_version': get_data_version(),
        'model_version': get_model_version()
    }

    save_prediction_record(prediction_record)
```

**Best Practice:**
- Set random seeds for reproducibility
- Snapshot data at prediction time (don't requery live data)
- Version predictions (track what data/model was used)
- Lock predictions once made (don't update after bet placed)

---

## TROUBLESHOOTING GUIDE

### Issue: Low Prediction Accuracy (<60%)

**Diagnosis:**
```python
def diagnose_low_accuracy(predictions, actuals):
    """Identify accuracy issues"""

    # Check by category
    for category in categories:
        category_accuracy = calculate_category_accuracy(predictions, actuals, category)
        print(f"{category}: {category_accuracy:.2%}")

    # Check for biases
    print("\nBias Analysis:")
    print(f"Favorites bias: {favorites_accuracy - non_favorites_accuracy:.2%}")
    print(f"Venue bias: {best_venue_accuracy - worst_venue_accuracy:.2%}")
```

**Common Causes & Fixes:**
1. **Overfitting:** Reduce model complexity, add regularization
2. **Missing critical category:** Implement speed ratings, historical performance
3. **Integration issues:** Check category cross-interactions
4. **Data quality:** Validate data completeness, accuracy

---

### Issue: API Timeouts

**Diagnosis:**
```python
import time

def profile_api_performance():
    """Profile API bottlenecks"""

    start = time.time()

    t1 = time.time()
    data = fetch_race_data(race_id)
    print(f"Data fetch: {time.time() - t1:.2f}s")

    t2 = time.time()
    features = engineer_features(data)
    print(f"Feature engineering: {time.time() - t2:.2f}s")

    t3 = time.time()
    prediction = model.predict(features)
    print(f"Model prediction: {time.time() - t3:.2f}s")

    print(f"Total: {time.time() - start:.2f}s")
```

**Common Causes & Fixes:**
1. **Slow database queries:** Add indexes, optimize queries
2. **No caching:** Implement Redis caching
3. **Synchronous operations:** Use async/await
4. **Large model:** Optimize model size, use quantization

---

**Document Complete: Part 25 (Troubleshooting & Best Practices)**
**Next: Part 26 (Final Summary & Master Checklist)**
