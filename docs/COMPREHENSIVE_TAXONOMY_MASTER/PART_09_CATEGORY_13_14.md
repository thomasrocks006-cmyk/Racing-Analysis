# Master Taxonomy - Part 9: Categories 13-14 (Weather Sensitivity & Historical Performance)

**Document Purpose:** Implementation reference for weather impact and historical race records
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (feature engineering)
**Implementation Priority:** Phase 1 Week 4 (Category 13), Phase 1 Week 1 (Category 14)

---

## CATEGORY 13: WEATHER SENSITIVITY

### Overview
- **Category ID:** 13
- **Prediction Power:** 3-8% (context-dependent, significant in extreme weather)
- **Pipeline Usage:** PRIMARILY Qualitative (weather interpretation)
- **Priority Phase:** Phase 1 Week 4
- **Cost per Race:** $0 (BOM API free)
- **ChatGPT Access:** 60%
- **Our Target Access:** 100%

---

## SUBCATEGORIES

### 13.1 Horse Performance in Various Weather Conditions
**Description:** How horse performs under different weather (heat, cold, rain)
**Data Type:** Derived statistics by weather condition
**Prediction Impact:** 5-8%

**Weather Condition Categories:**
```python
WEATHER_CONDITIONS = {
    'extreme_heat': {'temp_min': 35, 'impact': 'high'},
    'hot': {'temp_min': 30, 'temp_max': 35, 'impact': 'moderate'},
    'warm': {'temp_min': 25, 'temp_max': 30, 'impact': 'low'},
    'mild': {'temp_min': 15, 'temp_max': 25, 'impact': 'neutral'},
    'cool': {'temp_min': 10, 'temp_max': 15, 'impact': 'low'},
    'cold': {'temp_min': 5, 'temp_max': 10, 'impact': 'moderate'},
    'extreme_cold': {'temp_max': 5, 'impact': 'high'}
}
```

**Calculate Horse Weather Performance:**
```python
def calculate_horse_weather_performance(horse_history, todays_weather):
    """Analyze horse's historical performance by weather conditions"""

    # Categorize today's weather
    temp = todays_weather['temperature_celsius']
    today_weather_cat = categorize_weather(temp)

    # Filter historical starts by similar weather
    similar_weather_starts = [
        r for r in horse_history
        if categorize_weather(r.get('temperature', 20)) == today_weather_cat
    ]

    if len(similar_weather_starts) < 3:
        return {
            'weather_experience': 'limited',
            'weather_win_pct': None,
            'confidence': 'low'
        }

    # Calculate performance in this weather
    wins = sum(1 for r in similar_weather_starts if r['position'] == 1)
    win_pct = wins / len(similar_weather_starts)

    # Compare to overall win rate
    overall_wins = sum(1 for r in horse_history if r['position'] == 1)
    overall_win_pct = overall_wins / len(horse_history) if horse_history else 0

    performance_delta = win_pct - overall_win_pct

    return {
        'weather_experience': today_weather_cat,
        'weather_starts': len(similar_weather_starts),
        'weather_win_pct': win_pct,
        'overall_win_pct': overall_win_pct,
        'weather_performance_delta': performance_delta,
        'weather_suited': performance_delta > 0.05,
        'confidence': 'high' if len(similar_weather_starts) > 5 else 'medium'
    }

def categorize_weather(temperature):
    """Categorize temperature into weather condition"""
    if temperature >= 35:
        return 'extreme_heat'
    elif temperature >= 30:
        return 'hot'
    elif temperature >= 25:
        return 'warm'
    elif temperature >= 15:
        return 'mild'
    elif temperature >= 10:
        return 'cool'
    elif temperature >= 5:
        return 'cold'
    else:
        return 'extreme_cold'
```

**Qualitative Usage (GPT-5):**
- Context: "Temperature 37°C (extreme heat), Horse X has 2 wins from 4 starts in 35°C+ conditions (50% win rate vs 25% overall)..."
- Reasoning: "Horse handles heat well, significant advantage today"
- Output: Weather suitability adjustment (+10-15% if proven heat performer)

**Quantitative Features:**
```python
def engineer_weather_sensitivity_features(weather_perf_data):
    """Create weather sensitivity features"""

    if weather_perf_data['weather_experience'] == 'limited':
        return {
            'has_weather_history': 0,
            'weather_suited': 0,
            'weather_performance_delta': 0
        }

    features = {
        'has_weather_history': 1,
        'weather_starts': weather_perf_data['weather_starts'],
        'weather_win_pct': weather_perf_data['weather_win_pct'],
        'weather_performance_delta': weather_perf_data['weather_performance_delta'],
        'weather_suited': 1 if weather_perf_data['weather_suited'] else 0,
        'weather_confidence': weather_perf_data['confidence'],

        # Binary flags
        'proven_heat_performer': 1 if (
            weather_perf_data['weather_experience'] in ['hot', 'extreme_heat'] and
            weather_perf_data['weather_performance_delta'] > 0.10
        ) else 0,

        'proven_cold_performer': 1 if (
            weather_perf_data['weather_experience'] in ['cold', 'extreme_cold'] and
            weather_perf_data['weather_performance_delta'] > 0.10
        ) else 0
    }

    return features
```

---

### 13.2 Respiratory/Health Considerations
**Description:** Health issues exacerbated by weather (allergies, breathing)
**Data Type:** Qualitative flags + historical patterns
**Prediction Impact:** 2-5%

**Health Indicators:**
```python
def detect_respiratory_patterns(horse_history, horse_name):
    """Detect potential respiratory or health patterns"""

    # Look for DNF (Did Not Finish) or poor performances in extreme conditions
    extreme_condition_starts = [
        r for r in horse_history
        if (r.get('temperature', 20) > 35 or r.get('temperature', 20) < 8) or
           (r.get('track_condition', '') in ['Heavy 9', 'Heavy 10'])
    ]

    if not extreme_condition_starts:
        return {
            'has_respiratory_concerns': False,
            'confidence': 'no_data'
        }

    # Check for DNF or significant performance drop
    dnf_count = sum(1 for r in extreme_condition_starts if r.get('dnf', False))
    avg_position = np.mean([r['position'] for r in extreme_condition_starts if not r.get('dnf', False)])
    overall_avg = np.mean([r['position'] for r in horse_history if not r.get('dnf', False)])

    if dnf_count >= 2 or avg_position > overall_avg + 3:
        return {
            'has_respiratory_concerns': True,
            'extreme_condition_starts': len(extreme_condition_starts),
            'dnf_count': dnf_count,
            'performance_drop': avg_position - overall_avg,
            'confidence': 'medium'
        }

    return {
        'has_respiratory_concerns': False,
        'confidence': 'low'
    }
```

**Qualitative Usage (GPT-5):**
- Context: "Horse has DNF twice in extreme heat (both 38°C+ days), potential heat sensitivity..."
- Reasoning: "Respiratory concerns in heat, risky selection today (37°C forecast)"
- Output: Health concern flag (reduce confidence -10-15% in extreme conditions)

---

## CATEGORY 14: HISTORICAL PERFORMANCE

### Overview
- **Category ID:** 14
- **Prediction Power:** 20-30% (most predictive single category)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 1
- **Cost per Race:** $0 (public racing data)
- **ChatGPT Access:** 85%
- **Our Target Access:** 100%

---

## SUBCATEGORIES

### 14.1 Recent Form (Last 5 Starts)
**Description:** Detailed recent race history
**Data Type:** Structured race results
**Prediction Impact:** 15-20%

**Recent Form Schema:**
```python
recent_form_schema = {
    "start_1": {  # Most recent
        "date": datetime,
        "days_ago": int,
        "venue": str,
        "distance": int,
        "track_condition": str,
        "position": int,
        "margin": float,
        "field_size": int,
        "race_class": str,
        "weight_carried": float,
        "jockey": str,
        "settling_position": int,
        "prize_money": int,
        "beaten_by": list,  # Horses that finished ahead
        "beaten": list      # Horses beaten
    },
    "start_2": {},  # ... same structure
    "start_3": {},
    "start_4": {},
    "start_5": {}
}
```

**Form String Encoding:**
```python
def encode_form_string(recent_starts):
    """Create traditional form string (e.g., "3-1-2-4-1")"""
    positions = [str(r['position']) for r in recent_starts[:5]]
    return '-'.join(positions)

def calculate_form_score(recent_starts):
    """Calculate numerical form score (0-100)"""
    if not recent_starts:
        return 50  # Neutral

    scores = []
    weights = [0.4, 0.3, 0.2, 0.075, 0.025]  # More weight to recent starts

    for i, start in enumerate(recent_starts[:5]):
        position = start['position']
        field_size = start['field_size']

        # Base score (1st = 100, scale down based on position)
        if position == 1:
            base = 100
        elif position == 2:
            base = 90
        elif position == 3:
            base = 80
        elif position <= 5:
            base = 70 - (position - 3) * 5
        else:
            base = max(30, 60 - (position - 5) * 3)

        # Adjust for field size (winning in larger field = more impressive)
        field_adjustment = (field_size - 10) * 0.5

        # Adjust for margin (close-up finish better than distant)
        margin = start.get('margin', 0)
        margin_adjustment = -min(margin * 2, 15)

        start_score = base + field_adjustment + margin_adjustment
        scores.append(start_score * weights[i])

    return max(20, min(sum(scores), 100))
```

**Quantitative Features:**
```python
def engineer_recent_form_features(recent_starts):
    """Create recent form features"""

    if not recent_starts:
        return {
            'has_form': 0,
            'form_score': 50,
            'avg_position': None
        }

    features = {
        'has_form': 1,
        'starts_count': len(recent_starts),
        'form_string': encode_form_string(recent_starts),
        'form_score': calculate_form_score(recent_starts),

        # Statistical measures
        'avg_position_last_5': np.mean([r['position'] for r in recent_starts[:5]]),
        'avg_position_last_3': np.mean([r['position'] for r in recent_starts[:3]]),
        'best_position_last_5': min([r['position'] for r in recent_starts[:5]]),
        'worst_position_last_5': max([r['position'] for r in recent_starts[:5]]),

        # Win/place counts
        'wins_last_5': sum(1 for r in recent_starts[:5] if r['position'] == 1),
        'wins_last_3': sum(1 for r in recent_starts[:3] if r['position'] == 1),
        'places_last_5': sum(1 for r in recent_starts[:5] if r['position'] <= 3),
        'places_last_3': sum(1 for r in recent_starts[:3] if r['position'] <= 3),

        # Form trend
        'improving_form': 1 if is_improving_form(recent_starts) else 0,
        'declining_form': 1 if is_declining_form(recent_starts) else 0,

        # Recent win flag
        'won_last_start': 1 if recent_starts[0]['position'] == 1 else 0,
        'placed_last_start': 1 if recent_starts[0]['position'] <= 3 else 0,

        # Days since last run
        'days_since_last_run': recent_starts[0]['days_ago'],
        'is_fresh': 1 if recent_starts[0]['days_ago'] >= 21 else 0,
        'is_backing_up': 1 if recent_starts[0]['days_ago'] <= 10 else 0
    }

    return features

def is_improving_form(recent_starts):
    """Check if form is improving (positions getting better)"""
    if len(recent_starts) < 3:
        return False

    # Compare last 2 starts to previous 2 starts
    recent_avg = np.mean([r['position'] for r in recent_starts[:2]])
    previous_avg = np.mean([r['position'] for r in recent_starts[2:4]])

    return recent_avg < previous_avg - 1  # At least 1 position improvement

def is_declining_form(recent_starts):
    """Check if form is declining"""
    if len(recent_starts) < 3:
        return False

    recent_avg = np.mean([r['position'] for r in recent_starts[:2]])
    previous_avg = np.mean([r['position'] for r in recent_starts[2:4]])

    return recent_avg > previous_avg + 1  # At least 1 position decline
```

**Qualitative Usage (GPT-5):**
- Context: "Recent form: 1-2-3-1-2 (form score 88), last start winner at Caulfield 1400m on Good 4..."
- Reasoning: "Excellent recent form, consistent top-3 finishes, won last start"
- Output: Form-based confidence (+20-25% for strong recent form)

---

### 14.2 Career Statistics
**Description:** Lifetime racing record
**Data Type:** Cumulative statistics
**Prediction Impact:** 5-10%

**Career Stats Schema:**
```python
career_stats_schema = {
    "career_starts": int,
    "career_wins": int,
    "career_seconds": int,
    "career_thirds": int,
    "career_win_pct": float,
    "career_place_pct": float,
    "career_prize_money": int,
    "career_avg_position": float,
    "career_best_position": int
}
```

**Quantitative Features:**
```python
def engineer_career_features(career_stats):
    """Create career statistics features"""

    features = {
        'career_starts': career_stats['career_starts'],
        'career_wins': career_stats['career_wins'],
        'career_win_pct': career_stats['career_win_pct'],
        'career_place_pct': career_stats['career_place_pct'],
        'career_prize_money': career_stats['career_prize_money'],

        # Experience categories
        'experience_level': categorize_experience(career_stats['career_starts']),

        # Quality indicators
        'is_proven_winner': 1 if career_stats['career_wins'] >= 3 else 0,
        'is_consistent': 1 if career_stats['career_place_pct'] > 0.40 else 0,
        'is_lightly_raced': 1 if career_stats['career_starts'] < 5 else 0
    }

    return features

def categorize_experience(career_starts):
    """Categorize horse by racing experience"""
    if career_starts == 0:
        return 'debut'
    elif career_starts < 5:
        return 'lightly_raced'
    elif career_starts < 15:
        return 'moderate_experience'
    elif career_starts < 30:
        return 'experienced'
    else:
        return 'seasoned'
```

---

### 14.3 First-Up Performance
**Description:** Performance returning from spell (21+ days)
**Data Type:** Statistics for first-up runs
**Prediction Impact:** 8-12%

**First-Up Analysis:**
```python
def calculate_firstup_statistics(horse_history):
    """Analyze horse's first-up (fresh) performance"""

    # Identify first-up starts (>= 21 days since previous run)
    firstup_starts = []

    for i, start in enumerate(horse_history):
        if i < len(horse_history) - 1:
            days_since_prev = (start['date'] - horse_history[i+1]['date']).days
            if days_since_prev >= 21:
                firstup_starts.append(start)

    if not firstup_starts:
        return {
            'has_firstup_history': False,
            'firstup_starts': 0
        }

    # Calculate first-up statistics
    firstup_wins = sum(1 for r in firstup_starts if r['position'] == 1)
    firstup_places = sum(1 for r in firstup_starts if r['position'] <= 3)

    return {
        'has_firstup_history': True,
        'firstup_starts': len(firstup_starts),
        'firstup_wins': firstup_wins,
        'firstup_win_pct': firstup_wins / len(firstup_starts),
        'firstup_place_pct': firstup_places / len(firstup_starts),
        'firstup_avg_position': np.mean([r['position'] for r in firstup_starts]),
        'firstup_strong': firstup_wins / len(firstup_starts) > 0.20  # 20%+ strike rate
    }
```

**Quantitative Features:**
```python
def engineer_firstup_features(firstup_stats, is_firstup_today):
    """Create first-up performance features"""

    if not firstup_stats['has_firstup_history']:
        return {
            'is_firstup': is_firstup_today,
            'firstup_history_available': 0
        }

    features = {
        'is_firstup': is_firstup_today,
        'firstup_history_available': 1,
        'firstup_win_pct': firstup_stats['firstup_win_pct'],
        'firstup_place_pct': firstup_stats['firstup_place_pct'],
        'firstup_starts': firstup_stats['firstup_starts'],
        'firstup_strong': 1 if firstup_stats['firstup_strong'] else 0,

        # Interaction: is first-up today AND has strong first-up record
        'firstup_advantage': 1 if (is_firstup_today and firstup_stats['firstup_strong']) else 0
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "First-up today, horse has 3 wins from 8 first-up starts (38% strike rate, well above 12% career rate)..."
- Reasoning: "Strong first-up record, performs fresh"
- Output: First-up advantage (+12-15% if proven first-up performer)

---

### 14.4 Consistency & Win Strike Rate
**Description:** Overall consistency and winning frequency
**Data Type:** Derived statistics
**Prediction Impact:** 6-10%

**Consistency Measures:**
```python
def calculate_consistency_metrics(horse_history):
    """Calculate various consistency measures"""

    positions = [r['position'] for r in horse_history]

    return {
        'position_std': np.std(positions),
        'position_variance': np.var(positions),
        'consistency_score': calculate_consistency_score(positions),
        'win_strike_rate': sum(1 for p in positions if p == 1) / len(positions),
        'place_strike_rate': sum(1 for p in positions if p <= 3) / len(positions),
        'top_5_strike_rate': sum(1 for p in positions if p <= 5) / len(positions)
    }

def calculate_consistency_score(positions):
    """Calculate consistency score (0-100, higher = more consistent)"""
    if len(positions) < 3:
        return 50  # Neutral

    std = np.std(positions)
    avg = np.mean(positions)

    # Lower std = more consistent (inverse relationship)
    # Adjust for average position (consistent at top better than consistent at back)
    consistency = 100 - (std * 10) - (avg * 2)

    return max(20, min(consistency, 100))
```

**Quantitative Features:**
```python
def engineer_consistency_features(consistency_data):
    """Create consistency features"""

    features = {
        'position_std': consistency_data['position_std'],
        'consistency_score': consistency_data['consistency_score'],
        'win_strike_rate': consistency_data['win_strike_rate'],
        'place_strike_rate': consistency_data['place_strike_rate'],
        'top_5_strike_rate': consistency_data['top_5_strike_rate'],

        # Categorization
        'consistency_category': categorize_consistency(consistency_data['consistency_score']),

        # Binary flags
        'is_consistent': 1 if consistency_data['consistency_score'] > 70 else 0,
        'is_erratic': 1 if consistency_data['position_std'] > 5.0 else 0,
        'is_reliable_placer': 1 if consistency_data['place_strike_rate'] > 0.50 else 0
    }

    return features

def categorize_consistency(score):
    """Categorize consistency level"""
    if score >= 80:
        return 'highly_consistent'
    elif score >= 65:
        return 'consistent'
    elif score >= 50:
        return 'moderate'
    else:
        return 'inconsistent'
```

---

## INTEGRATION GUIDELINES

### Category 13-14 Cross-Integration

**Weather + Historical Performance:**
```python
def analyze_weather_form_interaction(weather_perf, recent_form):
    """Analyze how weather affects current form"""

    # If horse is in good form AND suited to weather = strong combo
    if recent_form['form_score'] > 75 and weather_perf.get('weather_suited', False):
        return {
            'weather_form_synergy': 0.15,
            'combined_confidence': 'very_high'
        }

    # If in poor form but weather-suited = some redemption potential
    elif recent_form['form_score'] < 50 and weather_perf.get('weather_suited', False):
        return {
            'weather_form_synergy': 0.08,
            'combined_confidence': 'medium'
        }

    return {
        'weather_form_synergy': 0.0,
        'combined_confidence': 'neutral'
    }
```

---

## UNIFIED DATA MODEL

```python
weather_historical_schema = {
    "weather_sensitivity": {
        "weather_suited": bool,
        "weather_performance_delta": float,
        "weather_confidence": str,
        "has_respiratory_concerns": bool
    },
    "historical_performance": {
        "form_string": str,
        "form_score": float,
        "avg_position_last_3": float,
        "wins_last_5": int,
        "days_since_last_run": int,
        "career_win_pct": float,
        "career_starts": int,
        "firstup_win_pct": float,
        "is_firstup": bool,
        "consistency_score": float
    }
}
```

---

## COST ANALYSIS

**Categories 13-14 Cost Breakdown:**
- **Weather data:** $0 (BOM API free)
- **Historical performance:** $0 (public racing records)

**Total Cost:** $0 per race

---

**Document Complete: Categories 13-14 (Weather Sensitivity & Historical Performance)**
**Next Document: PART_10_CATEGORY_15_16.md (Track/Distance Suitability & Intangibles)**
