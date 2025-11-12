# Master Taxonomy - Part 2: Category 3 (Track Conditions)

**Document Purpose:** Implementation reference for track condition assessment and impact analysis
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (feature engineering)
**Implementation Priority:** Phase 1 Week 1 (foundational environmental data)

---

## CATEGORY 3: TRACK CONDITIONS

### Overview
- **Category ID:** 3
- **Prediction Power:** 10-18% (significant impact on race outcomes)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 1
- **Cost per Race:** $0 (free weather API + track reports)
- **ChatGPT Access:** 70% (has track condition, limited weather context)
- **Our Target Access:** 100% (real-time weather + detailed track analysis)

### Enhanced Quantitative Coverage
**Status:** ⚠️ Needs Enhancement (currently qualitative-heavy, need numerical indices)

**Enhancements Added:**
1. Track condition index (1-10 numerical scale)
2. Performance-on-rating (horse historical performance by track condition)
3. Weather impact scores (temperature, humidity, wind effects)
4. Track bias quantification (rail position, inside/outside advantages)

---

## SUBCATEGORIES

### 3.1 Official Track Condition Rating
**Description:** Official track condition classification (Firm, Good, Soft, Heavy)
**Data Type:** String (categorical, ordinal)
**Prediction Impact:** 12-18% (horses have strong preferences)

**Track Condition Scale:**
```python
TRACK_CONDITION_SCALE = {
    'Firm 1': {
        'numeric_index': 1,
        'moisture': 'very_low',
        'penetrometer': '5.5+',
        'description': 'Extremely hard and dry',
        'speed_rating': 100,  # Baseline speed
        'favors': 'on_pace_runners'
    },
    'Firm 2': {
        'numeric_index': 2,
        'moisture': 'low',
        'penetrometer': '5.0-5.5',
        'description': 'Hard and firm',
        'speed_rating': 99,
        'favors': 'on_pace_runners'
    },
    'Good 3': {
        'numeric_index': 3,
        'moisture': 'ideal',
        'penetrometer': '4.5-5.0',
        'description': 'Ideal racing conditions',
        'speed_rating': 100,
        'favors': 'balanced'
    },
    'Good 4': {
        'numeric_index': 4,
        'moisture': 'moderate',
        'penetrometer': '4.0-4.5',
        'description': 'Slight give in track',
        'speed_rating': 98,
        'favors': 'balanced'
    },
    'Soft 5': {
        'numeric_index': 5,
        'moisture': 'moderate_high',
        'penetrometer': '3.5-4.0',
        'description': 'Noticeable give',
        'speed_rating': 95,
        'favors': 'strong_finishers'
    },
    'Soft 6': {
        'numeric_index': 6,
        'moisture': 'high',
        'penetrometer': '3.0-3.5',
        'description': 'Significantly softer',
        'speed_rating': 92,
        'favors': 'strong_finishers'
    },
    'Soft 7': {
        'numeric_index': 7,
        'moisture': 'very_high',
        'penetrometer': '2.5-3.0',
        'description': 'Quite wet',
        'speed_rating': 88,
        'favors': 'mudlarks'
    },
    'Heavy 8': {
        'numeric_index': 8,
        'moisture': 'saturated',
        'penetrometer': '2.0-2.5',
        'description': 'Very wet and testing',
        'speed_rating': 83,
        'favors': 'mudlarks'
    },
    'Heavy 9': {
        'numeric_index': 9,
        'moisture': 'saturated_plus',
        'penetrometer': '1.5-2.0',
        'description': 'Extremely wet',
        'speed_rating': 78,
        'favors': 'mudlarks'
    },
    'Heavy 10': {
        'numeric_index': 10,
        'moisture': 'waterlogged',
        'penetrometer': '<1.5',
        'description': 'Rare, near unraceable',
        'speed_rating': 70,
        'favors': 'specialist_mudlarks'
    }
}
```

**Sources:**
- Racing.com official track report (Tier 1, 100% coverage, free, posted ~30 min before first race)
- Tab.com.au race card (Tier 3, 90% coverage, free)
- BOM weather API (Tier 1, 100% coverage, free, for forecasting)

**Access Method:**
```python
def extract_track_condition(race_url, venue, race_datetime):
    """Extract official track condition rating"""
    # Method 1: Racing.com official report
    track_report_url = f"https://racing.com/track-report/{venue}/{race_datetime.date()}"
    response = requests.get(track_report_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    condition_element = soup.find('span', class_='track-condition')
    if condition_element:
        condition_text = condition_element.text.strip()  # e.g., "Good 4"
        return parse_track_condition(condition_text)

    # Method 2: Parse from race page (fallback)
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    condition_element = soup.find('div', class_='race-conditions')
    if condition_element:
        condition_text = condition_element.text
        return parse_track_condition(condition_text)

    # Method 3: Forecast from weather (if race is future)
    if race_datetime > datetime.now():
        return forecast_track_condition(venue, race_datetime)

    return None

def parse_track_condition(condition_text):
    """Parse track condition string to structured data"""
    import re

    # Extract condition and rating (e.g., "Good 4")
    match = re.search(r'(Firm|Good|Soft|Heavy)\s*(\d+)?', condition_text, re.IGNORECASE)
    if match:
        condition = match.group(1).capitalize()
        rating = int(match.group(2)) if match.group(2) else None

        # Build full condition string
        if rating:
            full_condition = f"{condition} {rating}"
        else:
            # Default ratings if not specified
            defaults = {'Firm': 2, 'Good': 3, 'Soft': 5, 'Heavy': 8}
            rating = defaults.get(condition, 3)
            full_condition = f"{condition} {rating}"

        # Get metadata
        condition_data = TRACK_CONDITION_SCALE.get(full_condition, {})

        return {
            'condition': condition,
            'rating': rating,
            'full_condition': full_condition,
            'numeric_index': condition_data.get('numeric_index', rating),
            'speed_rating': condition_data.get('speed_rating', 100),
            'favors': condition_data.get('favors', 'balanced'),
            'moisture': condition_data.get('moisture', 'unknown')
        }

    return None
```

**Qualitative Usage (GPT-5):**
- Context: "Track rated Good 4, ideal racing conditions with slight give..."
- Reasoning: "Horse X has 4 wins from 6 starts on Good tracks (67% win rate vs 30% overall)"
- Output: Track condition adjustment (+15-20% if strong track preference match)

**Quantitative Features:**
- `track_condition` (categorical: Firm/Good/Soft/Heavy)
- `track_condition_rating` (numeric: 1-10)
- `track_condition_index` (numeric: 1-10, same as rating)
- `track_speed_rating` (numeric: 70-100, expected race pace)
- `horse_track_condition_win_pct` (numeric: horse's win % on this condition)
- `horse_track_condition_starts` (numeric: experience on this condition)
- `track_condition_preference` (derived: horse's best condition)
- `is_preferred_condition` (binary: 1 if racing on preferred condition)

**Feature Engineering:**
```python
def engineer_track_condition_features(track_condition_data, horse_history):
    """Create track condition features"""
    features = {}

    # Base track condition
    features['track_condition'] = track_condition_data['condition']
    features['track_condition_rating'] = track_condition_data['rating']
    features['track_condition_index'] = track_condition_data['numeric_index']
    features['track_speed_rating'] = track_condition_data['speed_rating']

    # Horse's performance on this condition
    condition_category = track_condition_data['condition']  # Firm/Good/Soft/Heavy
    condition_starts = [r for r in horse_history
                       if r['track_condition'].startswith(condition_category)]

    if condition_starts:
        wins = sum(1 for r in condition_starts if r['position'] == 1)
        features['horse_track_condition_win_pct'] = wins / len(condition_starts)
        features['horse_track_condition_starts'] = len(condition_starts)
    else:
        features['horse_track_condition_win_pct'] = 0
        features['horse_track_condition_starts'] = 0

    # Calculate horse's preferred condition
    condition_performance = {}
    for condition in ['Firm', 'Good', 'Soft', 'Heavy']:
        starts = [r for r in horse_history if r['track_condition'].startswith(condition)]
        if starts:
            wins = sum(1 for r in starts if r['position'] == 1)
            condition_performance[condition] = wins / len(starts)

    if condition_performance:
        best_condition = max(condition_performance, key=condition_performance.get)
        features['track_condition_preference'] = best_condition
        features['is_preferred_condition'] = 1 if condition_category == best_condition else 0
    else:
        features['track_condition_preference'] = 'unknown'
        features['is_preferred_condition'] = 0

    return features
```

---

### 3.2 Weather Conditions
**Description:** Current and forecast weather (temperature, humidity, wind, rainfall)
**Data Type:** Mixed (numeric + categorical)
**Prediction Impact:** 5-10% (affects track condition and horse comfort)

**Weather Data Sources:**
- Bureau of Meteorology (BOM) API (Tier 1, free, official)
- Racing.com weather widget (Tier 1, free, integrated)

**BOM API Integration:**
```python
import requests

def get_weather_forecast(venue, race_datetime):
    """Get weather forecast from BOM API"""
    # Get venue coordinates
    venue_coords = VENUE_DATABASE[venue]['coordinates']
    lat, lon = venue_coords['lat'], venue_coords['lon']

    # BOM API endpoint (free, no auth required)
    bom_url = f"http://www.bom.gov.au/fwo/IDV60901/IDV60901.{get_bom_station_id(venue)}.json"

    response = requests.get(bom_url)
    weather_data = response.json()

    # Extract relevant forecast
    forecast = weather_data['observations']['data'][0]

    return {
        'temperature': forecast.get('air_temp', None),  # Celsius
        'apparent_temp': forecast.get('apparent_t', None),
        'humidity': forecast.get('rel_hum', None),  # Percentage
        'wind_speed': forecast.get('wind_spd_kmh', None),  # km/h
        'wind_direction': forecast.get('wind_dir', None),  # e.g., 'NW'
        'rainfall_24h': forecast.get('rain_trace', 0),  # mm in last 24h
        'conditions': forecast.get('weather', 'Unknown')  # e.g., 'Sunny', 'Cloudy'
    }

def get_bom_station_id(venue):
    """Map venue to nearest BOM weather station"""
    BOM_STATIONS = {
        'flemington': '95866',  # Melbourne Olympic Park
        'caulfield': '95866',   # Melbourne Olympic Park
        'randwick': '66062',    # Sydney Observatory Hill
        'rosehill': '66062',    # Sydney Observatory Hill
        # ... add all venues
    }
    return BOM_STATIONS.get(venue, '95866')
```

**Qualitative Usage (GPT-5):**
- Context: "Temperature 32°C, hot summer day, may affect stamina..."
- Reasoning: "High temperature can disadvantage horses with high cruising speeds (stamina drain)"
- Output: Weather context (affects fitness assessment in Category 16)

**Quantitative Features:**
- `temperature_celsius` (numeric: -5 to 45 range)
- `apparent_temperature` (numeric: feels-like temp)
- `humidity_percent` (numeric: 0-100)
- `wind_speed_kmh` (numeric: 0-80)
- `wind_direction` (categorical: N/NE/E/SE/S/SW/W/NW)
- `rainfall_24h_mm` (numeric: 0-100+)
- `weather_conditions` (categorical: Sunny/Cloudy/Rainy/Stormy)
- `is_extreme_heat` (binary: 1 if temp > 35°C)
- `is_extreme_cold` (binary: 1 if temp < 10°C)
- `is_windy` (binary: 1 if wind > 40 km/h)

**Feature Engineering:**
```python
def engineer_weather_features(weather_data):
    """Create weather features"""
    features = {}

    # Raw weather data
    features['temperature_celsius'] = weather_data['temperature']
    features['apparent_temperature'] = weather_data['apparent_temp']
    features['humidity_percent'] = weather_data['humidity']
    features['wind_speed_kmh'] = weather_data['wind_speed']
    features['wind_direction'] = weather_data['wind_direction']
    features['rainfall_24h_mm'] = weather_data['rainfall_24h']
    features['weather_conditions'] = weather_data['conditions']

    # Extreme conditions flags
    temp = weather_data['temperature']
    features['is_extreme_heat'] = 1 if temp > 35 else 0
    features['is_extreme_cold'] = 1 if temp < 10 else 0
    features['is_moderate_temp'] = 1 if 15 <= temp <= 28 else 0

    wind = weather_data['wind_speed']
    features['is_windy'] = 1 if wind > 40 else 0
    features['is_calm'] = 1 if wind < 10 else 0

    # Humidity categories
    humidity = weather_data['humidity']
    if humidity < 40:
        features['humidity_category'] = 'low'
    elif humidity < 70:
        features['humidity_category'] = 'moderate'
    else:
        features['humidity_category'] = 'high'

    # Comfort index (combined temp + humidity)
    features['comfort_index'] = calculate_comfort_index(temp, humidity)

    return features

def calculate_comfort_index(temp, humidity):
    """Calculate heat index / comfort score"""
    # Simplified heat index formula
    if temp < 27:
        return 100  # Comfortable

    # Heat index increases with temp + humidity
    heat_index = temp + (humidity / 100) * 10

    if heat_index < 30:
        return 95  # Mild discomfort
    elif heat_index < 35:
        return 85  # Moderate discomfort
    elif heat_index < 40:
        return 70  # Significant discomfort
    else:
        return 50  # Extreme discomfort
```

---

### 3.3 Track Bias
**Description:** Rail position and inside/outside running advantages
**Data Type:** String + Numeric (categorical + quantitative bias score)
**Prediction Impact:** 8-15% (can strongly favor inside or outside runners)

**Track Bias Categories:**
```python
TRACK_BIAS_TYPES = {
    'true': {
        'bias_score': 0,
        'description': 'No bias, all lanes equal',
        'strategy': 'Balanced approach'
    },
    'inside_favored': {
        'bias_score': -10,  # Negative = inside advantage
        'description': 'Inside lanes 1-6 advantaged',
        'strategy': 'Hold rail position'
    },
    'outside_favored': {
        'bias_score': +10,  # Positive = outside advantage
        'description': 'Outside lanes 8+ advantaged',
        'strategy': 'Race wide'
    },
    'leaders_track': {
        'bias_score': 0,
        'description': 'On-pace runners favored',
        'strategy': 'Settle forward'
    },
    'backmarkers_track': {
        'bias_score': 0,
        'description': 'Strong finishers favored',
        'strategy': 'Settle back, strong finish'
    }
}
```

**Rail Position Impact:**
```python
RAIL_POSITIONS = {
    'true': {
        'distance_from_fence': 0,
        'impact': 'neutral',
        'bias_multiplier': 1.0
    },
    'out_3m': {
        'distance_from_fence': 3,
        'impact': 'slight_outside_advantage',
        'bias_multiplier': 1.05
    },
    'out_6m': {
        'distance_from_fence': 6,
        'impact': 'moderate_outside_advantage',
        'bias_multiplier': 1.10
    },
    'out_9m': {
        'distance_from_fence': 9,
        'impact': 'significant_outside_advantage',
        'bias_multiplier': 1.15
    }
}
```

**Sources:**
- Racing.com track report (Tier 1, 90% coverage, posted morning of race day)
- Punters.com.au track analysis (Tier 2, 70% coverage, subscription)
- Historical bias analysis (Tier 1, internal database)

**Access Method:**
```python
def extract_track_bias(venue, race_date, track_condition):
    """Extract track bias information"""
    # Get official rail position
    track_report_url = f"https://racing.com/track-report/{venue}/{race_date}"
    response = requests.get(track_report_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    rail_element = soup.find('span', class_='rail-position')
    rail_text = rail_element.text if rail_element else "True"

    # Parse rail position
    rail_position = parse_rail_position(rail_text)

    # Get historical bias for venue + condition + rail
    historical_bias = get_historical_bias(venue, track_condition, rail_position)

    return {
        'rail_position': rail_position,
        'rail_distance_meters': RAIL_POSITIONS[rail_position]['distance_from_fence'],
        'bias_type': historical_bias['bias_type'],
        'bias_score': historical_bias['bias_score'],
        'bias_confidence': historical_bias['confidence']
    }

def get_historical_bias(venue, track_condition, rail_position):
    """Analyze historical data to determine bias"""
    # Query internal database for past races with same conditions
    query = f"""
    SELECT
        AVG(CASE WHEN barrier_position <= 6 THEN win_flag ELSE 0 END) as inside_win_rate,
        AVG(CASE WHEN barrier_position > 6 THEN win_flag ELSE 0 END) as outside_win_rate,
        AVG(CASE WHEN settling_position <= 4 THEN win_flag ELSE 0 END) as leader_win_rate,
        COUNT(*) as sample_size
    FROM race_results
    WHERE venue = '{venue}'
      AND track_condition LIKE '{track_condition}%'
      AND rail_position = '{rail_position}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 2 YEAR)
    """

    results = execute_query(query)

    if results['sample_size'] < 20:
        # Insufficient data
        return {
            'bias_type': 'unknown',
            'bias_score': 0,
            'confidence': 'low'
        }

    # Analyze win rates
    inside_win = results['inside_win_rate']
    outside_win = results['outside_win_rate']
    leader_win = results['leader_win_rate']

    # Determine bias
    if inside_win > outside_win * 1.3:
        bias_type = 'inside_favored'
        bias_score = -10 * (inside_win / outside_win - 1)
    elif outside_win > inside_win * 1.3:
        bias_type = 'outside_favored'
        bias_score = +10 * (outside_win / inside_win - 1)
    elif leader_win > 0.30:
        bias_type = 'leaders_track'
        bias_score = 0
    else:
        bias_type = 'true'
        bias_score = 0

    return {
        'bias_type': bias_type,
        'bias_score': round(bias_score, 2),
        'confidence': 'high' if results['sample_size'] > 50 else 'medium'
    }
```

**Qualitative Usage (GPT-5):**
- Context: "Rail out 6m, historically favors outside barriers at Flemington 1200m..."
- Reasoning: "Horse X drawn barrier 12 (outside), suits track bias today"
- Output: Track bias adjustment (+8-12% if barrier suits bias)

**Quantitative Features:**
- `rail_position` (categorical: true/out_3m/out_6m/out_9m)
- `rail_distance_meters` (numeric: 0, 3, 6, 9)
- `track_bias_type` (categorical: true/inside_favored/outside_favored/leaders_track)
- `track_bias_score` (numeric: -20 to +20, negative=inside, positive=outside)
- `bias_confidence` (categorical: low/medium/high)
- `barrier_bias_match` (binary: 1 if horse's barrier suits bias)

**Feature Engineering:**
```python
def engineer_track_bias_features(track_bias_data, barrier_position):
    """Create track bias features"""
    features = {}

    # Base bias data
    features['rail_position'] = track_bias_data['rail_position']
    features['rail_distance_meters'] = track_bias_data['rail_distance_meters']
    features['track_bias_type'] = track_bias_data['bias_type']
    features['track_bias_score'] = track_bias_data['bias_score']
    features['bias_confidence'] = track_bias_data['bias_confidence']

    # Barrier-bias interaction
    bias_type = track_bias_data['bias_type']
    barrier = barrier_position

    if bias_type == 'inside_favored' and barrier <= 6:
        features['barrier_bias_match'] = 1
        features['bias_advantage'] = abs(track_bias_data['bias_score'])
    elif bias_type == 'outside_favored' and barrier > 6:
        features['barrier_bias_match'] = 1
        features['bias_advantage'] = abs(track_bias_data['bias_score'])
    else:
        features['barrier_bias_match'] = 0
        features['bias_advantage'] = 0

    return features
```

---

## INTEGRATION GUIDELINES

### Cross-Category Dependencies

**Category 3 Integration with Other Categories:**

1. **With Category 2 (Race Type):**
   - Track condition + race class → field quality assessment
   - Heavy track + Group 1 → elite horses may scratch
   - Good track + Maiden → full field likely

2. **With Category 4 (Barrier Draw):**
   - Track bias + barrier position → barrier advantage/disadvantage
   - Inside bias + barrier 1-3 → significant advantage
   - Outside bias + barrier 10+ → advantage

3. **With Category 8 (Pace Scenario):**
   - Track condition + pace → stamina demands
   - Heavy track + fast pace → extreme stamina test
   - Firm track + slow pace → sprint finish likely

4. **With Category 14 (Historical Performance):**
   - Horse's track condition preference + today's condition → suitability
   - Horse 60% win rate on Soft + Soft 5 today → strong suit

5. **With Category 16 (Intangibles):**
   - Weather + horse fitness → comfort/stress factors
   - Extreme heat + horse returning from spell → potential issue

### Validation Rules

**Category 3 Validation:**
```python
def validate_track_conditions(track_data, weather_data):
    """Validate category 3 data"""
    errors = []
    warnings = []

    # Track condition validation
    if track_data['track_condition_index'] < 1 or track_data['track_condition_index'] > 10:
        errors.append("Track condition index out of range (1-10)")

    # Weather-track condition consistency
    if weather_data['rainfall_24h_mm'] > 20 and track_data['track_condition_index'] < 4:
        warnings.append("Heavy rain but track rated Good/Firm, verify track report")

    if weather_data['rainfall_24h_mm'] == 0 and track_data['track_condition_index'] > 6:
        warnings.append("No rain but track rated Soft/Heavy, check for irrigation")

    # Temperature validation
    if weather_data['temperature_celsius'] < -5 or weather_data['temperature_celsius'] > 50:
        errors.append("Temperature out of realistic range")

    # Rail position validation
    if track_data['rail_distance_meters'] > 15:
        warnings.append("Rail position extremely wide (>15m), verify")

    return {'errors': errors, 'warnings': warnings}
```

### Data Collection Priority

**Phase 1 Week 1 Implementation Order:**
1. Official track condition (critical, check 30min before race)
2. Rail position (critical, check morning of race)
3. Weather forecast (important, check 24h before + 2h before race)
4. Historical track bias (medium, pre-computed database)

---

## UNIFIED DATA MODEL

### Complete Schema for Category 3

```python
track_conditions_schema = {
    # 3.1 Track Condition
    "track_condition": {
        "condition": str,              # "Good"
        "rating": int,                 # 4
        "full_condition": str,         # "Good 4"
        "numeric_index": int,          # 4 (1-10 scale)
        "speed_rating": int,           # 98 (70-100 scale)
        "favors": str,                 # "balanced"
        "moisture": str                # "moderate"
    },

    # 3.2 Weather
    "weather": {
        "temperature_celsius": float,
        "apparent_temperature": float,
        "humidity_percent": int,
        "wind_speed_kmh": float,
        "wind_direction": str,
        "rainfall_24h_mm": float,
        "conditions": str,
        "comfort_index": int,
        "is_extreme_heat": bool,
        "is_windy": bool
    },

    # 3.3 Track Bias
    "track_bias": {
        "rail_position": str,
        "rail_distance_meters": int,
        "bias_type": str,
        "bias_score": float,
        "bias_confidence": str
    }
}
```

### Example Complete Record

```python
example_track_conditions = {
    "track_condition": {
        "condition": "Good",
        "rating": 4,
        "full_condition": "Good 4",
        "numeric_index": 4,
        "speed_rating": 98,
        "favors": "balanced",
        "moisture": "moderate"
    },
    "weather": {
        "temperature_celsius": 24.5,
        "apparent_temperature": 26.0,
        "humidity_percent": 65,
        "wind_speed_kmh": 15.0,
        "wind_direction": "NW",
        "rainfall_24h_mm": 0.0,
        "conditions": "Partly Cloudy",
        "comfort_index": 95,
        "is_extreme_heat": False,
        "is_windy": False
    },
    "track_bias": {
        "rail_position": "out_3m",
        "rail_distance_meters": 3,
        "bias_type": "outside_favored",
        "bias_score": 6.5,
        "bias_confidence": "high"
    }
}
```

---

## COST ANALYSIS

**Category 3 Cost Breakdown:**
- **BOM Weather API:** $0 (free, official government API)
- **Racing.com track reports:** $0 (free public data)
- **Historical bias database:** $0 (internal, pre-computed)
- **Processing time:** <10 seconds per race

**Total Cost:** $0 per race

---

## IMPLEMENTATION CHECKLIST

### Phase 1 Week 1: Category 3 Implementation

**Day 1: Track Condition Setup**
- [ ] Implement `extract_track_condition()`
- [ ] Build TRACK_CONDITION_SCALE dictionary
- [ ] Implement `parse_track_condition()`
- [ ] Test on 10 sample races

**Day 2: Weather Integration**
- [ ] Set up BOM API client
- [ ] Implement `get_weather_forecast()`
- [ ] Map all venues to BOM weather stations
- [ ] Test weather extraction for all major venues

**Day 3: Track Bias Analysis**
- [ ] Build historical bias database (query past 2 years)
- [ ] Implement `get_historical_bias()`
- [ ] Implement `extract_track_bias()`
- [ ] Validate bias patterns against known track characteristics

**Day 4: Feature Engineering**
- [ ] Implement all feature engineering functions
- [ ] Create derived features (comfort index, bias match, etc.)
- [ ] Test feature generation on sample dataset

**Day 5: Integration Testing**
- [ ] Test full Category 3 pipeline on 20 races
- [ ] Validate weather-track condition consistency
- [ ] Check bias confidence scores
- [ ] Document edge cases

---

**Document Complete: Category 3 (Track Conditions)**
**Next Document: PART_03_CATEGORY_04.md (Barrier Draw)**
