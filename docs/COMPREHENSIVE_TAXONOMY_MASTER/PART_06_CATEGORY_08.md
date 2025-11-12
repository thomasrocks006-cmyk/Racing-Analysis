# Master Taxonomy - Part 6: Category 8 (Pace Scenario - Enhanced)

**Document Purpose:** Implementation reference for pace analysis and speed ratings
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (feature engineering)
**Implementation Priority:** Phase 2 Week 1-2 (requires historical data analysis)

---

## CATEGORY 8: PACE SCENARIO

### Overview
- **Category ID:** 8
- **Prediction Power:** 12-22% (highly predictive, especially with quantitative enhancements)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 2 Week 1-2
- **Cost per Race:** $0.05-$0.10 (Speedmaps.com.au optional subscription)
- **ChatGPT Access:** 40% (limited pace analysis, no numerical ratings)
- **Our Target Access:** 90% (comprehensive pace + speed ratings)

### Enhanced Quantitative Coverage
**Status:** ⚠️ Needs Enhancement (currently qualitative-heavy)

**Enhancements Added:**
1. Speed ratings (numerical 1-100 scale per horse)
2. Pace pressure index (0-100 quantifying race tempo)
3. Sectional time analysis (600m, 400m, 200m splits)
4. Run style encoding (categorical + numerical positioning data)

---

## SUBCATEGORIES

### 8.1 Expected Pace
**Description:** Predicted race tempo based on field composition
**Data Type:** Categorical + Numeric (pace_pressure_index)
**Prediction Impact:** 15-22%

**Pace Categories:**
```python
PACE_CATEGORIES = {
    'very_slow': {
        'pace_pressure_index': 20,
        'description': '0-1 genuine leaders, tactical race',
        'favors': 'on_pace_runners',
        'avg_600m_time_1200m': 36.5  # seconds (slow)
    },
    'slow': {
        'pace_pressure_index': 40,
        'description': '1-2 leaders, controlled tempo',
        'favors': 'on_pace_runners',
        'avg_600m_time_1200m': 35.8
    },
    'moderate': {
        'pace_pressure_index': 60,
        'description': '2-3 leaders, genuine pace',
        'favors': 'balanced',
        'avg_600m_time_1200m': 35.2
    },
    'fast': {
        'pace_pressure_index': 80,
        'description': '3-4 leaders, strong pressure',
        'favors': 'backmarkers',
        'avg_600m_time_1200m': 34.6
    },
    'very_fast': {
        'pace_pressure_index': 95,
        'description': '4+ leaders, breakneck speed',
        'favors': 'backmarkers',
        'avg_600m_time_1200m': 34.0  # (fast)
    }
}
```

**Pace Calculation Method:**
```python
def calculate_expected_pace(runner_data, distance):
    """Calculate expected pace based on field composition"""

    # Count run style distribution
    leaders = 0
    stalkers = 0
    midfield = 0
    backmarkers = 0

    for runner in runner_data:
        run_style = runner['typical_run_style']
        if run_style in ['leader', 'front_runner']:
            leaders += 1
        elif run_style in ['stalker', 'on_pace']:
            stalkers += 1
        elif run_style == 'midfield':
            midfield += 1
        else:
            backmarkers += 1

    # Calculate pace pressure
    field_size = len(runner_data)
    leader_percentage = leaders / field_size
    stalker_percentage = stalkers / field_size

    # Pace pressure index formula
    pace_pressure_index = (
        leaders * 20 +           # Each leader adds significant pressure
        stalkers * 10 +          # Stalkers add moderate pressure
        midfield * 3 +           # Midfield minimal pressure
        backmarkers * 0          # Backmarkers no pressure
    )

    # Cap at 100
    pace_pressure_index = min(pace_pressure_index, 100)

    # Categorize pace
    if pace_pressure_index < 30:
        pace_category = 'very_slow'
    elif pace_pressure_index < 50:
        pace_category = 'slow'
    elif pace_pressure_index < 70:
        pace_category = 'moderate'
    elif pace_pressure_index < 85:
        pace_category = 'fast'
    else:
        pace_category = 'very_fast'

    pace_data = PACE_CATEGORIES[pace_category]

    return {
        'pace_category': pace_category,
        'pace_pressure_index': pace_pressure_index,
        'leader_count': leaders,
        'stalker_count': stalkers,
        'midfield_count': midfield,
        'backmarker_count': backmarkers,
        'leader_percentage': leader_percentage,
        'expected_600m_time': pace_data['avg_600m_time_1200m'] if distance == 1200 else None,
        'favors_position': pace_data['favors']
    }
```

**Qualitative Usage (GPT-5):**
- Context: "4 genuine leaders in field, expect fast early pace (pressure index 85)..."
- Reasoning: "Fast pace will tire leaders, favors strong finishers like Horse X"
- Output: Pace suitability adjustment (+15-20% if run style suits pace scenario)

**Quantitative Features:**
```python
def engineer_pace_features(pace_data, horse_run_style):
    """Create pace scenario features"""
    features = {
        'pace_pressure_index': pace_data['pace_pressure_index'],
        'pace_category': pace_data['pace_category'],
        'leader_count': pace_data['leader_count'],
        'stalker_count': pace_data['stalker_count'],
        'leader_percentage': pace_data['leader_percentage'],

        # Horse run style vs pace interaction
        'horse_run_style': horse_run_style,
        'pace_suits_run_style': calculate_pace_run_style_match(
            pace_data['pace_category'],
            horse_run_style
        ),

        # Derived advantage
        'has_pace_advantage': 1 if calculate_pace_run_style_match(
            pace_data['pace_category'], horse_run_style
        ) > 0.7 else 0
    }
    return features

def calculate_pace_run_style_match(pace_category, run_style):
    """Calculate how well run style suits expected pace"""
    # Matching matrix
    PACE_RUNSTYLE_MATRIX = {
        'very_slow': {
            'leader': 0.9,
            'stalker': 0.8,
            'midfield': 0.5,
            'backmarker': 0.3
        },
        'slow': {
            'leader': 0.8,
            'stalker': 0.8,
            'midfield': 0.6,
            'backmarker': 0.5
        },
        'moderate': {
            'leader': 0.7,
            'stalker': 0.8,
            'midfield': 0.7,
            'backmarker': 0.6
        },
        'fast': {
            'leader': 0.4,
            'stalker': 0.5,
            'midfield': 0.7,
            'backmarker': 0.9
        },
        'very_fast': {
            'leader': 0.2,
            'stalker': 0.3,
            'midfield': 0.6,
            'backmarker': 1.0
        }
    }

    return PACE_RUNSTYLE_MATRIX.get(pace_category, {}).get(run_style, 0.5)
```

---

### 8.2 Individual Horse Run Style
**Description:** Each horse's typical racing pattern and positioning
**Data Type:** Categorical + Numeric (avg_settling_position)
**Prediction Impact:** 10-15%

**Run Style Categories:**
```python
RUN_STYLE_CATEGORIES = {
    'leader': {
        'avg_settling_position': 1.5,
        'typical_range': (1, 2),
        'description': 'Leads from start',
        'energy_expenditure': 'high'
    },
    'stalker': {
        'avg_settling_position': 3.5,
        'typical_range': (2, 5),
        'description': 'Just behind leaders',
        'energy_expenditure': 'moderate_high'
    },
    'midfield': {
        'avg_settling_position': 7.0,
        'typical_range': (5, 10),
        'description': 'Settles mid-pack',
        'energy_expenditure': 'moderate'
    },
    'backmarker': {
        'avg_settling_position': 11.0,
        'typical_range': (9, 16),
        'description': 'Settles at rear',
        'energy_expenditure': 'low'
    }
}
```

**Calculate Horse Run Style:**
```python
def calculate_horse_run_style(horse_history):
    """Determine horse's typical run style from history"""

    if not horse_history or len(horse_history) < 3:
        return {
            'run_style': 'unknown',
            'avg_settling_position': None,
            'consistency': 'insufficient_data'
        }

    # Extract settling positions from last 5 starts
    recent_starts = horse_history[:5]
    settling_positions = [r['settling_position'] for r in recent_starts if r.get('settling_position')]

    if not settling_positions:
        return {
            'run_style': 'unknown',
            'avg_settling_position': None,
            'consistency': 'no_data'
        }

    # Calculate average settling position
    avg_settling = np.mean(settling_positions)
    std_settling = np.std(settling_positions)

    # Categorize run style
    if avg_settling <= 2.5:
        run_style = 'leader'
    elif avg_settling <= 5.0:
        run_style = 'stalker'
    elif avg_settling <= 9.0:
        run_style = 'midfield'
    else:
        run_style = 'backmarker'

    # Consistency measure
    if std_settling < 2.0:
        consistency = 'very_consistent'
    elif std_settling < 3.5:
        consistency = 'consistent'
    elif std_settling < 5.0:
        consistency = 'variable'
    else:
        consistency = 'inconsistent'

    return {
        'run_style': run_style,
        'avg_settling_position': avg_settling,
        'settling_position_std': std_settling,
        'consistency': consistency,
        'sample_size': len(settling_positions)
    }
```

**Quantitative Features:**
```python
def engineer_run_style_features(run_style_data):
    """Create run style features"""
    features = {
        'run_style': run_style_data['run_style'],
        'avg_settling_position': run_style_data['avg_settling_position'],
        'settling_position_std': run_style_data['settling_position_std'],
        'run_style_consistency': run_style_data['consistency'],

        # Binary flags
        'is_leader': 1 if run_style_data['run_style'] == 'leader' else 0,
        'is_stalker': 1 if run_style_data['run_style'] == 'stalker' else 0,
        'is_backmarker': 1 if run_style_data['run_style'] == 'backmarker' else 0,

        # Energy expenditure
        'energy_expenditure_category': RUN_STYLE_CATEGORIES.get(
            run_style_data['run_style'], {}
        ).get('energy_expenditure', 'moderate')
    }
    return features
```

---

### 8.3 Speed Ratings (NEW - Enhanced Quantitative)
**Description:** Numerical speed ratings for each horse (1-100 scale)
**Data Type:** Numeric
**Prediction Impact:** 18-25%

**Speed Rating Calculation:**
```python
def calculate_speed_rating(horse_history, distance, track_condition):
    """Calculate speed rating based on recent performances"""

    if not horse_history or len(horse_history) < 2:
        return {
            'speed_rating': 50,  # Default baseline
            'confidence': 'low'
        }

    # Get last 3 starts at similar distance (±200m)
    similar_distance_starts = [
        r for r in horse_history
        if abs(r['distance'] - distance) < 200
    ][:3]

    if not similar_distance_starts:
        # Use all recent starts if no similar distance
        similar_distance_starts = horse_history[:3]

    # Calculate rating for each start
    ratings = []
    for start in similar_distance_starts:
        # Base rating from finish position
        if start['position'] == 1:
            base_rating = 100
        elif start['position'] == 2:
            base_rating = 95
        elif start['position'] == 3:
            base_rating = 90
        elif start['position'] <= 5:
            base_rating = 85 - (start['position'] - 3) * 3
        else:
            base_rating = 75 - (start['position'] - 5) * 2

        # Adjust for race class
        class_adjustment = get_class_adjustment(start['race_class'])

        # Adjust for margin
        margin_adjustment = -min(start.get('margin', 0) * 2, 15)  # Lose up to 15 points for big losses

        # Adjust for track condition
        condition_adjustment = get_condition_adjustment(
            start['track_condition'],
            track_condition
        )

        # Calculate final rating for this start
        rating = base_rating + class_adjustment + margin_adjustment + condition_adjustment
        ratings.append(max(20, min(rating, 120)))  # Cap between 20-120

    # Average the ratings
    avg_rating = np.mean(ratings)
    std_rating = np.std(ratings)

    # Normalize to 1-100 scale
    normalized_rating = max(1, min(avg_rating, 100))

    # Confidence based on consistency
    if std_rating < 5:
        confidence = 'high'
    elif std_rating < 10:
        confidence = 'medium'
    else:
        confidence = 'low'

    return {
        'speed_rating': round(normalized_rating, 1),
        'speed_rating_std': round(std_rating, 1),
        'confidence': confidence,
        'sample_size': len(ratings)
    }

def get_class_adjustment(race_class):
    """Adjust speed rating based on race class"""
    CLASS_ADJUSTMENTS = {
        'Group 1': +15,
        'Group 2': +12,
        'Group 3': +9,
        'Listed': +6,
        'Open Handicap': +3,
        'Benchmark 90+': +2,
        'Benchmark 78': 0,
        'Benchmark 64': -3,
        'Maiden': -5,
        'Class 1': -8
    }
    return CLASS_ADJUSTMENTS.get(race_class, 0)

def get_condition_adjustment(previous_condition, todays_condition):
    """Adjust if track condition significantly different"""
    # Parse condition indices
    prev_index = parse_track_condition(previous_condition)['numeric_index']
    today_index = parse_track_condition(todays_condition)['numeric_index']

    # If similar conditions, no adjustment
    if abs(prev_index - today_index) <= 1:
        return 0

    # If today significantly wetter/dryer, small penalty for uncertainty
    return -abs(prev_index - today_index) * 1.5
```

**Quantitative Features:**
```python
def engineer_speed_rating_features(speed_rating_data, field_ratings):
    """Create speed rating features"""
    features = {
        'speed_rating': speed_rating_data['speed_rating'],
        'speed_rating_std': speed_rating_data['speed_rating_std'],
        'speed_rating_confidence': speed_rating_data['confidence'],

        # Relative to field
        'speed_rating_vs_field_avg': speed_rating_data['speed_rating'] - np.mean(field_ratings),
        'speed_rating_rank': sorted(field_ratings, reverse=True).index(speed_rating_data['speed_rating']) + 1,
        'speed_rating_percentile': 1 - (sorted(field_ratings, reverse=True).index(
            speed_rating_data['speed_rating']
        ) / len(field_ratings)),

        # Binary flags
        'is_top_3_rated': 1 if sorted(field_ratings, reverse=True).index(
            speed_rating_data['speed_rating']
        ) < 3 else 0,
        'is_highest_rated': 1 if speed_rating_data['speed_rating'] == max(field_ratings) else 0
    }
    return features
```

---

### 8.4 Sectional Times (NEW - Enhanced Quantitative)
**Description:** Split times for 600m, 400m, 200m sections
**Data Type:** Numeric (seconds)
**Prediction Impact:** 10-18%

**Sectional Data Schema:**
```python
sectional_schema = {
    "last_600m_time": float,    # seconds
    "last_400m_time": float,
    "last_200m_time": float,
    "first_600m_time": float,   # For longer races
    "closing_sectional_rank": int  # Rank within field for last 600m
}
```

**Sources:**
- Racing.com (Tier 1, 60% coverage, free for select races)
- Punters.com.au (Tier 2, 80% coverage, subscription $25/month)
- Speedmaps.com.au (Tier 2, 90% coverage, subscription $30/month)

**Access Method:**
```python
def extract_sectional_times(horse_name, race_id):
    """Extract sectional times if available"""

    # Try Racing.com first (free)
    racing_url = f"https://racing.com/race/{race_id}/sectionals"
    response = requests.get(racing_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    sectional_table = soup.find('table', class_='sectionals')
    if sectional_table:
        for row in sectional_table.find_all('tr'):
            horse = row.find('td', class_='horse-name')
            if horse and horse.text == horse_name:
                last_600m = float(row.find('td', class_='last-600m').text)
                last_400m = float(row.find('td', class_='last-400m').text)
                last_200m = float(row.find('td', class_='last-200m').text)

                return {
                    'last_600m_time': last_600m,
                    'last_400m_time': last_400m,
                    'last_200m_time': last_200m,
                    'source': 'racing.com'
                }

    # Fallback to Punters (if subscribed)
    # ... similar extraction logic

    # If no sectionals available
    return None

def calculate_sectional_ranking(horse_sectionals, all_sectionals):
    """Rank horse's closing sectional vs field"""
    if not horse_sectionals or not all_sectionals:
        return None

    # Sort by last 600m time (faster = better = lower time)
    sorted_sectionals = sorted(all_sectionals, key=lambda x: x['last_600m_time'])

    # Find horse's rank
    for rank, sectional in enumerate(sorted_sectionals, 1):
        if sectional['horse_name'] == horse_sectionals['horse_name']:
            return rank

    return None
```

**Quantitative Features:**
```python
def engineer_sectional_features(sectional_data, distance):
    """Create sectional time features"""
    if not sectional_data:
        return {
            'has_sectionals': 0,
            'last_600m_time': None,
            'closing_sectional_speed': None
        }

    features = {
        'has_sectionals': 1,
        'last_600m_time': sectional_data['last_600m_time'],
        'last_400m_time': sectional_data['last_400m_time'],
        'last_200m_time': sectional_data['last_200m_time'],
        'closing_sectional_rank': sectional_data.get('closing_sectional_rank'),

        # Calculate speed (m/s)
        'closing_sectional_speed': 600 / sectional_data['last_600m_time'],  # m/s

        # Acceleration (difference between 400-200m and last 200m)
        'acceleration_last_200m': (
            (sectional_data['last_400m_time'] - sectional_data['last_200m_time']) -
            sectional_data['last_200m_time']
        ) if sectional_data['last_400m_time'] and sectional_data['last_200m_time'] else None,

        # Strong finisher flag
        'is_strong_finisher': 1 if sectional_data.get('closing_sectional_rank', 999) <= 3 else 0
    }

    return features
```

---

## INTEGRATION GUIDELINES

### Category 8 Cross-Integration

**Pace + Barrier (Category 4):**
```python
def analyze_pace_barrier_interaction(pace_data, barrier_position, run_style):
    """How pace affects barrier advantage"""

    # Fast pace + wide barrier + backmarker = advantageous (can settle back, save ground)
    # Slow pace + inside barrier + leader = advantageous (control pace from rail)

    if pace_data['pace_category'] in ['fast', 'very_fast']:
        if barrier_position > 8 and run_style == 'backmarker':
            return {'pace_barrier_synergy': 0.85, 'advantage': 'high'}
    elif pace_data['pace_category'] in ['slow', 'very_slow']:
        if barrier_position <= 4 and run_style == 'leader':
            return {'pace_barrier_synergy': 0.90, 'advantage': 'high'}

    return {'pace_barrier_synergy': 0.5, 'advantage': 'neutral'}
```

**Pace + Track Condition (Category 3):**
```python
def analyze_pace_condition_interaction(pace_data, track_condition):
    """How track condition affects pace dynamics"""

    # Heavy track + fast pace = extreme stamina test
    # Firm track + slow pace = sprint finish likely

    track_index = track_condition['numeric_index']
    pace_index = pace_data['pace_pressure_index']

    if track_index >= 7 and pace_index >= 75:
        # Heavy track + fast pace
        return {
            'stamina_demand': 'extreme',
            'pace_condition_interaction': 'high_stamina_test',
            'favors': 'proven_stayers'
        }
    elif track_index <= 3 and pace_index <= 40:
        # Firm track + slow pace
        return {
            'stamina_demand': 'low',
            'pace_condition_interaction': 'sprint_finish',
            'favors': 'strong_sprinters'
        }

    return {
        'stamina_demand': 'moderate',
        'pace_condition_interaction': 'neutral',
        'favors': 'balanced'
    }
```

---

## UNIFIED DATA MODEL

```python
pace_schema = {
    "expected_pace": {
        "pace_category": str,
        "pace_pressure_index": int,
        "leader_count": int,
        "leader_percentage": float,
        "favors_position": str
    },
    "horse_run_style": {
        "run_style": str,
        "avg_settling_position": float,
        "consistency": str,
        "pace_match_score": float
    },
    "speed_rating": {
        "rating": float,
        "std": float,
        "confidence": str,
        "vs_field_avg": float,
        "rank": int
    },
    "sectionals": {
        "has_data": bool,
        "last_600m_time": float,
        "closing_speed": float,
        "rank": int,
        "is_strong_finisher": bool
    }
}
```

---

## COST ANALYSIS

**Category 8 Cost Breakdown:**
- **Pace calculation:** $0 (derived from form)
- **Speed ratings:** $0 (calculated internally)
- **Sectional data (optional):** $25-30/month subscription
  - Racing.com: $0 (60% coverage)
  - Punters/Speedmaps: $25-30/month (80-90% coverage)

**Total Cost:** $0.05-$0.10 per race (if using paid sectionals)

---

**Document Complete: Category 8 (Pace Scenario - Enhanced)**
**Next Document: PART_07_CATEGORY_09_10.md (Gear Changes & Barrier Trials)**
