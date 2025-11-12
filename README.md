# Racing Analysis System

**Production-ready AI horse racing prediction system with dual-pipeline architecture and concurrent multi-agent Bayesian fusion.**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Phase: 0 Complete](https://img.shields.io/badge/Phase-0%20Complete-green.svg)](PHASE_0_COMPLETE.md)

---

## 🎯 Project Status

**Current Phase:** Phase 0 Complete ✅ - Design & Architecture (100%)  
**Next Phase:** Phase 1 Starting - Data Layer Implementation (8 weeks)

### What We've Built

- ✅ **Complete Architecture Design** (~10,000 lines across 3 pipelines)
- ✅ **Qualitative Pipeline** (5 parts, ~5,000 lines) - Multi-stage LLM chain
- ✅ **Quantitative Pipeline** (3 parts, ~3,100 lines) - ML ensemble with calibration
- ✅ **Fusion Model** (2 docs, ~2,200 lines) - 15 concurrent agents via E2B forking
- ✅ **Documentation Organized** (85 active files, clear hierarchy)
- ✅ **Master Plan Updated** with fusion model details

**Read:** [PHASE_0_COMPLETE.md](PHASE_0_COMPLETE.md) for full status and Phase 1 roadmap

---

## 🏗️ System Architecture

### Dual Pipeline + Concurrent Fusion

```
Qualitative Pipeline          Quantitative Pipeline
(Categories 1-17)            (Categories 18-21)
      ↓                            ↓
Likelihood Ratios (LRs)      Base Probabilities
      ↓                            ↓
      └──────────┬─────────────────┘
                 ↓
    15 Concurrent Agents (E2B Forking)
    • Bayesian LR Weighting (3 agents)
    • Calibration Methods (3 agents)
    • Normalization Strategies (3 agents)
    • Uncertainty Quantification (3 agents)
    • Matrix Integration (3 agents)
                 ↓
         Consensus Synthesis
                 ↓
    Final Probabilities + Confidence
```

**Performance Targets:**
- Brier Score: 0.16 (11% better than sequential fusion)
- ROI: 7.2% after commission/slippage
- Cost: $0.96/race ($0.66 qual + $0.30 fusion)
- Runtime: 7-9 minutes per race

---

## 📚 Documentation

### Start Here

1. **[README.md](README.md)** ← You are here - Quick overview
2. **[PHASE_0_COMPLETE.md](PHASE_0_COMPLETE.md)** - Current status & Phase 1 roadmap
3. **[MASTER_PLAN.md](MASTER_PLAN.md)** - Complete system architecture
4. **[docs/DOCS_MANIFEST.md](docs/DOCS_MANIFEST.md)** - Full documentation index

### Architecture Deep Dive

- **[TAXONOMY_OVERVIEW.md](TAXONOMY_OVERVIEW.md)** - 21 categories explained
- **[docs/qualitative-pipeline/](docs/qualitative-pipeline/)** - 5-part LLM chain design
- **[docs/quantitative-pipeline/](docs/quantitative-pipeline/)** - 3-part ML ensemble design
- **[docs/FUSION_MODEL_ARCHITECTURE.md](docs/FUSION_MODEL_ARCHITECTURE.md)** - Concurrent multi-agent Bayesian integration

### Setup & Reference

- **[docs/setup/](docs/setup/)** - API configuration guides (11 files)
- **[docs/reference/](docs/reference/)** - Model research & strategies (6 files)
- **[docs/archive/](docs/archive/)** - Historical documentation (46 files)

**Total Documentation:** ~27,000 lines across 30+ canonical documents

---

## 🚀 Quick Start (Phase 1 - Data Layer)

**Current Phase:** Data collection and quantitative baseline (8 weeks)

### Prerequisites

- VS Code with Dev Containers extension
- Docker Desktop running
- Git installed

### Setup (5 minutes)

1. **Clone and open in container**:

   ```bash
   git clone <repo-url>
   cd Racing-Analysis
   code .
   # VS Code will prompt to "Reopen in Container" - click it
   ```

2. **Environment setup complete** ✅
   - Python 3.11+ ready
   - DuckDB installed
   - Git configured
   - GitHub Copilot active

3. **Next: Install Phase 1 packages**:

   ```bash
   # Data collection
   pip install requests beautifulsoup4 selenium lxml
   
   # Data processing  
   pip install pandas polars pyarrow duckdb pydantic
   
   # ML & feature engineering
   pip install scikit-learn catboost lightgbm xgboost optuna
   
   # Calibration & uncertainty
   pip install mapie netcal
   ```

4. **API Setup (Required for Phase 1)**:
   - [ ] Sign up for [Betfair API](https://developer.betfair.com/) (free)
   - [ ] Configure `.env` file with API keys
   - [ ] Verify with test script (coming in Week 1)

**Read Next:** [PHASE_0_COMPLETE.md](PHASE_0_COMPLETE.md) - Week 1-8 detailed roadmap

---

## 🏃 Phase 1 Workflow (Weeks 1-8)

**Week 1-2: Data Collection**

```bash
# Design database schema (DuckDB)
# Create tables: races, runs, horses, jockeys, trainers

# Build web scrapers
# Target: Racing.com + Stewards + Market odds

# Goal: 50 races with 80%+ completeness
```

**Week 3-4: Feature Engineering**

```bash
# Implement speed ratings (Category 18)
# Implement class ratings (Category 19)
# Build sectional analysis (Category 20)
# Pedigree modeling (Category 21)

# Goal: 50+ features per horse
```

**Week 5-6: ML Training**

```bash
# Train CatBoost + LightGBM + XGBoost
# Hyperparameter tuning with Optuna
# Feature importance analysis

# Goal: Brier score <0.22 (baseline)
```

**Week 7-8: Calibration**

```bash
# Isotonic regression per track group
# Conformal prediction sets
# Uncertainty quantification

# Goal: Calibration error <5%
```

**Detailed Roadmap:** See [PHASE_0_COMPLETE.md](PHASE_0_COMPLETE.md) sections Week 1-8

---

## 📊 System Components

### Pipelines (Production-Ready Designs)

**1. Qualitative Pipeline** (Categories 1-17)
- Multi-stage LLM chain: Gemini Flash 2.0 → GPT-5 → Claude Sonnet 4.5 → GPT-4o
- Output: Likelihood Ratios (LRs) for each category
- Cost: $0.66/race | Runtime: 5-7 minutes
- Docs: [docs/qualitative-pipeline/](docs/qualitative-pipeline/) (5 parts)

**2. Quantitative Pipeline** (Categories 18-21)
- ML ensemble: CatBoost + LightGBM + XGBoost
- Features: Speed ratings, class, sectionals, pedigree (100+)
- Output: Calibrated base probabilities
- Cost: $0.00/race | Runtime: 1-2 minutes
- Docs: [docs/quantitative-pipeline/](docs/quantitative-pipeline/) (3 parts)

**3. Fusion Model** (Concurrent Multi-Agent)
- 15 concurrent agents via E2B forking
- Bayesian integration of qualitative LRs + quantitative probabilities
- Output: Final probabilities + confidence intervals
- Cost: $0.30/race | Runtime: 30-60 seconds
- Docs: [docs/FUSION_MODEL_ARCHITECTURE.md](docs/FUSION_MODEL_ARCHITECTURE.md)

---

## 📁 Project Structure

```
Racing-Analysis/
├── MASTER_PLAN.md                # System architecture & implementation plan
├── PHASE_0_COMPLETE.md           # Current status & Phase 1 roadmap
├── TAXONOMY_OVERVIEW.md          # 21 categories explained
├── README.md                     # This file
│
├── docs/
│   ├── DOCS_MANIFEST.md          # Complete documentation index
│   ├── qualitative-pipeline/     # 5-part LLM chain design
│   ├── quantitative-pipeline/    # 3-part ML ensemble design
│   ├── FUSION_MODEL_ARCHITECTURE.md
│   ├── FUSION_MODEL_CRITICAL_ANALYSIS.md
│   ├── setup/                    # API configuration (11 files)
│   ├── reference/                # Model research (6 files)
│   └── archive/                  # Historical docs (46 files)
│
├── src/                          # Source code (Phase 1+)
│   ├── data/                     # Data collection & ETL
│   ├── features/                 # Feature engineering
│   ├── models/                   # ML model training
│   ├── fusion/                   # Fusion model implementation
│   ├── api/                      # FastAPI backend
│   └── dashboard/                # Streamlit UI
│
├── tests/                        # Unit & integration tests
├── configs/                      # Configuration files
└── scripts/                      # Utility scripts
```

**Current State:** Phase 0 (design) complete, Phase 1 (src/) to be implemented

---

## 🧪 Testing

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests
make test-integration

# With coverage
make test-cov
```

---

## 📊 Data Sources

- **Racing Data**: Racing.com, Racing Victoria (web scraping)
- **Market Data**: Betfair API (Historic + Stream)
- **Weather**: Open-Meteo API
- **Qualitative**: ChatGPT Deep Research (manual workflow)

**Note**: For non-commercial personal use. See MASTER_PLAN.md for API setup instructions.

---

## 🔧 Configuration

Key settings in `.env`:
- `BETFAIR_APP_KEY`: Betfair API credentials
- `WEATHER_API_KEY`: Weather data access
- `MODEL_TYPE`: catboost, lightgbm, or ensemble
- `KELLY_FRACTION`: Position sizing (0.25 = quarter Kelly)
- `MAX_STAKE_PER_RACE`: Risk limit per bet

See `.env.example` for full configuration options.

---

## 📈 Performance Targets

**Model Metrics** (Backtest):
- Brier Score: <0.20
- AUC: >0.75
- Calibration Error: <3%
- ROI: >5% (after commission/slippage)

**System Quality**:
- API Latency: <2s
- Data Completeness: >80%
- Test Coverage: >80%

---

## 🛣️ Roadmap

- [x] Phase 0: Foundation & scaffolding
- [ ] Phase 1: Data layer & ETL
- [ ] Phase 2: Feature engineering
- [ ] Phase 3: Modeling core
- [ ] Phase 4: Qualitative integration
- [ ] Phase 5: API & dashboard
- [ ] Phase 6: Production hardening

See `MASTER_PLAN.md` for detailed timeline and manual tasks.

---

## ⚠️ Risk Disclaimer

This software is for **educational and personal use only**.

- No guarantees of profitability
- Past performance does not indicate future results
- Gambling involves risk of financial loss
- Always bet responsibly within your means

---

## 🎯 Performance Targets

**Phase 1 (Baseline Quantitative):**
- Brier Score: <0.22
- Calibration Error: <5%
- Feature Count: 50+
- Coverage (90% CI): 85-95%

**Phase 2+3 (Full System):**
- Brier Score: 0.16 (fusion model)
- ROI: 7.2% after commission
- Calibration Error: <2%
- Annual Profit: +$1,700 (250 races)

---

## 🛠️ Technology Stack

**Data & ML:**
- Python 3.11+
- DuckDB (local warehouse)
- CatBoost, LightGBM, XGBoost (ensemble)
- pandas, polars (data processing)
- scikit-learn (calibration)
- mapie, netcal (uncertainty)

**Qualitative AI (Phase 2):**
- Gemini Flash 2.0 (source planning)
- GPT-5 Preview (deep reasoning)
- Claude Sonnet 4.5 (synthesis)
- GPT-4o (quality verification)
- LangChain (orchestration)

**Fusion (Phase 3):**
- E2B Sandboxes (concurrent agents)
- OpenHands Framework (micro-agents)
- FastAPI (coordination)
- Redis (state management)

**Development:**
- VS Code + Dev Containers
- GitHub Copilot
- Git version control
- pytest (testing)

---

## 📚 Documentation Index

**Getting Started:**
1. [README.md](README.md) - Project overview (you are here)
2. [PHASE_0_COMPLETE.md](PHASE_0_COMPLETE.md) - Status & Phase 1 roadmap
3. [MASTER_PLAN.md](MASTER_PLAN.md) - Complete system architecture

**Architecture:**
- [TAXONOMY_OVERVIEW.md](TAXONOMY_OVERVIEW.md) - 21 categories explained
- [docs/DOCS_MANIFEST.md](docs/DOCS_MANIFEST.md) - Complete documentation index
- [docs/qualitative-pipeline/](docs/qualitative-pipeline/) - LLM chain (5 parts)
- [docs/quantitative-pipeline/](docs/quantitative-pipeline/) - ML ensemble (3 parts)
- [docs/FUSION_MODEL_ARCHITECTURE.md](docs/FUSION_MODEL_ARCHITECTURE.md) - Concurrent fusion

**Setup & Reference:**
- [docs/setup/](docs/setup/) - API configuration guides
- [docs/reference/](docs/reference/) - Model research & strategies

---

## 🤝 Contributing

This is a personal research project. Design phase (Phase 0) is complete. Implementation starting Phase 1 (data layer).

---

## 📝 License

MIT License - Personal use only, no commercial application.

---

## 🙏 Acknowledgements

**Data Sources:**
- Betfair (market data API)
- Racing.com (official form)
- Racing Victoria (stewards reports)
- Open-Meteo (weather data)

**Technology:**
- OpenAI (GPT-5, GPT-4o)
- Anthropic (Claude Sonnet 4.5)
- Google (Gemini Flash 2.0)
- CatBoost, LightGBM, XGBoost teams
- E2B (sandbox infrastructure)
- GitHub Copilot

---

**Phase 0 Complete ✅ | Phase 1 Ready to Start 🚀**

*Last updated: November 12, 2025*
