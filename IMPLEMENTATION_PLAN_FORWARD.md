# Racing Analysis System - Complete Implementation Plan

**From November 13, 2025 onwards**

---

## 🎯 Current Status: Foundation Phase (10% Complete)

### ✅ **Completed (Weeks 1-2)**

- [x] Project structure & database schema
- [x] Data models (21 categories mapped)
- [x] Racing.com scraper infrastructure (needs CSS selector refinement)
- [x] Betfair API integration (ready for testing)
- [x] Context engineering system (MASTER_CONTEXT.md, project_snapshot.json)

### 📊 **System Completeness**

- **Scrapers:** 5% (2/15 data sources, both need refinement)
- **Database:** 10% (schema only, ~10 placeholder races)
- **Qualitative Pipeline:** 0% (6 stages not built)
- **Quantitative Pipeline:** 0% (feature engineering not started)
- **Fusion Model:** 0% (only docstring exists)
- **Production System:** 0% (no deployment, monitoring, APIs)

---

## 📋 PHASE 1: DATA COLLECTION (Weeks 3-8) - IMMEDIATE PRIORITY

### **Week 3: Core Data Sources (Days 15-21)**

#### **Day 15: Racing.com Scraper Finalization** 🔥🔥🔥

**Goal:** Get real race data flowing

**Tasks:**

1. **Inspect Live HTML Structure**
   - Visit <https://www.racing.com/form/2024-11-05/flemington> (Melbourne Cup)
   - Document actual CSS selectors for:
     - Race details (name, distance, condition, class, prize)
     - Runner table (horses, jockeys, trainers, barriers, weights)
     - Gear changes
   - Update `_extract_race_details()` and `_extract_runners()`

2. **Test on Historical Races**
   - Melbourne Cup 2024 (Nov 5): All 10 races
   - Caulfield Cup 2024 (Oct 19): All 9 races
   - Validate data completeness >80%

3. **Error Handling Enhancement**
   - Handle scratched horses
   - Manage emergency runners
   - Deal with race postponements

**Deliverable:** Racing.com scraper returning real data (not placeholders)

---

#### **Day 16: Betfair Testing & Integration** 🔥🔥🔥

**Goal:** Verify Betfair API works with live data

**Tasks:**

1. **Account Setup**
   - Create Betfair account (15 min)
   - Get API key (5 min)
   - Set environment variables
   - Run `python test_betfair.py`

2. **Live Race Testing**
   - Find next race day (weekend)
   - Test on 3-5 races:
     - Market search
     - Live odds retrieval
     - Market tracking (30 min pre-race)
   - Validate steam/drift detection

3. **Database Integration**
   - Ensure `MarketOdds` inserts work
   - Test foreign key relationships
   - Verify timestamp handling

**Deliverable:** Betfair client operational with real market data

---

#### **Day 17: Weather API Integration** 🔥🔥

**Goal:** Add track condition intelligence

**Implementation:**

```python
# src/data/scrapers/weather_api.py

class WeatherAPI:
    """Weatherzone/BOM API integration"""

    def get_track_conditions(venue: str, race_date: date) -> dict:
        """
        Returns:
            {
                'temperature': 24.5,
                'humidity': 65,
                'wind_speed': 15,
                'wind_direction': 'NW',
                'rainfall_24h': 2.5,
                'rainfall_7d': 15.0,
                'track_rating': 'Good 4',
                'penetrometer': 4.2
            }
        """
```

**Data Sources:**

- Bureau of Meteorology (BOM): Free, historical data
- Weatherzone API: Free tier, current conditions
- Racing.com track reports: Scrape actual penetrometer readings

**Deliverable:** Weather data for all major venues

---

#### **Day 18-19: Historical Data Population** 🔥🔥🔥

**Goal:** Populate database with 1000+ historical races

**Strategy:**

1. **Target Races (Oct-Nov 2024 Spring Carnival)**
   - Flemington: 50 races
   - Caulfield: 40 races
   - Moonee Valley: 30 races
   - Randwick: 40 races
   - Rosehill: 40 races
   - = **200 races minimum**

2. **Scraping Schedule**
   - 50 races/day (rate limit: 1 sec/race = 50 sec)
   - 4 days to collect 200 races
   - Parallel: Racing.com + Betfair + Weather

3. **Data Validation**
   - Check completeness >75% average
   - Verify foreign keys intact
   - Validate odds ranges (1.01-1001.0)

**Script:**

```python
# scripts/backfill_historical.py

def backfill_spring_carnival_2024():
    """Backfill Oct-Nov 2024 races"""
    venues = ['flemington', 'caulfield', 'moonee-valley', 'randwick', 'rosehill']
    start_date = date(2024, 10, 1)
    end_date = date(2024, 11, 30)

    for venue in venues:
        for race_date in daterange(start_date, end_date):
            for race_num in range(1, 13):
                scrape_and_store(venue, race_date, race_num)
```

**Deliverable:** 200+ complete historical races in database

---

#### **Day 20: TAB Fixed Odds Scraper** 🔥

**Goal:** Complement Betfair with bookmaker odds

**Implementation:**

```python
# src/data/scrapers/tab_odds.py

class TABOddsScraper:
    """Tab.com.au fixed odds scraper"""

    BASE_URL = "https://www.tab.com.au/racing"

    def scrape_tab_odds(venue: str, race_date: date, race_num: int) -> list[MarketOdds]:
        """
        Returns TAB fixed odds (win/place)
        Compares with Betfair for arbitrage detection
        """
```

**URL Pattern:**
`https://www.tab.com.au/racing/vic/flemington/2024-11-05/R1`

**Deliverable:** TAB odds scraper operational

---

#### **Day 21: Stewards Reports (PDF Parsing)** 🔥

**Goal:** Extract vet checks, track bias, incidents

**Implementation:**

```python
# src/data/scrapers/stewards_reports.py

import PyPDF2
import pdfplumber

class StewardsReportParser:
    """Parse stewards reports from Racing Victoria"""

    BASE_URL = "https://www.racingvictoria.com.au/the-sport/stewards-reports"

    def parse_report(pdf_path: str) -> dict:
        """
        Extract:
        - Vet checks (scratched horses)
        - Track bias reports
        - Incidents (interference, falls)
        - Track condition changes
        - Rail position
        """
```

**Sources:**

- Racing Victoria: <https://www.racingvictoria.com.au/>
- Racing NSW: <https://www.racingnsw.com.au/>
- PDF format (requires pdfplumber)

**Deliverable:** Stewards data extraction working

---

### **Week 4: Supplementary Data (Days 22-28)**

#### **Day 22: Barrier Trial Scraper** 🔥

**Goal:** Extract trial performance data

**Challenge:** Racing.com trials require authentication (Selenium)

**Implementation:**

```python
# src/data/scrapers/barrier_trials.py

from selenium import webdriver
from selenium.webdriver.common.by import By

class BarrierTrialScraper:
    """Selenium-based scraper for Racing.com trials"""

    def login_racing_com(driver):
        """Handle Racing.com authentication"""
        # Navigate to login
        # Enter credentials
        # Handle 2FA if needed

    def scrape_trials(horse_name: str, last_days: int = 90) -> list[dict]:
        """
        Returns:
            [{
                'trial_date': date,
                'venue': str,
                'distance': int,
                'time': float,
                'margin': float,
                'position': int,
                'field_size': int,
                'comments': str
            }]
        """
```

**Note:** Most critical scraper (trial data = 10-15% signal)

**Deliverable:** Trial extraction with 90%+ success rate

---

#### **Day 23: Gear Changes Scraper**

**Goal:** Detect first-time blinkers, tongue ties, etc.

**Implementation:**

```python
# src/data/scrapers/gear_changes.py

class GearChangeDetector:
    """Detect and score gear changes"""

    def detect_changes(horse_id: str, race_id: str) -> list[Gear]:
        """
        Compare current gear to last 3 runs
        Flag first-time applications
        Calculate expected impact scores
        """
```

**Data Sources:**

- Racing.com form guide (gear column)
- Historical database lookups
- Stewards reports (official notifications)

**Deliverable:** Gear change detection operational

---

#### **Day 24: Form Scraper (Detailed Run History)**

**Goal:** Extract last 5 runs with sectionals

**Implementation:**

```python
# src/data/scrapers/form_scraper.py

class FormScraper:
    """Extract detailed form from Racing.com"""

    def scrape_form(horse_id: str, runs: int = 5) -> list[dict]:
        """
        Returns last N runs with:
        - Race details (date, venue, distance, track)
        - Performance (position, margin, time)
        - Sectionals (600m, 400m, 200m splits)
        - Jockey/trainer
        - Weight carried
        - Comments
        """
```

**Deliverable:** Detailed form history for all runners

---

#### **Day 25: Jockey/Trainer Stats**

**Goal:** Build performance statistics database

**Implementation:**

```python
# src/data/scrapers/jockey_stats.py

class JockeyStatsBuilder:
    """Calculate jockey/trainer statistics"""

    def calculate_stats(jockey_id: str, lookback_days: int = 365) -> dict:
        """
        Returns:
        - Win rate (overall, by venue, by distance)
        - Strike rate with specific trainers
        - Track specialization
        - Big race performance
        - Recent form (last 14 days)
        """
```

**Source:** Database aggregation (no scraping needed)

**Deliverable:** Jockey/trainer statistics engine

---

#### **Day 26-27: Expert Commentary & Media Scraper**

**Goal:** Extract qualitative intelligence

**Sources:**

1. **Racing.com Articles**
   - Selenium scraper for premium content
   - Extract quotes, insights, betting moves

2. **Punters.com.au Tips**
   - Scrape expert selections
   - Track tipster performance

3. **Social Media (Twitter/X)**
   - Track racing journalists
   - Monitor stable updates
   - Detect late scratchings

**Implementation:**

```python
# src/data/scrapers/media_scraper.py

class MediaIntelligence:
    """Extract media insights"""

    def scrape_racing_com_articles(race_id: str) -> list[dict]:
        """Extract race previews, quotes, insights"""

    def scrape_punters_tips(race_id: str) -> list[dict]:
        """Get expert selections"""

    def monitor_social_media(keywords: list[str]) -> list[dict]:
        """Track Twitter for breaking news"""
```

**Deliverable:** Media intelligence extraction

---

#### **Day 28: Data Quality Validation**

**Goal:** Verify all scrapers working, data clean

**Tasks:**

1. **Completeness Check**
   - Run all scrapers on sample races
   - Verify >80% data completeness
   - Check foreign key integrity

2. **Data Quality Metrics**
   - Odds ranges valid (1.01-1001.0)
   - Dates consistent
   - No duplicate entries
   - Missing data <20%

3. **Performance Testing**
   - Measure scrape time per race
   - Check rate limit compliance
   - Optimize slow scrapers

**Deliverable:** Data quality report, all scrapers operational

---

## 📋 PHASE 2: QUALITATIVE PIPELINE (Weeks 5-8)

### **Week 5: Pipeline Architecture (Days 29-35)**

#### **Day 29-30: Stage 1 - Source Planning Agent (Gemini)** 🔥🔥🔥

**Goal:** Implement Category 1-17 intelligent source discovery

**Architecture:**

```python
# src/pipelines/qualitative/stage1_source_planner.py

class SourcePlanningAgent:
    """
    Gemini-based agent for dynamic source discovery

    Categories Covered: 1-17
    - Category 1: Recent form analysis
    - Category 2: Class assessment
    - Category 3: Track/distance suitability
    - ... (all 17 categories)
    """

    def plan_sources(self, race_context: dict) -> list[str]:
        """
        Input: {race_details, horse_details, market_context}

        Output: Prioritized source list
        [
            "racing.com_article_12345",
            "punters_expert_tip_456",
            "twitter_stable_update_789",
            ...
        ]

        Gemini Prompt:
        "Given this R1 Flemington 1200m race, what information sources
        would help analyze each runner? Prioritize by relevance and
        information quality. Consider: recent form, track specialists,
        barrier draws, jockey changes, market moves, etc."
        """
```

**Gemini Integration:**

```python
import google.generativeai as genai

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('gemini-1.5-pro')

response = model.generate_content(source_planning_prompt)
```

**Deliverable:** Source planning agent operational

---

#### **Day 31-32: Stage 2 - Content Extraction** 🔥🔥

**Goal:** Extract and structure content from planned sources

**Implementation:**

```python
# src/pipelines/qualitative/stage2_content_extractor.py

class ContentExtractor:
    """Extract content from discovered sources"""

    def extract_content(self, source_url: str) -> dict:
        """
        Returns structured content:
        {
            'source_id': 'racing_com_article_12345',
            'content_type': 'article',
            'text': "...",
            'quotes': [...],
            'key_points': [...],
            'mentioned_horses': [...],
            'sentiment': 'positive/neutral/negative'
        }
        """
```

**Techniques:**

- BeautifulSoup for HTML extraction
- Selenium for authenticated content
- NLP for quote extraction
- Sentiment analysis

**Deliverable:** Content extraction engine

---

#### **Day 33-34: Stage 3 - Information Synthesis (GPT-4)** 🔥🔥🔥

**Goal:** Synthesize extracted content into insights

**Architecture:**

```python
# src/pipelines/qualitative/stage3_synthesis.py

class InformationSynthesizer:
    """GPT-4 synthesis of multi-source information"""

    def synthesize_horse_intelligence(
        self,
        horse_name: str,
        sources: list[dict]
    ) -> dict:
        """
        GPT-4 Prompt:
        "Synthesize the following 15 information sources about
        [Horse Name] running in R1 Flemington 1200m today:

        [Source 1: Racing.com preview says...]
        [Source 2: Expert tip from Punters.com...]
        [Source 3: Stable Twitter update...]
        ...

        Provide:
        1. Key insights (3-5 points)
        2. Strengths for this race
        3. Concerns or weaknesses
        4. Market implications
        5. Overall assessment (100-200 words)
        "

        Returns:
            {
                'insights': [...],
                'strengths': [...],
                'concerns': [...],
                'market_implications': str,
                'assessment': str,
                'confidence': 0.0-1.0
            }
        """
```

**Deliverable:** Multi-source synthesis working

---

#### **Day 35: Stage 4 - Likelihood Ratio Generation** 🔥🔥🔥

**Goal:** Convert qualitative insights to quantitative LRs

**Implementation:**

```python
# src/pipelines/qualitative/stage4_lr_generation.py

class LikelihoodRatioGenerator:
    """Convert synthesis to LR adjustments"""

    def generate_lr(
        self,
        synthesis: dict,
        category: int
    ) -> tuple[float, str, float]:
        """
        GPT-4 Prompt:
        "Based on this synthesis for Category {category}:

        {synthesis_text}

        Generate a likelihood ratio (LR) adjustment:
        - LR range: 0.70 (strong negative) to 1.30 (strong positive)
        - 1.0 = neutral (no adjustment)
        - Provide reasoning (2-3 sentences)
        - Assign confidence (0.0-1.0)

        Format:
        LR: X.XX
        Reasoning: ...
        Confidence: 0.XX
        "

        Returns:
            (lr: float, reasoning: str, confidence: float)
        """
```

**Category-Specific LR Ranges:**

- Category 1 (Recent Form): 0.75-1.25
- Category 2 (Class): 0.80-1.20
- Category 3 (Track/Distance): 0.85-1.15
- Category 12 (Market): 0.90-1.15 (steam/drift)
- etc.

**Deliverable:** LR generation from qualitative analysis

---

### **Week 6: Pipeline Integration (Days 36-42)**

#### **Day 36-37: Stage 5 - Confidence Calibration** 🔥

**Goal:** Validate and calibrate LR confidence scores

**Implementation:**

```python
# src/pipelines/qualitative/stage5_calibration.py

class ConfidenceCalibrator:
    """Calibrate LR confidence using historical performance"""

    def calibrate_lr(
        self,
        lr: float,
        reasoning: str,
        confidence: float,
        historical_accuracy: float
    ) -> float:
        """
        Adjust confidence based on:
        - Source reliability
        - Historical GPT accuracy for this category
        - Certainty indicators in reasoning
        - Cross-source agreement

        Returns calibrated confidence (0.0-1.0)
        """
```

**Deliverable:** Confidence calibration system

---

#### **Day 38-39: Stage 6 - Fusion Preparation** 🔥

**Goal:** Format qualitative LRs for fusion model

**Implementation:**

```python
# src/pipelines/qualitative/stage6_fusion_prep.py

class FusionPreparation:
    """Prepare qualitative LRs for Bayesian fusion"""

    def prepare_for_fusion(
        self,
        horse_lrs: dict[int, tuple[float, float]]
    ) -> dict:
        """
        Input: {category: (lr, confidence), ...}

        Output: {
            'qualitative_lrs': {
                1: {'lr': 1.15, 'confidence': 0.80, 'weight': 0.72},
                2: {'lr': 1.08, 'confidence': 0.65, 'weight': 0.58},
                ...
            },
            'combined_confidence': 0.73,
            'source_count': 15
        }
        """
```

**Deliverable:** Fusion-ready qualitative output

---

#### **Day 40-42: End-to-End Qualitative Testing**

**Goal:** Test full pipeline on 10 races

**Test Cases:**

1. **High-Quality Race** (Group 1, 15+ sources)
2. **Medium-Quality Race** (Listed, 8-10 sources)
3. **Low-Quality Race** (Maiden, 3-5 sources)

**Metrics:**

- Source discovery accuracy
- Extraction success rate
- Synthesis quality (manual review)
- LR calibration (compare to results)
- Processing time per horse

**Deliverable:** Qualitative pipeline validated

---

### **Week 7-8: Quantitative Pipeline (Days 43-56)**

#### **Day 43-45: Feature Engineering (Categories 18-21)** 🔥🔥🔥

**Goal:** Build quantitative features from database

**Categories:**

- **Category 18: Speed Ratings**

  ```python
  def calculate_speed_rating(run: Run, race: Race) -> float:
      """
      Adjusted for:
      - Distance
      - Track condition
      - Weight carried
      - Sectional times
      """
  ```

- **Category 19: Weight & Barrier**

  ```python
  def engineer_weight_features(run: Run) -> dict:
      """
      Returns:
      - weight_carried
      - weight_differential (vs avg)
      - weight_per_rating
      - barrier_bias (track-specific)
      - inside/outside barrier flag
      """
  ```

- **Category 20: Pace Analysis**

  ```python
  def analyze_race_pace(runs: list[Run]) -> dict:
      """
      Returns:
      - expected_pace (fast/moderate/slow)
      - speed_map (leader/settler/closer)
      - run_style_advantage
      """
  ```

- **Category 21: Historical Patterns**

  ```python
  def extract_historical_features(horse: Horse, race: Race) -> dict:
      """
      Returns:
      - venue_win_rate
      - distance_win_rate
      - track_condition_performance
      - days_since_last_run
      - career_statistics
      """
  ```

**Deliverable:** 150+ quantitative features per horse

---

#### **Day 46-48: XGBoost Model Training** 🔥🔥

**Goal:** Train quantitative prediction model

**Implementation:**

```python
# src/models/quantitative/xgboost_model.py

import xgboost as xgb

class QuantitativeModel:
    """XGBoost model for quantitative features"""

    def train(self, historical_races: pd.DataFrame):
        """
        Features: 150+ quantitative features
        Target: Win probability (0/1)

        Model: XGBoost classifier
        Hyperparameters:
        - max_depth: 6
        - learning_rate: 0.05
        - n_estimators: 500
        - subsample: 0.8
        """

    def predict_probabilities(self, features: pd.DataFrame) -> np.ndarray:
        """Returns win probabilities for each horse"""
```

**Training Data:**

- 1000+ historical races
- 10,000+ runners
- Features: Speed ratings, weight, barrier, pace, form

**Validation:**

- 80/20 train/test split
- Cross-validation (5-fold)
- Metrics: Log-loss, Brier score, ROI

**Deliverable:** Trained XGBoost model

---

#### **Day 49-50: Quantitative LR Generation** 🔥

**Goal:** Convert XGBoost probabilities to LRs

**Implementation:**

```python
# src/models/quantitative/lr_converter.py

class QuantitativeLRConverter:
    """Convert XGBoost probabilities to likelihood ratios"""

    def probability_to_lr(
        self,
        xgb_prob: float,
        market_prob: float
    ) -> float:
        """
        LR = (XGBoost_prob / market_prob)

        Example:
        - XGBoost: 25% win chance
        - Market: 20% (odds $5.00)
        - LR = 0.25 / 0.20 = 1.25 (25% boost)
        """
```

**Deliverable:** Quantitative LR generation

---

#### **Day 51-53: Quantitative Pipeline Testing**

**Goal:** Validate quantitative predictions

**Test Cases:**

- 100 test races
- Compare XGBoost vs market odds
- Measure Brier score, log-loss, ROI

**Target Metrics:**

- Brier score: <0.18 (market: ~0.20)
- Log-loss: <0.50
- ROI (if betting model predictions): >5%

**Deliverable:** Quantitative pipeline validated

---

#### **Day 54-56: Pipeline Integration**

**Goal:** Connect qualitative + quantitative pipelines

**Architecture:**

```python
# src/pipelines/integrated_pipeline.py

class IntegratedPipeline:
    """Combined qualitative + quantitative pipeline"""

    def process_race(self, race_id: str) -> dict:
        """
        1. Qualitative Pipeline (Categories 1-17)
           - Source discovery → Extraction → Synthesis → LR

        2. Quantitative Pipeline (Categories 18-21)
           - Feature engineering → XGBoost → LR

        3. Return combined LRs for fusion

        Returns:
            {
                horse_id: {
                    'qualitative_lrs': {1: 1.15, 2: 1.08, ...},
                    'quantitative_lr': 1.12,
                    'combined_confidence': 0.73
                }
            }
        """
```

**Deliverable:** Integrated dual-pipeline system

---

## 📋 PHASE 3: FUSION MODEL (Weeks 9-10)

### **Week 9: Bayesian Fusion (Days 57-63)**

#### **Day 57-59: Fusion Model Implementation** 🔥🔥🔥

**Goal:** Build 15-agent Bayesian LR fusion system

**Architecture:**

```python
# src/models/fusion/bayesian_fusion.py

class BayesianFusionModel:
    """
    15-agent Bayesian LR fusion system

    Agents:
    - 1 Quantitative agent (Categories 18-21)
    - 14 Qualitative agents (Categories 1-17, some grouped)
    """

    def fuse_likelihood_ratios(
        self,
        lrs: dict[int, float],
        confidences: dict[int, float]
    ) -> float:
        """
        Bayesian LR Fusion:

        Combined_LR = LR₁^(w₁) × LR₂^(w₂) × ... × LR₁₅^(w₁₅)

        Where weights (w) = confidence scores

        Example:
        - Category 1: LR=1.15, confidence=0.80 → 1.15^0.80 = 1.117
        - Category 2: LR=1.08, confidence=0.65 → 1.08^0.65 = 1.050
        - Combined: 1.117 × 1.050 × ... = 1.28

        Returns final LR adjustment to market odds
        """
```

**Formula:**

```
Combined_LR = ∏(LRᵢ^wᵢ)  where wᵢ = confidence

Final_Probability = (Market_Prob × Combined_LR) / Normalization
```

**Deliverable:** Bayesian fusion model operational

---

#### **Day 60-61: E2B + OpenHands Agentic Integration** 🔥🔥

**Goal:** Enable autonomous agent execution for complex tasks

**E2B Integration:**

```python
# src/models/fusion/e2b_agent.py

from e2b import Sandbox

class E2BAgent:
    """E2B sandbox for autonomous code execution"""

    def execute_analysis(self, code: str) -> dict:
        """
        Execute GPT-generated Python code in E2B sandbox

        Use cases:
        - Complex statistical analysis
        - Custom metric calculations
        - Data transformations
        - Visualization generation
        """

        sandbox = Sandbox()
        result = sandbox.run_code(code)
        return result.output
```

**OpenHands Integration:**

```python
# src/models/fusion/openhands_agent.py

class OpenHandsAgent:
    """OpenHands for multi-step reasoning"""

    def reason_about_race(self, race_context: dict) -> dict:
        """
        Multi-step reasoning:
        1. Analyze race dynamics
        2. Identify key factors
        3. Simulate scenarios
        4. Generate predictions
        """
```

**Deliverable:** Agentic capabilities integrated

---

#### **Day 62-63: Fusion Testing & Calibration**

**Goal:** Validate fusion model performance

**Test Dataset:**

- 200 historical races (separate from training)
- Full pipeline execution
- Compare fused predictions vs market

**Metrics:**

- **Brier Score:** Target <0.16 (ChatGPT: ~0.20)
- **Log-Loss:** Target <0.45
- **ROI:** Target >7.2% (ChatGPT: ~0%)
- **Value Identification:** >15% of bets profitable

**Calibration:**

- Adjust confidence weights
- Fine-tune LR ranges
- Optimize agent contributions

**Deliverable:** Calibrated fusion model (Brier <0.16)

---

### **Week 10: End-to-End System (Days 64-70)**

#### **Day 64-65: Prediction API** 🔥

**Goal:** Build REST API for predictions

**Implementation:**

```python
# src/api/prediction_api.py

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.post("/predict/race")
async def predict_race(race_id: str) -> dict:
    """
    Full pipeline execution:
    1. Scrape race data (Racing.com, Betfair, Weather)
    2. Run qualitative pipeline (15 sources per horse)
    3. Run quantitative pipeline (XGBoost)
    4. Fuse LRs (Bayesian fusion)
    5. Generate predictions

    Returns:
        {
            'race_id': 'flemington-2025-11-20-R1',
            'predictions': [
                {
                    'horse': 'Anamoe',
                    'win_probability': 0.28,
                    'market_probability': 0.20,
                    'value': 0.08,  # 8% edge
                    'recommended_bet': True,
                    'confidence': 0.85
                },
                ...
            ],
            'processing_time': 45.2,
            'data_completeness': 0.87
        }
    """
```

**Deliverable:** FastAPI prediction endpoint

---

#### **Day 66-67: Real-Time Monitoring**

**Goal:** Build live race monitoring system

**Implementation:**

```python
# src/monitoring/live_monitor.py

class LiveRaceMonitor:
    """Monitor races in real-time"""

    def monitor_race_day(self, date: date):
        """
        Continuous monitoring:
        1. Track market movements (Betfair every 5 min)
        2. Detect late scratchings
        3. Update predictions dynamically
        4. Alert on value opportunities
        5. Generate reports
        """
```

**Features:**

- Real-time Betfair tracking
- Steam/drift alerts
- Late information updates
- Prediction refreshes

**Deliverable:** Live monitoring system

---

#### **Day 68-69: Production Deployment**

**Goal:** Deploy to cloud infrastructure

**Architecture:**

```
┌─────────────────────────────────────┐
│         Load Balancer               │
└──────────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌─────▼──────┐
│  FastAPI    │  │  FastAPI   │
│  Server 1   │  │  Server 2  │
└──────┬──────┘  └─────┬──────┘
       │                │
       └───────┬────────┘
               │
    ┌──────────▼──────────────┐
    │   PostgreSQL Database   │
    └─────────────────────────┘
               │
    ┌──────────▼──────────────┐
    │   Redis Cache           │
    └─────────────────────────┘
```

**Components:**

- **Servers:** 2× FastAPI instances (AWS EC2 or Heroku)
- **Database:** PostgreSQL (AWS RDS)
- **Cache:** Redis (for Betfair data)
- **Storage:** S3 (for PDF reports, logs)
- **Monitoring:** CloudWatch or Datadog

**Deliverable:** Production deployment

---

#### **Day 70: System Validation & Documentation**

**Goal:** Final validation and handoff

**Validation:**

1. **Performance Test**
   - Process 100 races end-to-end
   - Measure latency (<60 sec/race)
   - Verify accuracy (Brier <0.16)

2. **Stress Test**
   - Handle 50 concurrent requests
   - Process full race day (80+ races)
   - Monitor resource usage

3. **Documentation**
   - API documentation (Swagger/OpenAPI)
   - Deployment guide
   - Maintenance procedures
   - Troubleshooting guide

**Deliverable:** Production-ready system

---

## 📋 PHASE 4: OPTIMIZATION & SCALING (Weeks 11-16)

### **Week 11-12: Performance Optimization**

#### **Tasks:**

1. **Scraper Optimization**
   - Parallel scraping (asyncio)
   - Cache frequently accessed data
   - Optimize rate limits

2. **Pipeline Optimization**
   - Batch processing
   - GPU acceleration (XGBoost)
   - Reduce API calls (Gemini/GPT-4)

3. **Database Optimization**
   - Add indexes on foreign keys
   - Partitioning (by race_date)
   - Query optimization

**Target:** <30 sec per race (currently ~60 sec)

---

### **Week 13-14: Advanced Features**

#### **Features:**

1. **Multi-Race Optimization**
   - Optimize betting across entire race day
   - Kelly criterion stake sizing
   - Bankroll management

2. **Historical Analysis**
   - Backtest over 5000+ historical races
   - Generate performance reports
   - Identify optimal betting strategies

3. **Value Detection**
   - Automated value bet identification
   - Alert system (SMS/email)
   - Confidence-based filtering

4. **Visualization Dashboard**
   - Streamlit dashboard
   - Live odds visualization
   - Performance metrics
   - Prediction confidence heatmaps

---

### **Week 15-16: Production Features**

#### **Features:**

1. **User Authentication**
   - JWT-based auth
   - API key management
   - Rate limiting per user

2. **Subscription System**
   - Free tier (10 predictions/day)
   - Pro tier (unlimited)
   - Enterprise tier (API access)

3. **Mobile App**
   - React Native app
   - Live predictions
   - Bet tracking
   - Performance analytics

4. **Automated Betting Integration**
   - Betfair automated betting
   - TAB integration
   - Stake optimization
   - Risk management

---

## 📊 SUCCESS METRICS

### **Data Collection (Phase 1)**

- ✅ 1000+ historical races in database
- ✅ Data completeness >80% average
- ✅ All 15 data sources operational
- ✅ <5% scraping failure rate

### **Qualitative Pipeline (Phase 2)**

- ✅ 15+ sources per horse average
- ✅ GPT-4 synthesis quality >85%
- ✅ LR generation accuracy >80%
- ✅ Processing time <30 sec/horse

### **Quantitative Pipeline (Phase 2)**

- ✅ 150+ features engineered
- ✅ XGBoost accuracy >85%
- ✅ Brier score <0.18
- ✅ ROI >5% on test set

### **Fusion Model (Phase 3)**

- ✅ Brier score <0.16 (beat ChatGPT's 0.20)
- ✅ ROI >7.2% (beat ChatGPT's 0%)
- ✅ Value identification >15%
- ✅ Processing time <60 sec/race

### **Production System (Phase 4)**

- ✅ 99.9% uptime
- ✅ <30 sec latency
- ✅ Handle 100+ concurrent users
- ✅ Profitable over 1000+ bets

---

## 🚀 IMMEDIATE NEXT STEPS (This Week)

### **Priority 1: Racing.com Finalization** (Day 15)

1. Inspect Melbourne Cup 2024 HTML
2. Update CSS selectors
3. Test on 10 historical races
4. Validate >80% completeness

### **Priority 2: Betfair Testing** (Day 16)

1. Set up account (if not done)
2. Test on live race
3. Verify database integration
4. Validate steam/drift detection

### **Priority 3: Historical Backfill** (Days 17-19)

1. Write backfill script
2. Target 200 Spring Carnival races
3. Scrape Racing.com + Betfair + Weather
4. Populate database

### **Priority 4: Remaining Scrapers** (Days 20-28)

1. TAB odds (Day 20)
2. Stewards reports (Day 21)
3. Barrier trials (Day 22)
4. Form scraper (Days 23-24)
5. Media intelligence (Days 25-27)
6. Validation (Day 28)

---

## 📅 TIMELINE SUMMARY

| Phase | Duration | Key Deliverables | Completion Target |
|-------|----------|-----------------|-------------------|
| **Phase 1: Data Collection** | Weeks 3-8 (6 weeks) | 15 scrapers, 1000+ races | Dec 25, 2025 |
| **Phase 2: Pipelines** | Weeks 5-8 (4 weeks) | Qual + Quant pipelines | Jan 15, 2026 |
| **Phase 3: Fusion Model** | Weeks 9-10 (2 weeks) | Bayesian fusion, Brier <0.16 | Jan 30, 2026 |
| **Phase 4: Production** | Weeks 11-16 (6 weeks) | API, deployment, optimization | Mar 15, 2026 |

**Total Timeline: 16 weeks from now (November 13, 2025 → March 15, 2026)**

---

## 💰 RESOURCE REQUIREMENTS

### **APIs & Services**

- **Betfair:** Free (account required)
- **Gemini API:** ~$50/month (qualitative synthesis)
- **GPT-4 API:** ~$100/month (LR generation)
- **E2B Sandbox:** ~$50/month
- **Weather API:** Free (BOM) or $20/month (Weatherzone)
- **Cloud Hosting:** ~$100/month (AWS/Heroku)
- **Database:** ~$50/month (PostgreSQL RDS)

**Total Monthly Cost:** ~$370/month (operational)

### **One-Time Costs**

- **Development Time:** 16 weeks @ 40 hrs/week = 640 hours
- **Testing & Validation:** 100 hours
- **Documentation:** 40 hours

---

## ⚠️ CRITICAL SUCCESS FACTORS

1. **Racing.com Scraper Quality**
   - Must achieve >80% completeness
   - Foundation for entire system
   - **Risk:** High (authentication, rate limits)

2. **Betfair Integration**
   - 15-20% of predictive power
   - Real-time tracking essential
   - **Risk:** Medium (API stability)

3. **Qualitative Pipeline Quality**
   - GPT-4 synthesis must be accurate
   - Source discovery critical
   - **Risk:** Medium (LLM reliability)

4. **Historical Data Volume**
   - Need 1000+ races for training
   - Quality > quantity
   - **Risk:** Medium (time-consuming)

5. **Fusion Model Calibration**
   - Must beat Brier 0.16 target
   - Requires careful tuning
   - **Risk:** High (complex system)

---

## 📝 DECISION POINTS

### **Week 4 Decision: Qualitative vs Quantitative Priority**

- **Option A:** Build quantitative first (faster, lower risk)
- **Option B:** Build qualitative first (higher ceiling, more complex)
- **Recommendation:** Parallel development (split work)

### **Week 8 Decision: Fusion Model Architecture**

- **Option A:** Simple weighted average (fast, less accurate)
- **Option B:** Full Bayesian LR fusion (slower, more accurate)
- **Recommendation:** Full Bayesian (per master plan)

### **Week 10 Decision: Deployment Strategy**

- **Option A:** Cloud (AWS/GCP) - scalable, expensive
- **Option B:** Heroku - simple, limited scale
- **Recommendation:** Start Heroku, migrate AWS when needed

---

## 🎯 FINAL GOAL

**Build a racing prediction system that:**

1. **Beats ChatGPT:** Brier <0.16 (vs 0.20), ROI >7.2% (vs 0%)
2. **Processes races end-to-end:** <60 seconds per race
3. **Handles 15+ data sources:** Racing.com, Betfair, weather, trials, etc.
4. **Dual pipeline:** Qualitative (Categories 1-17) + Quantitative (18-21)
5. **15-agent fusion:** Bayesian LR fusion with E2B + OpenHands
6. **Production-ready:** API, monitoring, deployment, documentation

**Expected Performance:**

- **Accuracy:** Brier score <0.16
- **Profitability:** ROI >7.2% over 1000+ bets
- **Reliability:** 99.9% uptime
- **Speed:** <60 sec per race prediction

---

**This is the complete roadmap. Start with Week 3, Day 15 (Racing.com finalization) and follow the plan sequentially. Each week builds on the previous, leading to a production-ready system in 16 weeks.**
