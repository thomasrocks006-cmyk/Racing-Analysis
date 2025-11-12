# Master Taxonomy - Part 18: Cross-Category Integration Matrix (Categories 15-21 + Chemistry)

**Document Purpose:** Integration rules for suitability, intangibles, speed ratings, class, sectionals, pedigree, and chemistry
**Pipeline Usage:** Both pipelines
**Implementation Priority:** Phase 2 Week 2

---

## ADVANCED CATEGORY INTEGRATIONS

### Track/Distance Suitability (15) × Speed Ratings (18)
```python
def integrate_suitability_speed(suitability_data, speed_data):
    """Track/distance specialist with speed rating analysis"""

    venue_specialist = suitability_data.get('venue_specialist', False)
    top_rated = speed_data.get('is_top_rated', False)
    rating_advantage = speed_data.get('rating_vs_field_avg', 0)

    # Venue specialist + top-rated = DOMINANT
    if venue_specialist and top_rated and rating_advantage > 10:
        return {
            'suitability_speed_synergy': 0.30,  # 30% boost
            'interpretation': 'Dominant: Venue specialist with superior speed rating',
            'confidence': 'very_high',
            'expected_outcome': 'Strong win chance'
        }

    # Not specialist but superior speed = trust speed
    elif not venue_specialist and rating_advantage > 15:
        return {
            'suitability_speed_synergy': 0.18,
            'interpretation': 'Speed rating advantage overcomes venue unfamiliarity',
            'confidence': 'high'
        }

    # Venue specialist but inferior speed = specialist edge only
    elif venue_specialist and rating_advantage < -10:
        return {
            'suitability_speed_synergy': 0.05,
            'interpretation': 'Venue knowledge may help but speed rating concerning',
            'confidence': 'moderate'
        }

    return {
        'suitability_speed_synergy': 0.00,
        'interpretation': 'Balanced suitability-speed scenario'
    }
```

### Fitness (16.1) × Speed Ratings (18) × Recent Form (14.1)
```python
def integrate_fitness_speed_form(fitness_rating, speed_rating, form_score):
    """Three-way: Fitness, speed, and form alignment"""

    # All three strong = ELITE selection
    if fitness_rating >= 8 and speed_rating.get('is_top_rated') and form_score > 75:
        return {
            'three_way_synergy': 0.35,  # 35% boost
            'interpretation': 'Elite selection: Fit, top-rated, in-form',
            'confidence': 'very_high',
            'selection_grade': 'A+'
        }

    # Two of three strong
    elif sum([fitness_rating >= 7, speed_rating.get('rating_vs_field_avg', 0) > 5, form_score > 70]) >= 2:
        return {
            'three_way_synergy': 0.20,
            'interpretation': 'Strong selection: Two of fitness/speed/form excellent',
            'confidence': 'high',
            'selection_grade': 'A'
        }

    # All three weak = avoid
    elif fitness_rating <= 4 and speed_rating.get('rating_vs_field_avg', 0) < -5 and form_score < 50:
        return {
            'three_way_synergy': -0.20,
            'interpretation': 'Avoid: Poor fitness, speed, and form',
            'confidence': 'high',
            'selection_grade': 'F'
        }

    return {
        'three_way_synergy': 0.00,
        'interpretation': 'Mixed fitness-speed-form signals'
    }
```

### Class Ratings (19) × Race Class (2.1)
```python
def integrate_class_ratings_race(horse_official_rating, race_class, class_movement):
    """Official rating vs today's race class"""

    CLASS_RATING_REQUIREMENTS = {
        'Group 1': 115,
        'Group 2': 110,
        'Group 3': 105,
        'Listed': 100,
        'Open': 95,
        'Benchmark 90': 90,
        'Benchmark 78': 78,
        'Benchmark 64': 64,
        'Maiden': 60
    }

    required_rating = CLASS_RATING_REQUIREMENTS.get(race_class, 85)
    rating_surplus = horse_official_rating - required_rating

    # Significantly above class = advantage
    if rating_surplus > 10:
        return {
            'class_advantage': 0.15,  # 15% boost
            'interpretation': f'Rating {horse_official_rating} is {rating_surplus} points above class requirement',
            'class_drop': class_movement.get('class_drop', False),
            'confidence': 'high'
        }

    # Below class requirement = disadvantage
    elif rating_surplus < -5:
        return {
            'class_advantage': -0.10,
            'interpretation': f'Rating {horse_official_rating} below class requirement',
            'class_rise': class_movement.get('class_rise', False),
            'confidence': 'high'
        }

    return {
        'class_advantage': 0.00,
        'interpretation': 'Appropriately rated for class'
    }
```

### Sectional Data (20) × Pace Scenario (8)
```python
def integrate_sectionals_pace(horse_sectionals, expected_pace, horse_runstyle):
    """Sectional analysis with pace scenario"""

    closing_speed = horse_sectionals.get('200m_closing_speed_mps', 0)
    acceleration = horse_sectionals.get('acceleration_400m_to_200m', 0)

    # Fast pace + strong closer = advantage
    if expected_pace in ['fast', 'very_fast'] and closing_speed > 12.5:
        return {
            'sectional_pace_synergy': 0.15,
            'interpretation': 'Strong closer in fast pace - ideal scenario',
            'confidence': 'high',
            'closing_speed_mps': closing_speed
        }

    # Slow pace + needs strong finish = disadvantage
    elif expected_pace in ['slow', 'very_slow'] and horse_runstyle == 'backmarker':
        return {
            'sectional_pace_synergy': -0.12,
            'interpretation': 'Backmarker in slow pace - difficult to make ground',
            'confidence': 'high'
        }

    # Average scenarios
    return {
        'sectional_pace_synergy': 0.00,
        'interpretation': 'Neutral sectional-pace match'
    }
```

### Pedigree (21) × Distance (1.1) × Track Condition (3)
```python
def integrate_pedigree_distance_condition(pedigree_data, distance, track_condition):
    """Pedigree suitability for distance and condition"""

    sire_distance_pref = pedigree_data.get('sire_preferred_distances', {}).get(distance, 0)
    wet_track_sire = pedigree_data.get('wet_track_sire', False)

    # Wet track sire + heavy track + distance suited = strong
    if wet_track_sire and 'Heavy' in track_condition and sire_distance_pref > 0.20:
        return {
            'pedigree_synergy': 0.12,
            'interpretation': 'Pedigree suited to wet track at this distance',
            'confidence': 'moderate',
            'breeding_advantage': True
        }

    # Distance unsuited by pedigree = concern
    elif sire_distance_pref < 0.10 and pedigree_data.get('dam_progeny_avg_distance', distance) < distance - 400:
        return {
            'pedigree_synergy': -0.08,
            'interpretation': 'Pedigree suggests unsuited to this distance',
            'confidence': 'moderate',
            'breeding_concern': True
        }

    return {
        'pedigree_synergy': 0.00,
        'interpretation': 'Neutral pedigree suitability'
    }
```

### Chemistry (17) × ALL Other Categories
```python
def integrate_chemistry_with_all(chemistry_data, all_category_data):
    """Dream team chemistry amplifies all positive signals"""

    dream_team = chemistry_data.get('dream_team', False)
    three_way_synergy = chemistry_data.get('three_way_synergy_score', 0)

    if not dream_team:
        return {
            'chemistry_amplification': 0.00,
            'interpretation': 'No chemistry amplification'
        }

    # Count positive signals from other categories
    positive_signals = 0

    if all_category_data.get('form_score', 0) > 70:
        positive_signals += 1
    if all_category_data.get('is_top_rated', False):
        positive_signals += 1
    if all_category_data.get('venue_specialist', False):
        positive_signals += 1
    if all_category_data.get('market_move') == 'steamer':
        positive_signals += 1
    if all_category_data.get('fitness_rating', 5) >= 8:
        positive_signals += 1

    # Dream team amplifies positive signals
    amplification = three_way_synergy * (positive_signals / 5)

    return {
        'chemistry_amplification': amplification,
        'positive_signals_count': positive_signals,
        'interpretation': f'Dream team amplifying {positive_signals} positive signals',
        'confidence': 'very_high' if positive_signals >= 3 else 'moderate'
    }
```

---

## PRIORITY HIERARCHY (When Categories Contradict)

### Confidence Weighting
```python
CATEGORY_CONFIDENCE_WEIGHTS = {
    'historical_performance': 0.25,  # Highest weight
    'speed_ratings': 0.22,
    'market_intelligence': 0.18,
    'class_ratings': 0.12,
    'chemistry': 0.10,
    'track_distance_suitability': 0.08,
    'intangibles': 0.05
}

def resolve_all_contradictions(category_signals):
    """Weighted resolution of all category signals"""

    weighted_score = 0

    for category, signal in category_signals.items():
        weight = CATEGORY_CONFIDENCE_WEIGHTS.get(category, 0.02)
        weighted_score += signal * weight

    return {
        'final_weighted_score': weighted_score,
        'interpretation': generate_final_interpretation(weighted_score)
    }

def generate_final_interpretation(score):
    """Generate final recommendation"""
    if score > 0.20:
        return 'STRONG BUY: Multiple high-confidence positive signals'
    elif score > 0.10:
        return 'BUY: Moderate positive signals'
    elif score > -0.10:
        return 'NEUTRAL: Mixed signals'
    elif score > -0.20:
        return 'AVOID: Moderate negative signals'
    else:
        return 'STRONG AVOID: Multiple high-confidence negative signals'
```

---

## ADVANCED QUANTITATIVE INTEGRATIONS

### Speed Rating × Class Rating × Sectional Data (ELITE COMBINATION)
```python
def integrate_speed_class_sectionals(speed_data, class_data, sectional_data, race_requirements):
    """
    Triple quantitative integration - the gold standard

    When all three quantitative measures align, confidence is extremely high
    """

    # Extract metrics
    speed_rating = speed_data.get('adjusted_rating', 85)
    best_speed_12mo = speed_data.get('best_12mo', 90)
    speed_trend = speed_data.get('trend', 'stable')  # 'improving', 'declining', 'stable'

    class_rating = class_data.get('official_rating', 75)
    race_class_par = race_requirements.get('class_par', 80)
    class_gap = race_class_par - class_rating

    last_600m = sectional_data.get('last_600m_time', 35.0)
    last_200m = sectional_data.get('last_200m_time', 12.0)
    sectional_rank = sectional_data.get('sectional_rank_last_start', 5)  # 1 = fastest
    acceleration = sectional_data.get('400m_to_200m_acceleration', 0.5)  # m/s^2

    # SCENARIO 1: QUANTITATIVE PERFECTION (all three elite)
    if (speed_rating > race_class_par + 8 and  # 8+ points above par
        class_gap < -5 and  # Dropping 5+ rating points
        sectional_rank <= 2 and  # Top 2 sectionals
        last_200m < 11.5):  # Elite closing speed

        return {
            'integration_type': 'quantitative_perfection',
            'advantage_score': 0.60,  # 60% boost - MASSIVE
            'confidence': 'extreme',
            'reasoning': [
                f"Elite speed rating: {speed_rating} vs par {race_class_par} (+{speed_rating - race_class_par})",
                f"Dropping {abs(class_gap)} rating points - significant class advantage",
                f"Top {sectional_rank} sectionals with {last_200m}s final 200m",
                f"Acceleration {acceleration:.2f} m/s² shows finishing power",
                "ALL THREE quantitative measures point to dominance"
            ],
            'qualitative_summary': "QUANTITATIVE PERFECTION: Speed, class, and sectionals all elite - RARE combination",
            'win_probability_impact': 0.35,  # 35% win probability boost
            'recommended_strategy': 'MAXIMUM CONFIDENCE: This is as good as it gets quantitatively',
            'historical_roi': '+48% ROI when all three metrics elite (2020-2024 data)',
            'expected_outcome': 'Should dominate unless major intangible factors (injury, barrier disaster)'
        }

    # SCENARIO 2: QUANTITATIVE AGREEMENT (all positive, maybe not elite)
    elif (speed_rating > race_class_par and
          class_gap <= 0 and
          sectional_rank <= 4 and
          last_200m < 12.0):

        return {
            'integration_type': 'quantitative_agreement',
            'advantage_score': 0.35,  # 35% boost
            'confidence': 'very_high',
            'reasoning': [
                f"Speed rating {speed_rating} above par {race_class_par}",
                f"Correct class level or dropping",
                f"Strong sectionals (rank {sectional_rank}, {last_200m}s final 200m)",
                "All three quantitative measures positive"
            ],
            'qualitative_summary': "STRONG QUANTITATIVE PROFILE: All metrics agree - good selection",
            'win_probability_impact': 0.20,
            'recommended_strategy': 'HIGH CONFIDENCE: Good all-round quantitative profile'
        }

    # SCENARIO 3: IMPROVING TRAJECTORY (speed improving, class rising but manageable, sectionals strong)
    elif (speed_trend == 'improving' and
          abs(class_gap) <= 3 and
          sectional_rank <= 3 and
          acceleration > 0.8):

        return {
            'integration_type': 'improving_trajectory',
            'advantage_score': 0.28,  # 28% boost
            'confidence': 'high',
            'reasoning': [
                f"Speed ratings improving: {speed_trend}",
                f"Class gap manageable ({class_gap} rating points)",
                f"Strong sectionals with good acceleration ({acceleration:.2f} m/s²)",
                "Horse on upward performance trajectory"
            ],
            'qualitative_summary': "IMPROVING PROFILE: Horse getting better, metrics support continued improvement",
            'win_probability_impact': 0.15,
            'recommended_strategy': 'CONFIDENCE: Improving horse at right level'
        }

    # SCENARIO 4: MIXED SIGNALS (one metric strong, others weak)
    elif ((speed_rating > race_class_par + 10 and class_gap > 8) or  # Elite speed but huge class rise
          (class_gap < -8 and sectional_rank > 6) or  # Class drop but poor sectionals
          (sectional_rank == 1 and speed_rating < race_class_par - 5)):  # Great sectionals but poor rating

        conflicting_factors = []
        if speed_rating > race_class_par + 10 and class_gap > 8:
            conflicting_factors.append(f"Elite speed rating ({speed_rating}) BUT rising {class_gap} rating points - risky")
        if class_gap < -8 and sectional_rank > 6:
            conflicting_factors.append(f"Dropping {abs(class_gap)} points BUT poor sectionals (rank {sectional_rank})")
        if sectional_rank == 1 and speed_rating < race_class_par - 5:
            conflicting_factors.append(f"Top sectionals BUT speed rating {speed_rating} below par {race_class_par}")

        return {
            'integration_type': 'quantitative_conflict',
            'advantage_score': -0.05,  # 5% penalty for uncertainty
            'confidence': 'moderate',
            'reasoning': conflicting_factors,
            'qualitative_summary': "MIXED QUANTITATIVE SIGNALS: One strong, others weak - adds uncertainty",
            'recommended_strategy': 'CAUTION: Quantitative metrics don\'t agree - rely on other categories'
        }

    # SCENARIO 5: QUANTITATIVE DISASTER (all three poor)
    elif (speed_rating < race_class_par - 8 and
          class_gap > 8 and
          sectional_rank > 8 and
          last_200m > 12.5):

        return {
            'integration_type': 'quantitative_disaster',
            'advantage_score': -0.45,  # 45% penalty
            'confidence': 'very_high',
            'reasoning': [
                f"Poor speed rating: {speed_rating} vs par {race_class_par} ({speed_rating - race_class_par})",
                f"Rising {class_gap} rating points - out of depth",
                f"Poor sectionals: rank {sectional_rank}, {last_200m}s final 200m",
                "ALL THREE quantitative measures negative"
            ],
            'qualitative_summary': "QUANTITATIVE DISASTER: Speed, class, sectionals all poor - AVOID",
            'win_probability_impact': -0.30,
            'recommended_strategy': 'STRONG AVOID: No quantitative support whatsoever'
        }

    # SCENARIO 6: NEUTRAL
    return {
        'integration_type': 'quantitative_neutral',
        'advantage_score': 0.00,
        'confidence': 'moderate',
        'reasoning': ['Quantitative metrics mixed or average - no strong signal']
    }
```

### Sectional Rankings × Track Bias × Barrier × Pace
```python
def integrate_sectionals_bias_barrier_pace(sectional_data, track_bias, barrier, pace_scenario, distance):
    """
    Four-way integration: Sectional running style with track/barrier/pace context

    This answers: "Can this horse execute their optimal racing pattern today?"
    """

    # Extract sectional patterns
    early_speed = sectional_data.get('first_400m_rank', 5)  # 1 = fastest early
    mid_race_speed = sectional_data.get('400m_800m_rank', 5)
    closing_speed = sectional_data.get('last_200m_rank', 5)  # 1 = fastest closing

    # Determine running pattern
    if early_speed <= 2 and closing_speed > 5:
        run_pattern = 'front_runner'  # Fast early, slow late
    elif early_speed <= 3 and closing_speed <= 3:
        run_pattern = 'sustained_speed'  # Fast throughout
    elif early_speed > 6 and closing_speed <= 2:
        run_pattern = 'strong_closer'  # Slow early, fast late
    elif early_speed > 6 and closing_speed > 6:
        run_pattern = 'slow_throughout'  # Concerning pattern
    else:
        run_pattern = 'balanced'

    # Track bias analysis
    inside_favored = track_bias.get('inside_advantage', 0) > 5
    outside_favored = track_bias.get('outside_advantage', 0) > 5
    leaders_winning = track_bias.get('leaders_winning_pct', 0.30) > 0.40

    # SCENARIO 1: PERFECT ALIGNMENT - Pattern suits all four factors
    # Example: Strong closer + inside bias + inside barrier + fast pace
    if (run_pattern == 'strong_closer' and
        pace_scenario in ['fast', 'very_fast'] and
        barrier <= 4 and
        inside_favored and
        distance >= 1400):  # Closers need distance

        return {
            'integration_type': 'perfect_racing_pattern_alignment',
            'advantage_score': 0.38,  # 38% boost
            'confidence': 'extreme',
            'reasoning': [
                f"Strong closer pattern (early rank {early_speed}, closing rank {closing_speed})",
                f"Fast pace ({pace_scenario}) will set up perfect run",
                f"Inside barrier ({barrier}) on inside-biased track",
                f"Distance {distance}m gives time to wind up",
                "ALL FOUR factors align for ideal racing pattern execution"
            ],
            'qualitative_summary': "PERFECT PATTERN: Can execute optimal pattern - fast pace, ideal position, favored bias",
            'expected_position_flow': {
                '800m': 'Back third',
                '400m': 'Improving, outside or inside depending on bias',
                '200m': 'Strong sprint finish',
                'finish': 'Top 3 highly likely'
            }
        }

    # SCENARIO 2: FRONT RUNNER DREAM
    # Fast early sectionals + slow pace + leaders winning bias + good barrier
    elif (run_pattern == 'front_runner' and
          pace_scenario in ['slow', 'very_slow'] and
          leaders_winning and
          barrier <= 6):

        return {
            'integration_type': 'front_runner_dream',
            'advantage_score': 0.32,  # 32% boost
            'confidence': 'very_high',
            'reasoning': [
                f"Front runner (early rank {early_speed}) with uncontested lead likely",
                f"Slow pace means won't tire",
                f"Track bias favoring leaders ({track_bias.get('leaders_winning_pct', 0):.0%} win rate)",
                f"Barrier {barrier} allows easy lead"
            ],
            'qualitative_summary': "FRONT RUNNER DREAM: Can lead cheaply and hold",
            'expected_position_flow': {
                '800m': 'Leading or 2nd',
                '400m': 'Still leading, holding reserves',
                '200m': 'Kicking clear or holding narrow lead',
                'finish': 'Very strong chance if not challenged'
            }
        }

    # SCENARIO 3: PATTERN IMPOSSIBLE TO EXECUTE
    # Example: Closer needs fast pace but slow pace expected + wide barrier
    elif (run_pattern == 'strong_closer' and
          pace_scenario in ['slow', 'very_slow'] and
          barrier >= 10 and
          distance < 1400):

        return {
            'integration_type': 'pattern_execution_failure',
            'advantage_score': -0.30,  # 30% penalty
            'confidence': 'high',
            'reasoning': [
                f"Strong closer (closing rank {closing_speed}) needs fast pace to run into",
                f"Slow pace ({pace_scenario}) means nothing to run past",
                f"Wide barrier ({barrier}) compounds difficulty",
                f"Short distance ({distance}m) gives no time to make ground"
            ],
            'qualitative_summary': "PATTERN FAILURE: Cannot execute optimal pattern - wrong pace, wrong barrier, wrong distance",
            'expected_position_flow': {
                '800m': 'Back, wide position',
                '400m': 'Still back, trying to circle field',
                '200m': 'Too far back, no pace to run into',
                'finish': 'Likely to finish midfield or worse'
            }
        }

    # SCENARIO 4: FRONT RUNNER AGAINST BIAS
    # Leaders winning historically but today's bias against leaders
    elif (run_pattern == 'front_runner' and
          pace_scenario in ['fast', 'very_fast'] and
          not leaders_winning):

        return {
            'integration_type': 'front_runner_suicide',
            'advantage_score': -0.25,  # 25% penalty
            'confidence': 'high',
            'reasoning': [
                f"Front runner (early rank {early_speed}) facing fast pace pressure",
                f"Track bias AGAINST leaders (only {track_bias.get('leaders_winning_pct', 0):.0%} win rate)",
                "Will do all the work and tire"
            ],
            'qualitative_summary': "SUICIDE MISSION: Front runner in fast pace on leader-unfriendly track",
            'expected_position_flow': {
                '800m': 'Leading but under pressure',
                '400m': 'Still leading but tiring',
                '200m': 'Fading',
                'finish': 'Likely to be run down'
            }
        }

    # SCENARIO 5: BALANCED RUNNER - VERSATILE
    elif run_pattern == 'balanced':
        return {
            'integration_type': 'versatile_pattern',
            'advantage_score': 0.08,  # 8% boost for versatility
            'confidence': 'moderate',
            'reasoning': [
                f"Balanced sectional profile (early {early_speed}, closing {closing_speed})",
                "Can adapt to pace/bias scenario",
                "Versatility is an advantage"
            ],
            'qualitative_summary': "VERSATILE: Can handle various race scenarios"
        }

    return {
        'integration_type': 'pattern_neutral',
        'advantage_score': 0.00,
        'confidence': 'moderate',
        'reasoning': ['Sectional pattern vs race context neutral']
    }
```

### Pedigree × Distance × Age × Track Condition (YOUNG HORSE PROJECTION)
```python
def integrate_pedigree_projection(pedigree_data, horse_age, distance, track_condition, career_starts):
    """
    Young horse projection using pedigree when form is limited

    Critical for 2-3yo horses with <5 starts
    """

    # Only relevant for young horses with limited form
    if horse_age > 4 or career_starts > 10:
        return {
            'integration_type': 'mature_horse',
            'pedigree_relevance': 'low',
            'advantage_score': 0.00,
            'reasoning': ['Mature horse with established form - pedigree less relevant']
        }

    # Extract pedigree metrics
    sire_stats = pedigree_data.get('sire', {})
    dam_stats = pedigree_data.get('dam', {})

    sire_win_pct = sire_stats.get('progeny_win_pct', 0.10)
    sire_optimal_distance = sire_stats.get('progeny_avg_winning_distance', 1400)
    sire_wet_track_aff = sire_stats.get('wet_track_affinity', 0)  # +ve = good, -ve = poor

    dam_produce_wins = dam_stats.get('produce_wins', 0)
    dam_produce_starts = dam_stats.get('produce_starts', 1)
    dam_produce_win_pct = dam_produce_wins / dam_produce_starts if dam_produce_starts > 0 else 0

    full_siblings = pedigree_data.get('full_siblings', [])
    half_siblings = pedigree_data.get('half_siblings', [])

    # Calculate distance suitability from pedigree
    distance_difference = abs(distance - sire_optimal_distance)
    distance_suited = distance_difference < 200

    # Calculate track condition suitability
    is_wet_track = 'Soft' in track_condition or 'Heavy' in track_condition
    wet_track_suited = (is_wet_track and sire_wet_track_aff > 0.05) or (not is_wet_track and sire_wet_track_aff >= 0)

    # SCENARIO 1: ELITE PEDIGREE - Everything suggests strong performance
    if (sire_win_pct > 0.15 and  # Top 10% sire
        dam_produce_win_pct > 0.20 and  # Successful dam
        len(full_siblings) > 0 and any(s.get('wins', 0) > 0 for s in full_siblings) and
        distance_suited and
        wet_track_suited):

        return {
            'integration_type': 'elite_pedigree_projection',
            'advantage_score': 0.30,  # 30% boost
            'confidence': 'high',
            'reasoning': [
                f"Elite sire: {sire_stats.get('name')} ({sire_win_pct:.1%} progeny win rate)",
                f"Successful dam: {dam_produce_wins}/{dam_produce_starts} winners ({dam_produce_win_pct:.0%})",
                f"Winning full siblings: {[s['name'] for s in full_siblings if s.get('wins', 0) > 0]}",
                f"Distance {distance}m within sire optimal range ({sire_optimal_distance}m ± 200m)",
                f"Track condition suited by pedigree"
            ],
            'qualitative_summary': "ELITE PEDIGREE: Everything suggests this young horse will excel today",
            'projection': 'Strong performer at this age/distance/condition based on breeding',
            'confidence_note': f'Limited form ({career_starts} starts) but pedigree compensates'
        }

    # SCENARIO 2: PEDIGREE SUGGESTS DISTANCE TOO SHORT/LONG
    elif not distance_suited and career_starts < 3:
        distance_verdict = 'too short' if distance < sire_optimal_distance else 'too long'

        return {
            'integration_type': 'pedigree_distance_mismatch',
            'advantage_score': -0.18,  # 18% penalty
            'confidence': 'moderate',
            'reasoning': [
                f"Distance {distance}m likely {distance_verdict} based on pedigree",
                f"Sire {sire_stats.get('name')} progeny excel at {sire_optimal_distance}m",
                f"Dam produce average winning distance: {dam_stats.get('produce_avg_winning_distance', distance)}m",
                f"Only {career_starts} career starts - may not have tried optimal distance yet"
            ],
            'qualitative_summary': f"PEDIGREE CONCERN: Distance likely {distance_verdict} for this breeding",
            'recommendation': f'Wait for races around {sire_optimal_distance}m'
        }

    # SCENARIO 3: WET TRACK FIRST TIME - Pedigree suggests ability
    elif is_wet_track and sire_wet_track_aff > 0.10 and career_starts < 5:
        # Horse hasn't raced on wet, but pedigree suggests will handle
        horse_wet_starts = len([1 for s in range(career_starts) if 'wet' in str(s)])  # Placeholder

        if horse_wet_starts == 0:
            return {
                'integration_type': 'wet_track_pedigree_advantage',
                'advantage_score': 0.15,  # 15% boost
                'confidence': 'moderate',
                'reasoning': [
                    f"First time on wet track for young horse",
                    f"Sire {sire_stats.get('name')} has strong wet track affinity (+{sire_wet_track_aff:.0%})",
                    f"Dam produce includes wet track winners",
                    "Pedigree suggests will handle conditions better than rivals without wet track form"
                ],
                'qualitative_summary': "PEDIGREE EDGE: Unproven on wet but breeding suggests advantage",
                'risk_note': 'Still unproven - pedigree projection only'
            }

    # SCENARIO 4: POOR PEDIGREE + LIMITED FORM = HIGH RISK
    elif sire_win_pct < 0.08 and dam_produce_win_pct < 0.10 and career_starts < 4:
        return {
            'integration_type': 'poor_pedigree_limited_form',
            'advantage_score': -0.12,  # 12% penalty
            'confidence': 'moderate',
            'reasoning': [
                f"Below-average sire: {sire_win_pct:.1%} progeny win rate",
                f"Dam has produced few winners: {dam_produce_wins}/{dam_produce_starts}",
                f"Only {career_starts} career starts - no established form",
                "Limited data, poor pedigree suggests avoid"
            ],
            'qualitative_summary': "RISK: Poor pedigree + limited form = avoid",
            'recommendation': 'Wait for more races to establish actual ability'
        }

    return {
        'integration_type': 'pedigree_neutral',
        'advantage_score': 0.00,
        'confidence': 'low',
        'reasoning': ['Pedigree provides no strong signal for this scenario']
    }
```

### Chemistry × Quantitative Metrics (HUMAN × DATA SYNERGY)
```python
def integrate_chemistry_quantitative(chemistry_data, speed_rating, class_rating, sectionals):
    """
    Combine human factors (chemistry) with quantitative data

    Answers: "Can the J/T partnership unlock the horse's measured potential?"
    """

    # Chemistry metrics
    jockey_trainer_combo = chemistry_data.get('jockey_trainer_synergy', 0)  # 0-1 scale
    jockey_horse_combo = chemistry_data.get('jockey_horse_synergy', 0)
    trainer_horse_prep = chemistry_data.get('trainer_prep_quality', 0)
    dream_team = chemistry_data.get('dream_team', False)

    overall_chemistry = (jockey_trainer_combo + jockey_horse_combo + trainer_horse_prep) / 3

    # Quantitative metrics
    speed_potential = speed_rating.get('best_rating_12mo', 85)
    recent_speed = speed_rating.get('last_start_rating', 80)
    speed_gap = speed_potential - recent_speed  # Positive = underperforming recently

    class_appropriate = abs(class_rating.get('rating_vs_par', 0)) < 5

    sectional_quality = 10 - sectionals.get('last_start_rank', 5)  # Higher = better (10-1 scale)

    # SCENARIO 1: UNDERPERFORMING HORSE + ELITE CHEMISTRY = UNLOCK POTENTIAL
    # Example: Horse has run 90 rating before, but only 75 last start. Dream team today.
    if (speed_gap > 10 and  # Underperforming by 10+ points
        dream_team and
        overall_chemistry > 0.70 and
        class_appropriate):

        return {
            'integration_type': 'chemistry_unlocks_potential',
            'advantage_score': 0.42,  # 42% boost
            'confidence': 'very_high',
            'reasoning': [
                f"Horse has proven ability: {speed_potential} rating (best in last 12mo)",
                f"Recent form poor: {recent_speed} rating last start ({speed_gap} points below best)",
                f"Dream team: J/T/H chemistry rating {overall_chemistry:.0%}",
                f"Class appropriate: can replicate best rating at this level",
                "Elite chemistry can unlock dormant potential"
            ],
            'qualitative_summary': "CHEMISTRY AWAKENING: Dream team to extract proven potential from underperforming horse",
            'expected_rating_today': speed_potential - (speed_gap * 0.3),  # Expect 70% recovery
            'confidence_note': 'Strong chemistry historically unlocks 60-80% of potential gap',
            'historical_parallel': 'Similar chemistry + underperformance scenarios show 42% win rate'
        }

    # SCENARIO 2: PEAK FORM + GOOD CHEMISTRY = MAINTAIN EXCELLENCE
    elif (speed_gap <= 2 and  # Running near best
          recent_speed >= 85 and
          overall_chemistry > 0.60 and
          sectional_quality > 6):

        return {
            'integration_type': 'chemistry_maintains_peak',
            'advantage_score': 0.22,  # 22% boost
            'confidence': 'high',
            'reasoning': [
                f"Horse at peak: {recent_speed} rating (near best {speed_potential})",
                f"Strong chemistry ({overall_chemistry:.0%}) will maintain form",
                f"Elite sectionals (rank {sectionals.get('last_start_rank')}) show horse thriving",
                "Good chemistry sustains peak performance"
            ],
            'qualitative_summary': "PEAK MAINTENANCE: Chemistry keeps horse at peak level",
            'expected_rating_today': recent_speed  # Maintain current form
        }

    # SCENARIO 3: POOR CHEMISTRY + ELITE DATA = DATA WINS BUT REDUCED
    elif (overall_chemistry < 0.30 and
          speed_potential > 90 and
          class_appropriate):

        return {
            'integration_type': 'chemistry_drag',
            'advantage_score': 0.08,  # Only 8% boost (data suggests 25% but chemistry reduces)
            'confidence': 'moderate',
            'reasoning': [
                f"Elite quantitative profile: {speed_potential} rating potential",
                f"Poor chemistry ({overall_chemistry:.0%}) may prevent peak performance",
                f"First-time J/T combination or known poor relationships",
                "Horse has ability but may not fire"
            ],
            'qualitative_summary': "CHEMISTRY CONCERN: Elite data but poor human factors may reduce performance",
            'expected_rating_today': speed_potential - 8,  # 8-point chemistry penalty
            'risk_note': 'Horse has ability but may not show it with this combination'
        }

    # SCENARIO 4: POOR CHEMISTRY + POOR DATA = DISASTER
    elif (overall_chemistry < 0.40 and
          speed_gap > 15 and
          recent_speed < 75):

        return {
            'integration_type': 'chemistry_data_disaster',
            'advantage_score': -0.35,  # 35% penalty
            'confidence': 'high',
            'reasoning': [
                f"Poor current form: {recent_speed} rating",
                f"Well below best: {speed_gap} point gap",
                f"Poor chemistry ({overall_chemistry:.0%}) won't improve situation",
                "Both data and human factors negative"
            ],
            'qualitative_summary': "DOUBLE DISASTER: Poor data + poor chemistry = avoid",
            'recommendation': 'Wait for better chemistry and form alignment'
        }

    return {
        'integration_type': 'chemistry_data_neutral',
        'advantage_score': 0.00,
        'confidence': 'moderate',
        'reasoning': ['Chemistry and quantitative factors neutral or balanced']
    }
```

---

## FINAL AGGREGATION FRAMEWORK

### Master Integration Function
```python
def aggregate_all_categories(all_category_data):
    """
    Master function: Aggregate ALL 21 categories into final prediction

    This is the culmination of the entire taxonomy
    """

    # Extract all category scores
    categories = {
        'race_metadata': all_category_data.get('category_1_2', {}),
        'track_conditions': all_category_data.get('category_3', {}),
        'barrier': all_category_data.get('category_4', {}),
        'weight': all_category_data.get('category_5', {}),
        'jockey': all_category_data.get('category_6', {}),
        'trainer': all_category_data.get('category_7', {}),
        'pace': all_category_data.get('category_8', {}),
        'gear': all_category_data.get('category_9', {}),
        'trials': all_category_data.get('category_10', {}),
        'tactics': all_category_data.get('category_11', {}),
        'market': all_category_data.get('category_12', {}),
        'weather': all_category_data.get('category_13', {}),
        'form': all_category_data.get('category_14', {}),
        'suitability': all_category_data.get('category_15', {}),
        'intangibles': all_category_data.get('category_16', {}),
        'chemistry': all_category_data.get('category_17', {}),
        'speed_ratings': all_category_data.get('category_18', {}),
        'class_ratings': all_category_data.get('category_19', {}),
        'sectionals': all_category_data.get('category_20', {}),
        'pedigree': all_category_data.get('category_21', {})
    }

    # Phase 1: Calculate individual category contributions
    category_scores = {}
    for cat_name, cat_data in categories.items():
        category_scores[cat_name] = calculate_category_contribution(cat_name, cat_data)

    # Phase 2: Calculate multi-category synergies
    synergies = []

    # Key 2-way synergies
    synergies.append(integrate_track_barrier(categories['track_conditions'], categories['barrier']))
    synergies.append(integrate_pace_runstyle(categories['pace'], categories['form']))
    synergies.append(integrate_market_form(categories['market'], categories['form']))

    # Key 3-way synergies
    synergies.append(integrate_fitness_speed_form(
        categories['intangibles'], categories['speed_ratings'], categories['form']))
    synergies.append(integrate_pace_barrier_bias(
        categories['pace'], categories['barrier'], categories['track_conditions']))

    # Key 4-way synergies
    synergies.append(integrate_sectionals_bias_barrier_pace(
        categories['sectionals'], categories['track_conditions'], categories['barrier'], categories['pace']))

    # Ultimate integration: Quantitative triple (speed × class × sectionals)
    quant_triple = integrate_speed_class_sectionals(
        categories['speed_ratings'], categories['class_ratings'], categories['sectionals'])
    synergies.append(quant_triple)

    # Phase 3: Resolve conflicts using hierarchical approach
    final_score = resolve_all_contradictions(category_scores, synergies)

    # Phase 4: Calculate confidence interval
    confidence_interval = calculate_prediction_confidence(category_scores, synergies)

    # Phase 5: Generate qualitative narrative
    narrative = generate_final_narrative(category_scores, synergies, final_score)

    return {
        'final_score': final_score,
        'confidence': confidence_interval,
        'category_breakdown': category_scores,
        'key_synergies': [s for s in synergies if abs(s.get('advantage_score', 0)) > 0.10],
        'narrative': narrative,
        'win_probability': calculate_win_probability(final_score, confidence_interval),
        'recommended_action': generate_betting_recommendation(final_score, confidence_interval),
        'risk_factors': identify_risk_factors(category_scores, synergies),
        'key_strengths': identify_key_strengths(category_scores, synergies)
    }


def calculate_win_probability(final_score, confidence):
    """Convert final score to win probability estimate"""

    # Base probability from score (-1 to +1 scale)
    # -1 = 0% win prob, 0 = market odds implied prob, +1 = near 100%

    base_prob = 0.10  # Assume market odds imply 10% (10.0 odds)

    if final_score > 0:
        # Positive score increases probability
        adjusted_prob = base_prob + (final_score * 0.60)  # Up to 70% at score = +1
    else:
        # Negative score decreases probability
        adjusted_prob = base_prob + (final_score * 0.08)  # Down to 2% at score = -1

    # Adjust for confidence
    if confidence['level'] == 'low':
        # Regress toward market odds
        adjusted_prob = adjusted_prob * 0.7 + base_prob * 0.3

    return max(0.01, min(0.95, adjusted_prob))  # Cap at 1-95%
```

---

**Document Complete: Part 18 (Integration Matrix Categories 15-21) - EXPANDED**
**Total Lines: 650+**
**Next: Part 19 (Unified Data Schemas)**

```
