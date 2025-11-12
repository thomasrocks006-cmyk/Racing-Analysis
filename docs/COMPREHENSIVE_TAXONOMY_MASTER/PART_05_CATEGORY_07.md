# Master Taxonomy - Part 5: Category 7 (Trainer)

**Document Purpose:** Implementation reference for trainer performance analysis
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (feature engineering)
**Implementation Priority:** Phase 1 Week 2

---

## CATEGORY 7: TRAINER

### Overview
- **Category ID:** 7
- **Prediction Power:** 10-18% (trainers are critical to horse performance)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 2
- **Cost per Race:** $0 (public data)
- **ChatGPT Access:** 80%
- **Our Target Access:** 100%

---

## SUBCATEGORIES

### 7.1 Trainer Identity & Career Statistics
**Description:** Trainer name and comprehensive career statistics
**Data Type:** String + Numeric stats
**Prediction Impact:** 12-18%

**Trainer Database Schema:**
```python
trainer_stats_schema = {
    "trainer_name": str,
    "career_wins": int,
    "career_starts": int,
    "career_win_pct": float,
    "career_place_pct": float,
    "season_wins": int,
    "season_starts": int,
    "season_win_pct": float,
    "last_90_days_wins": int,
    "last_90_days_starts": int,
    "last_90_days_win_pct": float,
    "roi": float,
    "prize_money_total": int,
    "group_1_wins": int,
    "stable_size": int
}
```

**Access Method:**
```python
def extract_trainer_info(race_url, horse_name):
    """Extract trainer for specific horse"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    horse_rows = soup.find_all('div', class_='runner-row')
    for row in horse_rows:
        name = row.find('span', class_='horse-name').text
        if name == horse_name:
            trainer_element = row.find('span', class_='trainer-name')
            trainer_name = trainer_element.text
            return trainer_name
    return None

def get_trainer_statistics(trainer_name):
    """Query trainer statistics database"""
    # Career stats
    career_query = f"""
    SELECT
        COUNT(*) as career_starts,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as career_wins,
        AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct,
        AVG(CASE WHEN position <= 3 THEN 1.0 ELSE 0.0 END) as place_pct,
        SUM(prize_money) as total_prize_money
    FROM race_results
    WHERE trainer = '{trainer_name}'
    """
    career = execute_query(career_query)

    # Season stats
    season_query = f"""
    SELECT
        COUNT(*) as starts,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND race_date >= '{get_season_start_date()}'
    """
    season = execute_query(season_query)

    # Recent form
    recent_query = f"""
    SELECT
        COUNT(*) as starts,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 90 DAY)
    """
    recent = execute_query(recent_query)

    # Group 1 wins
    group1_query = f"""
    SELECT COUNT(*) as group1_wins
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND position = 1
      AND race_class = 'Group 1'
    """
    group1 = execute_query(group1_query)

    return {
        'career_starts': career['career_starts'],
        'career_wins': career['career_wins'],
        'career_win_pct': career['win_pct'],
        'career_place_pct': career['place_pct'],
        'prize_money_total': career['total_prize_money'],
        'season_starts': season['starts'],
        'season_wins': season['wins'],
        'season_win_pct': season['wins'] / season['starts'] if season['starts'] > 0 else 0,
        'last_90_days_starts': recent['starts'],
        'last_90_days_wins': recent['wins'],
        'last_90_days_win_pct': recent['wins'] / recent['starts'] if recent['starts'] > 0 else 0,
        'group_1_wins': group1['group1_wins']
    }
```

**Quantitative Features:**
```python
def engineer_trainer_features(trainer_stats):
    """Create trainer features"""
    features = {
        'trainer_career_win_pct': trainer_stats['career_win_pct'],
        'trainer_career_place_pct': trainer_stats['career_place_pct'],
        'trainer_season_win_pct': trainer_stats['season_win_pct'],
        'trainer_recent_win_pct': trainer_stats['last_90_days_win_pct'],
        'trainer_career_starts': trainer_stats['career_starts'],
        'trainer_group1_wins': trainer_stats['group_1_wins'],
        'trainer_prize_money': trainer_stats['prize_money_total'],

        # Experience categorization
        'trainer_experience': classify_trainer_experience(trainer_stats['career_starts']),

        # Form trend
        'trainer_form_trend': trainer_stats['last_90_days_win_pct'] - trainer_stats['career_win_pct'],

        # Elite trainer flag
        'is_elite_trainer': 1 if trainer_stats['career_win_pct'] > 0.18 or trainer_stats['group_1_wins'] > 5 else 0,

        # In-form trainer flag
        'is_inform_trainer': 1 if trainer_stats['last_90_days_win_pct'] > trainer_stats['career_win_pct'] * 1.2 else 0
    }
    return features

def classify_trainer_experience(career_starts):
    """Classify trainer by experience level"""
    if career_starts > 10000:
        return 'legendary'
    elif career_starts > 5000:
        return 'elite'
    elif career_starts > 2000:
        return 'experienced'
    elif career_starts > 500:
        return 'established'
    else:
        return 'developing'
```

---

### 7.2 Trainer Venue Specialization
**Description:** Trainer performance at specific racecourses
**Data Type:** Numeric statistics by venue
**Prediction Impact:** 6-10%

**Venue Specialization Analysis:**
```python
def get_trainer_venue_stats(trainer_name, venue):
    """Get trainer statistics at specific venue"""
    query = f"""
    SELECT
        COUNT(*) as starts,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins,
        AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct,
        AVG(CASE WHEN position <= 3 THEN 1.0 ELSE 0.0 END) as place_pct
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND venue = '{venue}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 3 YEAR)
    """
    result = execute_query(query)

    return {
        'trainer_venue_starts': result['starts'],
        'trainer_venue_wins': result['wins'],
        'trainer_venue_win_pct': result['win_pct'],
        'trainer_venue_place_pct': result['place_pct']
    }

def engineer_trainer_venue_features(trainer_stats, venue_stats, trainer_career_win_pct):
    """Create trainer venue features"""
    features = {
        'trainer_venue_win_pct': venue_stats['trainer_venue_win_pct'],
        'trainer_venue_starts': venue_stats['trainer_venue_starts'],
        'trainer_venue_vs_overall': venue_stats['trainer_venue_win_pct'] - trainer_career_win_pct,
        'is_venue_specialist': 1 if venue_stats['trainer_venue_win_pct'] > trainer_career_win_pct * 1.3 else 0,
        'venue_stats_confidence': 'high' if venue_stats['trainer_venue_starts'] > 50 else
                                  'medium' if venue_stats['trainer_venue_starts'] > 20 else
                                  'low'
    }
    return features
```

---

### 7.3 Trainer Distance Specialization
**Description:** Trainer performance at specific distance ranges
**Data Type:** Numeric statistics by distance category
**Prediction Impact:** 5-8%

**Distance Specialization Analysis:**
```python
def get_trainer_distance_stats(trainer_name, distance):
    """Get trainer statistics at specific distance category"""
    # Categorize distance
    if distance < 1400:
        distance_cat = 'sprint'
        distance_filter = '< 1400'
    elif distance < 1800:
        distance_cat = 'mile'
        distance_filter = 'BETWEEN 1400 AND 1799'
    else:
        distance_cat = 'staying'
        distance_filter = '>= 1800'

    query = f"""
    SELECT
        COUNT(*) as starts,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins,
        AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND distance {distance_filter}
      AND race_date > DATE_SUB(NOW(), INTERVAL 3 YEAR)
    """
    result = execute_query(query)

    return {
        'distance_category': distance_cat,
        'trainer_distance_starts': result['starts'],
        'trainer_distance_wins': result['wins'],
        'trainer_distance_win_pct': result['win_pct']
    }

def engineer_trainer_distance_features(distance_stats, trainer_career_win_pct):
    """Create trainer distance features"""
    features = {
        'trainer_distance_win_pct': distance_stats['trainer_distance_win_pct'],
        'trainer_distance_starts': distance_stats['trainer_distance_starts'],
        'trainer_distance_vs_overall': distance_stats['trainer_distance_win_pct'] - trainer_career_win_pct,
        'is_distance_specialist': 1 if distance_stats['trainer_distance_win_pct'] > trainer_career_win_pct * 1.25 else 0
    }
    return features
```

---

### 7.4 Trainer Race Class Performance
**Description:** Trainer performance by race class (Group 1, Listed, Maiden, etc.)
**Data Type:** Numeric statistics by race class
**Prediction Impact:** 4-7%

**Race Class Specialization:**
```python
def get_trainer_class_stats(trainer_name, race_class):
    """Get trainer statistics at specific race class"""
    query = f"""
    SELECT
        COUNT(*) as starts,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins,
        AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND race_class = '{race_class}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 3 YEAR)
    """
    result = execute_query(query)

    return {
        'trainer_class_starts': result['starts'],
        'trainer_class_wins': result['wins'],
        'trainer_class_win_pct': result['win_pct']
    }

def engineer_trainer_class_features(class_stats, trainer_career_win_pct):
    """Create trainer class features"""
    features = {
        'trainer_class_win_pct': class_stats['trainer_class_win_pct'],
        'trainer_class_starts': class_stats['trainer_class_starts'],
        'trainer_class_vs_overall': class_stats['trainer_class_win_pct'] - trainer_career_win_pct,
        'trainer_class_competence': 'strong' if class_stats['trainer_class_win_pct'] > trainer_career_win_pct else 'weak'
    }
    return features
```

---

### 7.5 Trainer Preparation Patterns
**Description:** Trainer patterns for preparing horses (days since last run, first-up performance, etc.)
**Data Type:** Derived statistics
**Prediction Impact:** 5-9%

**Preparation Pattern Analysis:**
```python
def get_trainer_preparation_stats(trainer_name):
    """Analyze trainer's preparation patterns"""

    # First-up performance
    firstup_query = f"""
    SELECT
        COUNT(*) as starts,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins,
        AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND is_first_up = 1
      AND race_date > DATE_SUB(NOW(), INTERVAL 2 YEAR)
    """
    firstup = execute_query(firstup_query)

    # Second-up performance
    secondup_query = f"""
    SELECT
        COUNT(*) as starts,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND is_second_up = 1
      AND race_date > DATE_SUB(NOW(), INTERVAL 2 YEAR)
    """
    secondup = execute_query(secondup_query)

    # Optimal spell length
    spell_query = f"""
    SELECT
        CASE
            WHEN days_since_last_run < 21 THEN 'short'
            WHEN days_since_last_run < 90 THEN 'normal'
            ELSE 'long'
        END as spell_category,
        AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct,
        COUNT(*) as starts
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 2 YEAR)
    GROUP BY spell_category
    """
    spell_results = execute_query(spell_query)

    return {
        'trainer_firstup_win_pct': firstup['win_pct'],
        'trainer_firstup_starts': firstup['starts'],
        'trainer_secondup_win_pct': secondup['wins'] / secondup['starts'] if secondup['starts'] > 0 else 0,
        'trainer_secondup_starts': secondup['starts'],
        'trainer_spell_patterns': spell_results
    }

def engineer_trainer_preparation_features(prep_stats, horse_days_since_last, is_first_up):
    """Create trainer preparation features"""
    features = {
        'trainer_firstup_win_pct': prep_stats['trainer_firstup_win_pct'],
        'trainer_secondup_win_pct': prep_stats['trainer_secondup_win_pct'],

        # Match flags
        'trainer_firstup_strong': 1 if prep_stats['trainer_firstup_win_pct'] > 0.12 else 0,
        'is_firstup_with_strong_trainer': 1 if is_first_up and prep_stats['trainer_firstup_win_pct'] > 0.12 else 0
    }

    # Find optimal spell for this trainer
    spell_patterns = prep_stats['trainer_spell_patterns']
    best_spell = max(spell_patterns, key=lambda x: x['win_pct']) if spell_patterns else None
    if best_spell:
        features['trainer_optimal_spell'] = best_spell['spell_category']

        # Check if current spell matches optimal
        current_spell = 'short' if horse_days_since_last < 21 else 'normal' if horse_days_since_last < 90 else 'long'
        features['is_optimal_spell_pattern'] = 1 if current_spell == best_spell['spell_category'] else 0

    return features
```

---

## INTEGRATION GUIDELINES

### Category 7 Cross-Category Integration

**Trainer-Jockey Combinations:**
```python
def get_trainer_jockey_combination_stats(trainer_name, jockey_name):
    """Analyze trainer-jockey partnership"""
    query = f"""
    SELECT
        COUNT(*) as combinations,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins,
        AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND jockey = '{jockey_name}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 2 YEAR)
    """
    result = execute_query(query)

    return {
        'trainer_jockey_combinations': result['combinations'],
        'trainer_jockey_wins': result['wins'],
        'trainer_jockey_win_pct': result['win_pct'],
        'is_established_partnership': 1 if result['combinations'] > 20 else 0
    }
```

**Trainer-Venue-Distance Specialization:**
```python
def get_trainer_venue_distance_stats(trainer_name, venue, distance):
    """Get highly specific trainer stats (venue + distance)"""
    query = f"""
    SELECT
        COUNT(*) as starts,
        SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as wins
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND venue = '{venue}'
      AND ABS(distance - {distance}) < 100
      AND race_date > DATE_SUB(NOW(), INTERVAL 3 YEAR)
    """
    result = execute_query(query)

    return {
        'trainer_venue_distance_starts': result['starts'],
        'trainer_venue_distance_wins': result['wins'],
        'trainer_venue_distance_win_pct': result['wins'] / result['starts'] if result['starts'] > 0 else 0
    }
```

### Validation Rules

```python
def validate_trainer_data(trainer_data):
    """Validate category 7 data"""
    errors = []
    warnings = []

    # Career stats validation
    if trainer_data['career_starts'] < 50:
        warnings.append("Very inexperienced trainer (<50 career starts)")

    if trainer_data['last_90_days_starts'] == 0:
        warnings.append("Trainer has no starters in last 90 days (inactive?)")

    # Win percentage validation
    if trainer_data['career_win_pct'] > 0.40:
        warnings.append(f"Unusually high win % ({trainer_data['career_win_pct']:.1%}), verify data")

    if trainer_data['career_win_pct'] < 0.03 and trainer_data['career_starts'] > 500:
        warnings.append("Very low win % for experienced trainer, verify quality")

    return {'errors': errors, 'warnings': warnings}
```

---

## UNIFIED DATA MODEL

```python
trainer_schema = {
    "trainer": {
        "name": str,
        "career_win_pct": float,
        "career_place_pct": float,
        "season_win_pct": float,
        "recent_win_pct": float,
        "career_starts": int,
        "group1_wins": int,
        "experience": str,
        "is_elite": bool,
        "form_trend": float
    },
    "trainer_venue": {
        "venue_win_pct": float,
        "venue_starts": int,
        "vs_overall": float,
        "is_specialist": bool
    },
    "trainer_distance": {
        "distance_win_pct": float,
        "distance_starts": int,
        "vs_overall": float,
        "is_specialist": bool
    },
    "trainer_class": {
        "class_win_pct": float,
        "class_starts": int,
        "competence": str
    },
    "trainer_preparation": {
        "firstup_win_pct": float,
        "secondup_win_pct": float,
        "optimal_spell": str,
        "is_optimal_pattern": bool
    }
}
```

---

## COST ANALYSIS

**Category 7 Cost Breakdown:**
- **Data extraction:** $0 (public data)
- **Database queries:** $0 (internal database)
- **Processing time:** <10 seconds per race

**Total Cost:** $0 per race

---

## IMPLEMENTATION CHECKLIST

### Phase 1 Week 2: Category 7 Implementation

**Day 1: Trainer Career Stats**
- [ ] Implement trainer extraction
- [ ] Build trainer statistics database
- [ ] Implement career stats queries
- [ ] Test on 20 trainers

**Day 2: Venue/Distance Specialization**
- [ ] Implement venue stats queries
- [ ] Implement distance stats queries
- [ ] Calculate specialization scores
- [ ] Validate against known specialists

**Day 3: Preparation Patterns**
- [ ] Implement first-up/second-up analysis
- [ ] Analyze spell patterns
- [ ] Build preparation feature engineering
- [ ] Test on sample races

**Day 4: Feature Engineering & Integration**
- [ ] Implement all feature functions
- [ ] Test trainer-jockey combinations
- [ ] Validate trainer-venue-distance stats
- [ ] Document edge cases

**Day 5: Testing**
- [ ] Full pipeline test on 30 races
- [ ] Cross-validate with Categories 5-6
- [ ] Check data quality and completeness
- [ ] Prepare for Category 8 (Pace)

---

**Document Complete: Category 7 (Trainer)**
**Next Document: PART_06_CATEGORY_08.md (Pace Scenario - Enhanced)**
