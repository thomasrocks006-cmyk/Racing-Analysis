# Racing Analysis System

**AI-powered horse racing prediction system with quantitative modeling and qualitative research fusion.**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Overview

This system combines:
- **Quantitative modeling**: CatBoost/LightGBM with calibration and conformal prediction
- **Qualitative research**: Deep Research integration for contextual insights
- **Execution simulation**: Realistic ROI estimation with commission and slippage
- **Real-time integration**: Betfair API for live market data

**Goal**: Produce calibrated win/place probabilities and identify value betting opportunities.

---

## 🚀 Quick Start

### Prerequisites
- VS Code with Dev Containers extension
- Docker Desktop
- Git

### Setup

1. **Clone and open in container**:
   ```bash
   git clone <repo-url>
   cd Racing-Analysis
   code .
   # VS Code will prompt to "Reopen in Container" - click it
   ```

2. **Wait for automatic setup** (runs `.devcontainer/post-create.sh`):
   - Installs dependencies
   - Creates database
   - Sets up directories

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (see MASTER_PLAN.md for details)
   ```

4. **Verify installation**:
   ```bash
   make status
   make test
   ```

---

## 📖 Usage

### Daily Workflow

```bash
# Ingest data for today
make ingest date=2025-11-09

# Compute features
make features date=2025-11-09

# Make predictions for a race
make predict race_id=FLE-2025-11-09-R6

# Launch dashboard
make serve
```

### Development

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Format code
make format

# Check for issues
make lint
```

### Modeling

```bash
# Train models
make train

# Run backtest
make backtest period=last_30_days

# Generate report
make report
```

See `make help` for all available commands.

---

## 📁 Project Structure

```
racing-analysis/
├── src/
│   ├── connectors/       # Data source integrations
│   ├── etl/              # Data pipeline
│   ├── features/         # Feature engineering
│   ├── models/           # ML models
│   ├── fusion/           # Qualitative integration
│   ├── execution/        # Betting simulation
│   ├── api/              # FastAPI backend
│   └── dashboard/        # Streamlit UI
├── tests/                # Unit & integration tests
├── configs/              # Configuration files
├── scripts/              # Utility scripts
├── data/                 # Data storage (gitignored)
└── MASTER_PLAN.md       # Complete implementation guide
```

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

## 📚 Documentation

- **[MASTER_PLAN.md](MASTER_PLAN.md)**: Complete implementation guide
- **[API Documentation](http://localhost:8000/docs)**: FastAPI docs (when running)
- **[Dashboard](http://localhost:8501)**: Streamlit UI (when running)

---

## 🤝 Contributing

This is a personal project, but suggestions are welcome via issues.

---

## 📝 License

MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgements

- Betfair for API access
- Open-Meteo for weather data
- Racing Victoria for stewards reports
- CatBoost & LightGBM teams

---

**Built with ❤️ for smarter racing analysis**

*Last updated: November 8, 2025* 
