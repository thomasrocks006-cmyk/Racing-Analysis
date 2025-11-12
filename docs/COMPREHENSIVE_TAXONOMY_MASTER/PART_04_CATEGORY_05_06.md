# Master Taxonomy - Part 4: Categories 5-6 (Weight & Jockey)

**Document Purpose:** Implementation reference for weight carried and jockey performance analysis
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (feature engineering)
**Implementation Priority:** Phase 1 Week 2

---

## CATEGORY 5: WEIGHT

### Overview
- **Category ID:** 5
- **Prediction Power:** 5-10% (moderate impact, especially in handicaps)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 2
- **Cost per Race:** $0 (public data)
- **ChatGPT Access:** 90%
- **Our Target Access:** 100%

### Subcategories

#### 5.1 Weight Carried
**Description:** Total weight carried by horse (kg) including jockey, saddle, gear
**Data Type:** Float (kg)
**Prediction Impact:** 5-8%

**Sources:**
- Racing.com form guide (Tier 1, 100% coverage)
- Tab.com.au (Tier 3, 100% coverage)

**Access Method:**
```python
def extract_weight_carried(race_url, horse_name):
    """Extract weight for specific horse"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    horse_rows = soup.find_all('div', class_='runner-row')
    for row in horse_rows:
        name = row.find('span', class_='horse-name').text
        if name == horse_name:
            weight_element = row.find('span', class_='weight')
            weight_text = weight_element.text  # e.g., "58.5kg"
            weight_kg = float(weight_text.replace('kg', ''))
            return weight_kg
    return None
```

**Quantitative Features:**
```python
def engineer_weight_features(weight_kg, horse_history, race_class):
    """Create weight features"""
    features = {
        'weight_carried': weight_kg,
        'weight_category': 'heavy' if weight_kg > 58 else 'moderate' if weight_kg > 54 else 'light',
        'horse_avg_weight_carried': np.mean([r['weight'] for r in horse_history]),
        'weight_vs_average': weight_kg - np.mean([r['weight'] for r in horse_history]),
        'is_topweight': 0,  # Set in race-level processing
        'is_lightweight': 1 if weight_kg < 54 else 0
    }
    return features
```

#### 5.2 Weight Differentials
**Description:** Weight comparison across field (topweight, lightweight, spreads)
**Data Type:** Derived numeric
**Prediction Impact:** 3-5%

**Feature Engineering:**
```python
def calculate_weight_differentials(all_weights):
    """Calculate weight spreads and differentials"""
    weights = list(all_weights.values())

    return {
        'topweight_kg': max(weights),
        'lightweight_kg': min(weights),
        'weight_spread': max(weights) - min(weights),
        'weight_median': np.median(weights),
        'weight_mean': np.mean(weights)
    }

def assign_weight_position(horse_weight, weight_differentials):
    """Assign weight position flags"""
    return {
        'is_topweight': 1 if horse_weight == weight_differentials['topweight_kg'] else 0,
        'is_lightweight': 1 if horse_weight == weight_differentials['lightweight_kg'] else 0,
        'weight_vs_topweight': weight_differentials['topweight_kg'] - horse_weight,
        'weight_vs_median': horse_weight - weight_differentials['weight_median']
    }
```

---

## CATEGORY 6: JOCKEY

### Overview
- **Category ID:** 6
- **Prediction Power:** 8-15% (highly skilled jockeys significantly outperform)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 2
- **Cost per Race:** $0 (public data)
- **ChatGPT Access:** 85%
- **Our Target Access:** 100%

### Subcategories

#### 6.1 Jockey Identity & Statistics
**Description:** Jockey name and career statistics
**Data Type:** String + Numeric stats
**Prediction Impact:** 10-15%

**Jockey Database Schema:**
```python
jockey_stats_schema = {
    "jockey_name": str,
    "career_wins": int,
    "career_rides": int,
    "career_win_pct": float,
    "career_place_pct": float,
    "season_wins": int,
    "season_rides": int,
    "season_win_pct": float,
    "last_90_days_wins": int,
    "last_90_days_rides": int,
    "last_90_days_win_pct": float,
    "roi": float,  # Return on investment
    "prize_money_total": int
}
```

**Access Method:**
```python
def extract_jockey_info(race_url, horse_name):
    """Extract jockey for specific horse"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    horse_rows = soup.find_all('div', class_='runner-row')
    for row in horse_rows:
        name = row.find('span', class_='horse-name').text
        if name == horse_name:
            jockey_element = row.find('span', class_='jockey-name')
            jockey_name = jockey_element.text
            return jockey_name
    return None

def get_jockey_statistics(jockey_name):
    """Query jockey statistics database"""
    query = f"""
    SELECT
        COUNT(*) as career_rides,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as career_wins,
        AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct,
        AVG(CASE WHEN position <= 3 THEN 1.0 ELSE 0.0 END) as place_pct
    FROM race_results
    WHERE jockey = '{jockey_name}'
    """
    result = execute_query(query)

    # Get recent form (last 90 days)
    recent_query = f"""
    SELECT
        COUNT(*) as rides,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins
    FROM race_results
    WHERE jockey = '{jockey_name}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 90 DAY)
    """
    recent = execute_query(recent_query)

    return {
        'career_rides': result['career_rides'],
        'career_wins': result['career_wins'],
        'career_win_pct': result['win_pct'],
        'career_place_pct': result['place_pct'],
        'last_90_days_rides': recent['rides'],
        'last_90_days_wins': recent['wins'],
        'last_90_days_win_pct': recent['wins'] / recent['rides'] if recent['rides'] > 0 else 0
    }
```

**Quantitative Features:**
```python
def engineer_jockey_features(jockey_stats):
    """Create jockey features"""
    features = {
        'jockey_career_win_pct': jockey_stats['career_win_pct'],
        'jockey_career_place_pct': jockey_stats['career_place_pct'],
        'jockey_recent_win_pct': jockey_stats['last_90_days_win_pct'],
        'jockey_career_rides': jockey_stats['career_rides'],
        'jockey_experience': 'elite' if jockey_stats['career_rides'] > 5000 else
                            'experienced' if jockey_stats['career_rides'] > 1000 else
                            'developing' if jockey_stats['career_rides'] > 200 else
                            'apprentice',
        'jockey_form_trend': jockey_stats['last_90_days_win_pct'] - jockey_stats['career_win_pct'],
        'is_elite_jockey': 1 if jockey_stats['career_win_pct'] > 0.15 else 0
    }
    return features
```

#### 6.2 Jockey Venue/Distance Specialization
**Description:** Jockey performance at specific venues and distances
**Data Type:** Numeric statistics by venue/distance
**Prediction Impact:** 5-8%

**Venue Specialization Query:**
```python
def get_jockey_venue_stats(jockey_name, venue):
    """Get jockey statistics at specific venue"""
    query = f"""
    SELECT
        COUNT(*) as rides,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins,
        AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct
    FROM race_results
    WHERE jockey = '{jockey_name}'
      AND venue = '{venue}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 2 YEAR)
    """
    result = execute_query(query)
    return {
        'jockey_venue_rides': result['rides'],
        'jockey_venue_wins': result['wins'],
        'jockey_venue_win_pct': result['win_pct']
    }

def get_jockey_distance_stats(jockey_name, distance):
    """Get jockey statistics at specific distance category"""
    # Categorize distance
    if distance < 1400:
        distance_cat = 'sprint'
    elif distance < 1800:
        distance_cat = 'mile'
    else:
        distance_cat = 'staying'

    query = f"""
    SELECT
        COUNT(*) as rides,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins
    FROM race_results
    WHERE jockey = '{jockey_name}'
      AND distance {'< 1400' if distance_cat == 'sprint' else
                    'BETWEEN 1400 AND 1799' if distance_cat == 'mile' else
                    '>= 1800'}
      AND race_date > DATE_SUB(NOW(), INTERVAL 2 YEAR)
    """
    result = execute_query(query)
    return {
        'jockey_distance_rides': result['rides'],
        'jockey_distance_wins': result['wins'],
        'jockey_distance_win_pct': result['wins'] / result['rides'] if result['rides'] > 0 else 0
    }
```

---

## INTEGRATION GUIDELINES

### Category 5-6 Cross-Integration

**Weight-Jockey Interaction:**
```python
def analyze_weight_jockey_interaction(weight_kg, jockey_stats, horse_weight_history):
    """Analyze if jockey handles weight well"""

    # Calculate jockey's performance with various weights
    heavy_weight_query = f"""
    SELECT AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct
    FROM race_results
    WHERE jockey = '{jockey_stats['jockey_name']}'
      AND weight_carried > 57
    """

    light_weight_query = f"""
    SELECT AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct
    FROM race_results
    WHERE jockey = '{jockey_stats['jockey_name']}'
      AND weight_carried < 54
    """

    heavy_result = execute_query(heavy_weight_query)
    light_result = execute_query(light_weight_query)

    return {
        'jockey_heavy_weight_win_pct': heavy_result['win_pct'],
        'jockey_light_weight_win_pct': light_result['win_pct'],
        'jockey_weight_versatility': abs(heavy_result['win_pct'] - light_result['win_pct'])
    }
```

### Validation Rules

```python
def validate_weight_jockey_data(weight_data, jockey_data):
    """Validate categories 5-6"""
    errors = []
    warnings = []

    # Weight validation
    if weight_data['weight_carried'] < 50 or weight_data['weight_carried'] > 65:
        errors.append(f"Weight {weight_data['weight_carried']}kg out of normal range (50-65kg)")

    # Jockey validation
    if jockey_data['career_rides'] < 10:
        warnings.append("Very inexperienced jockey (<10 career rides)")

    if jockey_data['last_90_days_rides'] == 0:
        warnings.append("Jockey has no rides in last 90 days (inactive?)")

    return {'errors': errors, 'warnings': warnings}
```

---

## UNIFIED DATA MODEL

```python
weight_jockey_schema = {
    "weight": {
        "carried": float,
        "category": str,
        "vs_average": float,
        "vs_topweight": float,
        "is_topweight": bool,
        "is_lightweight": bool
    },
    "jockey": {
        "name": str,
        "career_win_pct": float,
        "recent_win_pct": float,
        "venue_win_pct": float,
        "distance_win_pct": float,
        "experience": str,
        "is_elite": bool,
        "form_trend": float
    }
}
```

---

**Document Complete: Categories 5-6 (Weight & Jockey)**
**Next Document: PART_05_CATEGORY_07.md (Trainer)**
