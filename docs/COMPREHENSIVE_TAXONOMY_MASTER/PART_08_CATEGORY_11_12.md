# Master Taxonomy - Part 8: Categories 11-12 (Jockey/Trainer Tactics & Market Data)

**Document Purpose:** Implementation reference for tactical patterns and betting market intelligence
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (feature engineering)
**Implementation Priority:** Phase 1 Week 4 (Category 11), Phase 1 Week 2 (Category 12)

---

## CATEGORY 11: JOCKEY/TRAINER TACTICS

### Overview
- **Category ID:** 11
- **Prediction Power:** 5-10% (tactical insights provide edge)
- **Pipeline Usage:** PRIMARILY Qualitative (tactical reasoning)
- **Priority Phase:** Phase 1 Week 4
- **Cost per Race:** $0 (derived from historical data)
- **ChatGPT Access:** 30% (limited tactical analysis)
- **Our Target Access:** 80% (comprehensive tactical database)

---

## SUBCATEGORIES

### 11.1 Jockey Riding Style
**Description:** Jockey's typical tactical approach (aggressive, patient, tactical)
**Data Type:** Categorical + Behavioral patterns
**Prediction Impact:** 5-8%

**Riding Style Categories:**
```python
RIDING_STYLES = {
    'aggressive': {
        'description': 'Pushes forward early, controls race',
        'typical_positions': [1, 2, 3],
        'suits_barriers': 'inside',
        'suits_pace': 'slow',
        'risk_profile': 'high'
    },
    'patient': {
        'description': 'Settles back, strong finish',
        'typical_positions': [8, 9, 10, 11, 12],
        'suits_barriers': 'wide',
        'suits_pace': 'fast',
        'risk_profile': 'medium'
    },
    'tactical': {
        'description': 'Adapts to race dynamics',
        'typical_positions': [4, 5, 6, 7],
        'suits_barriers': 'any',
        'suits_pace': 'any',
        'risk_profile': 'low'
    },
    'front_running': {
        'description': 'Leads or nothing',
        'typical_positions': [1, 2],
        'suits_barriers': 'inside',
        'suits_pace': 'slow',
        'risk_profile': 'very_high'
    }
}
```

**Calculate Jockey Riding Style:**
```python
def calculate_jockey_riding_style(jockey_name):
    """Analyze jockey's typical riding style from history"""

    query = f"""
    SELECT
        AVG(settling_position) as avg_settling,
        STDDEV(settling_position) as settling_std,
        AVG(CASE WHEN settling_position <= 3 THEN 1.0 ELSE 0.0 END) as forward_pct,
        AVG(CASE WHEN settling_position > 8 THEN 1.0 ELSE 0.0 END) as back_pct,
        COUNT(*) as rides
    FROM race_results
    WHERE jockey = '{jockey_name}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 1 YEAR)
    """

    result = execute_query(query)

    if result['rides'] < 50:
        return {
            'style': 'unknown',
            'confidence': 'low'
        }

    # Classify based on settling patterns
    avg_settling = result['avg_settling']
    forward_pct = result['forward_pct']
    back_pct = result['back_pct']
    settling_std = result['settling_std']

    if forward_pct > 0.6:
        style = 'aggressive'
    elif back_pct > 0.5:
        style = 'patient'
    elif settling_std > 4.0:
        style = 'tactical'  # High variance = adapts to race
    else:
        style = 'tactical'

    return {
        'style': style,
        'avg_settling_position': avg_settling,
        'forward_percentage': forward_pct,
        'back_percentage': back_pct,
        'consistency': settling_std,
        'confidence': 'high' if result['rides'] > 100 else 'medium'
    }
```

**Qualitative Usage (GPT-5):**
- Context: "Jockey is aggressive front-runner, will push forward from barrier 3..."
- Reasoning: "Aggressive style + inside barrier + slow pace = tactical advantage"
- Output: Tactical fit assessment (enhances confidence if jockey style suits race scenario)

---

### 11.2 Trainer Race Placement Strategy
**Description:** Trainer's pattern of placing horses in suitable races
**Data Type:** Derived tactical patterns
**Prediction Impact:** 4-7%

**Placement Strategy Analysis:**
```python
def analyze_trainer_placement_strategy(trainer_name, horse_name, race_conditions):
    """Analyze if trainer places horses strategically"""

    # Get trainer's historical placement patterns
    query = f"""
    SELECT
        horse,
        distance,
        track_condition,
        race_class,
        position,
        CASE WHEN position = 1 THEN 1 ELSE 0 END as won
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 2 YEAR)
    """

    results = execute_query(query)

    # Analyze: Does trainer place horses at optimal distances/conditions?
    placement_success = {}

    for result in results:
        key = (result['distance'], result['track_condition'])
        if key not in placement_success:
            placement_success[key] = {'starts': 0, 'wins': 0}
        placement_success[key]['starts'] += 1
        placement_success[key]['wins'] += result['won']

    # Calculate win rate for each distance/condition combo
    for key in placement_success:
        placement_success[key]['win_pct'] = (
            placement_success[key]['wins'] / placement_success[key]['starts']
        )

    # Check if current race matches trainer's strong placement patterns
    current_key = (race_conditions['distance'], race_conditions['track_condition'])

    if current_key in placement_success:
        data = placement_success[current_key]

        if data['win_pct'] > 0.20 and data['starts'] > 10:
            return {
                'placement_quality': 'strong',
                'trainer_win_pct_this_setup': data['win_pct'],
                'sample_size': data['starts'],
                'confidence': 'high'
            }

    return {
        'placement_quality': 'unknown',
        'trainer_win_pct_this_setup': None,
        'confidence': 'low'
    }
```

**Qualitative Usage (GPT-5):**
- Context: "Trainer has 25% strike rate placing horses at Flemington 1600m on Good tracks (12 wins from 48 starts)..."
- Reasoning: "Strong placement record suggests horse is well-suited to today's conditions"
- Output: Strategic placement confidence boost

---

### 11.3 Trainer-Jockey Partnership Tactics
**Description:** How specific trainer-jockey combinations operate tactically
**Data Type:** Partnership behavioral patterns
**Prediction Impact:** 3-5%

**Partnership Analysis:**
```python
def analyze_trainer_jockey_tactics(trainer_name, jockey_name):
    """Analyze tactical patterns of trainer-jockey partnership"""

    query = f"""
    SELECT
        AVG(settling_position) as avg_settling,
        AVG(finish_position) as avg_finish,
        AVG(CASE WHEN position = 1 THEN 1.0 ELSE 0.0 END) as win_pct,
        COUNT(*) as combinations
    FROM race_results
    WHERE trainer = '{trainer_name}'
      AND jockey = '{jockey_name}'
      AND race_date > DATE_SUB(NOW(), INTERVAL 2 YEAR)
    """

    result = execute_query(query)

    if result['combinations'] < 10:
        return {
            'partnership_established': False,
            'tactical_pattern': 'unknown'
        }

    # Analyze their tactical approach together
    avg_settling = result['avg_settling']

    if avg_settling <= 4:
        tactical_pattern = 'forward_partnership'
    elif avg_settling > 8:
        tactical_pattern = 'patient_partnership'
    else:
        tactical_pattern = 'balanced_partnership'

    return {
        'partnership_established': True,
        'tactical_pattern': tactical_pattern,
        'partnership_win_pct': result['win_pct'],
        'partnership_combinations': result['combinations'],
        'avg_settling_position': avg_settling
    }
```

---

## CATEGORY 12: MARKET DATA

### Overview
- **Category ID:** 12
- **Prediction Power:** 15-25% (market is highly informative)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 2
- **Cost per Race:** $0 (Betfair API free tier, Tab public odds)
- **ChatGPT Access:** 75% (has odds, limited market depth)
- **Our Target Access:** 100% (real-time market tracking)

---

## SUBCATEGORIES

### 12.1 Fixed Odds (Bookmaker Prices)
**Description:** Bookmaker fixed odds at various time points
**Data Type:** Numeric (decimal odds)
**Prediction Impact:** 12-18%

**Odds Data Schema:**
```python
odds_schema = {
    "opening_odds": float,          # First odds published
    "current_odds": float,          # Latest odds
    "odds_24h_ago": float,          # 24 hours before race
    "odds_1h_ago": float,           # 1 hour before race
    "odds_at_jump": float,          # Final odds at race start
    "best_available_odds": float,   # Best price across bookmakers
    "worst_available_odds": float,  # Worst price across bookmakers
    "avg_bookmaker_odds": float     # Average across all bookmakers
}
```

**Access Method:**
```python
def extract_tab_odds(race_url):
    """Extract odds from Tab.com.au"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    odds_data = {}
    runner_rows = soup.find_all('div', class_='runner-row')

    for row in runner_rows:
        horse_name = row.find('span', class_='horse-name').text
        odds_element = row.find('span', class_='odds')

        if odds_element:
            odds_text = odds_element.text  # e.g., "$3.50"
            odds_decimal = float(odds_text.replace('$', ''))
            odds_data[horse_name] = odds_decimal

    return odds_data

def track_odds_movement(horse_name, race_id):
    """Track odds changes over time"""

    # Query internal odds tracking database
    query = f"""
    SELECT
        timestamp,
        odds
    FROM odds_tracking
    WHERE race_id = '{race_id}'
      AND horse_name = '{horse_name}'
    ORDER BY timestamp
    """

    odds_history = execute_query(query)

    if not odds_history:
        return None

    # Calculate movements
    opening_odds = odds_history[0]['odds']
    current_odds = odds_history[-1]['odds']

    # Get specific time points
    odds_24h = get_odds_at_time(odds_history, hours_before=24)
    odds_1h = get_odds_at_time(odds_history, hours_before=1)

    return {
        'opening_odds': opening_odds,
        'current_odds': current_odds,
        'odds_24h_ago': odds_24h,
        'odds_1h_ago': odds_1h,
        'odds_movement_total': opening_odds - current_odds,
        'odds_movement_pct': (opening_odds - current_odds) / opening_odds if opening_odds > 0 else 0
    }
```

**Quantitative Features:**
```python
def engineer_odds_features(odds_data):
    """Create odds-based features"""

    features = {
        'current_odds': odds_data['current_odds'],
        'opening_odds': odds_data['opening_odds'],
        'odds_movement': odds_data.get('odds_movement_total', 0),
        'odds_movement_pct': odds_data.get('odds_movement_pct', 0),

        # Implied probability
        'implied_probability': 1 / odds_data['current_odds'],

        # Market position categories
        'market_position': categorize_market_position(odds_data['current_odds']),

        # Movement flags
        'is_shortening': 1 if odds_data.get('odds_movement_total', 0) > 0.5 else 0,
        'is_drifting': 1 if odds_data.get('odds_movement_total', 0) < -0.5 else 0,
        'is_steady': 1 if abs(odds_data.get('odds_movement_total', 0)) <= 0.5 else 0,

        # Strong move flag
        'strong_shorten': 1 if odds_data.get('odds_movement_pct', 0) > 0.20 else 0,  # 20%+ shorten
        'strong_drift': 1 if odds_data.get('odds_movement_pct', 0) < -0.20 else 0    # 20%+ drift
    }

    return features

def categorize_market_position(odds):
    """Categorize horse by market position"""
    if odds < 3.0:
        return 'favourite'
    elif odds < 6.0:
        return 'second_tier'
    elif odds < 12.0:
        return 'midfield'
    elif odds < 25.0:
        return 'outsider'
    else:
        return 'longshot'
```

**Qualitative Usage (GPT-5):**
- Context: "Horse has shortened from $7.00 to $4.50 (36% move), significant market support..."
- Reasoning: "Strong money suggests informed opinion, horse is well-fancied"
- Output: Market confidence adjustment (+8-12% if strong shortening)

---

### 12.2 Betfair Exchange Prices & Liquidity
**Description:** Exchange odds, matched volume, market depth
**Data Type:** Numeric (odds + volume)
**Prediction Impact:** 18-25%

**Betfair Data Schema:**
```python
betfair_schema = {
    "back_price_1": float,          # Best back price (to bet on)
    "back_price_2": float,
    "back_price_3": float,
    "back_volume_1": float,         # Volume available at best price
    "back_volume_2": float,
    "back_volume_3": float,
    "lay_price_1": float,           # Best lay price (to bet against)
    "lay_price_2": float,
    "lay_price_3": float,
    "lay_volume_1": float,
    "lay_volume_2": float,
    "lay_volume_3": float,
    "total_matched": float,         # Total money matched on horse
    "last_price_traded": float,
    "volume_weighted_avg_price": float
}
```

**Betfair API Integration:**
```python
import betfairlightweight

def authenticate_betfair():
    """Authenticate with Betfair API"""
    trading = betfairlightweight.APIClient(
        username=os.environ.get('BETFAIR_USERNAME'),
        password=os.environ.get('BETFAIR_PASSWORD'),
        app_key=os.environ.get('BETFAIR_APP_KEY')
    )
    trading.login()
    return trading

def get_betfair_market_data(market_id, selection_id):
    """Get live market data from Betfair"""
    trading = authenticate_betfair()

    # Get market book
    market_book = trading.betting.list_market_book(
        market_ids=[market_id],
        price_projection={
            'priceData': ['EX_BEST_OFFERS', 'EX_TRADED'],
            'virtualise': True
        }
    )

    # Find runner
    for runner in market_book[0].runners:
        if runner.selection_id == selection_id:
            ex = runner.ex

            return {
                'back_price_1': ex.available_to_back[0].price if ex.available_to_back else None,
                'back_volume_1': ex.available_to_back[0].size if ex.available_to_back else 0,
                'back_price_2': ex.available_to_back[1].price if len(ex.available_to_back) > 1 else None,
                'back_volume_2': ex.available_to_back[1].size if len(ex.available_to_back) > 1 else 0,
                'lay_price_1': ex.available_to_lay[0].price if ex.available_to_lay else None,
                'lay_volume_1': ex.available_to_lay[0].size if ex.available_to_lay else 0,
                'total_matched': runner.total_matched,
                'last_price_traded': runner.last_price_traded
            }

    return None
```

**Quantitative Features:**
```python
def engineer_betfair_features(betfair_data, field_betfair_data):
    """Create Betfair exchange features"""

    if not betfair_data:
        return {'has_betfair_data': 0}

    # Calculate total matched for entire field
    field_total_matched = sum([r['total_matched'] for r in field_betfair_data])

    features = {
        'has_betfair_data': 1,
        'betfair_back_price': betfair_data['back_price_1'],
        'betfair_lay_price': betfair_data['lay_price_1'],
        'betfair_back_volume': betfair_data['back_volume_1'],
        'betfair_lay_volume': betfair_data['lay_volume_1'],
        'betfair_total_matched': betfair_data['total_matched'],

        # Market depth
        'betfair_spread': betfair_data['lay_price_1'] - betfair_data['back_price_1'] if betfair_data['lay_price_1'] else 0,
        'betfair_spread_pct': (
            (betfair_data['lay_price_1'] - betfair_data['back_price_1']) / betfair_data['back_price_1']
            if betfair_data['lay_price_1'] and betfair_data['back_price_1'] else 0
        ),

        # Market share
        'betfair_market_share': (
            betfair_data['total_matched'] / field_total_matched
            if field_total_matched > 0 else 0
        ),

        # Liquidity flags
        'high_liquidity': 1 if betfair_data['total_matched'] > 50000 else 0,  # $50k+ matched
        'low_liquidity': 1 if betfair_data['total_matched'] < 5000 else 0     # <$5k matched
    }

    return features
```

**Qualitative Usage (GPT-5):**
- Context: "Betfair price $3.80 with $127k matched, heavy market support and liquidity..."
- Reasoning: "High matched volume indicates strong informed opinion"
- Output: Market intelligence adjustment (high liquidity + shortening = strong confidence)

---

### 12.3 Market Movements & Steamer/Drifter Analysis
**Description:** Significant market movements indicating information flow
**Data Type:** Derived from odds tracking
**Prediction Impact:** 10-15%

**Movement Analysis:**
```python
def identify_steamers_drifters(odds_history, threshold=0.20):
    """Identify horses with significant market moves"""

    steamers = []
    drifters = []

    for horse, odds_data in odds_history.items():
        opening = odds_data['opening_odds']
        current = odds_data['current_odds']

        movement_pct = (opening - current) / opening

        if movement_pct > threshold:
            steamers.append({
                'horse': horse,
                'opening': opening,
                'current': current,
                'movement_pct': movement_pct,
                'category': 'steamer'
            })
        elif movement_pct < -threshold:
            drifters.append({
                'horse': horse,
                'opening': opening,
                'current': current,
                'movement_pct': movement_pct,
                'category': 'drifter'
            })

    return {'steamers': steamers, 'drifters': drifters}

def calculate_market_momentum(odds_movement_history):
    """Calculate rate and acceleration of market moves"""

    if len(odds_movement_history) < 3:
        return {'momentum': 'insufficient_data'}

    # Calculate velocity (rate of change)
    recent_movements = odds_movement_history[-5:]  # Last 5 updates
    velocity = np.mean([m['change'] for m in recent_movements])

    # Calculate acceleration (change in velocity)
    if len(recent_movements) >= 3:
        early_velocity = np.mean([m['change'] for m in recent_movements[:2]])
        late_velocity = np.mean([m['change'] for m in recent_movements[-2:]])
        acceleration = late_velocity - early_velocity
    else:
        acceleration = 0

    return {
        'velocity': velocity,
        'acceleration': acceleration,
        'momentum': 'accelerating_in' if acceleration > 0.05 else
                   'decelerating' if acceleration < -0.05 else
                   'steady'
    }
```

**Quantitative Features:**
```python
def engineer_market_movement_features(odds_data, movement_analysis):
    """Create market movement features"""

    features = {
        'is_steamer': 1 if movement_analysis.get('category') == 'steamer' else 0,
        'is_drifter': 1 if movement_analysis.get('category') == 'drifter' else 0,
        'market_momentum': movement_analysis.get('momentum', 'steady'),
        'movement_velocity': movement_analysis.get('velocity', 0),
        'movement_acceleration': movement_analysis.get('acceleration', 0),

        # Timing flags
        'late_steamer': 1 if (
            movement_analysis.get('category') == 'steamer' and
            abs(odds_data.get('odds_movement_total', 0)) > 1.0 and
            movement_analysis.get('acceleration', 0) > 0.05
        ) else 0
    }

    return features
```

---

## INTEGRATION GUIDELINES

### Category 11-12 Cross-Integration

**Tactics + Market:**
```python
def analyze_tactics_market_alignment(jockey_style, odds_movement):
    """Check if market movement aligns with tactical setup"""

    # Example: Aggressive jockey + inside barrier + shortening odds = strong alignment
    # Market has identified tactical advantage

    if jockey_style['style'] == 'aggressive' and odds_movement['is_steamer']:
        return {
            'tactics_market_alignment': 'strong',
            'confidence_boost': 0.08
        }

    return {
        'tactics_market_alignment': 'neutral',
        'confidence_boost': 0.0
    }
```

---

## UNIFIED DATA MODEL

```python
tactics_market_schema = {
    "tactics": {
        "jockey_style": str,
        "trainer_placement_quality": str,
        "partnership_established": bool,
        "tactical_pattern": str
    },
    "market": {
        "current_odds": float,
        "implied_probability": float,
        "odds_movement_pct": float,
        "is_steamer": bool,
        "is_drifter": bool,
        "betfair_price": float,
        "betfair_total_matched": float,
        "market_position": str
    }
}
```

---

## COST ANALYSIS

**Categories 11-12 Cost Breakdown:**
- **Tactics:** $0 (derived from historical data)
- **Fixed odds:** $0 (public Tab data)
- **Betfair API:** $0 (free tier, 1000 requests/hour sufficient)

**Total Cost:** $0 per race

---

**Document Complete: Categories 11-12 (Tactics & Market Data)**
**Next Document: PART_09_CATEGORY_13_14.md (Weather Sensitivity & Historical Performance)**
