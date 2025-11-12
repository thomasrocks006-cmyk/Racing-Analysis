# Master Taxonomy - Part 16: Cross-Category Integration Matrix (Categories 1-7)

**Document Purpose:** Rules for combining insights from multiple categories (first half)
**Pipeline Usage:** Both pipelines (integration logic)
**Implementation Priority:** Phase 2 Week 1

---

## INTEGRATION PRINCIPLES

### Core Rules

1. **Multiplicative vs Additive Adjustments**
   - Multiplicative: When categories interact (barrier × track bias)
   - Additive: When categories are independent (weight + jockey skill)

2. **Confidence Hierarchy**
   - Historical Performance (14) > Speed Ratings (18) > Market (12) > Other categories
   - When categories contradict, trust higher-confidence categories

3. **Sample Size Requirements**
   - Minimum 3 data points for any statistical feature
   - Minimum 5 data points for high-confidence assertions

---

## CATEGORY INTEGRATION MATRICES

### Distance (1.1) × Venue (1.2)
```python
def integrate_distance_venue(distance, venue, horse_history):
    """Integrate distance and venue suitability"""

    # Specific venue+distance combo (strongest signal)
    venue_distance_records = [
        r for r in horse_history
        if r['venue'] == venue and abs(r['distance'] - distance) <= 100
    ]

    if len(venue_distance_records) >= 3:
        return {
            'synergy_type': 'specific_combo',
            'confidence': 'high',
            'weight': 1.0,
            'records': venue_distance_records
        }

    # Separate venue + distance analysis (moderate signal)
    venue_records = [r for r in horse_history if r['venue'] == venue]
    distance_records = [r for r in horse_history if abs(r['distance'] - distance) <= 100]

    if len(venue_records) >= 3 and len(distance_records) >= 3:
        return {
            'synergy_type': 'separate_analysis',
            'confidence': 'moderate',
            'weight': 0.7,
            'venue_records': venue_records,
            'distance_records': distance_records
        }

    return {
        'synergy_type': 'insufficient_data',
        'confidence': 'low',
        'weight': 0.3
    }
```

### Track Conditions (3) × Barrier (4)
```python
def integrate_track_barrier(track_rating, rail_position, barrier_num, venue, distance):
    """Track condition and barrier interaction"""

    # Rail position affects barrier advantage
    RAIL_EFFECTS = {
        'true_position': {  # Rail out wide
            'inside_barriers': -0.05,  # Inside barriers disadvantaged
            'outside_barriers': +0.05   # Outside barriers advantaged
        },
        '4m_out_or_less': {
            'inside_barriers': +0.03,
            'outside_barriers': -0.03
        }
    }

    # Track condition affects pace/barrier
    CONDITION_EFFECTS = {
        'heavy': {
            'inside_barriers': +0.08,  # Inside rail better in heavy
            'outside_barriers': -0.05
        },
        'firm': {
            'inside_barriers': -0.02,
            'outside_barriers': +0.02
        }
    }

    # Determine barrier category
    barrier_category = 'inside_barriers' if barrier_num <= 6 else 'outside_barriers'

    # Calculate combined effect
    rail_effect = RAIL_EFFECTS.get(rail_position, {}).get(barrier_category, 0)
    condition_effect = CONDITION_EFFECTS.get(categorize_track(track_rating), {}).get(barrier_category, 0)

    combined_barrier_adjustment = rail_effect + condition_effect

    return {
        'barrier_adjustment': combined_barrier_adjustment,
        'rail_component': rail_effect,
        'condition_component': condition_effect,
        'interpretation': generate_barrier_interpretation(combined_barrier_adjustment, barrier_num)
    }

def categorize_track(track_rating):
    """Categorize track condition"""
    if 'Heavy' in track_rating or track_rating in ['Soft 7', 'Soft 6']:
        return 'heavy'
    elif 'Firm' in track_rating:
        return 'firm'
    else:
        return 'good'

def generate_barrier_interpretation(adjustment, barrier_num):
    """Generate qualitative interpretation"""
    if adjustment > 0.05:
        return f"Barrier {barrier_num} significantly favored by conditions (+{adjustment:.0%})"
    elif adjustment < -0.05:
        return f"Barrier {barrier_num} disadvantaged by conditions ({adjustment:.0%})"
    else:
        return f"Barrier {barrier_num} neutral impact"
```

### Weight (5) × Jockey (6)
```python
def integrate_weight_jockey(weight_carried, jockey_data, race_distance):
    """Weight burden and jockey ability interaction"""

    # Jockey skill can mitigate weight burden
    weight_burden = calculate_weight_burden(weight_carried, race_distance)
    jockey_skill = jockey_data.get('career_win_pct', 0.10)

    # Strong jockey reduces weight impact
    if jockey_skill > 0.18:  # Top-tier jockey
        weight_mitigation = 0.70  # Reduces weight penalty by 70%
    elif jockey_skill > 0.12:  # Good jockey
        weight_mitigation = 0.50
    else:  # Average/below jockey
        weight_mitigation = 0.30

    effective_weight_burden = weight_burden * (1 - weight_mitigation)

    # Jockey experience with heavy weights
    heavy_weight_experience = jockey_data.get('rides_over_58kg', 0)
    experience_bonus = min(heavy_weight_experience / 100, 0.05) if weight_carried > 58 else 0

    return {
        'base_weight_burden': weight_burden,
        'effective_weight_burden': effective_weight_burden,
        'jockey_mitigation': weight_mitigation,
        'experience_bonus': experience_bonus,
        'final_weight_impact': effective_weight_burden - experience_bonus
    }

def calculate_weight_burden(weight_kg, distance_m):
    """Calculate weight burden (longer races = higher impact)"""

    base_burden = (weight_kg - 54) * 0.01  # 1% per kg above 54kg

    # Distance multiplier
    if distance_m > 2000:
        distance_multiplier = 1.5  # Weight hurts more in staying races
    elif distance_m > 1600:
        distance_multiplier = 1.2
    elif distance_m < 1200:
        distance_multiplier = 0.8  # Weight matters less in sprints
    else:
        distance_multiplier = 1.0

    return base_burden * distance_multiplier
```

### Trainer (7) × Jockey (6) × Horse (Partnership)
```python
def integrate_trainer_jockey_partnership(trainer_data, jockey_data, partnership_data):
    """Trainer-jockey partnership synergy"""

    # Individual performances
    trainer_win_pct = trainer_data.get('career_win_pct', 0.15)
    jockey_win_pct = jockey_data.get('career_win_pct', 0.10)

    # Expected combined performance (if independent)
    expected_combined = (trainer_win_pct + jockey_win_pct) / 2

    # Actual partnership performance
    if partnership_data.get('partnership_rides', 0) >= 10:
        actual_partnership_pct = partnership_data['partnership_win_pct']
        synergy_score = actual_partnership_pct - expected_combined

        if synergy_score > 0.10:
            synergy_level = 'strong'
            synergy_boost = 0.15  # 15% boost
        elif synergy_score > 0.05:
            synergy_level = 'moderate'
            synergy_boost = 0.08
        else:
            synergy_level = 'weak'
            synergy_boost = 0.02
    else:
        synergy_level = 'unknown'
        synergy_boost = 0.00

    return {
        'expected_combined_win_pct': expected_combined,
        'actual_partnership_win_pct': partnership_data.get('partnership_win_pct'),
        'synergy_score': synergy_score if partnership_data.get('partnership_rides', 0) >= 10 else None,
        'synergy_level': synergy_level,
        'synergy_boost': synergy_boost
    }
```

---

## CONTRADICTION RESOLUTION

### When Categories Disagree

**Example: Strong Historical Performance vs Poor Market Support**
```python
def resolve_form_market_contradiction(form_score, market_position):
    """Resolve when form and market disagree"""

    # Case 1: Excellent form (80+) but drifting in market
    if form_score > 80 and market_position == 'drifter':
        return {
            'interpretation': 'Market may be undervaluing form - potential value',
            'recommended_action': 'Trust form over market (70% weight to form)',
            'confidence': 'moderate',
            'reasoning': 'Recent form is concrete data, market can overreact'
        }

    # Case 2: Poor form (40-) but steaming in market
    elif form_score < 40 and market_position == 'steamer':
        return {
            'interpretation': 'Market knows something we don\'t - inside info likely',
            'recommended_action': 'Trust market over form (60% weight to market)',
            'confidence': 'moderate',
            'reasoning': 'Market steamers often indicate stable confidence/gear changes'
        }

    # Case 3: No strong contradiction
    else:
        return {
            'interpretation': 'Form and market aligned',
            'recommended_action': 'Equal weighting',
            'confidence': 'high'
        }
```

**Example: Venue Specialist vs Poor Current Form**
```python
def resolve_venue_form_contradiction(venue_specialist, form_score):
    """Resolve when venue suitability contradicts current form"""

    # Venue specialist (70%+ win rate at venue) but poor form
    if venue_specialist and form_score < 50:
        return {
            'interpretation': 'Venue suitability may trump poor form - worth consideration',
            'recommended_action': 'Weight venue specialist 60%, form 40%',
            'confidence': 'moderate',
            'reasoning': 'Horses often perform above form at favored venues'
        }

    # Not venue specialist but excellent form
    elif not venue_specialist and form_score > 75:
        return {
            'interpretation': 'Strong current form compensates for venue unfamiliarity',
            'recommended_action': 'Weight form 70%, venue 30%',
            'confidence': 'high',
            'reasoning': 'In-form horses can perform anywhere'
        }

    return {
        'interpretation': 'Venue and form aligned',
        'recommended_action': 'Equal weighting'
    }
```

---

## CONFIDENCE SCORING FRAMEWORK

### Aggregate Confidence Calculation

```python
def calculate_aggregate_confidence(category_data):
    """Calculate overall prediction confidence from all categories"""

    confidence_components = []

    # Historical Performance (highest weight)
    if category_data.get('form_score'):
        form_confidence = min(category_data['form_starts'] / 10, 1.0)  # Sample size confidence
        confidence_components.append(('form', form_confidence * 0.25))

    # Speed Ratings
    if category_data.get('speed_rating'):
        speed_confidence = 0.20 if category_data.get('has_recent_speed_rating') else 0.10
        confidence_components.append(('speed', speed_confidence))

    # Market
    if category_data.get('market_position'):
        market_confidence = 0.15
        confidence_components.append(('market', market_confidence))

    # Venue/Distance Suitability
    if category_data.get('venue_specialist') or category_data.get('distance_specialist'):
        suitability_confidence = 0.12
        confidence_components.append(('suitability', suitability_confidence))

    # Jockey/Trainer Partnership
    if category_data.get('strong_partnership'):
        partnership_confidence = 0.10
        confidence_components.append(('partnership', partnership_confidence))

    # Other categories
    other_confidence = 0.18
    confidence_components.append(('other', other_confidence))

    # Aggregate
    total_confidence = sum(score for _, score in confidence_components)

    return {
        'aggregate_confidence': total_confidence,
        'confidence_breakdown': dict(confidence_components),
        'confidence_category': 'high' if total_confidence > 0.75 else
                              'moderate' if total_confidence > 0.50 else
                              'low'
    }
```

---

---

## MULTI-WAY INTEGRATIONS (3+ Categories)

### Track Bias × Barrier × Pace Scenario
```python
def integrate_track_bias_barrier_pace(track_bias, barrier_num, pace_scenario, distance):
    """Three-way integration: Track bias, barrier, and pace"""

    # Inside track bias + inside barrier + on-pace horse = STRONG ADVANTAGE
    if (track_bias.get('favored_positions') == ['inside'] and
        barrier_num <= 4 and
        pace_scenario.get('horse_pace_style') == 'on_pace'):

        return {
            'integration_type': 'triple_synergy',
            'advantage_score': 0.35,  # 35% boost
            'confidence': 'very_high',
            'reasoning': [
                f"Inside barrier ({barrier_num}) allows easy access to favored inside track",
                f"On-pace style ensures early positioning on bias",
                f"Track bias magnifies positional advantage by 2-3 lengths"
            ],
            'qualitative_summary': "PERFECT STORM: Inside draw on inside-biased track with on-pace style"
        }

    # Outside bias + outside barrier + back-marker = MODERATE ADVANTAGE
    elif (track_bias.get('favored_positions') == ['outside'] and
          barrier_num >= 10 and
          pace_scenario.get('horse_pace_style') == 'closer'):

        return {
            'integration_type': 'synergy',
            'advantage_score': 0.20,  # 20% boost
            'confidence': 'high',
            'reasoning': [
                f"Wide barrier ({barrier_num}) positions horse on favored outside rail",
                f"Closer/back-marker style allows time to navigate to outside",
                f"Track bias rewards wide runners"
            ],
            'qualitative_summary': "STRONG SETUP: Wide draw suits outside bias and closing style"
        }

    # Inside bias + outside barrier + on-pace = MAJOR DISADVANTAGE
    elif (track_bias.get('favored_positions') == ['inside'] and
          barrier_num >= 10 and
          pace_scenario.get('horse_pace_style') == 'on_pace'):

        return {
            'integration_type': 'triple_negative',
            'advantage_score': -0.25,  # 25% penalty
            'confidence': 'high',
            'reasoning': [
                f"Wide barrier ({barrier_num}) forces outside position",
                f"On-pace style commits to wide run from start",
                f"Inside bias means losing 2-3 lengths entire race"
            ],
            'qualitative_summary': "MAJOR CONCERN: Wide on-pacer facing inside bias"
        }

    # Sprint distances amplify barrier × bias interaction
    if distance < 1200:
        return enhance_sprint_interaction(track_bias, barrier_num, pace_scenario)

    # Staying races reduce barrier importance
    elif distance > 2000:
        return reduce_staying_barrier_impact(track_bias, barrier_num, pace_scenario)

    return {
        'integration_type': 'neutral',
        'advantage_score': 0.00,
        'confidence': 'moderate',
        'reasoning': ['No strong synergy or conflict detected']
    }


def enhance_sprint_interaction(track_bias, barrier_num, pace_scenario):
    """Sprint races amplify barrier × bias effects"""
    base_integration = integrate_track_bias_barrier_pace(track_bias, barrier_num, pace_scenario, 1000)

    # Amplify advantage/disadvantage by 50% in sprints
    enhanced_score = base_integration.get('advantage_score', 0) * 1.5

    base_integration['advantage_score'] = enhanced_score
    base_integration['reasoning'].append("Sprint distance amplifies barrier × bias effect by 50%")

    return base_integration


def reduce_staying_barrier_impact(track_bias, barrier_num, pace_scenario):
    """Staying races reduce barrier importance"""
    base_integration = integrate_track_bias_barrier_pace(track_bias, barrier_num, pace_scenario, 2400)

    # Reduce advantage/disadvantage by 60% in staying races
    reduced_score = base_integration.get('advantage_score', 0) * 0.4

    base_integration['advantage_score'] = reduced_score
    base_integration['reasoning'].append("Staying distance reduces barrier impact by 60% (time to navigate)")

    return base_integration
```

### Weather × Track Condition × Horse Preference
```python
def integrate_weather_track_horse(weather_data, track_condition, horse_history):
    """Weather, track, and horse wet-track ability integration"""

    # Extract weather factors
    recent_rainfall = weather_data.get('rainfall_72hrs_mm', 0)
    forecast_rain = weather_data.get('forecast_rain', False)
    temperature = weather_data.get('temperature_c', 20)

    # Track condition rating
    track_rating = track_condition.get('official_rating', 'Good 4')
    penetrometer = track_condition.get('penetrometer', 5.0)

    # Horse wet-track performance
    wet_track_record = calculate_wet_track_record(horse_history)

    # Scenario 1: Heavy track + proven wet-tracker
    if penetrometer > 6.0 and wet_track_record['win_rate'] > 0.30:
        return {
            'scenario': 'proven_wet_tracker_on_heavy',
            'advantage_score': 0.40,  # 40% boost
            'confidence': 'very_high',
            'reasoning': [
                f"Heavy track (penetrometer {penetrometer}) suits proven wet-tracker",
                f"Horse has {wet_track_record['win_rate']:.0%} win rate on wet",
                f"Many competitors will struggle in heavy - field winnows itself"
            ],
            'qualitative_summary': "MAJOR ADVANTAGE: Elite wet-tracker in heavy conditions",
            'field_impact': 'Expect 30-40% of field to underperform'
        }

    # Scenario 2: Deteriorating track + wet-track question mark
    elif recent_rainfall > 20 and wet_track_record['starts'] == 0:
        return {
            'scenario': 'unproven_wet_track',
            'advantage_score': -0.15,  # 15% penalty (uncertainty)
            'confidence': 'moderate',
            'reasoning': [
                f"Heavy recent rainfall ({recent_rainfall}mm) suggests soft/heavy",
                f"Horse has never raced on wet track - major unknown",
                f"Pedigree suggests wet-track ability but unproven"
            ],
            'qualitative_summary': "RISK FACTOR: Unproven on wet track, conditions likely soft/heavy",
            'recommendation': 'Monitor market - stable confidence may indicate trials/jumpouts on wet'
        }

    # Scenario 3: Drying track + firm-track specialist
    elif recent_rainfall == 0 and temperature > 25 and track_rating == 'Firm 1':
        firm_track_record = calculate_firm_track_record(horse_history)
        if firm_track_record['win_rate'] > 0.25:
            return {
                'scenario': 'firm_track_specialist',
                'advantage_score': 0.25,  # 25% boost
                'confidence': 'high',
                'reasoning': [
                    f"Firm track (rating {track_rating}) suits specialist",
                    f"Hot weather ({temperature}°C) and no rain = fast surface",
                    f"Horse excels on firm: {firm_track_record['win_rate']:.0%} win rate"
                ],
                'qualitative_summary': "STRONG ADVANTAGE: Firm-track specialist in ideal conditions"
            }

    # Scenario 4: Improving track + versatile horse
    elif track_condition.get('track_improving', False):
        return {
            'scenario': 'improving_track_versatile',
            'advantage_score': 0.05,  # 5% boost
            'confidence': 'moderate',
            'reasoning': [
                "Track improving throughout day",
                "Versatile horse can handle changing conditions",
                "Later races on card may see faster times"
            ],
            'qualitative_summary': "MINOR ADVANTAGE: Versatility on improving track"
        }

    return {
        'scenario': 'neutral',
        'advantage_score': 0.00,
        'confidence': 'moderate',
        'reasoning': ['No strong weather × track × horse interaction detected']
    }


def calculate_wet_track_record(horse_history):
    """Calculate horse's wet-track performance"""
    wet_races = [
        r for r in horse_history
        if r.get('track_rating', '') in ['Soft 5', 'Soft 6', 'Soft 7', 'Heavy 8', 'Heavy 9', 'Heavy 10']
    ]

    if not wet_races:
        return {'starts': 0, 'wins': 0, 'win_rate': 0.0, 'avg_position': None}

    wins = sum(1 for r in wet_races if r.get('position') == 1)
    avg_position = sum(r.get('position', 99) for r in wet_races) / len(wet_races)

    return {
        'starts': len(wet_races),
        'wins': wins,
        'win_rate': wins / len(wet_races),
        'avg_position': avg_position
    }


def calculate_firm_track_record(horse_history):
    """Calculate horse's firm-track performance"""
    firm_races = [
        r for r in horse_history
        if r.get('track_rating', '') in ['Firm 1', 'Firm 2', 'Good 3']
    ]

    if not firm_races:
        return {'starts': 0, 'wins': 0, 'win_rate': 0.0}

    wins = sum(1 for r in firm_races if r.get('position') == 1)

    return {
        'starts': len(firm_races),
        'wins': wins,
        'win_rate': wins / len(firm_races)
    }
```

### Market Movement × Gear Change × Jockey Booking
```python
def integrate_market_gear_jockey(market_data, gear_change, jockey_data, horse_data):
    """Market movement, gear, and jockey booking as stable confidence indicator"""

    # Extract signals
    market_movement = market_data.get('movement_category', 'stable')  # 'steamer', 'drifter', 'stable'
    odds_change_pct = market_data.get('odds_change_percent', 0)

    gear_added = gear_change.get('gear_added', [])
    gear_removed = gear_change.get('gear_removed', [])
    significant_gear = any(g in gear_added for g in ['Blinkers', 'Tongue Tie', 'Lugging Bit'])

    jockey_upgrade = jockey_data.get('is_leading_jockey', False)
    jockey_booking_late = jockey_data.get('booking_confirmed_late', False)

    # Scenario 1: STEAMER + GEAR CHANGE + JOCKEY UPGRADE = MAJOR STABLE CONFIDENCE
    if market_movement == 'steamer' and significant_gear and jockey_upgrade:
        return {
            'integration_type': 'triple_stable_confidence',
            'confidence_boost': 0.45,  # 45% boost
            'signal_strength': 'very_strong',
            'reasoning': [
                f"Market steaming: Odds shortened {abs(odds_change_pct):.0%}",
                f"Significant gear added: {', '.join(gear_added)}",
                f"Leading jockey booked: {jockey_data.get('name')}",
                "All three signals indicate major stable confidence"
            ],
            'qualitative_summary': "VERY STRONG BUY: Triple stable confidence signal - market, gear, jockey all positive",
            'interpretation': "Stable clearly expects major improvement - likely trial/jumpout went well"
        }

    # Scenario 2: STEAMER + GEAR REMOVAL = HORSE GOING BETTER
    elif market_movement == 'steamer' and len(gear_removed) > 0:
        return {
            'integration_type': 'improvement_signal',
            'confidence_boost': 0.30,  # 30% boost
            'signal_strength': 'strong',
            'reasoning': [
                f"Market steaming: Odds shortened {abs(odds_change_pct):.0%}",
                f"Gear removed: {', '.join(gear_removed)}",
                "Gear removal + steaming = horse going well, doesn't need aids"
            ],
            'qualitative_summary': "STRONG BUY: Market confident, gear removal suggests horse is thriving",
            'interpretation': "Horse likely training well, stable confident enough to remove aids"
        }

    # Scenario 3: DRIFTER + GEAR ADDED + JOCKEY DOWNGRADE = RED FLAGS
    elif market_movement == 'drifter' and len(gear_added) > 0 and not jockey_upgrade:
        return {
            'integration_type': 'concern_cluster',
            'confidence_boost': -0.30,  # 30% penalty
            'signal_strength': 'strong_negative',
            'reasoning': [
                f"Market drifting: Odds blown out {abs(odds_change_pct):.0%}",
                f"Gear added (desperation): {', '.join(gear_added)}",
                "No jockey upgrade - stable not showing confidence",
                "All signals point to concerns about horse's chances"
            ],
            'qualitative_summary': "RED FLAGS: Market, gear, jockey all signal lack of confidence",
            'interpretation': "Stable may be trying gear as last resort, market not convinced"
        }

    # Scenario 4: STABLE MARKET + LATE JOCKEY BOOKING = INSIDER KNOWLEDGE
    elif market_movement == 'stable' and jockey_booking_late and jockey_upgrade:
        return {
            'integration_type': 'quiet_confidence',
            'confidence_boost': 0.20,  # 20% boost
            'signal_strength': 'moderate',
            'reasoning': [
                "Market stable - no obvious money coming",
                f"Late booking of leading jockey {jockey_data.get('name')}",
                "Quiet confidence signal - stable not broadcasting intentions"
            ],
            'qualitative_summary': "MODERATE BUY: Quiet confidence - late jockey upgrade without market fanfare",
            'interpretation': "Stable may be keeping expectations low to preserve odds"
        }

    return {
        'integration_type': 'neutral',
        'confidence_boost': 0.00,
        'signal_strength': 'weak',
        'reasoning': ['No strong market × gear × jockey pattern detected']
    }
```

### Class × Speed Rating × Sectionals
```python
def integrate_class_speed_sectionals(class_data, speed_rating, sectional_data, race_class):
    """Quantitative integration: Class, speed, and sectional analysis"""

    # Extract metrics
    horse_class_rating = class_data.get('official_rating', 70)
    race_class_par = class_data.get('race_par_rating', 75)
    class_gap = race_class_par - horse_class_rating

    last_speed_rating = speed_rating.get('last_start_rating', 85)
    best_speed_rating = speed_rating.get('best_rating_12mo', 90)

    last_sectionals = sectional_data.get('last_start_sectionals', {})
    last_600m = last_sectionals.get('last_600m_time', 35.0)
    last_200m = last_sectionals.get('last_200m_time', 12.0)

    # Scenario 1: CLASS DROP + ELITE SPEED + STRONG FINISH = DOMINANT
    if class_gap < -5 and best_speed_rating > race_class_par + 8 and last_200m < 11.5:
        return {
            'scenario': 'class_dropper_elite_speed',
            'advantage_score': 0.50,  # 50% boost
            'confidence': 'very_high',
            'reasoning': [
                f"Dropping {abs(class_gap)} rating points in class - major advantage",
                f"Best speed rating ({best_speed_rating}) {best_speed_rating - race_class_par} points above race par",
                f"Elite last 200m sectional ({last_200m}s) shows finishing speed",
                "All metrics suggest complete dominance"
            ],
            'qualitative_summary': "ELITE PROSPECT: Class dropper with proven speed and finishing power",
            'win_probability_boost': 0.25  # 25% win probability increase
        }

    # Scenario 2: CLASS RISE + POOR SECTIONALS = MAJOR CONCERN
    elif class_gap > 8 and last_600m > 36.0 and last_200m > 12.5:
        return {
            'scenario': 'class_rise_struggling',
            'advantage_score': -0.35,  # 35% penalty
            'confidence': 'high',
            'reasoning': [
                f"Rising {class_gap} rating points in class - big step up",
                f"Slow last 600m sectional ({last_600m}s) indicates struggling",
                f"Slow last 200m ({last_200m}s) - no finishing punch",
                "Horse likely to be found wanting at higher class"
            ],
            'qualitative_summary': "MAJOR CONCERN: Rising in class with poor sectionals",
            'win_probability_impact': -0.15  # 15% win probability decrease
        }

    # Scenario 3: CORRECT CLASS + IMPROVING SPEED + BEST LAST = CONFIDENCE
    elif abs(class_gap) <= 3 and speed_rating.get('trend', 'stable') == 'improving' and last_200m < 11.8:
        return {
            'scenario': 'correct_class_improving',
            'advantage_score': 0.25,  # 25% boost
            'confidence': 'high',
            'reasoning': [
                f"Correct class level (rating {horse_class_rating} vs par {race_class_par})",
                "Speed ratings improving - horse on upward trajectory",
                f"Strong last 200m ({last_200m}s) - finishing well",
                "Well-placed horse with positive indicators"
            ],
            'qualitative_summary': "STRONG CONTENDER: Correct class with improving speed and finishing ability"
        }

    # Scenario 4: CLASS PERFECT MATCH + SPEED PEAK = FAIR CHANCE
    elif abs(class_gap) <= 2 and abs(last_speed_rating - best_speed_rating) <= 3:
        return {
            'scenario': 'well_matched',
            'advantage_score': 0.10,  # 10% boost
            'confidence': 'moderate',
            'reasoning': [
                f"Perfect class match (rating {horse_class_rating} vs par {race_class_par})",
                f"Recent speed rating ({last_speed_rating}) near best ({best_speed_rating}) - running well",
                "Horse is competitive at this level"
            ],
            'qualitative_summary': "FAIR CHANCE: Well-matched and running to ability"
        }

    return {
        'scenario': 'neutral',
        'advantage_score': 0.00,
        'confidence': 'moderate',
        'reasoning': ['No strong class × speed × sectional pattern detected']
    }
```

---

## ADVANCED SYNERGY CALCULATIONS

### Multiplicative Synergy Framework
```python
def calculate_multiplicative_synergy(category_scores, interaction_matrix):
    """
    Calculate synergies where categories multiply effects

    Example: Track bias × barrier × pace all interact multiplicatively
    """

    base_score = 1.0

    # Apply each category's multiplicative effect
    for category, score in category_scores.items():
        category_multiplier = 1.0 + score  # Convert -0.2 to 0.8, +0.3 to 1.3
        base_score *= category_multiplier

    # Apply interaction bonuses/penalties
    for interaction, effect in interaction_matrix.items():
        cat_a, cat_b = interaction.split('×')
        if cat_a in category_scores and cat_b in category_scores:
            # Both categories present - apply interaction
            interaction_multiplier = 1.0 + effect
            base_score *= interaction_multiplier

    # Convert back to advantage score
    advantage_score = base_score - 1.0

    return {
        'base_score': base_score,
        'advantage_score': advantage_score,
        'synergy_type': 'multiplicative',
        'components': category_scores,
        'interactions': interaction_matrix
    }


# Example usage
category_scores = {
    'track_bias': 0.15,      # 15% advantage from bias
    'barrier': 0.10,          # 10% advantage from draw
    'pace': 0.08,             # 8% advantage from pace setup
}

interaction_matrix = {
    'track_bias×barrier': 0.12,  # Extra 12% when bias + barrier align
    'barrier×pace': 0.08,          # Extra 8% when barrier + pace align
    'track_bias×pace': 0.10,       # Extra 10% when bias + pace align
}

synergy_result = calculate_multiplicative_synergy(category_scores, interaction_matrix)
# Result: ~56% total advantage (not just 33% from adding)
```

### Additive Synergy Framework
```python
def calculate_additive_synergy(category_scores, cap_at=0.70):
    """
    Calculate synergies where categories add effects

    Example: Weight + jockey skill + trainer skill add independently
    """

    total_score = sum(category_scores.values())

    # Cap total synergy to prevent unrealistic predictions
    if total_score > cap_at:
        scaling_factor = cap_at / total_score
        adjusted_scores = {k: v * scaling_factor for k, v in category_scores.items()}
        total_score = cap_at
    else:
        adjusted_scores = category_scores

    return {
        'total_score': total_score,
        'synergy_type': 'additive',
        'components': adjusted_scores,
        'capped': total_score >= cap_at
    }


# Example usage
category_scores = {
    'jockey_skill': 0.15,
    'trainer_skill': 0.12,
    'weight_advantage': 0.08,
    'partnership': 0.10
}

synergy_result = calculate_additive_synergy(category_scores)
# Result: 45% total advantage (sum of all components, capped if needed)
```

### Conditional Synergy Framework
```python
def calculate_conditional_synergy(primary_category, secondary_categories, conditions):
    """
    Calculate synergies that only activate under specific conditions

    Example: Pedigree only matters for young horses, class only matters at extremes
    """

    synergies = []

    for condition_name, condition_check in conditions.items():
        if condition_check():
            # Condition met - activate synergy
            secondary_score = secondary_categories.get(condition_name, 0)
            synergy_bonus = primary_category * secondary_score * 0.5  # 50% boost

            synergies.append({
                'condition': condition_name,
                'activated': True,
                'bonus': synergy_bonus
            })
        else:
            synergies.append({
                'condition': condition_name,
                'activated': False,
                'bonus': 0.0
            })

    total_conditional_synergy = sum(s['bonus'] for s in synergies)

    return {
        'primary_score': primary_category,
        'conditional_synergies': synergies,
        'total_synergy': primary_category + total_conditional_synergy
    }


# Example usage
def is_young_horse():
    return horse_age <= 3

def is_extreme_class_gap():
    return abs(class_gap) > 10

conditions = {
    'pedigree': is_young_horse,
    'class_emphasis': is_extreme_class_gap
}

primary_score = 0.20  # Base horse quality score
secondary_scores = {
    'pedigree': 0.15,
    'class_emphasis': 0.25
}

synergy_result = calculate_conditional_synergy(primary_score, secondary_scores, conditions)
```

---

## CONFLICT RESOLUTION ALGORITHMS

### Weighted Voting System
```python
def resolve_conflicts_weighted_voting(category_predictions, confidence_weights):
    """
    Resolve conflicts using confidence-weighted voting

    Each category "votes" for a prediction, weighted by confidence
    """

    votes = {}

    for category, prediction in category_predictions.items():
        confidence = confidence_weights.get(category, 0.5)
        horse_id = prediction['horse_id']

        if horse_id not in votes:
            votes[horse_id] = {
                'total_confidence': 0.0,
                'supporting_categories': []
            }

        votes[horse_id]['total_confidence'] += confidence
        votes[horse_id]['supporting_categories'].append(category)

    # Rank horses by confidence-weighted votes
    ranked_horses = sorted(
        votes.items(),
        key=lambda x: x[1]['total_confidence'],
        reverse=True
    )

    return {
        'predicted_winner': ranked_horses[0][0] if ranked_horses else None,
        'confidence': ranked_horses[0][1]['total_confidence'] if ranked_horses else 0.0,
        'supporting_categories': ranked_horses[0][1]['supporting_categories'] if ranked_horses else [],
        'full_rankings': ranked_horses
    }


# Example usage
category_predictions = {
    'form': {'horse_id': 5, 'prediction': 'win'},
    'speed_rating': {'horse_id': 5, 'prediction': 'win'},
    'market': {'horse_id': 3, 'prediction': 'win'},
    'jockey': {'horse_id': 5, 'prediction': 'place'},
    'track_bias': {'horse_id': 7, 'prediction': 'win'}
}

confidence_weights = {
    'form': 0.25,
    'speed_rating': 0.20,
    'market': 0.15,
    'jockey': 0.12,
    'track_bias': 0.10
}

result = resolve_conflicts_weighted_voting(category_predictions, confidence_weights)
# Horse 5 wins with 0.57 confidence (form + speed + jockey support)
```

### Tiered Override System
```python
def resolve_conflicts_tiered_override(category_predictions, tier_hierarchy):
    """
    Resolve conflicts using tier hierarchy - higher tiers override lower

    Tier 1: Historical Performance, Speed Ratings (concrete data)
    Tier 2: Market, Class, Sectionals (strong indicators)
    Tier 3: Jockey, Trainer, Track Bias (supporting factors)
    Tier 4: Intangibles, Chemistry (soft factors)
    """

    # Group predictions by tier
    tiered_predictions = {tier: [] for tier in range(1, 5)}

    for category, prediction in category_predictions.items():
        tier = tier_hierarchy.get(category, 4)
        tiered_predictions[tier].append({
            'category': category,
            'prediction': prediction
        })

    # Start from Tier 1, look for consensus
    for tier in range(1, 5):
        tier_predictions = tiered_predictions[tier]

        if not tier_predictions:
            continue

        # Check for consensus within tier
        horse_votes = {}
        for pred in tier_predictions:
            horse_id = pred['prediction']['horse_id']
            horse_votes[horse_id] = horse_votes.get(horse_id, 0) + 1

        # If any horse has majority within tier, that's our answer
        max_votes = max(horse_votes.values()) if horse_votes else 0
        if max_votes > len(tier_predictions) / 2:
            winner_id = max(horse_votes, key=horse_votes.get)
            supporting_cats = [
                p['category'] for p in tier_predictions
                if p['prediction']['horse_id'] == winner_id
            ]

            return {
                'predicted_winner': winner_id,
                'deciding_tier': tier,
                'supporting_categories': supporting_cats,
                'override_applied': tier < 4,  # Was a higher tier decision
                'confidence': 'high' if tier <= 2 else 'moderate'
            }

    # No consensus - return most common across all tiers
    all_predictions = [p['prediction']['horse_id'] for tier_preds in tiered_predictions.values() for p in tier_preds]
    winner_id = max(set(all_predictions), key=all_predictions.count)

    return {
        'predicted_winner': winner_id,
        'deciding_tier': None,
        'confidence': 'low',
        'override_applied': False
    }


# Example usage
tier_hierarchy = {
    'form': 1,
    'speed_rating': 1,
    'sectionals': 2,
    'class': 2,
    'market': 2,
    'jockey': 3,
    'trainer': 3,
    'track_bias': 3,
    'chemistry': 4,
    'intangibles': 4
}
```

---

**Document Complete: Part 16 (Integration Matrix Categories 1-7) - EXPANDED**
**Total Lines: 650+**
**Next: Part 17 (Integration Matrix Categories 8-14)**

```
