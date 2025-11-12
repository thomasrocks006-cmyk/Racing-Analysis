# Master Taxonomy - Part 12: Category 18 (Speed Ratings - NEW Quantitative Category)

**Document Purpose:** Implementation reference for speed rating systems and adjusted speed figures
**Pipeline Usage:** PRIMARILY Quantitative (core ML features) + Qualitative (GPT-5 context)
**Implementation Priority:** Phase 1 Week 6 (CRITICAL for quantitative pipeline)

---

## CATEGORY 18: SPEED RATINGS (NEW QUANTITATIVE CATEGORY)

### Overview
- **Category ID:** 18
- **Prediction Power:** 20-30% (one of THE MOST predictive quantitative features)
- **Pipeline Usage:** PRIMARILY Quantitative (core ML feature)
- **Priority Phase:** Phase 1 Week 6
- **Cost per Race:** $0-$0.15 (depends on subscription)
- **ChatGPT Access:** 30% (limited speed rating data)
- **Our Target Access:** 95%

**Critical Note:** Speed ratings are ESSENTIAL for quantitative modeling. They normalize performance across different track conditions, distances, and race classes. A horse running 1:10.5 for 1200m on a Fast track is not directly comparable to 1:10.5 on a Heavy 8 track - speed ratings make this comparison possible.

---

## SUBCATEGORIES

### 18.1 Timeform Ratings
**Description:** Professional speed ratings from Timeform
**Data Type:** Numerical ratings (typically 60-140 scale)
**Prediction Impact:** 15-25%

**Timeform Rating System:**
```python
class TimeformRatings:
    """Access and interpret Timeform ratings"""

    RATING_SCALE = {
        'champion': (130, 140),
        'group_1_quality': (120, 129),
        'group_2_quality': (115, 119),
        'group_3_quality': (110, 114),
        'listed_quality': (105, 109),
        'open_class': (100, 104),
        'benchmark': (85, 99),
        'maiden': (60, 84)
    }

    def __init__(self, subscription_key=None):
        """Initialize with optional Timeform subscription"""
        self.has_subscription = subscription_key is not None
        self.api_key = subscription_key

    def get_horse_rating(self, horse_name, race_date=None):
        """Get Timeform rating for horse"""

        if not self.has_subscription:
            # Fallback: scrape public ratings or use calculated ratings
            return self._calculate_approximate_rating(horse_name)

        # API call to Timeform
        url = f"https://api.timeform.com/ratings"
        params = {
            'horse': horse_name,
            'date': race_date,
            'api_key': self.api_key
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            return {
                'timeform_rating': data['rating'],
                'rating_category': self._categorize_rating(data['rating']),
                'rating_confidence': data.get('confidence', 'medium'),
                'last_updated': data.get('last_updated')
            }
        else:
            return self._calculate_approximate_rating(horse_name)

    def _calculate_approximate_rating(self, horse_name):
        """Calculate approximate Timeform-style rating from historical data"""

        # Get horse's recent performances
        horse_history = get_horse_history(horse_name, limit=5)

        if not horse_history:
            return {
                'timeform_rating': None,
                'rating_category': 'unknown',
                'rating_confidence': 'none'
            }

        # Calculate adjusted speed for each run
        ratings = []
        for run in horse_history:
            adjusted_speed = self._calculate_adjusted_speed(run)
            ratings.append(adjusted_speed)

        # Average top 3 ratings
        top_ratings = sorted(ratings, reverse=True)[:3]
        estimated_rating = np.mean(top_ratings) if top_ratings else 80

        return {
            'timeform_rating': estimated_rating,
            'rating_category': self._categorize_rating(estimated_rating),
            'rating_confidence': 'estimated',
            'estimated': True
        }

    def _calculate_adjusted_speed(self, run):
        """Calculate adjusted speed rating for a single run"""

        # Base rating from finishing position
        position_scores = {1: 110, 2: 105, 3: 100, 4: 95, 5: 90}
        base_rating = position_scores.get(run['position'], 85 - (run['position'] - 5) * 2)

        # Adjust for race class
        class_adjustments = {
            'Group 1': +15,
            'Group 2': +10,
            'Group 3': +7,
            'Listed': +5,
            'Open': 0,
            'Benchmark': -5,
            'Maiden': -15
        }
        base_rating += class_adjustments.get(run['race_class'], 0)

        # Adjust for margin
        if run['position'] == 1:
            margin = run.get('winning_margin', 0)
            base_rating += margin * 0.5  # +0.5 per length won by
        else:
            margin = run.get('margin', 0)
            base_rating -= margin * 0.3  # -0.3 per length beaten

        # Adjust for track condition
        track_adjustments = {
            'Firm 1': +3,
            'Good 3': 0,
            'Soft 5': -2,
            'Soft 7': -4,
            'Heavy 8': -6,
            'Heavy 10': -8
        }
        base_rating += track_adjustments.get(run['track_condition'], 0)

        # Cap rating
        return max(60, min(base_rating, 140))

    def _categorize_rating(self, rating):
        """Categorize rating into class level"""
        for category, (low, high) in self.RATING_SCALE.items():
            if low <= rating <= high:
                return category
        return 'unknown'
```

**Quantitative Features:**
```python
def engineer_timeform_features(timeform_data, field_ratings):
    """Create Timeform rating features"""

    if timeform_data['timeform_rating'] is None:
        return {
            'has_timeform_rating': 0,
            'timeform_rating': None
        }

    rating = timeform_data['timeform_rating']

    # Field analysis
    field_ratings_list = [r for r in field_ratings if r is not None]

    if field_ratings_list:
        field_avg = np.mean(field_ratings_list)
        field_max = max(field_ratings_list)
        rating_vs_field_avg = rating - field_avg
        rating_vs_field_max = rating - field_max
        field_rank = sorted(field_ratings_list, reverse=True).index(rating) + 1
        field_percentile = (len(field_ratings_list) - field_rank + 1) / len(field_ratings_list)
    else:
        field_avg = None
        rating_vs_field_avg = None
        field_rank = None
        field_percentile = None

    features = {
        'has_timeform_rating': 1,
        'timeform_rating': rating,
        'rating_category': timeform_data['rating_category'],
        'rating_confidence': timeform_data['rating_confidence'],

        # Field comparisons
        'rating_vs_field_avg': rating_vs_field_avg,
        'rating_vs_field_max': rating_vs_field_max,
        'field_rating_rank': field_rank,
        'field_rating_percentile': field_percentile,

        # Binary flags
        'is_top_rated': 1 if field_rank == 1 else 0 if field_rank else None,
        'is_above_field_avg': 1 if rating_vs_field_avg and rating_vs_field_avg > 0 else 0,
        'rating_advantage': 'strong' if rating_vs_field_avg and rating_vs_field_avg > 10 else
                           'moderate' if rating_vs_field_avg and rating_vs_field_avg > 5 else
                           'slight' if rating_vs_field_avg and rating_vs_field_avg > 0 else
                           'disadvantage'
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Timeform rating 118 (Group 2 quality), 12 points above field average, top-rated runner..."
- Reasoning: "Significant class advantage on speed ratings, highest-rated in field"
- Output: Speed rating confidence boost (+15-25% if top-rated with strong advantage)

---

### 18.2 Racing Post Ratings (RPR)
**Description:** Racing Post speed ratings (UK/AU adaptation)
**Data Type:** Numerical ratings (0-150+ scale)
**Prediction Impact:** 15-25%

**Racing Post Rating System:**
```python
def calculate_racing_post_rating(run_data):
    """Calculate Racing Post style rating"""

    # Base rating from standard time
    standard_time = get_standard_time(run_data['distance'], run_data['track'])
    actual_time = run_data['finish_time_seconds']

    # Seconds faster/slower than standard
    time_diff = standard_time - actual_time

    # Base rating: 100 + (time_diff * 2 per second)
    base_rating = 100 + (time_diff * 2)

    # Weight adjustment
    weight_adjustment = (run_data['weight_carried'] - 54) * 0.5
    base_rating += weight_adjustment

    # Track condition adjustment
    condition_adjustments = {
        'Firm 1': +5,
        'Good 3': 0,
        'Soft 5': -5,
        'Soft 7': -10,
        'Heavy 8': -15,
        'Heavy 10': -20
    }
    base_rating += condition_adjustments.get(run_data['track_condition'], 0)

    # Race class adjustment
    class_adjustments = {
        'Group 1': +20,
        'Group 2': +15,
        'Group 3': +10,
        'Listed': +7,
        'Open': 0,
        'Benchmark 78': -5,
        'Maiden': -15
    }
    base_rating += class_adjustments.get(run_data['race_class'], 0)

    return max(50, min(base_rating, 150))

def get_standard_time(distance, track):
    """Get standard time for distance at track"""

    # Standard times database (seconds)
    STANDARD_TIMES = {
        ('Flemington', 1200): 69.5,
        ('Flemington', 1600): 94.0,
        ('Flemington', 2000): 120.0,
        ('Randwick', 1200): 70.0,
        ('Randwick', 1600): 95.0,
        # ... more standards
    }

    return STANDARD_TIMES.get((track, distance), estimate_standard_time(distance))

def estimate_standard_time(distance):
    """Estimate standard time if not in database"""
    # Approximate: 12.5 m/s average race pace
    return distance / 12.5
```

**RPR Features:**
```python
def engineer_rpr_features(horse_rpr_history, todays_class):
    """Create Racing Post Rating features"""

    if not horse_rpr_history:
        return {
            'has_rpr_history': 0
        }

    # Best RPR
    best_rpr = max(horse_rpr_history)

    # Recent average (last 3)
    recent_rprs = horse_rpr_history[-3:]
    recent_avg_rpr = np.mean(recent_rprs)

    # RPR trend
    if len(recent_rprs) >= 3:
        rpr_trend = 'improving' if recent_rprs[-1] > recent_rprs[0] else 'declining'
    else:
        rpr_trend = 'stable'

    features = {
        'has_rpr_history': 1,
        'best_rpr': best_rpr,
        'recent_avg_rpr': recent_avg_rpr,
        'last_rpr': horse_rpr_history[-1] if horse_rpr_history else None,
        'rpr_trend': rpr_trend,
        'rpr_consistency': np.std(recent_rprs) if len(recent_rprs) > 1 else 0
    }

    return features
```

---

### 18.3 Class-Adjusted Speed Ratings
**Description:** Speed ratings normalized by race class
**Data Type:** Numerical ratings with class adjustment
**Prediction Impact:** 12-18%

**Class-Adjusted Speed Calculation:**
```python
def calculate_class_adjusted_speed(run_data):
    """Calculate speed rating adjusted for class of race"""

    # Raw speed rating
    raw_speed = calculate_racing_post_rating(run_data)

    # Class par (expected rating for this class)
    class_pars = {
        'Group 1': 120,
        'Group 2': 115,
        'Group 3': 110,
        'Listed': 105,
        'Open': 100,
        'Benchmark 90': 95,
        'Benchmark 78': 90,
        'Benchmark 64': 85,
        'Maiden': 75
    }

    class_par = class_pars.get(run_data['race_class'], 90)

    # Class-adjusted rating
    class_adjusted = raw_speed - class_par + 100

    # This normalizes all ratings to 100 baseline
    # A horse running 120 in Group 1 = 100 class-adjusted (par performance)
    # A horse running 110 in Maiden = 110-75+100 = 135 class-adjusted (well above par)

    return {
        'raw_speed_rating': raw_speed,
        'class_par': class_par,
        'class_adjusted_rating': class_adjusted,
        'above_class_par': class_adjusted > 100,
        'class_adjustment_factor': class_adjusted - 100
    }
```

**Class-Adjusted Features:**
```python
def engineer_class_adjusted_features(horse_history, todays_class):
    """Create class-adjusted speed features"""

    if not horse_history:
        return {'has_class_adjusted_data': 0}

    # Calculate class-adjusted ratings for recent runs
    adjusted_ratings = []
    for run in horse_history[-5:]:
        adjusted = calculate_class_adjusted_speed(run)
        adjusted_ratings.append(adjusted['class_adjusted_rating'])

    best_adjusted = max(adjusted_ratings)
    recent_avg_adjusted = np.mean(adjusted_ratings)

    # Predict expected rating for today's class
    todays_par = {
        'Group 1': 120, 'Group 2': 115, 'Group 3': 110,
        'Listed': 105, 'Open': 100, 'Benchmark': 90, 'Maiden': 75
    }.get(todays_class, 90)

    expected_rating_today = recent_avg_adjusted - 100 + todays_par

    features = {
        'has_class_adjusted_data': 1,
        'best_class_adjusted_rating': best_adjusted,
        'recent_avg_class_adjusted': recent_avg_adjusted,
        'expected_rating_for_todays_class': expected_rating_today,
        'class_suited': 1 if recent_avg_adjusted > 100 else 0
    }

    return features
```

---

### 18.4 Condition-Adjusted Speed Ratings
**Description:** Speed ratings adjusted for track conditions
**Data Type:** Numerical ratings with condition adjustment
**Prediction Impact:** 10-15%

**Condition-Adjusted Calculation:**
```python
def calculate_condition_adjusted_speed(run_data):
    """Calculate speed rating adjusted for track condition"""

    # Raw speed rating
    raw_speed = calculate_racing_post_rating(run_data)

    # Condition adjustment factors
    CONDITION_ADJUSTMENTS = {
        'Firm 1': +8,
        'Firm 2': +5,
        'Good 3': 0,    # Baseline
        'Good 4': -2,
        'Soft 5': -5,
        'Soft 6': -8,
        'Soft 7': -12,
        'Heavy 8': -16,
        'Heavy 9': -20,
        'Heavy 10': -25
    }

    adjustment = CONDITION_ADJUSTMENTS.get(run_data['track_condition'], 0)

    # Condition-adjusted rating (normalized to Good 3)
    condition_adjusted = raw_speed - adjustment

    return {
        'raw_speed': raw_speed,
        'track_condition': run_data['track_condition'],
        'condition_adjustment': adjustment,
        'condition_adjusted_rating': condition_adjusted
    }

def predict_speed_for_condition(horse_history, target_condition):
    """Predict horse's speed rating for target condition"""

    # Find runs in similar conditions
    similar_runs = [
        r for r in horse_history
        if r['track_condition'] == target_condition
    ]

    if similar_runs:
        # Use actual performance in this condition
        condition_ratings = [calculate_racing_post_rating(r) for r in similar_runs]
        predicted_rating = np.mean(condition_ratings)
        confidence = 'high'
    else:
        # Use condition-adjusted average
        all_adjusted = [calculate_condition_adjusted_speed(r) for r in horse_history]
        avg_adjusted = np.mean([r['condition_adjusted_rating'] for r in all_adjusted])

        # Re-apply target condition adjustment
        target_adjustment = {
            'Firm 1': -8, 'Good 3': 0, 'Soft 5': +5,
            'Soft 7': +12, 'Heavy 8': +16, 'Heavy 10': +25
        }.get(target_condition, 0)

        predicted_rating = avg_adjusted + target_adjustment
        confidence = 'medium'

    return {
        'predicted_rating': predicted_rating,
        'target_condition': target_condition,
        'confidence': confidence,
        'based_on_actual': len(similar_runs) > 0
    }
```

**Condition-Adjusted Features:**
```python
def engineer_condition_adjusted_features(horse_history, todays_condition):
    """Create condition-adjusted speed features"""

    if not horse_history:
        return {'has_condition_adjusted_data': 0}

    # Predict rating for today's condition
    prediction = predict_speed_for_condition(horse_history, todays_condition)

    # Calculate average condition-adjusted rating
    adjusted_ratings = [
        calculate_condition_adjusted_speed(r)['condition_adjusted_rating']
        for r in horse_history[-5:]
    ]

    features = {
        'has_condition_adjusted_data': 1,
        'predicted_rating_for_condition': prediction['predicted_rating'],
        'condition_prediction_confidence': prediction['confidence'],
        'has_runs_in_condition': 1 if prediction['based_on_actual'] else 0,
        'avg_condition_adjusted_rating': np.mean(adjusted_ratings)
    }

    return features
```

---

## INTEGRATION GUIDELINES

### Speed Ratings + Historical Performance
```python
def integrate_speed_with_form(speed_data, form_data):
    """Integrate speed ratings with recent form"""

    # High speed rating + good form = very strong
    if speed_data.get('is_top_rated', False) and form_data.get('form_score', 0) > 70:
        return {
            'confidence': 'very_high',
            'synergy_score': 0.30,
            'narrative': 'Top-rated with excellent form'
        }

    # High speed rating + poor form = form may be misleading
    elif speed_data.get('is_top_rated', False) and form_data.get('form_score', 0) < 50:
        return {
            'confidence': 'moderate',
            'synergy_score': 0.15,
            'narrative': 'Top-rated despite poor recent form - trust the rating'
        }

    return {'confidence': 'neutral', 'synergy_score': 0.0}
```

---

## UNIFIED DATA MODEL

```python
speed_ratings_schema = {
    "timeform": {
        "rating": float,
        "rating_category": str,
        "rating_vs_field_avg": float,
        "is_top_rated": bool
    },
    "rpr": {
        "best_rpr": float,
        "recent_avg_rpr": float,
        "rpr_trend": str
    },
    "class_adjusted": {
        "best_class_adjusted": float,
        "expected_rating_today": float,
        "class_suited": bool
    },
    "condition_adjusted": {
        "predicted_rating_for_condition": float,
        "has_runs_in_condition": bool
    }
}
```

---

## COST ANALYSIS

- **Timeform subscription:** $0.10-$0.15/race (optional, can calculate)
- **Racing Post ratings:** $0 (can scrape or calculate)
- **Calculations:** $0 (local computation)

**Total:** $0-$0.15/race

---

**Document Complete: Category 18 (Speed Ratings - NEW Quantitative)**
**Next Document: PART_13_CATEGORY_19.md (Class Ratings - NEW Quantitative)**
