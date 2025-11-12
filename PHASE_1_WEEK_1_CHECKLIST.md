# Phase 1 - Week 1 Checklist

**Date Started:** November 12, 2025  
**Goal:** Database schema design + initial web scrapers  
**Target:** 50 races with 80%+ data completeness

---

## ✅ Environment Setup (COMPLETE)

- [x] Python 3.11+ installed
- [x] All Phase 1 packages installed:
  - [x] requests, beautifulsoup4, selenium, lxml (web scraping)
  - [x] pandas, polars, pyarrow, duckdb (data processing)
  - [x] pydantic (validation)
  - [x] scikit-learn, catboost, lightgbm, xgboost (ML)
  - [x] optuna (hyperparameter tuning)
  - [x] mapie, netcal (calibration & uncertainty)
- [x] Git repository ready
- [x] Documentation organized (DOCS_MANIFEST.md)

---

## 📋 Week 1 Tasks (Days 1-7)

### Day 1-2: Database Schema Design

**Goal:** Design DuckDB schema for racing data storage

- [ ] **Create database schema file** (`src/data/schema.sql`)
  - [ ] `races` table (race_id, date, venue, track_condition, distance, class)
  - [ ] `runs` table (run_id, race_id, horse_id, jockey_id, trainer_id, barrier, weight)
  - [ ] `horses` table (horse_id, name, age, sex, color, sire, dam)
  - [ ] `jockeys` table (jockey_id, name, active_since)
  - [ ] `trainers` table (trainer_id, name, stable_location)
  - [ ] `results` table (run_id, finish_position, margin, time, sectionals)
  - [ ] `market_odds` table (run_id, timestamp, betfair_odds, tab_odds)
  - [ ] `stewards` table (race_id, report_text, incident_type)
  - [ ] `gear` table (run_id, gear_type, first_time)

- [ ] **Create Pydantic validation models** (`src/data/models.py`)
  - [ ] `Race` model
  - [ ] `Run` model
  - [ ] `Horse` model
  - [ ] `Result` model
  - [ ] `MarketOdds` model

- [ ] **Create database initialization script** (`src/data/init_db.py`)
  - [ ] Load schema.sql
  - [ ] Create tables if not exists
  - [ ] Add indexes (race_id, horse_id, date)
  - [ ] Add constraints (foreign keys, check constraints)

**Deliverable:** Working DuckDB database with proper schema

**Reference:** 
- `docs/quantitative-pipeline/PART_1_OVERVIEW_AND_CATEGORIES.md` (data requirements)
- DuckDB docs: https://duckdb.org/docs/

---

### Day 3-5: Web Scraper Development

**Goal:** Build scrapers for Racing.com and basic data sources

#### Task 1: Racing.com Results Scraper

- [ ] **Create base scraper** (`src/data/scrapers/racing_com.py`)
  - [ ] `RacingComScraper` class
  - [ ] `get_race_card(venue, date)` method
  - [ ] `get_results(race_id)` method
  - [ ] Error handling & retries
  - [ ] Rate limiting (respect robots.txt)

- [ ] **Parse race data**
  - [ ] Extract race details (venue, distance, class, track condition)
  - [ ] Extract runner details (horse, jockey, trainer, barrier, weight)
  - [ ] Extract results (finish position, margin, time)
  - [ ] Extract gear changes

- [ ] **Test scraper**
  - [ ] Scrape 5 recent race cards
  - [ ] Validate data completeness (>80%)
  - [ ] Check data quality (no missing critical fields)

#### Task 2: Stewards Reports Scraper

- [ ] **Create stewards scraper** (`src/data/scrapers/stewards.py`)
  - [ ] `StewardsScraper` class
  - [ ] `get_report(race_id)` method
  - [ ] Extract incident types (protests, inquiries, falls)
  - [ ] Parse report text

#### Task 3: Market Odds Collector (Basic)

- [ ] **Create odds collector** (`src/data/scrapers/market_odds.py`)
  - [ ] `MarketOddsCollector` class
  - [ ] `get_betfair_odds(race_id)` method (placeholder)
  - [ ] `get_tab_odds(race_id)` method (basic scraping)
  - [ ] Store odds with timestamp

**Note:** Betfair API integration in Week 2 after account setup

**Deliverable:** Working scrapers that collect race data

**Reference:**
- Beautiful Soup docs: https://www.crummy.com/software/BeautifulSoup/
- Selenium docs: https://selenium-python.readthedocs.io/

---

### Day 6-7: Data Ingestion Pipeline

**Goal:** Automated pipeline to scrape → validate → store

- [ ] **Create ETL pipeline** (`src/data/etl_pipeline.py`)
  - [ ] `ETLPipeline` class
  - [ ] `scrape_race(race_id)` - orchestrate scrapers
  - [ ] `validate_data(data)` - Pydantic validation
  - [ ] `store_data(data)` - insert into DuckDB
  - [ ] `check_completeness(race_id)` - verify 80%+ complete

- [ ] **Create data quality checks** (`src/data/quality.py`)
  - [ ] Check for missing critical fields
  - [ ] Validate data types
  - [ ] Check for duplicates
  - [ ] Flag anomalies (e.g., impossible times)

- [ ] **Create ingestion script** (`scripts/ingest_race.py`)
  - [ ] CLI interface: `python scripts/ingest_race.py --date 2025-11-09 --venue FLE`
  - [ ] Progress bar (tqdm)
  - [ ] Error logging
  - [ ] Summary report

**Deliverable:** Automated pipeline that ingests race data

**Test:** Ingest 10 races and verify data in database

---

## 🎯 Week 1 Success Criteria

By end of Week 1, you should have:

1. ✅ **Working DuckDB database** with proper schema
2. ✅ **3 working scrapers** (Racing.com, Stewards, Basic odds)
3. ✅ **Data validation** via Pydantic models
4. ✅ **ETL pipeline** that orchestrates scrape → validate → store
5. ✅ **10+ races ingested** with 80%+ data completeness

**Metrics:**
- Data completeness: >80% (critical fields present)
- Scraper success rate: >90% (successful requests)
- Data quality: 0 validation errors
- Pipeline runtime: <5 min per race

---

## 📚 Key References

**Documentation:**
- [PHASE_0_COMPLETE.md](PHASE_0_COMPLETE.md) - Full Phase 1 roadmap
- [docs/quantitative-pipeline/PART_1_OVERVIEW_AND_CATEGORIES.md](docs/quantitative-pipeline/PART_1_OVERVIEW_AND_CATEGORIES.md) - Data requirements
- [docs/DOCS_MANIFEST.md](docs/DOCS_MANIFEST.md) - Complete doc index

**External Resources:**
- DuckDB: https://duckdb.org/docs/
- Pydantic: https://docs.pydantic.dev/
- Beautiful Soup: https://www.crummy.com/software/BeautifulSoup/
- Selenium: https://selenium-python.readthedocs.io/

---

## 🔧 Useful Commands

```bash
# Initialize database
python src/data/init_db.py

# Test scrapers
python src/data/scrapers/racing_com.py --test

# Ingest a race
python scripts/ingest_race.py --date 2025-11-09 --venue FLE

# Check database
duckdb data/racing.duckdb "SELECT COUNT(*) FROM races;"

# View recent races
duckdb data/racing.duckdb "SELECT * FROM races ORDER BY date DESC LIMIT 10;"
```

---

## ⚠️ Important Notes

**API Accounts Needed (Week 2):**
- [ ] Betfair API account (https://developer.betfair.com/) - FREE
- [ ] Weather API (open-meteo.com) - FREE, no key needed

**Scraping Best Practices:**
- ✅ Respect robots.txt
- ✅ Rate limit (1-2 sec between requests)
- ✅ Use descriptive User-Agent
- ✅ Handle errors gracefully
- ✅ Cache responses where appropriate

**Time-Ordered Data:**
- ⚠️ CRITICAL: Only scrape historical data (no future data)
- ⚠️ Add `scraped_at` timestamp to all tables
- ⚠️ Ensure race date < scrape date (prevent data leakage)

---

## 🚀 Getting Started

**Right now, start with:**

1. Create directory structure:
   ```bash
   mkdir -p src/data/scrapers
   mkdir -p scripts
   mkdir -p data
   ```

2. Create `src/data/schema.sql` with table definitions

3. Create `src/data/init_db.py` to initialize database

4. Test database creation:
   ```bash
   python src/data/init_db.py
   duckdb data/racing.duckdb "SHOW TABLES;"
   ```

**Then proceed with scraper development (Day 3-5)**

---

**Week 1 Status:** ⏳ In Progress (Started: 2025-11-12)  
**Next Review:** End of Week 1 (check success criteria)
