# Master Taxonomy - Part 11: Category 17 (Jockey-Trainer-Horse Chemistry)

**Document Purpose:** Implementation reference for analyzing partnership synergies and combination statistics
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (partnership features)
**Implementation Priority:** Phase 1 Week 5

---

## CATEGORY 17: CHEMISTRY (JOCKEY-TRAINER-HORSE COMBINATIONS)

### Overview
- **Category ID:** 17
- **Prediction Power:** 8-15% (partnerships can be highly predictive)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 5
- **Cost per Race:** $0 (derived from historical data)
- **ChatGPT Access:** 60%
- **Our Target Access:** 95%

**Key Insight:** Some jockey-trainer-horse combinations significantly outperform expectations. A trainer might have 15% win rate overall but 35% with a specific jockey on a specific horse. This is critical alpha.

---

## SUBCATEGORIES

### 17.1 Jockey-Trainer Partnerships
**Description:** Historical performance of jockey-trainer combinations
**Data Type:** Partnership statistics
**Prediction Impact:** 5-10%

**Partnership Analysis:**
```python
def calculate_jockey_trainer_partnership(jockey, trainer, historical_db):
    """Calculate jockey-trainer partnership performance"""

    # Query all rides where jockey rode for trainer
    partnership_rides = historical_db.query(f"""
        SELECT *
        FROM race_results
        WHERE jockey = '{jockey}'
        AND trainer = '{trainer}'
    """)

    if len(partnership_rides) == 0:
        return {
            'has_partnership_history': False,
            'partnership_rides': 0
        }

    # Calculate partnership statistics
    partnership_wins = partnership_rides['position'].eq(1).sum()
    partnership_places = partnership_rides['position'].le(3).sum()

    partnership_win_pct = partnership_wins / len(partnership_rides)
    partnership_place_pct = partnership_places / len(partnership_rides)
    partnership_avg_position = partnership_rides['position'].mean()

    # Compare to jockey's overall performance with other trainers
    jockey_other_rides = historical_db.query(f"""
        SELECT *
        FROM race_results
        WHERE jockey = '{jockey}'
        AND trainer != '{trainer}'
    """)

    if len(jockey_other_rides) > 0:
        jockey_overall_win_pct = jockey_other_rides['position'].eq(1).sum() / len(jockey_other_rides)
        partnership_vs_jockey_overall = partnership_win_pct - jockey_overall_win_pct
    else:
        partnership_vs_jockey_overall = 0

    # Compare to trainer's overall performance with other jockeys
    trainer_other_rides = historical_db.query(f"""
        SELECT *
        FROM race_results
        WHERE trainer = '{trainer}'
        AND jockey != '{jockey}'
    """)

    if len(trainer_other_rides) > 0:
        trainer_overall_win_pct = trainer_other_rides['position'].eq(1).sum() / len(trainer_other_rides)
        partnership_vs_trainer_overall = partnership_win_pct - trainer_overall_win_pct
    else:
        partnership_vs_trainer_overall = 0

    # Calculate synergy score
    synergy_score = (partnership_vs_jockey_overall + partnership_vs_trainer_overall) / 2

    return {
        'has_partnership_history': True,
        'partnership_rides': len(partnership_rides),
        'partnership_wins': partnership_wins,
        'partnership_win_pct': partnership_win_pct,
        'partnership_place_pct': partnership_place_pct,
        'partnership_avg_position': partnership_avg_position,
        'partnership_vs_jockey_overall': partnership_vs_jockey_overall,
        'partnership_vs_trainer_overall': partnership_vs_trainer_overall,
        'partnership_synergy_score': synergy_score,
        'strong_partnership': synergy_score > 0.10 and len(partnership_rides) >= 10,
        'partnership_strike_rate': partnership_win_pct
    }
```

**Partnership Quantitative Features:**
```python
def engineer_partnership_features(partnership_data):
    """Create jockey-trainer partnership features"""

    if not partnership_data['has_partnership_history']:
        return {
            'has_partnership_history': 0,
            'partnership_rides': 0,
            'partnership_win_pct': None
        }

    features = {
        'has_partnership_history': 1,
        'partnership_rides': partnership_data['partnership_rides'],
        'partnership_wins': partnership_data['partnership_wins'],
        'partnership_win_pct': partnership_data['partnership_win_pct'],
        'partnership_place_pct': partnership_data['partnership_place_pct'],
        'partnership_avg_position': partnership_data['partnership_avg_position'],
        'partnership_synergy_score': partnership_data['partnership_synergy_score'],
        'strong_partnership': 1 if partnership_data['strong_partnership'] else 0,

        # Confidence levels based on sample size
        'partnership_confidence': 'high' if partnership_data['partnership_rides'] > 20 else
                                  'medium' if partnership_data['partnership_rides'] > 10 else
                                  'low',

        # Partnership quality categories
        'partnership_quality': 'excellent' if partnership_data['partnership_synergy_score'] > 0.15 else
                              'good' if partnership_data['partnership_synergy_score'] > 0.08 else
                              'average' if partnership_data['partnership_synergy_score'] > 0 else
                              'below_average'
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Jockey Smith and Trainer Jones partnership: 12 wins from 35 rides (34% win rate vs Smith's 18% overall and Jones' 15% overall), synergy score +15%..."
- Reasoning: "Very strong partnership, significantly outperforms individual statistics"
- Output: Partnership synergy adjustment (+10-15% if strong partnership)

---

### 17.2 Jockey-Horse Combinations
**Description:** Historical performance of jockey on specific horse
**Data Type:** Jockey-horse statistics
**Prediction Impact:** 6-12%

**Jockey-Horse Analysis:**
```python
def calculate_jockey_horse_combination(jockey, horse, historical_db):
    """Calculate jockey's record on specific horse"""

    # Query all rides of this jockey on this horse
    combo_rides = historical_db.query(f"""
        SELECT *
        FROM race_results
        WHERE jockey = '{jockey}'
        AND horse = '{horse}'
    """)

    if len(combo_rides) == 0:
        return {
            'has_combo_history': False,
            'combo_rides': 0
        }

    # Calculate statistics
    combo_wins = combo_rides['position'].eq(1).sum()
    combo_places = combo_rides['position'].le(3).sum()

    combo_win_pct = combo_wins / len(combo_rides)
    combo_place_pct = combo_places / len(combo_rides)
    combo_avg_position = combo_rides['position'].mean()

    # Compare to horse's overall performance with other jockeys
    horse_all_rides = historical_db.query(f"""
        SELECT *
        FROM race_results
        WHERE horse = '{horse}'
    """)

    horse_overall_win_pct = horse_all_rides['position'].eq(1).sum() / len(horse_all_rides)
    combo_vs_horse_overall = combo_win_pct - horse_overall_win_pct

    # Check for consistent improvement
    recent_combo_rides = combo_rides.tail(5)
    if len(recent_combo_rides) >= 3:
        recent_avg_position = recent_combo_rides['position'].mean()
    else:
        recent_avg_position = None

    return {
        'has_combo_history': True,
        'combo_rides': len(combo_rides),
        'combo_wins': combo_wins,
        'combo_win_pct': combo_win_pct,
        'combo_place_pct': combo_place_pct,
        'combo_avg_position': combo_avg_position,
        'combo_vs_horse_overall': combo_vs_horse_overall,
        'jockey_horse_synergy': combo_vs_horse_overall > 0.10 and len(combo_rides) >= 5,
        'recent_combo_avg_position': recent_avg_position,
        'proven_combination': combo_win_pct > 0.25 and len(combo_rides) >= 5
    }
```

**Jockey-Horse Features:**
```python
def engineer_jockey_horse_features(combo_data):
    """Create jockey-horse combination features"""

    if not combo_data['has_combo_history']:
        return {
            'has_combo_history': 0,
            'combo_rides': 0
        }

    features = {
        'has_combo_history': 1,
        'combo_rides': combo_data['combo_rides'],
        'combo_wins': combo_data['combo_wins'],
        'combo_win_pct': combo_data['combo_win_pct'],
        'combo_place_pct': combo_data['combo_place_pct'],
        'combo_avg_position': combo_data['combo_avg_position'],
        'combo_vs_horse_overall': combo_data['combo_vs_horse_overall'],
        'jockey_horse_synergy': 1 if combo_data['jockey_horse_synergy'] else 0,
        'proven_combination': 1 if combo_data['proven_combination'] else 0,

        # Confidence
        'combo_confidence': 'high' if combo_data['combo_rides'] > 10 else
                           'medium' if combo_data['combo_rides'] > 5 else
                           'low'
    }

    return features
```

**Qualitative Usage (GPP-5):**
- Context: "Jockey Williams has 4 wins from 8 rides on this horse (50% win rate vs horse's 20% overall), proven combination..."
- Reasoning: "Excellent jockey-horse synergy, jockey significantly improves horse's performance"
- Output: Jockey-horse synergy adjustment (+8-12% if proven combination)

---

### 17.3 Trainer-Horse Preparation Patterns
**Description:** How trainer prepares this specific horse (trials, spell lengths, gear)
**Data Type:** Horse-specific preparation history
**Prediction Impact:** 4-8%

**Preparation Pattern Analysis:**
```python
def analyze_trainer_horse_patterns(trainer, horse, historical_db):
    """Analyze how trainer prepares this specific horse"""

    # Get all runs of this horse under this trainer
    horse_runs = historical_db.query(f"""
        SELECT *
        FROM race_results
        WHERE horse = '{horse}'
        AND trainer = '{trainer}'
        ORDER BY race_date
    """)

    if len(horse_runs) < 3:
        return {
            'has_pattern_data': False
        }

    # Analyze winning patterns
    winning_runs = horse_runs[horse_runs['position'] == 1]

    # Spell lengths before wins
    winning_spells = []
    for idx in winning_runs.index:
        prev_run = horse_runs[horse_runs['race_date'] < horse_runs.loc[idx, 'race_date']].tail(1)
        if not prev_run.empty:
            days_between = (horse_runs.loc[idx, 'race_date'] - prev_run['race_date'].iloc[0]).days
            winning_spells.append(days_between)

    if winning_spells:
        avg_winning_spell = np.mean(winning_spells)
        optimal_spell_range = (avg_winning_spell - 10, avg_winning_spell + 10)
    else:
        avg_winning_spell = None
        optimal_spell_range = None

    # Trial usage before wins
    wins_with_trial = sum(1 for idx in winning_runs.index if horse_runs.loc[idx, 'had_trial'])
    trial_usage_pct = wins_with_trial / len(winning_runs) if len(winning_runs) > 0 else 0

    # Gear usage patterns
    gear_usage = horse_runs['gear'].value_counts().to_dict() if 'gear' in horse_runs.columns else {}

    return {
        'has_pattern_data': True,
        'total_runs_for_trainer': len(horse_runs),
        'wins_for_trainer': len(winning_runs),
        'avg_winning_spell': avg_winning_spell,
        'optimal_spell_range': optimal_spell_range,
        'trial_usage_before_wins_pct': trial_usage_pct,
        'gear_usage_patterns': gear_usage,
        'winning_spell_pattern': 'consistent' if len(winning_spells) > 2 and np.std(winning_spells) < 10 else 'variable'
    }
```

**Preparation Pattern Features:**
```python
def engineer_preparation_pattern_features(pattern_data, todays_spell, todays_trial, todays_gear):
    """Create trainer-horse preparation pattern features"""

    if not pattern_data['has_pattern_data']:
        return {
            'has_pattern_data': 0
        }

    # Check if today matches winning pattern
    matches_spell_pattern = False
    if pattern_data['optimal_spell_range']:
        matches_spell_pattern = pattern_data['optimal_spell_range'][0] <= todays_spell <= pattern_data['optimal_spell_range'][1]

    matches_trial_pattern = False
    if pattern_data['trial_usage_before_wins_pct'] > 0.7 and todays_trial:
        matches_trial_pattern = True
    elif pattern_data['trial_usage_before_wins_pct'] < 0.3 and not todays_trial:
        matches_trial_pattern = True

    features = {
        'has_pattern_data': 1,
        'total_runs_for_trainer': pattern_data['total_runs_for_trainer'],
        'wins_for_trainer': pattern_data['wins_for_trainer'],
        'avg_winning_spell': pattern_data['avg_winning_spell'],
        'matches_winning_spell_pattern': 1 if matches_spell_pattern else 0,
        'matches_trial_pattern': 1 if matches_trial_pattern else 0,
        'preparation_pattern_match': 1 if matches_spell_pattern and matches_trial_pattern else 0,
        'winning_spell_consistency': pattern_data['winning_spell_pattern']
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Trainer typically wins with this horse after 35-45 day spell + trial. Today: 38-day spell + trial. Pattern match..."
- Reasoning: "Preparation matches proven winning formula"
- Output: Preparation pattern confidence (+5-8% if matches winning pattern)

---

### 17.4 Three-Way Synergy (Jockey-Trainer-Horse)
**Description:** Performance when all three elements combine
**Data Type:** Triple combination statistics
**Prediction Impact:** 8-15% (when sufficient history exists)

**Three-Way Synergy Analysis:**
```python
def calculate_three_way_synergy(jockey, trainer, horse, historical_db):
    """Calculate jockey-trainer-horse combination performance"""

    # Query all runs with this exact combination
    three_way_rides = historical_db.query(f"""
        SELECT *
        FROM race_results
        WHERE jockey = '{jockey}'
        AND trainer = '{trainer}'
        AND horse = '{horse}'
    """)

    if len(three_way_rides) == 0:
        return {
            'has_three_way_history': False,
            'three_way_rides': 0
        }

    # Calculate statistics
    three_way_wins = three_way_rides['position'].eq(1).sum()
    three_way_places = three_way_rides['position'].le(3).sum()

    three_way_win_pct = three_way_wins / len(three_way_rides)
    three_way_place_pct = three_way_places / len(three_way_rides)

    # Compare to two-way combinations
    jockey_trainer_rides = historical_db.query(f"""
        SELECT *
        FROM race_results
        WHERE jockey = '{jockey}'
        AND trainer = '{trainer}'
    """)

    jockey_trainer_win_pct = jockey_trainer_rides['position'].eq(1).sum() / len(jockey_trainer_rides) if len(jockey_trainer_rides) > 0 else 0

    jockey_horse_rides = historical_db.query(f"""
        SELECT *
        FROM race_results
        WHERE jockey = '{jockey}'
        AND horse = '{horse}'
    """)

    jockey_horse_win_pct = jockey_horse_rides['position'].eq(1).sum() / len(jockey_horse_rides) if len(jockey_horse_rides) > 0 else 0

    # Calculate three-way synergy score
    avg_two_way = (jockey_trainer_win_pct + jockey_horse_win_pct) / 2
    three_way_synergy = three_way_win_pct - avg_two_way

    return {
        'has_three_way_history': True,
        'three_way_rides': len(three_way_rides),
        'three_way_wins': three_way_wins,
        'three_way_win_pct': three_way_win_pct,
        'three_way_place_pct': three_way_place_pct,
        'jockey_trainer_win_pct': jockey_trainer_win_pct,
        'jockey_horse_win_pct': jockey_horse_win_pct,
        'three_way_synergy_score': three_way_synergy,
        'dream_team': three_way_win_pct > 0.30 and len(three_way_rides) >= 5,
        'proven_three_way': three_way_synergy > 0.10 and len(three_way_rides) >= 5
    }
```

**Three-Way Features:**
```python
def engineer_three_way_features(three_way_data):
    """Create three-way synergy features"""

    if not three_way_data['has_three_way_history']:
        return {
            'has_three_way_history': 0,
            'three_way_rides': 0
        }

    features = {
        'has_three_way_history': 1,
        'three_way_rides': three_way_data['three_way_rides'],
        'three_way_wins': three_way_data['three_way_wins'],
        'three_way_win_pct': three_way_data['three_way_win_pct'],
        'three_way_place_pct': three_way_data['three_way_place_pct'],
        'three_way_synergy_score': three_way_data['three_way_synergy_score'],
        'dream_team': 1 if three_way_data['dream_team'] else 0,
        'proven_three_way': 1 if three_way_data['proven_three_way'] else 0,

        # Confidence
        'three_way_confidence': 'high' if three_way_data['three_way_rides'] > 10 else
                               'medium' if three_way_data['three_way_rides'] > 5 else
                               'low'
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "This exact jockey-trainer-horse combination: 5 wins from 7 starts (71% win rate), three-way synergy score +22%..."
- Reasoning: "Dream team combination, proven formula"
- Output: Three-way synergy boost (+12-15% if dream team)

---

## INTEGRATION GUIDELINES

### Chemistry Category Integration

**Chemistry + Historical Performance:**
```python
def analyze_chemistry_form_synergy(chemistry_data, form_data):
    """Analyze synergy between chemistry and recent form"""

    # Strong chemistry + good form = amplified confidence
    if chemistry_data.get('proven_three_way', False) and form_data.get('form_score', 0) > 70:
        return {
            'synergy_score': 0.20,  # 20% boost
            'confidence': 'very_high',
            'narrative': 'Proven combination in excellent form'
        }

    # Strong chemistry + poor form = still hopeful
    elif chemistry_data.get('proven_three_way', False) and form_data.get('form_score', 0) < 50:
        return {
            'synergy_score': 0.08,  # 8% boost
            'confidence': 'moderate',
            'narrative': 'Poor recent form but proven combination may turn around'
        }

    return {
        'synergy_score': 0.0,
        'confidence': 'neutral',
        'narrative': 'No strong chemistry-form synergy'
    }
```

**Sample Size Confidence Rules:**
- **High confidence:** 10+ rides for any combination
- **Medium confidence:** 5-10 rides
- **Low confidence:** 3-5 rides
- **Insufficient data:** <3 rides (don't use as strong factor)

---

## UNIFIED DATA MODEL

```python
chemistry_schema = {
    "jockey_trainer_partnership": {
        "partnership_rides": int,
        "partnership_win_pct": float,
        "partnership_synergy_score": float,
        "strong_partnership": bool
    },
    "jockey_horse_combination": {
        "combo_rides": int,
        "combo_win_pct": float,
        "combo_vs_horse_overall": float,
        "proven_combination": bool
    },
    "trainer_horse_patterns": {
        "avg_winning_spell": int,
        "matches_winning_pattern": bool,
        "trial_usage_pct": float
    },
    "three_way_synergy": {
        "three_way_rides": int,
        "three_way_win_pct": float,
        "three_way_synergy_score": float,
        "dream_team": bool
    }
}
```

**Example Data Record:**
```json
{
  "horse": "Champion Colt",
  "jockey": "James McDonald",
  "trainer": "Chris Waller",
  "chemistry": {
    "jockey_trainer_partnership": {
      "partnership_rides": 45,
      "partnership_win_pct": 0.33,
      "partnership_synergy_score": 0.15,
      "strong_partnership": true
    },
    "jockey_horse_combination": {
      "combo_rides": 8,
      "combo_win_pct": 0.50,
      "combo_vs_horse_overall": 0.20,
      "proven_combination": true
    },
    "three_way_synergy": {
      "three_way_rides": 8,
      "three_way_win_pct": 0.50,
      "three_way_synergy_score": 0.18,
      "dream_team": true
    }
  }
}
```

---

## COST ANALYSIS

**Category 17 Cost Breakdown:**
- **Partnership analysis:** $0 (derived from historical database)
- **Combination statistics:** $0 (database queries)
- **Pattern analysis:** $0 (historical analysis)

**Total Cost:** $0 per race

**Database Requirements:**
- Historical race results (3+ years recommended)
- Indexed by jockey, trainer, horse
- Query optimization for combination lookups

---

## IMPLEMENTATION CHECKLIST

### Phase 1 Week 5: Chemistry Analysis

**Day 1: Database Setup**
- [ ] Create indexed tables for jockey-trainer-horse combinations
- [ ] Build historical combination statistics (pre-compute for speed)
- [ ] Set up sample size confidence thresholds

**Day 2: Partnership Analysis**
- [ ] Implement jockey-trainer partnership calculator
- [ ] Implement jockey-horse combination calculator
- [ ] Test with known successful partnerships

**Day 3: Pattern Analysis**
- [ ] Implement trainer-horse preparation pattern analyzer
- [ ] Build winning spell pattern detection
- [ ] Implement gear/trial pattern matching

**Day 4: Three-Way Synergy**
- [ ] Implement three-way combination analyzer
- [ ] Build dream team detection logic
- [ ] Test synergy score calculations

**Day 5: Integration & Validation**
- [ ] Integrate chemistry with historical performance
- [ ] Validate sample size confidence rules
- [ ] Test full chemistry pipeline

---

**Document Complete: Category 17 (Jockey-Trainer-Horse Chemistry)**
**Next Document: PART_12_CATEGORY_18.md (Speed Ratings - NEW Quantitative Category)**
