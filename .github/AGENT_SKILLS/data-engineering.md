# Agent Skill: Data Engineering

## Purpose

Handle data pipeline tasks: scraping, validation, transformation, and storage.

## When to Use

- "Use data-engineering skill: Create a new scraper for..."
- "Use data-engineering skill: Add data validation for..."
- "Use data-engineering skill: Refactor the data pipeline..."

## Typical Workflow

1. **Analysis Phase**
   - Examine existing scrapers in `src/data/scrapers/`
   - Check data models in `src/data/models.py`
   - Review `ARCHITECTURE.md` for pipeline design

2. **Implementation**
   - Use GraphQL when available (Racing.com), fallback to Selenium
   - Follow error handling patterns from `racing_com_graphql.py`
   - Add rate limiting to respect API limits
   - Include comprehensive logging

3. **Testing**
   - Create test file following `test_*.py` pattern
   - Test with live data when possible
   - Validate data completeness metrics
   - Check for edge cases (missing fields, API changes)

4. **Integration**
   - Update `src/data/scrapers/__init__.py` with exports
   - Document API keys and endpoints securely
   - Add to `requirements.txt` if new dependencies
   - Update README with usage examples

## Code Patterns to Follow

```python
# Rate limiting
import time
time.sleep(0.5)  # Be polite to APIs

# Error handling
try:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"API request failed: {e}")
    raise

# Logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Processing {venue} on {date}")
```

## Key Files

- `src/data/scrapers/racing_com_graphql.py` - Production scraper reference
- `src/data/models.py` - Data model definitions
- `test_racing_graphql.py` - Test suite reference
- `ARCHITECTURE.md` - Pipeline design

## Common Tasks

### Add a New Scraper

- [ ] Create `src/data/scrapers/new_scraper.py`
- [ ] Implement error handling and rate limiting
- [ ] Create `test_new_scraper.py`
- [ ] Update `__init__.py` exports
- [ ] Document in README

### Validate Data Quality

- [ ] Check for missing fields
- [ ] Verify data types
- [ ] Test edge cases (empty results, API errors)
- [ ] Document completeness percentage

### Update Data Models

- [ ] Modify `src/data/models.py`
- [ ] Update scrapers to match new schema
- [ ] Add migration notes in ARCHITECTURE.md
- [ ] Update tests

## Success Criteria

- ✅ Scraper handles all documented APIs
- ✅ Error handling with graceful fallbacks
- ✅ Data validation tests pass
- ✅ Code follows project patterns
- ✅ Rate limiting respects API terms
- ✅ Logging shows data flow clearly
