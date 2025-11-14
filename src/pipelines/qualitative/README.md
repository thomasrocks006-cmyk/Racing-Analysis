# Qualitative Analysis Pipeline

This directory contains the qualitative analysis pipeline for racing predictions, implementing the multi-stage approach defined in the taxonomy.

## Overview

The qualitative pipeline analyzes non-numerical factors that influence race outcomes, such as expert commentary, media intelligence, track conditions, and contextual information. It operates in three stages:

1. **Stage 1: Source Planning** - Identify and prioritize information sources
2. **Stage 2: Content Extraction** - Extract content from identified sources
3. **Stage 3: Synthesis** - Synthesize extracted content into structured insights

## Stage 1: Source Planning Agent

The Source Planning Agent uses Google Gemini API to intelligently identify and prioritize 15-25 information sources for each race, covering Categories 1-17 from the taxonomy.

### Quick Start

```python
from src.pipelines.qualitative.stage1_source_planner import SourcePlanningAgent

# Initialize agent (requires GOOGLE_API_KEY environment variable)
agent = SourcePlanningAgent()

# Create race context
race_context = {
    "race_id": "FLE-2025-11-14-R1",
    "race_name": "Group 1 Champions Sprint",
    "venue": "FLE",
    "venue_name": "Flemington",
    "distance": 1200,
    "race_type": "Group 1",
    "track_condition": "Good 4",
    "field_size": 12,
    "prize_money": 1000000,
    "runners": [
        {
            "horse_name": "Nature Strip",
            "barrier": 5,
            "jockey_name": "J. McDonald",
            "trainer_name": "C. Waller",
            "odds": 2.50,
        },
        # ... more runners
    ],
    "market_context": {
        "favourite_odds": 2.50,
    },
}

# Get source recommendations
plan = agent.plan_sources(race_context)

# Access results
print(f"Total sources: {plan.total_sources}")
print(f"High priority sources: {len(plan.high_priority_sources)}")

for source in plan.sources:
    print(f"- {source.source_type} (relevance: {source.relevance_score:.2f})")
```

### Using with Pydantic Models

```python
from src.data.models import Race, Run, Horse, Jockey, Trainer, MarketOdds
from src.pipelines.qualitative.stage1_source_planner import (
    create_race_context_from_models
)

# Create models (from database or scrapers)
race = Race(...)
runs = [Run(...), ...]
horses = [Horse(...), ...]
jockeys = [Jockey(...), ...]
trainers = [Trainer(...), ...]
odds = [MarketOdds(...), ...]

# Convert to race context
race_context = create_race_context_from_models(
    race=race,
    runs=runs,
    horses=horses,
    jockeys=jockeys,
    trainers=trainers,
    market_odds=odds,
)

# Plan sources
plan = agent.plan_sources(race_context)
```

### Category Mapping

The Source Planning Agent maps to these taxonomy categories:

- **Category 1**: Race Metadata (distance, venue, date)
- **Category 2**: Field Composition (number of runners, quality)
- **Category 3**: Track Conditions (going, weather, rail)
- **Category 4**: Barrier Draw (post position effects)
- **Category 5**: Jockey (rider skill, form, venue performance)
- **Category 6**: Trainer (trainer skill, stable form)
- **Category 7**: Weight Carried (handicap allocation)
- **Category 8**: Market Movements (betting patterns, steam)
- **Category 9**: Odds & Probability (market-implied odds)
- **Category 10**: Expert Commentary (tips, analysis)
- **Category 11**: Media Intelligence (news, stable reports)
- **Category 12**: Gear Changes (blinkers, tongue tie, etc.)
- **Category 13**: Barrier Trials (recent jumpouts)
- **Category 14**: Stewards Reports (incidents, penalties)
- **Category 15**: Breeding/Pedigree (sire/dam analysis)
- **Category 16**: Track Bias (rail position advantage)
- **Category 17**: Race Pace Scenario (predicted tempo)

### Source Types

Examples of source types recommended by the agent:

- `racing.com_race_card` - Complete race metadata
- `betfair_market_moves` - Live market movements
- `racing.com_jockey_stats` - Jockey performance data
- `racing.com_trainer_stats` - Trainer performance data
- `racing.com_expert_tips` - Expert analysis and tips
- `racing.com_gear_changes` - Equipment changes
- `racing.com_barrier_trials` - Recent trial performances
- `racing_victoria_stewards` - Stewards reports
- `punters.com_track_bias` - Track bias analysis
- `punters.com_pace_map` - Race pace predictions

### Relevance Scoring

Each source receives a relevance score from 0.0 to 1.0:

- **1.0**: Critical source (e.g., race metadata)
- **0.9-0.95**: Very high priority (e.g., odds, market moves)
- **0.8-0.89**: High priority (e.g., jockey/trainer stats)
- **0.7-0.79**: Important (e.g., gear changes, trials)
- **0.6-0.69**: Valuable (e.g., pedigree, pace maps)
- **< 0.6**: Supplementary information

### Configuration

The agent can be configured with different Gemini models:

```python
# Default: Gemini 1.5 Pro
agent = SourcePlanningAgent(model_name="gemini-1.5-pro")

# Or use a different model
agent = SourcePlanningAgent(model_name="gemini-1.5-flash")
```

### Error Handling

The agent includes fallback mechanisms:

1. If Gemini returns fewer than 15 sources, default sources are added
2. Invalid sources (wrong category, relevance out of range) are filtered
3. Maximum of 25 sources to prevent information overload

### Testing

Run the test suite:

```bash
# Run all tests
pytest tests/unit/test_stage1_source_planner.py -v

# Run specific scenario
pytest tests/unit/test_stage1_source_planner.py::test_scenario_1_group1_race -v

# Run with coverage
pytest tests/unit/test_stage1_source_planner.py --cov=src/pipelines/qualitative
```

### Examples

See `examples/example_source_planner.py` for complete working examples:

```bash
# Set your API key
export GOOGLE_API_KEY='your-api-key-here'

# Run examples
python examples/example_source_planner.py
```

## Stage 2 & 3 (Coming Soon)

- **Stage 2: Content Extraction** - Extract and structure content from planned sources
- **Stage 3: Synthesis** - Synthesize extracted content using GPT-4/Claude

## Performance Targets

- **Source Discovery Accuracy**: 90%+ (validated in tests)
- **Source Count**: 15-25 per race
- **Processing Time**: < 5 seconds per race
- **Coverage**: All 17 qualitative categories

## Architecture

```
qualitative/
├── __init__.py
├── stage1_source_planner.py     # Source planning agent
├── stage2_content_extractor.py  # Content extraction (coming soon)
└── stage3_synthesis.py          # Content synthesis (coming soon)
```

## Dependencies

- `google-generativeai>=0.8.0` - Gemini API integration
- `pydantic>=2.4.0` - Data validation
- `python-dotenv>=1.0.0` - Environment configuration

## Environment Variables

Required:
- `GOOGLE_API_KEY` - Google API key for Gemini access

## License

MIT
