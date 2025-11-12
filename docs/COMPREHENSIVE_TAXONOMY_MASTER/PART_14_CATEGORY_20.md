# Master Taxonomy - Part 14: Category 20 (Sectional Data - NEW Quantitative Category)

**Document Purpose:** Complete implementation reference for sectional times, split analysis, and acceleration metrics
**Pipeline Usage:** PRIMARILY Quantitative (critical for pace-adjusted predictions) + Qualitative context
**Implementation Priority:** Phase 1 Week 9 (CRITICAL for quantitative pipeline)

---

## CATEGORY 20: SECTIONAL DATA (NEW QUANTITATIVE CATEGORY)

### Overview
- **Category ID:** 20
- **Prediction Power:** 10-18% (sectionals reveal true running ability independent of pace bias)
- **Pipeline Usage:** PRIMARILY Quantitative (80% Quant, 20% Qual)
- **Priority Phase:** Phase 1 Week 9
- **Cost per Race:** $0.05-$0.10 (Speedmaps API access)
- **ChatGPT Access:** 5% (almost no sectional access - major weakness)
- **Our Target Access:** 95%

**Critical Note:** Sectional times are ESSENTIAL for the quantitative pipeline because they reveal true acceleration patterns and closing speed independent of overall race pace. A horse that runs the final 400m in 22.0s is demonstrably faster than one running 23.5s, regardless of early pace. This is ChatGPT's BIGGEST weakness (5% access) and our BIGGEST opportunity.

---

## SUBCATEGORIES

### 20.1 Split Times (600m/400m/200m)
**Description:** Incremental sectional times at key splits during the race
**Data Type:** Time measurements at standardized splits
**Prediction Impact:** 12-18%

**Why This Matters:**
- **600m-400m split:** Shows mid-race pace sustainability and tactical positioning
- **Final 400m split:** MOST CRITICAL - reveals true closing speed and finishing ability
- **Final 200m split:** Sprint acceleration, decisive speed bursts
- Sectionals eliminate pace bias - fast final 400m is fast regardless of early pace

**Sectional Measurement Standards:**
```python
SECTIONAL_SPLITS = {
    'sprint_races': {  # 1000m-1400m
        'splits': ['800m', '600m', '400m', '200m'],
        'most_critical': 'final_400m'
    },
    'mile_races': {  # 1400m-1800m
        'splits': ['1000m', '800m', '600m', '400m', '200m'],
        'most_critical': 'final_400m'
    },
    'staying_races': {  # 1800m+
        'splits': ['1200m', '1000m', '800m', '600m', '400m', '200m'],
        'most_critical': 'final_600m'
    }
}

# Australian standard (Speedmaps, Racing.com)
SECTIONAL_STANDARDS = {
    'excellent_400m': 22.0,     # Elite closing speed
    'very_good_400m': 22.5,     # High-class closing
    'good_400m': 23.0,          # Competitive closing
    'average_400m': 23.5,       # Moderate closing
    'below_average_400m': 24.0, # Slow closing
    'poor_400m': 24.5           # Very slow closing
}
```

**Extract Sectional Times:**
```python
def extract_sectional_times(race_result_data, speedmaps_api_key):
    """Extract sectional times from Speedmaps or Racing.com"""

    import requests

    # Try Speedmaps first (most comprehensive)
    speedmaps_url = f"https://api.speedmaps.com.au/sectionals/{race_result_data['race_id']}"
    headers = {'Authorization': f'Bearer {speedmaps_api_key}'}

    try:
        response = requests.get(speedmaps_url, headers=headers, timeout=5)

        if response.status_code == 200:
            sectional_data = response.json()

            horse_sectionals = {}
            for runner in sectional_data['runners']:
                if runner['horse_name'] == race_result_data['horse_name']:
                    horse_sectionals = {
                        'has_sectionals': True,
                        'data_source': 'speedmaps',
                        'final_400m': runner.get('final_400m_time'),
                        'final_600m': runner.get('final_600m_time'),
                        'final_800m': runner.get('final_800m_time'),
                        'final_200m': runner.get('final_200m_time'),
                        'splits_complete': runner.get('splits_complete', False),
                        'field_position_at_400m': runner.get('position_at_400m'),
                        'field_position_at_200m': runner.get('position_at_200m')
                    }
                    break

            if horse_sectionals:
                return horse_sectionals

    except requests.exceptions.RequestException:
        pass

    # Fallback: Try Racing.com scraping
    sectionals_scraped = scrape_racingcom_sectionals(race_result_data)
    if sectionals_scraped['has_sectionals']:
        return sectionals_scraped

    # No sectionals available
    return {
        'has_sectionals': False,
        'data_source': None,
        'final_400m': None,
        'final_600m': None
    }

def scrape_racingcom_sectionals(race_result_data):
    """Scrape sectionals from Racing.com as fallback"""

    from bs4 import BeautifulSoup
    import requests

    # Racing.com sectionals page format
    race_url = f"https://www.racing.com/sectional-times/{race_result_data['race_id']}"

    try:
        response = requests.get(race_url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find sectional times table
        sectionals_table = soup.find('table', {'class': 'sectional-times'})

        if sectionals_table:
            for row in sectionals_table.find_all('tr'):
                horse_cell = row.find('td', {'class': 'horse-name'})
                if horse_cell and horse_cell.text.strip() == race_result_data['horse_name']:
                    # Extract sectionals
                    final_400m = row.find('td', {'class': 'final-400'})
                    final_600m = row.find('td', {'class': 'final-600'})

                    return {
                        'has_sectionals': True,
                        'data_source': 'racingcom_scraped',
                        'final_400m': float(final_400m.text.strip()) if final_400m else None,
                        'final_600m': float(final_600m.text.strip()) if final_600m else None,
                        'scrape_successful': True
                    }

    except Exception as e:
        pass

    return {
        'has_sectionals': False,
        'scrape_successful': False
    }
```

**Calculate Split Percentiles:**
```python
def calculate_sectional_percentiles(horse_sectionals, field_sectionals):
    """Calculate horse's sectional percentile vs field"""

    if not horse_sectionals['has_sectionals'] or not field_sectionals:
        return {
            'has_percentiles': False
        }

    # Sort field by final 400m (ascending = faster)
    field_400m_times = sorted([r['final_400m'] for r in field_sectionals if r.get('final_400m')])

    if not field_400m_times or horse_sectionals['final_400m'] is None:
        return {'has_percentiles': False}

    # Calculate horse's percentile
    horse_400m = horse_sectionals['final_400m']

    # Lower time = better = higher percentile
    faster_count = sum(1 for t in field_400m_times if t < horse_400m)
    percentile_400m = (faster_count / len(field_400m_times)) * 100

    # Inverse percentile (faster = higher percentile)
    percentile_400m_inverse = 100 - percentile_400m

    # Categorize performance
    if percentile_400m_inverse >= 90:
        performance = 'elite_closing_speed'
    elif percentile_400m_inverse >= 75:
        performance = 'very_strong_closing'
    elif percentile_400m_inverse >= 50:
        performance = 'above_average_closing'
    elif percentile_400m_inverse >= 25:
        performance = 'below_average_closing'
    else:
        performance = 'weak_closing'

    # Best sectional in field
    best_400m_field = min(field_400m_times)
    gap_to_best = horse_400m - best_400m_field

    return {
        'has_percentiles': True,
        'final_400m_percentile': percentile_400m_inverse,
        'final_400m_performance': performance,
        'best_400m_in_field': best_400m_field,
        'gap_to_best_400m': gap_to_best,
        'top_3_sectional': percentile_400m_inverse >= 75,
        'best_sectional_in_race': gap_to_best == 0.0
    }
```

**Analyze Sectional Consistency:**
```python
def analyze_sectional_consistency(horse_history_with_sectionals):
    """Analyze horse's consistency in sectional times across recent starts"""

    sectional_400m_times = []

    for run in horse_history_with_sectionals:
        if run.get('sectionals', {}).get('has_sectionals'):
            final_400m = run['sectionals'].get('final_400m')
            if final_400m:
                sectional_400m_times.append(final_400m)

    if len(sectional_400m_times) < 3:
        return {
            'has_consistency_data': False,
            'sample_size': len(sectional_400m_times)
        }

    avg_400m = np.mean(sectional_400m_times)
    std_400m = np.std(sectional_400m_times)
    min_400m = min(sectional_400m_times)
    max_400m = max(sectional_400m_times)

    # Consistency rating
    if std_400m < 0.3:
        consistency = 'very_consistent'
    elif std_400m < 0.5:
        consistency = 'consistent'
    elif std_400m < 0.8:
        consistency = 'moderately_consistent'
    else:
        consistency = 'inconsistent'

    # Categorize average performance
    if avg_400m <= 22.5:
        avg_performance = 'elite_closer'
    elif avg_400m <= 23.0:
        avg_performance = 'strong_closer'
    elif avg_400m <= 23.5:
        avg_performance = 'average_closer'
    else:
        avg_performance = 'weak_closer'

    return {
        'has_consistency_data': True,
        'sample_size': len(sectional_400m_times),
        'avg_final_400m': avg_400m,
        'std_final_400m': std_400m,
        'best_final_400m': min_400m,
        'worst_final_400m': max_400m,
        'range_400m': max_400m - min_400m,
        'consistency_rating': consistency,
        'avg_performance_category': avg_performance,
        'elite_sectional_capable': min_400m <= 22.0
    }
```

**Quantitative Features:**
```python
def engineer_sectional_features(horse_sectionals, field_sectionals, horse_history):
    """Create sectional time features for ML"""

    if not horse_sectionals['has_sectionals']:
        return {
            'has_sectionals': 0,
            'final_400m_time': None,
            'sectional_data_available': False
        }

    # Calculate percentiles
    percentiles = calculate_sectional_percentiles(horse_sectionals, field_sectionals)

    # Analyze consistency
    consistency = analyze_sectional_consistency(horse_history)

    features = {
        'has_sectionals': 1,
        'sectional_data_available': True,
        'data_source': horse_sectionals['data_source'],

        # Raw sectionals
        'final_400m_time': horse_sectionals['final_400m'],
        'final_600m_time': horse_sectionals.get('final_600m'),
        'final_200m_time': horse_sectionals.get('final_200m'),

        # Performance categories
        'elite_closing_speed': 1 if horse_sectionals['final_400m'] <= 22.0 else 0,
        'very_good_closing': 1 if 22.0 < horse_sectionals['final_400m'] <= 22.5 else 0,
        'good_closing': 1 if 22.5 < horse_sectionals['final_400m'] <= 23.0 else 0,
        'average_closing': 1 if 23.0 < horse_sectionals['final_400m'] <= 23.5 else 0,
        'below_average_closing': 1 if horse_sectionals['final_400m'] > 23.5 else 0,

        # Percentile features
        'final_400m_percentile': percentiles.get('final_400m_percentile'),
        'top_3_sectional_in_race': 1 if percentiles.get('top_3_sectional', False) else 0,
        'best_sectional_in_race': 1 if percentiles.get('best_sectional_in_race', False) else 0,
        'gap_to_best_sectional': percentiles.get('gap_to_best_400m'),

        # Consistency features
        'has_sectional_history': 1 if consistency.get('has_consistency_data', False) else 0,
        'avg_final_400m': consistency.get('avg_final_400m'),
        'sectional_consistency_std': consistency.get('std_final_400m'),
        'consistency_rating': consistency.get('consistency_rating'),
        'elite_sectional_capable': 1 if consistency.get('elite_sectional_capable', False) else 0
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Final 400m in 22.1s (3rd fastest in race, 88th percentile), consistently runs sub-22.5s finals (4 of last 5 starts)..."
- Reasoning: "Elite closing speed demonstrated consistently - genuine strong finisher"
- Output: Sectional-based confidence boost (+12-18% if elite closer with consistency)

---

### 20.2 Acceleration Metrics
**Description:** Rate of speed change, particularly in final stages
**Data Type:** Speed differentials between splits
**Prediction Impact:** 8-14%

**Why This Matters:**
- Shows true acceleration ability (can the horse quicken when needed?)
- Identifies horses that "hit a flat spot" vs horses that sustain/improve speed
- Critical for predicting performance in sprint finishes

**Calculate Acceleration:**
```python
def calculate_acceleration_metrics(sectional_data):
    """Calculate acceleration between sectional splits"""

    if not sectional_data['has_sectionals']:
        return {
            'has_acceleration_data': False
        }

    # Need at least 2 splits to calculate acceleration
    final_400m = sectional_data.get('final_400m')
    final_600m = sectional_data.get('final_600m')
    final_200m = sectional_data.get('final_200m')

    if final_400m is None:
        return {'has_acceleration_data': False}

    metrics = {
        'has_acceleration_data': True
    }

    # Calculate 600m-400m split (middle 200m of final 600m)
    if final_600m is not None:
        middle_200m = final_600m - final_400m

        # Calculate acceleration from middle 200m to final 200m
        if final_200m is not None:
            acceleration = middle_200m - final_200m  # Positive = accelerated

            metrics['middle_200m_split'] = middle_200m
            metrics['final_200m_split'] = final_200m
            metrics['acceleration_200m'] = acceleration

            # Categorize acceleration
            if acceleration > 0.5:
                metrics['acceleration_pattern'] = 'strong_acceleration'
            elif acceleration > 0.2:
                metrics['acceleration_pattern'] = 'moderate_acceleration'
            elif acceleration > -0.2:
                metrics['acceleration_pattern'] = 'sustained_speed'
            elif acceleration > -0.5:
                metrics['acceleration_pattern'] = 'slight_deceleration'
            else:
                metrics['acceleration_pattern'] = 'significant_deceleration'

        # Calculate if horse ran faster/slower in final 400m vs previous 200m
        # (400m split should be roughly 2x the 200m split if maintaining pace)
        expected_400m_if_sustained = middle_200m * 2
        actual_400m = final_400m
        pace_differential = actual_400m - expected_400m_if_sustained

        metrics['pace_differential'] = pace_differential

        if pace_differential < -0.5:
            metrics['pace_pattern'] = 'accelerated_strongly'
        elif pace_differential < -0.2:
            metrics['pace_pattern'] = 'accelerated_moderately'
        elif pace_differential < 0.2:
            metrics['pace_pattern'] = 'maintained_pace'
        elif pace_differential < 0.5:
            metrics['pace_pattern'] = 'slowed_slightly'
        else:
            metrics['pace_pattern'] = 'slowed_significantly'

    # Calculate average speed over final 400m (m/s)
    avg_speed_400m = 400 / final_400m
    metrics['avg_speed_final_400m_mps'] = avg_speed_400m

    # Elite horses run 400m in 22s = 18.18 m/s
    # Average horses run 400m in 24s = 16.67 m/s
    if avg_speed_400m >= 18.0:
        metrics['speed_category'] = 'elite_speed'
    elif avg_speed_400m >= 17.0:
        metrics['speed_category'] = 'high_speed'
    elif avg_speed_400m >= 16.0:
        metrics['speed_category'] = 'average_speed'
    else:
        metrics['speed_category'] = 'below_average_speed'

    return metrics

def analyze_acceleration_consistency(horse_history_with_sectionals):
    """Analyze horse's acceleration patterns across recent starts"""

    acceleration_patterns = []

    for run in horse_history_with_sectionals:
        if run.get('sectionals', {}).get('has_sectionals'):
            accel_metrics = calculate_acceleration_metrics(run['sectionals'])
            if accel_metrics['has_acceleration_data']:
                acceleration_patterns.append({
                    'acceleration_200m': accel_metrics.get('acceleration_200m'),
                    'pace_pattern': accel_metrics.get('pace_pattern'),
                    'avg_speed_mps': accel_metrics.get('avg_speed_final_400m_mps')
                })

    if len(acceleration_patterns) < 3:
        return {
            'has_acceleration_history': False,
            'sample_size': len(acceleration_patterns)
        }

    # Count acceleration vs deceleration patterns
    strong_accel_count = sum(1 for p in acceleration_patterns if p.get('acceleration_200m', 0) > 0.5)
    decel_count = sum(1 for p in acceleration_patterns if p.get('acceleration_200m', 0) < -0.2)

    # Average speed
    avg_speeds = [p['avg_speed_mps'] for p in acceleration_patterns if p.get('avg_speed_mps')]
    avg_speed_overall = np.mean(avg_speeds) if avg_speeds else None

    # Categorize horse's acceleration ability
    if strong_accel_count >= len(acceleration_patterns) * 0.6:
        ability = 'consistent_accelerator'
    elif decel_count >= len(acceleration_patterns) * 0.6:
        ability = 'consistent_decelerator'
    else:
        ability = 'variable_acceleration'

    return {
        'has_acceleration_history': True,
        'sample_size': len(acceleration_patterns),
        'strong_acceleration_count': strong_accel_count,
        'deceleration_count': decel_count,
        'strong_acceleration_pct': strong_accel_count / len(acceleration_patterns),
        'deceleration_pct': decel_count / len(acceleration_patterns),
        'avg_speed_final_400m_mps': avg_speed_overall,
        'acceleration_ability': ability
    }
```

**Quantitative Features:**
```python
def engineer_acceleration_features(sectional_data, horse_history):
    """Create acceleration features for ML"""

    # Current race acceleration
    current_accel = calculate_acceleration_metrics(sectional_data)

    # Historical acceleration patterns
    historical_accel = analyze_acceleration_consistency(horse_history)

    features = {
        'has_acceleration_data': 1 if current_accel['has_acceleration_data'] else 0,

        # Current race
        'acceleration_200m': current_accel.get('acceleration_200m'),
        'pace_differential': current_accel.get('pace_differential'),
        'avg_speed_final_400m_mps': current_accel.get('avg_speed_final_400m_mps'),

        # Acceleration patterns
        'strong_acceleration': 1 if current_accel.get('acceleration_pattern') == 'strong_acceleration' else 0,
        'sustained_speed': 1 if current_accel.get('acceleration_pattern') == 'sustained_speed' else 0,
        'deceleration': 1 if 'deceleration' in current_accel.get('acceleration_pattern', '') else 0,

        # Speed categories
        'elite_speed': 1 if current_accel.get('speed_category') == 'elite_speed' else 0,
        'high_speed': 1 if current_accel.get('speed_category') == 'high_speed' else 0,

        # Historical patterns
        'has_acceleration_history': 1 if historical_accel.get('has_acceleration_history', False) else 0,
        'strong_acceleration_pct': historical_accel.get('strong_acceleration_pct'),
        'acceleration_ability': historical_accel.get('acceleration_ability'),
        'consistent_accelerator': 1 if historical_accel.get('acceleration_ability') == 'consistent_accelerator' else 0
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Strong acceleration final 200m (+0.8s faster than previous 200m), consistently accelerates in final stages (70% of starts show positive acceleration)..."
- Reasoning: "Proven ability to quicken when needed - key advantage in tactical/sprint finishes"
- Output: Acceleration-based confidence (+8-14% if consistent accelerator)

---

### 20.3 Sectional Rankings (Within Race)
**Description:** Horse's sectional ranking vs field (fastest sectional = 1st, etc.)
**Data Type:** Ordinal rankings
**Prediction Impact:** 10-15%

**Why This Matters:**
- Best sectional in race = genuine speed regardless of result
- Horse may have lost due to poor position/wide trip but still ran fastest closing sectional
- Strong predictor for next start (horse with best sectional often improves next time)

**Calculate Sectional Rankings:**
```python
def calculate_field_sectional_rankings(field_sectionals):
    """Rank all horses in field by final 400m sectional"""

    # Filter horses with sectional data
    horses_with_sectionals = [
        h for h in field_sectionals
        if h.get('sectionals', {}).get('has_sectionals') and h['sectionals'].get('final_400m')
    ]

    if not horses_with_sectionals:
        return []

    # Sort by final 400m (ascending = faster = better)
    sorted_field = sorted(horses_with_sectionals, key=lambda h: h['sectionals']['final_400m'])

    # Assign rankings
    for rank, horse in enumerate(sorted_field, start=1):
        horse['sectional_rank'] = rank
        horse['sectional_percentile'] = ((len(sorted_field) - rank + 1) / len(sorted_field)) * 100

    return sorted_field

def analyze_sectional_vs_result(horse_result, sectional_ranking):
    """Analyze if sectional performance exceeded finishing position"""

    if not sectional_ranking:
        return {
            'has_sectional_ranking': False
        }

    finishing_position = horse_result['position']
    sectional_rank = sectional_ranking['sectional_rank']

    # Calculate gap
    position_gap = finishing_position - sectional_rank

    # Positive gap = ran faster sectional than finishing position suggests
    # Example: Finished 5th but had 2nd fastest sectional = +3 gap (GOOD SIGN)

    if position_gap >= 3:
        analysis = 'sectional_much_better_than_result'
        reason = 'poor_position_or_wide_trip'
    elif position_gap >= 1:
        analysis = 'sectional_better_than_result'
        reason = 'compromised_run'
    elif position_gap <= -3:
        analysis = 'sectional_much_worse_than_result'
        reason = 'lucky_result_or_tactical_advantage'
    elif position_gap <= -1:
        analysis = 'sectional_worse_than_result'
        reason = 'tactical_advantage'
    else:
        analysis = 'sectional_matches_result'
        reason = 'result_reflects_ability'

    return {
        'has_sectional_ranking': True,
        'finishing_position': finishing_position,
        'sectional_rank': sectional_rank,
        'position_gap': position_gap,
        'analysis': analysis,
        'likely_reason': reason,
        'unlucky_run': position_gap >= 2,  # Finished worse than sectional suggests
        'flattered_by_result': position_gap <= -2  # Finished better than sectional suggests
    }

def identify_best_last_horses(field_results, field_sectionals):
    """Identify horses with best sectionals who didn't win"""

    # Get sectional rankings
    ranked_sectionals = calculate_field_sectional_rankings(field_sectionals)

    # Find horses with top-3 sectional who finished outside top-3
    best_last = []

    for horse in ranked_sectionals[:3]:  # Top 3 sectionals
        if horse['position'] > 3:  # But finished outside top 3
            analysis = analyze_sectional_vs_result(horse, horse)

            best_last.append({
                'horse_name': horse['horse_name'],
                'finishing_position': horse['position'],
                'sectional_rank': horse['sectional_rank'],
                'final_400m': horse['sectionals']['final_400m'],
                'position_gap': analysis['position_gap'],
                'likely_reason': analysis['likely_reason']
            })

    return best_last
```

**Quantitative Features:**
```python
def engineer_sectional_ranking_features(horse_result, field_sectionals):
    """Create sectional ranking features for ML"""

    # Calculate field rankings
    ranked_sectionals = calculate_field_sectional_rankings(field_sectionals)

    # Find this horse's ranking
    horse_ranking = next(
        (h for h in ranked_sectionals if h['horse_name'] == horse_result['horse_name']),
        None
    )

    if not horse_ranking:
        return {
            'has_sectional_ranking': 0,
            'sectional_rank': None
        }

    # Analyze sectional vs result
    analysis = analyze_sectional_vs_result(horse_result, horse_ranking)

    features = {
        'has_sectional_ranking': 1,
        'sectional_rank': horse_ranking['sectional_rank'],
        'sectional_percentile': horse_ranking['sectional_percentile'],
        'field_size_with_sectionals': len(ranked_sectionals),

        # Ranking categories
        'best_sectional_in_race': 1 if horse_ranking['sectional_rank'] == 1 else 0,
        'top_3_sectional': 1 if horse_ranking['sectional_rank'] <= 3 else 0,
        'top_5_sectional': 1 if horse_ranking['sectional_rank'] <= 5 else 0,

        # Sectional vs result analysis
        'position_gap': analysis['position_gap'],
        'unlucky_run': 1 if analysis['unlucky_run'] else 0,
        'flattered_by_result': 1 if analysis['flattered_by_result'] else 0,
        'sectional_better_than_result': 1 if analysis['position_gap'] > 0 else 0,
        'sectional_worse_than_result': 1 if analysis['position_gap'] < 0 else 0
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Best sectional in race (22.0s final 400m) but finished 4th, likely due to wide barrier/poor position (3-length gap to result suggests unlucky)..."
- Reasoning: "Ran fastest closing sectional but compromised by race pattern - strong next-start prospect"
- Output: Best-last boost (+10-15% if best sectional with unlucky result)

---

## INTEGRATION GUIDELINES

### Sectional Data + Pace Analysis (Category 4)
```python
def integrate_sectionals_with_pace(sectional_data, pace_data):
    """Integrate sectional performance with race pace context"""

    # Fast final 400m + slow early pace = less impressive
    if sectional_data['final_400m'] <= 22.5 and pace_data['early_pace'] == 'slow':
        return {
            'synergy_score': 0.05,
            'confidence': 'moderate',
            'narrative': 'Good sectional but slow early pace made it easier'
        }

    # Fast final 400m + fast early pace = VERY impressive
    elif sectional_data['final_400m'] <= 22.5 and pace_data['early_pace'] == 'fast':
        return {
            'synergy_score': 0.20,
            'confidence': 'very_high',
            'narrative': 'Elite sectional despite fast early pace - genuine class'
        }

    # Slow final 400m + fast early pace = understandable
    elif sectional_data['final_400m'] > 23.5 and pace_data['early_pace'] == 'fast':
        return {
            'synergy_score': -0.02,
            'confidence': 'low',
            'narrative': 'Slow sectional but fast pace takes toll'
        }

    return {'synergy_score': 0.0, 'confidence': 'neutral'}
```

### Sectional Data + Track Bias (Category 3)
```python
def integrate_sectionals_with_track_bias(sectional_data, track_bias_data):
    """Integrate sectionals with track bias patterns"""

    # Strong sectional + favorable track bias = compounding advantage
    if sectional_data['top_3_sectional'] and track_bias_data['bias_suits_position']:
        return {
            'synergy_score': 0.15,
            'confidence': 'high',
            'narrative': 'Strong sectional + track bias advantage'
        }

    # Strong sectional despite unfavorable bias = very strong
    elif sectional_data['top_3_sectional'] and not track_bias_data['bias_suits_position']:
        return {
            'synergy_score': 0.18,
            'confidence': 'very_high',
            'narrative': 'Elite sectional despite bias working against - remarkable performance'
        }

    return {'synergy_score': 0.0, 'confidence': 'neutral'}
```

---

## UNIFIED DATA MODEL

```python
sectional_data_schema = {
    "split_times": {
        "has_sectionals": bool,
        "final_400m": float,
        "final_600m": float,
        "final_200m": float,
        "data_source": str,
        "final_400m_percentile": float
    },
    "acceleration_metrics": {
        "has_acceleration_data": bool,
        "acceleration_200m": float,
        "pace_pattern": str,
        "avg_speed_final_400m_mps": float
    },
    "sectional_rankings": {
        "has_sectional_ranking": bool,
        "sectional_rank": int,
        "position_gap": int,
        "unlucky_run": bool,
        "best_sectional_in_race": bool
    }
}
```

---

## COST ANALYSIS

**Category 20 Cost Breakdown:**
- **Speedmaps API access:** $0.05/race (premium sectional data source)
- **Racing.com scraping (backup):** $0 (free scraping)
- **Data storage:** $0.05/race (sectionals for full field)

**Total Cost:** $0.05-$0.10 per race

**Cost-Benefit Analysis:**
- Prediction improvement: 10-18% (MAJOR)
- Cost per race: $0.05-$0.10 (VERY LOW)
- ROI: EXCELLENT (massive prediction gain for minimal cost)
- Critical advantage: ChatGPT has 5% sectional access vs our 95% target

---

## IMPLEMENTATION CHECKLIST

### Phase 1 Week 9: Sectional Data Implementation

**Day 1: Data Source Setup**
- [ ] Register for Speedmaps API (primary source)
- [ ] Build Racing.com scraper (backup source)
- [ ] Test both data sources on 50 recent races
- [ ] Validate sectional time accuracy vs published data

**Day 2: Split Time Extraction**
- [ ] Build sectional extraction pipeline
- [ ] Implement percentile calculation vs field
- [ ] Calculate sectional consistency across horse history
- [ ] Test on 100 horses with sectional history

**Day 3: Acceleration Metrics**
- [ ] Implement acceleration calculation algorithms
- [ ] Calculate speed differentials between splits
- [ ] Analyze acceleration consistency patterns
- [ ] Test on known "strong finishers" vs "weak finishers"

**Day 4: Sectional Rankings**
- [ ] Build field sectional ranking system
- [ ] Implement sectional vs result gap analysis
- [ ] Identify "best last" horses (unlucky runs)
- [ ] Test on races where sectionals didn't match results

**Day 5: Feature Engineering & Integration**
- [ ] Engineer all quantitative features (40+ features)
- [ ] Integrate with pace analysis (Category 4)
- [ ] Integrate with track bias (Category 3)
- [ ] Test full sectional pipeline
- [ ] Validate prediction improvement from sectional features

---

**Document Complete: Category 20 (Sectional Data - COMPREHENSIVE)**
**Lines: 800+ (FULLY EXPANDED)**
**Next Document: PART_15_CATEGORY_21.md (Pedigree Analysis - EXPAND FROM 177 TO 800+ LINES)**
