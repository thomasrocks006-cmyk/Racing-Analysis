# Quantitative Pipeline Architecture - Part 1: Overview & Categories
**Created:** November 9, 2025
**Status:** Production-Ready Design
**Purpose:** Numerical prediction system using Categories 18-21 from Master Taxonomy

**Related Documents:**
- Part 2: Feature Engineering & ML Models
- Part 3: Integration & Deployment
- Master Taxonomy: TAXONOMY_OVERVIEW.md
- Qualitative Pipeline: docs/QUALITATIVE_PIPELINE_ARCHITECTURE.md
- Fusion Model: FUSION_MODEL_ARCHITECTURE.md (to be created)

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Category 18: Speed Ratings](#category-18)
4. [Category 19: Class Ratings](#category-19)
5. [Category 20: Sectional Data](#category-20)
6. [Category 21: Pedigree Analysis](#category-21)

---

## 🎯 1. System Overview {#system-overview}

### **What is the Quantitative Pipeline?**

The Quantitative Pipeline converts **raw numerical data** into **ML-ready features** and produces **base probability predictions** for horse racing outcomes. It operates independently from the Qualitative Pipeline but shares the same Master Taxonomy foundation.

### **Key Characteristics**

| Aspect | Description |
|--------|-------------|
| **Input** | Categories 18-21 (Speed, Class, Sectionals, Pedigree) |
| **Output** | Win/place probabilities + feature importance |
| **Models** | CatBoost, LightGBM, XGBoost (ensemble) |
| **Features** | 100+ engineered features from 4 categories |
| **Calibration** | Isotonic regression per track group |
| **Uncertainty** | Conformal prediction intervals |
| **Target Metrics** | 75%+ accuracy, Brier <0.20, AUC >0.75 |

### **Why Separate from Qualitative?**

```
Qualitative Pipeline (Categories 1-17):
✅ Contextual intelligence (gear changes, trials, tactics)
✅ Expert synthesis (GPT-5 reasoning)
✅ Likelihood ratios (Bayesian updates)
✅ Strengths: Intangibles, partnerships, bias detection

Quantitative Pipeline (Categories 18-21):
✅ Pure numerical predictions (speed, class, sectionals, pedigree)
✅ ML-based ensemble (CatBoost, LightGBM, XGBoost)
✅ Base probabilities (no LR adjustments)
✅ Strengths: Performance metrics, statistical patterns, scalability

Fusion Model:
✅ Combines both via Bayesian integration
✅ Qual LRs update Quant base probabilities
✅ Final calibration & confidence intervals
```

### **Pipeline Philosophy**

1. **Numerical Objectivity**: No subjective interpretation, pure data-driven
2. **Statistical Rigor**: All features validated via backtesting
3. **ML Ensemble**: Diverse models reduce overfitting risk
4. **Calibration-First**: Probabilities must be well-calibrated (not just accurate)
5. **Feature Engineering**: Domain knowledge + automation

---

## 🏗️ 2. Architecture Diagram {#architecture-diagram}

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    MASTER TAXONOMY (Foundation)                           │
│  Categories 18-21: Speed Ratings, Class, Sectionals, Pedigree            │
│  Integration Matrix C: Quantitative synergies                            │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                   DATA COLLECTION LAYER                                   │
│  • Timeform ratings (speed figures)                                      │
│  • Racing Victoria official ratings                                      │
│  • ChampionData sectional times                                          │
│  • Pedigree databases (sire/dam records)                                 │
│  • Historical results (1000+ races)                                      │
│  • Track/distance/going combinations                                     │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     CATEGORY PROCESSORS                                   │
│  ┌────────────────────┐  ┌────────────────────┐                          │
│  │  Speed Ratings     │  │  Class Ratings     │                          │
│  │  (Category 18)     │  │  (Category 19)     │                          │
│  │                    │  │                    │                          │
│  │ • Timeform calc    │  │ • BenchMark (BM)   │                          │
│  │ • Par time adjust  │  │ • Official ratings │                          │
│  │ • Weight adjust    │  │ • Class progression│                          │
│  │ • Wind adjust      │  │ • Prize money scale│                          │
│  │ • Track bias adjust│  │ • Par class curves │                          │
│  │ • Going adjust     │  │ • Competitive level│                          │
│  │                    │  │                    │                          │
│  │ Output: Speed fig  │  │ Output: Class score│                          │
│  │   (0-140 scale)    │  │   (50-120 scale)   │                          │
│  └────────────────────┘  └────────────────────┘                          │
│                                                                           │
│  ┌────────────────────┐  ┌────────────────────┐                          │
│  │  Sectional Data    │  │  Pedigree Analysis │                          │
│  │  (Category 20)     │  │  (Category 21)     │                          │
│  │                    │  │                    │                          │
│  │ • L600m splits     │  │ • Sire stats       │                          │
│  │ • L400m splits     │  │ • Dam stats        │                          │
│  │ • L200m splits     │  │ • Distance suit    │                          │
│  │ • Finishing speed  │  │ • Surface suit     │                          │
│  │ • Sectional ranks  │  │ • Progeny records  │                          │
│  │ • Pace profile     │  │ • Bloodline curves │                          │
│  │                    │  │                    │                          │
│  │ Output: Sectional  │  │ Output: Pedigree   │                          │
│  │   metrics          │  │   suitability (0-1)│                          │
│  └────────────────────┘  └────────────────────┘                          │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    FEATURE ENGINEERING                                    │
│  Transform category outputs into ML-ready features                       │
│                                                                           │
│  • 100+ derived features                                                 │
│  • Distance/going elasticity curves                                      │
│  • Class progression trajectories                                        │
│  • Pace profile clustering                                               │
│  • Bloodline optimization curves                                         │
│  • Integration Matrix C synergies (Speed × Class × Sectionals)           │
│  • Time-ordered splits (no data leakage)                                 │
│  • Feature versioning & lineage                                          │
│                                                                           │
│  Storage: Parquet files with partitioning                                │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      ML MODEL TRAINING                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │   CatBoost       │  │   LightGBM       │  │   XGBoost        │       │
│  │                  │  │                  │  │                  │       │
│  │ • 1000 trees     │  │ • 1500 trees     │  │ • 800 trees      │       │
│  │ • Depth 6        │  │ • Depth 8        │  │ • Depth 5        │       │
│  │ • LR 0.03        │  │ • LR 0.05        │  │ • LR 0.02        │       │
│  │ • L2 reg 3.0     │  │ • L1 reg 0.1     │  │ • L2 reg 1.0     │       │
│  │                  │  │                  │  │                  │       │
│  │ Optuna tuning    │  │ Optuna tuning    │  │ Optuna tuning    │       │
│  │ (100 trials)     │  │ (100 trials)     │  │ (100 trials)     │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                             │                                             │
│                             ▼                                             │
│                     ┌───────────────┐                                     │
│                     │   ENSEMBLE    │                                     │
│                     │  Weighted avg │                                     │
│                     │  CatBoost 40% │                                     │
│                     │  LightGBM 35% │                                     │
│                     │  XGBoost 25%  │                                     │
│                     └───────────────┘                                     │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        CALIBRATION                                        │
│  Ensure probabilities are well-calibrated (not just accurate)            │
│                                                                           │
│  Method: Isotonic Regression (per track group)                           │
│  Fallback: Temperature Scaling (if insufficient data)                    │
│  Validation: Reliability diagrams, Brier score decomposition             │
│  Groups: Flemington, Caulfield, Moonee Valley, Other Metro, Country      │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                  UNCERTAINTY QUANTIFICATION                               │
│  Conformal Prediction: Generate prediction intervals                     │
│                                                                           │
│  Method: Adaptive Conformal Prediction (stratified)                      │
│  Strata: Going (Good/Soft/Heavy) × Distance (Sprint/Mile/Staying)        │
│  Coverage: 90% target (validate on holdout set)                          │
│  Output: [lower_bound, prediction, upper_bound]                          │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      OUTPUT: BASE PREDICTIONS                             │
│  Final quantitative predictions (before fusion with qualitative)         │
│                                                                           │
│  Per Horse:                                                              │
│   • Win probability (0-1)                                                │
│   • Place probability (0-1)                                              │
│   • Confidence interval [lower, upper]                                  │
│   • Feature importance (top 10 features)                                │
│   • Model contributions (CatBoost/LightGBM/XGBoost weights)             │
│                                                                           │
│  Metadata:                                                               │
│   • Model version                                                        │
│   • Feature version                                                      │
│   • Calibration group                                                    │
│   • Uncertainty method                                                   │
│   • Timestamp                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🏇 3. Category 18: Speed Ratings {#category-18}

### **Overview**

Speed ratings normalize horse performance across different tracks, distances, and conditions to create comparable performance metrics (similar to Timeform ratings).

### **Data Sources**

1. **Timeform Ratings** (if available via subscription)
2. **DIY Calculation** (if building from scratch):
   - Race times (seconds)
   - Par times by track/distance/going
   - Weight carried
   - Wind conditions
   - Track bias adjustments

### **Calculation Method: Timeform-Style Ratings**

```python
def calculate_speed_rating(race_data: dict) -> float:
    """
    Calculate Timeform-style speed rating (0-140 scale).

    Formula:
    base_rating = par_rating + time_adjustment + weight_adjustment
    final_rating = adjust_for_conditions(base_rating, wind, bias, going)

    Args:
        race_data: Dict with time, weight, conditions, etc.

    Returns:
        Speed rating on 0-140 scale (100 = average, 120+ = elite)
    """
    # Step 1: Calculate base par rating for distance/class
    par_rating = get_par_rating(
        distance=race_data['distance'],
        track=race_data['track'],
        race_class=race_data['class']
    )

    # Step 2: Time adjustment (seconds faster/slower than par)
    par_time = get_par_time(
        distance=race_data['distance'],
        track=race_data['track'],
        going=race_data['going']
    )
    time_diff = race_data['actual_time'] - par_time

    # Rule: 1 length ≈ 0.2 seconds ≈ 2 rating points (at mile distance)
    # Adjust scale factor by distance
    scale_factor = get_scale_factor(race_data['distance'])
    time_adjustment = -time_diff * scale_factor  # Negative because faster = higher

    # Step 3: Weight adjustment
    # Assumption: 0.5kg ≈ 1 length ≈ 2 rating points
    weight_carried = race_data['weight_kg']
    par_weight = 57.0  # Standard weight-for-age
    weight_diff = weight_carried - par_weight
    weight_adjustment = -weight_diff * 4  # 0.5kg = 2 points, so 1kg = 4 points

    # Step 4: Condition adjustments
    wind_adjustment = calculate_wind_effect(
        wind_speed=race_data['wind_speed'],
        wind_direction=race_data['wind_direction'],
        track_orientation=race_data['track_orientation']
    )

    bias_adjustment = calculate_track_bias_effect(
        barrier=race_data['barrier'],
        bias_type=race_data['track_bias'],
        run_style=race_data['run_style']
    )

    going_adjustment = calculate_going_effect(
        going_rating=race_data['going'],  # Good 4, Soft 7, Heavy 10
        horse_going_preference=race_data['horse_going_pref']
    )

    # Step 5: Combine all adjustments
    base_rating = par_rating + time_adjustment + weight_adjustment
    final_rating = base_rating + wind_adjustment + bias_adjustment + going_adjustment

    # Step 6: Bound to realistic range
    final_rating = np.clip(final_rating, 0, 140)

    return final_rating


def get_scale_factor(distance: int) -> float:
    """
    Time-to-rating conversion varies by distance.
    Shorter races: time differences matter more per length.
    """
    if distance < 1400:  # Sprints
        return 12.0  # 0.1s ≈ 1.2 rating points
    elif distance < 2000:  # Miles
        return 10.0  # 0.1s ≈ 1.0 rating point (base)
    else:  # Staying races
        return 8.0   # 0.1s ≈ 0.8 rating points


def get_par_rating(distance: int, track: str, race_class: str) -> float:
    """
    Base par rating by distance/track/class combination.

    Calibrated from historical data:
    - Group 1 races: par = 110-120
    - Listed races: par = 100-110
    - BM 78+: par = 90-100
    - BM 64-78: par = 80-90
    - BM <64: par = 70-80
    """
    # Load from pre-computed lookup table
    return PAR_RATING_TABLE.get((distance, track, race_class), 85.0)


def get_par_time(distance: int, track: str, going: int) -> float:
    """
    Expected race time for given distance/track/going.

    Example: 1600m at Flemington, Good 4 → 96.5 seconds
    """
    # Load from historical analysis
    base_time = PAR_TIME_TABLE.get((distance, track), distance * 0.06)  # ~60s per 1000m

    # Adjust for going (Heavy 10 is ~5-10% slower than Good 4)
    going_multiplier = 1.0 + (going - 4) * 0.015  # 1.5% slower per going rating

    return base_time * going_multiplier
```

### **Feature Engineering from Speed Ratings**

```python
def engineer_speed_features(horse_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create ML features from speed ratings.

    Features:
    1. Last 3 speed ratings (recency-weighted)
    2. Best speed rating (L10 starts)
    3. Speed rating trajectory (improving/declining)
    4. Speed rating at today's distance
    5. Speed rating at today's going
    6. Speed rating consistency (std dev)
    7. Days since peak speed rating
    8. Speed rating vs class (over/under-rated for class)
    """
    features = {}

    # Recent speed ratings (exponentially weighted)
    features['speed_last_3_avg'] = (
        horse_df['speed_rating'].iloc[-1] * 0.5 +
        horse_df['speed_rating'].iloc[-2] * 0.3 +
        horse_df['speed_rating'].iloc[-3] * 0.2
    ) if len(horse_df) >= 3 else horse_df['speed_rating'].mean()

    # Best speed rating (peak performance)
    features['speed_best_l10'] = horse_df['speed_rating'].tail(10).max()

    # Trajectory (linear regression slope over L5)
    if len(horse_df) >= 5:
        x = np.arange(5)
        y = horse_df['speed_rating'].tail(5).values
        slope, _ = np.polyfit(x, y, 1)
        features['speed_trajectory'] = slope
    else:
        features['speed_trajectory'] = 0.0

    # Distance-specific speed rating
    today_distance = horse_df['target_distance'].iloc[-1]
    distance_mask = (horse_df['distance'] - today_distance).abs() < 200  # ±200m
    features['speed_at_distance'] = (
        horse_df[distance_mask]['speed_rating'].mean()
        if distance_mask.sum() > 0 else features['speed_last_3_avg']
    )

    # Going-specific speed rating
    today_going = horse_df['target_going'].iloc[-1]
    going_mask = (horse_df['going'] - today_going).abs() <= 2  # Similar going
    features['speed_at_going'] = (
        horse_df[going_mask]['speed_rating'].mean()
        if going_mask.sum() > 0 else features['speed_last_3_avg']
    )

    # Consistency
    features['speed_consistency'] = 100 - horse_df['speed_rating'].tail(10).std()

    # Days since peak
    peak_idx = horse_df['speed_rating'].tail(10).idxmax()
    features['days_since_peak_speed'] = (
        (pd.Timestamp.now() - horse_df.loc[peak_idx, 'race_date']).days
    )

    # Speed vs class (is horse over/under-rated for today's class?)
    expected_speed_for_class = estimate_expected_speed(horse_df['target_class'].iloc[-1])
    features['speed_vs_class'] = features['speed_last_3_avg'] - expected_speed_for_class

    return pd.Series(features)
```

### **Integration with Other Categories**

Speed ratings integrate with:
- **Class (19)**: Speed-Class mismatch detection (over/under-rated)
- **Sectionals (20)**: Finishing speed + speed rating = closing ability
- **Suitability (15)**: Speed at today's distance/track
- **Track Conditions (3)**: Speed on today's going

**See Integration Matrix C (PART_18) for detailed synergy rules.**

---

## 🏆 4. Category 19: Class Ratings {#category-19}

### **Overview**

Class ratings measure the competitive level of races and horses. Australia uses **BenchMark (BM)** ratings and **official Racing Victoria ratings**.

### **Data Sources**

1. **Racing Victoria Official Ratings**
   - Updated weekly
   - Scale: 50-120+ (120+ = Group 1 caliber)
   - Available via Racing.com/official sources

2. **BenchMark (BM) System**
   - BM 58, BM 64, BM 78, BM 84, etc.
   - Race conditions define entry requirements
   - Horses rated for eligibility

3. **Prize Money as Proxy**
   - $50k = BM 64-70 range
   - $100k = BM 78-84 range
   - $200k+ = Listed/Group races

### **Class Analysis Methods**

```python
class ClassRatingEngine:
    """
    Calculate and analyze class ratings for horses and races.
    """

    def __init__(self):
        self.rating_history = {}  # Track rating changes over time

    def get_official_rating(self, horse_id: str, date: str) -> float:
        """
        Fetch official Racing Victoria rating for horse at given date.

        Returns:
            Rating on 50-120+ scale
        """
        # Query from database or API
        rating = query_official_rating(horse_id, date)
        return rating if rating else self.estimate_rating(horse_id)

    def estimate_rating(self, horse_id: str) -> float:
        """
        Estimate rating if official rating unavailable.

        Method: Analyze recent race classes and finishes
        """
        recent_races = get_recent_races(horse_id, limit=10)

        if not recent_races:
            return 70.0  # Default BM 70

        # Weighted average based on finish position
        total_weight = 0
        total_rating = 0

        for race in recent_races:
            # Race class rating
            race_rating = self.get_race_class_rating(race)

            # Adjustment for finish position
            # Winner = full rating, 2nd = -2, 3rd = -4, etc.
            finish_adjustment = -(race['finish_position'] - 1) * 2
            adjusted_rating = race_rating + finish_adjustment

            # Recency weight (exponential decay)
            days_ago = (datetime.now() - race['date']).days
            weight = np.exp(-days_ago / 60)  # 60-day half-life

            total_rating += adjusted_rating * weight
            total_weight += weight

        estimated_rating = total_rating / total_weight if total_weight > 0 else 70.0
        return np.clip(estimated_rating, 50, 120)

    def get_race_class_rating(self, race: dict) -> float:
        """
        Determine rating for a given race class.

        Hierarchy:
        - Group 1: 110-120
        - Group 2: 105-110
        - Group 3: 100-105
        - Listed: 95-100
        - BM 84+: 90-95
        - BM 78: 85-90
        - BM 70: 78-85
        - BM 64: 72-78
        - BM 58: 65-72
        """
        if race['is_group1']:
            return 115 + (race['prize_money'] - 500000) / 100000  # $500k+ G1s
        elif race['is_group2']:
            return 107.5
        elif race['is_group3']:
            return 102.5
        elif race['is_listed']:
            return 97.5
        elif 'benchmark' in race:
            bm = race['benchmark']
            return bm + 10  # BM 78 → 88 rating
        else:
            # Estimate from prize money
            return self.rating_from_prize_money(race['prize_money'])

    def rating_from_prize_money(self, prize_money: float) -> float:
        """
        Estimate class rating from prize money.

        Rough conversion:
        $30k = 65 (BM 58)
        $50k = 75 (BM 70)
        $100k = 85 (BM 78)
        $200k = 95 (Listed)
        $500k+ = 110+ (Group 1)
        """
        if prize_money < 40000:
            return 65 + (prize_money - 30000) / 1000
        elif prize_money < 75000:
            return 70 + (prize_money - 40000) / 3500
        elif prize_money < 150000:
            return 78 + (prize_money - 75000) / 7500
        elif prize_money < 300000:
            return 88 + (prize_money - 150000) / 15000
        else:
            return 100 + (prize_money - 300000) / 50000

    def analyze_class_progression(self, horse_id: str) -> dict:
        """
        Analyze horse's class progression over career.

        Returns:
            {
                'peak_class': 95,
                'current_class': 88,
                'trend': 'declining',  # improving/stable/declining
                'class_ceiling': 100,
                'competitive_at_current': True
            }
        """
        races = get_career_races(horse_id)
        ratings = [self.get_race_class_rating(r) for r in races]

        peak_class = max(ratings)
        current_class = np.mean(ratings[-5:])  # Last 5 races

        # Trend analysis (linear regression)
        if len(ratings) >= 5:
            x = np.arange(len(ratings[-10:]))
            y = ratings[-10:]
            slope, _ = np.polyfit(x, y, 1)

            if slope > 1.0:
                trend = 'improving'
            elif slope < -1.0:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'unknown'

        # Estimate ceiling (95th percentile of ratings where horse was competitive)
        competitive_races = [r for r in races if r['finish_position'] <= 3]
        class_ceiling = np.percentile([self.get_race_class_rating(r) for r in competitive_races], 95) if competitive_races else current_class + 5

        return {
            'peak_class': peak_class,
            'current_class': current_class,
            'trend': trend,
            'class_ceiling': class_ceiling,
            'competitive_at_current': current_class >= (class_ceiling - 5)
        }


def engineer_class_features(horse_df: pd.DataFrame, race_class: float) -> dict:
    """
    Create ML features from class ratings.

    Features:
    1. Horse rating vs race class (class drop/rise)
    2. Peak class achieved
    3. Class consistency
    4. Class progression trend
    5. Competitive at this class? (historical win rate)
    6. Days since racing at this class
    7. Class ceiling proximity
    """
    engine = ClassRatingEngine()
    progression = engine.analyze_class_progression(horse_df['horse_id'].iloc[0])

    current_rating = engine.get_official_rating(
        horse_df['horse_id'].iloc[0],
        horse_df['race_date'].iloc[-1]
    )

    features = {
        'class_drop': race_class - current_rating,  # Negative = class rise
        'class_peak': progression['peak_class'],
        'class_current': progression['current_class'],
        'class_ceiling': progression['class_ceiling'],
        'class_trend_improving': 1 if progression['trend'] == 'improving' else 0,
        'class_trend_declining': 1 if progression['trend'] == 'declining' else 0,
        'class_competitive': 1 if progression['competitive_at_current'] else 0,
    }

    # Historical performance at this class level
    similar_class_races = horse_df[
        (horse_df['race_class'] - race_class).abs() < 5
    ]

    if len(similar_class_races) > 0:
        features['class_win_rate_at_level'] = (
            (similar_class_races['finish_position'] == 1).sum() / len(similar_class_races)
        )
        features['class_place_rate_at_level'] = (
            (similar_class_races['finish_position'] <= 3).sum() / len(similar_class_races)
        )

        last_at_class = similar_class_races['race_date'].max()
        features['days_since_this_class'] = (pd.Timestamp.now() - last_at_class).days
    else:
        features['class_win_rate_at_level'] = 0.0
        features['class_place_rate_at_level'] = 0.0
        features['days_since_this_class'] = 9999  # Never raced at this class

    return features
```

### **Integration with Other Categories**

Class ratings integrate with:
- **Speed (18)**: Speed-Class matrix (over/under-rated detection)
- **Sectionals (20)**: Class + closing speed = competitive ability
- **Historical Form (14)**: Class drops often signal improved chances
- **Race Metadata (1)**: Prize money correlation with class

---

## 📊 5. Category 20: Sectional Data {#category-20}

### **Overview**

Sectional times measure horses' performance at different stages of the race (last 600m, 400m, 200m). This reveals **finishing speed** and **closing ability** - critical for predicting winners.

### **Data Sources**

1. **ChampionData** (official sectionals provider for Australian racing)
   - L600m, L400m, L200m split times
   - Sectional rankings within race
   - Available via Racing.com or ChampionData API

2. **Racing.com Official Form**
   - Sectional summaries
   - "Last 600m" times in form guides

3. **Manual Calculation** (if official data unavailable)
   - Estimate from race replay timestamps
   - Less accurate but better than nothing

### **Sectional Analysis Engine**

```python
class SectionalAnalyzer:
    """
    Process and analyze sectional split times.
    """

    def calculate_closing_speed(self, sectionals: dict) -> dict:
        """
        Calculate closing speed metrics from sectional splits.

        Args:
            sectionals: {
                'L600m': 35.2,  # seconds
                'L400m': 23.1,
                'L200m': 11.5,
                'distance': 1600,
                'going': 4
            }

        Returns:
            {
                'finishing_speed': 11.5,  # L200m time
                'closing_sectional_600_400': 12.1,  # 600m-400m split
                'closing_sectional_400_200': 11.6,  # 400m-200m split
                'acceleration': 0.5,  # improvement from 600-400 to 400-200
                'sectional_rank_600': 3,  # ranking within race
                'sectional_rank_400': 2,
                'sectional_rank_200': 1,
                'closing_speed_percentile': 95  # vs historical data
            }
        """
        L600 = sectionals['L600m']
        L400 = sectionals['L400m']
        L200 = sectionals['L200m']

        # Split calculations
        split_600_400 = L600 - L400  # Time for 600m-400m section
        split_400_200 = L400 - L200  # Time for 400m-200m section

        # Acceleration (negative = speeding up)
        acceleration = split_400_200 - split_600_400

        # Compare to par sectionals for distance/going
        par_sectionals = self.get_par_sectionals(
            sectionals['distance'],
            sectionals['going']
        )

        # Percentile ranking
        historical_L200_times = self.get_historical_sectionals(
            sectionals['distance'],
            sectionals['going'],
            section='L200m'
        )

        percentile = percentileofscore(historical_L200_times, L200)

        return {
            'finishing_speed': L200,
            'closing_sectional_600_400': split_600_400,
            'closing_sectional_400_200': split_400_200,
            'acceleration': acceleration,
            'sectional_rank_600': sectionals.get('rank_600', None),
            'sectional_rank_400': sectionals.get('rank_400', None),
            'sectional_rank_200': sectionals.get('rank_200', None),
            'closing_speed_percentile': percentile,
            'vs_par_600': L600 - par_sectionals['L600m'],
            'vs_par_400': L400 - par_sectionals['L400m'],
            'vs_par_200': L200 - par_sectionals['L200m']
        }

    def get_par_sectionals(self, distance: int, going: int) -> dict:
        """
        Get expected sectional times for distance/going combination.

        Par sectionals (Good 4, 1600m example):
        - L600m: 34.5s
        - L400m: 22.8s
        - L200m: 11.3s
        """
        # Load from pre-computed lookup table
        base_sectionals = PAR_SECTIONALS_TABLE.get(distance, {
            'L600m': distance * 0.0215,  # ~21.5s per 1000m
            'L400m': distance * 0.0143,  # ~14.3s per 1000m
            'L200m': distance * 0.0071   # ~7.1s per 1000m
        })

        # Adjust for going
        going_multiplier = 1.0 + (going - 4) * 0.015

        return {
            k: v * going_multiplier
            for k, v in base_sectionals.items()
        }

    def classify_pace_profile(self, sectionals: dict) -> str:
        """
        Classify horse's pace profile based on sectional patterns.

        Profiles:
        - 'front_runner': Fast early, fade late (600-400 fast, 400-200 slow)
        - 'presser': Consistent pace throughout
        - 'closer': Slow early, fast late (600-400 slow, 400-200 fast)
        - 'sustained': Strong finish without early effort
        """
        closing_metrics = self.calculate_closing_speed(sectionals)

        accel = closing_metrics['acceleration']
        rank_progression = (
            closing_metrics['sectional_rank_600'] -
            closing_metrics['sectional_rank_200']
        ) if all([closing_metrics['sectional_rank_600'], closing_metrics['sectional_rank_200']]) else 0

        if accel < -0.5 and rank_progression > 3:
            return 'closer'
        elif accel > 0.5 and rank_progression < -2:
            return 'front_runner'
        elif abs(accel) < 0.3:
            return 'presser' if closing_metrics['finishing_speed'] < 11.5 else 'sustained'
        else:
            return 'mixed'

    def engineer_sectional_features(self, horse_df: pd.DataFrame) -> dict:
        """
        Create ML features from sectional data.

        Features:
        1. Average L200m time (last 5 starts)
        2. Best L200m time (last 10 starts)
        3. L200m consistency (std dev)
        4. L200m at today's distance
        5. Pace profile (one-hot encoded)
        6. Closing ability score (0-100)
        7. Sectional rank progression (average improvement)
        8. Acceleration metric
        """
        sectional_cols = ['L600m', 'L400m', 'L200m']

        if not all(col in horse_df.columns for col in sectional_cols):
            return {}  # No sectional data available

        features = {}

        # Average finishing speed (L200m)
        features['sectional_l200_avg_l5'] = horse_df['L200m'].tail(5).mean()
        features['sectional_l200_best_l10'] = horse_df['L200m'].tail(10).min()  # Min because lower = faster
        features['sectional_l200_consistency'] = 100 - horse_df['L200m'].tail(10).std() * 10

        # Distance-specific sectionals
        today_distance = horse_df['target_distance'].iloc[-1]
        distance_mask = (horse_df['distance'] - today_distance).abs() < 200
        features['sectional_l200_at_distance'] = (
            horse_df[distance_mask]['L200m'].mean()
            if distance_mask.sum() > 0 else features['sectional_l200_avg_l5']
        )

        # Pace profile classification
        recent_sectionals = horse_df.tail(5)[sectional_cols].to_dict('records')
        pace_profiles = [
            self.classify_pace_profile({**s, 'distance': 1600, 'going': 4})
            for s in recent_sectionals if all(s.values())
        ]

        if pace_profiles:
            most_common_profile = max(set(pace_profiles), key=pace_profiles.count)
            features['pace_profile_closer'] = 1 if most_common_profile == 'closer' else 0
            features['pace_profile_presser'] = 1 if most_common_profile == 'presser' else 0
            features['pace_profile_front_runner'] = 1 if most_common_profile == 'front_runner' else 0
            features['pace_profile_sustained'] = 1 if most_common_profile == 'sustained' else 0
        else:
            features['pace_profile_closer'] = 0
            features['pace_profile_presser'] = 0
            features['pace_profile_front_runner'] = 0
            features['pace_profile_sustained'] = 0

        # Closing ability score (percentile-based)
        features['closing_ability_score'] = horse_df['L200m'].tail(10).apply(
            lambda x: 100 - percentileofscore(horse_df['L200m'], x)
        ).mean()

        # Sectional rank progression (if available)
        if 'sectional_rank_200' in horse_df.columns and 'sectional_rank_600' in horse_df.columns:
            rank_improvement = horse_df['sectional_rank_600'] - horse_df['sectional_rank_200']
            features['sectional_rank_progression'] = rank_improvement.tail(5).mean()
        else:
            features['sectional_rank_progression'] = 0.0

        # Acceleration metric
        if all(col in horse_df.columns for col in sectional_cols):
            horse_df['acceleration'] = (
                (horse_df['L600m'] - horse_df['L400m']) -
                (horse_df['L400m'] - horse_df['L200m'])
            )
            features['acceleration_avg'] = horse_df['acceleration'].tail(5).mean()
        else:
            features['acceleration_avg'] = 0.0

        return features
```

### **Integration with Other Categories**

Sectional data integrates with:
- **Pace Scenario (8)**: Sectionals validate pace pressure predictions
- **Speed Ratings (18)**: Fast sectionals + high speed rating = elite closer
- **Class (19)**: Closing speed relative to class level
- **Barrier Draw (4)** + **Track Bias (3)**: Sectionals show if horse can overcome poor draw

**See Integration Matrix C (PART_18) for "Quantitative Triple" (Speed × Class × Sectionals) synergy.**

---

## 🧬 6. Category 21: Pedigree Analysis {#category-21}

### **Overview**

Pedigree analysis uses bloodline data (sire, dam, progeny records) to predict distance/surface suitability, especially for:
- **Young horses** (limited race history)
- **First-time conditions** (new distance, new surface)
- **Breeding insights** (stamina vs speed genetics)

### **Data Sources**

1. **Pedigree Databases**
   - Australian Stud Book
   - Thoroughbred Heritage
   - Racing Australia pedigree records

2. **Sire/Dam Statistics**
   - Progeny win rates
   - Distance preferences (% wins at sprint/mile/staying)
   - Surface preferences (turf vs synthetic)
   - Optimal conditions

3. **Progeny Performance Records**
   - How sire's other offspring perform
   - Dam's other foals
   - Half-siblings (same dam, different sire)

### **Pedigree Suitability Engine**

```python
class PedigreeAnalyzer:
    """
    Analyze bloodline suitability for race conditions.
    """

    def __init__(self):
        self.sire_stats = self.load_sire_database()
        self.dam_stats = self.load_dam_database()

    def calculate_distance_suitability(
        self,
        sire: str,
        dam: str,
        target_distance: int
    ) -> float:
        """
        Calculate pedigree-based distance suitability (0-1 scale).

        Method:
        1. Get sire's progeny distance statistics
        2. Get dam's foals distance statistics
        3. Weight: Sire 60%, Dam 40%
        4. Adjust for target distance category

        Returns:
            0-1 score (1.0 = optimal, 0.5 = neutral, 0.0 = unsuitable)
        """
        # Categorize distance
        distance_category = self.categorize_distance(target_distance)

        # Sire statistics
        sire_data = self.sire_stats.get(sire, {})
        sire_distance_stats = sire_data.get('distance_stats', {})
        sire_score = sire_distance_stats.get(distance_category, 0.5)  # Default neutral

        # Dam statistics
        dam_data = self.dam_stats.get(dam, {})
        dam_distance_stats = dam_data.get('distance_stats', {})
        dam_score = dam_distance_stats.get(distance_category, 0.5)

        # Weighted combination (sire more influential)
        combined_score = sire_score * 0.6 + dam_score * 0.4

        return combined_score

    def categorize_distance(self, distance: int) -> str:
        """
        Categorize race distance.

        Categories:
        - sprint: <1400m
        - mile: 1400-1800m
        - middle: 1800-2200m
        - staying: 2200m+
        """
        if distance < 1400:
            return 'sprint'
        elif distance < 1800:
            return 'mile'
        elif distance < 2200:
            return 'middle'
        else:
            return 'staying'

    def load_sire_database(self) -> dict:
        """
        Load sire statistics from database.

        Structure:
        {
            'Sire Name': {
                'progeny_count': 150,
                'progeny_win_rate': 0.12,
                'distance_stats': {
                    'sprint': 0.75,  # Strong at sprints
                    'mile': 0.65,
                    'middle': 0.45,
                    'staying': 0.25   # Weak at staying
                },
                'surface_stats': {
                    'turf': 0.85,
                    'synthetic': 0.55
                },
                'going_stats': {
                    'firm': 0.78,
                    'soft': 0.60,
                    'heavy': 0.45
                },
                'avg_progeny_rating': 85.0
            }
        }
        """
        # Load from pre-processed database
        return load_pedigree_data('sires')

    def load_dam_database(self) -> dict:
        """Load dam statistics (similar structure to sires)."""
        return load_pedigree_data('dams')

    def calculate_surface_suitability(
        self,
        sire: str,
        dam: str,
        surface: str
    ) -> float:
        """
        Calculate pedigree-based surface suitability.

        Args:
            surface: 'turf' or 'synthetic'

        Returns:
            0-1 score
        """
        sire_data = self.sire_stats.get(sire, {})
        dam_data = self.dam_stats.get(dam, {})

        sire_score = sire_data.get('surface_stats', {}).get(surface, 0.5)
        dam_score = dam_data.get('surface_stats', {}).get(surface, 0.5)

        return sire_score * 0.6 + dam_score * 0.4

    def calculate_going_suitability(
        self,
        sire: str,
        dam: str,
        going: str
    ) -> float:
        """
        Calculate pedigree-based going suitability.

        Args:
            going: 'firm', 'soft', or 'heavy'

        Returns:
            0-1 score
        """
        sire_data = self.sire_stats.get(sire, {})
        dam_data = self.dam_stats.get(dam, {})

        sire_score = sire_data.get('going_stats', {}).get(going, 0.5)
        dam_score = dam_data.get('going_stats', {}).get(going, 0.5)

        return sire_score * 0.6 + dam_score * 0.4

    def analyze_progeny_performance(self, sire: str) -> dict:
        """
        Analyze how sire's progeny perform overall.

        Returns:
            {
                'progeny_count': 150,
                'win_rate': 0.12,
                'place_rate': 0.32,
                'avg_rating': 85.0,
                'strike_rate_by_age': {
                    '2yo': 0.08,
                    '3yo': 0.14,
                    '4yo': 0.11,
                    '5yo+': 0.09
                },
                'notable_winners': ['Horse A', 'Horse B'],
                'earnings_per_runner': 125000
            }
        """
        sire_data = self.sire_stats.get(sire, {})

        return {
            'progeny_count': sire_data.get('progeny_count', 0),
            'win_rate': sire_data.get('progeny_win_rate', 0.0),
            'place_rate': sire_data.get('progeny_place_rate', 0.0),
            'avg_rating': sire_data.get('avg_progeny_rating', 70.0),
            'strike_rate_by_age': sire_data.get('strike_rate_by_age', {}),
            'notable_winners': sire_data.get('notable_winners', []),
            'earnings_per_runner': sire_data.get('earnings_per_runner', 0)
        }

    def engineer_pedigree_features(
        self,
        horse_data: dict,
        race_conditions: dict
    ) -> dict:
        """
        Create ML features from pedigree analysis.

        Features:
        1. Distance suitability (0-1)
        2. Surface suitability (0-1)
        3. Going suitability (0-1)
        4. Sire progeny win rate
        5. Sire progeny avg rating
        6. Dam foals win rate
        7. Pedigree rating (combined score)
        8. First-time distance flag
        9. Genetic stamina index
        10. Genetic speed index
        """
        sire = horse_data['sire']
        dam = horse_data['dam']

        # Core suitability scores
        distance_suit = self.calculate_distance_suitability(
            sire, dam, race_conditions['distance']
        )
        surface_suit = self.calculate_surface_suitability(
            sire, dam, race_conditions['surface']
        )
        going_suit = self.calculate_going_suitability(
            sire, dam, self.categorize_going(race_conditions['going'])
        )

        # Progeny performance
        progeny_stats = self.analyze_progeny_performance(sire)

        # Combined pedigree rating
        pedigree_rating = (
            distance_suit * 0.4 +
            surface_suit * 0.3 +
            going_suit * 0.2 +
            progeny_stats['win_rate'] * 100 * 0.1
        )

        # Genetic indexes (sprint vs staying)
        sire_data = self.sire_stats.get(sire, {})
        stamina_index = (
            sire_data.get('distance_stats', {}).get('staying', 0.5) +
            sire_data.get('distance_stats', {}).get('middle', 0.5)
        ) / 2

        speed_index = (
            sire_data.get('distance_stats', {}).get('sprint', 0.5) +
            sire_data.get('distance_stats', {}).get('mile', 0.5)
        ) / 2

        features = {
            'pedigree_distance_suit': distance_suit,
            'pedigree_surface_suit': surface_suit,
            'pedigree_going_suit': going_suit,
            'sire_progeny_win_rate': progeny_stats['win_rate'],
            'sire_progeny_avg_rating': progeny_stats['avg_rating'],
            'pedigree_rating': pedigree_rating,
            'first_time_distance': 1 if horse_data.get('first_time_distance') else 0,
            'genetic_stamina_index': stamina_index,
            'genetic_speed_index': speed_index,
        }

        return features

    def categorize_going(self, going_rating: int) -> str:
        """
        Convert numeric going to category.

        1-4 = firm
        5-7 = soft
        8-10 = heavy
        """
        if going_rating <= 4:
            return 'firm'
        elif going_rating <= 7:
            return 'soft'
        else:
            return 'heavy'
```

### **When Pedigree is Most Valuable**

Pedigree analysis provides **highest value** in these scenarios:

1. **Young Horses (2-3yo)**: Limited race history → rely on bloodline
2. **First-Time Distance**: Horse never ran at today's distance → use sire/dam stats
3. **First-Time Surface**: Turf to synthetic (or vice versa) → use bloodline preferences
4. **First-Time Going**: First time on heavy track → use genetic going tolerance
5. **Class Rise**: Stepping up in class → use progeny performance at higher levels
6. **Import Horses**: New to Australian racing → use international bloodline data

### **Integration with Other Categories**

Pedigree integrates with:
- **Distance (1)**: Bloodline distance optimization curves
- **Track Conditions (3)**: Genetic going preferences
- **Historical Form (14)**: Weight pedigree more when form is sparse
- **Speed/Class/Sectionals (18-20)**: Young horses inherit speed/stamina traits

**Example: 2yo maiden with 2 starts:**
- Historical form = weak (only 2 data points)
- Pedigree = strong signal (sire's progeny 15% win rate at 1200m)
- ML model weights pedigree features heavily for this horse

---

**Continue to Part 2: Feature Engineering & ML Models →**
