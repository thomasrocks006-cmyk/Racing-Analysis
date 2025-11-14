# Agent Skills Architecture & Design

## Overview

You asked: "Do you think we should set up specialized agent skills like Claude skills for different tasks?"

**Yes, absolutely.** I've already set this up, and here's the architecture and rationale:

## Current Architecture

### 5 Specialized Skills

Each skill focuses on a specific domain with its own patterns, tools, and success criteria:

```
Agent Skills System
├── Data Engineering (scrapers, validation, ETL)
├── Model Development (features, training, optimization)
├── Analysis & Insights (EDA, stats, reporting)
├── Integration & Orchestration (pipelines, data flow)
└── Testing & QA (tests, code quality, performance)
```

### Design Principles

1. **Separation of Concerns**: Each skill has distinct tools, patterns, and workflows
2. **Reusable Patterns**: Code examples show the "right way" to do things in each domain
3. **Task-Specific Checklists**: Each skill has concrete steps, not vague guidance
4. **Success Criteria**: Clear metrics for knowing when you're done
5. **Composability**: Skills work together for complex projects

## Why This Design Works

### ✅ The Agent Becomes Domain-Aware

Without skills:

```
Agent: "I'll help you create a scraper... now a model... now a test..."
→ Generic advice, inconsistent patterns, may miss domain-specific best practices
```

With skills:

```
Agent: [loads data-engineering skill] "I'll create a scraper following these patterns..."
→ Consistent with your project's scraper architecture
→ Includes proper error handling, rate limiting, logging
→ References your existing RacingComGraphQLScraper as a template
```

### ✅ Prevents Context Switching Cost

Data engineers need to think about:

- API design, rate limits, error recovery
- Data validation, completeness metrics
- Scraper testability and reproducibility

ML engineers need to think about:

- Feature interactions, data leakage
- Train/val/test splits, cross-validation
- Hyperparameter search, evaluation metrics

When you reference the right skill, the agent focuses on the right things.

### ✅ Scales With Your Project

As your project grows:

- Add new skills for emerging patterns (e.g., "Betfair Integration", "Qualitative Analysis")
- Update existing skills when you discover better patterns
- Skills become institutional knowledge for your team

## How Skills Map to Your Project

### Data Engineering Skill

**Aligns with:**

- `src/data/scrapers/` - Existing scrapers you want to follow
- `src/data/models.py` - Data model definitions
- `ARCHITECTURE.md` - Pipeline design

**Example:** When you say "Use data-engineering skill: Create a Betfair odds scraper", the agent:

1. Loads the data-engineering skill
2. Reviews `racing_com_graphql.py` as a template
3. Follows the same error handling, logging, rate limiting patterns
4. Creates tests following your existing test structure
5. Returns code that fits naturally into your codebase

### Model Development Skill

**Aligns with:**

- `src/features/` - Feature engineering patterns
- `src/models/` - Model training patterns
- CatBoost configs in your project
- Your existing evaluation practices

**Example:** "Use model-development skill: Engineer features for win prediction"

1. Agent reviews your feature structure
2. Uses DuckDB queries like existing features
3. Tests features with your validation patterns
4. Returns code that integrates with existing model pipeline

### Analysis & Insights Skill

**Aligns with:**

- Your DuckDB data warehouse setup
- Matplotlib/Seaborn visualization style
- Documentation standards in `docs/`
- Report structure you prefer

### Integration & Orchestration Skill

**Aligns with:**

- `ARCHITECTURE.md` - Your pipeline design
- Error handling patterns in your codebase
- Logging and monitoring setup
- Existing orchestration code

### Testing & QA Skill

**Aligns with:**

- `tests/` directory structure
- Pytest configuration in `pyproject.toml`
- Test patterns in `test_*.py` files
- Coverage standards you follow

## Extending the Skills System

### Add a New Skill

If you discover a pattern that crops up repeatedly (e.g., "Betfair API Integration"), create a new skill:

```
.github/AGENT_SKILLS/
├── betfair-integration.md      # NEW: Betfair-specific patterns
├── data-engineering.md
├── model-development.md
└── ...
```

**Template for new skill:**

```markdown
# Agent Skill: [Name]

## Purpose
[What this skill handles]

## When to Use
- "Use [skill] skill: ..."
- Example tasks

## Typical Workflow
1. [Step]
2. [Step]
3. [Step]

## Code Patterns to Follow
[Code examples]

## Key Files
[Relevant files in your project]

## Common Tasks
[Checklists]

## Success Criteria
- ✅ [Metric 1]
- ✅ [Metric 2]
```

### Evolve Existing Skills

As you discover better patterns, update the skills:

```bash
# Example: Update data-engineering skill with new best practice
Edit .github/AGENT_SKILLS/data-engineering.md
Add new pattern to "Code Patterns to Follow"
Commit with message "Improve data-engineering skill with new pattern"
```

Next time you use the skill, the agent will follow the updated pattern.

## Advanced: Multi-Skill Workflows

### Example: Build New ML Feature

```
Start:
"First, use analysis-insights skill: Analyze gear change impact on race outcome"

Then:
"Use model-development skill: Engineer gear change features for prediction"

Then:
"Use testing-qa skill: Write tests for gear change features"

Then:
"Use integration-orchestration skill: Add gear features to main prediction pipeline"

Finally:
"Use analysis-insights skill: Generate report on model improvement from new features"
```

Each skill brings its expertise to the appropriate phase:

1. **Analysis** - Understand the phenomenon
2. **Model Dev** - Build features
3. **Testing** - Validate quality
4. **Integration** - Connect to pipeline
5. **Analysis** - Measure impact

## Comparison: With vs Without Skills

### Without Skills

```
You: "Create a new scraper for Betfair"
Agent: [Generic Python scraper code]
Problem: Might not follow your patterns, miss error handling, skip tests
```

### With Skills

```
You: "Use data-engineering skill: Create scraper for Betfair live odds API"
Agent: [Reads data-engineering skill]
Agent: [Follows your existing scraper patterns]
Agent: [Includes error handling, rate limiting, tests]
Agent: [Returns code that integrates seamlessly]
```

## Benefits Summary

| Aspect | Without Skills | With Skills |
|--------|---|---|
| Code Consistency | Variable | Consistent across project |
| Error Handling | Sometimes forgotten | Always included |
| Testing | Optional | Built into workflow |
| Documentation | Generic | Domain-specific and relevant |
| Performance | Variable | Follows best practices |
| Integration Time | High (need to refactor) | Low (fits existing patterns) |
| Knowledge Preservation | Lost | Documented in skills |

## Future Enhancements

### 1. Skill Versions

```
.github/AGENT_SKILLS/data-engineering.md@v1.0
.github/AGENT_SKILLS/data-engineering.md@v1.1  # Improved pattern
```

### 2. Skill Dependencies

```
"model-development skill requires data-engineering skill"
→ Agent loads both in correct order
```

### 3. Skill Combinations

```
"data+model skill: Create scraper AND train model on scraped data"
→ Agent coordinates between skills
```

### 4. Skill Templates

```
.github/AGENT_SKILLS/_TEMPLATE.md
→ For adding new skills quickly
```

## Getting Maximum Value

### ✅ Do This

1. **Keep skills updated** - When you find a better pattern, update the skill
2. **Use skills consistently** - Always reference the skill for the task type
3. **Review agent output** - Check that agent followed skill guidance
4. **Document patterns** - Add patterns to skills that work well in your project
5. **Combine skills** - Use multiple skills for complex workflows

### ❌ Avoid This

1. **Asking outside skills** - Asking the agent for a scraper without the data-engineering skill context
2. **Ignoring skill guidance** - Getting agent output that doesn't match skill patterns
3. **Letting skills drift** - Skills becoming outdated as your project evolves
4. **Creating redundant skills** - Having overlap between different skills
5. **Being too rigid** - Skills are guides, not absolute laws

## Conclusion

The 5-skill system I've created is:

✅ **Ready to use immediately** - Just reference them in your chat
✅ **Aligned with your project** - Based on your existing patterns
✅ **Extensible** - Easy to add new skills or evolve existing ones
✅ **Composable** - Skills work together for complex projects
✅ **Documented** - Full guidance in each skill file

**Start using them today by referencing skills when you have tasks:**

```
Use [skill-name] skill: [your task]
```

The agent will load the appropriate skill, follow your project's patterns, and produce consistent, high-quality code.
