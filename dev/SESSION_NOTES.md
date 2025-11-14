# Session Notes & Agent TODO

## Current Goal
Improve Racing-Analysis ML pipeline with specialized agent skills and optimized data processing.

## Active Sprint
- [ ] Set up GitHub Copilot operating instructions
- [ ] Create specialized agent skill files for different tasks
- [ ] Establish session notes tracking system
- [ ] Document agent skill workflows

## Decisions Made
- Using `.github/COPILOT_INSTRUCTIONS.md` as the persistent operating manual
- Using `dev/SESSION_NOTES.md` as the session brain file
- Organizing agent skills by domain: data, models, analysis, orchestration

## Completed Tasks
- ✅ Fixed git branch issue (main is clean and ready for PRs)
- ✅ GraphQL scraper implementation and tests

## Next Steps
1. Create specialized agent skill files for different tasks
2. Document each skill's purpose and usage
3. Link skills to the main COPILOT_INSTRUCTIONS.md
4. Test agent behavior with structured prompts

## Design Constraints
- Must follow existing Racing.com GraphQL scraper patterns
- Keep scrapers production-ready with error handling
- Maintain data models in `src/data/models.py`
- All changes should be tested before merge to main

## Repository Quick Stats
- Main modules: `src/data/`, `src/models/`, `src/analysis/`
- Tests: `tests/`, root-level `test_*.py` files
- Scrapers: `src/data/scrapers/` (racing_com_graphql.py, racing_com_selenium.py, etc.)
- Configuration: `configs/`, `pyproject.toml`, `requirements.txt`
