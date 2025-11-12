# Master Taxonomy - Part 10: Categories 15-16 (Track/Distance Suitability & Intangibles - Enhanced)

**Document Purpose:** Implementation reference for venue/distance specialization and fitness/readiness indicators
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (feature engineering)
**Implementation Priority:** Phase 1 Week 4

---

## CATEGORY 15: TRACK/DISTANCE SUITABILITY

### Overview
- **Category ID:** 15
- **Prediction Power:** 12-18% (horses have strong venue/distance preferences)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 4
- **Cost per Race:** $0 (derived from historical data)
- **ChatGPT Access:** 75%
- **Our Target Access:** 100%

---

## SUBCATEGORIES

### 15.1 Venue-Specific Performance
**Description:** Horse's historical record at today's venue
**Data Type:** Statistics by venue
**Prediction Impact:** 8-12%

**Venue Performance Analysis:**
```python
def calculate_venue_performance(horse_history, todays_venue):
    """Calculate horse's performance at specific venue"""

    # Filter starts at this venue
    venue_starts = [r for r in horse_history if r['venue'] == todays_venue]

    if not venue_starts:
        return {
            'has_venue_history': False,
            'venue_starts': 0,
            'venue_familiarity': 'none'
        }

    # Calculate statistics
    venue_wins = sum(1 for r in venue_starts if r['position'] == 1)
    venue_places = sum(1 for r in venue_starts if r['position'] <= 3)

    venue_win_pct = venue_wins / len(venue_starts)
    venue_place_pct = venue_places / len(venue_starts)
    venue_avg_position = np.mean([r['position'] for r in venue_starts])

    # Compare to overall performance
    overall_wins = sum(1 for r in horse_history if r['position'] == 1)
    overall_win_pct = overall_wins / len(horse_history) if horse_history else 0

    venue_vs_overall = venue_win_pct - overall_win_pct

    return {
        'has_venue_history': True,
        'venue_starts': len(venue_starts),
        'venue_wins': venue_wins,
        'venue_win_pct': venue_win_pct,
        'venue_place_pct': venue_place_pct,
        'venue_avg_position': venue_avg_position,
        'venue_vs_overall': venue_vs_overall,
        'venue_specialist': venue_vs_overall > 0.15,  # 15%+ better at this venue
        'venue_familiarity': categorize_familiarity(len(venue_starts))
    }

def categorize_familiarity(starts):
    """Categorize venue familiarity"""
    if starts == 0:
        return 'none'
    elif starts < 3:
        return 'limited'
    elif starts < 7:
        return 'moderate'
    else:
        return 'extensive'
```

**Quantitative Features:**
```python
def engineer_venue_features(venue_perf_data):
    """Create venue performance features"""

    if not venue_perf_data['has_venue_history']:
        return {
            'has_venue_history': 0,
            'venue_starts': 0,
            'venue_win_pct': None,
            'venue_specialist': 0
        }

    features = {
        'has_venue_history': 1,
        'venue_starts': venue_perf_data['venue_starts'],
        'venue_wins': venue_perf_data['venue_wins'],
        'venue_win_pct': venue_perf_data['venue_win_pct'],
        'venue_place_pct': venue_perf_data['venue_place_pct'],
        'venue_avg_position': venue_perf_data['venue_avg_position'],
        'venue_vs_overall': venue_perf_data['venue_vs_overall'],
        'venue_specialist': 1 if venue_perf_data['venue_specialist'] else 0,
        'venue_familiarity': venue_perf_data['venue_familiarity'],

        # Confidence levels
        'venue_stats_confidence': 'high' if venue_perf_data['venue_starts'] > 5 else
                                  'medium' if venue_perf_data['venue_starts'] > 2 else
                                  'low'
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Horse has 4 wins from 9 starts at Flemington (44% win rate vs 18% overall), clear venue specialist..."
- Reasoning: "Proven track specialist, significant advantage today"
- Output: Venue suitability adjustment (+12-18% if venue specialist)

---

### 15.2 Distance-Specific Performance
**Description:** Horse's historical record at today's distance
**Data Type:** Statistics by distance range
**Prediction Impact:** 10-15%

**Distance Performance Analysis:**
```python
def calculate_distance_performance(horse_history, todays_distance):
    """Calculate horse's performance at specific distance"""

    # Define distance tolerance (±100m)
    distance_starts = [
        r for r in horse_history
        if abs(r['distance'] - todays_distance) <= 100
    ]

    if not distance_starts:
        # Broaden search to distance category if no exact matches
        distance_category = categorize_distance(todays_distance)
        distance_starts = [
            r for r in horse_history
            if categorize_distance(r['distance']) == distance_category
        ]

    if not distance_starts:
        return {
            'has_distance_history': False,
            'distance_starts': 0
        }

    # Calculate statistics
    distance_wins = sum(1 for r in distance_starts if r['position'] == 1)
    distance_places = sum(1 for r in distance_starts if r['position'] <= 3)

    distance_win_pct = distance_wins / len(distance_starts)
    distance_place_pct = distance_places / len(distance_starts)

    # Compare to overall
    overall_win_pct = sum(1 for r in horse_history if r['position'] == 1) / len(horse_history)
    distance_vs_overall = distance_win_pct - overall_win_pct

    # Find optimal distance
    optimal_distance = find_optimal_distance(horse_history)
    distance_delta = abs(todays_distance - optimal_distance) if optimal_distance else None

    return {
        'has_distance_history': True,
        'distance_starts': len(distance_starts),
        'distance_wins': distance_wins,
        'distance_win_pct': distance_win_pct,
        'distance_place_pct': distance_place_pct,
        'distance_vs_overall': distance_vs_overall,
        'distance_specialist': distance_vs_overall > 0.15,
        'optimal_distance': optimal_distance,
        'distance_delta_from_optimal': distance_delta,
        'at_optimal_distance': abs(distance_delta) < 100 if distance_delta else False
    }

def categorize_distance(distance):
    """Categorize distance into sprint/mile/staying"""
    if distance < 1400:
        return 'sprint'
    elif distance < 1800:
        return 'mile'
    else:
        return 'staying'

def find_optimal_distance(horse_history):
    """Find horse's optimal distance (highest win rate)"""

    # Group by distance categories
    distance_performance = {}

    for distance in [1200, 1400, 1600, 2000, 2400]:
        starts = [r for r in horse_history if abs(r['distance'] - distance) <= 100]
        if starts:
            wins = sum(1 for r in starts if r['position'] == 1)
            win_pct = wins / len(starts)
            distance_performance[distance] = {
                'win_pct': win_pct,
                'starts': len(starts)
            }

    if not distance_performance:
        return None

    # Return distance with highest win rate (minimum 3 starts)
    valid_distances = {d: p for d, p in distance_performance.items() if p['starts'] >= 3}

    if valid_distances:
        return max(valid_distances, key=lambda d: valid_distances[d]['win_pct'])
    else:
        return max(distance_performance, key=lambda d: distance_performance[d]['win_pct'])
```

**Quantitative Features:**
```python
def engineer_distance_features(distance_perf_data, todays_distance):
    """Create distance performance features"""

    if not distance_perf_data['has_distance_history']:
        return {
            'has_distance_history': 0,
            'distance_starts': 0,
            'distance_win_pct': None
        }

    features = {
        'has_distance_history': 1,
        'distance_starts': distance_perf_data['distance_starts'],
        'distance_wins': distance_perf_data['distance_wins'],
        'distance_win_pct': distance_perf_data['distance_win_pct'],
        'distance_place_pct': distance_perf_data['distance_place_pct'],
        'distance_vs_overall': distance_perf_data['distance_vs_overall'],
        'distance_specialist': 1 if distance_perf_data['distance_specialist'] else 0,
        'optimal_distance': distance_perf_data['optimal_distance'],
        'distance_delta_from_optimal': distance_perf_data['distance_delta_from_optimal'],
        'at_optimal_distance': 1 if distance_perf_data['at_optimal_distance'] else 0,

        # Distance category match
        'distance_category': categorize_distance(todays_distance),
        'racing_at_preferred_category': 1 if distance_perf_data.get('distance_specialist') else 0
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Horse has 5 wins from 7 starts at 1600m (71% win rate), optimal distance..."
- Reasoning: "Racing at proven optimal distance, strong suitability"
- Output: Distance suitability adjustment (+15-18% if at optimal distance)

---

### 15.3 Venue-Distance Combination
**Description:** Performance at specific venue+distance combination
**Data Type:** Combined statistics
**Prediction Impact:** 6-10%

**Venue-Distance Analysis:**
```python
def calculate_venue_distance_performance(horse_history, venue, distance):
    """Calculate performance at specific venue+distance combo"""

    # Filter for exact venue+distance (±100m)
    combo_starts = [
        r for r in horse_history
        if r['venue'] == venue and abs(r['distance'] - distance) <= 100
    ]

    if not combo_starts:
        return {
            'has_combo_history': False,
            'combo_starts': 0
        }

    combo_wins = sum(1 for r in combo_starts if r['position'] == 1)
    combo_win_pct = combo_wins / len(combo_starts)

    return {
        'has_combo_history': True,
        'combo_starts': len(combo_starts),
        'combo_wins': combo_wins,
        'combo_win_pct': combo_win_pct,
        'combo_specialist': combo_win_pct > 0.30 and len(combo_starts) >= 3
    }
```

**Quantitative Features:**
```python
def engineer_venue_distance_combo_features(combo_data):
    """Create venue-distance combination features"""

    if not combo_data['has_combo_history']:
        return {
            'has_combo_history': 0,
            'combo_starts': 0
        }

    features = {
        'has_combo_history': 1,
        'combo_starts': combo_data['combo_starts'],
        'combo_wins': combo_data['combo_wins'],
        'combo_win_pct': combo_data['combo_win_pct'],
        'combo_specialist': 1 if combo_data['combo_specialist'] else 0
    }

    return features
```

---

## CATEGORY 16: INTANGIBLES (FITNESS, READINESS, PEAK PERFORMANCE - Enhanced)

### Overview
- **Category ID:** 16
- **Prediction Power:** 8-15% (subjective but impactful indicators)
- **Pipeline Usage:** PRIMARILY Qualitative (GPT-5 interpretation)
- **Priority Phase:** Phase 1 Week 4
- **Cost per Race:** $0 (derived indicators)
- **ChatGPT Access:** 40% (limited fitness assessment)
- **Our Target Access:** 85% (systematic fitness indicators)

### Enhanced Quantitative Coverage
**Status:** ⚠️ Needs Enhancement (currently qualitative-heavy)

**Enhancements Added:**
1. Fitness rating (1-10 numerical scale)
2. Peak performance window index (probability of peak form)
3. Preparation quality score (trial + spell analysis)

---

## SUBCATEGORIES

### 16.1 Fitness & Conditioning (Enhanced)
**Description:** Horse's fitness level and preparation quality
**Data Type:** Derived indicators + Numerical fitness rating
**Prediction Impact:** 10-15%

**Fitness Indicators:**
```python
FITNESS_INDICATORS = {
    'excellent': {
        'rating': 9,
        'criteria': [
            'Won recent trial',
            'Ideal spell length (30-60 days)',
            'Weight stable or increased',
            'No gear changes (settled)',
            'Strong recent gallop reports'
        ]
    },
    'good': {
        'rating': 7,
        'criteria': [
            'Placed in trial',
            'Reasonable spell (20-90 days)',
            'Weight within 3kg of ideal',
            'Minimal gear changes'
        ]
    },
    'moderate': {
        'rating': 5,
        'criteria': [
            'Had a trial (any result)',
            'Spell length acceptable',
            'Weight reasonable'
        ]
    },
    'concerning': {
        'rating': 3,
        'criteria': [
            'No trial',
            'Long spell (>120 days) OR very short (<14 days)',
            'Weight concerns',
            'Multiple gear changes'
        ]
    }
}
```

**Calculate Fitness Rating:**
```python
def calculate_fitness_rating(horse_data):
    """Calculate numerical fitness rating (1-10)"""

    base_rating = 5  # Start at neutral

    # Trial performance (+3 to -1)
    if horse_data.get('trial_data'):
        trial = horse_data['trial_data']
        if trial['finish_position'] == 1:
            base_rating += 3
        elif trial['finish_position'] <= 3:
            base_rating += 2
        elif trial['finish_position'] <= 5:
            base_rating += 1
        else:
            base_rating -= 1
    else:
        base_rating -= 2  # No trial = fitness question mark

    # Spell length (+2 to -2)
    days_since = horse_data.get('days_since_last_run', 30)
    if 30 <= days_since <= 60:
        base_rating += 2  # Optimal spell
    elif 20 <= days_since < 30 or 60 < days_since <= 90:
        base_rating += 1  # Acceptable spell
    elif days_since < 14:
        base_rating -= 2  # Too short (backing up)
    elif days_since > 120:
        base_rating -= 1  # Long spell, fitness uncertain

    # Weight carried pattern (+1 to -1)
    if horse_data.get('weight_trend'):
        if horse_data['weight_trend'] == 'stable':
            base_rating += 1
        elif horse_data['weight_trend'] == 'decreasing':
            base_rating -= 1

    # Gear stability (+1 to -1)
    if horse_data.get('gear_changes', 0) == 0:
        base_rating += 1
    elif horse_data.get('gear_changes', 0) > 1:
        base_rating -= 1

    # Cap rating at 1-10
    return max(1, min(base_rating, 10))

def calculate_preparation_quality_score(horse_data):
    """Calculate overall preparation quality (0-100)"""

    fitness_rating = calculate_fitness_rating(horse_data)

    # Components
    trial_score = 0
    if horse_data.get('trial_data'):
        trial_score = horse_data['trial_data'].get('trial_performance_score', 50)
    else:
        trial_score = 30  # Penalty for no trial

    spell_score = 0
    days_since = horse_data.get('days_since_last_run', 30)
    if 30 <= days_since <= 60:
        spell_score = 100
    elif 20 <= days_since < 30 or 60 < days_since <= 90:
        spell_score = 75
    elif 14 <= days_since < 20:
        spell_score = 50
    else:
        spell_score = 30

    # Weighted average
    preparation_score = (
        fitness_rating * 10 * 0.4 +  # Fitness rating (converted to 0-100)
        trial_score * 0.35 +          # Trial performance
        spell_score * 0.25            # Spell appropriateness
    )

    return max(20, min(preparation_score, 100))
```

**Quantitative Features:**
```python
def engineer_fitness_features(horse_data):
    """Create fitness and conditioning features"""

    fitness_rating = calculate_fitness_rating(horse_data)
    prep_score = calculate_preparation_quality_score(horse_data)

    features = {
        'fitness_rating': fitness_rating,
        'preparation_quality_score': prep_score,

        # Categorical fitness
        'fitness_category': 'excellent' if fitness_rating >= 8 else
                           'good' if fitness_rating >= 6 else
                           'moderate' if fitness_rating >= 4 else
                           'concerning',

        # Binary flags
        'is_fit': 1 if fitness_rating >= 7 else 0,
        'is_well_prepared': 1 if prep_score >= 70 else 0,
        'has_fitness_concerns': 1 if fitness_rating <= 4 else 0,

        # Component scores
        'has_recent_trial': 1 if horse_data.get('trial_data') else 0,
        'optimal_spell_length': 1 if 30 <= horse_data.get('days_since_last_run', 30) <= 60 else 0
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Fitness rating 9/10: won trial impressively 10 days ago, ideal 45-day spell, weight stable at 495kg..."
- Reasoning: "Excellent preparation, horse is fit and ready to perform"
- Output: Fitness confidence boost (+12-15% if fitness rating 8+)

---

### 16.2 Peak Performance Window (Enhanced)
**Description:** Whether horse is in peak age/maturity window
**Data Type:** Age-based + Recent form trend
**Prediction Impact:** 5-8%

**Peak Performance Analysis:**
```python
def calculate_peak_performance_window(horse_age, horse_history):
    """Calculate if horse is in peak performance window"""

    # Peak age ranges by horse type
    PEAK_AGE_RANGES = {
        'sprinter': (4, 7),      # Peak 4-7 years old
        'miler': (4, 8),         # Peak 4-8 years old
        'stayer': (5, 9),        # Peak 5-9 years old (develop later)
        'unknown': (4, 8)        # Default
    }

    # Determine horse type from history
    avg_distance = np.mean([r['distance'] for r in horse_history]) if horse_history else 1600
    horse_type = 'sprinter' if avg_distance < 1400 else 'stayer' if avg_distance > 1800 else 'miler'

    peak_range = PEAK_AGE_RANGES[horse_type]

    # Calculate peak window index (0-1, 1 = optimal age)
    if peak_range[0] <= horse_age <= peak_range[1]:
        # In peak window
        midpoint = (peak_range[0] + peak_range[1]) / 2
        distance_from_midpoint = abs(horse_age - midpoint)
        peak_index = 1.0 - (distance_from_midpoint / (peak_range[1] - peak_range[0]))
    elif horse_age < peak_range[0]:
        # Developing (below peak)
        years_below = peak_range[0] - horse_age
        peak_index = max(0.5, 1.0 - (years_below * 0.15))
    else:
        # Declining (above peak)
        years_above = horse_age - peak_range[1]
        peak_index = max(0.3, 1.0 - (years_above * 0.12))

    return {
        'horse_age': horse_age,
        'horse_type': horse_type,
        'peak_age_range': peak_range,
        'peak_window_index': round(peak_index, 2),
        'in_peak_window': peak_range[0] <= horse_age <= peak_range[1],
        'maturity_status': 'peak' if peak_range[0] <= horse_age <= peak_range[1] else
                          'developing' if horse_age < peak_range[0] else
                          'veteran'
    }
```

**Quantitative Features:**
```python
def engineer_peak_window_features(peak_data):
    """Create peak performance window features"""

    features = {
        'horse_age': peak_data['horse_age'],
        'peak_window_index': peak_data['peak_window_index'],
        'in_peak_window': 1 if peak_data['in_peak_window'] else 0,
        'maturity_status': peak_data['maturity_status'],
        'horse_type': peak_data['horse_type'],

        # Binary flags
        'is_prime_age': 1 if peak_data['in_peak_window'] else 0,
        'is_developing': 1 if peak_data['maturity_status'] == 'developing' else 0,
        'is_veteran': 1 if peak_data['maturity_status'] == 'veteran' else 0
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "5-year-old miler in prime age window (peak 4-8), peak performance index 0.95..."
- Reasoning: "Optimal age for miler, in prime condition"
- Output: Age suitability context (neutral to +5-8% if in peak window)

---

### 16.3 Horse Temperament & Race Day Demeanor
**Description:** Behavioral indicators from parade/mounting yard
**Data Type:** Qualitative observations
**Prediction Impact:** 3-5%

**Temperament Indicators:**
```python
def analyze_race_day_demeanor(observations):
    """Analyze horse behavior on race day (if available)"""

    # This data typically comes from:
    # - Stewards reports
    # - Parade ring observations
    # - Mounting yard behavior
    # - Pre-race commentary

    concern_flags = []
    positive_flags = []

    keywords_concern = [
        'sweating', 'fractious', 'difficult', 'agitated',
        'refused to load', 'kicked barrier', 'difficult parade'
    ]

    keywords_positive = [
        'relaxed', 'calm', 'professional', 'well-behaved',
        'alert', 'bright', 'on toes'
    ]

    obs_lower = observations.lower()

    for keyword in keywords_concern:
        if keyword in obs_lower:
            concern_flags.append(keyword)

    for keyword in keywords_positive:
        if keyword in obs_lower:
            positive_flags.append(keyword)

    if concern_flags:
        demeanor = 'concerning'
        impact = -0.05  # 5% penalty
    elif positive_flags:
        demeanor = 'positive'
        impact = +0.03  # 3% boost
    else:
        demeanor = 'neutral'
        impact = 0.0

    return {
        'demeanor': demeanor,
        'impact': impact,
        'concern_flags': concern_flags,
        'positive_flags': positive_flags
    }
```

**Qualitative Usage (GPT-5):**
- Context: "Stewards noted horse was 'fractious in barriers and sweating up'..."
- Reasoning: "Behavioral concerns indicate stress, may impact performance"
- Output: Temperament concern flag (reduce confidence -5-8% if concerning behavior)

---

## INTEGRATION GUIDELINES

### Category 15-16 Cross-Integration

**Track/Distance Suitability + Fitness:**
```python
def analyze_suitability_fitness_synergy(venue_data, distance_data, fitness_data):
    """Analyze combined impact of suitability and fitness"""

    # Best case: Venue specialist + distance specialist + fit
    if (venue_data.get('venue_specialist', False) and
        distance_data.get('distance_specialist', False) and
        fitness_data['fitness_rating'] >= 8):
        return {
            'synergy_score': 0.25,  # 25% boost
            'confidence': 'very_high',
            'narrative': 'Proven specialist at venue/distance, excellent fitness'
        }

    # Good case: One specialist + fit
    elif ((venue_data.get('venue_specialist', False) or distance_data.get('distance_specialist', False)) and
          fitness_data['fitness_rating'] >= 7):
        return {
            'synergy_score': 0.15,  # 15% boost
            'confidence': 'high',
            'narrative': 'Suited to conditions and well-prepared'
        }

    return {
        'synergy_score': 0.0,
        'confidence': 'neutral',
        'narrative': 'No strong suitability/fitness synergy'
    }
```

---

## UNIFIED DATA MODEL

```python
suitability_intangibles_schema = {
    "track_distance_suitability": {
        "venue_win_pct": float,
        "venue_specialist": bool,
        "distance_win_pct": float,
        "distance_specialist": bool,
        "at_optimal_distance": bool,
        "combo_specialist": bool
    },
    "intangibles": {
        "fitness_rating": int,
        "preparation_quality_score": float,
        "is_fit": bool,
        "peak_window_index": float,
        "in_peak_window": bool,
        "maturity_status": str,
        "demeanor": str
    }
}
```

---

## COST ANALYSIS

**Categories 15-16 Cost Breakdown:**
- **Venue/distance analysis:** $0 (derived from historical data)
- **Fitness indicators:** $0 (derived from trials + form)
- **Demeanor observations:** $0 (optional from stewards/commentary)

**Total Cost:** $0 per race

---

**Document Complete: Categories 15-16 (Track/Distance Suitability & Intangibles - Enhanced)**
**Next Document: PART_11_CATEGORY_17.md (Jockey-Trainer-Horse Chemistry)**
