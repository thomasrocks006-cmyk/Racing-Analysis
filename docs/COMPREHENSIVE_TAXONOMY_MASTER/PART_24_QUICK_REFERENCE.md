# Master Taxonomy - Part 24: Quick Reference Tables & Lookup Matrices

**Document Purpose:** Fast lookup reference for category details, prediction power, costs, and integration rules
**Usage:** Quick consultant during implementation

---

## CATEGORY PREDICTION POWER MATRIX

| Category | ID | Prediction Power | Pipeline | Priority | Cost/Race |
|----------|-----|------------------|----------|----------|-----------|
| Historical Performance | 14 | 20-30% ⭐⭐⭐ | Both | Phase 1 Week 7 | $0 |
| Speed Ratings | 18 | 20-30% ⭐⭐⭐ | Quant | Phase 1 Week 8 | $0-$0.15 |
| Class Ratings | 19 | 15-25% ⭐⭐ | Quant | Phase 1 Week 8 | $0 |
| Market Intelligence | 12 | 15-25% ⭐⭐ | Both | Phase 1 Week 6 | $0 |
| Pace Scenario | 8 | 12-22% ⭐⭐ | Both | Phase 1 Week 5 | $0.05-$0.10 |
| Track/Distance Suitability | 15 | 12-18% ⭐ | Both | Phase 1 Week 4 | $0 |
| Track Conditions | 3 | 10-15% ⭐ | Both | Phase 1 Week 2 | $0 |
| Barrier Draw | 4 | 8-15% ⭐ | Both | Phase 1 Week 2 | $0 |
| Sectional Data | 20 | 10-18% ⭐ | Quant | Phase 1 Week 8 | $0.05-$0.10 |
| Trainer | 7 | 10-18% ⭐ | Both | Phase 1 Week 4 | $0 |
| Chemistry (J-T-H) | 17 | 8-15% | Both | Phase 1 Week 5 | $0 |
| Jockey | 6 | 8-12% | Both | Phase 1 Week 3 | $0 |
| Barrier Trials | 10 | 8-15% | Both | Phase 1 Week 6 | $0.05 |
| Pedigree/Breeding | 21 | 8-15% | Both | Phase 1 Week 8 | $0 |
| Intangibles (Fitness) | 16 | 8-15% | Qual | Phase 1 Week 4 | $0 |
| Gear Changes | 9 | 6-12% | Both | Phase 1 Week 6 | $0 |
| Weather Sensitivity | 13 | 5-10% | Qual | Phase 1 Week 7 | $0 |
| Weight | 5 | 5-8% | Both | Phase 1 Week 3 | $0 |
| Tactics | 11 | 4-8% | Qual | Phase 1 Week 7 | $0 |
| Basic Race Info | 1-2 | 3-5% | Both | Phase 1 Week 1 | $0 |

**Legend:**
- ⭐⭐⭐ = Critical (>20% prediction power)
- ⭐⭐ = High Impact (15-20% prediction power)
- ⭐ = Moderate Impact (8-15% prediction power)

---

## DATA SOURCE SUMMARY

| Category | Primary Source | Backup Source | Access Method | Cost | ChatGPT Access |
|----------|----------------|---------------|---------------|------|----------------|
| Basic Race Info | Racing.com | Tab.com.au | Web scraping | $0 | 95% |
| Track Conditions | Racing.com | BOM API | Web scraping + API | $0 | 80% |
| Barrier Draw | Racing.com | Historical DB | Web scraping | $0 | 90% |
| Weight | Racing.com | Tab.com.au | Web scraping | $0 | 95% |
| Jockey | Racing.com | Historical DB | Web scraping + DB | $0 | 85% |
| Trainer | Racing.com | Historical DB | Web scraping + DB | $0 | 80% |
| Pace Scenario | Speedmaps | Calculated | Subscription/Calc | $0.05-$0.10 | 40% |
| Gear Changes | Racing.com | Stewards | Web scraping | $0 | 90% |
| Barrier Trials | Racing.com | None | Selenium auth | $0.05 | **0%** ⭐ |
| Tactics | Historical DB | Racing.com | Database | $0 | 50% |
| Market | Betfair API | Tab.com.au | API + scraping | $0 | 60% |
| Weather | BOM API | Weather.com | API | $0 | 80% |
| Historical | Historical DB | Racing.com | Database | $0 | 75% |
| Suitability | Historical DB | Calculated | Database | $0 | 60% |
| Intangibles | Derived | Racing.com | Calculated | $0 | 40% |
| Chemistry | Historical DB | Calculated | Database | $0 | 60% |
| Speed Ratings | Timeform | Calculated | Subscription/Calc | $0-$0.15 | 30% ⭐ |
| Class Ratings | Calculated | Racing.com | Calculated | $0 | 40% |
| Sectional Data | Speedmaps | Calculated | Subscription | $0.05-$0.10 | 20% ⭐ |
| Pedigree | Pedigree DB | Racing.com | Database | $0 | 50% |

**Competitive Advantages (ChatGPT <50% access):**
- ⭐ **Barrier Trials:** 0% vs our 90% (authentication wall)
- ⭐ **Speed Ratings:** 30% vs our 95% (calculated/subscription)
- ⭐ **Sectional Data:** 20% vs our 90% (subscription required)
- **Pace Scenario:** 40% vs our 90% (calculated from sectionals)

---

## COST PER RACE BREAKDOWN

| Component | Cost Range | Notes |
|-----------|------------|-------|
| **Data Collection** | | |
| Basic scraping (Categories 1-7, 9, 11-16, 19, 21) | $0 | Free public data |
| Barrier trials extraction (Category 10) | $0.05 | Selenium processing time |
| Market data (Category 12) | $0 | Betfair API free tier |
| Weather data (Category 3, 13) | $0 | BOM API free |
| **Optional Enhancements** | | |
| Speedmaps sectional data (Category 8, 20) | $0.05-$0.10 | Subscription ($50/month ~$0.08/race) |
| Timeform ratings (Category 18) | $0.10-$0.15 | Subscription ($100/month ~$0.15/race) |
| **Total Cost** | | |
| Minimum (no subscriptions) | $0.05 | Barrier trials only |
| Recommended (Speedmaps) | $0.10-$0.15 | Trials + sectionals |
| Premium (Speedmaps + Timeform) | $0.20-$0.30 | Trials + sectionals + ratings |

**Break-even Analysis:**
- At $0.15/race average cost
- Need to analyze ~667 races/month to justify $100/month subscription
- Australian racing: ~300-400 races/week (1200-1600/month)
- ✅ Subscriptions justified for serious operation

---

## INTEGRATION PRIORITY MATRIX

### High-Priority Integrations (Implement First)
| Integration | Categories | Impact | Complexity |
|-------------|-----------|--------|------------|
| Track × Barrier | 3, 4 | High | Low |
| Pace × Run Style | 8 | High | Medium |
| Market × Form | 12, 14 | High | Low |
| Speed × Form | 18, 14 | Very High | Low |
| Chemistry × All | 17, ALL | Medium | Medium |

### Medium-Priority Integrations
| Integration | Categories | Impact | Complexity |
|-------------|-----------|--------|------------|
| Weight × Jockey | 5, 6 | Medium | Low |
| Trainer × Jockey | 7, 6 | Medium | Low |
| Gear × Trials | 9, 10 | Medium | Low |
| Weather × Track | 13, 3 | Medium | Low |
| Pedigree × Distance × Condition | 21, 1, 3 | Medium | High |

### Advanced Integrations (Optimize Later)
| Integration | Categories | Impact | Complexity |
|-------------|-----------|--------|------------|
| Fitness × Speed × Form | 16, 18, 14 | High | High |
| Class × Race Class | 19, 2 | Medium | Medium |
| Sectionals × Pace | 20, 8 | Medium | Medium |

---

## CONTRADICTION RESOLUTION HIERARCHY

**When categories disagree, trust in this order:**

1. **Historical Performance (14)** - 30% weight
   - Most concrete data (actual results)

2. **Speed Ratings (18)** - 25% weight
   - Normalized performance metric

3. **Market Intelligence (12)** - 20% weight
   - Collective wisdom (inside info indicator)

4. **Class Ratings (19)** - 10% weight
   - Objective class assessment

5. **Chemistry (17)** - 8% weight
   - Proven partnerships

6. **Track/Distance Suitability (15)** - 7% weight
   - Venue-specific advantages

**Example Contradiction:**
- Form (14): Excellent (80/100) → +20% confidence
- Market (12): Drifting → -10% confidence
- **Resolution:** Trust form (30% weight) over market (20% weight)
  - **Final:** +8% net confidence (form outweighs market drift)

---

## FEATURE ENGINEERING SUMMARY

**Total Features by Category:**

| Category Group | Feature Count | Type |
|----------------|---------------|------|
| Basic Race Info (1-2) | 30 | Numerical, Categorical |
| Conditions (3-4) | 25 | Numerical, Categorical |
| Weight/Jockey/Trainer (5-7) | 40 | Numerical, Categorical |
| Pace/Gear/Trials (8-10) | 35 | Numerical, Binary |
| Tactics/Market (11-12) | 20 | Numerical, Categorical |
| Weather/Historical (13-14) | 45 | Numerical, Binary |
| Suitability/Intangibles (15-16) | 25 | Numerical, Binary |
| Chemistry (17) | 15 | Numerical, Binary |
| Speed/Class/Sectionals/Pedigree (18-21) | 40 | Numerical |

**Total:** 275 features (quantitative pipeline)

---

**Document Complete: Part 24 (Quick Reference Tables)**
**Next: Part 25 (Common Pitfalls & Troubleshooting)**
