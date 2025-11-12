# Master Taxonomy - Part 7: Categories 9-10 (Gear Changes & Barrier Trials)

**Document Purpose:** Implementation reference for gear/equipment changes and trial performance
**Pipeline Usage:** Both Qualitative (GPT-5 context) and Quantitative (feature engineering)
**Implementation Priority:** Phase 1 Week 3

---

## CATEGORY 9: GEAR CHANGES

### Overview
- **Category ID:** 9
- **Prediction Power:** 5-12% (significant when first-time gear applied)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 3
- **Cost per Race:** $0 (public data)
- **ChatGPT Access:** 75%
- **Our Target Access:** 100%

---

## SUBCATEGORIES

### 9.1 Blinkers
**Description:** Eye shields restricting peripheral vision (focus horse forward)
**Data Type:** Binary + Categorical (first-time, removed, continuing)
**Prediction Impact:** 8-12% when first applied

**Blinker Status Categories:**
```python
BLINKER_STATUS = {
    'first_time': {
        'code': 'B1',
        'impact': 'high',
        'avg_improvement': 0.10,  # 10% improvement on average
        'description': 'Blinkers applied for first time'
    },
    'continuing': {
        'code': 'B',
        'impact': 'low',
        'avg_improvement': 0.02,  # 2% (marginal once adapted)
        'description': 'Continuing with blinkers'
    },
    'removed': {
        'code': 'B-',
        'impact': 'negative',
        'avg_improvement': -0.05,  # 5% decline (change is disruptive)
        'description': 'Blinkers removed'
    },
    'none': {
        'code': '',
        'impact': 'neutral',
        'avg_improvement': 0.0,
        'description': 'No blinkers'
    }
}
```

**Access Method:**
```python
def extract_gear_info(race_url, horse_name):
    """Extract gear information for horse"""
    response = requests.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    horse_rows = soup.find_all('div', class_='runner-row')
    for row in horse_rows:
        name = row.find('span', class_='horse-name').text
        if name == horse_name:
            gear_element = row.find('span', class_='gear')
            gear_text = gear_element.text if gear_element else ""

            return parse_gear(gear_text)
    return None

def parse_gear(gear_text):
    """Parse gear string into structured data"""
    gear = {
        'blinkers': 'none',
        'tongue_tie': False,
        'visors': False,
        'lugging_bit': False,
        'nose_roll': False,
        'ear_muffs': False,
        'pacifiers': False
    }

    # Parse blinkers
    if 'B1' in gear_text or '1. B' in gear_text:
        gear['blinkers'] = 'first_time'
    elif 'B' in gear_text:
        gear['blinkers'] = 'continuing'

    # Parse other gear
    if 'TT' in gear_text or 'Tongue Tie' in gear_text:
        gear['tongue_tie'] = True
    if 'V' in gear_text or 'Visor' in gear_text:
        gear['visors'] = True
    if 'LB' in gear_text:
        gear['lugging_bit'] = True
    if 'NR' in gear_text:
        gear['nose_roll'] = True
    if 'EM' in gear_text:
        gear['ear_muffs'] = True
    if 'P' in gear_text:
        gear['pacifiers'] = True

    return gear

def determine_blinker_status(current_gear, previous_gear_history):
    """Determine if blinkers are first-time, continuing, or removed"""

    current_has_blinkers = current_gear['blinkers'] in ['first_time', 'continuing']

    if not previous_gear_history:
        # No history, assume first time if wearing
        return 'first_time' if current_has_blinkers else 'none'

    # Check last 3 starts
    recent_starts = previous_gear_history[:3]
    recent_had_blinkers = [s['blinkers'] in ['first_time', 'continuing'] for s in recent_starts]

    if current_has_blinkers and not any(recent_had_blinkers):
        return 'first_time'
    elif current_has_blinkers and all(recent_had_blinkers):
        return 'continuing'
    elif not current_has_blinkers and any(recent_had_blinkers):
        return 'removed'
    else:
        return 'none'
```

**Qualitative Usage (GPT-5):**
- Context: "Blinkers applied for first time (B1), historically leads to 10% average improvement..."
- Reasoning: "First-time blinkers often improve focus and performance"
- Output: Gear change adjustment (+8-12% if first-time blinkers)

**Quantitative Features:**
```python
def engineer_blinker_features(blinker_status, horse_history):
    """Create blinker features"""

    # Get blinker status
    status_data = BLINKER_STATUS[blinker_status]

    features = {
        'blinkers_status': blinker_status,
        'blinkers_code': status_data['code'],
        'is_first_time_blinkers': 1 if blinker_status == 'first_time' else 0,
        'is_blinkers_removed': 1 if blinker_status == 'removed' else 0,
        'blinkers_impact_expected': status_data['avg_improvement'],

        # Historical performance with/without blinkers
        'has_blinker_history': 0,
        'blinkers_win_pct': 0,
        'no_blinkers_win_pct': 0
    }

    # Calculate historical blinker performance
    if horse_history:
        blinker_starts = [r for r in horse_history if r.get('blinkers') in ['first_time', 'continuing']]
        no_blinker_starts = [r for r in horse_history if r.get('blinkers') in ['none', 'removed']]

        if blinker_starts:
            features['has_blinker_history'] = 1
            blinker_wins = sum(1 for r in blinker_starts if r['position'] == 1)
            features['blinkers_win_pct'] = blinker_wins / len(blinker_starts)

        if no_blinker_starts:
            no_blinker_wins = sum(1 for r in no_blinker_starts if r['position'] == 1)
            features['no_blinkers_win_pct'] = no_blinker_wins / len(no_blinker_starts)

        # Performance delta
        if features['has_blinker_history']:
            features['blinkers_performance_delta'] = features['blinkers_win_pct'] - features['no_blinkers_win_pct']

    return features
```

---

### 9.2 Other Gear (Tongue Tie, Visors, Nose Roll, etc.)
**Description:** Additional equipment affecting horse behavior
**Data Type:** Binary flags
**Prediction Impact:** 2-5% per item

**Gear Impact Database:**
```python
GEAR_IMPACT = {
    'tongue_tie': {
        'impact': 'moderate',
        'avg_improvement': 0.03,
        'purpose': 'Prevent airway obstruction',
        'typical_use': 'Horses that get tongue over bit'
    },
    'visors': {
        'impact': 'moderate',
        'avg_improvement': 0.04,
        'purpose': 'Partial peripheral vision restriction',
        'typical_use': 'Less restrictive than blinkers'
    },
    'nose_roll': {
        'impact': 'low',
        'avg_improvement': 0.02,
        'purpose': 'Keep head down, improve breathing',
        'typical_use': 'Horses that carry head high'
    },
    'lugging_bit': {
        'impact': 'low',
        'avg_improvement': 0.01,
        'purpose': 'Prevent lugging/hanging',
        'typical_use': 'Horses that hang in or out'
    },
    'ear_muffs': {
        'impact': 'low',
        'avg_improvement': 0.01,
        'purpose': 'Reduce noise distractions',
        'typical_use': 'Nervous or easily distracted horses'
    },
    'pacifiers': {
        'impact': 'low',
        'avg_improvement': 0.01,
        'purpose': 'Calm horse in barriers',
        'typical_use': 'Barrier-shy or anxious horses'
    }
}
```

**Quantitative Features:**
```python
def engineer_other_gear_features(gear_data):
    """Create features for all gear items"""
    features = {
        'has_tongue_tie': 1 if gear_data['tongue_tie'] else 0,
        'has_visors': 1 if gear_data['visors'] else 0,
        'has_nose_roll': 1 if gear_data['nose_roll'] else 0,
        'has_lugging_bit': 1 if gear_data['lugging_bit'] else 0,
        'has_ear_muffs': 1 if gear_data['ear_muffs'] else 0,
        'has_pacifiers': 1 if gear_data['pacifiers'] else 0,

        # Total gear count
        'total_gear_count': sum([
            gear_data['tongue_tie'],
            gear_data['visors'],
            gear_data['nose_roll'],
            gear_data['lugging_bit'],
            gear_data['ear_muffs'],
            gear_data['pacifiers']
        ]),

        # Expected cumulative impact
        'gear_expected_impact': sum([
            GEAR_IMPACT['tongue_tie']['avg_improvement'] if gear_data['tongue_tie'] else 0,
            GEAR_IMPACT['visors']['avg_improvement'] if gear_data['visors'] else 0,
            GEAR_IMPACT['nose_roll']['avg_improvement'] if gear_data['nose_roll'] else 0,
            GEAR_IMPACT['lugging_bit']['avg_improvement'] if gear_data['lugging_bit'] else 0,
            GEAR_IMPACT['ear_muffs']['avg_improvement'] if gear_data['ear_muffs'] else 0,
            GEAR_IMPACT['pacifiers']['avg_improvement'] if gear_data['pacifiers'] else 0
        ])
    }

    return features
```

---

## CATEGORY 10: BARRIER TRIALS

### Overview
- **Category ID:** 10
- **Prediction Power:** 18-25% (highly predictive when recent and positive)
- **Pipeline Usage:** BOTH (Qualitative + Quantitative)
- **Priority Phase:** Phase 1 Week 3
- **Cost per Race:** $0.05 (authentication + scraping Racing.com trials)
- **ChatGPT Access:** 0% (authentication wall)
- **Our Target Access:** 90% (Selenium + cookies authentication)

**Critical Note:** This is a MAJOR competitive advantage over ChatGPT (0% access vs our 90%)

---

## SUBCATEGORIES

### 10.1 Recent Trial Performance
**Description:** Most recent barrier trial result (within 21 days)
**Data Type:** Structured trial data
**Prediction Impact:** 20-25%

**Trial Data Schema:**
```python
trial_schema = {
    "trial_date": datetime,
    "days_since_trial": int,
    "venue": str,
    "distance": int,
    "track_condition": str,
    "finish_position": int,
    "margin": float,
    "field_size": int,
    "trial_time": float,        # If available
    "comment": str,             # Steward/clocker comments
    "heat_number": int,         # Which heat in the session
    "is_jumpout": bool          # Official trial vs jumpout
}
```

**Access Method (Authentication Required):**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def authenticate_racing_com(driver):
    """Login to Racing.com to access barrier trials"""
    driver.get("https://racing.com/login")

    # Enter credentials (use environment variables)
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")

    username_field.send_keys(os.environ.get('RACING_COM_USERNAME'))
    password_field.send_keys(os.environ.get('RACING_COM_PASSWORD'))

    login_button = driver.find_element(By.ID, "login-button")
    login_button.click()

    # Wait for login to complete
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "user-profile"))
    )

    return driver

def extract_barrier_trials(horse_name, authenticated_driver):
    """Extract barrier trial history for horse"""

    # Navigate to trials page
    search_url = f"https://racing.com/horse-profile/search?name={horse_name.replace(' ', '+')}"
    authenticated_driver.get(search_url)

    # Click on horse profile
    horse_link = authenticated_driver.find_element(By.CLASS_NAME, "horse-profile-link")
    horse_link.click()

    # Navigate to trials tab
    trials_tab = authenticated_driver.find_element(By.LINK_TEXT, "Trials")
    trials_tab.click()

    time.sleep(2)  # Wait for trials to load

    # Extract trial rows
    trial_rows = authenticated_driver.find_elements(By.CLASS_NAME, "trial-row")

    trials = []
    for row in trial_rows[:5]:  # Get last 5 trials
        trial_date_str = row.find_element(By.CLASS_NAME, "trial-date").text
        venue = row.find_element(By.CLASS_NAME, "trial-venue").text
        distance = int(row.find_element(By.CLASS_NAME, "trial-distance").text.replace('m', ''))
        position = int(row.find_element(By.CLASS_NAME, "trial-position").text)
        margin = float(row.find_element(By.CLASS_NAME, "trial-margin").text.replace('L', ''))

        trial_date = datetime.strptime(trial_date_str, "%d/%m/%Y")
        days_since = (datetime.now() - trial_date).days

        trials.append({
            'trial_date': trial_date,
            'days_since_trial': days_since,
            'venue': venue,
            'distance': distance,
            'finish_position': position,
            'margin': margin
        })

    return trials

def get_most_recent_trial(trials):
    """Get most recent trial (within 21 days)"""
    if not trials:
        return None

    # Sort by date (most recent first)
    sorted_trials = sorted(trials, key=lambda x: x['trial_date'], reverse=True)

    most_recent = sorted_trials[0]

    # Only consider if within 21 days
    if most_recent['days_since_trial'] > 21:
        return None

    return most_recent
```

**Qualitative Usage (GPT-5):**
- Context: "Won recent trial at Flemington 1000m by 1.5L (7 days ago), impressive hit-out..."
- Reasoning: "Recent trial win suggests horse is fit and ready to perform"
- Output: Trial form adjustment (+15-20% if trial win within 14 days)

**Quantitative Features:**
```python
def engineer_trial_features(trial_data):
    """Create barrier trial features"""

    if not trial_data:
        return {
            'has_recent_trial': 0,
            'days_since_trial': None,
            'trial_position': None,
            'trial_win': 0,
            'trial_performance_score': 0
        }

    features = {
        'has_recent_trial': 1,
        'days_since_trial': trial_data['days_since_trial'],
        'trial_position': trial_data['finish_position'],
        'trial_margin': trial_data['margin'],
        'trial_distance': trial_data['distance'],

        # Binary flags
        'trial_win': 1 if trial_data['finish_position'] == 1 else 0,
        'trial_place': 1 if trial_data['finish_position'] <= 3 else 0,

        # Trial freshness (peak at 7-14 days)
        'trial_freshness_score': calculate_trial_freshness(trial_data['days_since_trial']),

        # Performance score
        'trial_performance_score': calculate_trial_performance_score(trial_data)
    }

    return features

def calculate_trial_freshness(days_since):
    """Calculate how fresh/relevant the trial is"""
    if days_since <= 7:
        return 1.0  # Very fresh
    elif days_since <= 14:
        return 0.9  # Optimal timing
    elif days_since <= 21:
        return 0.7  # Still relevant
    else:
        return 0.0  # Too old

def calculate_trial_performance_score(trial_data):
    """Calculate overall trial performance score (0-100)"""

    # Base score from position
    position = trial_data['finish_position']
    if position == 1:
        base_score = 95
    elif position == 2:
        base_score = 85
    elif position == 3:
        base_score = 75
    elif position <= 5:
        base_score = 65
    else:
        base_score = 50

    # Adjust for margin
    margin = trial_data.get('margin', 0)
    if position == 1:
        margin_adjustment = min(margin * 3, 10)  # Win by more = better (up to +10)
    else:
        margin_adjustment = -min(margin * 2, 20)  # Lose by more = worse (up to -20)

    # Adjust for field size
    field_size = trial_data.get('field_size', 6)
    field_adjustment = (field_size - 6) * 2  # Larger field = more impressive

    # Final score
    score = base_score + margin_adjustment + field_adjustment
    return max(20, min(score, 100))  # Cap 20-100
```

---

### 10.2 Trial History Pattern
**Description:** Pattern of multiple recent trials
**Data Type:** Derived from trial sequence
**Prediction Impact:** 5-10%

**Pattern Analysis:**
```python
def analyze_trial_pattern(trials):
    """Analyze pattern in trial performances"""

    if not trials or len(trials) < 2:
        return {
            'pattern': 'insufficient_data',
            'improvement_trend': 0
        }

    # Sort by date (oldest first for trend analysis)
    sorted_trials = sorted(trials, key=lambda x: x['trial_date'])

    # Calculate trend (improving vs declining)
    positions = [t['finish_position'] for t in sorted_trials]

    # Simple trend: compare first trial to last trial
    if len(positions) >= 2:
        improvement = positions[0] - positions[-1]  # Positive = improving (lower position number)

        if improvement > 2:
            pattern = 'strongly_improving'
            improvement_trend = 0.15
        elif improvement > 0:
            pattern = 'improving'
            improvement_trend = 0.08
        elif improvement == 0:
            pattern = 'consistent'
            improvement_trend = 0.05
        elif improvement > -2:
            pattern = 'slight_decline'
            improvement_trend = -0.03
        else:
            pattern = 'declining'
            improvement_trend = -0.08
    else:
        pattern = 'single_trial'
        improvement_trend = 0

    return {
        'pattern': pattern,
        'improvement_trend': improvement_trend,
        'trial_count': len(trials),
        'avg_trial_position': np.mean(positions)
    }
```

---

## INTEGRATION GUIDELINES

### Category 9-10 Cross-Integration

**Gear Changes + Trial Performance:**
```python
def analyze_gear_trial_interaction(gear_data, trial_data):
    """Check if gear was worn in trial (readiness indicator)"""

    if not trial_data or not gear_data:
        return {'gear_trial_synergy': 0}

    # If first-time gear today and worn in trial = well-prepared
    if gear_data['blinkers_status'] == 'first_time':
        # Check if blinkers were in trial (if data available)
        trial_had_blinkers = trial_data.get('gear', {}).get('blinkers')

        if trial_had_blinkers:
            return {
                'gear_trial_synergy': 0.12,
                'gear_trialed': True,
                'preparation_quality': 'excellent'
            }
        else:
            return {
                'gear_trial_synergy': 0.0,
                'gear_trialed': False,
                'preparation_quality': 'untested_gear'
            }

    return {'gear_trial_synergy': 0}
```

### Validation Rules

```python
def validate_gear_trial_data(gear_data, trial_data):
    """Validate categories 9-10"""
    errors = []
    warnings = []

    # Gear validation
    if gear_data['total_gear_count'] > 4:
        warnings.append(f"Horse has {gear_data['total_gear_count']} pieces of gear (unusual)")

    # Trial validation
    if trial_data and trial_data.get('has_recent_trial'):
        days_since = trial_data['days_since_trial']

        if days_since > 21:
            warnings.append(f"Trial is {days_since} days old (>21 days, less relevant)")

        if days_since < 3:
            warnings.append(f"Trial only {days_since} days ago (very tight turnaround)")

        if trial_data['trial_position'] > 8:
            warnings.append(f"Poor trial performance (finished {trial_data['trial_position']})")

    return {'errors': errors, 'warnings': warnings}
```

---

## UNIFIED DATA MODEL

```python
gear_trial_schema = {
    "gear": {
        "blinkers_status": str,
        "is_first_time_blinkers": bool,
        "has_tongue_tie": bool,
        "has_visors": bool,
        "total_gear_count": int,
        "gear_expected_impact": float
    },
    "trial": {
        "has_recent_trial": bool,
        "days_since_trial": int,
        "trial_position": int,
        "trial_win": bool,
        "trial_performance_score": float,
        "trial_freshness_score": float,
        "pattern": str,
        "improvement_trend": float
    }
}
```

---

## COST ANALYSIS

**Categories 9-10 Cost Breakdown:**
- **Gear extraction:** $0 (public data)
- **Trial extraction:** $0.05/race (Selenium authentication + scraping)
  - Setup cost: $0 (free Racing.com account)
  - Processing time: ~10 seconds per horse

**Total Cost:** $0.05 per race

---

## IMPLEMENTATION CHECKLIST

### Phase 1 Week 3: Categories 9-10

**Day 1: Gear Extraction**
- [ ] Implement gear parsing
- [ ] Build gear database
- [ ] Test on 20 horses
- [ ] Validate first-time blinkers detection

**Day 2-3: Barrier Trials Setup**
- [ ] Set up Selenium + Racing.com authentication
- [ ] Implement trial extraction
- [ ] Test on 10 horses
- [ ] Handle authentication errors

**Day 4: Feature Engineering**
- [ ] Implement all gear features
- [ ] Implement all trial features
- [ ] Test gear-trial interaction
- [ ] Calculate performance scores

**Day 5: Testing & Validation**
- [ ] Full pipeline test on 20 races
- [ ] Validate trial freshness calculations
- [ ] Check gear change impact accuracy
- [ ] Document authentication setup

---

**Document Complete: Categories 9-10 (Gear Changes & Barrier Trials)**
**Next Document: PART_08_CATEGORY_11_12.md (Jockey/Trainer Tactics & Market Data)**
