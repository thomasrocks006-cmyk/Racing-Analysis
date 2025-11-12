# Master Taxonomy - Part 3: Category 4 (Barrier Draw)

**Document Purpose:** Implementation reference for barrier position analysis and impact assessment
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (feature engineering)
**Implementation Priority:** Phase 1 Week 2

---

## CATEGORY 4: BARRIER DRAW

### Overview
- **Category ID:** 4
- **Prediction Power:** 8-15% (highly venue and distance dependent)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 2
- **Cost per Race:** $0 (public data)
- **ChatGPT Access:** 95% (good barrier access, limited bias analysis)
- **Our Target Access:** 100% (systematic barrier + historical bias analysis)

---

## SUBCATEGORIES

### 4.1 Barrier Position
**Description:** Starting gate position (1 = inside rail, higher numbers = outside)
**Data Type:** Integer (1-24, typically 1-20 for most races)
**Prediction Impact:** 8-15% at venues with strong bias, 3-5% at neutral venues

**Sources:**
- Racing.com form guide (Tier 1, 100% coverage, free)
- Tab.com.au race card (Tier 3, 100% coverage, free)

**Access Method:**
```python
def extract_barrier_positions(race_url):
    """Extract barrier positions for all horses in race"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    barriers = {}
    horse_rows = soup.find_all('div', class_='runner-row')

    for row in horse_rows:
        horse_name = row.find('span', class_='horse-name').text
        barrier_element = row.find('span', class_='barrier')
        barrier_number = int(barrier_element.text)

        barriers[horse_name] = barrier_number

    return barriers
```

**Qualitative Usage (GPT-5):**
- Context: "Horse X drawn barrier 2 at Flemington 1200m, typically advantageous..."
- Reasoning: "Flemington 1200m shows inside barriers (1-4) win at 18% vs outside (10+) at 8%"
- Output: Barrier advantage adjustment (+10-15% if strongly favorable draw)

**Quantitative Features:**
- `barrier_position` (numeric: 1-24)
- `barrier_category` (categorical: inside_1_4, middle_5_8, wide_9_plus)
- `barrier_percentile` (numeric: 0-1, position relative to field size)
- `venue_distance_barrier_win_pct` (numeric: historical win % for this barrier at venue+distance)
- `is_inside_barrier` (binary: 1 if barrier <= 4)
- `is_outside_barrier` (binary: 1 if barrier > field_size * 0.6)

**Feature Engineering:**
```python
def engineer_barrier_features(barrier_position, field_size, venue, distance):
    """Create barrier position features"""
    features = {}

    # Base barrier position
    features['barrier_position'] = barrier_position

    # Barrier category
    if barrier_position <= 4:
        features['barrier_category'] = 'inside'
    elif barrier_position <= 8:
        features['barrier_category'] = 'middle'
    else:
        features['barrier_category'] = 'wide'

    # Barrier percentile (relative to field)
    features['barrier_percentile'] = barrier_position / field_size

    # Flags
    features['is_inside_barrier'] = 1 if barrier_position <= 4 else 0
    features['is_outside_barrier'] = 1 if barrier_position > field_size * 0.6 else 0

    # Historical barrier performance at venue+distance
    historical_win_pct = get_barrier_win_rate(venue, distance, barrier_position)
    features['venue_distance_barrier_win_pct'] = historical_win_pct

    # Barrier advantage score (vs average)
    avg_win_pct = 1 / field_size  # Baseline
    features['barrier_advantage_score'] = historical_win_pct - avg_win_pct

    return features

def get_barrier_win_rate(venue, distance, barrier_position):
    """Query historical win rate for specific barrier at venue+distance"""
    query = f"""
    SELECT
        COUNT(CASE WHEN position = 1 THEN 1 END) * 1.0 / COUNT(*) as win_pct
    FROM race_results
    WHERE venue = '{venue}'
      AND distance = {distance}
      AND barrier_position = {barrier_position}
      AND race_date > DATE_SUB(NOW(), INTERVAL 3 YEAR)
    """
    result = execute_query(query)
    return result['win_pct'] if result else 0.1  # Default if no data
```

---

### 4.2 Barrier Statistics by Venue/Distance
**Description:** Historical barrier performance patterns for specific venue+distance combinations
**Data Type:** Structured database (pre-computed)
**Prediction Impact:** 8-12% (provides context for barrier interpretation)

**Barrier Statistics Database Structure:**
```python
BARRIER_STATS_SCHEMA = {
    "venue": str,
    "distance": int,
    "barrier_position": int,
    "sample_size": int,           # Number of historical races
    "win_count": int,
    "win_percentage": float,      # Win rate for this barrier
    "place_percentage": float,    # Top 3 rate
    "avg_finish_position": float,
    "roi": float,                 # Return on investment (if backed at $1)
    "last_updated": datetime
}
```

**Pre-computation Script:**
```python
def build_barrier_stats_database():
    """Build comprehensive barrier statistics database"""
    venues = ['flemington', 'randwick', 'caulfield', 'rosehill', 'moonee_valley']
    distances = [1000, 1100, 1200, 1400, 1600, 1800, 2000, 2400, 3200]

    barrier_stats = []

    for venue in venues:
        for distance in distances:
            # Query historical data
            query = f"""
            SELECT
                barrier_position,
                COUNT(*) as sample_size,
                SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) as win_count,
                AVG(CASE WHEN position <= 3 THEN 1.0 ELSE 0.0 END) as place_pct,
                AVG(position) as avg_position,
                AVG(CASE WHEN position = 1 THEN odds ELSE -1.0 END) as roi
            FROM race_results
            WHERE venue = '{venue}'
              AND distance = {distance}
              AND race_date > DATE_SUB(NOW(), INTERVAL 3 YEAR)
            GROUP BY barrier_position
            """

            results = execute_query(query)

            for row in results:
                barrier_stats.append({
                    'venue': venue,
                    'distance': distance,
                    'barrier_position': row['barrier_position'],
                    'sample_size': row['sample_size'],
                    'win_count': row['win_count'],
                    'win_percentage': row['win_count'] / row['sample_size'],
                    'place_percentage': row['place_pct'],
                    'avg_finish_position': row['avg_position'],
                    'roi': row['roi'],
                    'last_updated': datetime.now()
                })

    # Save to database
    save_to_database(barrier_stats, table='barrier_statistics')

    return barrier_stats

# Run monthly to keep data fresh
```

**Access Barrier Statistics:**
```python
def get_barrier_statistics(venue, distance):
    """Retrieve barrier statistics for venue+distance combination"""
    query = f"""
    SELECT *
    FROM barrier_statistics
    WHERE venue = '{venue}'
      AND distance = {distance}
    ORDER BY barrier_position
    """

    stats = execute_query(query)

    # Convert to structured format
    barrier_dict = {}
    for stat in stats:
        barrier_dict[stat['barrier_position']] = {
            'win_pct': stat['win_percentage'],
            'place_pct': stat['place_percentage'],
            'avg_position': stat['avg_finish_position'],
            'roi': stat['roi'],
            'sample_size': stat['sample_size']
        }

    return barrier_dict
```

**Qualitative Usage (GPT-5):**
- Context: "Flemington 1200m barrier statistics: Barrier 1-3 win 16%, Barrier 10+ win 6%..."
- Reasoning: "Strong inside barrier bias, Horse X drawn barrier 2 is advantageous"
- Output: Statistical barrier context (enhances confidence in barrier assessment)

**Quantitative Features:**
- `barrier_stats_win_pct` (numeric: historical win % for this barrier)
- `barrier_stats_place_pct` (numeric: historical place % for this barrier)
- `barrier_stats_avg_position` (numeric: average finish position)
- `barrier_stats_roi` (numeric: return on investment)
- `barrier_stats_sample_size` (numeric: data reliability indicator)
- `barrier_vs_expected` (derived: actual barrier vs field average)

**Feature Engineering:**
```python
def engineer_barrier_stats_features(barrier_position, venue, distance, field_size):
    """Create features from barrier statistics"""
    features = {}

    # Get barrier statistics for this venue+distance
    barrier_stats = get_barrier_statistics(venue, distance)

    if barrier_position in barrier_stats:
        stats = barrier_stats[barrier_position]
        features['barrier_stats_win_pct'] = stats['win_pct']
        features['barrier_stats_place_pct'] = stats['place_pct']
        features['barrier_stats_avg_position'] = stats['avg_position']
        features['barrier_stats_roi'] = stats['roi']
        features['barrier_stats_sample_size'] = stats['sample_size']

        # Calculate vs expected
        expected_win_pct = 1 / field_size
        features['barrier_vs_expected'] = stats['win_pct'] - expected_win_pct

        # Statistical confidence
        if stats['sample_size'] > 100:
            features['barrier_stats_confidence'] = 'high'
        elif stats['sample_size'] > 30:
            features['barrier_stats_confidence'] = 'medium'
        else:
            features['barrier_stats_confidence'] = 'low'
    else:
        # No historical data for this barrier (unusual)
        features['barrier_stats_win_pct'] = 1 / field_size
        features['barrier_stats_place_pct'] = 3 / field_size
        features['barrier_stats_avg_position'] = (field_size + 1) / 2
        features['barrier_stats_roi'] = 1.0
        features['barrier_stats_sample_size'] = 0
        features['barrier_vs_expected'] = 0
        features['barrier_stats_confidence'] = 'none'

    return features
```

---

### 4.3 Barrier Bias Interaction with Track Conditions
**Description:** How barrier advantage changes with track condition and rail position
**Data Type:** Derived (combination of Category 3 + Category 4)
**Prediction Impact:** 5-10% (refines barrier assessment based on conditions)

**Barrier-Condition Interaction Matrix:**
```python
BARRIER_CONDITION_INTERACTION = {
    'flemington_1200m': {
        'Good_true_rail': {
            'inside_advantage': 0.05,   # Inside barriers slight edge
            'outside_advantage': 0.0
        },
        'Good_out_6m': {
            'inside_advantage': 0.0,
            'outside_advantage': 0.12   # Outside strongly favored
        },
        'Heavy_true_rail': {
            'inside_advantage': 0.15,   # Inside heavily favored (saves ground)
            'outside_advantage': 0.0
        },
        'Heavy_out_6m': {
            'inside_advantage': -0.05,  # Inside disadvantaged (worst ground)
            'outside_advantage': 0.08
        }
    },
    # ... add all major venue+distance combinations
}
```

**Calculate Barrier-Condition Advantage:**
```python
def calculate_barrier_condition_advantage(barrier_position, venue, distance,
                                         track_condition, rail_position, field_size):
    """Calculate how conditions affect barrier advantage"""

    # Build interaction key
    interaction_key = f"{venue}_{distance}m"
    condition_key = f"{track_condition['condition']}_{rail_position}"

    # Get interaction matrix
    interaction = BARRIER_CONDITION_INTERACTION.get(interaction_key, {}).get(condition_key, {})

    # Determine if barrier is inside or outside
    barrier_percentile = barrier_position / field_size

    if barrier_percentile < 0.4:  # Inside barriers
        advantage = interaction.get('inside_advantage', 0)
    elif barrier_percentile > 0.6:  # Outside barriers
        advantage = interaction.get('outside_advantage', 0)
    else:  # Middle barriers
        # Interpolate advantage
        advantage = 0

    return {
        'barrier_condition_advantage': advantage,
        'barrier_condition_key': condition_key,
        'barrier_position_type': 'inside' if barrier_percentile < 0.4 else
                                'outside' if barrier_percentile > 0.6 else 'middle'
    }
```

**Qualitative Usage (GPT-5):**
- Context: "Rail out 6m + Good 4 + barrier 11 = typically 12% advantage at Flemington 1200m..."
- Reasoning: "Conditions favor outside barriers, Horse X well-drawn"
- Output: Refined barrier adjustment accounting for today's specific conditions

**Quantitative Features:**
- `barrier_condition_advantage` (numeric: -0.2 to +0.2 adjustment)
- `barrier_condition_interaction` (categorical: favorable/neutral/unfavorable)
- `is_barrier_condition_match` (binary: 1 if barrier suits today's conditions)

**Feature Engineering:**
```python
def engineer_barrier_condition_features(barrier_position, venue, distance,
                                       track_condition, rail_position, field_size):
    """Create barrier-condition interaction features"""

    advantage_data = calculate_barrier_condition_advantage(
        barrier_position, venue, distance, track_condition, rail_position, field_size
    )

    features = {}
    features['barrier_condition_advantage'] = advantage_data['barrier_condition_advantage']
    features['barrier_position_type'] = advantage_data['barrier_position_type']

    # Interaction categorization
    if advantage_data['barrier_condition_advantage'] > 0.08:
        features['barrier_condition_interaction'] = 'highly_favorable'
    elif advantage_data['barrier_condition_advantage'] > 0.03:
        features['barrier_condition_interaction'] = 'favorable'
    elif advantage_data['barrier_condition_advantage'] > -0.03:
        features['barrier_condition_interaction'] = 'neutral'
    else:
        features['barrier_condition_interaction'] = 'unfavorable'

    # Match flag
    features['is_barrier_condition_match'] = 1 if advantage_data['barrier_condition_advantage'] > 0.05 else 0

    return features
```

---

## INTEGRATION GUIDELINES

### Cross-Category Dependencies

**Category 4 Integration with Other Categories:**

1. **With Category 3 (Track Conditions):**
   - Rail position + track bias → barrier advantage shifts
   - Heavy track + true rail → inside barriers save ground (advantage)
   - Firm track + rail out 6m → outside barriers have better footing (advantage)

2. **With Category 8 (Pace Scenario):**
   - Barrier + pace pressure → tactical positioning
   - Inside barrier + high pace pressure → can slot in, save ground
   - Wide barrier + slow pace → forced wide, disadvantaged

3. **With Category 11 (Jockey/Trainer Tactics):**
   - Barrier + riding style → race strategy
   - Wide barrier + on-pace jockey → likely to push forward early
   - Inside barrier + patient jockey → can settle and wait

4. **With Category 14 (Historical Performance):**
   - Horse's barrier record → barrier draw suitability
   - Horse wins 4 of 8 from inside barriers → inside draw favorable
   - Horse never won from barrier 10+ → wide draw concern

### Validation Rules

**Category 4 Validation:**
```python
def validate_barrier_data(barrier_data, field_size):
    """Validate category 4 data"""
    errors = []
    warnings = []

    # Barrier position validation
    if barrier_data['barrier_position'] < 1:
        errors.append("Barrier position must be >= 1")

    if barrier_data['barrier_position'] > field_size:
        errors.append(f"Barrier {barrier_data['barrier_position']} exceeds field size {field_size}")

    if barrier_data['barrier_position'] > 20:
        warnings.append("Unusually wide barrier (>20), verify field size")

    # Barrier statistics validation
    if barrier_data.get('barrier_stats_sample_size', 0) < 10:
        warnings.append("Limited barrier statistics (<10 samples), low confidence")

    # Barrier advantage validation
    advantage = barrier_data.get('barrier_condition_advantage', 0)
    if abs(advantage) > 0.25:
        warnings.append(f"Extreme barrier advantage ({advantage}), verify calculation")

    return {'errors': errors, 'warnings': warnings}
```

---

## UNIFIED DATA MODEL

### Complete Schema for Category 4

```python
barrier_schema = {
    # 4.1 Barrier Position
    "barrier_position": {
        "position": int,               # 2
        "category": str,               # "inside"
        "percentile": float,           # 0.125 (2/16)
        "is_inside": bool,
        "is_outside": bool
    },

    # 4.2 Barrier Statistics
    "barrier_stats": {
        "win_pct": float,
        "place_pct": float,
        "avg_position": float,
        "roi": float,
        "sample_size": int,
        "confidence": str,
        "vs_expected": float
    },

    # 4.3 Barrier-Condition Interaction
    "barrier_condition": {
        "advantage": float,
        "interaction": str,
        "is_match": bool,
        "position_type": str
    }
}
```

### Example Complete Record

```python
example_barrier = {
    "barrier_position": {
        "position": 2,
        "category": "inside",
        "percentile": 0.125,
        "is_inside": True,
        "is_outside": False
    },
    "barrier_stats": {
        "win_pct": 0.16,
        "place_pct": 0.42,
        "avg_position": 5.2,
        "roi": 1.15,
        "sample_size": 87,
        "confidence": "high",
        "vs_expected": 0.0975  # 16% - 6.25% baseline
    },
    "barrier_condition": {
        "advantage": 0.12,
        "interaction": "highly_favorable",
        "is_match": True,
        "position_type": "inside"
    }
}
```

---

## COST ANALYSIS

**Category 4 Cost Breakdown:**
- **Barrier data extraction:** $0 (public data)
- **Barrier statistics database:** $0 (one-time build, monthly refresh)
- **Processing time:** <5 seconds per race

**Total Cost:** $0 per race

---

## IMPLEMENTATION CHECKLIST

### Phase 1 Week 2: Category 4 Implementation

**Day 1: Barrier Data Extraction**
- [ ] Implement `extract_barrier_positions()`
- [ ] Test on 20 sample races
- [ ] Validate barrier extraction accuracy (100% target)

**Day 2: Barrier Statistics Database**
- [ ] Build `build_barrier_stats_database()` script
- [ ] Run historical analysis (past 3 years)
- [ ] Create `barrier_statistics` database table
- [ ] Schedule monthly refresh job

**Day 3: Barrier-Condition Interaction**
- [ ] Build BARRIER_CONDITION_INTERACTION matrix
- [ ] Implement `calculate_barrier_condition_advantage()`
- [ ] Validate interaction patterns against known biases

**Day 4: Feature Engineering**
- [ ] Implement all feature engineering functions
- [ ] Test on diverse venue/distance/condition combinations
- [ ] Validate feature ranges and distributions

**Day 5: Integration Testing**
- [ ] Test full Category 4 pipeline on 30 races
- [ ] Cross-validate with Category 3 (track conditions)
- [ ] Document barrier patterns by major venues
- [ ] Prepare for Category 5 (Weight) integration

---

**Document Complete: Category 4 (Barrier Draw)**
**Next Document: PART_04_CATEGORY_05.md (Weight)**
