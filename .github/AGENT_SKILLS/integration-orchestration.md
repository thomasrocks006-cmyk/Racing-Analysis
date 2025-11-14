# Agent Skill: Integration & Orchestration

## Purpose

Handle system integration tasks: pipeline orchestration, API integration, data flow coordination, and cross-module communication.

## When to Use

- "Use integration-orchestration skill: Connect the..."
- "Use integration-orchestration skill: Build pipeline for..."
- "Use integration-orchestration skill: Integrate API..."
- "Use integration-orchestration skill: Fix data flow issue..."

## Typical Workflow

1. **Design Phase**
   - Review `ARCHITECTURE.md` and `END_TO_END_SYSTEM_OVERVIEW.md`
   - Identify data flow and dependencies
   - Check existing orchestration in `src/`
   - Plan module interfaces

2. **Integration**
   - Connect data sources (scrapers)
   - Route data through feature engineering
   - Feed into model inference
   - Output results to appropriate storage

3. **Error Handling**
   - Implement retry logic with exponential backoff
   - Handle partial failures gracefully
   - Log all critical transitions
   - Create fallback mechanisms

4. **Testing**
   - Test end-to-end workflows
   - Verify data consistency across modules
   - Check error recovery
   - Monitor performance and latency

5. **Documentation**
   - Document data flow diagrams
   - Explain module dependencies
   - Create runbooks for common tasks
   - Update architecture documentation

## Code Patterns to Follow

```python
# Pipeline orchestration
from src.data.scrapers.racing_com_graphql import RacingComGraphQLScraper
from src.features.builder import FeatureBuilder
from src.models.predictor import ModelPredictor

class RacingPipeline:
    def __init__(self):
        self.scraper = RacingComGraphQLScraper()
        self.features = FeatureBuilder()
        self.model = ModelPredictor()

    def process_race(self, venue, date, race_num):
        """End-to-end race processing."""
        try:
            # Step 1: Scrape
            race_card = self.scraper.scrape_race(venue, date, race_num)
            logger.info(f"Scraped {race_card.race.race_id}")

            # Step 2: Feature engineering
            features = self.features.build(race_card)
            logger.info(f"Generated {len(features)} features")

            # Step 3: Predict
            predictions = self.model.predict(features)
            logger.info(f"Generated predictions for {len(predictions)} runners")

            return predictions
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise

# Error handling with retry
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_race_data_with_retry(venue, date, race_num):
    return scraper.scrape_race(venue, date, race_num)
```

## Key Files

- `src/` - Main application modules
- `ARCHITECTURE.md` - System design and data flow
- `END_TO_END_SYSTEM_OVERVIEW.md` - Complete pipeline overview
- `docs/setup/` - Setup and configuration
- `configs/` - Configuration files
- `Makefile` - Common tasks and workflows

## Common Tasks

### Create Data Pipeline

- [ ] Define data sources and destinations
- [ ] Implement each stage with error handling
- [ ] Add logging at critical points
- [ ] Test with sample data
- [ ] Document data contracts between modules

### Integrate New API

- [ ] Add API client wrapper in appropriate scraper
- [ ] Implement rate limiting
- [ ] Add error handling for common failures
- [ ] Create integration tests
- [ ] Update pipeline to use new data

### Fix Data Flow Issue

- [ ] Trace data through pipeline stages
- [ ] Identify bottleneck or failure point
- [ ] Review logs for error patterns
- [ ] Implement fix with tests
- [ ] Document root cause and prevention

### Orchestrate Batch Job

- [ ] Define job parameters (dates, venues, etc.)
- [ ] Implement parallel processing where possible
- [ ] Add progress tracking and checkpointing
- [ ] Create failure recovery mechanism
- [ ] Log job completion and metrics

## Success Criteria

- ✅ Data flows smoothly through all pipeline stages
- ✅ Errors are caught and handled gracefully
- ✅ System recovers from transient failures automatically
- ✅ Performance meets requirements (latency, throughput)
- ✅ Logs provide clear visibility into data flow
- ✅ Integration points are well-documented
- ✅ Cross-module dependencies are minimized
