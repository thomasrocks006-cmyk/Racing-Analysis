# Racing Analysis System - Master Implementation Plan

**Created**: November 8, 2025  
**Status**: Phase 0 - Foundation  
**Goal**: Build a high-accuracy horse racing prediction system with quantitative modeling + qualitative research fusion

---

## 🎯 Project Goals

1. **Primary**: Produce calibrated win/place probabilities and fair odds per race
2. **Secondary**: Identify value opportunities vs market prices (Betfair/TAB)
3. **Tertiary**: Build reproducible backtesting framework with uncertainty quantification

**Non-Negotiables**:
- ✅ Strict event-time ordering (no data leakage)
- ✅ Reproducible runs with versioning
- ✅ Uncertainty quantification on all predictions
- ✅ Non-commercial personal use (scraping permitted)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                             │
│  Betfair (Historic/Stream) │ Racing.com │ Weather │ Stewards    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ETL PIPELINE                                │
│  Scrapers → Parsers → Validation → DuckDB Warehouse             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FEATURE STORE (Parquet)                        │
│  Sectionals │ Ratings │ Pace │ Bias │ Weather │ Market          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MODELING LAYER                              │
│  CatBoost/LightGBM → Calibration → Conformal Prediction         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   QUALITATIVE FUSION                             │
│  Deep Research → Claim Extraction → Bayesian LR Update          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION LAYER                               │
│  Simulator → Kelly Sizing → Order Placement                     │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API + DASHBOARD                              │
│  FastAPI Backend │ Streamlit UI │ Monitoring                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Phases

### **PHASE 0: Foundation** (Days 1-3) ⏳ CURRENT
**Goal**: Set up development environment and core scaffolding

**Tasks** (automated):
- [x] Create comprehensive plan document
- [ ] Set up repository structure
- [ ] Create `.devcontainer` with Python 3.11, dependencies
- [ ] Initialize DuckDB database schema
- [ ] Create configuration management system
- [ ] Set up Makefile with common commands
- [ ] Create basic test framework

**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- None for Phase 0 (all automated)

**Deliverables**:
- ✅ Working devcontainer
- ✅ Database schema created
- ✅ `make test` passes
- ✅ `make ingest --help` shows options

---

### **PHASE 1: Data Layer** (Days 4-10)
**Goal**: Ingest and store historical racing data

#### 1.1 Database Schema Design
**Automated**:
- Core tables: races, runs, horses, jockeys, trainers
- Market tables: prices, depth, traded_volume
- Qualitative tables: stewards, gear, weather
- Time-series indexes and partitioning

**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- [ ] **Sign up for Betfair API account** (https://developer.betfair.com/)
  - Create app, get API key and session token
  - Add to `.env` file
- [ ] **Sign up for weather API** (https://open-meteo.com/ - free)
  - Get API key if rate limits needed
  - Add to `.env` file

#### 1.2 Web Scrapers
**Automated**:
- Racing.com results scraper
- Stewards reports scraper (Racing Victoria)
- TAB price scraper (where available)
- Gear change scraper

**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- [ ] **Test scrapers on first run** - check output quality
- [ ] **Identify any site structure changes** - provide updated HTML samples if scrapers break

#### 1.3 Betfair Integration
**Automated**:
- Historic data downloader
- Stream API client (for live markets)
- Price history parser

**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- [ ] **Download sample Betfair historic data** (manual download from Betfair site)
  - Place in `data/betfair_historic/` folder
  - Format: CSV or JSON as provided by Betfair

#### 1.4 Data Validation
**Automated**:
- Schema validation (Pydantic)
- Completeness checks
- Anomaly detection

**Deliverables**:
- ✅ `make ingest date=2025-11-09` loads a full race card
- ✅ DuckDB has 1000+ races with complete data
- ✅ Data quality report shows >80% completeness on key fields

---

### **PHASE 2: Feature Engineering** (Days 11-17)
**Goal**: Calculate predictive features from raw data

#### 2.1 Core Features
**Automated**:
- Par-adjusted sectionals (L600/L400/L200)
- Distance suitability curves (spline fits)
- Going (wet/firm) elasticity curves
- Days since run / fitness curves
- Trainer/jockey rolling metrics (30/90/365 day)
- Career statistics and trajectories

#### 2.2 Race Dynamics
**Automated**:
- Early speed classification (leader/presser/mid/back)
- Simplified pace pressure (field-wide tempo)
- Barrier advantage by track/distance
- Field size effects

#### 2.3 Context Features
**Automated**:
- Weather alignment (rain, wind, temp at jump time)
- Track condition history
- Gear changes (first-time flags, removals)
- Stewards incidents (parsed and encoded)

#### 2.4 Market Features
**Automated**:
- Price movements (T-60, T-15, T-2)
- Market depth and liquidity
- Overround normalization
- SP vs BSP comparison

#### 2.5 Feature Store
**Automated**:
- Parquet storage with partitioning
- Feature versioning and lineage
- Train/test split respecting time ordering

**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- [ ] **Review feature distributions** - check for bugs or anomalies
- [ ] **Approve feature set** before modeling

**Deliverables**:
- ✅ `make features date=2025-11-09` computes 100+ features
- ✅ Feature catalog document auto-generated
- ✅ No data leakage (validated by time-split test)

---

### **PHASE 3: Modeling Core** (Days 18-28)
**Goal**: Build, calibrate, and validate predictive models

#### 3.1 Baseline Models
**Automated**:
- CatBoost classifier (win/place)
- LightGBM classifier (win/place)
- Feature importance analysis
- Hyperparameter tuning (Optuna)

#### 3.2 Calibration
**Automated**:
- Isotonic regression per track group
- Temperature scaling fallback
- Reliability diagrams
- Brier score decomposition

#### 3.3 Uncertainty Quantification
**Automated**:
- Conformal prediction sets
- Stratified by going/distance/field_size
- Coverage validation

#### 3.4 Backtesting Framework
**Automated**:
- Walk-forward validation
- Metrics: Brier, log-loss, AUC, calibration error
- ROI simulation with commission/slippage
- Drawdown analysis
- Performance by track/going/distance

**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- [ ] **Review backtest results** - validate no overfitting
- [ ] **Approve model for Phase 4** - check metrics meet targets:
  - Brier score <0.20
  - AUC >0.75
  - Simulated ROI >5% (conservative assumptions)

**Deliverables**:
- ✅ `make train` produces versioned model artifacts
- ✅ `make backtest` runs 1000-race validation
- ✅ Backtest report shows positive ROI and good calibration

---

### **PHASE 4: Qualitative Integration** (Days 29-35)
**Goal**: Fuse Deep Research insights with quantitative predictions

#### 4.1 Deep Research Pipeline
**Automated**:
- Pre-fetch overnight for next day's cards
- Structured claim extraction (JSON schema)
- Source quality scoring
- Timestamp and recency decay

**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- [ ] **Set up ChatGPT Plus account** (if not already)
- [ ] **Configure Deep Research agent** (or use API if available)
- [ ] **Manual deep research workflow** (short-term):
  1. Export race card for next day
  2. Run deep research queries manually
  3. Paste results into `data/qual_claims/YYYY-MM-DD.json`
  4. System will auto-process

#### 4.2 Claim Ontology
**Automated**:
- Coarse categories (5 types):
  1. Health (positive/neutral/negative)
  2. Fitness (peak/building/underdone)
  3. Tactics (rail/mid/back preference)
  4. Gear (first-time significant)
  5. Bias (inside/outside advantage)

#### 4.3 Likelihood Ratio Learning
**Automated**:
- Start with domain expert priors
- Hierarchical Bayesian updates from outcomes
- Heavy regularization toward priors
- Shadow mode logging for validation

#### 4.4 Fusion Logic
**Automated**:
- Apply LRs post-calibration (Bayesian update)
- Re-normalize probabilities
- Track adjustments for audit trail

**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- [ ] **Set LR priors** (will provide template with suggested values)
- [ ] **Review fusion outputs** - sanity check first 50 races
- [ ] **Tune LR strength** - dial up/down based on validation

**Deliverables**:
- ✅ Qualitative claims ingested and parsed
- ✅ LR fusion improves backtest Brier by ≥1%
- ✅ Audit trail shows rationale for each adjustment

---

### **PHASE 5: Execution & API** (Days 36-42)
**Goal**: Deploy prediction system with API and dashboard

#### 5.1 Execution Simulator
**Automated**:
- Order book dynamics model
- Partial fill simulation
- Commission and slippage
- Kelly criterion sizing (fractional)
- Market impact estimation

#### 5.2 FastAPI Backend
**Automated**:
- `/predict` endpoint (race_id → probabilities)
- `/qualify` endpoint (trigger qual scan)
- `/backtest` endpoint (historical performance)
- `/meeting` endpoint (full card analysis)

#### 5.3 Streamlit Dashboard
**Automated**:
- Race card selector
- Probability table (win/place, fair odds)
- Edge calculator (vs Betfair/TAB)
- Recommended stakes (Kelly sizing)
- Uncertainty bands (conformal sets)
- Qualitative rationale (citations)
- Backtest performance charts

#### 5.4 Monitoring & Alerting
**Automated**:
- Model drift detection (PSI on features)
- Performance tracking (live Brier vs backtest)
- Data quality alerts
- API health checks

**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- [ ] **Review dashboard UX** - request changes
- [ ] **Test full workflow** - ingest → features → predict → display

**Deliverables**:
- ✅ `make serve` launches dashboard at localhost:8501
- ✅ Full race card analysis in <10 seconds
- ✅ All endpoints documented with examples

---

### **PHASE 6: Hardening & Production** (Days 43+)
**Goal**: Prepare for live operation

#### 6.1 Live Data Pipeline
**Automated**:
- Scheduled daily ingestion (cron/Prefect)
- Real-time Betfair streaming (final 5 min)
- Automatic retrain weekly
- Model A/B testing framework

#### 6.2 Paper Trading
**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- [ ] **Run paper trading for 50 races** - log predictions vs outcomes
- [ ] **Validate performance** - compare to backtest expectations
- [ ] **Approve for live use** - only after 50-race validation

#### 6.3 Live Trading (Optional)
**Manual Tasks**: 🚨 **USER ACTION REQUIRED**
- [ ] **Set risk limits** (max stake, daily loss limit, drawdown stop)
- [ ] **Implement kill switch** - manual override to stop all betting
- [ ] **Start with minimum stakes** - 1/10th target size for first 100 bets

---

## 🔧 Technology Stack

### Core
- **Language**: Python 3.11
- **Database**: DuckDB (embedded analytical DB)
- **Data Processing**: Polars (fast dataframes)
- **ML**: CatBoost, LightGBM, scikit-learn
- **Calibration**: scikit-learn, MAPIE (conformal)
- **API**: FastAPI
- **UI**: Streamlit
- **Testing**: pytest
- **Task Runner**: Make

### Data Sources
- **Racing Data**: Racing.com, Racing Victoria (scraping)
- **Market Data**: Betfair API (Historic + Stream)
- **Weather**: Open-Meteo / BOM
- **Qualitative**: ChatGPT Deep Research (manual initially)

### DevOps
- **Environment**: VS Code Devcontainer
- **Orchestration**: Prefect (later phases)
- **Versioning**: Git + DVC (data version control)
- **Monitoring**: Prometheus + Grafana (optional)

---

## 📊 Success Metrics

### Model Performance (Backtests)
- **Brier Score**: <0.20 (market baseline ~0.18-0.19)
- **AUC**: >0.75 (rank discrimination)
- **Calibration Error**: <3% at 90% confidence band
- **ROI**: >5% after commission/slippage (1000-race test set)

### System Quality
- **Data Completeness**: >80% on key features (sectionals, weather)
- **API Latency**: <2s for `/predict` (excluding Deep Research)
- **Uptime**: >99% during racing hours
- **Test Coverage**: >80% code coverage

### Operational
- **Backtest-Live Gap**: <10% difference in Brier score
- **Max Drawdown**: <20% of bankroll (paper trading)
- **Sharpe Ratio**: >1.5 (if live trading)

---

## 🚨 Manual Task Summary

### **Phase 1: Data Layer**
- [ ] Sign up for Betfair API (30 min)
- [ ] Sign up for weather API (10 min)
- [ ] Download sample Betfair historic data (1 hour)
- [ ] Test scrapers and validate outputs (1 hour)

### **Phase 2: Feature Engineering**
- [ ] Review feature distributions (30 min)
- [ ] Approve feature set (15 min)

### **Phase 3: Modeling**
- [ ] Review backtest results (1 hour)
- [ ] Approve model for next phase (15 min)

### **Phase 4: Qualitative**
- [ ] Set up ChatGPT Plus / Deep Research access (10 min)
- [ ] Run manual deep research (daily: 30 min)
- [ ] Set LR priors (30 min, one-time)
- [ ] Review fusion outputs (30 min)

### **Phase 5: API & UI**
- [ ] Review dashboard UX (30 min)
- [ ] Test full workflow (1 hour)

### **Phase 6: Production**
- [ ] Paper trading validation (50 races, ~1 week)
- [ ] Set risk limits (30 min)
- [ ] Approve for live use (decision point)

**Total Manual Time Estimate**: ~12 hours over 6 weeks

---

## 📁 Repository Structure

```
racing-analysis/
├── .devcontainer/
│   └── devcontainer.json         # VS Code container config
├── .github/
│   └── workflows/                # CI/CD (later)
├── configs/
│   ├── database.yml              # DB schema definitions
│   ├── features.yml              # Feature catalog
│   ├── models.yml                # Model hyperparameters
│   └── scrapers.yml              # Scraper configs
├── data/                         # Gitignored
│   ├── raw/
│   ├── processed/
│   ├── features/
│   ├── models/
│   └── betfair_historic/
├── src/
│   ├── connectors/
│   │   ├── betfair.py           # Betfair API client
│   │   ├── racing_scraper.py   # Racing.com scraper
│   │   ├── stewards_scraper.py # Stewards reports
│   │   └── weather.py           # Weather API
│   ├── etl/
│   │   ├── ingest.py            # Data ingestion
│   │   ├── validate.py          # Data quality checks
│   │   └── warehouse.py         # DuckDB interface
│   ├── features/
│   │   ├── sectionals.py        # Pace/sectional features
│   │   ├── ratings.py           # Distance/going curves
│   │   ├── trainers.py          # Trainer/jockey metrics
│   │   ├── market.py            # Market features
│   │   └── store.py             # Feature store
│   ├── models/
│   │   ├── train.py             # Model training
│   │   ├── calibrate.py         # Calibration
│   │   ├── conformal.py         # Uncertainty quantification
│   │   └── registry.py          # Model versioning
│   ├── fusion/
│   │   ├── claims.py            # Claim extraction
│   │   ├── likelihood_ratios.py # LR learning
│   │   └── fuser.py             # Bayesian fusion
│   ├── execution/
│   │   ├── simulator.py         # Execution sim
│   │   └── kelly.py             # Position sizing
│   ├── api/
│   │   ├── app.py               # FastAPI application
│   │   ├── schemas.py           # Pydantic models
│   │   └── routes/
│   ├── dashboard/
│   │   ├── app.py               # Streamlit app
│   │   └── components/
│   └── utils/
│       ├── config.py            # Config management
│       ├── logging.py           # Logging setup
│       └── metrics.py           # Performance metrics
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── notebooks/                    # Jupyter notebooks for analysis
├── scripts/
│   ├── setup_db.py              # Initialize database
│   ├── download_data.py         # Data download helpers
│   └── backtest_runner.py       # Backtest orchestration
├── .env.example                 # Template for secrets
├── .gitignore
├── Makefile                     # Task automation
├── pyproject.toml               # Python dependencies (uv/pip)
├── README.md                    # Project overview
└── MASTER_PLAN.md              # This document
```

---

## 🔄 Development Workflow

### Daily Development
```bash
# Start devcontainer in VS Code
# Open terminal in container

# Ingest latest data
make ingest date=today

# Compute features
make features date=today

# Train models (if needed)
make train

# Run predictions
make predict race_id=FLE-2025-11-09-R6

# Launch dashboard
make serve
```

### Weekly Workflow
```bash
# Retrain models
make train

# Run full backtest
make backtest period=last_30_days

# Check drift
make monitor_drift

# Review performance
make report
```

### Pre-Live Checklist
```bash
# Run all tests
make test

# Validate data quality
make validate_data

# Check calibration
make check_calibration

# Simulate execution
make simulate_execution

# Review logs
make review_logs
```

---

## ⚠️ Risk Management

### Model Risks
- **Overfitting**: Walk-forward validation, regularization, ensemble diversity
- **Concept Drift**: Weekly retraining, drift monitoring, automatic rollback
- **Data Leakage**: Strict time-ordering, manual audits of feature creation

### Execution Risks
- **Slippage**: Conservative assumptions (50% haircut on backtest ROI)
- **Market Impact**: Position size limits, liquidity checks
- **Latency**: Betfair Stream in final 5 min, <500ms order placement

### Operational Risks
- **Data Outages**: Graceful degradation, manual data entry fallback
- **API Rate Limits**: Request throttling, caching, retry logic
- **Model Failures**: Health checks, automatic fallback to simpler model

### Financial Risks
- **Drawdowns**: Kelly criterion with 1/4 to 1/2 fractional sizing
- **Stop Losses**: Maximum daily loss limit, maximum drawdown kill switch
- **Stake Limits**: Never exceed 5% of bankroll on single race

---

## 📈 Future Enhancements (Post-MVP)

### Advanced Modeling
- Hierarchical Bayesian logistic regression
- Full Monte Carlo pace simulation
- Meeting-level bias detection (live)
- Neural networks for non-linear interactions

### Data Expansion
- International form integration (Japan, Europe)
- Barrier trial data
- Track work data (where available)
- Jockey booking timing signals

### Qualitative Improvements
- Automated Deep Research via API (when available)
- LLM-based stewards report parsing
- Parade ring video analysis (ML vision)
- Social media sentiment (trainer/jockey confidence)

### Operations
- Multi-market support (Hong Kong, UK)
- Automated live trading
- Portfolio optimization across multiple races
- Mobile app for live updates

---

## 🎓 Learning Resources

### Racing Domain
- [TimeformUS Speed Figures](https://www.timeform.com/)
- [Betfair Trading Guide](https://betting.betfair.com/how-to-use-betfair/)
- [Racing Victoria Stewards](https://www.racingvictoria.com.au/the-sport/stewards)

### Modeling
- [Applied Predictive Modeling (Kuhn)](https://link.springer.com/book/10.1007/978-1-4614-6849-3)
- [Conformal Prediction Tutorial](https://github.com/valeman/awesome-conformal-prediction)
- [Calibration in Modern ML (Guo et al.)](https://arxiv.org/abs/1706.04599)

### Trading
- [Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion)
- [Execution Algorithms](https://www.quantstart.com/articles/)

---

## ✅ Current Status

**Phase**: 0 - Foundation  
**Progress**: 10% (plan created, ready to build)  
**Next Steps**: 
1. Create repository structure
2. Set up devcontainer
3. Initialize database schema
4. Begin Phase 1 data connectors

**Last Updated**: November 8, 2025  
**Owner**: thomasrocks006-cmyk

---

## 📝 Change Log

| Date | Phase | Change | Reason |
|------|-------|--------|--------|
| 2025-11-08 | Planning | Initial plan created | Project kickoff |
| 2025-11-08 | Planning | Removed licensing requirements | Non-commercial use |
| 2025-11-08 | Planning | Adjusted Deep Research cost model | ChatGPT Plus available |

---

**Ready to build. Let's start with Phase 0.**
