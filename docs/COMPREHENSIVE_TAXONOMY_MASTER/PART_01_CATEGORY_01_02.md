# Master Taxonomy - Part 1: Categories 1-2 (Basic Race Information)

**Document Purpose:** Implementation reference for basic race metadata and foundational information
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (feature engineering)
**Implementation Priority:** Phase 1 Week 1 (foundational data layer)

---

## CATEGORY 1: RACE METADATA

### Overview
- **Category ID:** 1
- **Prediction Power:** 3-8% (foundational context, not highly predictive alone)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 1
- **Cost per Race:** $0 (public data, no authentication required)
- **ChatGPT Access:** 90% (good public access)
- **Our Target Access:** 100% (systematic API/scraping)

### Subcategories

#### 1.1 Distance
**Description:** Race distance in meters (e.g., 1200m, 1600m, 2400m)
**Data Type:** Integer (meters)
**Prediction Impact:** 5-8% when matched to horse's optimal distance

**Sources:**
- Racing.com form guide (Tier 1, 100% coverage, free)
- Tab.com.au race card (Tier 3, 100% coverage, free)
- Punters.com.au (Tier 2, 100% coverage, subscription)

**Access Method:**
```python
def extract_race_distance(race_url):
    """Extract race distance from form guide"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    distance_element = soup.find('span', class_='race-distance')
    distance_text = distance_element.text  # e.g., "1200m"
    distance_meters = int(distance_text.replace('m', ''))

    return distance_meters
```

**Qualitative Usage (GPT-5):**
- Context: "This is a 1200m sprint at Flemington..."
- Reasoning: "Horse X has won 3 of 5 starts at 1200m (60% strike rate)"
- Output: Distance suitability adjustment (+8-12% if optimal, -10-15% if unsuitable)

**Quantitative Features:**
- `distance_meters` (numeric, 1000-3200 range)
- `distance_category` (categorical: sprint <1400m, mile 1400-1800m, staying >1800m)
- `horse_distance_win_pct` (derived: horse's historical win % at this distance)
- `distance_delta_from_ideal` (derived: |race_distance - horse_ideal_distance|)
- `is_distance_specialist` (binary: 1 if horse_distance_win_pct > 30%)

**Feature Engineering:**
```python
def engineer_distance_features(race_distance, horse_history):
    """Create distance-related features for quantitative model"""
    features = {}

    # Base distance
    features['distance_meters'] = race_distance

    # Distance category
    if race_distance < 1400:
        features['distance_category'] = 'sprint'
    elif race_distance < 1800:
        features['distance_category'] = 'mile'
    else:
        features['distance_category'] = 'staying'

    # Horse's performance at this distance
    distance_starts = [r for r in horse_history if r['distance'] == race_distance]
    if distance_starts:
        wins = sum(1 for r in distance_starts if r['position'] == 1)
        features['horse_distance_win_pct'] = wins / len(distance_starts)
    else:
        features['horse_distance_win_pct'] = 0

    # Distance delta from ideal
    ideal_distance = calculate_ideal_distance(horse_history)
    features['distance_delta_from_ideal'] = abs(race_distance - ideal_distance)

    # Specialist flag
    features['is_distance_specialist'] = 1 if features['horse_distance_win_pct'] > 0.3 else 0

    return features
```

**Data Schema:**
```python
distance_schema = {
    "distance_meters": int,          # 1200
    "distance_text": str,            # "1200m"
    "distance_category": str,        # "sprint" | "mile" | "staying"
    "distance_furlong": float        # 6.0 (for international)
}
```

**Validation Rules:**
- Distance must be 1000-3200m (Australian racing standard)
- Warn if <1000m or >3200m (unusual, verify)
- Cross-reference with venue typical distances (Flemington 1200-3200m)

**Integration Rules:**
- Combine with Category 2 (race type) for class analysis
- Combine with Category 14 (historical performance) for distance suitability
- Combine with Category 16 (horse intangibles) for distance preference

---

#### 1.2 Venue
**Description:** Racecourse location (e.g., Flemington, Randwick, Caulfield)
**Data Type:** String (categorical)
**Prediction Impact:** 3-5% (venue-specific biases and characteristics)

**Sources:**
- Racing.com form guide (Tier 1, 100% coverage, free)
- Tab.com.au race card (Tier 3, 100% coverage, free)

**Access Method:**
```python
def extract_venue(race_url):
    """Extract venue from race URL or page"""
    # Method 1: Parse from URL
    # https://racing.com/form-guide/thoroughbred/2024-12-28/flemington/race-7
    url_parts = race_url.split('/')
    venue = url_parts[-2]  # 'flemington'

    # Method 2: Parse from page (fallback)
    if not venue:
        response = requests.get(race_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        venue_element = soup.find('span', class_='venue-name')
        venue = venue_element.text.lower()

    return venue
```

**Venue Database:**
```python
VENUE_DATABASE = {
    'flemington': {
        'state': 'VIC',
        'class': 'metro',
        'track_type': 'turf',
        'circumference': 2312,  # meters
        'turn_type': 'wide',
        'straight_length': 450,
        'typical_distances': [1100, 1200, 1400, 1600, 2000, 2500, 3200],
        'known_biases': ['outside_barrier_advantage', 'on_pace_favored']
    },
    'randwick': {
        'state': 'NSW',
        'class': 'metro',
        'track_type': 'turf',
        'circumference': 2224,
        'turn_type': 'tight',
        'straight_length': 400,
        'typical_distances': [1000, 1200, 1400, 1600, 2000, 2400],
        'known_biases': ['inside_barrier_advantage_wet', 'backmarker_straight']
    },
    # ... add all major venues
}
```

**Qualitative Usage (GPT-5):**
- Context: "Race at Flemington, known for wide turns and outside barrier advantage..."
- Reasoning: "Horse X has 3 wins from 5 starts at Flemington (60% strike rate)"
- Output: Venue familiarity adjustment (+5-8% if strong venue record)

**Quantitative Features:**
- `venue` (categorical, one-hot encoded)
- `venue_class` (categorical: metro, provincial, country)
- `horse_venue_win_pct` (numeric: horse's win % at this venue)
- `horse_venue_starts` (numeric: count of starts at venue)
- `jockey_venue_win_pct` (numeric: jockey's win % at this venue)
- `trainer_venue_win_pct` (numeric: trainer's win % at this venue)

**Feature Engineering:**
```python
def engineer_venue_features(venue, horse_history, jockey_stats, trainer_stats):
    """Create venue-related features"""
    features = {}

    # Venue metadata
    venue_data = VENUE_DATABASE.get(venue, {})
    features['venue'] = venue
    features['venue_class'] = venue_data.get('class', 'unknown')
    features['venue_state'] = venue_data.get('state', 'unknown')

    # Horse venue performance
    venue_starts = [r for r in horse_history if r['venue'] == venue]
    if venue_starts:
        wins = sum(1 for r in venue_starts if r['position'] == 1)
        features['horse_venue_win_pct'] = wins / len(venue_starts)
        features['horse_venue_starts'] = len(venue_starts)
    else:
        features['horse_venue_win_pct'] = 0
        features['horse_venue_starts'] = 0

    # Jockey venue performance
    features['jockey_venue_win_pct'] = jockey_stats.get(f'{venue}_win_pct', 0)

    # Trainer venue performance
    features['trainer_venue_win_pct'] = trainer_stats.get(f'{venue}_win_pct', 0)

    return features
```

**Data Schema:**
```python
venue_schema = {
    "venue": str,                    # "flemington"
    "venue_display": str,            # "Flemington"
    "venue_class": str,              # "metro" | "provincial" | "country"
    "venue_state": str,              # "VIC" | "NSW" | "QLD" | "SA" | "WA"
    "track_type": str,               # "turf" | "synthetic"
    "venue_metadata": dict           # Full venue details from VENUE_DATABASE
}
```

---

#### 1.3 Race Date & Time
**Description:** When the race is run (date, time, timezone)
**Data Type:** DateTime (ISO 8601)
**Prediction Impact:** 1-3% (seasonal patterns, time-of-day effects)

**Sources:**
- Racing.com form guide (Tier 1, 100% coverage, free)
- Tab.com.au race card (Tier 3, 100% coverage, free)

**Access Method:**
```python
from datetime import datetime
import pytz

def extract_race_datetime(race_url):
    """Extract race date and time"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract date from URL or page
    date_str = soup.find('span', class_='race-date').text  # "28 Dec 2024"
    time_str = soup.find('span', class_='race-time').text  # "3:45 PM"

    # Parse to datetime
    datetime_str = f"{date_str} {time_str}"
    race_datetime = datetime.strptime(datetime_str, "%d %b %Y %I:%M %p")

    # Add timezone (Australian Eastern Time)
    tz = pytz.timezone('Australia/Sydney')
    race_datetime = tz.localize(race_datetime)

    return race_datetime
```

**Qualitative Usage (GPT-5):**
- Context: "Race scheduled for 3:45 PM on December 28, 2024..."
- Reasoning: "Summer racing at Flemington, potential heat factor..."
- Output: Minimal direct impact, but informs weather analysis (Category 3)

**Quantitative Features:**
- `race_date` (date object)
- `race_time` (time object)
- `race_datetime` (datetime object, timezone-aware)
- `day_of_week` (categorical: Monday-Sunday)
- `month` (numeric: 1-12)
- `season` (categorical: summer, autumn, winter, spring)
- `is_weekend` (binary: Saturday/Sunday = 1)
- `time_of_day` (categorical: morning, afternoon, evening, night)

**Feature Engineering:**
```python
def engineer_datetime_features(race_datetime):
    """Create datetime-related features"""
    features = {}

    # Basic components
    features['race_date'] = race_datetime.date()
    features['race_time'] = race_datetime.time()
    features['day_of_week'] = race_datetime.strftime('%A')
    features['month'] = race_datetime.month

    # Season (Australian)
    month = race_datetime.month
    if month in [12, 1, 2]:
        features['season'] = 'summer'
    elif month in [3, 4, 5]:
        features['season'] = 'autumn'
    elif month in [6, 7, 8]:
        features['season'] = 'winter'
    else:
        features['season'] = 'spring'

    # Weekend flag
    features['is_weekend'] = 1 if race_datetime.weekday() >= 5 else 0

    # Time of day
    hour = race_datetime.hour
    if hour < 12:
        features['time_of_day'] = 'morning'
    elif hour < 17:
        features['time_of_day'] = 'afternoon'
    elif hour < 20:
        features['time_of_day'] = 'evening'
    else:
        features['time_of_day'] = 'night'

    return features
```

**Data Schema:**
```python
datetime_schema = {
    "race_datetime": datetime,       # 2024-12-28T15:45:00+11:00
    "race_date": str,                # "2024-12-28"
    "race_time": str,                # "15:45"
    "timezone": str,                 # "Australia/Sydney"
    "day_of_week": str,              # "Saturday"
    "month": int,                    # 12
    "season": str                    # "summer"
}
```

---

## CATEGORY 2: RACE TYPE & CLASS

### Overview
- **Category ID:** 2
- **Prediction Power:** 5-12% (race class impacts quality and competitiveness)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 1
- **Cost per Race:** $0 (public data)
- **ChatGPT Access:** 90%
- **Our Target Access:** 100%

### Subcategories

#### 2.1 Race Type/Class
**Description:** Race classification (Group 1, Listed, Open Handicap, Maiden, etc.)
**Data Type:** String (categorical, hierarchical)
**Prediction Impact:** 8-12% (class affects field quality and competitiveness)

**Race Class Hierarchy:**
```python
RACE_CLASS_HIERARCHY = {
    'Group 1': {
        'tier': 1,
        'prestige': 100,
        'prize_money_min': 500000,
        'quality': 'elite'
    },
    'Group 2': {
        'tier': 2,
        'prestige': 90,
        'prize_money_min': 200000,
        'quality': 'elite'
    },
    'Group 3': {
        'tier': 3,
        'prestige': 80,
        'prize_money_min': 150000,
        'quality': 'high'
    },
    'Listed': {
        'tier': 4,
        'prestige': 70,
        'prize_money_min': 100000,
        'quality': 'high'
    },
    'Open Handicap': {
        'tier': 5,
        'prestige': 50,
        'prize_money_min': 50000,
        'quality': 'medium'
    },
    'Benchmark 78': {
        'tier': 6,
        'prestige': 40,
        'prize_money_min': 30000,
        'quality': 'medium'
    },
    'Maiden': {
        'tier': 7,
        'prestige': 20,
        'prize_money_min': 20000,
        'quality': 'low'
    },
    'Class 1': {
        'tier': 8,
        'prestige': 10,
        'prize_money_min': 15000,
        'quality': 'low'
    }
}
```

**Sources:**
- Racing.com form guide (Tier 1, 100% coverage, free)
- Tab.com.au race card (Tier 3, 100% coverage, free)
- Punters.com.au (Tier 2, 100% coverage, subscription)

**Access Method:**
```python
def extract_race_class(race_url):
    """Extract race class/type"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Look for race class in title or metadata
    race_title = soup.find('h1', class_='race-title').text

    # Pattern matching for class
    if 'Group 1' in race_title or 'Gr1' in race_title:
        return 'Group 1'
    elif 'Group 2' in race_title or 'Gr2' in race_title:
        return 'Group 2'
    elif 'Group 3' in race_title or 'Gr3' in race_title:
        return 'Group 3'
    elif 'Listed' in race_title:
        return 'Listed'
    elif 'BM' in race_title or 'Benchmark' in race_title:
        # Extract benchmark number (e.g., "BM78")
        import re
        match = re.search(r'BM(\d+)', race_title)
        if match:
            return f'Benchmark {match.group(1)}'
    elif 'Maiden' in race_title:
        return 'Maiden'
    elif 'Class' in race_title:
        match = re.search(r'Class (\d+)', race_title)
        if match:
            return f'Class {match.group(1)}'
    else:
        return 'Open Handicap'  # Default
```

**Qualitative Usage (GPT-5):**
- Context: "This is a Group 1 race at Flemington, elite level competition..."
- Reasoning: "Horse X stepping up from Benchmark 78 to Group 3 (class rise)"
- Output: Class adjustment (+10-15% if dropping in class, -8-12% if rising)

**Quantitative Features:**
- `race_class` (categorical)
- `race_class_tier` (numeric: 1-8, lower = higher prestige)
- `race_prestige_score` (numeric: 0-100)
- `prize_money` (numeric: dollars)
- `horse_class_vs_race` (derived: horse's typical class vs this race)
- `is_class_drop` (binary: 1 if horse dropping in class)
- `is_class_rise` (binary: 1 if horse rising in class)

**Feature Engineering:**
```python
def engineer_race_class_features(race_class, prize_money, horse_typical_class):
    """Create race class features"""
    features = {}

    # Race class metadata
    class_data = RACE_CLASS_HIERARCHY.get(race_class, {})
    features['race_class'] = race_class
    features['race_class_tier'] = class_data.get('tier', 5)
    features['race_prestige_score'] = class_data.get('prestige', 50)
    features['prize_money'] = prize_money

    # Horse class comparison
    horse_class_tier = RACE_CLASS_HIERARCHY.get(horse_typical_class, {}).get('tier', 5)
    features['horse_typical_class_tier'] = horse_class_tier

    # Class drop/rise
    if horse_class_tier > features['race_class_tier']:
        features['is_class_drop'] = 1
        features['is_class_rise'] = 0
        features['class_movement'] = horse_class_tier - features['race_class_tier']
    elif horse_class_tier < features['race_class_tier']:
        features['is_class_drop'] = 0
        features['is_class_rise'] = 1
        features['class_movement'] = features['race_class_tier'] - horse_class_tier
    else:
        features['is_class_drop'] = 0
        features['is_class_rise'] = 0
        features['class_movement'] = 0

    return features
```

**Data Schema:**
```python
race_class_schema = {
    "race_class": str,               # "Group 1"
    "race_class_tier": int,          # 1 (1-8 scale)
    "race_class_short": str,         # "G1"
    "prestige_score": int,           # 100 (0-100 scale)
    "quality_level": str             # "elite" | "high" | "medium" | "low"
}
```

---

#### 2.2 Prize Money
**Description:** Total prize pool for the race (AUD)
**Data Type:** Integer (dollars)
**Prediction Impact:** 3-5% (higher prize = stronger fields, class proxy)

**Sources:**
- Racing.com form guide (Tier 1, 100% coverage, free)
- Tab.com.au race card (Tier 3, 100% coverage, free)

**Access Method:**
```python
def extract_prize_money(race_url):
    """Extract total prize money"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    prize_element = soup.find('span', class_='prize-money')
    prize_text = prize_element.text  # e.g., "$500,000" or "$50K"

    # Parse to integer
    prize_text = prize_text.replace('$', '').replace(',', '')

    if 'K' in prize_text:
        prize_value = float(prize_text.replace('K', '')) * 1000
    elif 'M' in prize_text:
        prize_value = float(prize_text.replace('M', '')) * 1000000
    else:
        prize_value = float(prize_text)

    return int(prize_value)
```

**Qualitative Usage (GPT-5):**
- Context: "Race worth $500,000 total prize money, attracting strong field..."
- Reasoning: "High prize money suggests quality opposition"
- Output: Field strength context (minimal direct adjustment)

**Quantitative Features:**
- `prize_money_total` (numeric: dollars)
- `prize_money_log` (numeric: log transformation for modeling)
- `prize_money_category` (categorical: <$50k, $50k-$100k, $100k-$250k, >$250k)
- `prize_to_winner` (numeric: first place prize, usually ~60% of total)

**Feature Engineering:**
```python
def engineer_prize_money_features(prize_money_total):
    """Create prize money features"""
    import math

    features = {}

    # Raw prize money
    features['prize_money_total'] = prize_money_total

    # Log transformation (for linear models)
    features['prize_money_log'] = math.log(prize_money_total + 1)

    # Category
    if prize_money_total < 50000:
        features['prize_money_category'] = 'low'
    elif prize_money_total < 100000:
        features['prize_money_category'] = 'medium'
    elif prize_money_total < 250000:
        features['prize_money_category'] = 'high'
    else:
        features['prize_money_category'] = 'elite'

    # Winner's share (approximately 60%)
    features['prize_to_winner'] = int(prize_money_total * 0.6)

    return features
```

---

#### 2.3 Field Size
**Description:** Number of horses competing
**Data Type:** Integer (count)
**Prediction Impact:** 3-5% (larger fields = more competitive, harder to win)

**Sources:**
- Racing.com form guide (Tier 1, 100% coverage, free)

**Access Method:**
```python
def extract_field_size(race_url):
    """Extract number of horses in race"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Count horse rows in form guide
    horse_rows = soup.find_all('div', class_='horse-row')
    field_size = len(horse_rows)

    return field_size
```

**Qualitative Usage (GPT-5):**
- Context: "Field of 16 runners, large competitive field..."
- Reasoning: "Harder to win with 16 runners vs small field of 8"
- Output: Field size context (affects win probability baseline)

**Quantitative Features:**
- `field_size` (numeric: count of starters)
- `field_size_category` (categorical: small <10, medium 10-14, large >14)
- `baseline_win_probability` (derived: 1/field_size)

**Feature Engineering:**
```python
def engineer_field_size_features(field_size):
    """Create field size features"""
    features = {}

    # Raw field size
    features['field_size'] = field_size

    # Category
    if field_size < 10:
        features['field_size_category'] = 'small'
    elif field_size <= 14:
        features['field_size_category'] = 'medium'
    else:
        features['field_size_category'] = 'large'

    # Baseline win probability
    features['baseline_win_probability'] = 1 / field_size

    return features
```

**Data Schema:**
```python
field_size_schema = {
    "field_size": int,                      # 16
    "field_size_category": str,             # "large"
    "acceptances": int,                     # 18 (before scratchings)
    "scratchings": int,                     # 2 (horses withdrawn)
    "emergencies": int                      # 2 (horses on standby)
}
```

---

## INTEGRATION GUIDELINES

### Cross-Category Dependencies

**Category 1-2 Integration with Other Categories:**

1. **With Category 3 (Track Conditions):**
   - Venue + season → expected track condition
   - Flemington summer → typically Good/Firm
   - Randwick winter → often Soft/Heavy

2. **With Category 4 (Barrier Draw):**
   - Venue + distance → barrier bias patterns
   - Flemington 1200m → outside barriers (8-12) favored
   - Randwick 2400m → inside barriers (1-4) favored

3. **With Category 8 (Pace Scenario):**
   - Field size + race class → pace pressure
   - Large field (>14) + Open Handicap → high pace pressure
   - Small field (<10) + Group 1 → tactical pace

4. **With Category 14 (Historical Performance):**
   - Distance + venue → horse's venue/distance record
   - Horse's win % at Flemington 1600m

5. **With Category 19 (Class Ratings - NEW):**
   - Race class → expected class rating range
   - Group 1 → ratings 110-120+
   - Benchmark 78 → ratings 70-85

### Data Collection Order

**Priority Order for Categories 1-2:**
1. Extract venue (needed for all subsequent analysis)
2. Extract distance (needed for pace, barrier bias)
3. Extract race datetime (needed for weather forecast)
4. Extract race class (needed for field quality assessment)
5. Extract prize money (supplementary context)
6. Extract field size (needed for pace scenario, win probability)

### Validation Rules

**Category 1-2 Validation:**
```python
def validate_basic_race_info(race_data):
    """Validate categories 1-2 data"""
    errors = []
    warnings = []

    # Distance validation
    if race_data['distance_meters'] < 1000:
        errors.append("Distance too short (<1000m), verify data")
    if race_data['distance_meters'] > 3200:
        warnings.append("Distance unusually long (>3200m), verify data")

    # Venue validation
    if race_data['venue'] not in VENUE_DATABASE:
        warnings.append(f"Unknown venue: {race_data['venue']}, add to database")

    # Race datetime validation
    if race_data['race_datetime'] < datetime.now():
        warnings.append("Race is in the past, historical analysis mode")

    # Race class validation
    if race_data['race_class'] not in RACE_CLASS_HIERARCHY:
        warnings.append(f"Unknown race class: {race_data['race_class']}")

    # Prize money validation
    expected_prize = RACE_CLASS_HIERARCHY.get(race_data['race_class'], {}).get('prize_money_min', 0)
    if race_data['prize_money_total'] < expected_prize * 0.7:
        warnings.append(f"Prize money lower than expected for {race_data['race_class']}")

    # Field size validation
    if race_data['field_size'] < 4:
        warnings.append("Very small field (<4), verify acceptances")
    if race_data['field_size'] > 20:
        warnings.append("Very large field (>20), unusual")

    return {'errors': errors, 'warnings': warnings}
```

### Cost Analysis

**Categories 1-2 Cost Breakdown:**
- **Data Sources:** All free (Racing.com, Tab.com.au public pages)
- **API Calls:** 0 (web scraping sufficient)
- **Authentication Required:** No
- **Processing Time:** <5 seconds per race
- **Storage:** ~500 bytes per race (minimal)

**Total Cost:** $0 per race

---

## UNIFIED DATA MODEL

### Complete Schema for Categories 1-2

```python
basic_race_info_schema = {
    # Category 1: Race Metadata
    "distance": {
        "meters": int,
        "furlongs": float,
        "category": str,
        "text": str
    },
    "venue": {
        "name": str,
        "display_name": str,
        "state": str,
        "class": str,
        "metadata": dict
    },
    "datetime": {
        "race_datetime": datetime,
        "date": str,
        "time": str,
        "timezone": str,
        "day_of_week": str,
        "month": int,
        "season": str,
        "is_weekend": bool
    },

    # Category 2: Race Type & Class
    "race_class": {
        "class_name": str,
        "class_tier": int,
        "prestige_score": int,
        "quality_level": str,
        "class_short": str
    },
    "prize_money": {
        "total": int,
        "to_winner": int,
        "category": str,
        "currency": str
    },
    "field": {
        "size": int,
        "acceptances": int,
        "scratchings": int,
        "emergencies": int,
        "baseline_win_prob": float
    }
}
```

### Example Complete Record

```python
example_race = {
    "distance": {
        "meters": 1600,
        "furlongs": 8.0,
        "category": "mile",
        "text": "1600m"
    },
    "venue": {
        "name": "flemington",
        "display_name": "Flemington",
        "state": "VIC",
        "class": "metro",
        "metadata": VENUE_DATABASE['flemington']
    },
    "datetime": {
        "race_datetime": datetime(2024, 12, 28, 15, 45, tzinfo=pytz.timezone('Australia/Sydney')),
        "date": "2024-12-28",
        "time": "15:45",
        "timezone": "Australia/Sydney",
        "day_of_week": "Saturday",
        "month": 12,
        "season": "summer",
        "is_weekend": True
    },
    "race_class": {
        "class_name": "Group 1",
        "class_tier": 1,
        "prestige_score": 100,
        "quality_level": "elite",
        "class_short": "G1"
    },
    "prize_money": {
        "total": 500000,
        "to_winner": 300000,
        "category": "elite",
        "currency": "AUD"
    },
    "field": {
        "size": 16,
        "acceptances": 18,
        "scratchings": 2,
        "emergencies": 2,
        "baseline_win_prob": 0.0625
    }
}
```

---

## IMPLEMENTATION CHECKLIST

### Phase 1 Week 1: Categories 1-2 Implementation

**Day 1-2: Data Collection Setup**
- [ ] Implement `extract_race_distance()`
- [ ] Implement `extract_venue()`
- [ ] Implement `extract_race_datetime()`
- [ ] Build VENUE_DATABASE with all major tracks
- [ ] Test extraction on 5 sample races

**Day 3-4: Race Class & Prize Money**
- [ ] Implement `extract_race_class()`
- [ ] Build RACE_CLASS_HIERARCHY dictionary
- [ ] Implement `extract_prize_money()`
- [ ] Implement `extract_field_size()`
- [ ] Test on Group 1-3, Listed, Benchmark races

**Day 5: Feature Engineering**
- [ ] Implement all feature engineering functions
- [ ] Create unified data schema
- [ ] Build validation rules
- [ ] Test integration with mock data

**Day 6: Testing & Validation**
- [ ] Run on 20+ historical races
- [ ] Validate data quality (no errors/warnings)
- [ ] Benchmark extraction speed (<5 sec/race)
- [ ] Document any edge cases

**Day 7: Integration Preparation**
- [ ] Export data to unified format (JSON/DataFrame)
- [ ] Prepare interfaces for Categories 3-7
- [ ] Create quick reference lookup functions
- [ ] Ready for Phase 1 Week 2 (Track Conditions)

---

**Document Complete: Categories 1-2 (Basic Race Information)**
**Next Document: PART_02_CATEGORY_03.md (Track Conditions with enhanced numerical subcategories)**
