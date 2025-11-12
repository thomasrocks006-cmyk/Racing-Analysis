.PHONY: help install test clean setup ingest features train predict backtest serve

# Colors for output
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

help: ## Show this help message
	@echo '${GREEN}Racing Analysis - Available Commands${RESET}'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-20s${RESET} %s\n", $$1, $$2}'
	@echo ''

# ============================================================================
# Setup & Installation
# ============================================================================

install: ## Install Python dependencies
	@echo "${GREEN}Installing dependencies...${RESET}"
	pip install -e ".[dev]"
	@echo "${GREEN}✓ Installation complete${RESET}"

setup: install ## Full setup (install + database + directories)
	@echo "${GREEN}Setting up Racing Analysis...${RESET}"
	mkdir -p data/{raw,processed,features,models,betfair_historic,qual_claims}
	mkdir -p data/raw/{races,markets,weather,stewards,gear}
	mkdir -p logs
	python scripts/setup_db.py
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "${GREEN}✓ Setup complete${RESET}"

clean: ## Clean generated files and cache
	@echo "${YELLOW}Cleaning...${RESET}"
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "${GREEN}✓ Clean complete${RESET}"

# ============================================================================
# Data Pipeline
# ============================================================================

ingest: ## Ingest data for a specific date (usage: make ingest date=2025-11-09)
	@echo "${GREEN}Ingesting data for ${date}...${RESET}"
	python -m src.etl.ingest --date=$(date)
	@echo "${GREEN}✓ Ingest complete${RESET}"

ingest-betfair: ## Ingest Betfair historic data
	@echo "${GREEN}Ingesting Betfair historic data...${RESET}"
	python -m src.connectors.betfair --mode=historic
	@echo "${GREEN}✓ Betfair ingest complete${RESET}"

features: ## Compute features for a specific date (usage: make features date=2025-11-09)
	@echo "${GREEN}Computing features for ${date}...${RESET}"
	python -m src.features.store --date=$(date)
	@echo "${GREEN}✓ Feature computation complete${RESET}"

validate: ## Validate data quality
	@echo "${GREEN}Validating data quality...${RESET}"
	python -m src.etl.validate
	@echo "${GREEN}✓ Validation complete${RESET}"

# ============================================================================
# Modeling
# ============================================================================

train: ## Train models
	@echo "${GREEN}Training models...${RESET}"
	python -m src.models.train
	@echo "${GREEN}✓ Training complete${RESET}"

calibrate: ## Calibrate model probabilities
	@echo "${GREEN}Calibrating models...${RESET}"
	python -m src.models.calibrate
	@echo "${GREEN}✓ Calibration complete${RESET}"

backtest: ## Run backtest (usage: make backtest period=last_30_days)
	@echo "${GREEN}Running backtest...${RESET}"
	python scripts/backtest_runner.py --period=$(or $(period),last_30_days)
	@echo "${GREEN}✓ Backtest complete${RESET}"

# ============================================================================
# Prediction & Analysis
# ============================================================================

predict: ## Make predictions (usage: make predict race_id=FLE-2025-11-09-R6)
	@echo "${GREEN}Generating predictions for ${race_id}...${RESET}"
	python -m src.api.app predict --race-id=$(race_id)
	@echo "${GREEN}✓ Predictions generated${RESET}"

meeting: ## Analyze full race meeting (usage: make meeting venue=FLE date=2025-11-09)
	@echo "${GREEN}Analyzing meeting ${venue} on ${date}...${RESET}"
	python -m src.api.app meeting --venue=$(venue) --date=$(date)
	@echo "${GREEN}✓ Meeting analysis complete${RESET}"

qual-scan: ## Run qualitative scan (usage: make qual-scan race_id=FLE-2025-11-09-R6)
	@echo "${YELLOW}Qualitative scan for ${race_id}...${RESET}"
	@echo "${YELLOW}Note: This requires manual Deep Research - check MASTER_PLAN.md${RESET}"
	python -m src.fusion.claims --race-id=$(race_id)

# ============================================================================
# Serving & UI
# ============================================================================

serve: ## Launch Streamlit dashboard
	@echo "${GREEN}Launching dashboard at http://localhost:8501${RESET}"
	streamlit run src/dashboard/app.py

api: ## Start FastAPI server
	@echo "${GREEN}Starting FastAPI server at http://localhost:8000${RESET}"
	uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# ============================================================================
# Testing & Quality
# ============================================================================

test: ## Run all tests
	@echo "${GREEN}Running tests...${RESET}"
	pytest tests/ -v
	@echo "${GREEN}✓ Tests complete${RESET}"

test-cov: ## Run tests with coverage report
	@echo "${GREEN}Running tests with coverage...${RESET}"
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "${GREEN}✓ Coverage report generated in htmlcov/index.html${RESET}"

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

lint: ## Run linting checks
	@echo "${GREEN}Running linter...${RESET}"
	ruff check src/ tests/
	@echo "${GREEN}✓ Linting complete${RESET}"

format: ## Format code
	@echo "${GREEN}Formatting code...${RESET}"
	ruff format src/ tests/
	@echo "${GREEN}✓ Formatting complete${RESET}"

type-check: ## Run type checking
	@echo "${GREEN}Running type checker...${RESET}"
	mypy src/
	@echo "${GREEN}✓ Type checking complete${RESET}"

# ============================================================================
# Monitoring & Debugging
# ============================================================================

monitor-drift: ## Check for feature drift
	@echo "${GREEN}Monitoring feature drift...${RESET}"
	python -m src.utils.monitor --check-drift
	@echo "${GREEN}✓ Drift check complete${RESET}"

report: ## Generate performance report
	@echo "${GREEN}Generating performance report...${RESET}"
	python scripts/generate_report.py
	@echo "${GREEN}✓ Report generated in reports/latest.html${RESET}"

logs: ## Tail application logs
	tail -f logs/racing-analysis.log

db-shell: ## Open DuckDB shell
	duckdb data/racing.duckdb

# ============================================================================
# Data Downloads (Manual Helpers)
# ============================================================================

download-betfair-sample: ## Download sample Betfair data (requires manual action)
	@echo "${YELLOW}===========================================================${RESET}"
	@echo "${YELLOW}MANUAL ACTION REQUIRED${RESET}"
	@echo "${YELLOW}===========================================================${RESET}"
	@echo "1. Go to: https://historicdata.betfair.com/"
	@echo "2. Login with your Betfair account"
	@echo "3. Download Australian horse racing data (sample or full)"
	@echo "4. Extract to: data/betfair_historic/"
	@echo "5. Then run: make ingest-betfair"
	@echo "${YELLOW}===========================================================${RESET}"

# ============================================================================
# Utility
# ============================================================================

.PHONY: verify-glm
verify-glm:
	@echo "Verifying GLM API setup..."
	python scripts/verify_glm_setup.py

.PHONY: verify-copilot
verify-copilot:
	@echo "Verifying GitHub Copilot API setup..."
	python scripts/verify_copilot_api.py

.PHONY: verify-ai
verify-ai: verify-glm verify-copilot
	@echo ""
	@echo "=========================================="
	@echo "✅ All AI API verifications complete!"
	@echo "=========================================="

version: ## Show version info
	@echo "${GREEN}Racing Analysis v0.1.0${RESET}"
	@python --version
	@echo "DuckDB: $$(python -c 'import duckdb; print(duckdb.__version__)')"
	@echo "Polars: $$(python -c 'import polars; print(polars.__version__)')"
	@echo "CatBoost: $$(python -c 'import catboost; print(catboost.__version__)')"

status: ## Show system status
	@echo "${GREEN}Racing Analysis Status${RESET}"
	@echo "Environment: $$(cat .env | grep ENVIRONMENT | cut -d '=' -f2)"
	@echo "Database: $$(ls -lh data/racing.duckdb 2>/dev/null | awk '{print $$5}' || echo 'Not created')"
	@echo "Features: $$(find data/features -name '*.parquet' 2>/dev/null | wc -l) files"
	@echo "Models: $$(find data/models -name '*.cbm' -o -name '*.txt' 2>/dev/null | wc -l) files"
	@echo "Logs: $$(ls -lh logs/racing-analysis.log 2>/dev/null | awk '{print $$5}' || echo 'No logs yet')"

.DEFAULT_GOAL := help
