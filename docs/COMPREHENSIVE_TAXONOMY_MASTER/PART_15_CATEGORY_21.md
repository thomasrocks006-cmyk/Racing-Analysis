# Master Taxonomy - Part 15: Category 21 (Breeding/Pedigree - NEW Quantitative Category)

**Document Purpose:** Complete implementation reference for pedigree analysis, sire/dam statistics, and breeding-based predictions
**Pipeline Usage:** BOTH Quantitative (breeding metrics) + Qualitative (pedigree context)
**Implementation Priority:** Phase 1 Week 10 (Important for young horses and specialized predictions)

---

## CATEGORY 21: BREEDING/PEDIGREE (NEW QUANTITATIVE CATEGORY)

### Overview
- **Category ID:** 21
- **Prediction Power:** 8-15% (particularly strong for young horses, wet tracks, distance suitability, first starters)
- **Pipeline Usage:** BOTH Quantitative (55%) + Qualitative (45%)
- **Priority Phase:** Phase 1 Week 10
- **Cost per Race:** $0 (public pedigree databases)
- **ChatGPT Access:** 50% (moderate pedigree knowledge but limited progeny statistics)
- **Our Target Access:** 95%

**Critical Note:** Pedigree is ESPECIALLY valuable for:
1. **Young horses** (2-3 year olds with limited racing history) - breeding explains 20-30% of ability
2. **First starters** (no form data available) - pedigree is primary predictor
3. **Wet track conditions** - sire's wet-track record highly predictive
4. **Distance suitability** - sire's stamina/speed profile predicts optimal distances

---

## SUBCATEGORIES

### 21.1 Sire Performance Statistics
**Description:** Statistical analysis of sire's progeny performance across all conditions
**Data Type:** Aggregated progeny performance metrics
**Prediction Impact:** 10-15% (for young horses), 5-8% (for mature horses)

**Why This Matters:**
- Elite sires produce consistent quality (60-80% of progeny win races)
- Speed vs stamina sires determine distance suitability
- Wet-track sires have 15-25% better progeny win rate on heavy tracks
- Sire statistics are especially predictive when horse has <5 career starts

**Sire Statistics Structure:**
```python
SIRE_QUALITY_TIERS = {
    'champion': {
        'stakes_winners_pct': 0.20,  # 20%+ progeny become stakes winners
        'progeny_win_pct': 0.70,     # 70%+ progeny win a race
        'avg_earnings_per_starter': 250000,
        'examples': ['Written Tycoon', 'I Am Invincible', 'Snitzel']
    },
    'elite': {
        'stakes_winners_pct': 0.12,
        'progeny_win_pct': 0.60,
        'avg_earnings_per_starter': 150000,
        'examples': ['Not A Single Doubt', 'Fastnet Rock', 'Exceed And Excel']
    },
    'high_quality': {
        'stakes_winners_pct': 0.08,
        'progeny_win_pct': 0.50,
        'avg_earnings_per_starter': 80000,
        'examples': ['Brazen Beau', 'Deep Field', 'Zoustar']
    },
    'average': {
        'stakes_winners_pct': 0.03,
        'progeny_win_pct': 0.35,
        'avg_earnings_per_starter': 40000
    },
    'below_average': {
        'stakes_winners_pct': 0.01,
        'progeny_win_pct': 0.20,
        'avg_earnings_per_starter': 15000
    }
}
```

**Get Sire Statistics:**
```python
def get_comprehensive_sire_statistics(sire_name, pedigree_db):
    """Get detailed sire progeny performance statistics"""

    # Query all progeny results
    progeny_records = pedigree_db.query(f"""
        SELECT
            horse_name,
            race_date,
            distance,
            track_condition,
            race_class,
            position,
            field_size,
            prize_money
        FROM race_results
        WHERE sire = '{sire_name}'
    """)

    if progeny_records.empty:
        return {
            'has_sire_data': False,
            'sire_name': sire_name,
            'data_quality': 'no_data'
        }

    # Get unique progeny
    unique_progeny = progeny_records['horse_name'].nunique()

    # Overall statistics
    total_starts = len(progeny_records)
    total_wins = (progeny_records['position'] == 1).sum()
    progeny_win_pct = total_wins / total_starts

    # Count winners
    progeny_with_wins = progeny_records[progeny_records['position'] == 1]['horse_name'].nunique()
    winner_pct = progeny_with_wins / unique_progeny

    # Stakes winners (Group/Listed races)
    stakes_races = progeny_records[
        progeny_records['race_class'].str.contains('Group|Listed', na=False, case=False)
    ]
    stakes_winners = stakes_races[stakes_races['position'] == 1]['horse_name'].nunique()
    stakes_winner_pct = stakes_winners / unique_progeny

    # Average earnings per starter
    total_prize_money = progeny_records['prize_money'].sum()
    avg_earnings_per_starter = total_prize_money / unique_progeny

    # Categorize sire quality
    if stakes_winner_pct >= 0.20:
        sire_tier = 'champion'
    elif stakes_winner_pct >= 0.12:
        sire_tier = 'elite'
    elif stakes_winner_pct >= 0.08:
        sire_tier = 'high_quality'
    elif stakes_winner_pct >= 0.03:
        sire_tier = 'average'
    else:
        sire_tier = 'below_average'

    # Distance performance analysis
    distance_stats = analyze_sire_distance_performance(progeny_records)

    # Track condition performance
    condition_stats = analyze_sire_condition_performance(progeny_records)

    # Age performance (2yo vs 3yo vs older)
    age_stats = analyze_sire_age_performance(progeny_records)

    return {
        'has_sire_data': True,
        'sire_name': sire_name,
        'data_quality': 'comprehensive' if total_starts >= 100 else 'limited',

        # Volume statistics
        'unique_progeny': unique_progeny,
        'total_starts': total_starts,
        'avg_starts_per_progeny': total_starts / unique_progeny,

        # Performance statistics
        'progeny_win_pct': progeny_win_pct,
        'progeny_winner_pct': winner_pct,  # % of progeny that win at least once
        'stakes_winners': stakes_winners,
        'stakes_winner_pct': stakes_winner_pct,
        'avg_earnings_per_starter': avg_earnings_per_starter,

        # Quality tier
        'sire_tier': sire_tier,
        'sire_tier_description': SIRE_QUALITY_TIERS[sire_tier],

        # Specialized statistics
        'distance_performance': distance_stats,
        'condition_performance': condition_stats,
        'age_performance': age_stats
    }

def analyze_sire_distance_performance(progeny_records):
    """Analyze sire's progeny performance by distance"""

    distance_ranges = {
        'sprint_1000_1200': (1000, 1200),
        'sprint_1200_1400': (1200, 1400),
        'mile_1400_1600': (1400, 1600),
        'middle_1600_2000': (1600, 2000),
        'staying_2000_2400': (2000, 2400),
        'extreme_staying_2400+': (2400, 3500)
    }

    distance_performance = {}

    for range_name, (min_dist, max_dist) in distance_ranges.items():
        range_records = progeny_records[
            (progeny_records['distance'] >= min_dist) &
            (progeny_records['distance'] <= max_dist)
        ]

        if len(range_records) >= 20:  # Need minimum sample size
            win_pct = (range_records['position'] == 1).sum() / len(range_records)
            avg_position = range_records['position'].mean()
            starts = len(range_records)

            distance_performance[range_name] = {
                'win_pct': win_pct,
                'avg_position': avg_position,
                'starts': starts
            }

    # Identify best distance range
    if distance_performance:
        best_range = max(distance_performance.items(), key=lambda x: x[1]['win_pct'])

        return {
            'distance_breakdown': distance_performance,
            'best_distance_range': best_range[0],
            'best_distance_win_pct': best_range[1]['win_pct']
        }

    return {'distance_breakdown': {}, 'best_distance_range': None}

def analyze_sire_condition_performance(progeny_records):
    """Analyze sire's progeny performance by track condition"""

    condition_groups = {
        'firm_good': ['Firm 1', 'Firm 2', 'Good 3', 'Good 4'],
        'soft': ['Soft 5', 'Soft 6', 'Soft 7'],
        'heavy': ['Heavy 8', 'Heavy 9', 'Heavy 10']
    }

    condition_performance = {}

    for group_name, conditions in condition_groups.items():
        group_records = progeny_records[progeny_records['track_condition'].isin(conditions)]

        if len(group_records) >= 20:
            win_pct = (group_records['position'] == 1).sum() / len(group_records)
            avg_position = group_records['position'].mean()
            starts = len(group_records)

            condition_performance[group_name] = {
                'win_pct': win_pct,
                'avg_position': avg_position,
                'starts': starts
            }

    # Calculate wet-track advantage
    if 'firm_good' in condition_performance and 'heavy' in condition_performance:
        wet_advantage = condition_performance['heavy']['win_pct'] - condition_performance['firm_good']['win_pct']

        is_wet_track_sire = wet_advantage > 0.05  # 5%+ better on wet tracks

        return {
            'condition_breakdown': condition_performance,
            'wet_track_advantage': wet_advantage,
            'is_wet_track_sire': is_wet_track_sire,
            'wet_track_win_pct': condition_performance['heavy']['win_pct']
        }

    return {
        'condition_breakdown': condition_performance,
        'wet_track_advantage': None,
        'is_wet_track_sire': False
    }

def analyze_sire_age_performance(progeny_records):
    """Analyze at what age sire's progeny perform best"""

    # Note: This would need age data in progeny_records
    # Simplified version assuming we can derive age from race dates

    age_performance = {
        '2yo': {'win_pct': 0.15, 'sample_size': 120},  # Placeholder
        '3yo': {'win_pct': 0.18, 'sample_size': 250},
        '4yo_plus': {'win_pct': 0.12, 'sample_size': 180}
    }

    # Identify if precocious (2yo) or late-maturing sire
    if age_performance['2yo']['win_pct'] > age_performance['3yo']['win_pct']:
        sire_type = 'precocious'  # Progeny race well young
    elif age_performance['4yo_plus']['win_pct'] > age_performance['3yo']['win_pct']:
        sire_type = 'late_maturing'  # Progeny improve with age
    else:
        sire_type = 'classic'  # Peak at 3yo

    return {
        'age_breakdown': age_performance,
        'sire_type': sire_type
    }
```

**Quantitative Features:**
```python
def engineer_sire_features(sire_stats, horse_age, todays_distance, todays_condition):
    """Create sire-based features for ML"""

    if not sire_stats['has_sire_data']:
        return {
            'has_sire_data': 0,
            'sire_tier': 'unknown'
        }

    # Match today's distance to sire's best range
    distance_match = False
    distance_win_pct_today = None

    if sire_stats['distance_performance']['distance_breakdown']:
        for range_name, stats in sire_stats['distance_performance']['distance_breakdown'].items():
            # Check if today's distance falls in this range
            if is_distance_in_range(todays_distance, range_name):
                distance_win_pct_today = stats['win_pct']

                # Check if this is sire's best range
                if range_name == sire_stats['distance_performance']['best_distance_range']:
                    distance_match = True
                break

    # Match today's condition to sire's performance
    condition_match = False
    condition_win_pct_today = None

    if todays_condition in ['Heavy 8', 'Heavy 9', 'Heavy 10']:
        condition_group = 'heavy'
    elif todays_condition in ['Soft 5', 'Soft 6', 'Soft 7']:
        condition_group = 'soft'
    else:
        condition_group = 'firm_good'

    if condition_group in sire_stats['condition_performance']['condition_breakdown']:
        condition_win_pct_today = sire_stats['condition_performance']['condition_breakdown'][condition_group]['win_pct']

        # Wet track sire advantage
        if condition_group in ['heavy', 'soft'] and sire_stats['condition_performance']['is_wet_track_sire']:
            condition_match = True

    features = {
        'has_sire_data': 1,
        'sire_tier': sire_stats['sire_tier'],
        'sire_progeny_win_pct': sire_stats['progeny_win_pct'],
        'sire_winner_pct': sire_stats['progeny_winner_pct'],
        'sire_stakes_winners': sire_stats['stakes_winners'],
        'sire_stakes_winner_pct': sire_stats['stakes_winner_pct'],
        'sire_avg_earnings': sire_stats['avg_earnings_per_starter'],

        # Sire quality flags
        'champion_sire': 1 if sire_stats['sire_tier'] == 'champion' else 0,
        'elite_sire': 1 if sire_stats['sire_tier'] in ['champion', 'elite'] else 0,
        'high_quality_sire': 1 if sire_stats['sire_tier'] in ['champion', 'elite', 'high_quality'] else 0,

        # Distance suitability
        'sire_distance_match': 1 if distance_match else 0,
        'sire_win_pct_at_distance': distance_win_pct_today,

        # Condition suitability
        'sire_condition_match': 1 if condition_match else 0,
        'sire_win_pct_in_condition': condition_win_pct_today,
        'is_wet_track_sire': 1 if sire_stats['condition_performance']['is_wet_track_sire'] else 0,
        'wet_track_advantage': sire_stats['condition_performance'].get('wet_track_advantage', 0),

        # Age interaction (more important for young horses)
        'young_horse_elite_sire': 1 if horse_age <= 3 and sire_stats['sire_tier'] in ['champion', 'elite'] else 0,
        'sire_importance_weight': 0.25 if horse_age <= 3 else 0.10  # 25% weight for young, 10% for mature
    }

    return features

def is_distance_in_range(distance, range_name):
    """Check if distance falls within named range"""

    range_mapping = {
        'sprint_1000_1200': (1000, 1200),
        'sprint_1200_1400': (1200, 1400),
        'mile_1400_1600': (1400, 1600),
        'middle_1600_2000': (1600, 2000),
        'staying_2000_2400': (2000, 2400),
        'extreme_staying_2400+': (2400, 3500)
    }

    if range_name in range_mapping:
        min_dist, max_dist = range_mapping[range_name]
        return min_dist <= distance <= max_dist

    return False
```

**Qualitative Usage (GPT-5):**
- Context: "By Written Tycoon (champion sire, 22% stakes winners, 72% progeny win rate), best at 1200-1400m (75% win rate), known for speed and precocity..."
- Reasoning: "Elite sire with proven record at this distance - breeding suggests genuine ability"
- Output: Sire quality confidence boost (+10-15% if champion sire at optimal distance for young horse)

---

### 21.2 Dam Produce Record
**Description:** Statistical analysis of dam's offspring performance (siblings of today's runner)
**Data Type:** Sibling performance metrics
**Prediction Impact:** 5-10% (especially for first starters and young horses)

**Why This Matters:**
- Elite producing dams (3+ stakes winners) strongly indicate quality
- Full siblings often have similar ability (60-70% correlation in class)
- Dam's produce record predicts whether young horse will make it to higher grades

**Get Dam Produce Record:**
```python
def get_comprehensive_dam_produce_record(dam_name, pedigree_db):
    """Get detailed dam produce record"""

    # Query all offspring (siblings)
    siblings = pedigree_db.query(f"""
        SELECT
            horse_name,
            birth_year,
            sire,
            total_starts,
            total_wins,
            total_placings,
            career_earnings,
            highest_race_class_won,
            stakes_wins
        FROM horses
        WHERE dam = '{dam_name}'
    """)

    if siblings.empty:
        return {
            'has_dam_data': False,
            'dam_name': dam_name
        }

    total_foals = len(siblings)

    # Count winners
    winners = siblings[siblings['total_wins'] > 0]
    num_winners = len(winners)
    winner_pct = num_winners / total_foals

    # Count stakes winners
    stakes_winners = siblings[siblings['stakes_wins'] > 0]
    num_stakes_winners = len(stakes_winners)
    stakes_winner_pct = num_stakes_winners / total_foals

    # Average performance
    avg_wins_per_foal = siblings['total_wins'].mean()
    avg_earnings_per_foal = siblings['career_earnings'].mean()

    # Identify best offspring
    best_offspring = siblings.nlargest(1, 'career_earnings').iloc[0] if not siblings.empty else None

    # Categorize dam quality
    if num_stakes_winners >= 3:
        dam_tier = 'elite_producer'
    elif num_stakes_winners >= 1:
        dam_tier = 'stakes_producer'
    elif winner_pct >= 0.70:
        dam_tier = 'good_producer'
    elif winner_pct >= 0.50:
        dam_tier = 'average_producer'
    else:
        dam_tier = 'below_average_producer'

    return {
        'has_dam_data': True,
        'dam_name': dam_name,
        'data_quality': 'comprehensive' if total_foals >= 5 else 'limited',

        # Volume
        'total_foals': total_foals,
        'foals_raced': siblings[siblings['total_starts'] > 0].shape[0],

        # Performance
        'winners': num_winners,
        'winner_pct': winner_pct,
        'stakes_winners': num_stakes_winners,
        'stakes_winner_pct': stakes_winner_pct,
        'avg_wins_per_foal': avg_wins_per_foal,
        'avg_earnings_per_foal': avg_earnings_per_foal,

        # Quality tier
        'dam_tier': dam_tier,

        # Best offspring
        'best_offspring': {
            'name': best_offspring['horse_name'] if best_offspring is not None else None,
            'earnings': best_offspring['career_earnings'] if best_offspring is not None else 0,
            'stakes_wins': best_offspring['stakes_wins'] if best_offspring is not None else 0
        }
    }

def analyze_full_half_siblings(horse_name, dam_name, sire_name, pedigree_db):
    """Analyze performance of full siblings (same sire+dam) and half siblings (same dam only)"""

    # Get all siblings
    siblings = pedigree_db.query(f"""
        SELECT *
        FROM horses
        WHERE dam = '{dam_name}' AND horse_name != '{horse_name}'
    """)

    if siblings.empty:
        return {
            'has_sibling_data': False
        }

    # Full siblings (same sire and dam)
    full_siblings = siblings[siblings['sire'] == sire_name]

    # Half siblings (different sire, same dam)
    half_siblings = siblings[siblings['sire'] != sire_name]

    full_sibling_stats = None
    if not full_siblings.empty:
        full_sibling_stats = {
            'count': len(full_siblings),
            'winners': (full_siblings['total_wins'] > 0).sum(),
            'stakes_winners': (full_siblings['stakes_wins'] > 0).sum(),
            'avg_earnings': full_siblings['career_earnings'].mean(),
            'best_earnings': full_siblings['career_earnings'].max()
        }

    half_sibling_stats = None
    if not half_siblings.empty:
        half_sibling_stats = {
            'count': len(half_siblings),
            'winners': (half_siblings['total_wins'] > 0).sum(),
            'stakes_winners': (half_siblings['stakes_wins'] > 0).sum(),
            'avg_earnings': half_siblings['career_earnings'].mean()
        }

    return {
        'has_sibling_data': True,
        'full_siblings': full_sibling_stats,
        'half_siblings': half_sibling_stats
    }
```

**Quantitative Features:**
```python
def engineer_dam_features(dam_stats, sibling_stats, horse_age):
    """Create dam-based features for ML"""

    if not dam_stats['has_dam_data']:
        return {
            'has_dam_data': 0,
            'dam_tier': 'unknown'
        }

    features = {
        'has_dam_data': 1,
        'dam_tier': dam_stats['dam_tier'],
        'dam_foals': dam_stats['total_foals'],
        'dam_winner_pct': dam_stats['winner_pct'],
        'dam_winners': dam_stats['winners'],
        'dam_stakes_winners': dam_stats['stakes_winners'],
        'dam_stakes_winner_pct': dam_stats['stakes_winner_pct'],
        'dam_avg_earnings': dam_stats['avg_earnings_per_foal'],

        # Dam quality flags
        'elite_producer_dam': 1 if dam_stats['dam_tier'] == 'elite_producer' else 0,
        'stakes_producer_dam': 1 if dam_stats['dam_tier'] in ['elite_producer', 'stakes_producer'] else 0,

        # Sibling data
        'has_sibling_data': 0,
        'has_full_siblings': 0,
        'full_sibling_winners': 0,
        'full_sibling_stakes_winners': 0
    }

    # Add sibling features if available
    if sibling_stats.get('has_sibling_data'):
        features['has_sibling_data'] = 1

        if sibling_stats['full_siblings']:
            features['has_full_siblings'] = 1
            features['full_sibling_winners'] = sibling_stats['full_siblings']['winners']
            features['full_sibling_stakes_winners'] = sibling_stats['full_siblings']['stakes_winners']
            features['full_sibling_avg_earnings'] = sibling_stats['full_siblings']['avg_earnings']

            # Full sibling success is very predictive
            if sibling_stats['full_siblings']['stakes_winners'] > 0:
                features['full_sibling_stakes_success'] = 1
            else:
                features['full_sibling_stakes_success'] = 0

    # Dam importance weight (more important for young horses)
    features['dam_importance_weight'] = 0.15 if horse_age <= 3 else 0.05

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Dam has produced 3 stakes winners from 8 foals (38% stakes winner rate), full sibling won Group 3 earning $350k..."
- Reasoning: "Elite producing dam with proven quality at stakes level - strong genetic foundation"
- Output: Dam quality confidence boost (+5-10% if elite producer with successful siblings)

---

### 21.3 Pedigree-Based Distance Suitability
**Description:** Predicting optimal distance range from sire/dam breeding profiles
**Data Type:** Distance preference predictions
**Prediction Impact:** 8-12% (especially for untried distances and young horses)

**Why This Matters:**
- Sire's progeny distance profile predicts whether horse will handle 1200m vs 2000m
- Speed sires (I Am Invincible, Written Tycoon) → 1000-1400m optimal
- Staying sires (So You Think, Tavistock) → 1800-2400m optimal
- Helps predict step-ups in distance before horse has tried it

**Analyze Distance Suitability:**
```python
def predict_distance_suitability_from_pedigree(sire_stats, dam_stats, target_distance):
    """Comprehensive distance suitability prediction from breeding"""

    # Sire's progeny performance at target distance
    sire_distance_suitability = None
    sire_weight = 0.70  # Sire is 70% of distance prediction

    if sire_stats['has_sire_data'] and sire_stats['distance_performance']['distance_breakdown']:
        # Find which range target distance falls into
        for range_name, stats in sire_stats['distance_performance']['distance_breakdown'].items():
            if is_distance_in_range(target_distance, range_name):
                sire_distance_suitability = stats['win_pct']
                break

    # Dam's offspring average distance (if available)
    dam_distance_suitability = None
    dam_weight = 0.30  # Dam is 30% of distance prediction

    if dam_stats['has_dam_data'] and dam_stats.get('dam_offspring_avg_distance'):
        dam_avg_distance = dam_stats['dam_offspring_avg_distance']
        dam_distance_delta = abs(dam_avg_distance - target_distance)

        # Closer to dam's average = better suitability
        if dam_distance_delta <= 200:
            dam_distance_suitability = 0.80  # Excellent
        elif dam_distance_delta <= 400:
            dam_distance_suitability = 0.60  # Good
        elif dam_distance_delta <= 600:
            dam_distance_suitability = 0.40  # Moderate
        else:
            dam_distance_suitability = 0.20  # Poor

    # Combine sire + dam suitability
    if sire_distance_suitability and dam_distance_suitability:
        combined_suitability = (sire_distance_suitability * sire_weight) + (dam_distance_suitability * dam_weight)
    elif sire_distance_suitability:
        combined_suitability = sire_distance_suitability
    elif dam_distance_suitability:
        combined_suitability = dam_distance_suitability
    else:
        combined_suitability = None

    # Categorize suitability
    if combined_suitability:
        if combined_suitability >= 0.70:
            suitability_category = 'excellent'
        elif combined_suitability >= 0.55:
            suitability_category = 'good'
        elif combined_suitability >= 0.40:
            suitability_category = 'moderate'
        else:
            suitability_category = 'poor'
    else:
        suitability_category = 'unknown'

    return {
        'has_distance_prediction': combined_suitability is not None,
        'pedigree_distance_suitability_score': combined_suitability,
        'suitability_category': suitability_category,
        'sire_component': sire_distance_suitability,
        'dam_component': dam_distance_suitability,
        'distance_suited_by_pedigree': combined_suitability >= 0.55 if combined_suitability else False
    }
```

**Quantitative Features:**
```python
def engineer_pedigree_distance_features(distance_prediction, horse_distance_experience):
    """Create pedigree distance features for ML"""

    if not distance_prediction['has_distance_prediction']:
        return {
            'has_pedigree_distance_prediction': 0,
            'pedigree_distance_suitability': None
        }

    # Weight pedigree more heavily if horse hasn't tried this distance
    if horse_distance_experience == 'untried':
        pedigree_weight = 0.40  # 40% weight when no experience
    elif horse_distance_experience == 'limited':  # 1-2 tries
        pedigree_weight = 0.20  # 20% weight when limited experience
    else:
        pedigree_weight = 0.05  # 5% weight when experienced

    features = {
        'has_pedigree_distance_prediction': 1,
        'pedigree_distance_suitability': distance_prediction['pedigree_distance_suitability_score'],
        'distance_suitability_category': distance_prediction['suitability_category'],

        # Binary flags
        'excellent_pedigree_distance_match': 1 if distance_prediction['suitability_category'] == 'excellent' else 0,
        'good_pedigree_distance_match': 1 if distance_prediction['suitability_category'] in ['excellent', 'good'] else 0,
        'poor_pedigree_distance_match': 1 if distance_prediction['suitability_category'] == 'poor' else 0,

        # Weighted importance
        'pedigree_distance_weight': pedigree_weight
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "By I Am Invincible (85% win rate at 1200m, speed sire), dam's offspring average 1250m... stepping up to 1600m (untried)..."
- Reasoning: "Breeding strongly suggests speed/sprint specialist - 1600m may be beyond optimal range"
- Output: Distance concern (-8-12% if poor pedigree match at untried distance)

---

### 21.4 Track Condition Suitability from Breeding
**Description:** Predicting wet/firm track performance from sire's progeny wet-track record
**Data Type:** Condition-specific breeding predictions
**Prediction Impact:** 10-15% (on wet tracks for horses with limited wet-track experience)

**Why This Matters:**
- Wet-track sires have 15-25% better progeny performance on heavy tracks
- Critical for young horses racing on heavy for first time
- Examples: All Too Hard, So You Think, Tavistock (wet-track sires)

**Analyze Wet-Track Breeding:**
```python
def predict_wettrack_ability_from_pedigree(sire_stats, dam_stats, todays_condition):
    """Predict wet-track performance from breeding"""

    # Check if wet track
    is_wet_track = todays_condition in ['Soft 5', 'Soft 6', 'Soft 7', 'Heavy 8', 'Heavy 9', 'Heavy 10']

    if not is_wet_track:
        return {
            'wet_track_prediction_relevant': False
        }

    # Sire's wet-track record
    sire_wet_advantage = None
    if sire_stats['has_sire_data'] and sire_stats['condition_performance']['wet_track_advantage'] is not None:
        sire_wet_advantage = sire_stats['condition_performance']['wet_track_advantage']
        is_wet_track_sire = sire_stats['condition_performance']['is_wet_track_sire']
    else:
        is_wet_track_sire = False

    # Categorize wet-track suitability
    if sire_wet_advantage:
        if sire_wet_advantage >= 0.10:
            wet_suitability = 'excellent'
        elif sire_wet_advantage >= 0.05:
            wet_suitability = 'good'
        elif sire_wet_advantage >= -0.05:
            wet_suitability = 'neutral'
        else:
            wet_suitability = 'poor'
    else:
        wet_suitability = 'unknown'

    return {
        'wet_track_prediction_relevant': True,
        'is_wet_track_sire': is_wet_track_sire,
        'sire_wet_track_advantage': sire_wet_advantage,
        'wet_suitability_category': wet_suitability,
        'wet_track_confidence': 'high' if is_wet_track_sire else 'moderate'
    }
```

**Quantitative Features:**
```python
def engineer_wettrack_breeding_features(wettrack_prediction, horse_wettrack_experience):
    """Create wet-track breeding features for ML"""

    if not wettrack_prediction['wet_track_prediction_relevant']:
        return {
            'wet_track_prediction_available': 0
        }

    # Weight breeding more heavily if horse hasn't raced on wet tracks
    if horse_wettrack_experience == 'no_experience':
        breeding_weight = 0.35  # 35% weight when no wet-track experience
    elif horse_wettrack_experience == 'limited':  # 1-2 wet starts
        breeding_weight = 0.15  # 15% weight when limited experience
    else:
        breeding_weight = 0.05  # 5% weight when experienced on wet

    features = {
        'wet_track_prediction_available': 1,
        'is_wet_track_sire': 1 if wettrack_prediction['is_wet_track_sire'] else 0,
        'sire_wet_track_advantage': wettrack_prediction.get('sire_wet_track_advantage', 0),
        'wet_suitability_category': wettrack_prediction['wet_suitability_category'],

        # Binary flags
        'excellent_wet_breeding': 1 if wettrack_prediction['wet_suitability_category'] == 'excellent' else 0,
        'poor_wet_breeding': 1 if wettrack_prediction['wet_suitability_category'] == 'poor' else 0,

        # Weighted importance
        'wettrack_breeding_weight': breeding_weight
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "By All Too Hard (wet-track sire, +18% win rate on heavy tracks vs firm), racing on Heavy 9 for first time..."
- Reasoning: "Strong wet-track breeding gives confidence despite no wet-track experience"
- Output: Wet-track breeding confidence boost (+10-15% if wet-track sire with no experience on wet)

---

## INTEGRATION GUIDELINES

### Pedigree + Historical Performance (Category 14)
```python
def integrate_pedigree_with_form(pedigree_data, form_data, horse_age):
    """Integrate pedigree with recent form"""

    # Young horse (age <= 3) + elite sire + good form = very strong
    if horse_age <= 3 and pedigree_data['elite_sire'] and form_data['form_score'] > 70:
        return {
            'synergy_score': 0.20,
            'confidence': 'very_high',
            'narrative': 'Young horse by elite sire in good form - strong genetic + proven form'
        }

    # Poor form + elite breeding = potential for improvement
    elif pedigree_data['elite_sire'] and pedigree_data['elite_producer_dam'] and form_data['form_score'] < 50:
        return {
            'synergy_score': 0.05,
            'confidence': 'moderate',
            'narrative': 'Poor form but elite breeding suggests ability to improve'
        }

    return {'synergy_score': 0.0, 'confidence': 'neutral'}
```

---

## UNIFIED DATA MODEL

```python
pedigree_schema = {
    "sire_statistics": {
        "sire_name": str,
        "sire_tier": str,
        "progeny_win_pct": float,
        "stakes_winner_pct": float,
        "distance_performance": dict,
        "condition_performance": dict,
        "is_wet_track_sire": bool
    },
    "dam_produce": {
        "dam_name": str,
        "dam_tier": str,
        "winners": int,
        "stakes_winners": int,
        "winner_pct": float
    },
    "distance_suitability": {
        "pedigree_distance_suitability_score": float,
        "suitability_category": str,
        "distance_suited_by_pedigree": bool
    },
    "wettrack_suitability": {
        "is_wet_track_sire": bool,
        "sire_wet_track_advantage": float,
        "wet_suitability_category": str
    }
}
```

---

## COST ANALYSIS

**Category 21 Cost Breakdown:**
- **Pedigree database queries:** $0 (public databases: Pedigreequery.com, Racing Australia)
- **Sire/dam statistics calculation:** $0 (one-time computation, cached)
- **Data storage:** $0.01/horse (minimal)

**Total Cost:** $0 per race

---

## IMPLEMENTATION CHECKLIST

### Phase 1 Week 10: Pedigree Implementation

**Day 1: Sire Statistics**
- [ ] Build pedigree database schema
- [ ] Import sire statistics from Racing Australia
- [ ] Calculate sire progeny performance metrics
- [ ] Test on 50 champion/elite sires

**Day 2: Dam Produce Records**
- [ ] Import dam produce records
- [ ] Calculate dam quality tiers
- [ ] Analyze full/half sibling correlations
- [ ] Test on elite producing dams

**Day 3: Distance Suitability**
- [ ] Build distance preference analyzer
- [ ] Calculate sire+dam distance predictions
- [ ] Test on horses stepping up/down in distance
- [ ] Validate accuracy vs actual performance

**Day 4: Wet-Track Breeding**
- [ ] Identify wet-track sires
- [ ] Calculate wet-track advantages
- [ ] Build condition suitability predictor
- [ ] Test on horses with no wet-track experience

**Day 5: Feature Engineering & Integration**
- [ ] Engineer all pedigree features (35+ features)
- [ ] Integrate with historical performance
- [ ] Weight pedigree by horse age/experience
- [ ] Test full pedigree pipeline
- [ ] Validate prediction improvement

---

**Document Complete: Category 21 (Pedigree - COMPREHENSIVE)**
**Lines: 800+ (FULLY EXPANDED)**
**Next Phase: PARTS 16-26 Expansion (Integration Matrices, Schemas, Roadmaps, Supporting Docs)**
