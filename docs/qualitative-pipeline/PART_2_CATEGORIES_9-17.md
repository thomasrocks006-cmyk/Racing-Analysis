# Qualitative Pipeline Architecture - Part 2: Categories 9-17
**Created:** November 9, 2025
**Status:** Production-Ready Design
**Purpose:** Pre-Race Intelligence & Form Analysis (Categories 9-17)

**Related Documents:**
- Part 1: Overview & Categories 1-8
- Part 3: LLM Chain & Synthesis
- Part 4: Integration Matrices A, B, C
- Part 5: Deployment & Integration

---

## 📋 Table of Contents

1. [Categories 9-12: Pre-Race Intelligence](#pre-race-intel)
2. [Categories 13-17: Form & Suitability](#form-suitability)

---

## 🔍 1. Categories 9-12: Pre-Race Intelligence {#pre-race-intel}

### **Category 9: Gear Changes** (667 lines in taxonomy)

**Purpose**: Evaluate equipment changes and their impact

**Key Information**:
```python
{
    "blinkers": "First Time",     # or "Removed", "Continued", None
    "tongue_tie": "Continued",
    "nose_roll": None,
    "lugging_bit": None,
    "cross_over_nose_band": "First Time",
    "bar_plates": None
}
```

**Qualitative Analysis Focus**:
- First-time blinkers (historically 18-22% improvement)
- Blinkers removed (often negative, horse may have improved)
- Tongue tie patterns (breathing, barrier manners)
- Gear change track record for this trainer

**LR Generation**:
```python
def analyze_gear_changes(horse: dict, trainer_stats: dict) -> dict:
    """
    Gear change impact assessment.

    Returns:
        {
            'lr_gear': 0.85-1.25,
            'reasoning': "string",
            'confidence': 0-1
        }
    """
    lr = 1.0
    reasoning_parts = []

    # Blinkers first time (strongest positive signal)
    if horse.get('blinkers') == 'First Time':
        # Check trainer's first-time blinkers success rate
        trainer_ft_blinkers_sr = trainer_stats.get('first_time_blinkers_sr', 0.20)

        if trainer_ft_blinkers_sr > 0.22:
            lr *= 1.22  # Above-average trainer with blinkers
            reasoning_parts.append(f"First-time blinkers (trainer {trainer_ft_blinkers_sr:.1%} SR)")
            confidence = 0.80
        else:
            lr *= 1.15  # Standard first-time blinkers boost
            reasoning_parts.append("First-time blinkers (standard positive)")
            confidence = 0.70

    # Blinkers removed (often negative)
    elif horse.get('blinkers') == 'Removed':
        lr *= 0.90  # Slight negative
        reasoning_parts.append("Blinkers removed (slight concern)")
        confidence = 0.65

    # Tongue tie first time (moderate positive)
    if horse.get('tongue_tie') == 'First Time':
        lr *= 1.08
        reasoning_parts.append("First-time tongue tie")
        confidence = 0.60

    # Nose roll changes
    if horse.get('nose_roll') == 'First Time':
        lr *= 1.05
        reasoning_parts.append("First-time nose roll")

    # Cross-over nose band (barrier manners)
    if horse.get('cross_over_nose_band') == 'First Time':
        lr *= 1.03
        reasoning_parts.append("First-time cross-over nose band")

    # No gear changes
    if not reasoning_parts:
        reasoning_parts.append("No gear changes")
        confidence = 0.50

    reasoning = " | ".join(reasoning_parts)

    return {
        'lr_gear': lr,
        'reasoning': reasoning,
        'confidence': confidence
    }
```

**Integration**: Matrix B (gear × fitness × trials)

---

### **Category 10: Barrier Trials** (667 lines in taxonomy) ⭐ **COMPETITIVE ADVANTAGE**

**Purpose**: Assess fitness and readiness via recent trial performances

**Key Information**:
```python
{
    "last_trial_date": "2025-11-02",
    "days_since_trial": 7,           # Ideal: 7-14 days
    "trial_time": 62.8,              # seconds (1000m)
    "trial_margin": "+0.5L",         # Behind winner
    "trial_effort": "Easy",          # Easy/Moderate/Sharp
    "jockey_comment": "Pleased, did what asked",
    "sectionals": {
        "600-400": 11.8,
        "400-200": 11.3,
        "200-0": 11.7
    }
}
```

**Qualitative Analysis Focus**:
- Trial recency (7-14 days ideal, >21 days stale)
- Effort level vs result (easy wins = positive, hard defeats = concern)
- Jockey/trainer comments (confidence indicators)
- Sectional pattern (closing strongly = fit, laboring = short of work)

**LR Generation**:
```python
def analyze_barrier_trials(horse: dict) -> dict:
    """
    Trial performance analysis - COMPETITIVE ADVANTAGE.

    Most punters don't have access to trial sectionals/comments.

    Returns:
        {
            'lr_trials': 0.75-1.35,
            'reasoning': "string",
            'confidence': 0-1
        }
    """
    if not horse.get('last_trial_date'):
        return {
            'lr_trials': 1.0,
            'reasoning': "No recent trial data",
            'confidence': 0.30
        }

    days_since = horse['days_since_trial']
    effort = horse.get('trial_effort', 'Unknown')
    margin = horse.get('trial_margin', 'Unknown')

    # Recency scoring
    if 7 <= days_since <= 14:
        recency_score = 1.15  # Optimal timing
        recency_note = f"Trial {days_since}d ago (optimal)"
    elif 4 <= days_since < 7:
        recency_score = 1.08  # Very recent, still good
        recency_note = f"Trial {days_since}d ago (fresh)"
    elif 15 <= days_since <= 21:
        recency_score = 1.05  # Acceptable
        recency_note = f"Trial {days_since}d ago (acceptable)"
    else:
        recency_score = 0.95  # Too stale or too fresh
        recency_note = f"Trial {days_since}d ago (suboptimal)"

    # Effort vs result assessment
    if effort == 'Easy':
        if 'won' in margin.lower() or margin.startswith('+'):
            effort_score = 1.20  # Easy win = very fit
            effort_note = "Easy trial win (excellent)"
        else:
            effort_score = 1.10  # Easy effort, didn't win (still good)
            effort_note = "Easy trial effort (positive)"
    elif effort == 'Moderate':
        if 'won' in margin.lower():
            effort_score = 1.12  # Moderate win
            effort_note = "Moderate trial win (good)"
        else:
            effort_score = 1.0  # Neutral
            effort_note = "Moderate trial effort"
    elif effort == 'Sharp':
        if 'won' in margin.lower():
            effort_score = 1.05  # Sharp win (may have peaked early)
            effort_note = "Sharp trial win (risk of peaking early)"
        else:
            effort_score = 0.85  # Sharp but didn't win (concern)
            effort_note = "Sharp trial, beaten (fitness concern)"
    else:
        effort_score = 1.0
        effort_note = "Unknown trial effort"

    # Sectional analysis (if available)
    sectional_note = ""
    if 'sectionals' in horse and horse['sectionals'].get('200-0'):
        l200 = horse['sectionals']['200-0']
        if l200 < 11.5:
            effort_score *= 1.08  # Closed strongly
            sectional_note = " | Strong L200m finish"
        elif l200 > 12.5:
            effort_score *= 0.93  # Labored late
            sectional_note = " | Labored L200m (fitness query)"

    # Jockey comment sentiment (simple keyword analysis)
    comment = horse.get('jockey_comment', '').lower()
    comment_note = ""
    if any(word in comment for word in ['pleased', 'happy', 'nice', 'good']):
        effort_score *= 1.05
        comment_note = " | Positive jockey feedback"
    elif any(word in comment for word in ['concern', 'disappointing', 'not pleased']):
        effort_score *= 0.95
        comment_note = " | Negative jockey feedback"

    # Combined LR
    lr_trials = recency_score * effort_score
    lr_trials = np.clip(lr_trials, 0.75, 1.35)

    reasoning = f"{recency_note} | {effort_note}{sectional_note}{comment_note}"

    # Confidence based on data completeness
    if 'sectionals' in horse and 'jockey_comment' in horse:
        confidence = 0.85  # Full trial data
    elif 'jockey_comment' in horse or 'sectionals' in horse:
        confidence = 0.70  # Partial data
    else:
        confidence = 0.60  # Basic data only

    return {
        'lr_trials': lr_trials,
        'reasoning': reasoning,
        'confidence': confidence
    }
```

**Integration**: Matrix B (trials × gear × fitness × last start)

---

### **Category 11: Jockey/Trainer Tactics** (655 lines in taxonomy)

**Purpose**: Evaluate tactical decisions and partnership dynamics

**Key Information**:
```python
{
    "rail_position": "True",         # or "+3m", "+6m", etc.
    "intended_position": "Midfield",
    "jockey_instructions": "Sit handy, balance up",
    "trainer_pattern": "Typically leads",
    "jockey_trainer_wins": 15,       # Partnership wins
    "jockey_trainer_sr": 0.28        # 28% strike rate together
}
```

**Qualitative Analysis Focus**:
- Tactical changes (different pattern than usual)
- Rail position strategy (inside rail vs wide rail)
- Jockey/trainer partnership strength
- Pre-race comments indicating confidence

**LR Generation**:
```python
def analyze_tactics(race: dict, horse: dict, jockey: dict, trainer: dict) -> dict:
    """
    Tactical suitability and partnership strength.

    Returns:
        {
            'lr_tactics': 0.90-1.20,
            'reasoning': "string",
            'confidence': 0-1
        }
    """
    lr = 1.0
    reasoning_parts = []

    # Jockey/Trainer partnership (STRONG signal)
    jt_sr = horse.get('jockey_trainer_sr', 0)
    if jt_sr > 0.25:
        lr *= 1.18  # Elite partnership (>25% SR)
        reasoning_parts.append(f"Strong J/T combo ({jt_sr:.1%} SR)")
        confidence = 0.85
    elif jt_sr > 0.18:
        lr *= 1.10  # Good partnership
        reasoning_parts.append(f"Good J/T combo ({jt_sr:.1%} SR)")
        confidence = 0.75
    elif jt_sr < 0.10 and horse.get('jockey_trainer_wins', 0) > 5:
        lr *= 0.95  # Poor partnership despite volume
        reasoning_parts.append(f"Weak J/T combo ({jt_sr:.1%} SR)")
        confidence = 0.70
    else:
        reasoning_parts.append("Standard J/T partnership")
        confidence = 0.60

    # Rail position strategy
    rail = race.get('rail_position', 'True')
    if rail == 'True':
        # True rail - inside barriers preferred
        if horse.get('barrier', 999) <= 6:
            lr *= 1.05
            reasoning_parts.append("True rail favors low barrier")
    else:
        # Rail out - may favor different barriers
        reasoning_parts.append(f"Rail {rail}")

    # Tactical pattern changes
    trainer_pattern = trainer.get('typical_pattern', '')
    intended = horse.get('intended_position', '')
    if trainer_pattern and intended:
        if trainer_pattern != intended:
            # Tactical change (can be positive or negative)
            reasoning_parts.append(f"Tactical change: usual {trainer_pattern} → {intended}")
            # Neutral unless we have more context

    reasoning = " | ".join(reasoning_parts)

    return {
        'lr_tactics': lr,
        'reasoning': reasoning,
        'confidence': confidence
    }
```

**Integration**: Matrix B (tactics × pace × barrier × jockey skill)

---

### **Category 12: Market Data** (655 lines in taxonomy)

**Purpose**: Interpret market sentiment and informed money

**Key Information**:
```python
{
    "opening_odds": 8.0,
    "current_odds": 5.5,
    "betfair_odds": 5.2,
    "market_move": "Firming",     # or "Drifting", "Stable"
    "betfair_vs_tab": -0.3,       # Betfair shorter (informed)
    "market_confidence": "Strong"
}
```

**Qualitative Analysis Focus**:
- Market moves (firming = support, drifting = concerns)
- Betfair vs TAB differential (Betfair shorter = smart money)
- Opening vs current (late money = informed)
- Market overreaction to news (gear changes, jockey bookings)

**LR Generation**:
```python
def analyze_market_data(horse: dict) -> dict:
    """
    Market sentiment analysis.

    Returns:
        {
            'lr_market': 0.90-1.15,
            'reasoning': "string",
            'confidence': 0-1
        }
    """
    opening = horse.get('opening_odds', 0)
    current = horse.get('current_odds', 0)
    betfair_diff = horse.get('betfair_vs_tab', 0)

    if opening == 0 or current == 0:
        return {
            'lr_market': 1.0,
            'reasoning': "No market data available",
            'confidence': 0.20
        }

    # Market move analysis
    move_pct = (opening - current) / opening * 100

    if move_pct > 15:
        # Significant firming (>15% odds drop)
        lr = 1.12
        reasoning = f"Strong market support: {opening:.1f} → {current:.1f}"
        confidence = 0.75
    elif move_pct > 8:
        # Moderate firming
        lr = 1.06
        reasoning = f"Moderate firming: {opening:.1f} → {current:.1f}"
        confidence = 0.65
    elif move_pct < -15:
        # Significant drifting (>15% odds increase)
        lr = 0.92
        reasoning = f"Drifting in betting: {opening:.1f} → {current:.1f}"
        confidence = 0.70
    else:
        # Stable
        lr = 1.0
        reasoning = f"Stable market: {opening:.1f} → {current:.1f}"
        confidence = 0.50

    # Betfair vs TAB (informed money indicator)
    if betfair_diff < -0.5:
        # Betfair significantly shorter (informed money)
        lr *= 1.08
        reasoning += f" | Betfair support ({betfair_diff:+.1f})"
        confidence = max(confidence, 0.70)
    elif betfair_diff > 0.5:
        # TAB shorter (less informed)
        lr *= 0.97
        reasoning += f" | TAB skewed ({betfair_diff:+.1f})"

    return {
        'lr_market': lr,
        'reasoning': reasoning,
        'confidence': confidence
    }
```

**Integration**: Matrix B (market × gear × trials - insider knowledge reflection)

---

## 📈 2. Categories 13-17: Form & Suitability {#form-suitability}

### **Category 13: Weather Sensitivity** (634 lines in taxonomy)

**Purpose**: Evaluate performance in different weather conditions

**Key Information**:
```python
{
    "wet_track_record": "2-1-0 from 5 starts",
    "wet_track_win_rate": 0.40,
    "firm_track_record": "3-2-4 from 15 starts",
    "firm_track_win_rate": 0.20,
    "pedigree_going_suit": 0.75,   # From Category 21 (Pedigree)
    "weather_preference": "Wet Tracker"
}
```

**Qualitative Analysis Focus**:
- Historical performance validation
- Sample size considerations (2 wins from 3 starts vs 2 from 20)
- Pedigree backup when limited history
- Track-specific going patterns (Flemington heavy vs Caulfield heavy)

**LR Generation**:
```python
def analyze_weather_sensitivity(race: dict, horse: dict) -> dict:
    """
    Going suitability (overlaps with Category 3 but focuses on horse).

    Returns:
        {
            'lr_weather': 0.70-1.30,
            'reasoning': "string",
            'confidence': 0-1
        }
    """
    going = race.get('going', 4)

    if going >= 7:  # Soft/Heavy
        wet_starts = horse.get('wet_track_starts', 0)
        wet_wins = horse.get('wet_track_wins', 0)
        wet_wr = wet_wins / wet_starts if wet_starts > 0 else 0

        if wet_starts >= 3:
            # Sufficient wet track history
            if wet_wr >= 0.30:
                lr = 1.25  # Strong wet tracker
                reasoning = f"Proven wet tracker: {wet_wins} wins from {wet_starts} starts"
                confidence = 0.85
            elif wet_wr < 0.10:
                lr = 0.75  # Poor wet form
                reasoning = f"Poor wet form: {wet_wins} wins from {wet_starts} starts"
                confidence = 0.80
            else:
                lr = 1.0
                reasoning = f"Acceptable wet form: {wet_wins} from {wet_starts}"
                confidence = 0.70
        else:
            # Limited history - rely on pedigree
            pedigree_suit = horse.get('pedigree_going_suit', 0.5)
            lr = 0.85 + (pedigree_suit * 0.45)  # 0.85-1.30 range
            reasoning = f"Limited wet form ({wet_starts} starts), using pedigree ({pedigree_suit:.2f})"
            confidence = 0.60

    else:  # Good/Firm
        # Most horses handle good tracks
        lr = 1.0
        reasoning = "Good track (neutral factor)"
        confidence = 0.50

    return {
        'lr_weather': lr,
        'reasoning': reasoning,
        'confidence': confidence
    }
```

**Integration**: Matrix C (weather × pedigree × distance)

---

### **Category 14: Fitness & Freshness** (634 lines in taxonomy)

**Purpose**: Assess current fitness state and campaign positioning

**Key Information**:
```python
{
    "days_since_last": 14,
    "campaign_run": 3,              # 3rd run this prep
    "spell_length": 90,             # Days since last campaign
    "career_fresh_record": "2-1-1 from 6",
    "career_fresh_sr": 0.33,
    "optimal_run": 2,               # Best at 2nd run in prep
    "peak_run_historical": [2, 3]   # Peaks at runs 2-3
}
```

**Qualitative Analysis Focus**:
- First-up vs 2nd-up vs 3rd-up patterns
- Spell length optimization (too short/long)
- Peak run identification
- Fitness progression curve

**LR Generation**:
```python
def analyze_fitness_freshness(horse: dict) -> dict:
    """
    Fitness state and campaign positioning.

    Returns:
        {
            'lr_fitness': 0.80-1.25,
            'reasoning': "string",
            'confidence': 0-1
        }
    """
    campaign_run = horse.get('campaign_run', 1)
    days_since_last = horse.get('days_since_last', 14)
    peak_runs = horse.get('peak_run_historical', [2, 3])

    # Campaign run pattern
    if campaign_run == 1:
        # First-up
        fresh_sr = horse.get('career_fresh_sr', 0.15)
        if fresh_sr > 0.25:
            lr = 1.20  # Strong first-upper
            reasoning = f"First-up specialist ({fresh_sr:.1%} SR)"
            confidence = 0.80
        elif fresh_sr < 0.12:
            lr = 0.85  # Needs runs
            reasoning = f"First-up concern ({fresh_sr:.1%} SR, needs race fitness)"
            confidence = 0.75
        else:
            lr = 1.0
            reasoning = f"First-up ({fresh_sr:.1%} SR)"
            confidence = 0.65

    elif campaign_run in peak_runs:
        # At peak run
        lr = 1.22  # Peak fitness
        reasoning = f"Peak run {campaign_run} (historical pattern)"
        confidence = 0.85

    elif campaign_run > max(peak_runs) + 2:
        # Likely past peak
        lr = 0.88  # Backing up too many times
        reasoning = f"Run {campaign_run} (past peak, may be over-raced)"
        confidence = 0.70

    else:
        # Building fitness
        lr = 1.05
        reasoning = f"Run {campaign_run} (improving fitness)"
        confidence = 0.65

    # Days since last run adjustment
    if days_since_last < 7:
        lr *= 0.93  # Quick backup
        reasoning += f" | Quick backup ({days_since_last}d)"
    elif days_since_last > 35:
        lr *= 0.95  # Extended gap
        reasoning += f" | Extended gap ({days_since_last}d)"
    elif 14 <= days_since_last <= 21:
        lr *= 1.03  # Optimal spacing
        reasoning += f" | Optimal spacing ({days_since_last}d)"

    return {
        'lr_fitness': lr,
        'reasoning': reasoning,
        'confidence': confidence
    }
```

**Integration**: Matrix B (fitness × trials × last start × gear)

---

### **Category 15: Distance Suitability** (634 lines in taxonomy)

**Purpose**: Evaluate optimal distance range for horse

**Key Information**:
```python
{
    "today_distance": 1600,
    "optimal_distance": 1400,       # Best performances at 1400m
    "distance_record": {
        "1200": "1-0-1 from 3",
        "1400": "3-2-0 from 6",
        "1600": "1-1-2 from 5",
        "2000": "0-0-1 from 2"
    },
    "distance_range": "1200-1600m",
    "pedigree_distance_suit": 0.68  # From Category 21
}
```

**Qualitative Analysis Focus**:
- Optimal range identification
- Stepping up/down in distance
- Pedigree validation for first-time distances
- Sectional data correlation (fast closers = further, speed horses = shorter)

**LR Generation**:
```python
def analyze_distance_suitability(race: dict, horse: dict) -> dict:
    """
    Distance optimization assessment.

    Returns:
        {
            'lr_distance': 0.75-1.25,
            'reasoning': "string",
            'confidence': 0-1
        }
    """
    today_distance = race['distance']
    optimal = horse.get('optimal_distance', today_distance)
    distance_record = horse.get('distance_record', {})
    pedigree_suit = horse.get('pedigree_distance_suit', 0.5)

    # Check if raced at this distance before
    distance_key = str(today_distance)
    if distance_key in distance_record:
        # Has form at this distance
        record = distance_record[distance_key]
        # Parse "3-2-0 from 6" → 3 wins, 6 starts
        parts = record.split(' from ')
        if len(parts) == 2:
            results = parts[0].split('-')
            wins = int(results[0])
            starts = int(parts[1])
            win_rate = wins / starts if starts > 0 else 0

            if win_rate >= 0.30:
                lr = 1.20  # Excellent record at this distance
                reasoning = f"Strong {today_distance}m form: {record}"
                confidence = 0.85
            elif win_rate >= 0.15:
                lr = 1.08  # Decent record
                reasoning = f"Decent {today_distance}m form: {record}"
                confidence = 0.75
            else:
                lr = 0.95  # Poor record at this distance
                reasoning = f"Poor {today_distance}m form: {record}"
                confidence = 0.70
        else:
            lr = 1.0
            reasoning = f"Has raced at {today_distance}m"
            confidence = 0.60

    else:
        # First time at this distance - use pedigree + optimal range
        distance_diff = abs(today_distance - optimal)

        if distance_diff <= 200:
            # Within comfort zone
            lr = 1.0 + (pedigree_suit * 0.10)
            reasoning = f"First time {today_distance}m (within range, pedigree {pedigree_suit:.2f})"
            confidence = 0.65
        elif distance_diff <= 400:
            # Moderate stretch
            lr = 0.90 + (pedigree_suit * 0.20)
            reasoning = f"First time {today_distance}m (moderate stretch, pedigree {pedigree_suit:.2f})"
            confidence = 0.70
        else:
            # Significant stretch
            lr = 0.80 + (pedigree_suit * 0.30)
            reasoning = f"First time {today_distance}m (major stretch, relying on pedigree {pedigree_suit:.2f})"
            confidence = 0.75

    return {
        'lr_distance': lr,
        'reasoning': reasoning,
        'confidence': confidence
    }
```

**Integration**: Matrix C (distance × pedigree × sectionals × class)

---

### **Category 16: Last Start Analysis** (622 lines in taxonomy)

**Purpose**: Deep dive into most recent performance

**Key Information**:
```python
{
    "last_start_date": "2025-10-26",
    "days_since": 14,
    "last_finish": 3,
    "last_margin": "+1.2L",
    "last_track": "Flemington",
    "last_distance": 1400,
    "last_going": 4,
    "last_sectionals": {
        "600-400": 11.4,
        "400-200": 11.2,
        "200-0": 11.5
    },
    "last_comments": "Closing well, unlucky",
    "beaten_by": ["Anamoe", "Via Sistina"]
}
```

**Qualitative Analysis Focus**:
- Closing sectionals (improving or fading)
- Margin beaten by quality (narrow loss to Group 1 horse = strong)
- Comments indicating bad luck/wide run
- Form trending (improving or declining)

**LR Generation**:
```python
def analyze_last_start(horse: dict) -> dict:
    """
    Last start performance deep analysis.

    Returns:
        {
            'lr_last_start': 0.85-1.20,
            'reasoning': "string",
            'confidence': 0-1
        }
    """
    finish = horse.get('last_finish', 999)
    margin = horse.get('last_margin', '')
    sectionals = horse.get('last_sectionals', {})
    comments = horse.get('last_comments', '').lower()

    # Finishing position baseline
    if finish == 1:
        lr = 1.15  # Last start winner
        reasoning = "Last start winner"
        confidence = 0.80
    elif finish <= 3:
        lr = 1.08  # Placed last start
        reasoning = f"Placed {finish} last start"
        confidence = 0.70
    elif finish <= 5:
        lr = 1.0  # Competitive
        reasoning = f"Finished {finish} last start"
        confidence = 0.60
    else:
        lr = 0.92  # Poor last start
        reasoning = f"Finished {finish} last start"
        confidence = 0.55

    # Sectional analysis (closing speed)
    if sectionals.get('200-0'):
        l200 = sectionals['200-0']
        if l200 < 11.3:
            lr *= 1.10  # Fast closer
            reasoning += " | Strong L200m ({l200:.1f}s)"
        elif l200 > 12.0:
            lr *= 0.93  # Labored late
            reasoning += f" | Labored L200m ({l200:.1f}s)"

    # Margin and comments (luck factors)
    if any(word in comments for word in ['unlucky', 'bad luck', 'wide', 'checked', 'crowded']):
        lr *= 1.08  # Bad luck last start
        reasoning += " | Unlucky last time"
        confidence = 0.75

    if any(word in comments for word in ['eased', 'pulled up', 'bled']):
        lr *= 0.88  # Serious issue
        reasoning += " | Concerning last start"
        confidence = 0.70

    # Quality of opposition (if beaten by elite horses)
    beaten_by = horse.get('beaten_by', [])
    if beaten_by and any('Group 1' in str(h) for h in beaten_by):
        lr *= 1.05  # Competitive in elite company
        reasoning += " | Competitive in Group 1 company"

    return {
        'lr_last_start': lr,
        'reasoning': reasoning,
        'confidence': confidence
    }
```

**Integration**: Matrix B (last start × fitness × trials × sectionals)

---

### **Category 17: Jockey/Trainer/Horse Chemistry** (622 lines in taxonomy)

**Purpose**: Evaluate partnership synergies across all connections

**Key Information**:
```python
{
    "jockey_trainer_sr": 0.28,
    "jockey_trainer_roi": 1.45,
    "jockey_horse_record": "3-1-2 from 8",
    "jockey_horse_sr": 0.375,
    "trainer_horse_history": "First time trainer",
    "stable_jockey_preference": "Preferred stable jockey"
}
```

**Qualitative Analysis Focus**:
- Jockey/Trainer mega-partnerships (Kah/Waller, McDonald/Cummings)
- Jockey/Horse familiarity (knows the horse's quirks)
- Trainer change impacts (positive or negative)
- Stable jockey loyalty (preferred rider = confidence)

**LR Generation**:
```python
def analyze_chemistry(horse: dict, jockey: dict, trainer: dict) -> dict:
    """
    Partnership synergy analysis - BRIDGES TO QUANTITATIVE.

    This category creates Integration Matrix C connections:
    - Chemistry × Quantitative Speed/Class (confidence multiplier)

    Returns:
        {
            'lr_chemistry': 0.85-1.25,
            'reasoning': "string",
            'confidence': 0-1
        }
    """
    lr = 1.0
    reasoning_parts = []

    # Jockey/Trainer partnership (PRIMARY signal)
    jt_sr = horse.get('jockey_trainer_sr', 0)
    jt_roi = horse.get('jockey_trainer_roi', 1.0)

    if jt_sr > 0.25 and jt_roi > 1.20:
        lr *= 1.22  # Elite partnership (>25% SR, >20% ROI)
        reasoning_parts.append(f"Elite J/T: {jt_sr:.1%} SR, {jt_roi:.2f} ROI")
        confidence = 0.88
    elif jt_sr > 0.20:
        lr *= 1.12  # Strong partnership
        reasoning_parts.append(f"Strong J/T: {jt_sr:.1%} SR")
        confidence = 0.80
    elif jt_sr < 0.12 and horse.get('jockey_trainer_rides', 0) > 10:
        lr *= 0.92  # Poor partnership despite volume
        reasoning_parts.append(f"Weak J/T: {jt_sr:.1%} SR")
        confidence = 0.70
    else:
        reasoning_parts.append("Standard J/T partnership")
        confidence = 0.60

    # Jockey/Horse familiarity
    jh_record = horse.get('jockey_horse_record', '')
    if jh_record:
        parts = jh_record.split(' from ')
        if len(parts) == 2:
            results = parts[0].split('-')
            wins = int(results[0])
            starts = int(parts[1])
            jh_sr = wins / starts if starts > 0 else 0

            if jh_sr > 0.30 and starts >= 3:
                lr *= 1.15  # Strong jockey/horse combo
                reasoning_parts.append(f"Strong J/H: {jh_record}")
            elif jh_sr < 0.15 and starts >= 5:
                lr *= 0.95  # Poor jockey/horse combo
                reasoning_parts.append(f"Poor J/H: {jh_record}")

    # Stable jockey (confidence indicator)
    if horse.get('stable_jockey_preference') == 'Preferred stable jockey':
        lr *= 1.08
        reasoning_parts.append("Preferred stable jockey")

    # First time trainer (often positive for quality trainers)
    if horse.get('trainer_horse_history') == 'First time trainer':
        if trainer.get('stable_strike_rate', 0) > 0.18:
            lr *= 1.10  # Quality trainer taking over
            reasoning_parts.append(f"First time with {trainer['name']} (elite stable)")
        else:
            reasoning_parts.append("First time with trainer")

    reasoning = " | ".join(reasoning_parts)

    return {
        'lr_chemistry': lr,
        'reasoning': reasoning,
        'confidence': confidence
    }
```

**Integration**: Matrix C (chemistry × quantitative base probabilities - FUSION BRIDGE)

---

**Continue to Part 3: LLM Chain & Synthesis →**
