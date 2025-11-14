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

## Core Skills (Original 5)

### 📊 [Data Engineering](./data-engineering.md)

Handle data pipeline tasks: scraping, validation, transformation, and storage.

**Best for:**

- Creating new data scrapers
- Adding data validation
- Refactoring pipelines
- Integrating new data sources
- Fixing data quality issues

---

### 🤖 [Model Development](./model-development.md)

Handle machine learning tasks: feature engineering, model training, evaluation, and optimization.

**Best for:**

- Feature engineering
- Model training with CatBoost
- Hyperparameter optimization
- Performance evaluation
- Model comparison and selection

---

### 📈 [Analysis & Insights](./analysis-insights.md)

Handle analytical tasks: exploratory data analysis, hypothesis testing, reporting, and insights.

**Best for:**

- Exploratory data analysis
- Statistical testing
- Visualization creation
- Report generation
- Hypothesis validation

---

### 🔗 [Integration & Orchestration](./integration-orchestration.md)

Handle system integration: pipeline orchestration, API integration, data flow coordination.

**Best for:**

- Building end-to-end pipelines
- Integrating new APIs
- Fixing data flow issues
- Orchestrating batch jobs
- Error handling and recovery

---

### ✅ [Testing & Quality Assurance](./testing-qa.md)

Handle testing and quality assurance: unit tests, integration tests, code quality.

**Best for:**

- Writing unit tests
- Writing integration tests
- Debugging failing tests
- Code quality reviews
- Performance testing

---

## Advanced Skills (New!)

### 💡 [Creativity & Innovation](./creativity-innovation.md)

Handle creative problem-solving: brainstorming alternatives, challenging assumptions, thinking outside the box.

**Best for:**

- Brainstorming alternative architectures
- Challenging technical assumptions
- Finding novel solutions to bottlenecks
- Innovating feature design
- Breaking through design deadlocks

**Key Techniques:**

- SCAMPER method
- Cross-domain thinking
- Constraint relaxation
- Unconventional approaches

---

### 🔍 [Deep Critical Analysis](./deep-critical-analysis.md)

Handle rigorous, multi-layered critical analysis: gap analysis, assumption testing, harsh critique.

**Best for:**

- Identifying all gaps and flaws
- Testing assumptions thoroughly
- Asking tough questions
- Harsh but fair critique
- Comprehensive risk assessment

**Key Workflow:**

- Gap analysis (6+ categories)
- Assumption testing
- Critical questions
- Final comprehensive review
- Self-assessment checkpoints

---

### ⚡ [Performance & Optimization](./performance-optimization.md)

Handle system performance: profiling, bottleneck identification, optimization strategies.

**Best for:**

- Profiling slow code
- Identifying bottlenecks
- Optimizing database queries
- Reducing memory usage
- Benchmarking approaches

**Key Techniques:**

- Profiling (cProfile, memory_profiler)
- Algorithm optimization
- Caching and memoization
- Parallelization

---

### 🏗️ [Architecture & System Design](./architecture-design.md)

Handle system design: architecture patterns, design decisions, refactoring strategies.

**Best for:**

- Designing component architecture
- Evaluating design alternatives
- Refactoring for scalability
- Reviewing system coherence
- Designing for resilience

**Key Patterns:**

- Layered architecture
- Modular monolith
- Event-driven architecture
- ADR (Architecture Decision Records)

---

### 🔐 [Security & Risk Management](./security-risk-management.md)

Handle security: threat modeling, vulnerability assessment, risk mitigation.

**Best for:**

- Threat modeling components
- Identifying security vulnerabilities
- Risk assessment and prioritization
- Designing secure features
- Compliance and audit

**Key Techniques:**

- Threat modeling
- Attack surface analysis
- Risk matrix assessment
- Mitigation strategy design

---

## Advanced Skill Combinations

### System Architecture Review (Thorough)

```
First, use deep-critical-analysis skill: Ruthlessly analyze current architecture
Then, use creativity skill: Brainstorm alternative architectures
Then, use architecture-design skill: Evaluate and design new architecture
Then, use security-risk skill: Threat model new architecture
Then, use testing-qa skill: Plan testing strategy for changes
```

### Feature Engineering Innovation

```
First, use analysis-insights skill: Analyze the data and phenomenon
Then, use creativity skill: Brainstorm unconventional features
Then, use model-development skill: Engineer and test features
Then, use performance-optimization skill: Optimize for speed
Then, use deep-critical-analysis skill: Critique feature effectiveness
```

### Performance Optimization Deep Dive

```
First, use performance-optimization skill: Profile and identify bottleneck
Then, use deep-critical-analysis skill: Analyze root causes thoroughly
Then, use creativity skill: Brainstorm unconventional optimizations
Then, use architecture-design skill: Design optimized architecture
Then, use testing-qa skill: Benchmark improvements
```

### Complete Scraper Development (Advanced)

```
First, use security-risk skill: Threat model data source
Then, use architecture-design skill: Design scraper architecture
Then, use data-engineering skill: Implement scraper
Then, use testing-qa skill: Write comprehensive tests
Then, use performance-optimization skill: Optimize scraper speed
Then, use integration-orchestration skill: Connect to pipeline
```

### Critical Analysis Before Major Refactor

```
First, use deep-critical-analysis skill: Identify all gaps and risks
Then, use creativity skill: Challenge assumptions and generate alternatives
Then, use security-risk skill: Assess security implications
Then, use performance-optimization skill: Measure current performance
Then, use architecture-design skill: Design refactored system
Then, use integration-orchestration skill: Plan migration
```

## Quick Reference Table

| Skill | Category | Best For | Tech |
|-------|----------|----------|------|
| Data Engineering | Core | Scrapers, validation | Python, APIs, SQL |
| Model Development | Core | ML/features | CatBoost, DuckDB |
| Analysis & Insights | Core | EDA, statistics | Pandas, Scipy |
| Integration & Orchestration | Core | Pipelines | Python, Dataflow |
| Testing & QA | Core | Testing, quality | Pytest, Coverage |
| Creativity & Innovation | Advanced | Novel solutions | Creative thinking |
| Deep Critical Analysis | Advanced | Thorough critique | Analytical rigor |
| Performance & Optimization | Advanced | Speed, efficiency | Profiling tools |
| Architecture & System Design | Advanced | System design | Architecture patterns |
| Security & Risk Management | Advanced | Security posture | Threat modeling |

## Skill Selection Guide

**Feeling stuck or challenged?** → Use **Creativity & Innovation**

**Need a thorough review?** → Use **Deep Critical Analysis**

**Performance is sluggish?** → Use **Performance & Optimization**

**Designing new component?** → Use **Architecture & System Design**

**Concerned about security?** → Use **Security & Risk Management**

**Implementing a feature?** → Use **Data/Model/Testing skills**

**Connecting systems?** → Use **Integration & Orchestration**

## Notes

- Skills are cumulative: use multiple skills in combination for complex tasks
- Advanced skills add rigor and creativity to core tasks
- Start with core skills for basic tasks, add advanced skills for critical decisions
- Always read the skill document before starting work
- Each skill includes success criteria to know when you're done
- Refer back to project docs (ARCHITECTURE.md, README.md) for context
- Skills provide patterns and practices; adapt them to your specific needs
