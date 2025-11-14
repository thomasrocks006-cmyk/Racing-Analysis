# GitHub Copilot Agent Skills

These specialized skill documents guide the GitHub Copilot agent in this workspace. Each skill contains best practices, code patterns, common workflows, and success criteria for a specific domain.

## How to Use

When you want the agent to apply specialized knowledge, reference the skill by name:

**Format:**
```
Use [SKILL_NAME] skill: [TASK_DESCRIPTION]
```

**Examples:**
- "Use data-engineering skill: Create a new Betfair odds scraper"
- "Use model-development skill: Build features for win prediction"
- "Use analysis-insights skill: Analyze gear change impact on performance"
- "Use integration-orchestration skill: Connect the scraper to feature pipeline"
- "Use testing-qa skill: Write comprehensive tests for the new scraper"

## Available Skills

### 📊 [Data Engineering](./data-engineering.md)
Handle data pipeline tasks: scraping, validation, transformation, and storage.

**Best for:**
- Creating new data scrapers
- Adding data validation
- Refactoring pipelines
- Integrating new data sources
- Fixing data quality issues

**Key Patterns:**
- GraphQL API usage (Racing.com)
- Selenium web scraping
- Rate limiting and error handling
- Data model design

---

### 🤖 [Model Development](./model-development.md)
Handle machine learning tasks: feature engineering, model training, evaluation, and optimization.

**Best for:**
- Feature engineering
- Model training with CatBoost
- Hyperparameter optimization
- Performance evaluation
- Model comparison and selection

**Key Patterns:**
- DuckDB feature queries
- CatBoost configuration
- Train/val/test splits
- Evaluation metrics

---

### 📈 [Analysis & Insights](./analysis-insights.md)
Handle analytical tasks: exploratory data analysis, hypothesis testing, reporting, and insights.

**Best for:**
- Exploratory data analysis
- Statistical testing
- Visualization creation
- Report generation
- Hypothesis validation

**Key Patterns:**
- DuckDB queries
- Pandas DataFrames
- Statistical tests (scipy)
- Matplotlib/Seaborn visualization

---

### 🔗 [Integration & Orchestration](./integration-orchestration.md)
Handle system integration: pipeline orchestration, API integration, data flow coordination.

**Best for:**
- Building end-to-end pipelines
- Integrating new APIs
- Fixing data flow issues
- Orchestrating batch jobs
- Error handling and recovery

**Key Patterns:**
- Pipeline design
- Error handling with retry
- Logging and monitoring
- Cross-module coordination

---

### ✅ [Testing & Quality Assurance](./testing-qa.md)
Handle testing and quality assurance: unit tests, integration tests, code quality.

**Best for:**
- Writing unit tests
- Writing integration tests
- Debugging failing tests
- Code quality reviews
- Performance testing

**Key Patterns:**
- Pytest fixtures and parametrization
- Mocking external dependencies
- Code coverage measurement
- Linting and type checking

---

## Combination Examples

### Complete Scraper Development
```
First, use data-engineering skill: Design a new scraper for [source]
Then, use testing-qa skill: Write unit and integration tests
Then, use integration-orchestration skill: Connect to the main pipeline
```

### Feature Development
```
First, use analysis-insights skill: Analyze [phenomenon]
Then, use model-development skill: Engineer features for [target]
Then, use testing-qa skill: Validate features with tests
```

### Pipeline Debugging
```
First, use integration-orchestration skill: Trace the data flow
Then, use analysis-insights skill: Diagnose where it breaks
Then, use testing-qa skill: Add tests to prevent regression
```

## Quick Reference

| Skill | Primary Tech | Key Files |
|-------|-------------|-----------|
| Data Engineering | Python, APIs, SQL | `src/data/scrapers/`, `src/data/models.py` |
| Model Development | CatBoost, DuckDB, Pandas | `src/features/`, `src/models/`, `models/trained/` |
| Analysis & Insights | Pandas, Scipy, Matplotlib | `data/racing.duckdb`, `reports/`, `docs/` |
| Integration & Orchestration | Python, Dataflow Design | `src/`, `ARCHITECTURE.md` |
| Testing & QA | Pytest, Coverage Tools | `tests/`, `test_*.py` |

## Notes

- Skills are cumulative: use multiple skills in combination for complex tasks
- Always read the skill document before starting work
- Each skill includes success criteria to know when you're done
- Refer back to project docs (ARCHITECTURE.md, README.md) for context
- Skills provide patterns and practices; adapt them to your specific needs
