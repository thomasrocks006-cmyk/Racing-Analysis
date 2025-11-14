# Phase 2: Qualitative Pipeline - Delegation Plan

**Timeline: Week 5-6 (Days 29-42) | November 15-28, 2025**

---

## 🎯 Overview

Implement the 6-stage Qualitative Pipeline for intelligent multi-source information analysis:

1. **Stage 1**: Source Planning Agent (Category 1-17 discovery)
2. **Stage 2**: Content Extraction (parse sources)
3. **Stage 3**: Information Synthesis (multi-source synthesis)
4. **Stage 4**: LR Generation (convert to quantitative)
5. **Stage 5**: Confidence Calibration (validate LRs)
6. **Stage 6**: Fusion Preparation (format for Bayesian fusion)

---

## 👥 Agent Delegation

### **Agent 1: Cloud Copilot SWE Agent** 🔥🔥🔥

**Task**: Stage 1 - Source Planning Agent (Days 29-30)
**Dependencies**: None (starts immediately)

**Deliverables**:

- `src/pipelines/qualitative/stage1_source_planner.py`
- Gemini API integration
- Category 1-17 prompt engineering
- Unit tests (test_stage1_source_planner.py)

**Key Files to Reference**:

- `IMPLEMENTATION_PLAN_FORWARD.md` lines 461-500
- `src/data/models.py` - Race/Horse/Jockey models

**PR Target**: `pr/copilot-qualitative-stage1`

**Instructions**:

```
Build the Source Planning Agent using Google Gemini API:

1. Create SourcePlanningAgent class
2. Implement plan_sources(race_context) method
3. Input: Race details, horse details, market context (from Racing.com GraphQL)
4. Output: Prioritized list of sources to extract (15-25 sources per race)

Gemini Prompt Template:
"Given this race [race_name] [distance]m [conditions] at [venue]:
Runners: [horse_name] (barrier [num], odds $[price]), ...

What information sources would help analyze each runner?
Prioritize by: relevance, information quality, freshness.
Consider: recent form, track specialists, barrier draws, jockey changes, market moves.
Return top 20 sources with category (1-17) and relevance score (0-1)."

Include 18 test cases:
- Group 1 race (15+ sources expected)
- Listed race (8-10 sources)
- Maiden race (5-8 sources)
- High-profile jockey changes
- Market steam situations
- etc.

Target: 90%+ successful source identification
```

---

### **Agent 2: Copilot Chat** 🔥🔥

**Task**: Stage 2 & 3 - Content Extraction + Synthesis (Days 31-34)
**Dependencies**: Stage 1 (source list output)

**Deliverables**:

- `src/pipelines/qualitative/stage2_content_extractor.py`
- `src/pipelines/qualitative/stage3_synthesis.py`
- Integration with GPT-4 for synthesis
- Unit tests (test_stage2_3_pipelines.py)

**Key Files to Reference**:

- `IMPLEMENTATION_PLAN_FORWARD.md` lines 515-570
- BeautifulSoup for parsing
- NLP libraries for sentiment/quotes

**PR Target**: `pr/copilot-qualitative-stages2-3`

**Instructions**:

```
Build Content Extraction and Synthesis stages:

STAGE 2: ContentExtractor
1. Input: Source URLs from Stage 1
2. Extract content:
   - Web scraping (BeautifulSoup for HTML articles)
   - PDF parsing for reports
   - API calls for structured data
3. Output structure:
   {
     'source_id': str,
     'content_type': 'article|tip|report|social',
     'text': str,
     'quotes': list,
     'key_points': list,
     'mentioned_horses': list,
     'sentiment': 'positive|neutral|negative',
     'confidence': float,
     'timestamp': datetime
   }

STAGE 3: InformationSynthesizer
1. Input: 15-25 extracted sources per horse
2. Use GPT-4 to synthesize:
   - Identify consensus across sources
   - Flag disagreements/contradictions
   - Weight by source reliability
   - Generate 5-7 key insights
3. Output:
   {
     'insights': [...],
     'strengths': [...],
     'concerns': [...],
     'market_implications': str,
     'overall_assessment': str,
     'confidence': float,
     'sources_used': int
   }

Include 15 test cases covering:
- High-quality 15+ source synthesis
- Medium-quality 8-10 source synthesis
- Low-quality 3-5 source synthesis
- Conflicting source resolution
- Sentiment consistency

Target: 85%+ synthesis accuracy (vs manual review)
```

---

### **Agent 3: Claude/Codex** 🔥

**Task**: Stage 4, 5, 6 - LR Generation, Calibration, Fusion Prep (Days 35-39)
**Dependencies**: Stages 2-3 (synthesis output)

**Deliverables**:

- `src/pipelines/qualitative/stage4_lr_generation.py`
- `src/pipelines/qualitative/stage5_calibration.py`
- `src/pipelines/qualitative/stage6_fusion_prep.py`
- Unit tests (test_stage4_5_6_lrs.py)

**Key Files to Reference**:

- `IMPLEMENTATION_PLAN_FORWARD.md` lines 575-638
- `src/data/models.py` - Likelihood Ratio model
- Historical race results for calibration

**PR Target**: `pr/codex-qualitative-stages4-6`

**Instructions**:

```
Build Likelihood Ratio generation pipeline:

STAGE 4: LikelihoodRatioGenerator
1. Input: Synthesis from Stage 3
2. For each category (1-21):
   - GPT-4 prompt to generate LR
   - Output: (lr: 0.70-1.30, reasoning: str, confidence: 0.0-1.0)
3. Category-specific ranges:
   - Cat 1 (Recent Form): 0.75-1.25
   - Cat 2 (Class): 0.80-1.20
   - Cat 3 (Track): 0.85-1.15
   - Cat 12 (Market): 0.90-1.15
4. Store: {category: (lr, reasoning, confidence), ...}

STAGE 5: ConfidenceCalibrator
1. Input: LRs from Stage 4
2. Adjust confidence based on:
   - Source reliability score
   - Historical GPT accuracy (per category)
   - Certainty keywords in reasoning
   - Cross-source agreement
3. Output: Calibrated confidence (0.0-1.0)
4. Calibration formula:
   calibrated_conf = base_conf * source_weight * historical_accuracy

STAGE 6: FusionPreparation
1. Input: Calibrated LRs from Stage 5
2. Format for Bayesian fusion:
   {
     'qualitative_lrs': {
       1: {'lr': 1.15, 'confidence': 0.80, 'weight': calc_weight()},
       2: {'lr': 1.08, 'confidence': 0.65, 'weight': calc_weight()},
       ...
     },
     'combined_confidence': avg_confidence,
     'source_count': 15,
     'synthesis_quality': 'high|medium|low'
   }
3. Weight calculation: confidence * category_importance * source_agreement

Include 20 test cases:
- Single strong source vs multiple weak sources
- Conflicting LR calculations
- Confidence calibration accuracy
- Fusion format validation
- Category-specific LR ranges

Target: Calibration accuracy >85%, fusion format 100% valid
```

---

## 📅 Timeline & Sequencing

```
Week 5:
  Day 29-30: Cloud Copilot → Stage 1 (Source Planner) ✅
  Day 31-32: Copilot Chat → Stage 2 (Content Extractor) ⏳ (waiting for Stage 1)
  Day 33-34: Copilot Chat → Stage 3 (Synthesizer) ⏳ (waiting for Stage 2)
  Day 35-39: Codex → Stages 4-6 (LR + Calibration + Fusion) ⏳ (waiting for Stage 3)

Week 6:
  Day 40-42: Integration & E2E Testing
    - Connect all 6 stages
    - Test on 10 races (high/medium/low quality)
    - Validate Brier score, LR accuracy
```

---

## 🔗 Integration Points

**Stage 1 Input**:

- Racing.com race details (from GraphQL scraper)
- Current market odds (from Betfair scraper)

**Stage 2 Input**:

- Source list from Stage 1

**Stage 3 Input**:

- Extracted content from Stage 2

**Stage 4 Input**:

- Synthesis from Stage 3

**Stage 5 Input**:

- LRs from Stage 4
- Historical accuracy metrics (from past races)

**Stage 6 Input**:

- Calibrated LRs from Stage 5

**Final Output**:

- Ready for Bayesian Fusion (Phase 3)

---

## ✅ Success Criteria

| Stage | Agent | Success Metric | Target |
|-------|-------|----------------|--------|
| 1 | Cloud | Source discovery accuracy | 90%+ |
| 2 | Chat | Content extraction success | 85%+ |
| 3 | Chat | Synthesis accuracy (manual review) | 85%+ |
| 4 | Codex | LR generation validity | 95%+ |
| 5 | Codex | Calibration accuracy | 85%+ |
| 6 | Codex | Fusion format validity | 100% |
| **E2E** | All | Brier score on 10 test races | <0.22 |

---

## 📝 PR Naming Convention

- Cloud Agent: `pr/copilot-qualitative-stage1`
- Chat Agent: `pr/copilot-qualitative-stages2-3`
- Codex: `pr/codex-qualitative-stages4-6`

**Merge Order**: Stage 1 → Stage 2-3 → Stage 4-6 → Integration

---

## 🚨 Dependencies & Blockers

**BLOCKER**: Database must have 100+ historical races populated first!

- Current status: ~10 races
- **ACTION REQUIRED**: Run backfill script from Phase 1 FIRST
- Script: `scripts/backfill_historical.py`

Once database is populated:

- All three agents can start working in parallel (within dependency constraints)
- Stage 1 can start immediately (no database dependency)
- Stage 2-3 need Stage 1 output
- Stage 4-6 need Stage 3 output

---

## 📊 Monitoring & Checkpoints

**Checkpoint 1 (Day 30)**: Stage 1 delivers source lists

- PR review on 5 test races
- Source quality assessment

**Checkpoint 2 (Day 34)**: Stages 2-3 deliver synthesis

- PR review on same 5 races
- Compare synthesis quality across stages

**Checkpoint 3 (Day 39)**: Stages 4-6 deliver LRs

- PR review on same 5 races
- Verify LR ranges, calibration, fusion format

**Checkpoint 4 (Day 42)**: E2E Integration

- All 6 stages connected
- 10 races tested end-to-end
- Metrics validation

---

## 🎓 Knowledge Base

**Reference Implementation**: `IMPLEMENTATION_PLAN_FORWARD.md` (lines 461-638)

**Key Concepts**:

- Likelihood Ratios: `LR = P(evidence|hypothesis) / P(evidence|not_hypothesis)`
- Bayesian Fusion: Combine qualitative + quantitative LRs via Bayes theorem
- Confidence Calibration: Adjust confidence based on historical accuracy
- Source Weighting: Prioritize reliable sources over unreliable ones

**Testing Framework**:

- Use pytest for all unit tests
- Mock external APIs (Gemini, GPT-4) for reproducibility
- Include integration tests with real API calls

---

## 💾 Database Requirement

**Must have before starting**: 100+ historical races with:

- Complete race records
- All runner details
- Historical odds
- Race results (winner, placings)
- Jockey/trainer stats

**Backfill Script**: `scripts/backfill_historical.py`

- Populates Oct-Nov 2024 Spring Carnival races
- Should take 2-3 days to run

**Status**: PENDING (only ~10 races in DB currently)
