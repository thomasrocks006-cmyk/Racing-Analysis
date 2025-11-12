# Qualitative Pipeline Architecture - Part 4: Integration Matrices A, B, C
**Created:** November 9, 2025
**Status:** Production-Ready Design
**Purpose:** Cross-category synergy detection and LR adjustments

**Related Documents:**
- Part 1: Overview & Categories 1-8
- Part 2: Categories 9-17
- Part 3: LLM Chain & Synthesis
- Part 5: Deployment & Integration
- Master Taxonomy (PART_18: Integration Matrices)

---

## 📋 Table of Contents

1. [Integration Matrix Overview](#overview)
2. [Matrix A: Race Context × Horse Setup](#matrix-a)
3. [Matrix B: Tactical Intelligence Synergies](#matrix-b)
4. [Matrix C: Qualitative → Quantitative Bridges](#matrix-c)

---

## 🔗 1. Integration Matrix Overview {#overview}

### **Why Integration Matrices?**

```
Problem: Individual category analysis misses SYNERGIES

Example:
- Barrier 14 alone = -10% (negative)
- BUT: Barrier 14 + Early speed + True rail + Leaders bias = +5% (positive!)

Integration Matrices capture these non-linear interactions.
```

### **Matrix Structure**

| Matrix | Categories | Purpose | Impact |
|--------|-----------|---------|--------|
| **A** | 1-7 | Race context × Horse setup | Baseline suitability |
| **B** | 8-14 | Tactical intelligence synergies | Dynamic edge detection |
| **C** | 15-17 → 18-21 | Qualitative → Quantitative bridge | Fusion model interface |

### **Implementation Philosophy**

```python
# BAD: Additive adjustments (ignores interactions)
lr_total = lr_barrier + lr_pace + lr_gear  # ❌

# GOOD: Multiplicative with synergy detection
lr_base = lr_barrier * lr_pace * lr_gear
lr_synergy = detect_synergy(barrier, pace, gear)  # +0.08
lr_total = lr_base * (1 + lr_synergy)  # ✅
```

---

## 🎯 2. Matrix A: Race Context × Horse Setup (Categories 1-7) {#matrix-a}

### **Purpose**: Detect fundamental suitability patterns

**Key Synergies**:
1. **Track Conditions × Barrier**: Bias interactions
2. **Weight × Class**: Competitive positioning
3. **Jockey × Trainer**: Partnership excellence
4. **Distance × Track**: Venue-specific patterns
5. **Going × Barrier**: Inside/outside rail preference
6. **Class × Weight**: Handicap advantage detection

### **Synergy 1: Track Bias × Barrier × Early Speed**

```python
def matrix_a_bias_barrier_speed(
    race: dict,
    horse: dict
) -> dict:
    """
    Track bias + barrier + early speed synergy.

    Examples:
    - Leaders' bias + Low barrier + Early speed = STRONG POSITIVE
    - Closers' bias + Wide barrier + Closing style = STRONG POSITIVE
    - Inside bias + Low barrier + NO early speed = NEGATIVE (trapped)

    Returns:
        {
            'adjustment': -0.15 to +0.20,
            'reasoning': "string"
        }
    """
    bias_type = race['track_bias']['bias_type']
    barrier = horse['barrier']
    early_speed_rank = horse.get('early_speed_rank', 99)
    run_style = horse.get('run_style', 'Unknown')

    adjustment = 0.0
    reasoning_parts = []

    # Leaders' bias scenarios
    if bias_type == 'Leaders':
        if barrier <= 6 and early_speed_rank <= 3:
            adjustment = +0.18  # IDEAL: Low barrier + natural leader + leaders' track
            reasoning_parts.append("Leaders' bias + low barrier + early speed (ideal)")
        elif barrier >= 12 and run_style == 'Closer':
            adjustment = -0.12  # POOR: Wide barrier + closer + leaders' track
            reasoning_parts.append("Leaders' bias + wide barrier + closing style (poor)")
        elif barrier <= 6 and early_speed_rank > 5:
            adjustment = -0.08  # TRAPPED: Low barrier but no speed
            reasoning_parts.append("Leaders' bias + low barrier but no speed (risk trapped)")

    # Closers' bias scenarios
    elif bias_type == 'Closers':
        if barrier >= 10 and run_style == 'Closer':
            adjustment = +0.16  # IDEAL: Wide barrier + closer + closers' track
            reasoning_parts.append("Closers' bias + wide barrier + closing style (ideal)")
        elif barrier <= 4 and early_speed_rank <= 2:
            adjustment = -0.10  # POOR: Low barrier + leader + closers' track
            reasoning_parts.append("Closers' bias + low barrier + leader (disadvantaged)")

    # Inside bias scenarios
    elif bias_type == 'Inside':
        if barrier <= 4:
            adjustment = +0.15  # Inside bias + inside barrier
            reasoning_parts.append("Inside bias + low barrier (strong advantage)")
        elif barrier >= 12:
            adjustment = -0.15  # Inside bias + wide barrier
            reasoning_parts.append("Inside bias + wide barrier (strong disadvantage)")

    # Outside bias scenarios (rare)
    elif bias_type == 'Outside':
        if barrier >= 10:
            adjustment = +0.12
            reasoning_parts.append("Outside bias + wide barrier (advantage)")
        elif barrier <= 4:
            adjustment = -0.10
            reasoning_parts.append("Outside bias + inside barrier (disadvantage)")

    reasoning = " | ".join(reasoning_parts) if reasoning_parts else "No bias synergy"

    return {
        'adjustment': adjustment,
        'reasoning': reasoning,
        'confidence': race['track_bias'].get('confidence', 0.50)
    }
```

### **Synergy 2: Class × Weight × Distance**

```python
def matrix_a_class_weight_distance(
    race: dict,
    horse: dict
) -> dict:
    """
    Class level + weight allocation + distance synergy.

    Logic:
    - Class DROP + Weight RELIEF + Distance SUITED = STRONG POSITIVE
    - Class RISE + Weight PENALTY + Distance UNSUITED = STRONG NEGATIVE

    Returns:
        {
            'adjustment': -0.12 to +0.15,
            'reasoning': "string"
        }
    """
    race_class = race['class_band']
    horse_peak_class = horse.get('peak_class_achieved', 85)
    weight_shift = horse.get('weight_shift_vs_last', 0)
    distance = race['distance']
    optimal_distance = horse.get('optimal_distance', distance)

    # Class assessment
    class_drop = horse_peak_class - race_class
    if class_drop > 10:
        class_factor = +0.08  # Significant class drop
    elif class_drop > 5:
        class_factor = +0.04  # Moderate class drop
    elif class_drop < -5:
        class_factor = -0.06  # Class rise
    else:
        class_factor = 0.0  # Neutral

    # Weight assessment
    if weight_shift < -2.5:
        weight_factor = +0.05  # Significant weight relief
    elif weight_shift < -1.5:
        weight_factor = +0.02  # Moderate relief
    elif weight_shift > 3.0:
        weight_factor = -0.04  # Significant penalty
    else:
        weight_factor = 0.0

    # Distance assessment
    distance_diff = abs(distance - optimal_distance)
    if distance_diff <= 200:
        distance_factor = +0.03  # Optimal distance
    elif distance_diff > 400:
        distance_factor = -0.04  # Unsuited distance
    else:
        distance_factor = 0.0

    # Synergy: Triple alignment
    if class_factor > 0 and weight_factor > 0 and distance_factor > 0:
        # All three positive = SUPERCHARGE
        adjustment = class_factor + weight_factor + distance_factor + 0.05
        reasoning = f"Class drop ({class_drop:+.0f}) + weight relief ({weight_shift:+.1f}kg) + optimal distance (STRONG)"
    elif class_factor < 0 and weight_factor < 0 and distance_factor < 0:
        # All three negative = COMPOUNDING NEGATIVES
        adjustment = class_factor + weight_factor + distance_factor - 0.04
        reasoning = f"Class rise ({class_drop:+.0f}) + weight penalty ({weight_shift:+.1f}kg) + unsuited distance (POOR)"
    else:
        # Mixed signals
        adjustment = class_factor + weight_factor + distance_factor
        reasoning = f"Mixed signals: class {class_drop:+.0f}, weight {weight_shift:+.1f}kg, distance {'suited' if distance_factor >= 0 else 'concern'}"

    # Clip to range
    adjustment = np.clip(adjustment, -0.12, 0.15)

    return {
        'adjustment': adjustment,
        'reasoning': reasoning,
        'confidence': 0.75
    }
```

### **Synergy 3: Jockey × Trainer × Track**

```python
def matrix_a_jockey_trainer_track(
    race: dict,
    jockey: dict,
    trainer: dict
) -> dict:
    """
    Jockey/Trainer partnership + track specialization synergy.

    Logic:
    - Elite J/T partnership (>25% SR) + Both excel at this track = MEGA BOOST
    - Poor J/T (< 12% SR) + Track unfamiliarity = COMPOUNDING NEGATIVE

    Returns:
        {
            'adjustment': -0.10 to +0.20,
            'reasoning': "string"
        }
    """
    track = race['track']

    jt_sr = jockey.get('jockey_trainer_sr', 0)
    jt_roi = jockey.get('jockey_trainer_roi', 1.0)
    jockey_track_sr = jockey.get(f'track_sr_{track}', jockey.get('overall_sr', 0.15))
    trainer_track_sr = trainer.get(f'track_sr_{track}', trainer.get('overall_sr', 0.15))

    # J/T partnership strength
    if jt_sr > 0.25 and jt_roi > 1.20:
        jt_factor = +0.12  # Elite partnership
    elif jt_sr > 0.20:
        jt_factor = +0.06  # Strong partnership
    elif jt_sr < 0.12 and jockey.get('jockey_trainer_rides', 0) > 10:
        jt_factor = -0.06  # Poor partnership with history
    else:
        jt_factor = 0.0

    # Track specialization (both)
    track_synergy = 0.0
    if jockey_track_sr > 0.22 and trainer_track_sr > 0.20:
        track_synergy = +0.08  # Both excel at this track
    elif jockey_track_sr < 0.12 and trainer_track_sr < 0.12:
        track_synergy = -0.05  # Both struggle at this track

    # Combined adjustment
    adjustment = jt_factor + track_synergy

    # Mega-boost for elite combo at specialized track
    if jt_factor > 0.10 and track_synergy > 0.05:
        adjustment += 0.05  # Bonus for double excellence
        reasoning = f"Elite J/T ({jt_sr:.1%}) + Both excel at {track} (MEGA BOOST)"
    elif jt_factor < 0 and track_synergy < 0:
        adjustment -= 0.03  # Compounding negative
        reasoning = f"Poor J/T ({jt_sr:.1%}) + Track unfamiliarity (COMPOUNDING)"
    else:
        reasoning = f"J/T {jt_sr:.1%}, Track: J {jockey_track_sr:.1%} T {trainer_track_sr:.1%}"

    adjustment = np.clip(adjustment, -0.10, 0.20)

    return {
        'adjustment': adjustment,
        'reasoning': reasoning,
        'confidence': 0.80
    }
```

---

## ⚡ 3. Matrix B: Tactical Intelligence Synergies (Categories 8-14) {#matrix-b}

### **Purpose**: Detect pre-race edge and tactical advantages

**Key Synergies**:
1. **Gear × Trials**: Equipment + fitness confirmation
2. **Pace × Sectionals**: Run-style validation
3. **Market × Trials**: Informed money confirmation
4. **Fitness × Gear**: Peak fitness + new equipment
5. **Tactics × Pace**: Tactical positioning advantage

### **Synergy 1: Gear Changes × Barrier Trials**

```python
def matrix_b_gear_trials(
    horse: dict
) -> dict:
    """
    Gear changes + barrier trial performance synergy.

    Logic:
    - First-time blinkers + Easy trial win = STRONG POSITIVE
    - Gear removed + Poor trial = STRONG NEGATIVE
    - Gear added + Sharp trial = NEUTRAL (may have peaked)

    Returns:
        {
            'adjustment': -0.10 to +0.15,
            'reasoning': "string"
        }
    """
    blinkers = horse.get('blinkers', None)
    trial_effort = horse.get('trial_effort', None)
    trial_result = horse.get('trial_margin', '')
    days_since_trial = horse.get('days_since_trial', 999)

    if not trial_effort or days_since_trial > 21:
        return {
            'adjustment': 0.0,
            'reasoning': "No recent trial data for gear synergy",
            'confidence': 0.30
        }

    adjustment = 0.0
    reasoning = ""

    # First-time blinkers scenarios
    if blinkers == 'First Time':
        if trial_effort == 'Easy' and 'won' in trial_result.lower():
            adjustment = +0.12  # IDEAL: Blinkers + easy win
            reasoning = "First-time blinkers + easy trial win (strong synergy)"
        elif trial_effort == 'Easy':
            adjustment = +0.08  # Good: Blinkers + easy effort
            reasoning = "First-time blinkers + easy trial (positive)"
        elif trial_effort == 'Sharp':
            adjustment = +0.03  # Caution: May have peaked
            reasoning = "First-time blinkers + sharp trial (may have peaked early)"
        else:
            adjustment = +0.05  # Standard blinkers boost
            reasoning = "First-time blinkers (standard positive)"

    # Blinkers removed scenarios
    elif blinkers == 'Removed':
        if trial_effort == 'Sharp' and 'beaten' in trial_result.lower():
            adjustment = -0.10  # Concern: Removed + poor trial
            reasoning = "Blinkers removed + struggled in trial (concern)"
        else:
            adjustment = -0.03  # Standard blinkers removal
            reasoning = "Blinkers removed"

    # Other gear changes
    elif any(horse.get(gear) == 'First Time' for gear in ['tongue_tie', 'nose_roll']):
        if trial_effort == 'Easy':
            adjustment = +0.05
            reasoning = "Gear change + easy trial"

    return {
        'adjustment': adjustment,
        'reasoning': reasoning,
        'confidence': 0.75
    }
```

### **Synergy 2: Pace Scenario × Last Start Sectionals**

```python
def matrix_b_pace_sectionals(
    race: dict,
    horse: dict
) -> dict:
    """
    Pace scenario + last start sectional pattern synergy.

    Logic:
    - Fast pace + Fast L200m last start = STRONG POSITIVE (closer validated)
    - Slow pace + Slow L200m last start = NEGATIVE (no speed to run into)
    - Moderate pace = Neutral

    Returns:
        {
            'adjustment': -0.10 to +0.12,
            'reasoning': "string"
        }
    """
    pace_pressure = race.get('pace_pressure', 'Moderate')
    last_l200 = horse.get('last_sectionals', {}).get('200-0', None)
    run_style = horse.get('run_style', 'Unknown')

    if not last_l200:
        return {
            'adjustment': 0.0,
            'reasoning': "No sectional data for pace synergy",
            'confidence': 0.30
        }

    adjustment = 0.0
    reasoning = ""

    # Fast pace scenarios
    if pace_pressure == 'Fast':
        if last_l200 < 11.4 and run_style == 'Closer':
            adjustment = +0.12  # IDEAL: Closer + fast L200m + fast pace
            reasoning = "Closer with fast L200m in fast pace (ideal setup)"
        elif last_l200 < 11.4 and run_style == 'Midfield':
            adjustment = +0.08  # Good: Midfield with closing ability
            reasoning = "Midfield with closing ability in fast pace"
        elif last_l200 > 12.0 and run_style == 'Leader':
            adjustment = -0.08  # Concern: Leader labored last time in fast pace
            reasoning = "Leader labored last time, facing fast pace (concern)"

    # Slow pace scenarios
    elif pace_pressure == 'Slow':
        if last_l200 > 12.0 and run_style == 'Closer':
            adjustment = -0.10  # POOR: Closer needs pace to run into
            reasoning = "Closer without closing speed in slow pace (poor)"
        elif last_l200 < 11.5 and run_style == 'Leader':
            adjustment = +0.08  # Good: Leader with stamina
            reasoning = "Leader with sustained speed in slow pace"

    # Moderate pace
    else:
        adjustment = 0.0
        reasoning = "Moderate pace (neutral sectional synergy)"

    return {
        'adjustment': adjustment,
        'reasoning': reasoning,
        'confidence': 0.70
    }
```

### **Synergy 3: Market × Trials × Gear** (Insider Knowledge)

```python
def matrix_b_market_trials_gear(
    horse: dict
) -> dict:
    """
    Market support + trial performance + gear changes synergy.

    Logic:
    - Strong market support ($8→$5) + Easy trial + Gear change = INSIDERS KNOW
    - Market drift + Sharp trial + No gear = CONCERNS

    This synergy detects "informed money" patterns.

    Returns:
        {
            'adjustment': -0.08 to +0.15,
            'reasoning': "string"
        }
    """
    opening_odds = horse.get('opening_odds', 0)
    current_odds = horse.get('current_odds', 0)
    trial_effort = horse.get('trial_effort', None)
    trial_days = horse.get('days_since_trial', 999)
    has_gear_change = horse.get('blinkers') == 'First Time' or any(
        horse.get(g) == 'First Time' for g in ['tongue_tie', 'nose_roll']
    )

    if opening_odds == 0 or current_odds == 0:
        return {
            'adjustment': 0.0,
            'reasoning': "No market data",
            'confidence': 0.20
        }

    # Market move
    move_pct = (opening_odds - current_odds) / opening_odds * 100

    adjustment = 0.0
    reasoning_parts = []

    # Strong firming (>15%)
    if move_pct > 15:
        if trial_effort == 'Easy' and trial_days <= 14:
            adjustment = +0.10  # Firming + good trial
            reasoning_parts.append("Strong firming + easy trial")

            if has_gear_change:
                adjustment += 0.05  # TRIPLE: Market + trial + gear
                reasoning_parts.append("+ gear change (insiders confident)")
        else:
            adjustment = +0.06  # Firming alone
            reasoning_parts.append("Strong market support")

    # Strong drifting (>15%)
    elif move_pct < -15:
        if trial_effort == 'Sharp' or trial_days > 21:
            adjustment = -0.08  # Drifting + poor trial
            reasoning_parts.append("Drifting + trial concerns")
        else:
            adjustment = -0.04  # Drifting alone
            reasoning_parts.append("Market drifting")

    # Stable market
    else:
        adjustment = 0.0
        reasoning_parts.append("Stable market")

    reasoning = " | ".join(reasoning_parts)

    return {
        'adjustment': adjustment,
        'reasoning': reasoning,
        'confidence': 0.65
    }
```

---

## 🌉 4. Matrix C: Qualitative → Quantitative Bridges (Categories 15-17) {#matrix-c}

### **Purpose**: Bridge qualitative intelligence to quantitative base probabilities

**Key Bridges**:
1. **Chemistry (Cat 17) × Speed/Class (Cats 18-19)**: Confidence multiplier
2. **Distance Suitability (Cat 15) × Pedigree (Cat 21)**: First-time distance validation
3. **Weather (Cat 13) × Pedigree Going Suit (Cat 21)**: Going preference confirmation
4. **Last Start (Cat 16) × Sectionals (Cat 20)**: Form trajectory validation

### **Bridge 1: Chemistry × Quantitative Base Probability**

```python
def matrix_c_chemistry_quantitative(
    qualitative: dict,
    quantitative: dict
) -> dict:
    """
    Qualitative chemistry LR × Quantitative base probability.

    This is THE critical fusion interface.

    Logic:
    - Elite J/T chemistry (>25% SR) + Strong quant (>20% base) = MULTIPLY CONFIDENCE
    - Poor chemistry (<12% SR) + Weak quant (<10% base) = COMPOUNDING NEGATIVE
    - Chemistry validates or questions quantitative assessment

    Args:
        qualitative: {'lr_chemistry': 1.18, 'jt_sr': 0.28, ...}
        quantitative: {'win_prob_base': 0.185, 'speed_rating': 105, ...}

    Returns:
        {
            'multiplier': 0.90-1.15,
            'reasoning': "string",
            'final_probability': float
        }
    """
    lr_chemistry = qualitative.get('lr_chemistry', 1.0)
    jt_sr = qualitative.get('jockey_trainer_sr', 0)
    base_prob = quantitative.get('win_prob_base', 0)
    quant_score = quantitative.get('quant_triple_score', 50) / 100  # Normalize to 0-1

    # Chemistry strength
    chemistry_strong = jt_sr > 0.22
    chemistry_weak = jt_sr < 0.14

    # Quantitative strength
    quant_strong = quant_score > 0.70
    quant_weak = quant_score < 0.50

    # Synergy logic
    if chemistry_strong and quant_strong:
        # BOTH strong = confidence multiplier
        multiplier = 1.12
        reasoning = f"Elite chemistry ({jt_sr:.1%}) validates strong quant ({quant_score:.2f})"

    elif chemistry_strong and quant_weak:
        # Chemistry strong but quant weak = MODERATE boost (chemistry can't fix fundamentals)
        multiplier = 1.05
        reasoning = f"Elite chemistry ({jt_sr:.1%}) with weak quant ({quant_score:.2f}) - limited upside"

    elif chemistry_weak and quant_strong:
        # Quant strong but chemistry weak = SLIGHT concern
        multiplier = 0.97
        reasoning = f"Weak chemistry ({jt_sr:.1%}) questions strong quant ({quant_score:.2f})"

    elif chemistry_weak and quant_weak:
        # BOTH weak = compounding negative
        multiplier = 0.92
        reasoning = f"Weak chemistry ({jt_sr:.1%}) + weak quant ({quant_score:.2f}) - avoid"

    else:
        # Neutral
        multiplier = 1.0
        reasoning = "Neutral chemistry/quant synergy"

    # Apply multiplier to base probability
    final_probability = base_prob * multiplier * lr_chemistry

    return {
        'multiplier': multiplier,
        'reasoning': reasoning,
        'final_probability': final_probability,
        'confidence': 0.80
    }
```

### **Bridge 2: Distance × Pedigree Validation**

```python
def matrix_c_distance_pedigree(
    qualitative: dict,
    quantitative: dict
) -> dict:
    """
    Distance suitability (qual) × Pedigree analysis (quant).

    Logic:
    - First time at distance → Rely heavily on pedigree (quant Cat 21)
    - Proven at distance → Pedigree is secondary validation

    Returns:
        {
            'adjustment': -0.08 to +0.10,
            'reasoning': "string"
        }
    """
    distance = qualitative.get('distance', 1600)
    optimal_distance = qualitative.get('optimal_distance', distance)
    distance_record_exists = qualitative.get('distance_record_exists', False)
    pedigree_distance_suit = quantitative.get('pedigree_distance_suit', 0.5)

    adjustment = 0.0

    if not distance_record_exists:
        # First time at distance - pedigree critical
        if pedigree_distance_suit > 0.75:
            adjustment = +0.10  # Strong pedigree validation
            reasoning = f"First time {distance}m, strong pedigree suit ({pedigree_distance_suit:.2f})"
        elif pedigree_distance_suit < 0.40:
            adjustment = -0.08  # Poor pedigree indication
            reasoning = f"First time {distance}m, poor pedigree suit ({pedigree_distance_suit:.2f})"
        else:
            adjustment = 0.0
            reasoning = f"First time {distance}m, moderate pedigree ({pedigree_distance_suit:.2f})"

    else:
        # Has raced at distance - pedigree is validation
        distance_diff = abs(distance - optimal_distance)
        if distance_diff <= 200:
            adjustment = +0.03  # Within optimal range
            reasoning = f"Proven at {distance}m (optimal)"
        else:
            adjustment = 0.0
            reasoning = f"Has form at {distance}m"

    return {
        'adjustment': adjustment,
        'reasoning': reasoning,
        'confidence': 0.70
    }
```

### **Bridge 3: Weather × Going Suit (Pedigree)**

```python
def matrix_c_weather_pedigree_going(
    qualitative: dict,
    quantitative: dict
) -> dict:
    """
    Weather sensitivity (qual Cat 13) × Pedigree going suit (quant Cat 21).

    Logic:
    - Limited wet form + Strong wet pedigree = Trust pedigree
    - Poor wet form + Poor wet pedigree = STRONG NEGATIVE
    - Proven wet form + Wet pedigree = Confirmation

    Returns:
        {
            'adjustment': -0.12 to +0.08,
            'reasoning': "string"
        }
    """
    going = qualitative.get('going', 4)
    wet_track_starts = qualitative.get('wet_track_starts', 0)
    wet_track_wr = qualitative.get('wet_track_win_rate', 0)
    pedigree_going_suit = quantitative.get('pedigree_going_suit', 0.5)

    if going < 7:
        # Good/Firm track - no synergy needed
        return {
            'adjustment': 0.0,
            'reasoning': "Good track (no going synergy required)",
            'confidence': 0.50
        }

    adjustment = 0.0

    # Wet track scenarios
    if wet_track_starts >= 3:
        # Sufficient wet history
        if wet_track_wr > 0.25:
            # Proven wet tracker
            if pedigree_going_suit > 0.70:
                adjustment = +0.08  # History + pedigree confirmation
                reasoning = f"Proven wet tracker ({wet_track_wr:.1%}) + pedigree ({pedigree_going_suit:.2f})"
            else:
                adjustment = +0.05  # History alone
                reasoning = f"Proven wet tracker ({wet_track_wr:.1%})"
        elif wet_track_wr < 0.12:
            # Poor wet form
            if pedigree_going_suit < 0.40:
                adjustment = -0.12  # History + pedigree BOTH negative
                reasoning = f"Poor wet form ({wet_track_wr:.1%}) + poor pedigree ({pedigree_going_suit:.2f}) - AVOID"
            else:
                adjustment = -0.06  # History negative, pedigree offers hope
                reasoning = f"Poor wet form ({wet_track_wr:.1%}) but decent pedigree ({pedigree_going_suit:.2f})"

    else:
        # Limited wet history - rely on pedigree
        if pedigree_going_suit > 0.75:
            adjustment = +0.06  # Strong pedigree, no history
            reasoning = f"Limited wet form ({wet_track_starts} starts), strong pedigree ({pedigree_going_suit:.2f})"
        elif pedigree_going_suit < 0.40:
            adjustment = -0.08  # Poor pedigree, no history
            reasoning = f"Limited wet form ({wet_track_starts} starts), poor pedigree ({pedigree_going_suit:.2f})"
        else:
            adjustment = 0.0
            reasoning = f"Limited wet form, moderate pedigree ({pedigree_going_suit:.2f})"

    return {
        'adjustment': adjustment,
        'reasoning': reasoning,
        'confidence': 0.75
    }
```

---

## 🎯 Integration Matrix Master Function

```python
def apply_all_integration_matrices(
    qualitative_analysis: dict,
    quantitative_analysis: dict,
    race: dict,
    horse: dict
) -> dict:
    """
    Apply all integration matrices (A, B, C) and return final adjustments.

    Returns:
        {
            'matrix_a_adjustments': {...},
            'matrix_b_adjustments': {...},
            'matrix_c_adjustments': {...},
            'total_adjustment': float,
            'adjusted_lr_product': float,
            'reasoning': "string"
        }
    """
    # Matrix A: Race context × Horse setup
    matrix_a = {
        'bias_barrier_speed': matrix_a_bias_barrier_speed(race, horse),
        'class_weight_distance': matrix_a_class_weight_distance(race, horse),
        'jockey_trainer_track': matrix_a_jockey_trainer_track(
            race,
            qualitative_analysis['jockey'],
            qualitative_analysis['trainer']
        )
    }

    # Matrix B: Tactical intelligence
    matrix_b = {
        'gear_trials': matrix_b_gear_trials(horse),
        'pace_sectionals': matrix_b_pace_sectionals(race, horse),
        'market_trials_gear': matrix_b_market_trials_gear(horse)
    }

    # Matrix C: Qual → Quant bridges
    matrix_c = {
        'chemistry_quantitative': matrix_c_chemistry_quantitative(
            qualitative_analysis,
            quantitative_analysis
        ),
        'distance_pedigree': matrix_c_distance_pedigree(
            qualitative_analysis,
            quantitative_analysis
        ),
        'weather_pedigree': matrix_c_weather_pedigree_going(
            qualitative_analysis,
            quantitative_analysis
        )
    }

    # Sum adjustments
    total_adjustment = (
        sum(m['adjustment'] for m in matrix_a.values()) +
        sum(m['adjustment'] for m in matrix_b.values()) +
        sum(m['adjustment'] for m in matrix_c.values())
    )

    # Apply to LR product
    base_lr_product = qualitative_analysis.get('lr_product', 1.0)
    adjusted_lr_product = base_lr_product * (1 + total_adjustment)

    # Clip to valid range
    adjusted_lr_product = np.clip(adjusted_lr_product, 0.30, 3.50)

    return {
        'matrix_a_adjustments': matrix_a,
        'matrix_b_adjustments': matrix_b,
        'matrix_c_adjustments': matrix_c,
        'total_adjustment': total_adjustment,
        'base_lr_product': base_lr_product,
        'adjusted_lr_product': adjusted_lr_product,
        'reasoning': f"Integration matrices applied: {total_adjustment:+.2f} adjustment"
    }
```

---

**Continue to Part 5: Deployment & Integration →**
