# Agent Skill: Architecture & System Design

## Purpose

Design, evaluate, and refactor system architecture: making strategic trade-offs, ensuring scalability, maintaining coherence across components, and documenting decisions for long-term maintainability.

## When to Use

- "Use architecture-design skill: Design the scraper architecture"
- "Use architecture-design skill: Evaluate alternative architectures"
- "Use architecture-design skill: Refactor for scalability"
- "Use architecture-design skill: Review system coherence"
- "Use architecture-design skill: Design for resilience"

## Typical Workflow

1. **Understand Requirements**
   - Functional requirements (what must it do?)
   - Non-functional requirements (how must it perform?)
   - Constraints (time, budget, technology, team)
   - Scale requirements (data volume, throughput, users)

2. **Identify Key Design Decisions**
   - Layering and separation of concerns
   - Data flow and integration points
   - Error handling and resilience strategy
   - Scalability approach (horizontal vs. vertical)
   - Technology choices and trade-offs

3. **Generate Architecture Options**
   - Option A: Simple monolithic approach
   - Option B: Modular with clear separation
   - Option C: Distributed/microservices (if justified)
   - Option D: Novel approach for specific constraints

4. **Evaluate Trade-offs**
   - Simplicity vs. flexibility
   - Performance vs. maintainability
   - Consistency vs. availability
   - Cost vs. capability
   - Time-to-market vs. long-term scalability

5. **Select & Document**
   - Choose architecture with rationale
   - Document key decisions
   - Identify risks and mitigation
   - Plan implementation phases
   - Establish evolution strategy

## Architecture Design Patterns

### Layered Architecture

```
┌─────────────────────────────────────┐
│      Presentation/API Layer         │
├─────────────────────────────────────┤
│      Business Logic Layer           │
├─────────────────────────────────────┤
│      Data Access Layer              │
├─────────────────────────────────────┤
│      Database Layer                 │
└─────────────────────────────────────┘
```

**Pros:** Easy to understand, organize, test
**Cons:** Can become monolithic, not ideal for distribution

### Modular Monolith

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Scraper     │  │  Features    │  │  Models      │
│  Module      │  │  Module      │  │  Module      │
└──────────────┘  └──────────────┘  └──────────────┘
       ↓                ↓                   ↓
┌─────────────────────────────────────────────────┐
│         Shared Infrastructure                   │
│    (Logging, Error Handling, Database)          │
└─────────────────────────────────────────────────┘
```

**Pros:** Clear module boundaries, testable, can become distributed
**Cons:** Shared infrastructure can become bottleneck

### Event-Driven Architecture

```
┌──────────────┐
│  Scraper     │─┐
│  Service     │ │  Event:
└──────────────┘ │  race_scraped
                 ├→ Event Bus →┬→ Feature Extraction
                 │             ├→ Model Prediction
                 │             └→ Database Storage
┌──────────────┐ │
│  Betfair     │─┘
│  Service     │
└──────────────┘
```

**Pros:** Loose coupling, scalable, reactive
**Cons:** Complex, hard to debug, eventual consistency

## Architecture Decision Record (ADR) Template

```markdown
# ADR-001: Use GraphQL API over HTML Scraping

## Status
Accepted

## Context
Racing.com offers both GraphQL API and HTML pages. We need reliable data access.

## Decision
Use GraphQL API as primary data source.

## Consequences

### Positive
- Structured, versioned data
- Less brittle than CSS selectors
- Better error semantics
- Faster than full page download

### Negative
- Dependency on Racing.com API stability
- Need to handle API changes
- Rate limiting constraints

## Alternatives Considered
- HTML scraping (rejected: too fragile)
- Custom API wrapper (rejected: too much effort)

## Implementation Plan
1. Build GraphQL scraper module
2. Implement error handling and retries
3. Add comprehensive tests
4. Monitor for API changes
```

## Code Patterns for Architectural Integrity

```python
# Clear module boundaries
from src.data.scrapers import RacingComGraphQLScraper
from src.features.builder import FeatureBuilder
from src.models.predictor import ModelPredictor

class RacingAnalysisPipeline:
    """Orchestrate data flow across modules."""

    def __init__(self):
        self.scraper = RacingComGraphQLScraper()
        self.feature_builder = FeatureBuilder()
        self.predictor = ModelPredictor()

    def process_race(self, venue, date, race_num):
        """End-to-end processing with clear separation."""
        # Layer 1: Data ingestion
        race_card = self.scraper.scrape_race(venue, date, race_num)

        # Layer 2: Feature engineering
        features = self.feature_builder.build(race_card)

        # Layer 3: Prediction
        predictions = self.predictor.predict(features)

        # Layer 4: Results
        return predictions

# Dependency injection for testability
class RacingPipeline:
    def __init__(self, scraper, feature_builder, predictor):
        self.scraper = scraper
        self.feature_builder = feature_builder
        self.predictor = predictor

    # Allows injecting mocks for testing

# Interface/protocol definition
from typing import Protocol

class DataScraper(Protocol):
    """Contract for any scraper."""
    def scrape_race(self, venue: str, date: str, race_num: int) -> RaceCard:
        ...

# This allows multiple implementations (GraphQL, Selenium, etc.)
# without coupling to specific scraper

# Error handling at boundaries
class ScrapeError(Exception):
    """Scraper-specific errors."""
    pass

class FeatureError(Exception):
    """Feature engineering errors."""
    pass

class PredictionError(Exception):
    """Prediction errors."""
    pass

# Clear error propagation across boundaries
try:
    race_card = self.scraper.scrape_race(...)
except ScrapeError as e:
    # Handle scraper failure
    raise PipelineError(f"Scraping failed: {e}")
```

## Architecture Decision Matrix

| Decision | Option A | Option B | Option C |
|----------|----------|----------|----------|
| **Data Source** | GraphQL | HTML Scraping | API Wrapper |
| **Complexity** | Medium | Low | High |
| **Reliability** | High | Low | High |
| **Maintainability** | High | Low | Medium |
| **Speed** | Medium | Low | High |
| **Risk** | API change | Fragile | Extra layer |

## Key Architectural Principles for Racing-Analysis

### Separation of Concerns

- Scraping module: Only handles data fetching
- Feature module: Only builds features
- Model module: Only predictions
- Clear interfaces between modules

### Dependency Direction

```
Scraper → Features → Models → Results
   ↑        ↑         ↑
   └────────┴─────────┴── Shared Infrastructure (logging, errors, db)
```

Lower layers don't know about higher layers.

### Testability

- Each module testable independently
- Dependency injection for testing
- Clear contracts (protocols/interfaces)
- Mock-friendly design

### Scalability

- Identify bottlenecks early
- Design with parallelization in mind
- Use async/await where appropriate
- Plan for horizontal scaling

### Resilience

- Handle failures gracefully
- Implement retries with backoff
- Log and monitor errors
- Fail fast with clear errors

## Common Architectural Tasks

### Design New Component

- [ ] Clarify requirements and constraints
- [ ] Identify integration points
- [ ] Define module boundaries
- [ ] Design interfaces/protocols
- [ ] Document decisions
- [ ] Prototype key interactions

### Evaluate Architecture Alternative

- [ ] List criteria (simplicity, performance, scalability, etc.)
- [ ] Score each alternative
- [ ] Compare trade-offs
- [ ] Identify risks
- [ ] Make recommendation

### Refactor for Scalability

- [ ] Profile current system bottleneck
- [ ] Design scalable alternative
- [ ] Plan migration strategy
- [ ] Implement incrementally
- [ ] Verify improvements

### Review System Coherence

- [ ] Map data flow
- [ ] Identify tight coupling
- [ ] Check for consistency
- [ ] Review error handling
- [ ] Document findings

## Success Criteria

- ✅ Architecture aligns with requirements
- ✅ Clear separation of concerns
- ✅ Interfaces are well-defined
- ✅ Design decisions documented
- ✅ Trade-offs explicitly considered
- ✅ Scalability assessed
- ✅ Error handling strategy clear
- ✅ Team understands and agrees on design
