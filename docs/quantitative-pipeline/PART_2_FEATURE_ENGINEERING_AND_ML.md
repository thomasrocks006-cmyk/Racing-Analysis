# Quantitative Pipeline Architecture - Part 2: Feature Engineering & ML Models
**Created:** November 9, 2025
**Status:** Production-Ready Design
**Purpose:** ML feature engineering and model training for Categories 18-21

**Related Documents:**
- Part 1: Overview & Categories
- Part 3: Integration & Deployment
- Integration Matrix C: PART_18 (quantitative synergies)

---

## 📋 Table of Contents

1. [Feature Engineering Strategy](#feature-engineering)
2. [Integration Matrix C Implementation](#integration-matrix-c)
3. [Feature Store Design](#feature-store)
4. [ML Model Architecture](#ml-models)
5. [Calibration & Uncertainty](#calibration)

---

## 🔧 1. Feature Engineering Strategy {#feature-engineering}

### **Feature Engineering Philosophy**

```
Raw Categories (18-21) → Derived Features (100+) → ML Models → Predictions

Key Principles:
1. **Domain Knowledge First**: Use racing expertise to guide feature creation
2. **Recency Weighting**: Recent form > distant history (exponential decay)
3. **Context Awareness**: Same speed rating means different things at different classes
4. **Interaction Terms**: Speed × Class, Sectionals × Pace, etc.
5. **No Data Leakage**: Strict time-ordering, only past data available at prediction time
```

### **Feature Categories**

#### **A. Base Features** (from Categories 18-21 directly)
```python
BASE_FEATURES = {
    # Speed Ratings (18)
    'speed_last_3_avg': 'Recent avg speed rating (L3)',
    'speed_best_l10': 'Peak speed rating (L10)',
    'speed_at_distance': 'Speed at today's distance',
    'speed_at_going': 'Speed on today's going',
    'speed_consistency': 'Speed rating std dev',
    'days_since_peak_speed': 'Days since peak performance',
    'speed_vs_class': 'Speed relative to race class',

    # Class Ratings (19)
    'class_drop': 'Class rise/drop vs last start',
    'class_peak': 'Peak class achieved',
    'class_ceiling': 'Estimated class ceiling',
    'class_win_rate_at_level': 'Win rate at this class',
    'class_trend_improving': 'Class trajectory (binary)',
    'days_since_this_class': 'Recency at this level',

    # Sectional Data (20)
    'sectional_l200_avg_l5': 'Recent finishing speed',
    'sectional_l200_best_l10': 'Peak finishing speed',
    'sectional_l200_at_distance': 'Finishing speed at distance',
    'closing_ability_score': 'Percentile closing ability',
    'pace_profile_closer': 'Closer profile (binary)',
    'pace_profile_presser': 'Presser profile (binary)',
    'sectional_rank_progression': 'Avg rank improvement',
    'acceleration_avg': 'Acceleration metric',

    # Pedigree (21)
    'pedigree_distance_suit': 'Bloodline distance fit (0-1)',
    'pedigree_surface_suit': 'Bloodline surface fit (0-1)',
    'pedigree_going_suit': 'Bloodline going fit (0-1)',
    'sire_progeny_win_rate': 'Sire's progeny success',
    'genetic_stamina_index': 'Stamina genetics (0-1)',
    'genetic_speed_index': 'Speed genetics (0-1)',
    'first_time_distance': 'First time at distance (binary)'
}
```

#### **B. Interaction Features** (Integration Matrix C synergies)

```python
def engineer_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create interaction terms based on Integration Matrix C.

    Key Interactions:
    1. Speed × Class (over/under-rated detection)
    2. Speed × Class × Sectionals (quantitative triple - gold standard)
    3. Sectionals × Pace (closing ability validation)
    4. Pedigree × Distance (young horse optimization)
    5. Class × Going (class adjustment for conditions)
    """
    features = pd.DataFrame(index=df.index)

    # 1. Speed × Class Matrix
    # If speed rating high BUT class low → over-rated (risky)
    # If speed rating low BUT class high → under-rated (value)
    features['speed_class_ratio'] = df['speed_last_3_avg'] / df['class_current'].clip(lower=50)
    features['speed_class_mismatch'] = (
        (df['speed_last_3_avg'] - 100) - (df['class_current'] - 85)
    ).abs()

    # 2. Quantitative Triple: Speed × Class × Sectionals
    # The "gold standard" integration (PART_18)
    features['quant_triple_score'] = (
        df['speed_last_3_avg'] * 0.35 +
        df['class_current'] * 0.30 +
        (100 - df['sectional_l200_avg_l5'] * 8) * 0.35  # Convert time to score
    )

    # Normalize to 0-100 scale
    features['quant_triple_score'] = (
        (features['quant_triple_score'] - features['quant_triple_score'].min()) /
        (features['quant_triple_score'].max() - features['quant_triple_score'].min()) * 100
    )

    # 3. Sectionals × Pace Profile
    # Closers with fast L200m = dangerous
    # Front runners with fast L200m = stamina
    features['closing_power'] = (
        df['closing_ability_score'] * df['pace_profile_closer'] * 1.2 +
        df['closing_ability_score'] * df['pace_profile_presser'] * 1.0 +
        df['closing_ability_score'] * df['pace_profile_front_runner'] * 0.8
    )

    # 4. Pedigree × Distance × First-Time
    # If first time at distance, pedigree becomes critical
    features['pedigree_weight'] = (
        df['pedigree_distance_suit'] * df['first_time_distance'] * 2.0 +
        df['pedigree_distance_suit'] * (1 - df['first_time_distance']) * 0.5
    )

    # 5. Class × Going Adjustment
    # Heavy tracks favor certain class levels
    features['class_going_interaction'] = (
        df['class_current'] * df['pedigree_going_suit']
    )

    # 6. Speed × Sectionals (finishing kick validation)
    # High speed + fast L200m = elite
    features['speed_sectional_elite'] = (
        (df['speed_last_3_avg'] > 110).astype(int) *
        (df['sectional_l200_avg_l5'] < 11.5).astype(int)
    )

    # 7. Class Drop × Speed (class drop advantage)
    # Dropping in class with good speed = strong chance
    features['class_drop_advantage'] = (
        (df['class_drop'] > 5) *  # Dropping 5+ points
        (df['speed_vs_class'] > 3)  # Speed exceeds class expectation
    ).astype(float) * df['speed_last_3_avg'] / 10

    return features
```

#### **C. Temporal Features** (recency & trajectory)

```python
def engineer_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-based features: trajectories, decay, freshness.
    """
    features = pd.DataFrame(index=df.index)

    # 1. Speed Rating Trajectory (last 5 starts)
    # Positive slope = improving, negative = declining
    for idx in df.index:
        recent_speeds = df.loc[idx, ['speed_-1', 'speed_-2', 'speed_-3', 'speed_-4', 'speed_-5']]
        if recent_speeds.notna().all():
            x = np.arange(5)
            slope, _ = np.polyfit(x, recent_speeds.values, 1)
            features.loc[idx, 'speed_trajectory'] = slope
        else:
            features.loc[idx, 'speed_trajectory'] = 0.0

    # 2. Class Progression (improving/stable/declining)
    for idx in df.index:
        recent_classes = df.loc[idx, ['class_-1', 'class_-2', 'class_-3', 'class_-4', 'class_-5']]
        if recent_classes.notna().all():
            x = np.arange(5)
            slope, _ = np.polyfit(x, recent_classes.values, 1)
            features.loc[idx, 'class_trajectory'] = slope
        else:
            features.loc[idx, 'class_trajectory'] = 0.0

    # 3. Sectional Improvement (getting faster?)
    for idx in df.index:
        recent_sectionals = df.loc[idx, ['sectional_-1', 'sectional_-2', 'sectional_-3']]
        if recent_sectionals.notna().all():
            features.loc[idx, 'sectional_improving'] = (
                recent_sectionals.iloc[-1] < recent_sectionals.iloc[0]
            ).astype(float)
        else:
            features.loc[idx, 'sectional_improving'] = 0.0

    # 4. Days Since Last Run (freshness)
    features['days_since_last'] = df['days_since_last_start']
    features['optimal_gap'] = (
        (features['days_since_last'] >= 14) &
        (features['days_since_last'] <= 28)
    ).astype(float)

    # 5. Exponential Recency Weighting (for averaging)
    # Last start weight = 0.5, -2 = 0.3, -3 = 0.2
    weights = [0.5, 0.3, 0.2]
    features['speed_weighted_avg'] = (
        df['speed_-1'] * weights[0] +
        df['speed_-2'] * weights[1] +
        df['speed_-3'] * weights[2]
    )

    return features
```

#### **D. Contextual Features** (race-specific adjustments)

```python
def engineer_contextual_features(df: pd.DataFrame, race_context: dict) -> pd.DataFrame:
    """
    Create features that depend on race context.

    Args:
        race_context: {
            'track': 'Flemington',
            'distance': 1600,
            'going': 4,
            'class': 95,
            'field_size': 14
        }
    """
    features = pd.DataFrame(index=df.index)

    # 1. Distance Optimization Score
    # How well does horse's profile match today's distance?
    optimal_distance = df['optimal_distance']  # Estimated from history
    features['distance_optimization'] = 1.0 - (
        abs(race_context['distance'] - optimal_distance) / 1000
    ).clip(0, 1)

    # 2. Going Suitability (historical + pedigree combined)
    # If horse has form on this going, use history
    # Else, rely on pedigree
    features['going_suitability'] = np.where(
        df['races_at_this_going'] > 2,
        df['win_rate_this_going'] * 100,  # Historical data available
        df['pedigree_going_suit'] * 80    # Pedigree fallback
    )

    # 3. Class Fit Score
    # Is today's class within horse's competitive range?
    features['class_fit'] = np.where(
        (race_context['class'] >= df['class_current'] - 5) &
        (race_context['class'] <= df['class_ceiling']),
        1.0,  # Within competitive range
        0.5   # Outside comfort zone
    )

    # 4. Field Size Effect
    # Large fields favor certain profiles (closers)
    # Small fields favor leaders
    features['field_size_advantage'] = (
        (race_context['field_size'] >= 12) *
        df['pace_profile_closer'] * 1.2 +
        (race_context['field_size'] < 10) *
        df['pace_profile_front_runner'] * 1.2
    )

    # 5. Track-Specific Performance
    # Has horse won at this track before?
    features['track_winner'] = df[f'wins_at_{race_context["track"]}'].fillna(0)
    features['track_performance'] = df[f'avg_finish_{race_context["track"]}'].fillna(6.0)

    return features
```

### **Feature Engineering Pipeline**

```python
class QuantitativeFeatureEngineer:
    """
    Master feature engineering pipeline for Categories 18-21.
    """

    def __init__(self):
        self.speed_engine = SpeedRatingEngine()
        self.class_engine = ClassRatingEngine()
        self.sectional_analyzer = SectionalAnalyzer()
        self.pedigree_analyzer = PedigreeAnalyzer()

    def engineer_all_features(
        self,
        horse_history: pd.DataFrame,
        race_context: dict
    ) -> pd.DataFrame:
        """
        Generate complete feature set for ML models.

        Pipeline:
        1. Extract base features from Categories 18-21
        2. Create interaction features (Matrix C)
        3. Engineer temporal features (trajectories)
        4. Add contextual features (race-specific)
        5. Validate & clean (no nulls, no leakage)

        Returns:
            DataFrame with 100+ features per horse
        """
        # Step 1: Base features from each category
        speed_features = self.speed_engine.engineer_speed_features(horse_history)
        class_features = self.class_engine.engineer_class_features(
            horse_history,
            race_context['class']
        )
        sectional_features = self.sectional_analyzer.engineer_sectional_features(
            horse_history
        )
        pedigree_features = self.pedigree_analyzer.engineer_pedigree_features(
            {'sire': horse_history['sire'].iloc[0], 'dam': horse_history['dam'].iloc[0]},
            race_context
        )

        # Combine base features
        base_features = pd.concat([
            speed_features,
            pd.Series(class_features),
            pd.Series(sectional_features),
            pd.Series(pedigree_features)
        ])

        # Step 2: Interaction features
        # Convert to DataFrame for interaction calculations
        df_for_interactions = pd.DataFrame([base_features])
        interaction_features = engineer_interaction_features(df_for_interactions).iloc[0]

        # Step 3: Temporal features
        temporal_features = engineer_temporal_features(
            self._prepare_temporal_df(horse_history)
        ).iloc[0]

        # Step 4: Contextual features
        contextual_features = engineer_contextual_features(
            df_for_interactions,
            race_context
        ).iloc[0]

        # Step 5: Combine all features
        all_features = pd.concat([
            base_features,
            interaction_features,
            temporal_features,
            contextual_features
        ])

        # Step 6: Validate
        all_features = self._validate_features(all_features)

        return all_features

    def _validate_features(self, features: pd.Series) -> pd.Series:
        """
        Validate feature quality: no nulls, no inf, reasonable ranges.
        """
        # Fill nulls with sensible defaults
        features = features.fillna(0)

        # Clip extreme values
        features = features.clip(-1000, 1000)

        # Replace inf with large finite values
        features = features.replace([np.inf, -np.inf], [1000, -1000])

        return features

    def get_feature_names(self) -> list:
        """
        Return list of all feature names for ML model training.
        """
        return [
            # Speed features (18)
            'speed_last_3_avg', 'speed_best_l10', 'speed_at_distance',
            'speed_at_going', 'speed_consistency', 'days_since_peak_speed',
            'speed_vs_class', 'speed_trajectory', 'speed_weighted_avg',

            # Class features (19)
            'class_drop', 'class_peak', 'class_current', 'class_ceiling',
            'class_trend_improving', 'class_trend_declining', 'class_competitive',
            'class_win_rate_at_level', 'class_place_rate_at_level',
            'days_since_this_class', 'class_trajectory', 'class_fit',

            # Sectional features (20)
            'sectional_l200_avg_l5', 'sectional_l200_best_l10',
            'sectional_l200_at_distance', 'sectional_l200_consistency',
            'closing_ability_score', 'pace_profile_closer',
            'pace_profile_presser', 'pace_profile_front_runner',
            'pace_profile_sustained', 'sectional_rank_progression',
            'acceleration_avg', 'sectional_improving',

            # Pedigree features (21)
            'pedigree_distance_suit', 'pedigree_surface_suit',
            'pedigree_going_suit', 'sire_progeny_win_rate',
            'sire_progeny_avg_rating', 'pedigree_rating',
            'first_time_distance', 'genetic_stamina_index',
            'genetic_speed_index',

            # Interaction features (Matrix C)
            'speed_class_ratio', 'speed_class_mismatch',
            'quant_triple_score', 'closing_power', 'pedigree_weight',
            'class_going_interaction', 'speed_sectional_elite',
            'class_drop_advantage',

            # Contextual features
            'distance_optimization', 'going_suitability',
            'field_size_advantage', 'track_winner', 'track_performance',
            'optimal_gap', 'days_since_last'
        ]
```

---

## 🔗 2. Integration Matrix C Implementation {#integration-matrix-c}

### **What is Integration Matrix C?**

Integration Matrix C (from PART_18 of Master Taxonomy) defines **synergies between quantitative categories 18-21** and **bridges to qualitative categories 15-17**.

### **Key Integration Patterns**

#### **Pattern 1: Quantitative Triple (Speed × Class × Sectionals)**

```python
def integrate_speed_class_sectionals(
    speed_rating: float,
    class_rating: float,
    sectional_l200: float
) -> dict:
    """
    The "gold standard" quantitative integration.

    Scenarios:
    1. HIGH speed + HIGH class + FAST sectional = ELITE (90-95% confidence)
    2. HIGH speed + LOW class + FAST sectional = Over-rated (risky)
    3. LOW speed + HIGH class + FAST sectional = Under-rated (value)
    4. HIGH speed + HIGH class + SLOW sectional = Questionable stamina

    Returns:
        {
            'integrated_score': 0-100,
            'confidence': 0-1,
            'scenario': 'elite' | 'over_rated' | 'under_rated' | 'questionable',
            'adjustment': -0.2 to +0.2 (probability adjustment)
        }
    """
    # Normalize inputs to 0-1 scale
    speed_norm = (speed_rating - 80) / 40  # 80-120 scale
    class_norm = (class_rating - 70) / 50  # 70-120 scale
    sectional_norm = 1 - ((sectional_l200 - 10.5) / 2.0)  # 10.5-12.5s scale (inverted, lower = better)

    # Clip to 0-1
    speed_norm = np.clip(speed_norm, 0, 1)
    class_norm = np.clip(class_norm, 0, 1)
    sectional_norm = np.clip(sectional_norm, 0, 1)

    # Calculate integrated score (weighted average)
    integrated_score = (
        speed_norm * 0.35 +
        class_norm * 0.30 +
        sectional_norm * 0.35
    ) * 100

    # Scenario detection
    if speed_norm > 0.75 and class_norm > 0.75 and sectional_norm > 0.75:
        scenario = 'elite'
        confidence = 0.92
        adjustment = +0.15  # Strong positive

    elif speed_norm > 0.75 and class_norm < 0.50 and sectional_norm > 0.75:
        scenario = 'over_rated'
        confidence = 0.68
        adjustment = -0.10  # Negative (inflated by weak competition)

    elif speed_norm < 0.50 and class_norm > 0.75 and sectional_norm > 0.75:
        scenario = 'under_rated'
        confidence = 0.75
        adjustment = +0.12  # Value bet (class rise)

    elif speed_norm > 0.75 and class_norm > 0.75 and sectional_norm < 0.50:
        scenario = 'questionable'
        confidence = 0.60
        adjustment = -0.05  # Stamina concerns

    else:
        scenario = 'mixed'
        confidence = 0.50
        adjustment = 0.0  # Neutral

    return {
        'integrated_score': integrated_score,
        'confidence': confidence,
        'scenario': scenario,
        'adjustment': adjustment,
        'speed_contribution': speed_norm * 35,
        'class_contribution': class_norm * 30,
        'sectional_contribution': sectional_norm * 35
    }
```

#### **Pattern 2: Pedigree × Distance × Conditions**

```python
def integrate_pedigree_projection(
    pedigree_distance_suit: float,
    pedigree_going_suit: float,
    first_time_distance: bool,
    horse_age: int,
    race_distance: int
) -> dict:
    """
    Young horse / first-time distance pedigree projection.

    Use cases:
    - 2yo/3yo with limited form
    - First time at distance/surface
    - Stepping up in distance

    Returns:
        {
            'pedigree_confidence': 0-1,
            'projected_suitability': 0-1,
            'weight_factor': 0-3 (how much to weight pedigree vs form)
        }
    """
    # Base suitability (distance + going combined)
    base_suitability = (pedigree_distance_suit * 0.6 + pedigree_going_suit * 0.4)

    # Weight factor: how much to rely on pedigree
    if first_time_distance and horse_age <= 3:
        # Young horse, first time at distance = HIGH pedigree weight
        weight_factor = 2.5
        confidence = 0.72

    elif first_time_distance and horse_age > 3:
        # Older horse, first time = MODERATE pedigree weight
        weight_factor = 1.8
        confidence = 0.65

    elif horse_age <= 3 and race_distance > 2000:
        # Young staying race = MODERATE pedigree weight
        weight_factor = 2.0
        confidence = 0.68

    else:
        # Experienced horse, known distance = LOW pedigree weight
        weight_factor = 0.8
        confidence = 0.50

    return {
        'pedigree_confidence': confidence,
        'projected_suitability': base_suitability,
        'weight_factor': weight_factor,
        'recommendation': 'Trust pedigree' if weight_factor > 2.0 else 'Trust form'
    }
```

#### **Pattern 3: Chemistry × Quantitative (Bridge to Qualitative)**

```python
def integrate_chemistry_quantitative(
    jockey_trainer_win_rate: float,  # From Category 17
    speed_rating: float,              # From Category 18
    class_rating: float,              # From Category 19
    sectional_l200: float             # From Category 20
) -> dict:
    """
    Integrate qualitative chemistry with quantitative performance.

    Logic:
    - Strong chemistry (>20% win rate) + strong quant = BOOST
    - Strong chemistry + weak quant = SMALLER BOOST
    - Weak chemistry + strong quant = NEUTRAL
    - Weak chemistry + weak quant = NEGATIVE

    Returns:
        {
            'chemistry_multiplier': 0.9-1.15,
            'confidence': 0-1
        }
    """
    # Quantitative strength score
    quant_score = integrate_speed_class_sectionals(
        speed_rating, class_rating, sectional_l200
    )['integrated_score'] / 100

    # Chemistry strength (normalized)
    chemistry_strength = min(jockey_trainer_win_rate / 0.25, 1.0)  # 25% = perfect

    # Multiplier logic
    if chemistry_strength > 0.6 and quant_score > 0.7:
        # Strong chemistry + strong quant = SUPERCHARGE
        multiplier = 1.15
        confidence = 0.88

    elif chemistry_strength > 0.6 and quant_score > 0.5:
        # Strong chemistry + decent quant = BOOST
        multiplier = 1.08
        confidence = 0.75

    elif chemistry_strength > 0.6 and quant_score <= 0.5:
        # Strong chemistry + weak quant = SMALL BOOST
        multiplier = 1.03
        confidence = 0.60

    elif chemistry_strength <= 0.3 and quant_score <= 0.5:
        # Weak chemistry + weak quant = NEGATIVE
        multiplier = 0.92
        confidence = 0.65

    else:
        # Neutral scenario
        multiplier = 1.0
        confidence = 0.50

    return {
        'chemistry_multiplier': multiplier,
        'confidence': confidence,
        'quant_score': quant_score,
        'chemistry_strength': chemistry_strength
    }
```

---

## 💾 3. Feature Store Design {#feature-store}

### **Architecture**

```
Raw Data (DuckDB) → Feature Engineering → Feature Store (Parquet) → ML Training
                                              ↓
                                        Versioning & Lineage
```

### **Implementation**

```python
class QuantitativeFeatureStore:
    """
    Store and manage ML-ready features with versioning.
    """

    def __init__(self, base_path: str = 'data/features/quantitative'):
        self.base_path = Path(base_path)
        self.version = self._get_latest_version()

    def save_features(
        self,
        features: pd.DataFrame,
        race_date: str,
        version: str = None
    ):
        """
        Save features to Parquet with partitioning.

        Structure:
        data/features/quantitative/
          └── v1.0/
              └── year=2025/
                  └── month=11/
                      └── date=2025-11-09.parquet
        """
        version = version or self.version
        output_path = self.base_path / version / f'year={race_date[:4]}' / f'month={race_date[5:7]}'
        output_path.mkdir(parents=True, exist_ok=True)

        output_file = output_path / f'date={race_date}.parquet'
        features.to_parquet(output_file, compression='snappy', index=False)

        # Save metadata
        self._save_metadata(output_file, features)

    def load_features(
        self,
        start_date: str,
        end_date: str,
        version: str = None
    ) -> pd.DataFrame:
        """
        Load features for date range with time-ordered validation.
        """
        version = version or self.version

        # Read partitioned parquet
        df = pd.read_parquet(
            self.base_path / version,
            filters=[('date', '>=', start_date), ('date', '<=', end_date)]
        )

        # Validate time ordering
        assert df['race_date'].is_monotonic_increasing, "Data leakage: dates not ordered!"

        return df

    def create_train_test_split(
        self,
        cutoff_date: str
    ) -> tuple:
        """
        Split features into train/test with strict time ordering.

        Returns:
            (train_df, test_df)
        """
        all_features = self.load_features('2020-01-01', '2025-12-31')

        train = all_features[all_features['race_date'] < cutoff_date]
        test = all_features[all_features['race_date'] >= cutoff_date]

        print(f"Train: {len(train)} races (up to {cutoff_date})")
        print(f"Test: {len(test)} races (from {cutoff_date} onward)")

        return train, test
```

---

## 🤖 4. ML Model Architecture {#ml-models}

### **Model Selection Rationale**

| Model | Why Include? | Strengths | Weaknesses |
|-------|-------------|-----------|-----------|
| **CatBoost** | Best for categorical features | Handles missing data, GPU training, strong regularization | Slower than LightGBM |
| **LightGBM** | Fastest training, good accuracy | Speed, memory efficient, leaf-wise growth | Can overfit if not tuned |
| **XGBoost** | Proven benchmark | Robust, well-documented, industry standard | Middle-ground performance |

**Ensemble Strategy**: Weight by validation performance (CatBoost 40%, LightGBM 35%, XGBoost 25%)

### **Training Pipeline**

```python
class QuantitativePredictorEnsemble:
    """
    Ensemble of CatBoost + LightGBM + XGBoost for win/place prediction.
    """

    def __init__(self):
        self.models = {
            'catboost_win': None,
            'catboost_place': None,
            'lightgbm_win': None,
            'lightgbm_place': None,
            'xgboost_win': None,
            'xgboost_place': None
        }
        self.feature_names = None
        self.weights = {'catboost': 0.40, 'lightgbm': 0.35, 'xgboost': 0.25}

    def train(
        self,
        X_train: pd.DataFrame,
        y_train_win: pd.Series,
        y_train_place: pd.Series,
        X_val: pd.DataFrame,
        y_val_win: pd.Series,
        y_val_place: pd.Series
    ):
        """
        Train all models with hyperparameter tuning.
        """
        self.feature_names = X_train.columns.tolist()

        # Train CatBoost (best for categorical features)
        print("Training CatBoost...")
        self.models['catboost_win'] = self._train_catboost(
            X_train, y_train_win, X_val, y_val_win, task='win'
        )
        self.models['catboost_place'] = self._train_catboost(
            X_train, y_train_place, X_val, y_val_place, task='place'
        )

        # Train LightGBM (fastest)
        print("Training LightGBM...")
        self.models['lightgbm_win'] = self._train_lightgbm(
            X_train, y_train_win, X_val, y_val_win, task='win'
        )
        self.models['lightgbm_place'] = self._train_lightgbm(
            X_train, y_train_place, X_val, y_val_place, task='place'
        )

        # Train XGBoost (robust baseline)
        print("Training XGBoost...")
        self.models['xgboost_win'] = self._train_xgboost(
            X_train, y_train_win, X_val, y_val_win, task='win'
        )
        self.models['xgboost_place'] = self._train_xgboost(
            X_train, y_train_place, X_val, y_val_place, task='place'
        )

        print("Training complete. All models ready.")

    def _train_catboost(
        self,
        X_train, y_train, X_val, y_val, task='win'
    ) -> CatBoostClassifier:
        """
        Train CatBoost with Optuna hyperparameter tuning.
        """
        import optuna
        from catboost import CatBoostClassifier

        def objective(trial):
            params = {
                'iterations': trial.suggest_int('iterations', 500, 2000),
                'depth': trial.suggest_int('depth', 4, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
                'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1.0, 10.0),
                'random_strength': trial.suggest_float('random_strength', 0.1, 10.0),
                'bagging_temperature': trial.suggest_float('bagging_temperature', 0.0, 1.0),
                'loss_function': 'Logloss',
                'eval_metric': 'AUC',
                'random_seed': 42,
                'verbose': False
            }

            model = CatBoostClassifier(**params)
            model.fit(X_train, y_train, eval_set=(X_val, y_val), early_stopping_rounds=50, verbose=False)

            preds = model.predict_proba(X_val)[:, 1]
            auc = roc_auc_score(y_val, preds)
            return auc

        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=100, show_progress_bar=True)

        # Train final model with best params
        best_params = study.best_params
        best_params.update({'loss_function': 'Logloss', 'random_seed': 42, 'verbose': 100})

        model = CatBoostClassifier(**best_params)
        model.fit(X_train, y_train, eval_set=(X_val, y_val), early_stopping_rounds=50)

        return model

    def predict(self, X: pd.DataFrame) -> dict:
        """
        Generate ensemble predictions for win and place.

        Returns:
            {
                'win_prob': 0.185,
                'place_prob': 0.542,
                'model_contributions': {
                    'catboost': {'win': 0.19, 'place': 0.55},
                    'lightgbm': {'win': 0.18, 'place': 0.53},
                    'xgboost': {'win': 0.18, 'place': 0.54}
                }
            }
        """
        # Individual model predictions
        catboost_win = self.models['catboost_win'].predict_proba(X)[:, 1]
        catboost_place = self.models['catboost_place'].predict_proba(X)[:, 1]

        lightgbm_win = self.models['lightgbm_win'].predict_proba(X)[:, 1]
        lightgbm_place = self.models['lightgbm_place'].predict_proba(X)[:, 1]

        xgboost_win = self.models['xgboost_win'].predict_proba(X)[:, 1]
        xgboost_place = self.models['xgboost_place'].predict_proba(X)[:, 1]

        # Weighted ensemble
        win_prob = (
            catboost_win * self.weights['catboost'] +
            lightgbm_win * self.weights['lightgbm'] +
            xgboost_win * self.weights['xgboost']
        )[0]

        place_prob = (
            catboost_place * self.weights['catboost'] +
            lightgbm_place * self.weights['lightgbm'] +
            xgboost_place * self.weights['xgboost']
        )[0]

        return {
            'win_prob': win_prob,
            'place_prob': place_prob,
            'model_contributions': {
                'catboost': {'win': catboost_win[0], 'place': catboost_place[0]},
                'lightgbm': {'win': lightgbm_win[0], 'place': lightgbm_place[0]},
                'xgboost': {'win': xgboost_win[0], 'place': xgboost_place[0]}
            }
        }
```

---

## 📐 5. Calibration & Uncertainty Quantification {#calibration}

### **Why Calibration Matters**

```
Accuracy ≠ Calibration

Example:
Model A: 75% accuracy, poorly calibrated (all predictions near 0.5)
Model B: 72% accuracy, well-calibrated (20% predictions → 20% actual win rate)

Model B is BETTER for betting (can identify value)
```

### **Calibration Method: Isotonic Regression**

```python
from sklearn.isotonic import IsotonicRegression

class ProbabilityCalibrator:
    """
    Calibrate model probabilities using isotonic regression.
    """

    def __init__(self):
        self.calibrators = {}  # Per track group

    def fit(
        self,
        predictions: np.array,
        outcomes: np.array,
        track_groups: np.array
    ):
        """
        Fit calibration curves for each track group.

        Track groups:
        - Flemington
        - Caulfield
        - Moonee Valley
        - Other Metro
        - Country
        """
        unique_groups = np.unique(track_groups)

        for group in unique_groups:
            mask = track_groups == group

            if mask.sum() > 30:  # Need sufficient data
                calibrator = IsotonicRegression(out_of_bounds='clip')
                calibrator.fit(predictions[mask], outcomes[mask])
                self.calibrators[group] = calibrator
            else:
                # Fallback: temperature scaling
                self.calibrators[group] = self._fit_temperature_scaling(
                    predictions[mask], outcomes[mask]
                )

    def calibrate(
        self,
        predictions: np.array,
        track_group: str
    ) -> np.array:
        """
        Apply calibration to new predictions.
        """
        if track_group in self.calibrators:
            return self.calibrators[track_group].predict(predictions)
        else:
            # Default calibration
            return self.calibrators['Other Metro'].predict(predictions)

    def plot_reliability_diagram(
        self,
        predictions: np.array,
        outcomes: np.array,
        n_bins: int = 10
    ):
        """
        Visualize calibration quality.

        Perfect calibration: points on diagonal line
        """
        import matplotlib.pyplot as plt

        bins = np.linspace(0, 1, n_bins + 1)
        bin_centers = (bins[:-1] + bins[1:]) / 2

        observed_freqs = []
        for i in range(n_bins):
            mask = (predictions >= bins[i]) & (predictions < bins[i+1])
            if mask.sum() > 0:
                observed_freq = outcomes[mask].mean()
            else:
                observed_freq = np.nan
            observed_freqs.append(observed_freq)

        plt.figure(figsize=(8, 6))
        plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
        plt.plot(bin_centers, observed_freqs, 'o-', label='Model')
        plt.xlabel('Predicted Probability')
        plt.ylabel('Observed Frequency')
        plt.title('Reliability Diagram')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
```

### **Uncertainty Quantification: Conformal Prediction**

```python
from mapie.classification import MapieClassifier

class ConformalPredictor:
    """
    Generate prediction intervals using conformal prediction.
    """

    def __init__(self, base_model, alpha=0.1):
        """
        Args:
            base_model: Pre-trained classifier
            alpha: Miscoverage rate (0.1 = 90% coverage target)
        """
        self.mapie = MapieClassifier(base_model, method='score', cv='prefit')
        self.alpha = alpha

    def fit(self, X_calib: np.array, y_calib: np.array):
        """
        Fit conformal predictor on calibration set.
        """
        self.mapie.fit(X_calib, y_calib)

    def predict_with_intervals(self, X: np.array) -> dict:
        """
        Generate predictions with confidence intervals.

        Returns:
            {
                'prediction': 0.18,
                'lower_bound': 0.12,
                'upper_bound': 0.25,
                'coverage': 0.90
            }
        """
        y_pred, y_pis = self.mapie.predict(X, alpha=self.alpha)

        prediction = y_pred[0]
        lower = y_pis[0, 0, 0]
        upper = y_pis[0, 1, 0]

        return {
            'prediction': prediction,
            'lower_bound': lower,
            'upper_bound': upper,
            'coverage': 1 - self.alpha,
            'interval_width': upper - lower
        }
```

---

**Continue to Part 3: Integration & Deployment →**
