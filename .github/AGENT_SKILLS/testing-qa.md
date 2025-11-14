# Agent Skill: Testing & Quality Assurance

## Purpose

Handle testing, validation, and quality assurance tasks: unit tests, integration tests, performance testing, and code quality.

## When to Use

- "Use testing-qa skill: Write tests for..."
- "Use testing-qa skill: Debug failing test..."
- "Use testing-qa skill: Add integration tests..."
- "Use testing-qa skill: Review code quality..."
- "Use testing-qa skill: Performance test..."

## Typical Workflow

1. **Test Planning**
   - Identify what needs testing
   - Review existing tests in `tests/`
   - Determine test types needed (unit, integration, E2E)
   - Define success criteria

2. **Test Implementation**
   - Write clear, focused tests
   - Use fixtures for setup/teardown
   - Test both happy path and edge cases
   - Include parametrized tests for variations

3. **Running Tests**
   - Execute tests locally first
   - Verify coverage meets standards
   - Run integration tests with real data
   - Check for flaky or slow tests

4. **Code Quality**
   - Run linters (pylint, flake8)
   - Check type hints and mypy
   - Review code for maintainability
   - Identify technical debt

5. **Reporting**
   - Document test results
   - Identify gaps in coverage
   - Suggest improvements
   - Track metrics over time

## Code Patterns to Follow

```python
# Unit test template
import pytest
from src.data.scrapers.racing_com_graphql import RacingComGraphQLScraper

@pytest.fixture
def scraper():
    """Fixture for scraper instance."""
    return RacingComGraphQLScraper()

def test_parse_distance(scraper):
    """Test distance parsing."""
    assert scraper._parse_distance("1200m") == 1200
    assert scraper._parse_distance(1200) == 1200
    assert scraper._parse_distance(None) is None
    assert scraper._parse_distance("invalid") is None

# Integration test
@pytest.mark.integration
def test_scrape_race_end_to_end():
    """Test complete race scraping workflow."""
    scraper = RacingComGraphQLScraper()
    race_card = scraper.scrape_race("flemington", "2025-11-14", 1)

    assert race_card.race.race_id is not None
    assert len(race_card.runs) > 0
    assert race_card.validate_completeness() > 0

# Parametrized test
@pytest.mark.parametrize("input,expected", [
    ("GELDING", SexType.GELDING),
    ("MARE", SexType.MARE),
    ("HORSE", SexType.STALLION),
    ("UNKNOWN", None),
])
def test_parse_sex(scraper, input, expected):
    """Test sex type parsing with variations."""
    assert scraper._parse_gear_type(input) == expected
```

## Key Files

- `tests/` - Test directory with organized test modules
- `test_*.py` - Root-level integration tests
- `pyproject.toml` - Test configuration (pytest settings)
- `.github/workflows/` - CI/CD test pipeline (if exists)
- `requirements.txt` - Test dependencies (pytest, etc.)

## Common Tasks

### Write Unit Tests

- [ ] Test single function/method in isolation
- [ ] Mock external dependencies (APIs, databases)
- [ ] Test normal, boundary, and error cases
- [ ] Use fixtures for repeated setup
- [ ] Aim for >80% line coverage

### Write Integration Tests

- [ ] Test multiple components working together
- [ ] Use real data when possible (or fixtures)
- [ ] Test end-to-end workflows
- [ ] Include error scenarios
- [ ] Mark with `@pytest.mark.integration`

### Debug Failing Test

- [ ] Run test with verbose output (`-vv` flag)
- [ ] Add print statements or debugger breakpoints
- [ ] Isolate the issue with minimal test case
- [ ] Check for flakiness (run multiple times)
- [ ] Review recent changes that might have broken it

### Code Quality Review

- [ ] Run linters: `pylint src/`, `flake8 src/`
- [ ] Check types: `mypy src/`
- [ ] Check coverage: `coverage run -m pytest && coverage report`
- [ ] Review for common issues (unused imports, long functions, etc.)
- [ ] Suggest improvements with rationale

### Performance Testing

- [ ] Measure execution time of critical paths
- [ ] Profile memory usage
- [ ] Test with realistic data volumes
- [ ] Identify bottlenecks
- [ ] Document performance benchmarks

## Success Criteria

- ✅ All tests pass consistently (no flakiness)
- ✅ Coverage is >80% for critical paths
- ✅ Tests are fast (<5s per test, <30s total)
- ✅ Code passes linters and type checks
- ✅ Edge cases are covered
- ✅ Test code is clear and maintainable
- ✅ Integration tests verify real workflows
