# Master Taxonomy - Part 13: Category 19 (Class Ratings - NEW Quantitative Category)

**Document Purpose:** Complete implementation reference for official ratings, class assessment, and class-based predictions
**Pipeline Usage:** PRIMARILY Quantitative (core ML features) + Qualitative context
**Implementation Priority:** Phase 1 Week 8 (CRITICAL for quantitative pipeline)

---

## CATEGORY 19: CLASS RATINGS (NEW QUANTITATIVE CATEGORY)

### Overview
- **Category ID:** 19
- **Prediction Power:** 15-25% (class is fundamental predictor of performance)
- **Pipeline Usage:** PRIMARILY Quantitative (85% Quant, 15% Qual)
- **Priority Phase:** Phase 1 Week 8
- **Cost per Race:** $0 (calculated from public data)
- **ChatGPT Access:** 40% (limited class understanding)
- **Our Target Access:** 95%

**Critical Note:** Class ratings are ESSENTIAL for the quantitative pipeline. They normalize performance across different competitive levels. A horse winning a Maiden race is not comparable to a horse winning a Group 1 - class ratings make this comparison possible and quantifiable.

---

## SUBCATEGORIES

### 19.1 Official Ratings (OHR/BHA Equivalent)
**Description:** Official handicap ratings assigned by racing authorities
**Data Type:** Numerical ratings (40-130+ scale)
**Prediction Impact:** 12-20%

**Rating System Overview:**
- Australian racing doesn't have official ratings like UK (BHA) or USA (Beyer)
- We calculate equivalent ratings from race results and class levels
- Ratings account for: race class, finishing position, margin, weight carried, field strength

**Official Rating Structure:**
```python
RATING_BANDS = {
    'elite': (115, 130),           # Group 1 winners, champions
    'high_class': (105, 114),      # Group 1/2 contenders
    'open_class': (95, 104),       # Group 3/Listed level
    'mid_grade': (85, 94),         # Benchmark 90-78 level
    'lower_grade': (75, 84),       # Benchmark 64-70 level
    'maiden_grade': (60, 74),      # Maiden/beginner level
    'unrated': (40, 59)            # First starters, very limited data
}
```

**Calculate Official Rating:**
```python
def calculate_official_rating(horse_history, current_race_class):
    """Calculate equivalent official rating from historical performance"""

    if not horse_history:
        return {
            'official_rating': None,
            'has_rating': False,
            'rating_confidence': 'none'
        }

    # Base rating from best performance
    best_performance = find_best_performance(horse_history)
    base_rating = calculate_base_rating(best_performance)

    # Adjust for consistency
    consistency_adjustment = calculate_consistency_adjustment(horse_history)

    # Adjust for recency (decay old performances)
    recency_adjustment = calculate_recency_adjustment(horse_history)

    # Final rating
    official_rating = base_rating + consistency_adjustment + recency_adjustment

    # Cap rating between 40-130
    official_rating = max(40, min(official_rating, 130))

    return {
        'official_rating': official_rating,
        'rating_band': categorize_rating(official_rating),
        'has_rating': True,
        'rating_confidence': calculate_rating_confidence(horse_history),
        'base_rating': base_rating,
        'consistency_adjustment': consistency_adjustment,
        'recency_adjustment': recency_adjustment
    }

def find_best_performance(horse_history):
    """Find horse's best performance for rating calculation"""

    scored_performances = []

    for run in horse_history:
        # Score based on class and result
        class_value = get_class_value(run['race_class'])
        position_value = get_position_value(run['position'], run['field_size'])
        margin_value = get_margin_value(run['position'], run.get('margin', 0))

        performance_score = class_value + position_value + margin_value

        scored_performances.append({
            'run': run,
            'score': performance_score
        })

    # Return best performance
    best = max(scored_performances, key=lambda x: x['score'])
    return best['run']

def calculate_base_rating(best_run):
    """Calculate base rating from best performance"""

    # Start with class baseline
    class_baselines = {
        'Group 1': 115,
        'Group 2': 110,
        'Group 3': 105,
        'Listed': 100,
        'Open': 95,
        'Benchmark 90': 90,
        'Benchmark 78': 78,
        'Benchmark 64': 64,
        'Maiden': 65
    }

    base = class_baselines.get(best_run['race_class'], 75)

    # Adjust for finishing position
    position_adjustments = {
        1: +10,   # Win adds 10 points
        2: +5,    # 2nd adds 5 points
        3: +2,    # 3rd adds 2 points
        4: 0,     # 4th neutral
        5: -2     # 5th onwards penalty
    }

    position_adj = position_adjustments.get(best_run['position'], -3)

    # Adjust for margin
    if best_run['position'] == 1:
        margin = best_run.get('winning_margin', 0)
        margin_adj = min(margin * 0.5, 5)  # +0.5 per length (max +5)
    else:
        margin = best_run.get('margin', 0)
        margin_adj = -min(margin * 0.3, 8)  # -0.3 per length (max -8)

    # Adjust for field strength
    field_strength_adj = calculate_field_strength_adjustment(best_run)

    return base + position_adj + margin_adj + field_strength_adj

def calculate_field_strength_adjustment(run):
    """Adjust rating based on quality of opposition"""

    field_size = run.get('field_size', 10)

    # Larger fields = stronger competition (typically)
    if field_size >= 16:
        field_adj = +3
    elif field_size >= 12:
        field_adj = +1
    elif field_size <= 6:
        field_adj = -2
    else:
        field_adj = 0

    # Check for Group 1 winners in field (if available)
    if run.get('field_contains_g1_winners', False):
        field_adj += 3

    return field_adj

def calculate_consistency_adjustment(horse_history):
    """Adjust rating based on consistency of performances"""

    if len(horse_history) < 3:
        return 0

    # Calculate standard deviation of recent positions
    recent_positions = [r['position'] for r in horse_history[-5:]]
    position_std = np.std(recent_positions)

    # Consistent performers get bonus
    if position_std < 2.0:
        return +3  # Very consistent
    elif position_std < 3.0:
        return +1  # Moderately consistent
    elif position_std > 5.0:
        return -3  # Very inconsistent
    else:
        return 0

def calculate_recency_adjustment(horse_history):
    """Decay rating for horses without recent strong performances"""

    if not horse_history:
        return 0

    # Find most recent top-3 finish
    days_since_last_top3 = None

    for i, run in enumerate(reversed(horse_history)):
        if run['position'] <= 3:
            days_since_last_top3 = run.get('days_ago', i * 21)  # Estimate 3 weeks between runs
            break

    if days_since_last_top3 is None:
        return -5  # No recent top-3 finishes

    # Decay based on time
    if days_since_last_top3 <= 60:
        return 0  # Recent form, no decay
    elif days_since_last_top3 <= 120:
        return -2  # Moderate decay
    elif days_since_last_top3 <= 180:
        return -4  # Significant decay
    else:
        return -6  # Major decay

def categorize_rating(rating):
    """Categorize rating into class bands"""
    for band, (low, high) in RATING_BANDS.items():
        if low <= rating <= high:
            return band
    return 'unrated'

def calculate_rating_confidence(horse_history):
    """Calculate confidence in rating (based on sample size)"""

    starts = len(horse_history)

    if starts >= 15:
        return 'high'
    elif starts >= 8:
        return 'medium'
    elif starts >= 3:
        return 'low'
    else:
        return 'very_low'
```

**Get Official Rating (from Database if Available):**
```python
def get_official_rating(horse_name, rating_db):
    """Get official handicap rating if available, else calculate"""

    # Try to get from database first
    if rating_db is not None:
        rating = rating_db.query(f"""
            SELECT rating, rating_date, rating_type, rating_source
            FROM official_ratings
            WHERE horse = '{horse_name}'
            ORDER BY rating_date DESC
            LIMIT 1
        """)

        if not rating.empty:
            rating_row = rating.iloc[0]
            return {
                'official_rating': rating_row['rating'],
                'rating_date': rating_row['rating_date'],
                'rating_type': rating_row['rating_type'],
                'rating_source': rating_row['rating_source'],
                'rating_band': categorize_rating(rating_row['rating']),
                'has_rating': True,
                'is_calculated': False
            }

    # If no database rating, calculate from history
    horse_history = get_horse_history(horse_name)
    calculated = calculate_official_rating(horse_history, None)

    if calculated['has_rating']:
        calculated['is_calculated'] = True
        calculated['rating_source'] = 'calculated_from_history'

    return calculated
```

**Quantitative Features:**
```python
def engineer_official_rating_features(rating_data, todays_race_class):
    """Create official rating features for ML"""

    if not rating_data['has_rating']:
        return {
            'has_official_rating': 0,
            'official_rating': None,
            'rating_band': 'unrated'
        }

    rating = rating_data['official_rating']

    # Class requirement for today's race
    class_requirements = {
        'Group 1': 110,
        'Group 2': 105,
        'Group 3': 100,
        'Listed': 95,
        'Open': 90,
        'Benchmark 90': 85,
        'Benchmark 78': 75,
        'Benchmark 64': 65,
        'Maiden': 60
    }

    required_rating = class_requirements.get(todays_race_class, 75)
    rating_surplus = rating - required_rating

    features = {
        'has_official_rating': 1,
        'official_rating': rating,
        'rating_band': rating_data['rating_band'],
        'rating_confidence': rating_data['rating_confidence'],
        'is_calculated_rating': 1 if rating_data.get('is_calculated', False) else 0,

        # Class suitability
        'required_rating_for_class': required_rating,
        'rating_surplus': rating_surplus,
        'rating_deficit': abs(rating_surplus) if rating_surplus < 0 else 0,

        # Binary flags
        'above_class_requirement': 1 if rating_surplus > 0 else 0,
        'well_above_class': 1 if rating_surplus > 10 else 0,
        'below_class_requirement': 1 if rating_surplus < 0 else 0,
        'significantly_below_class': 1 if rating_surplus < -10 else 0,

        # Rating categories
        'is_elite_rated': 1 if rating >= 115 else 0,
        'is_high_class_rated': 1 if 105 <= rating < 115 else 0,
        'is_open_class_rated': 1 if 95 <= rating < 105 else 0,
        'is_mid_grade_rated': 1 if 85 <= rating < 95 else 0,
        'is_lower_grade_rated': 1 if rating < 85 else 0
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Official rating 112 (high class), 7 points above Group 2 requirement (105), rated in top 5% of horses..."
- Reasoning: "Strong class advantage - rating significantly exceeds race requirements"
- Output: Class confidence boost (+10-15% if well above requirement)

---

### 19.2 Class Drop/Rise Analysis
**Description:** Tracking horse's movement between class levels (upward or downward)
**Data Type:** Class progression patterns
**Prediction Impact:** 10-18%

**Why This Matters:**
- Horses dropping in class often have significant advantages (easier competition)
- Horses rising in class face tougher tests
- Significant drops (2+ class levels) can indicate trainer targeting winnable races

**Class Hierarchy:**
```python
CLASS_HIERARCHY = {
    'Group 1': 1,          # Highest level
    'Group 2': 2,
    'Group 3': 3,
    'Listed': 4,
    'Open': 5,
    'Benchmark 90+': 6,
    'Benchmark 78+': 7,
    'Benchmark 64+': 8,
    'Maiden': 9           # Lowest level
}

CLASS_DESCRIPTIONS = {
    1: 'Elite championship level (Cox Plate, Melbourne Cup)',
    2: 'High-class Group racing (Caulfield Guineas, VRC Oaks)',
    3: 'Quality Group racing (Blue Diamond Preview, Sandown Guineas)',
    4: 'Listed quality (strong open class)',
    5: 'Open handicap (unrestricted entry)',
    6: 'Benchmark 90+ (rating-restricted)',
    7: 'Benchmark 78+ (mid-grade restricted)',
    8: 'Benchmark 64+ (lower-grade restricted)',
    9: 'Maiden (winless horses only)'
}
```

**Analyze Class Movement:**
```python
def analyze_class_movement(horse_history, todays_race_class):
    """Comprehensive class progression/regression analysis"""

    if not horse_history or len(horse_history) < 2:
        return {
            'has_class_history': False,
            'class_pattern': 'unknown'
        }

    # Convert race classes to numerical tiers
    class_tiers = []
    for run in horse_history[-10:]:  # Last 10 starts
        tier = CLASS_HIERARCHY.get(run['race_class'], 7)
        class_tiers.append({
            'tier': tier,
            'class_name': run['race_class'],
            'position': run['position'],
            'days_ago': run.get('days_ago', 0)
        })

    today_tier = CLASS_HIERARCHY.get(todays_race_class, 7)

    # Detect pattern over last 5 starts
    recent_tiers = [c['tier'] for c in class_tiers[-5:]]

    # Pattern detection
    if len(set(recent_tiers[-3:])) == 1:
        pattern = 'stable'
    elif all(recent_tiers[i] <= recent_tiers[i+1] for i in range(len(recent_tiers)-1)):
        pattern = 'consistently_dropping'
    elif all(recent_tiers[i] >= recent_tiers[i+1] for i in range(len(recent_tiers)-1)):
        pattern = 'consistently_rising'
    elif recent_tiers[-1] < recent_tiers[0]:
        pattern = 'rising'
    elif recent_tiers[-1] > recent_tiers[0]:
        pattern = 'dropping'
    else:
        pattern = 'volatile'

    # Calculate class change from last start
    if len(class_tiers) >= 1:
        last_tier = class_tiers[-1]['tier']
        class_change = today_tier - last_tier  # Positive = drop, Negative = rise
    else:
        class_change = 0

    # Calculate peak class achieved
    peak_tier = min([c['tier'] for c in class_tiers])  # Lower tier = higher class
    peak_class = next(name for name, tier in CLASS_HIERARCHY.items() if tier == peak_tier)

    # Performance at different class levels
    class_performance = {}
    for tier in set([c['tier'] for c in class_tiers]):
        tier_runs = [c for c in class_tiers if c['tier'] == tier]
        tier_wins = sum(1 for c in tier_runs if c['position'] == 1)
        tier_win_pct = tier_wins / len(tier_runs) if tier_runs else 0

        class_name = next(name for name, t in CLASS_HIERARCHY.items() if t == tier)
        class_performance[class_name] = {
            'starts': len(tier_runs),
            'wins': tier_wins,
            'win_pct': tier_win_pct
        }

    # Today vs peak class
    class_drop_from_peak = today_tier - peak_tier

    return {
        'has_class_history': True,
        'class_pattern': pattern,
        'class_change_from_last': class_change,
        'class_drop': class_change > 0,
        'class_rise': class_change < 0,
        'significant_drop': class_change >= 2,
        'significant_rise': class_change <= -2,
        'peak_class_achieved': peak_class,
        'peak_class_tier': peak_tier,
        'class_drop_from_peak': class_drop_from_peak,
        'back_to_peak_class': class_drop_from_peak == 0,
        'class_performance_by_level': class_performance,
        'recent_class_tiers': recent_tiers,
        'today_class_tier': today_tier
    }

def calculate_class_drop_advantage(class_movement_data, official_rating):
    """Calculate advantage from dropping in class"""

    if not class_movement_data['class_drop']:
        return {
            'has_class_drop_advantage': False,
            'advantage_score': 0
        }

    drop_magnitude = class_movement_data['class_change_from_last']

    # Base advantage from drop size
    if drop_magnitude >= 3:
        base_advantage = 0.20  # 20% boost for major drop
    elif drop_magnitude == 2:
        base_advantage = 0.12  # 12% boost for significant drop
    elif drop_magnitude == 1:
        base_advantage = 0.06  # 6% boost for minor drop
    else:
        base_advantage = 0.00

    # Check if horse has won at this lower class before
    today_class = next(name for name, tier in CLASS_HIERARCHY.items()
                      if tier == class_movement_data['today_class_tier'])

    if today_class in class_movement_data['class_performance_by_level']:
        lower_class_win_pct = class_movement_data['class_performance_by_level'][today_class]['win_pct']

        if lower_class_win_pct > 0.30:
            proven_bonus = 0.08  # 8% bonus if proven winner at this class
        elif lower_class_win_pct > 0.15:
            proven_bonus = 0.04
        else:
            proven_bonus = 0.00
    else:
        proven_bonus = 0.00

    # Official rating vs class
    if official_rating and official_rating > 0:
        rating_surplus = official_rating - (100 - (class_movement_data['today_class_tier'] * 5))
        if rating_surplus > 15:
            rating_bonus = 0.10  # Rating well above class
        elif rating_surplus > 8:
            rating_bonus = 0.05
        else:
            rating_bonus = 0.00
    else:
        rating_bonus = 0.00

    total_advantage = base_advantage + proven_bonus + rating_bonus

    return {
        'has_class_drop_advantage': True,
        'advantage_score': total_advantage,
        'drop_magnitude': drop_magnitude,
        'base_advantage': base_advantage,
        'proven_bonus': proven_bonus,
        'rating_bonus': rating_bonus
    }
```

**Quantitative Features:**
```python
def engineer_class_movement_features(class_movement_data, official_rating):
    """Create class movement features for ML"""

    if not class_movement_data['has_class_history']:
        return {
            'has_class_history': 0,
            'class_pattern': 'unknown'
        }

    # Calculate class drop advantage
    drop_advantage = calculate_class_drop_advantage(class_movement_data, official_rating)

    features = {
        'has_class_history': 1,
        'class_pattern': class_movement_data['class_pattern'],
        'class_change_from_last': class_movement_data['class_change_from_last'],
        'class_drop': 1 if class_movement_data['class_drop'] else 0,
        'class_rise': 1 if class_movement_data['class_rise'] else 0,
        'significant_drop': 1 if class_movement_data['significant_drop'] else 0,
        'significant_rise': 1 if class_movement_data['significant_rise'] else 0,
        'class_drop_from_peak': class_movement_data['class_drop_from_peak'],
        'back_to_peak_class': 1 if class_movement_data['back_to_peak_class'] else 0,

        # Advantage scores
        'has_class_drop_advantage': 1 if drop_advantage['has_class_drop_advantage'] else 0,
        'class_drop_advantage_score': drop_advantage['advantage_score'],

        # Pattern flags
        'stable_class_pattern': 1 if class_movement_data['class_pattern'] == 'stable' else 0,
        'consistently_dropping_pattern': 1 if class_movement_data['class_pattern'] == 'consistently_dropping' else 0,
        'volatile_class_pattern': 1 if class_movement_data['class_pattern'] == 'volatile' else 0
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Dropping from Group 2 to Listed (2 class levels), proven Listed winner (3 wins from 8 starts at this level), rating 108 vs Listed par 95..."
- Reasoning: "Significant class drop + proven at this level + rating advantage = strong targeting by trainer"
- Output: Class drop confidence boost (+12-20% if significant drop with proven record)

---

### 19.3 Par Times by Class
**Description:** Expected finishing times for each class level at specific venues/distances
**Data Type:** Benchmark times database
**Prediction Impact:** 8-12%

**Why This Matters:**
- Par times establish performance benchmarks for each class
- Beating par time indicates above-class ability
- Consistently running below par indicates struggling at this level

**Par Time Database Structure:**
```python
# Comprehensive par times (seconds) for Australian racing
PAR_TIMES_DATABASE = {
    # Format: (venue, distance, track_condition, class): par_time_seconds

    # Flemington - Firm/Good
    ('Flemington', 1200, 'Good', 'Group 1'): 68.5,
    ('Flemington', 1200, 'Good', 'Group 2'): 69.0,
    ('Flemington', 1200, 'Good', 'Group 3'): 69.3,
    ('Flemington', 1200, 'Good', 'Listed'): 69.6,
    ('Flemington', 1200, 'Good', 'Open'): 70.0,
    ('Flemington', 1200, 'Good', 'Benchmark 78'): 70.5,
    ('Flemington', 1200, 'Good', 'Benchmark 64'): 71.0,
    ('Flemington', 1200, 'Good', 'Maiden'): 71.5,

    ('Flemington', 1400, 'Good', 'Group 1'): 82.0,
    ('Flemington', 1400, 'Good', 'Group 2'): 82.5,
    ('Flemington', 1400, 'Good', 'Group 3'): 83.0,
    ('Flemington', 1400, 'Good', 'Open'): 83.5,
    ('Flemington', 1400, 'Good', 'Benchmark 78'): 84.2,
    ('Flemington', 1400, 'Good', 'Maiden'): 85.0,

    ('Flemington', 1600, 'Good', 'Group 1'): 92.8,
    ('Flemington', 1600, 'Good', 'Group 2'): 93.5,
    ('Flemington', 1600, 'Good', 'Group 3'): 94.0,
    ('Flemington', 1600, 'Good', 'Open'): 94.8,
    ('Flemington', 1600, 'Good', 'Benchmark 78'): 95.5,
    ('Flemington', 1600, 'Good', 'Maiden'): 96.5,

    ('Flemington', 2000, 'Good', 'Group 1'): 119.5,
    ('Flemington', 2000, 'Good', 'Group 2'): 120.5,
    ('Flemington', 2000, 'Good', 'Open'): 121.5,
    ('Flemington', 2000, 'Good', 'Benchmark 78'): 122.5,

    ('Flemington', 2500, 'Good', 'Group 1'): 152.0,  # Melbourne Cup
    ('Flemington', 2500, 'Good', 'Group 2'): 153.5,

    # Flemington - Heavy
    ('Flemington', 1200, 'Heavy', 'Group 1'): 70.5,
    ('Flemington', 1200, 'Heavy', 'Open'): 72.0,
    ('Flemington', 1600, 'Heavy', 'Group 1'): 96.0,
    ('Flemington', 1600, 'Heavy', 'Open'): 98.0,

    # Randwick
    ('Randwick', 1200, 'Good', 'Group 1'): 69.0,
    ('Randwick', 1200, 'Good', 'Open'): 70.5,
    ('Randwick', 1400, 'Good', 'Group 1'): 82.5,
    ('Randwick', 1400, 'Good', 'Open'): 84.0,
    ('Randwick', 1600, 'Good', 'Group 1'): 93.5,
    ('Randwick', 1600, 'Good', 'Open'): 95.5,
    ('Randwick', 2000, 'Good', 'Group 1'): 120.0,
    ('Randwick', 2400, 'Good', 'Group 1'): 146.0,  # AJC Derby

    # Caulfield
    ('Caulfield', 1200, 'Good', 'Group 1'): 69.5,
    ('Caulfield', 1400, 'Good', 'Group 1'): 83.0,
    ('Caulfield', 1600, 'Good', 'Group 1'): 94.5,  # Caulfield Guineas
    ('Caulfield', 2000, 'Good', 'Group 1'): 121.0,
    ('Caulfield', 2400, 'Good', 'Group 1'): 147.5,  # Caulfield Cup

    # Moonee Valley
    ('Moonee Valley', 1200, 'Good', 'Group 1'): 69.8,
    ('Moonee Valley', 1600, 'Good', 'Group 1'): 94.8,
    ('Moonee Valley', 2040, 'Good', 'Group 1'): 123.5,  # Cox Plate

    # Rosehill
    ('Rosehill', 1200, 'Good', 'Group 1'): 69.2,
    ('Rosehill', 1500, 'Good', 'Group 1'): 88.5,
    ('Rosehill', 2000, 'Good', 'Group 1'): 120.5,  # Rosehill Guineas

    # ... (Add more venues/distances as needed)
}

def get_par_time(venue, distance, track_condition, race_class):
    """Get par time for given conditions"""

    # Try exact match first
    par_key = (venue, distance, track_condition, race_class)
    if par_key in PAR_TIMES_DATABASE:
        return PAR_TIMES_DATABASE[par_key]

    # Try with normalized track condition
    normalized_condition = normalize_track_condition(track_condition)
    par_key_normalized = (venue, distance, normalized_condition, race_class)
    if par_key_normalized in PAR_TIMES_DATABASE:
        return PAR_TIMES_DATABASE[par_key_normalized]

    # If no exact match, estimate from similar conditions
    return estimate_par_time(venue, distance, track_condition, race_class)

def normalize_track_condition(track_condition):
    """Normalize track condition to Good/Soft/Heavy"""
    if 'Firm' in track_condition or track_condition in ['Good 3', 'Good 4']:
        return 'Good'
    elif track_condition in ['Soft 5', 'Soft 6', 'Soft 7']:
        return 'Soft'
    elif 'Heavy' in track_condition:
        return 'Heavy'
    else:
        return 'Good'

def estimate_par_time(venue, distance, track_condition, race_class):
    """Estimate par time when exact match not available"""

    # Base time from distance (approximate 12.5 m/s average pace)
    base_time = distance / 12.5

    # Adjust for track condition
    condition_adjustments = {
        'Firm 1': -1.0,
        'Firm 2': -0.5,
        'Good': 0.0,
        'Soft': +2.0,
        'Heavy': +4.0
    }
    condition_adj = condition_adjustments.get(normalize_track_condition(track_condition), 0)

    # Adjust for class
    class_adjustments = {
        'Group 1': 0.0,
        'Group 2': +0.5,
        'Group 3': +0.8,
        'Listed': +1.0,
        'Open': +1.5,
        'Benchmark 90': +2.0,
        'Benchmark 78': +2.5,
        'Benchmark 64': +3.0,
        'Maiden': +3.5
    }
    class_adj = class_adjustments.get(race_class, +2.0)

    return base_time + condition_adj + class_adj
```

**Calculate Time vs Par:**
```python
def calculate_time_vs_par(run_data):
    """Calculate how horse performed relative to class par time"""

    if not run_data.get('finish_time_seconds'):
        return {
            'has_time_data': False,
            'par_time': None,
            'time_vs_par': None
        }

    par_time = get_par_time(
        run_data['venue'],
        run_data['distance'],
        run_data['track_condition'],
        run_data['race_class']
    )

    actual_time = run_data['finish_time_seconds']
    time_vs_par = actual_time - par_time

    # Categorize performance
    if time_vs_par < -2.0:
        performance = 'well_above_par'
    elif time_vs_par < -0.5:
        performance = 'above_par'
    elif time_vs_par < 0.5:
        performance = 'at_par'
    elif time_vs_par < 2.0:
        performance = 'below_par'
    else:
        performance = 'well_below_par'

    return {
        'has_time_data': True,
        'par_time': par_time,
        'actual_time': actual_time,
        'time_vs_par': time_vs_par,
        'seconds_faster_than_par': -time_vs_par if time_vs_par < 0 else 0,
        'seconds_slower_than_par': time_vs_par if time_vs_par > 0 else 0,
        'beat_par': time_vs_par < 0,
        'performance_vs_par': performance,
        'par_percentage': (par_time / actual_time) * 100  # >100% = faster than par
    }

def analyze_par_time_consistency(horse_history):
    """Analyze horse's consistency relative to par times"""

    par_performances = []

    for run in horse_history:
        par_analysis = calculate_time_vs_par(run)
        if par_analysis['has_time_data']:
            par_performances.append(par_analysis['time_vs_par'])

    if not par_performances:
        return {
            'has_par_history': False
        }

    avg_vs_par = np.mean(par_performances)
    std_vs_par = np.std(par_performances)

    # Count performances
    beats_par_count = sum(1 for p in par_performances if p < 0)
    beats_par_pct = beats_par_count / len(par_performances)

    return {
        'has_par_history': True,
        'total_timed_runs': len(par_performances),
        'avg_time_vs_par': avg_vs_par,
        'std_time_vs_par': std_vs_par,
        'beats_par_count': beats_par_count,
        'beats_par_percentage': beats_par_pct,
        'consistent_above_par': beats_par_pct > 0.60 and std_vs_par < 1.5,
        'consistent_below_par': beats_par_pct < 0.30 and std_vs_par < 1.5,
        'inconsistent': std_vs_par > 2.5
    }
```

**Quantitative Features:**
```python
def engineer_par_time_features(run_data, horse_history):
    """Create par time features for ML"""

    # Current race par analysis
    current_par = calculate_time_vs_par(run_data)

    # Historical par analysis
    historical_par = analyze_par_time_consistency(horse_history)

    features = {
        # Current race
        'has_par_time': 1 if current_par['has_time_data'] else 0,
        'par_time': current_par.get('par_time'),

        # Historical performance
        'has_par_history': 1 if historical_par.get('has_par_history', False) else 0,
        'avg_time_vs_par': historical_par.get('avg_time_vs_par'),
        'beats_par_percentage': historical_par.get('beats_par_percentage'),
        'consistent_above_par': 1 if historical_par.get('consistent_above_par', False) else 0,
        'consistent_below_par': 1 if historical_par.get('consistent_below_par', False) else 0,
        'inconsistent_vs_par': 1 if historical_par.get('inconsistent', False) else 0
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Consistently runs 1.5 seconds faster than class par (beats par in 8 of last 10 runs), average -1.8 seconds vs par..."
- Reasoning: "Consistently above-par performer, running faster than class standard indicates ability to compete at higher level"
- Output: Above-par performance confidence (+8-12% if consistent)

---

## INTEGRATION GUIDELINES

### Class Ratings + Historical Performance (Category 14)
```python
def integrate_class_with_form(class_data, form_data):
    """Integrate class ratings with recent form"""

    # High rating + good form = very strong
    if class_data['official_rating'] >= 105 and form_data['form_score'] > 75:
        return {
            'synergy_score': 0.25,
            'confidence': 'very_high',
            'narrative': 'High-class horse in excellent form'
        }

    # Class drop + good form = strong targeting
    elif class_data['significant_drop'] and form_data['form_score'] > 70:
        return {
            'synergy_score': 0.20,
            'confidence': 'high',
            'narrative': 'Dropping in class while in good form - trainer targeting win'
        }

    # High rating + poor form = rating may be stale
    elif class_data['official_rating'] >= 105 and form_data['form_score'] < 50:
        return {
            'synergy_score': -0.05,
            'confidence': 'moderate',
            'narrative': 'High rating but poor recent form - may be past peak'
        }

    return {'synergy_score': 0.0, 'confidence': 'neutral'}
```

---

## UNIFIED DATA MODEL

```python
class_ratings_schema = {
    "official_rating": {
        "rating": int,
        "rating_band": str,
        "has_rating": bool,
        "rating_confidence": str,
        "is_calculated": bool,
        "rating_surplus": int
    },
    "class_movement": {
        "class_pattern": str,
        "class_change_from_last": int,
        "class_drop": bool,
        "significant_drop": bool,
        "class_drop_advantage_score": float,
        "peak_class_achieved": str
    },
    "par_performance": {
        "has_par_history": bool,
        "avg_time_vs_par": float,
        "beats_par_percentage": float,
        "consistent_above_par": bool
    }
}
```

---

## COST ANALYSIS

**Category 19 Cost Breakdown:**
- **Official ratings calculation:** $0 (derived from historical data)
- **Class movement analysis:** $0 (database queries)
- **Par time database:** $0 (pre-computed from historical results)

**Total Cost:** $0 per race

---

## IMPLEMENTATION CHECKLIST

### Phase 1 Week 8: Class Ratings Implementation

**Day 1: Official Ratings**
- [ ] Build rating calculation algorithm
- [ ] Create rating database schema
- [ ] Implement rating confidence scoring
- [ ] Test rating calculations on 100 horses

**Day 2: Class Movement Analysis**
- [ ] Build class hierarchy database
- [ ] Implement class progression tracking
- [ ] Calculate class drop advantages
- [ ] Test on known class droppers

**Day 3: Par Time Database**
- [ ] Build comprehensive par time database (all major venues)
- [ ] Implement par time estimation for missing combinations
- [ ] Calculate time vs par for historical data
- [ ] Test par time accuracy

**Day 4: Feature Engineering**
- [ ] Engineer all quantitative features (30+ features)
- [ ] Test feature generation pipeline
- [ ] Validate feature ranges and distributions
- [ ] Handle edge cases (first starters, no time data)

**Day 5: Integration & Validation**
- [ ] Integrate with Category 14 (Historical Performance)
- [ ] Integrate with Category 18 (Speed Ratings)
- [ ] Test full class ratings pipeline
- [ ] Validate prediction improvement from class features

---

**Document Complete: Category 19 (Class Ratings - COMPREHENSIVE)**
**Lines: 800+ (FULLY EXPANDED)**
**Next Document: PART_14_CATEGORY_20.md (Sectional Data - EXPAND FROM 59 TO 800+ LINES)**
