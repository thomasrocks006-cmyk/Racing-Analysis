# 🌐 DATA SOURCE MAPPING & SCRAPING ARCHITECTURE

**Created:** November 12, 2025  
**Purpose:** Map all 21 taxonomy categories to specific data sources and define comprehensive scraping strategy  
**Status:** 🚨 CRITICAL - This is the foundation for building the actual system  
**References:** 
- MASTER_PLAN.md (Architecture)
- COMPREHENSIVE_TAXONOMY_MASTER (21 categories + integration matrices)
- FUSION_MODEL_ARCHITECTURE.md (Multi-agent requirements)

---

## 🎯 EXECUTIVE SUMMARY

**The Problem:**
The taxonomy defines what data we need across 21 categories. The fusion model defines how we'll use it. But **we haven't built the infrastructure to actually GET the data**.

**What This Document Provides:**
1. **Source Mapping**: Where to get data for each taxonomy category
2. **Scraping Strategy**: 15-40 sources per race (as specified in MASTER_PLAN.md)
3. **Implementation Roadmap**: Priority order for building scrapers
4. **Current State Audit**: What exists vs. what's missing

---

## 📊 CURRENT STATE AUDIT

### ✅ What Exists (Minimal):

```
src/data/scrapers/
├── racing_com.py        # ⚠️ Skeleton only (returns placeholders)
├── stewards.py          # ⚠️ Skeleton only (returns placeholders)
└── market_odds.py       # ⚠️ Skeleton only (returns placeholders)
```

**Reality Check:**
- All 3 scrapers are **placeholder code** that return hardcoded sample data
- **NO live web scraping is happening**
- **NO Betfair API integration**
- **NO barrier trials scraping**
- **NO gear changes automation**
- **NO expert commentary extraction**
- **NO stewards report parsing**

### ❌ What's Missing (95% of system):

**Categories 1-17 (Qualitative):** 0% data collection
**Categories 18-21 (Quantitative):** 10% data collection (basic structure only)

---

## 🗺️ COMPLETE DATA SOURCE MAPPING

### **TIER 1: OFFICIAL SOURCES (Required, Free, 100% Coverage)**

| Source | Categories Covered | Data Available | Access Method | Scraping Difficulty |
|--------|-------------------|----------------|---------------|-------------------|
| **Racing.com** | 1-10, 14, 18-21 | Race cards, form, results, barrier draws, weights, gear | Public HTML scraping | ⭐⭐ Medium |
| **Racing Victoria** | 2, 3, 5, 6 | Stewards reports, gear changes, track conditions | Public HTML scraping | ⭐⭐⭐ Hard (PDF parsing) |
| **Tab.com.au** | 1, 2, 8, 14 | Race cards, market odds, betting stats | Public HTML scraping | ⭐⭐ Medium |
| **Weatherzone.com.au** | 3 | Track weather, forecast | Public API (free tier) | ⭐ Easy |

### **TIER 2: PREMIUM DATA (Paid, High Quality)**

| Source | Categories Covered | Data Available | Cost | Scraping Difficulty |
|--------|-------------------|----------------|------|-------------------|
| **Punters.com.au** | 7, 8, 9, 10, 14, 15 | Form ratings, track bias, expert tips | $30/month | ⭐⭐ Medium (paywall) |
| **Timeform Australia** | 18, 19, 20 | Speed ratings, class ratings, sectionals | $50/month | ⭐⭐⭐ Hard (API or scraping) |
| **Champion Data** | 20, 21 | Sectional times, pace analytics | $100/month | ⭐⭐⭐⭐ Very hard (API only) |
| **Betfair API** | 8, 9 | Live market odds, liquidity, movements | Free (account required) | ⭐⭐ Medium (API integration) |

### **TIER 3: COMMUNITY & EXPERT SOURCES**

| Source | Categories Covered | Data Available | Access Method | Scraping Difficulty |
|--------|-------------------|----------------|---------------|-------------------|
| **The Races** (theraces.com.au) | 10, 11, 12 | Expert tips, track commentary | Public HTML scraping | ⭐⭐ Medium |
| **Racing Post** (international) | 15, 16, 17 | Pedigree analysis, bloodstock | Public HTML scraping | ⭐⭐⭐ Hard |
| **Twitter/X Racing Experts** | 10, 11 | Insider info, late scratchings | API scraping | ⭐⭐ Medium |
| **YouTube Racing Channels** | 10, 11 | Video analysis, expert previews | Video + transcript | ⭐⭐⭐⭐ Very hard |

---

## 📋 CATEGORY-BY-CATEGORY SOURCE MAPPING

### **CATEGORY 1: RACE METADATA (Distance, Venue, Date, Race Number)**

**Prediction Power:** 3-8%  
**Pipeline:** Both (Qual + Quant)  
**Priority:** 🔥 Phase 1 Week 1 (CRITICAL - foundational)

**Primary Sources:**
1. **Racing.com Form Guide** ⭐⭐⭐⭐⭐
   - URL: `https://www.racing.com/form-guide/thoroughbred/{date}/{venue}/race-{number}`
   - Data: Distance, venue, race name, race type, prize money
   - Format: HTML scraping
   - Coverage: 100% of Australian racing
   - Update frequency: Real-time
   
2. **Tab.com.au Race Card**
   - URL: `https://www.tab.com.au/racing/{state}/{venue}/{date}/R{number}`
   - Data: Same as Racing.com (backup source)
   - Format: HTML scraping
   - Coverage: 100%

**Scraper Implementation:**
```python
# src/data/scrapers/racing_com.py (NEEDS COMPLETE REWRITE)

class RacingComScraper:
    """
    CURRENT STATE: Returns placeholder data
    NEEDED: Actual BeautifulSoup web scraping
    """
    
    def scrape_race_metadata(self, venue: str, date: str, race_num: int) -> dict:
        """
        Extract Category 1 data from Racing.com
        
        Returns:
            {
                'distance_meters': 1200,
                'venue': 'flemington',
                'race_date': '2025-11-12',
                'race_number': 7,
                'race_name': 'VRC Emirates Stakes',
                'race_type': 'Group 1',
                'prize_money': 1000000,
                'track_condition': 'Good 4'
            }
        """
        url = f"https://www.racing.com/form-guide/thoroughbred/{date}/{venue}/race-{race_num}"
        
        # CURRENT: Returns fake data
        # NEEDED: Real scraping logic below
        
        response = requests.get(url, headers=self.HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract distance
        distance_elem = soup.select_one('.race-distance')
        distance = int(distance_elem.text.replace('m', ''))
        
        # Extract race name
        race_name_elem = soup.select_one('.race-name')
        race_name = race_name_elem.text.strip()
        
        # ... (continue for all fields)
        
        return metadata
```

**Implementation Status:**
- ❌ Live scraping: NOT IMPLEMENTED
- ❌ Error handling: NOT IMPLEMENTED
- ❌ Rate limiting: NOT IMPLEMENTED
- ❌ Data validation: MINIMAL

---

### **CATEGORY 2: RACE TYPE & CLASS (Group 1/2/3, Listed, BM, Maiden, Condition)**

**Prediction Power:** 8-12%  
**Pipeline:** Both (Qual + Quant)  
**Priority:** 🔥 Phase 1 Week 1 (CRITICAL)

**Primary Sources:**
1. **Racing.com Form Guide**
   - Data: Race class, BM rating, race conditions
   - Same URL structure as Category 1
   
2. **Racing Victoria Website**
   - URL: `https://www.racingvictoria.com.au/racing-information`
   - Data: Official race classifications, prize money brackets
   - Format: HTML scraping

**Scraper Implementation Needed:**
```python
def scrape_race_class(self, race_url: str) -> dict:
    """
    Extract race classification and class information
    
    Returns:
        {
            'race_class': 'Group 1',  # Group 1/2/3, Listed, Open, BM, Maiden
            'benchmark_rating': 100,   # 60-145 (if BM race)
            'race_grade': 'A',         # A/B/C/D classification
            'class_weight': 1.0,       # Multiplier for class adjustment
            'prize_money': 1000000,    # Total prize pool
            'is_restricted': False,    # Age/sex restrictions
            'restrictions': []         # List of restrictions if any
        }
    """
    # IMPLEMENTATION NEEDED
    pass
```

---

### **CATEGORY 3: TRACK CONDITIONS (Going, Weather, Rail Position)**

**Prediction Power:** 10-15%  
**Pipeline:** Both (Qual + Quant)  
**Priority:** 🔥 Phase 1 Week 1-2

**Primary Sources:**
1. **Racing.com Live Updates**
   - URL: `https://www.racing.com/live-vision/{venue}/{date}`
   - Data: Track condition (Heavy 10 → Firm 1), rail position, weather
   - Format: HTML scraping + live updates
   - Update frequency: Every 30 minutes on race day
   
2. **Weatherzone API**
   - URL: `https://api.weatherzone.com.au/v3/location/{lat}/{lng}/forecast`
   - Data: Temperature, wind speed/direction, humidity, rainfall
   - Format: JSON API (free tier: 1000 calls/day)
   - Coverage: All Australian venues

3. **Racing Victoria Stewards Reports**
   - URL: `https://www.racingvictoria.com.au/stewards-reports/{date}/{venue}`
   - Data: Official track condition, rail position, upgrades/downgrades
   - Format: PDF parsing (pypdf2)

**Scraper Implementation Needed:**
```python
class WeatherScraper:
    """NEW SCRAPER - Doesn't exist yet"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weatherzone.com.au/v3"
        
    def get_venue_weather(self, venue: str, race_time: datetime) -> dict:
        """
        Get weather forecast for race venue at race time
        
        Returns:
            {
                'temperature_c': 22,
                'wind_speed_kmh': 15,
                'wind_direction': 'NW',
                'humidity_pct': 60,
                'rainfall_mm': 0,
                'cloud_cover_pct': 40,
                'forecast_time': '2025-11-12T14:30:00'
            }
        """
        # Get venue coordinates
        coords = VENUE_COORDINATES.get(venue)
        
        # Call Weatherzone API
        url = f"{self.base_url}/location/{coords['lat']}/{coords['lng']}/forecast"
        response = requests.get(url, params={'apikey': self.api_key})
        
        # Parse forecast closest to race time
        forecast = self._find_closest_forecast(response.json(), race_time)
        
        return forecast

class TrackConditionScraper:
    """NEW SCRAPER - Doesn't exist yet"""
    
    def scrape_track_condition(self, venue: str, date: str) -> dict:
        """
        Get official track condition from Racing.com or RV
        
        Returns:
            {
                'track_condition': 'Good 4',
                'track_rating': 4,  # 1-10 scale (10=Heavy)
                'rail_position': 'True',  # True/+3m/+6m/+9m etc
                'track_bias': 'Favoring on-pace runners',
                'penetrometer_reading': 4.8,
                'last_updated': '2025-11-12T13:00:00'
            }
        """
        # IMPLEMENTATION NEEDED
        pass
```

**Implementation Status:**
- ❌ Weather API: NOT INTEGRATED
- ❌ Track condition live scraping: NOT IMPLEMENTED
- ❌ Rail position extraction: NOT IMPLEMENTED
- ❌ Historical track condition database: NOT CREATED

---

### **CATEGORY 4: BARRIER DRAW (Post Position Effects)**

**Prediction Power:** 5-8%  
**Pipeline:** Both (Qual + Quant)  
**Priority:** 🔥 Phase 1 Week 1-2

**Primary Sources:**
1. **Racing.com Form Guide** (same as Category 1)
   - Data: Barrier number per horse
   
2. **Punters.com.au Barrier Stats**
   - URL: `https://www.punters.com.au/track-stats/{venue}/barriers`
   - Data: Historical barrier win %, distance-specific bias
   - Format: HTML scraping (paywall)

**Scraper Implementation Needed:**
```python
def scrape_barrier_stats(self, venue: str, distance: int) -> dict:
    """
    Get venue-specific barrier bias statistics
    
    Returns:
        {
            'venue': 'flemington',
            'distance': 1200,
            'barrier_stats': {
                1: {'win_pct': 12.3, 'place_pct': 32.1, 'avg_position': 4.2},
                2: {'win_pct': 11.8, 'place_pct': 30.5, 'avg_position': 4.5},
                # ... barriers 1-20
            },
            'inside_bias': True,  # Barriers 1-6 advantaged
            'outside_bias': False,
            'data_sample_size': 247  # Races analyzed
        }
    """
    # IMPLEMENTATION NEEDED
    pass
```

---

### **CATEGORY 5: JOCKEY (Rider Skill, Form, Venue Performance)**

**Prediction Power:** 8-12%  
**Pipeline:** Both (Qual + Quant)  
**Priority:** 🔥 Phase 1 Week 2

**Primary Sources:**
1. **Racing.com Jockey Stats**
   - URL: `https://www.racing.com/jockey/{jockey-name}/statistics`
   - Data: Win rate, place rate, strike rate, earnings
   
2. **Tab.com.au Jockey Form**
   - URL: `https://www.tab.com.au/form/racing/jockey/{id}`
   - Data: Last 10 starts, venue-specific stats

**Scraper Implementation Needed:**
```python
class JockeyScraper:
    """NEW SCRAPER - Doesn't exist yet"""
    
    def scrape_jockey_profile(self, jockey_name: str) -> dict:
        """
        Get comprehensive jockey statistics
        
        Returns:
            {
                'jockey_name': 'Jamie Kah',
                'jockey_id': 'JK001',
                'career_stats': {
                    'total_rides': 5243,
                    'wins': 1247,
                    'places': 2103,
                    'win_pct': 23.8,
                    'place_pct': 40.1
                },
                'last_12_months': {
                    'rides': 623,
                    'wins': 152,
                    'win_pct': 24.4
                },
                'venue_stats': {
                    'flemington': {'rides': 234, 'wins': 67, 'win_pct': 28.6},
                    # ... other venues
                },
                'distance_stats': {
                    '1200': {'rides': 543, 'wins': 134, 'win_pct': 24.7},
                    # ... other distances
                },
                'trainer_combos': {
                    'Ciaron Maher': {'rides': 145, 'wins': 52, 'win_pct': 35.9},
                    # ... other trainers
                }
            }
        """
        # IMPLEMENTATION NEEDED
        pass
```

**Implementation Status:**
- ❌ Jockey stats scraping: NOT IMPLEMENTED
- ❌ Jockey-trainer combo analysis: NOT IMPLEMENTED
- ❌ Venue-specific jockey performance: NOT IMPLEMENTED

---

### **CATEGORY 6: TRAINER (Preparation Style, Stable Form)**

**Prediction Power:** 8-12%  
**Pipeline:** Both (Qual + Quant)  
**Priority:** 🔥 Phase 1 Week 2

**Primary Sources:**
1. **Racing.com Trainer Stats** (same structure as jockey)
2. **Punters.com.au Trainer Form**
   - Data: Recent stable form, first-up stats, spell stats

**Scraper Implementation Needed:**
```python
class TrainerScraper:
    """NEW SCRAPER - Doesn't exist yet"""
    
    def scrape_trainer_profile(self, trainer_name: str) -> dict:
        """
        Returns: Similar to jockey stats + preparation-specific data
        """
        # IMPLEMENTATION NEEDED
        pass
```

---

### **CATEGORY 7: GEAR CHANGES (Blinkers, Tongue Tie, etc.)**

**Prediction Power:** 5-8%  
**Pipeline:** Qualitative (GPT-5 analysis)  
**Priority:** 🔥 Phase 1 Week 2-3

**Primary Sources:**
1. **Racing Victoria Gear Changes**
   - URL: `https://www.racingvictoria.com.au/gear-changes/{date}`
   - Data: Gear added/removed, first-time gear
   - Format: PDF parsing or HTML scraping
   
2. **Racing.com Race Card** (gear column)
   - Data: Current gear per horse

**Scraper Implementation Needed:**
```python
class GearChangesScraper:
    """NEW SCRAPER - Doesn't exist yet"""
    
    def scrape_daily_gear_changes(self, date: str) -> list[dict]:
        """
        Get all gear changes for a specific race day
        
        Returns:
            [
                {
                    'horse_name': 'Anamoe',
                    'race_id': 'FLE-2025-11-12-R7',
                    'gear_added': ['Blinkers'],
                    'gear_removed': [],
                    'first_time_gear': ['Blinkers'],
                    'gear_reason': 'Improve focus'  # If available from stewards
                },
                ...
            ]
        """
        # IMPLEMENTATION NEEDED
        pass
```

**Implementation Status:**
- ❌ Gear changes scraping: NOT IMPLEMENTED
- ❌ Historical gear impact analysis: NOT IMPLEMENTED
- ❌ Stewards gear explanations: NOT EXTRACTED

---

### **CATEGORY 8: MARKET ODDS (Betfair, TAB, Bookmakers)**

**Prediction Power:** 15-20% (HIGHEST predictive power)  
**Pipeline:** Both (Qual + Quant)  
**Priority:** 🔥🔥🔥 Phase 1 Week 1 (CRITICAL - Value identification)

**Primary Sources:**
1. **Betfair API** ⭐⭐⭐⭐⭐
   - URL: `https://api.betfair.com/exchange/betting/rest/v1/`
   - Data: Live odds, liquidity, market movements, steam, drift
   - Format: REST API (requires account + app key)
   - Coverage: 95% of Australian racing
   - Update frequency: Real-time (every 1-2 seconds)
   
2. **Tab.com.au Fixed Odds**
   - URL: `https://www.tab.com.au/racing/{state}/{venue}/{date}/R{number}`
   - Data: TAB fixed odds, fluctuations
   - Format: HTML scraping
   
3. **Oddschecker.com**
   - URL: `https://www.oddschecker.com/horse-racing/australia/{venue}/{race}`
   - Data: Multiple bookmaker odds comparison
   - Format: HTML scraping

**Scraper Implementation Needed:**
```python
class BetfairAPI:
    """NEW INTEGRATION - Critical for value betting"""
    
    def __init__(self, app_key: str, session_token: str):
        self.app_key = app_key
        self.session_token = session_token
        self.base_url = "https://api.betfair.com/exchange/betting/rest/v1"
        
    def get_market_odds(self, market_id: str) -> dict:
        """
        Get live Betfair odds for a race
        
        Returns:
            {
                'market_id': '1.234567890',
                'status': 'OPEN',
                'total_matched': 125340.50,  # Total $ matched
                'runners': [
                    {
                        'selection_id': 12345,
                        'runner_name': 'Anamoe',
                        'back_prices': [
                            {'price': 3.5, 'size': 1234.50},  # $1234.50 available at 3.5
                            {'price': 3.45, 'size': 567.80},
                            {'price': 3.4, 'size': 890.20}
                        ],
                        'lay_prices': [
                            {'price': 3.55, 'size': 987.30},
                            {'price': 3.6, 'size': 1456.70},
                            {'price': 3.65, 'size': 789.50}
                        ],
                        'last_price_traded': 3.5,
                        'total_matched': 45678.90,  # $ matched on this runner
                        'implied_probability': 0.286  # 1 / 3.5
                    },
                    # ... other runners
                ],
                'timestamp': '2025-11-12T14:25:33Z'
            }
        """
        # IMPLEMENTATION NEEDED
        pass
    
    def track_market_movements(self, market_id: str, duration_mins: int = 60) -> list[dict]:
        """
        Track odds movements over time
        
        Returns:
            [
                {'timestamp': '14:00:00', 'runner': 'Anamoe', 'price': 4.0},
                {'timestamp': '14:15:00', 'runner': 'Anamoe', 'price': 3.7},  # Steam
                {'timestamp': '14:25:00', 'runner': 'Anamoe', 'price': 3.5},
                # ...
            ]
        """
        # IMPLEMENTATION NEEDED
        pass
```

**Implementation Status:**
- ❌ Betfair API: NOT INTEGRATED
- ❌ Market movements tracking: NOT IMPLEMENTED
- ❌ Steam/drift detection: NOT IMPLEMENTED
- ❌ Multi-bookmaker odds comparison: NOT IMPLEMENTED

---

### **CATEGORY 9: BETTING PATTERNS (Market Confidence, Steam, Drift)**

**Prediction Power:** 10-15%  
**Pipeline:** Qualitative (GPT-5 analysis)  
**Priority:** 🔥 Phase 1 Week 3-4

**Primary Sources:**
1. **Betfair API** (same as Category 8)
   - Data: Odds movements, liquidity changes, market sentiment
   
2. **Racing.com Market Movers**
   - URL: `https://www.racing.com/market-movers`
   - Data: Biggest odds changes, steam alerts

**Scraper Implementation Needed:**
```python
class MarketAnalyzer:
    """NEW ANALYZER - Pattern detection"""
    
    def detect_steam(self, odds_history: list[dict]) -> dict:
        """
        Detect steam (rapid odds shortening due to heavy backing)
        
        Returns:
            {
                'is_steam': True,
                'steam_magnitude': 'strong',  # weak/moderate/strong
                'odds_change': 6.0 -> 4.0,    # 33% reduction
                'timeframe': '15 minutes',
                'money_behind_move': 23456.70,  # Estimated $ causing move
                'confidence': 'high'  # Likely informed money
            }
        """
        # IMPLEMENTATION NEEDED
        pass
    
    def detect_drift(self, odds_history: list[dict]) -> dict:
        """
        Detect drift (odds lengthening, negative sentiment)
        """
        # IMPLEMENTATION NEEDED
        pass
```

---

### **CATEGORY 10: EXPERT COMMENTARY & TIPS**

**Prediction Power:** 5-8%  
**Pipeline:** Qualitative (GPT-5 synthesis)  
**Priority:** 🟡 Phase 2 Week 1-2

**Primary Sources:**
1. **Punters.com.au Expert Tips**
   - URL: `https://www.punters.com.au/racing/{venue}/{date}/race-{num}`
   - Data: Expert selections, ratings, comments
   
2. **The Races Preview**
   - URL: `https://www.theraces.com.au/races/{venue}/{date}`
   - Data: Race previews, horse-by-horse analysis
   
3. **Twitter Racing Experts**
   - Accounts: @tjcaulfield, @racing, @thetrots, etc.
   - Data: Late tips, insider info, scratching alerts

**Scraper Implementation Needed:**
```python
class ExpertCommentaryScraper:
    """NEW SCRAPER - Multi-source expert analysis"""
    
    def scrape_expert_tips(self, race_id: str) -> list[dict]:
        """
        Aggregate expert tips from multiple sources
        
        Returns:
            [
                {
                    'expert_name': 'Greg Radley',
                    'source': 'punters.com.au',
                    'selections': [
                        {'horse': 'Anamoe', 'position': 1, 'confidence': 'strong'},
                        {'horse': 'Zaaki', 'position': 2, 'confidence': 'moderate'},
                    ],
                    'commentary': 'Anamoe looks hard to beat from the inside gate...',
                    'timestamp': '2025-11-12T10:00:00'
                },
                # ... other experts
            ]
        """
        # IMPLEMENTATION NEEDED
        pass
    
    def scrape_twitter_racing_intel(self, race_date: str) -> list[dict]:
        """
        Scrape Twitter for late breaking news
        
        Returns:
            [
                {
                    'tweet_id': '1234567890',
                    'author': '@tjcaulfield',
                    'text': 'Hearing Anamoe trialled brilliantly Tuesday...',
                    'timestamp': '2025-11-11T18:30:00',
                    'mentions': ['Anamoe'],
                    'sentiment': 'positive'
                },
                # ...
            ]
        """
        # IMPLEMENTATION NEEDED
        pass
```

---

### **CATEGORY 11: STEWARDS REPORTS (Incidents, Explanations)**

**Prediction Power:** 5-10%  
**Pipeline:** Qualitative (GPT-5 analysis)  
**Priority:** 🔥 Phase 1 Week 3

**Primary Sources:**
1. **Racing Victoria Stewards Reports**
   - URL: `https://www.racingvictoria.com.au/stewards-reports/{date}/{venue}`
   - Data: Race incidents, inquiries, explanations, gear changes
   - Format: PDF parsing (pypdf2 + regex)
   
2. **Racing.com Stewards Notes**
   - URL: `https://www.racing.com/stewards/{venue}/{date}`
   - Data: Same as RV but HTML format

**Scraper Implementation Needed:**
```python
class StewardsReportScraper:
    """EXISTING but needs COMPLETE REWRITE"""
    
    def scrape_stewards_report(self, venue: str, date: str) -> list[dict]:
        """
        Extract stewards reports and parse incidents
        
        Returns:
            [
                {
                    'race_number': 7,
                    'horse_name': 'Anamoe',
                    'incident_type': 'checked',
                    'description': 'Checked near 400m when runner to inside shifted out',
                    'severity': 'moderate',
                    'jockey_inquiry': False,
                    'stewards_action': 'No action taken',
                    'gear_changes_ordered': []
                },
                {
                    'race_number': 7,
                    'horse_name': 'Zaaki',
                    'incident_type': 'vet_check',
                    'description': 'Underwent post-race veterinary examination, cleared to race',
                    'severity': 'low',
                    'next_race_clearance': True
                },
                # ...
            ]
        """
        # CURRENT: Returns placeholder
        # NEEDED: PDF parsing + regex extraction
        pass
```

**Implementation Status:**
- ❌ PDF parsing: NOT IMPLEMENTED
- ❌ Incident extraction: NOT IMPLEMENTED
- ❌ Historical stewards database: NOT CREATED

---

### **CATEGORY 12: BARRIER TRIALS (Pre-Race Trials, Jump-Outs)**

**Prediction Power:** 8-12%  
**Pipeline:** Qualitative (GPT-5 analysis)  
**Priority:** 🔥 Phase 2 Week 1-2

**Primary Sources:**
1. **Racing.com Barrier Trials**
   - URL: `https://www.racing.com/barrier-trials/{venue}/{date}`
   - Data: Trial results, videos, comments
   - Format: HTML scraping + video metadata
   
2. **Punters.com.au Trial Analysis**
   - URL: `https://www.punters.com.au/trials/{venue}/{date}`
   - Data: Expert trial analysis, ratings

**Scraper Implementation Needed:**
```python
class BarrierTrialsScraper:
    """NEW SCRAPER - Critical for first-up runners"""
    
    def scrape_horse_trials(self, horse_name: str, lookback_days: int = 60) -> list[dict]:
        """
        Get recent barrier trials for a specific horse
        
        Returns:
            [
                {
                    'trial_date': '2025-11-05',
                    'venue': 'cranbourne',
                    'distance': 800,
                    'track_condition': 'Good 4',
                    'finishing_position': 2,
                    'margin_to_winner': 0.5,  # lengths
                    'finishing_time': 47.2,  # seconds
                    'sectionals': {'L400': 23.1, 'L200': 11.8},
                    'jockey': 'Jamie Kah',
                    'trial_comment': 'Looked fit and well, worked home strongly',
                    'video_url': 'https://www.racing.com/watch/trial/12345',
                    'expert_rating': 8.5  # out of 10
                },
                # ... older trials
            ]
        """
        # IMPLEMENTATION NEEDED
        pass
```

**Implementation Status:**
- ❌ Barrier trials scraping: NOT IMPLEMENTED
- ❌ Trial video analysis: NOT IMPLEMENTED
- ❌ Trial performance database: NOT CREATED

---

### **CATEGORY 13-14: HORSE FORM & PERFORMANCE HISTORY**

**Prediction Power:** 15-20% (CRITICAL)  
**Pipeline:** Both (Qual + Quant)  
**Priority:** 🔥🔥🔥 Phase 1 Week 1-2

**Primary Sources:**
1. **Racing.com Form Guide**
   - URL: `https://www.racing.com/form-guide/thoroughbred/{date}/{venue}/race-{num}`
   - Data: Last 5-10 starts, positions, margins, sectionals
   - Format: HTML scraping
   
2. **Tab.com.au Detailed Form**
   - URL: `https://www.tab.com.au/form/racing/horse/{id}`
   - Data: Complete racing history, career stats

**Scraper Implementation Needed:**
```python
class HorseFormScraper:
    """NEW SCRAPER - Most important quantitative data"""
    
    def scrape_horse_history(self, horse_name: str) -> dict:
        """
        Get complete racing history for a horse
        
        Returns:
            {
                'horse_name': 'Anamoe',
                'age': 5,
                'sex': 'Gelding',
                'color': 'Bay',
                'sire': 'Street Boss',
                'dam': 'Anamato',
                'trainer': 'James Cummings',
                'owner': 'Godolphin',
                'career_stats': {
                    'starts': 23,
                    'wins': 11,
                    'places': 17,
                    'prize_money': 4567890
                },
                'race_history': [
                    {
                        'date': '2025-10-28',
                        'venue': 'flemington',
                        'distance': 1600,
                        'track_condition': 'Good 4',
                        'barrier': 5,
                        'weight': 58.5,
                        'jockey': 'Jamie Kah',
                        'position': 1,
                        'margin': 1.5,  # winning margin
                        'finishing_time': 93.42,
                        'sectionals': {'L600': 34.2, 'L400': 22.8, 'L200': 11.3},
                        'speed_rating': 105,
                        'class_rating': 102,
                        'race_class': 'Group 2',
                        'prize_money': 250000,
                        'comment': 'Won easily, strong finish'
                    },
                    # ... previous starts
                ],
                'distance_stats': {
                    '1200': {'starts': 5, 'wins': 2, 'win_pct': 0.4},
                    '1600': {'starts': 12, 'wins': 7, 'win_pct': 0.583},
                    # ...
                },
                'venue_stats': {
                    'flemington': {'starts': 8, 'wins': 5, 'win_pct': 0.625},
                    # ...
                },
                'track_condition_stats': {
                    'Good 4': {'starts': 15, 'wins': 9, 'win_pct': 0.6},
                    'Soft 7': {'starts': 3, 'wins': 0, 'win_pct': 0.0},
                    # ...
                }
            }
        """
        # IMPLEMENTATION NEEDED
        pass
```

**Implementation Status:**
- ❌ Complete form scraping: NOT IMPLEMENTED
- ❌ Historical database: MINIMAL (only placeholder data)
- ❌ Sectionals extraction: NOT IMPLEMENTED
- ❌ Career statistics aggregation: NOT IMPLEMENTED

---

### **CATEGORY 15-17: PEDIGREE & BLOODSTOCK**

**Prediction Power:** 5-8%  
**Pipeline:** Quantitative (Category 21)  
**Priority:** 🟡 Phase 2 Week 3-4

**Primary Sources:**
1. **Racing Post Pedigree**
   - URL: `https://www.racingpost.com/bloodstock/horse/{horse-name}/pedigree`
   - Data: Sire, dam, siblings, progeny performance
   
2. **Arion Pedigrees**
   - URL: `https://www.arionpedigrees.com`
   - Data: Australian pedigree database

**Scraper Implementation Needed:**
```python
class PedigreeScraper:
    """NEW SCRAPER - For quantitative pedigree modeling"""
    
    def scrape_pedigree_data(self, horse_name: str) -> dict:
        """
        Returns: Sire/dam/siblings performance, distance/surface preferences
        """
        # IMPLEMENTATION NEEDED
        pass
```

---

### **CATEGORY 18-21: QUANTITATIVE ANALYTICS (Speed, Class, Sectionals, Pedigree)**

**Prediction Power:** 20-25% (HIGHEST - ML models)  
**Pipeline:** Quantitative (ML training)  
**Priority:** 🔥🔥🔥 Phase 1 Week 2-4

**Primary Sources:**
1. **Timeform Australia**
   - URL: `https://www.timeform.com.au`
   - Data: Speed ratings, class ratings
   - Format: API or scraping (paid)
   
2. **Champion Data**
   - URL: API only (https://championdata.com.au)
   - Data: Sectional times (L600/L400/L200)
   - Format: Paid API
   
3. **Racing.com Sectionals**
   - URL: `https://www.racing.com/results/{venue}/{date}/race-{num}`
   - Data: Free sectional times (limited coverage)

**Scraper Implementation Needed:**
```python
class SectionalsScraper:
    """NEW SCRAPER - Critical for speed modeling"""
    
    def scrape_race_sectionals(self, race_id: str) -> dict:
        """
        Get sectional times for all runners in a race
        
        Returns:
            {
                'race_id': 'FLE-2025-11-12-R7',
                'distance': 1600,
                'track_condition': 'Good 4',
                'sectionals': [
                    {
                        'horse_name': 'Anamoe',
                        'finishing_position': 1,
                        'L1000_time': 57.8,
                        'L800_time': 46.2,
                        'L600_time': 34.2,
                        'L400_time': 22.8,
                        'L200_time': 11.3,
                        'L100_time': 5.8,
                        'final_time': 93.42,
                        'avg_stride_length': 7.2,  # If available
                        'top_speed_kmh': 65.3      # If available
                    },
                    # ... other horses
                ]
            }
        """
        # IMPLEMENTATION NEEDED
        pass
```

---

## 🏗️ SCRAPING ARCHITECTURE

### **Multi-Source Orchestration (15-40 sources per race)**

As per MASTER_PLAN.md, the qualitative pipeline requires **15-40 targeted sources per race**. Current implementation: **0 sources**.

**Architecture Needed:**

```python
class MultiSourceOrchestrator:
    """
    Coordinates scraping from 15-40 sources per race
    As specified in MASTER_PLAN.md Stage 2: Parallel Scraping
    """
    
    def __init__(self):
        self.scrapers = {
            'racing_com': RacingComScraper(),
            'tab': TabScraper(),
            'betfair': BetfairAPI(),
            'weather': WeatherScraper(),
            'stewards': StewardsReportScraper(),
            'trials': BarrierTrialsScraper(),
            'gear': GearChangesScraper(),
            'experts': ExpertCommentaryScraper(),
            'twitter': TwitterRacingScraper(),
            'market': MarketAnalyzer(),
            'sectionals': SectionalsScraper(),
            'pedigree': PedigreeScraper(),
            # ... 40+ scrapers total
        }
        
    async def scrape_race_comprehensive(self, race_id: str) -> dict:
        """
        Scrape 15-40 sources in parallel for a single race
        
        Returns complete data package for qualitative + quantitative pipelines
        """
        # Generate source plan (Stage 1: Source Planning with Gemini)
        source_plan = await self.generate_source_plan(race_id)
        
        # Execute parallel scraping (Stage 2: Parallel Scraping)
        tasks = []
        for source in source_plan:
            scraper = self.scrapers[source['type']]
            task = scraper.scrape_async(source['url'], source['params'])
            tasks.append(task)
        
        # Gather all results concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Validate completeness (90%+ target)
        completeness = self.calculate_completeness(results)
        
        return {
            'race_id': race_id,
            'sources_attempted': len(source_plan),
            'sources_successful': len([r for r in results if not isinstance(r, Exception)]),
            'completeness_pct': completeness,
            'data': results,
            'timestamp': datetime.now().isoformat()
        }
    
    async def generate_source_plan(self, race_id: str) -> list[dict]:
        """
        Stage 1: Source Planning (Gemini 2.5 Flash)
        Generate 15-40 targeted sources for this specific race
        
        Cost: $0.02/race
        Time: 30-60 seconds
        """
        # IMPLEMENTATION NEEDED
        # This requires Gemini API integration
        pass
```

---

## 🚀 IMPLEMENTATION ROADMAP

### **Phase 1: Foundation (Weeks 1-4) - CRITICAL PATH**

#### Week 1: Core Official Sources
- [ ] **Racing.com scraper** (Categories 1-6, 13-14)
  - Live web scraping (replace placeholder)
  - Form guide extraction
  - Historical results database population
  - Target: 1000+ historical races
  
- [ ] **Betfair API integration** (Categories 8-9)
  - API authentication
  - Live odds polling
  - Market movements tracking
  - Historical odds database

- [ ] **Weather API** (Category 3)
  - Weatherzone integration
  - Venue coordinate mapping
  - Historical weather database

#### Week 2: Extended Official Sources
- [ ] **Tab.com.au scraper** (backup data source)
- [ ] **Stewards reports** (Category 11)
  - PDF parsing
  - Incident extraction
  - Historical stewards database
  
- [ ] **Gear changes** (Category 7)
  - Racing Victoria gear scraping
  - First-time gear detection

#### Week 3-4: Qualitative Sources
- [ ] **Barrier trials** (Category 12)
- [ ] **Expert commentary** (Category 10)
- [ ] **Twitter racing intel**
- [ ] **Multi-source orchestration framework**

### **Phase 2: Premium & Advanced (Weeks 5-8)**

#### Week 5-6: Premium Data
- [ ] **Timeform integration** (Categories 18-19)
- [ ] **Champion Data API** (Category 20)
- [ ] **Punters.com.au** (enhanced analytics)

#### Week 7-8: Advanced Analytics
- [ ] **Pedigree scraping** (Categories 15-17, 21)
- [ ] **Market pattern detection** (Category 9)
- [ ] **Video analysis** (barrier trials, replays)

---

## 📊 DATA COMPLETENESS TARGETS

As per MASTER_PLAN.md:

| Target | Required | Current | Gap |
|--------|----------|---------|-----|
| **Historical Races** | 1000+ races | ~10 races | **-99%** |
| **Data Completeness** | 80-90% per race | 10% | **-75%** |
| **Official Data Access** | 90%+ | 5% | **-85%** |
| **Sources per Race** | 15-40 sources | 1-2 sources | **-93%** |
| **Qualitative Coverage** | Categories 1-17 | 0% | **-100%** |
| **Quantitative Coverage** | Categories 18-21 | 15% | **-85%** |

---

## ⚠️ CRITICAL ISSUES SUMMARY

### **Issue #1: No Live Data Collection**
- All scrapers return placeholder data
- Cannot test or validate system
- Cannot run in production
- **SEVERITY: CRITICAL - System is non-functional**

### **Issue #2: Missing 95% of Data Sources**
- Only 3 scrapers exist (all placeholders)
- Need 40+ scrapers for full coverage
- Missing ALL qualitative sources
- **SEVERITY: CRITICAL - Cannot build qualitative pipeline**

### **Issue #3: No Betfair Integration**
- Market odds = 15-20% of predictive power
- Value betting impossible without odds
- No steam/drift detection
- **SEVERITY: CRITICAL - Cannot identify value bets**

### **Issue #4: No Historical Database**
- Only ~10 sample races
- Cannot train ML models properly
- Cannot validate backtests
- **SEVERITY: CRITICAL - Cannot prove system works**

### **Issue #5: No Multi-Source Orchestration**
- Master plan requires 15-40 sources per race
- Current: 0 sources working
- No parallel scraping framework
- **SEVERITY: CRITICAL - 0% of designed architecture built**

---

## 🎯 IMMEDIATE ACTION ITEMS (Priority Order)

### 1. **Betfair API Integration** (3-5 days)
   - Most critical missing piece
   - Enables value identification
   - Required for Categories 8-9

### 2. **Racing.com Live Scraper** (5-7 days)
   - Replace placeholder with real scraping
   - Populate 1000+ historical races
   - Foundation for all other features

### 3. **Historical Database Population** (7-10 days)
   - Backfill 1000+ races
   - Validate data quality
   - Enable ML model training

### 4. **Multi-Source Orchestrator** (10-14 days)
   - Build async scraping framework
   - Implement 15-40 sources per race architecture
   - Enable qualitative pipeline

### 5. **Remaining Scrapers** (21-30 days)
   - Stewards, trials, gear, experts
   - Complete Categories 1-21 coverage
   - Achieve 80-90% completeness target

---

## 📝 CONCLUSION

**Current Reality:**
We have a **comprehensive taxonomy** (21 categories, 16,926 lines of specs), a **detailed master plan** (1039 lines), and a **fusion model architecture** (1530 lines) - but **ZERO functional data collection**.

**The System Cannot Run Because:**
1. No scrapers are actually scraping
2. Database has only placeholder data
3. Cannot train models without historical data
4. Cannot identify value without live odds
5. Cannot build qualitative pipeline without sources

**This Document Provides:**
- Complete mapping of 21 categories → data sources
- 40+ scraper specifications
- Implementation roadmap with priorities
- Architecture for 15-40 sources per race

**Next Step:**
Build the scrapers. This is **the most critical blocker** to having a functional system.

---

*Document Created: November 12, 2025*  
*Status: 🚨 CRITICAL - Foundation for all subsequent work*
