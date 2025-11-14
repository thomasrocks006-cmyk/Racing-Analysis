# Agent Skill: Analysis & Insights

## Purpose

Handle analytical tasks: exploratory data analysis, hypothesis testing, reporting, and insights extraction.

## When to Use

- "Use analysis-insights skill: Analyze..."
- "Use analysis-insights skill: Generate report for..."
- "Use analysis-insights skill: Test hypothesis about..."
- "Use analysis-insights skill: Create visualization..."

## Typical Workflow

1. **Problem Definition**
   - Clarify the research question
   - Identify relevant data sources
   - Review existing analyses in `docs/`
   - Define success metrics

2. **Data Exploration**
   - Query DuckDB for raw insights
   - Identify patterns, outliers, anomalies
   - Check data quality and completeness
   - Create exploratory visualizations

3. **Analysis**
   - Perform statistical tests where appropriate
   - Compare groups or time periods
   - Calculate effect sizes and confidence intervals
   - Document assumptions and limitations

4. **Visualization**
   - Create clear, labeled charts
   - Use consistent styling
   - Include legends and annotations
   - Export to `reports/` or `docs/`

5. **Reporting**
   - Summarize findings concisely
   - Highlight actionable insights
   - Document methodology
   - Suggest follow-up analyses

## Code Patterns to Follow

```python
# Query data with DuckDB
import duckdb
import pandas as pd

conn = duckdb.connect('data/racing.duckdb')
df = conn.execute("""
    SELECT
        venue,
        COUNT(*) as race_count,
        AVG(field_size) as avg_field_size
    FROM races
    GROUP BY venue
    ORDER BY race_count DESC
""").df()

# Statistical analysis
from scipy import stats
t_stat, p_value = stats.ttest_ind(group1, group2)
print(f"t-statistic: {t_stat:.3f}, p-value: {p_value:.4f}")

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='venue', y='odds')
plt.title('Odds Distribution by Venue')
plt.savefig('reports/odds_by_venue.png', dpi=300, bbox_inches='tight')
```

## Key Files

- `data/racing.duckdb` - Main data warehouse
- `docs/qualitative-pipeline/` - Analysis documentation
- `reports/` - Output reports and visualizations
- `docs/COMPREHENSIVE_TAXONOMY_MASTER/` - Domain knowledge
- `docs/reference/` - Reference materials

## Common Tasks

### Exploratory Data Analysis

- [ ] Load and inspect raw data
- [ ] Calculate summary statistics
- [ ] Identify distributions and outliers
- [ ] Check for missing values
- [ ] Create initial visualizations

### Statistical Testing

- [ ] Define null and alternative hypotheses
- [ ] Select appropriate statistical test
- [ ] Check test assumptions
- [ ] Calculate p-values and effect sizes
- [ ] Interpret results with caution

### Generate Report

- [ ] Write executive summary
- [ ] Include key findings and visualizations
- [ ] Explain methodology
- [ ] Note limitations and caveats
- [ ] Suggest next steps

### Create Dashboard

- [ ] Identify key metrics
- [ ] Design dashboard layout
- [ ] Implement interactive elements (if applicable)
- [ ] Add filtering and drill-down capabilities
- [ ] Document how to use

## Success Criteria

- ✅ Analysis answers the research question clearly
- ✅ Methodology is documented and reproducible
- ✅ Visualizations are clear and well-labeled
- ✅ Statistical claims are properly supported
- ✅ Limitations and assumptions are documented
- ✅ Insights are actionable and specific
- ✅ Report is accessible to stakeholders
