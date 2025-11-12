# Master Taxonomy - Part 20: Phase 1 Implementation Roadmap (Weeks 1-8)

**Document Purpose:** Week-by-week implementation guide for Phase 1 (foundational categories)
**Timeline:** 8 weeks
**Outcome:** Core system operational with 70%+ prediction capability

---

## WEEK 1: PROJECT SETUP & CATEGORY 1-2 (BASIC RACE INFORMATION)

### Day 1: Infrastructure & Environment Setup

**Morning (4 hours):**
```bash
# 1. Python environment setup
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# 2. Install core dependencies
pip install pandas==2.1.0 numpy==1.25.2 requests==2.31.0
pip install beautifulsoup4==4.12.2 selenium==4.12.0
pip install psycopg2-binary==2.9.7 sqlalchemy==2.0.20
pip install python-dotenv==1.0.0 pytest==7.4.0

# 3. Save requirements
pip freeze > requirements.txt
```

**Project Structure:**
```python
racing_analysis/
├── data/
│   ├── raw/                 # Raw scraped data
│   ├── processed/           # Cleaned data
│   └── historical/          # Historical database
├── src/
│   ├── __init__.py
│   ├── collectors/          # Data collection modules
│   │   ├── __init__.py
│   │   ├── base_collector.py
│   │   ├── racing_com.py
│   │   └── betfair.py
│   ├── features/            # Feature engineering
│   │   ├── __init__.py
│   │   └── category_*.py   # One file per category
│   ├── models/              # Prediction models
│   │   ├── __init__.py
│   │   └── predictor.py
│   ├── integration/         # Category integration
│   │   ├── __init__.py
│   │   └── integrator.py
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── database.py
│       └── helpers.py
├── tests/
│   ├── test_collectors/
│   ├── test_features/
│   └── test_integration/
├── config/
│   ├── config.yaml
│   └── .env.example
├── notebooks/               # Jupyter notebooks for analysis
├── requirements.txt
└── README.md
```

**Afternoon (4 hours):**
```python
# src/utils/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Race(Base):
    """Race table - Category 1-2"""
    __tablename__ = 'races'

    race_id = Column(String, primary_key=True)
    venue = Column(String, nullable=False)
    distance = Column(Integer, nullable=False)
    race_datetime = Column(DateTime, nullable=False)
    race_class = Column(String)  # 'Group 1', 'Benchmark 78', etc.
    prize_money = Column(Float)
    field_size = Column(Integer)
    track_condition = Column(String)  # 'Good 4', 'Heavy 8', etc.
    rail_position = Column(String)

    # Relationships
    runners = relationship("Runner", back_populates="race")

class Horse(Base):
    """Horse table"""
    __tablename__ = 'horses'

    horse_id = Column(String, primary_key=True)
    horse_name = Column(String, nullable=False)
    age = Column(Integer)
    sex = Column(String)  # 'M', 'F', 'G', 'C', 'H'
    colour = Column(String)
    sire = Column(String)
    dam = Column(String)

    # Relationships
    runs = relationship("Runner", back_populates="horse")

class Runner(Base):
    """Runner table - individual horse in a race"""
    __tablename__ = 'runners'

    runner_id = Column(String, primary_key=True)
    race_id = Column(String, ForeignKey('races.race_id'))
    horse_id = Column(String, ForeignKey('horses.horse_id'))

    # Category 4: Barrier
    barrier = Column(Integer)

    # Category 5: Weight
    weight_kg = Column(Float)

    # Category 6: Jockey
    jockey_name = Column(String)

    # Category 7: Trainer
    trainer_name = Column(String)

    # Category 9: Gear
    gear = Column(String)  # JSON string: ['Blinkers', 'Tongue Tie']

    # Results
    finish_position = Column(Integer)
    margin_lengths = Column(Float)
    finishing_time = Column(Float)

    # Odds
    starting_price = Column(Float)
    betfair_bsp = Column(Float)

    # Relationships
    race = relationship("Race", back_populates="runners")
    horse = relationship("Horse", back_populates="runs")

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/racing_analysis')
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(engine)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Day 1 Deliverables:**
- [x] Python environment configured
- [x] Project structure created
- [x] Database schema defined
- [x] Git repository initialized

**Testing Checklist:**
```python
# tests/test_database.py
import pytest
from src.utils.database import engine, Base, Race, Horse, Runner, SessionLocal

def test_database_connection():
    """Test database connection"""
    assert engine is not None
    connection = engine.connect()
    assert connection is not None
    connection.close()

def test_create_race():
    """Test creating race record"""
    db = SessionLocal()
    race = Race(
        race_id='FLEM_2024_05_15_R01',
        venue='Flemington',
        distance=1200,
        race_datetime='2024-05-15 14:00:00',
        race_class='Benchmark 78',
        prize_money=150000,
        field_size=14
    )
    db.add(race)
    db.commit()

    # Verify
    retrieved = db.query(Race).filter_by(race_id='FLEM_2024_05_15_R01').first()
    assert retrieved.venue == 'Flemington'
    assert retrieved.distance == 1200

    db.close()
```

---

### Day 2: Data Collection Framework

**Morning (4 hours): Base Collector Class**
```python
# src/collectors/base_collector.py
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """Abstract base class for all data collectors"""

    def __init__(self, headers=None):
        self.session = requests.Session()
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session.headers.update(self.headers)
        self.rate_limit_delay = 1.0  # seconds between requests

    @abstractmethod
    def collect(self, *args, **kwargs):
        """Main collection method - must be implemented by subclasses"""
        pass

    def get_page(self, url, retries=3):
        """GET request with retries and rate limiting"""
        for attempt in range(retries):
            try:
                time.sleep(self.rate_limit_delay)
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                logger.info(f"Successfully fetched: {url}")
                return response
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == retries - 1:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

    def parse_html(self, html):
        """Parse HTML content"""
        return BeautifulSoup(html, 'html.parser')

    def validate_data(self, data, required_fields):
        """Validate collected data has required fields"""
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        return True
```

**Afternoon (4 hours): Racing.com Scraper**
```python
# src/collectors/racing_com.py
from .base_collector import BaseCollector
from datetime import datetime
import re

class RacingComCollector(BaseCollector):
    """Collector for Racing.com data"""

    BASE_URL = 'https://www.racing.com'

    def collect_race_metadata(self, race_url):
        """
        Collect Categories 1-2: Race metadata

        Args:
            race_url: Full URL to race page on racing.com

        Returns:
            dict: Race metadata
        """
        response = self.get_page(race_url)
        soup = self.parse_html(response.content)

        # Extract race information
        race_data = {
            'url': race_url,
            'collected_at': datetime.now().isoformat()
        }

        # Category 1.1: Distance
        distance_elem = soup.find('span', class_='race-distance')
        if distance_elem:
            distance_text = distance_elem.text.strip()
            race_data['distance'] = int(re.search(r'(\d+)m', distance_text).group(1))

        # Category 1.2: Venue
        venue_elem = soup.find('h1', class_='race-header')
        if venue_elem:
            race_data['venue'] = venue_elem.text.strip().split('-')[0].strip()

        # Category 1.3: Date/Time
        datetime_elem = soup.find('span', class_='race-time')
        if datetime_elem:
            datetime_text = datetime_elem.get('data-datetime')
            race_data['race_datetime'] = datetime.fromisoformat(datetime_text)

        # Category 2.1: Race Class
        class_elem = soup.find('span', class_='race-class')
        if class_elem:
            race_data['race_class'] = class_elem.text.strip()

        # Category 2.2: Prize Money
        prize_elem = soup.find('span', class_='prize-money')
        if prize_elem:
            prize_text = prize_elem.text.strip()
            # Convert '$150,000' to 150000
            race_data['prize_money'] = float(re.sub(r'[,$]', '', prize_text))

        # Category 2.3: Field Size
        runners = soup.find_all('div', class_='runner-card')
        race_data['field_size'] = len(runners)

        # Category 3.1: Track Condition
        condition_elem = soup.find('span', class_='track-condition')
        if condition_elem:
            race_data['track_condition'] = condition_elem.text.strip()

        # Category 3.2: Rail Position
        rail_elem = soup.find('span', class_='rail-position')
        if rail_elem:
            race_data['rail_position'] = rail_elem.text.strip()

        # Validate required fields
        required = ['distance', 'venue', 'race_datetime', 'field_size']
        self.validate_data(race_data, required)

        return race_data

    def collect_runners(self, race_url):
        """Collect runner information for a race"""
        response = self.get_page(race_url)
        soup = self.parse_html(response.content)

        runners = []
        runner_cards = soup.find_all('div', class_='runner-card')

        for card in runner_cards:
            runner = {}

            # Horse name
            name_elem = card.find('h3', class_='horse-name')
            if name_elem:
                runner['horse_name'] = name_elem.text.strip()

            # Barrier (Category 4)
            barrier_elem = card.find('span', class_='barrier-number')
            if barrier_elem:
                runner['barrier'] = int(barrier_elem.text.strip())

            # Weight (Category 5)
            weight_elem = card.find('span', class_='weight')
            if weight_elem:
                weight_text = weight_elem.text.strip()
                runner['weight_kg'] = float(re.search(r'([\d.]+)kg', weight_text).group(1))

            # Jockey (Category 6)
            jockey_elem = card.find('span', class_='jockey-name')
            if jockey_elem:
                runner['jockey_name'] = jockey_elem.text.strip()

            # Trainer (Category 7)
            trainer_elem = card.find('span', class_='trainer-name')
            if trainer_elem:
                runner['trainer_name'] = trainer_elem.text.strip()

            # Gear (Category 9)
            gear_elem = card.find('span', class_='gear')
            if gear_elem:
                gear_text = gear_elem.text.strip()
                runner['gear'] = [g.strip() for g in gear_text.split(',') if g.strip()]
            else:
                runner['gear'] = []

            # Starting Price
            odds_elem = card.find('span', class_='starting-price')
            if odds_elem:
                runner['starting_price'] = float(odds_elem.text.strip().replace('$', ''))

            runners.append(runner)

        return runners

    def collect_race_full(self, race_url):
        """Collect complete race data (metadata + runners)"""
        race_data = self.collect_race_metadata(race_url)
        runners = self.collect_runners(race_url)
        race_data['runners'] = runners
        return race_data
```

**Testing:**
```python
# tests/test_collectors/test_racing_com.py
import pytest
from src.collectors.racing_com import RacingComCollector

def test_collect_race_metadata():
    """Test collecting race metadata"""
    collector = RacingComCollector()
    race_url = 'https://www.racing.com/form-guide/FLEM/2024-05-15/R01'  # Example URL

    race_data = collector.collect_race_metadata(race_url)

    # Verify required fields present
    assert 'distance' in race_data
    assert 'venue' in race_data
    assert 'race_datetime' in race_data
    assert 'field_size' in race_data

    # Verify data types
    assert isinstance(race_data['distance'], int)
    assert isinstance(race_data['field_size'], int)
    assert race_data['distance'] >= 800  # Minimum race distance
    assert race_data['field_size'] >= 2   # Minimum field size

def test_collect_runners():
    """Test collecting runner data"""
    collector = RacingComCollector()
    race_url = 'https://www.racing.com/form-guide/FLEM/2024-05-15/R01'

    runners = collector.collect_runners(race_url)

    # Verify runners collected
    assert len(runners) > 0

    # Verify first runner has required fields
    first_runner = runners[0]
    assert 'horse_name' in first_runner
    assert 'barrier' in first_runner
    assert 'jockey_name' in first_runner
    assert 'trainer_name' in first_runner
```

**Day 2 Deliverables:**
- [x] Base collector class implemented
- [x] Racing.com scraper functional
- [x] 10 sample races collected successfully
- [x] Unit tests passing

**Data Quality Validation:**
```python
# src/utils/data_validation.py
def validate_race_data(race_data):
    """Validate race data quality"""
    errors = []
    warnings = []

    # Distance validation
    if race_data['distance'] < 800 or race_data['distance'] > 3600:
        errors.append(f"Invalid distance: {race_data['distance']}m")

    # Field size validation
    if race_data['field_size'] < 2 or race_data['field_size'] > 24:
        warnings.append(f"Unusual field size: {race_data['field_size']}")

    # Prize money validation
    if 'prize_money' in race_data and race_data['prize_money'] < 10000:
        warnings.append(f"Low prize money: ${race_data['prize_money']}")

    # Track condition validation
    valid_conditions = ['Good', 'Soft', 'Heavy', 'Firm']
    if 'track_condition' in race_data:
        condition_type = race_data['track_condition'].split()[0]
        if condition_type not in valid_conditions:
            errors.append(f"Invalid track condition: {race_data['track_condition']}")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }
```

---

### Day 3: Categories 1.1-1.3 Feature Engineering

**Morning (4 hours): Distance Features**
```python
# src/features/category_1_race_metadata.py
import pandas as pd
import numpy as np
from datetime import datetime

class RaceMetadataFeatures:
    """Feature engineering for Categories 1-2"""

    def __init__(self):
        # Distance categories (Australian racing standard)
        self.distance_categories = {
            'sprint': (0, 1200),
            'short_middle': (1201, 1400),
            'middle': (1401, 1600),
            'middle_long': (1601, 1800),
            'stayers': (1801, 2400),
            'extreme': (2401, 9999)
        }

    def extract_distance_features(self, distance_m):
        """
        Extract distance features

        Args:
            distance_m: Race distance in meters

        Returns:
            dict: Distance features
        """
        features = {}

        # Raw distance
        features['distance_m'] = distance_m

        # Distance category
        for category, (min_d, max_d) in self.distance_categories.items():
            if min_d <= distance_m <= max_d:
                features['distance_category'] = category
                break

        # Binary indicators for common distances
        common_distances = [1000, 1100, 1200, 1400, 1600, 2000, 2400]
        for dist in common_distances:
            features[f'is_{dist}m'] = 1 if distance_m == dist else 0

        # Distance log-transform (for modeling)
        features['distance_log'] = np.log(distance_m)

        # Distance squared (captures non-linear effects)
        features['distance_squared'] = distance_m ** 2

        # Distance bands (100m intervals)
        features['distance_band_100m'] = (distance_m // 100) * 100

        return features

    def extract_venue_features(self, venue_name, venue_stats_db):
        """
        Extract venue features

        Args:
            venue_name: Venue name (e.g., 'Flemington')
            venue_stats_db: Database of venue statistics

        Returns:
            dict: Venue features
        """
        features = {}

        # Venue name
        features['venue'] = venue_name

        # Venue prestige level
        GROUP_1_VENUES = ['Flemington', 'Randwick', 'Caulfield', 'Rosehill']
        METRO_VENUES = ['Moonee Valley', 'Sandown', 'Canterbury', 'Doomben']

        if venue_name in GROUP_1_VENUES:
            features['venue_prestige'] = 'group_1'
            features['venue_prestige_score'] = 3
        elif venue_name in METRO_VENUES:
            features['venue_prestige'] = 'metro'
            features['venue_prestige_score'] = 2
        else:
            features['venue_prestige'] = 'provincial_country'
            features['venue_prestige_score'] = 1

        # Historical venue statistics (from database)
        if venue_name in venue_stats_db:
            stats = venue_stats_db[venue_name]
            features['venue_avg_field_size'] = stats.get('avg_field_size', 12)
            features['venue_avg_prize_money'] = stats.get('avg_prize_money', 50000)
            features['venue_avg_winning_time'] = stats.get('avg_winning_time', {})
            features['venue_track_bias_historical'] = stats.get('avg_track_bias', 0)

        # Binary indicators for major venues
        major_venues = ['Flemington', 'Randwick', 'Caulfield', 'Rosehill', 'Moonee Valley']
        for major_venue in major_venues:
            features[f'is_{major_venue.lower()}'] = 1 if venue_name == major_venue else 0

        return features

    def extract_datetime_features(self, race_datetime):
        """
        Extract datetime features

        Args:
            race_datetime: datetime object

        Returns:
            dict: Datetime features
        """
        features = {}

        # Basic components
        features['year'] = race_datetime.year
        features['month'] = race_datetime.month
        features['day'] = race_datetime.day
        features['hour'] = race_datetime.hour
        features['minute'] = race_datetime.minute
        features['day_of_week'] = race_datetime.weekday()  # 0=Monday, 6=Sunday

        # Season (Australian seasons)
        month = race_datetime.month
        if month in [12, 1, 2]:
            features['season'] = 'summer'
        elif month in [3, 4, 5]:
            features['season'] = 'autumn'
        elif month in [6, 7, 8]:
            features['season'] = 'winter'
        else:
            features['season'] = 'spring'

        # Time of day
        hour = race_datetime.hour
        if 10 <= hour < 12:
            features['time_of_day'] = 'morning'
        elif 12 <= hour < 15:
            features['time_of_day'] = 'early_afternoon'
        elif 15 <= hour < 17:
            features['time_of_day'] = 'late_afternoon'
        elif 17 <= hour < 20:
            features['time_of_day'] = 'twilight'
        else:
            features['time_of_day'] = 'night'

        # Weekend indicator
        features['is_weekend'] = 1 if race_datetime.weekday() >= 5 else 0

        # Major race day indicators (Australian racing calendar)
        race_date = race_datetime.date()
        features['is_melbourne_cup_week'] = 1 if (race_datetime.month == 11 and 1 <= race_datetime.day <= 7) else 0
        features['is_golden_slipper_day'] = 1 if (race_datetime.month == 3 and 15 <= race_datetime.day <= 25) else 0
        features['is_cox_plate_day'] = 1 if (race_datetime.month == 10 and 20 <= race_datetime.day <= 31) else 0

        # Days since epoch (for time-based modeling)
        features['days_since_epoch'] = (race_datetime - datetime(2020, 1, 1)).days

        return features
```

**Afternoon (4 hours): Class & Prize Money Features**
```python
# Continuing src/features/category_1_race_metadata.py

class RaceClassFeatures:
    """Feature engineering for Category 2"""

    def __init__(self):
        # Class hierarchy mapping
        self.class_hierarchy = {
            'Group 1': 9,
            'Group 2': 8,
            'Group 3': 7,
            'Listed': 6,
            'Open': 5,
            'Benchmark 90': 4.5,
            'Benchmark 78': 4,
            'Benchmark 64': 3,
            'Maiden': 1,
            'Rating 0-58': 2
        }

    def extract_class_features(self, race_class_str):
        """
        Extract race class features

        Args:
            race_class_str: Race class string (e.g., 'Group 1', 'Benchmark 78')

        Returns:
            dict: Class features
        """
        features = {}

        # Raw class
        features['race_class'] = race_class_str

        # Class numerical score
        features['class_score'] = self.class_hierarchy.get(race_class_str, 2.5)

        # Binary indicators
        features['is_group_race'] = 1 if 'Group' in race_class_str else 0
        features['is_group_1'] = 1 if 'Group 1' in race_class_str else 0
        features['is_listed'] = 1 if 'Listed' in race_class_str else 0
        features['is_maiden'] = 1 if 'Maiden' in race_class_str else 0
        features['is_benchmark'] = 1 if 'Benchmark' in race_class_str else 0

        # Extract benchmark level if applicable
        if 'Benchmark' in race_class_str:
            import re
            match = re.search(r'Benchmark (\d+)', race_class_str)
            if match:
                features['benchmark_level'] = int(match.group(1))

        return features

    def extract_prize_money_features(self, prize_money):
        """
        Extract prize money features

        Args:
            prize_money: Total prize money (float)

        Returns:
            dict: Prize money features
        """
        features = {}

        # Raw prize money
        features['prize_money'] = prize_money

        # Log-transform (reduces skew)
        features['prize_money_log'] = np.log(prize_money + 1)

        # Prize money categories
        if prize_money >= 1000000:
            features['prize_category'] = 'million_plus'
            features['prize_score'] = 5
        elif prize_money >= 500000:
            features['prize_category'] = 'high'
            features['prize_score'] = 4
        elif prize_money >= 150000:
            features['prize_category'] = 'medium_high'
            features['prize_score'] = 3
        elif prize_money >= 50000:
            features['prize_category'] = 'medium'
            features['prize_score'] = 2
        else:
            features['prize_category'] = 'low'
            features['prize_score'] = 1

        return features

    def extract_field_size_features(self, field_size):
        """
        Extract field size features

        Args:
            field_size: Number of runners (int)

        Returns:
            dict: Field size features
        """
        features = {}

        # Raw field size
        features['field_size'] = field_size

        # Field size categories
        if field_size <= 8:
            features['field_category'] = 'small'
        elif field_size <= 14:
            features['field_category'] = 'medium'
        else:
            features['field_category'] = 'large'

        # Binary indicators
        features['is_small_field'] = 1 if field_size <= 8 else 0
        features['is_large_field'] = 1 if field_size >= 16 else 0

        # Field competitiveness (inverse of field size - smaller field = less competitive)
        features['field_competitiveness'] = 1 / field_size if field_size > 0 else 0

        return features
```

**Testing:**
```python
# tests/test_features/test_category_1_2.py
import pytest
from src.features.category_1_race_metadata import RaceMetadataFeatures, RaceClassFeatures

def test_distance_features():
    """Test distance feature extraction"""
    extractor = RaceMetadataFeatures()

    # Test 1200m sprint
    features = extractor.extract_distance_features(1200)
    assert features['distance_m'] == 1200
    assert features['distance_category'] == 'sprint'
    assert features['is_1200m'] == 1
    assert features['is_1600m'] == 0

    # Test 2000m middle distance
    features = extractor.extract_distance_features(2000)
    assert features['distance_category'] == 'stayers'
    assert features['is_2000m'] == 1

def test_class_features():
    """Test class feature extraction"""
    extractor = RaceClassFeatures()

    # Test Group 1
    features = extractor.extract_class_features('Group 1')
    assert features['class_score'] == 9
    assert features['is_group_1'] == 1
    assert features['is_group_race'] == 1

    # Test Benchmark
    features = extractor.extract_class_features('Benchmark 78')
    assert features['class_score'] == 4
    assert features['is_benchmark'] == 1
    assert features['benchmark_level'] == 78

def test_prize_money_features():
    """Test prize money feature extraction"""
    extractor = RaceClassFeatures()

    # Test high prize money
    features = extractor.extract_prize_money_features(1500000)
    assert features['prize_category'] == 'million_plus'
    assert features['prize_score'] == 5

    # Test low prize money
    features = extractor.extract_prize_money_features(30000)
    assert features['prize_category'] == 'low'
    assert features['prize_score'] == 1
```

**Day 3 Deliverables:**
- [x] Distance feature engineering complete
- [x] Venue feature engineering complete
- [x] Datetime feature engineering complete
- [x] All unit tests passing

---

### Day 4: Categories 2.1-2.3 (Class, Prize Money, Field Size)

*[Similar detailed breakdown with code examples, testing, and validation...]*

### Day 5: Database Schema & Storage

*[Complete implementation with code examples...]*

**Week 1 Milestone:** ✅ Basic race information collection functional. Can extract and store race metadata for any Australian race.

---

## WEEK 2: CATEGORY 3 (TRACK CONDITIONS) & CATEGORY 4 (BARRIER DRAW)

### Day 1: Track Condition Parsing
- [ ] Build track condition parser (convert "Good 3" to index)
- [ ] Create track condition numerical features (1-10 scale)
- [ ] Implement BOM Weather API integration
- [ ] Test weather data extraction

### Day 2: Track Bias Analysis
- [ ] Build historical track bias database
- [ ] Implement rail position effects
- [ ] Create bias quantification algorithm (-20 to +20 scale)
- [ ] Test bias calculations

### Day 3: Barrier Statistics Database
- [ ] Build barrier statistics database (3-year historical data)
- [ ] Calculate win rates by venue+distance+barrier
- [ ] Implement barrier-condition interaction matrix
- [ ] Test barrier advantage calculations

### Day 4: Barrier Integration
- [ ] Integrate barrier with track bias
- [ ] Implement barrier-rail interaction
- [ ] Create barrier suitability scoring
- [ ] Write unit tests

### Day 5: Categories 3-4 Integration
- [ ] Test track-barrier combined effects
- [ ] Validate against historical data
- [ ] Performance optimization
- [ ] Documentation

**Week 2 Milestone:** Track conditions and barrier analysis complete. Can predict barrier advantage based on conditions.

---

## WEEK 3: CATEGORIES 5-6 (WEIGHT & JOCKEY)

### Day 1: Weight Analysis
- [ ] Implement weight feature engineering
- [ ] Calculate weight differentials (vs topweight, vs median)
- [ ] Build weight-distance interaction analysis
- [ ] Test weight calculations

### Day 2: Jockey Statistics Database
- [ ] Build jockey statistics database
- [ ] Calculate career/recent win percentages
- [ ] Implement venue/distance specialization tracking
- [ ] Test jockey queries

### Day 3: Jockey Experience Classification
- [ ] Categorize jockey experience levels
- [ ] Calculate jockey consistency metrics
- [ ] Build jockey-weight interaction analysis
- [ ] Write unit tests

### Day 4: Weight-Jockey Integration
- [ ] Integrate weight burden with jockey skill
- [ ] Test mitigation effects
- [ ] Validate against historical data
- [ ] Performance optimization

### Day 5: Categories 5-6 Validation
- [ ] End-to-end testing
- [ ] Data quality checks
- [ ] Documentation
- [ ] Code review

**Week 3 Milestone:** Weight and jockey analysis complete. Can assess jockey suitability and weight impact.

---

## WEEK 4: CATEGORY 7 (TRAINER) & CATEGORIES 15-16 (SUITABILITY & INTANGIBLES)

### Day 1-2: Trainer Statistics
- [ ] Build trainer statistics database
- [ ] Calculate career/venue/distance/class win percentages
- [ ] Implement preparation pattern analysis (first-up, spell lengths)
- [ ] Test trainer queries

### Day 3: Track/Distance Suitability (Category 15)
- [ ] Implement venue-specific performance analysis
- [ ] Calculate distance-specific performance
- [ ] Build venue-distance combination analysis
- [ ] Test suitability calculations

### Day 4: Intangibles (Category 16)
- [ ] Implement fitness rating calculation (1-10 scale)
- [ ] Build peak performance window analysis
- [ ] Create preparation quality scoring
- [ ] Test intangibles features

### Day 5: Integration & Validation
- [ ] Integrate trainer with suitability
- [ ] Test trainer-jockey partnerships
- [ ] Validate fitness indicators
- [ ] Documentation

**Week 4 Milestone:** Trainer analysis and suitability assessment complete.

---

## WEEK 5: CATEGORY 8 (PACE) & CATEGORY 17 (CHEMISTRY)

### Day 1-2: Pace Analysis
- [ ] Build pace pressure calculator
- [ ] Implement run style classification
- [ ] Create pace-run style matching matrix
- [ ] Add speed ratings (1-100 scale)
- [ ] Test pace calculations

### Day 3: Sectional Data (Basic)
- [ ] Extract sectional times (600m/400m/200m)
- [ ] Calculate closing speed metrics
- [ ] Implement sectional rankings
- [ ] Test sectional analysis

### Day 4-5: Chemistry Analysis (Category 17)
- [ ] Build jockey-trainer partnership analyzer
- [ ] Implement jockey-horse combination analysis
- [ ] Calculate three-way synergy (jockey-trainer-horse)
- [ ] Test chemistry calculations
- [ ] Validate dream team detection

**Week 5 Milestone:** Pace, sectionals, and chemistry analysis complete.

---

## WEEK 6: CATEGORIES 9-10 (GEAR & TRIALS) & CATEGORY 12 (MARKET)

### Day 1: Gear Changes (Category 9)
- [ ] Implement gear change detection
- [ ] Calculate expected impact scores
- [ ] Build first-time blinkers analysis
- [ ] Test gear features

### Day 2-3: Barrier Trials (Category 10) **CRITICAL**
- [ ] Build Selenium automation for Racing.com authentication
- [ ] Extract trial data (performance, freshness)
- [ ] Calculate trial performance scoring (0-100)
- [ ] Test trial extraction (authentication success rate target: 90%)

### Day 4: Market Data (Category 12)
- [ ] Integrate Betfair API (exchange data)
- [ ] Extract Tab fixed odds
- [ ] Calculate odds movement (steamer/drifter detection)
- [ ] Build market momentum tracking

### Day 5: Integration
- [ ] Integrate gear with trials
- [ ] Connect market with all other categories
- [ ] Test steamer/drifter signals
- [ ] Documentation

**Week 6 Milestone:** Gear, trials (authentication working), and market data integrated. Competitive advantage secured.

---

## WEEK 7: CATEGORIES 11, 13-14 (TACTICS, WEATHER, HISTORICAL PERFORMANCE)

### Day 1: Tactics (Category 11)
- [ ] Analyze jockey riding styles
- [ ] Build trainer placement strategy analysis
- [ ] Test tactics features

### Day 2: Weather Sensitivity (Category 13)
- [ ] Implement weather performance analysis
- [ ] Detect respiratory concerns
- [ ] Build condition-specific performance tracking
- [ ] Test weather features

### Day 3-4: Historical Performance (Category 14) **MOST PREDICTIVE**
- [ ] Build comprehensive form analysis (last 5 starts)
- [ ] Calculate form score (0-100)
- [ ] Implement career statistics tracking
- [ ] Build first-up performance analysis
- [ ] Calculate consistency metrics
- [ ] Test all historical features

### Day 5: Integration & Validation
- [ ] Integrate all Categories 11, 13-14
- [ ] Test contradictions (form vs market)
- [ ] Validate historical performance predictiveness
- [ ] Documentation

**Week 7 Milestone:** Most predictive category (Historical Performance) complete. Core prediction capability 60%+.

---

## WEEK 8: CATEGORIES 18-21 (SPEED RATINGS, CLASS, SECTIONALS, PEDIGREE)

### Day 1-2: Speed Ratings (Category 18) **CRITICAL FOR QUANT**
- [ ] Implement Timeform-style rating calculator
- [ ] Build class-adjusted speed ratings
- [ ] Create condition-adjusted speed ratings
- [ ] Calculate field speed rankings
- [ ] Test all speed features

### Day 3: Class Ratings (Category 19)
- [ ] Extract/calculate official ratings
- [ ] Implement class drop/rise analysis
- [ ] Build par time analysis
- [ ] Test class features

### Day 4: Sectional Data (Category 20) - Detailed
- [ ] Expand sectional analysis (beyond Week 5 basics)
- [ ] Build sectional rankings within field
- [ ] Calculate acceleration metrics
- [ ] Test detailed sectionals

### Day 5: Pedigree (Category 21) & Phase 1 Completion
- [ ] Build pedigree database (sire/dam statistics)
- [ ] Implement distance suitability from breeding
- [ ] Calculate wet-track sire analysis
- [ ] **Phase 1 Integration Testing**
- [ ] **Validate all 21 categories working together**
- [ ] **Performance benchmarking**

**Week 8 Milestone:** ALL 21 categories implemented. Phase 1 complete. System operational with 70%+ prediction capability.

---

## PHASE 1 DELIVERABLES

1. **Data Collection Pipeline:** Functional scraper for all 21 categories
2. **Database:** Complete schema with historical data (3+ years)
3. **Feature Engineering:** 200+ quantitative features
4. **Category Integration:** Cross-category analysis functional
5. **API:** Basic API for race predictions
6. **Testing:** 80%+ code coverage
7. **Documentation:** Complete implementation docs

**Phase 1 Success Criteria:**
- [ ] Can collect data for any Australian race in <30 seconds
- [ ] All 21 categories extracting successfully (90%+ success rate)
- [ ] Database contains 3+ years historical data
- [ ] Feature engineering producing valid features (no NaN errors)
- [ ] Integration testing passing
- [ ] Prediction accuracy 70%+ on held-out test set

**Ready for Phase 2:** ML model training, head-to-head vs ChatGPT-5 testing, production deployment

---

**Document Complete: Part 20 (Phase 1 Implementation Roadmap)**
**Next: Part 21 (Phase 2 Roadmap - ML & Production)**
