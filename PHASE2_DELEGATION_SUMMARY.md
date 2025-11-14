# Phase 2: Qualitative Pipeline - Agent Delegation Summary

**Timeline**: Week 5-6 (Days 29-42) | November 15-28, 2025

---

## 📋 Executive Summary

Delegating implementation of the 6-stage **Qualitative Intelligence Pipeline** to three parallel agents:

- **Cloud Copilot SWE Agent**: Stage 1 (Source Planning)
- **Copilot Chat**: Stages 2-3 (Content Extraction + Synthesis)
- **Claude/Codex**: Stages 4-6 (LR Generation + Calibration + Fusion Prep)

**Critical Prerequisite**: Must backfill database with 200+ historical races first (currently only ~10 races)

---

## 🎯 Three Agent Tasks

### **Agent 1: Cloud Copilot SWE** 🔥🔥🔥

**Task**: Build Stage 1 - Source Planning Agent (Days 29-30)

**Deliverables**:

- `src/pipelines/qualitative/stage1_source_planner.py` (300+ lines)
- Gemini API integration for Categories 1-17 discovery
- `tests/pipelines/test_stage1_source_planner.py` (18+ test cases)

**Key Responsibilities**:

- Implement `SourcePlanningAgent` class
- Method: `plan_sources(race_context) → list[str]` (15-25 sources)
- Gemini prompt engineering for category mapping
- Source prioritization by relevance (0-1 score)
- Category assignment (1-17) for each source

**Inputs**: Race details (GraphQL), horse details, market context
**Outputs**: Prioritized source list with categories and relevance scores

**Success Metric**: 90%+ source discovery accuracy across 18 test cases

**Reference**: `IMPLEMENTATION_PLAN_FORWARD.md` lines 461-500

**PR Target**: `pr/copilot-qualitative-stage1`

---

### **Agent 2: Copilot Chat** 🔥🔥

**Task**: Build Stages 2-3 - Content Extraction & Synthesis (Days 31-34)

**Deliverables**:

- `src/pipelines/qualitative/stage2_content_extractor.py` (250+ lines)
- `src/pipelines/qualitative/stage3_synthesis.py` (300+ lines)
- `tests/pipelines/test_stage2_3_pipelines.py` (15+ test cases)

**Stage 2 - Content Extraction**:

- Input: Source URLs from Stage 1
- Extract: Article text, quotes, key points, sentiment
- Output: Structured content with metadata
- Methods:
  - BeautifulSoup for HTML articles
  - PDF parsing for reports
  - API calls for structured data
  - Sentiment analysis (positive/neutral/negative)

**Stage 3 - Information Synthesis**:

- Input: 15-25 extracted sources per horse
- Use GPT-4 to synthesize consensus
- Output: 5-7 key insights, strengths, concerns, assessment
- Methods:
  - Multi-source aggregation
  - Conflict detection/resolution
  - Source weighting by reliability

**Success Metric**: 85%+ synthesis accuracy (vs manual review)

**Reference**: `IMPLEMENTATION_PLAN_FORWARD.md` lines 515-570

**PR Target**: `pr/copilot-qualitative-stages2-3`

---

### **Agent 3: Claude/Codex** 🔥

**Task**: Build Stages 4-6 - LR Generation, Calibration, Fusion Prep (Days 35-39)

**Deliverables**:

- `src/pipelines/qualitative/stage4_lr_generation.py` (200+ lines)
- `src/pipelines/qualitative/stage5_calibration.py` (180+ lines)
- `src/pipelines/qualitative/stage6_fusion_prep.py` (150+ lines)
- `tests/pipelines/test_stage4_5_6_lrs.py` (20+ test cases)

**Stage 4 - LR Generation**:

- Input: Synthesis from Stage 3
- For each category (1-21): Generate LR (0.70-1.30)
- Use GPT-4 to convert qualitative → quantitative
- Output: `{category: (lr, reasoning, confidence), ...}`

**Stage 5 - Confidence Calibration**:

- Input: LRs from Stage 4
- Adjust confidence based on:
  - Source reliability
  - Historical GPT accuracy per category
  - Certainty in reasoning
  - Cross-source agreement
- Output: Calibrated confidence scores

**Stage 6 - Fusion Preparation**:

- Input: Calibrated LRs from Stage 5
- Format for Bayesian fusion
- Calculate weights: `confidence × category_importance × source_agreement`
- Output: Fusion-ready dictionary

**Success Metrics**:

- LR validity: 95%+
- Calibration accuracy: 85%+
- Fusion format: 100% valid

**Reference**: `IMPLEMENTATION_PLAN_FORWARD.md` lines 575-638

**PR Target**: `pr/codex-qualitative-stages4-6`

---

## 📅 Timeline & Dependencies

```
PREREQUISITE (Priority 0):
  Day 1-3: Backfill 200+ historical races from Oct-Nov 2024
           Script: scripts/backfill_historical.py
           Status: READY (script created, needs execution)

PARALLEL WORK (starting after backfill):
  Week 5:
    Days 29-30: Cloud Agent → Stage 1 (Source Planner) ✅
    Days 31-32: Chat Agent → Stage 2 (Content Extractor) ⏳ waiting for Stage 1
    Days 33-34: Chat Agent → Stage 3 (Synthesizer) ⏳ waiting for Stage 2
    Days 35-39: Codex → Stages 4-6 (LR Pipeline) ⏳ waiting for Stage 3

  Week 6:
    Days 40-42: Integration & E2E Testing
               - Connect all 6 stages
               - Test on 10 races (high/medium/low quality)
               - Validate metrics
```

---

## 🔗 Integration Flow

```
Stage 1: Source Planner
  ↓ (prioritized source list)
Stage 2: Content Extractor
  ↓ (extracted content)
Stage 3: Synthesizer (GPT-4)
  ↓ (synthesis: insights, strengths, concerns)
Stage 4: LR Generator (GPT-4)
  ↓ (LR values per category)
Stage 5: Calibrator
  ↓ (calibrated LRs with confidence)
Stage 6: Fusion Prep
  ↓ (fusion-ready format)
Output: Ready for Bayesian Fusion (Phase 3)
```

---

## ✅ Success Criteria

| Component | Agent | Metric | Target |
|-----------|-------|--------|--------|
| Stage 1 | Cloud | Source discovery accuracy | 90%+ |
| Stage 2 | Chat | Content extraction success | 85%+ |
| Stage 3 | Chat | Synthesis accuracy (manual review) | 85%+ |
| Stage 4 | Codex | LR generation validity | 95%+ |
| Stage 5 | Codex | Calibration accuracy | 85%+ |
| Stage 6 | Codex | Fusion format validity | 100% |
| **E2E** | All | Brier score on 10 test races | <0.22 |
| **E2E** | All | Processing time per race | <2 min |

---

## 📊 Database Requirement

**BLOCKER**: Current database has only ~10 races. Need 100+ races minimum.

**Backfill Script**: `scripts/backfill_historical.py`

**How to Run**:

```bash
# Sample backfill (20 races for testing)
python scripts/backfill_historical.py --sample

# Full backfill (all venues, Oct-Nov 2024)
python scripts/backfill_historical.py --all

# Specific venue
python scripts/backfill_historical.py --venue flemington --start 2024-10-01 --end 2024-11-30
```

**Target**: 200+ races from Spring Carnival 2024

- Flemington: 50 races
- Caulfield: 40 races
- Moonee Valley: 30 races
- Randwick: 40 races
- Rosehill: 40 races

**Estimated Time**: 2-3 days (50 races/day @ 1 sec/race)

---

## 📝 API & Credential Requirements

**Cloud Agent (Stage 1)**:

- Google Gemini API key (set `GOOGLE_API_KEY` env var)
- Already integrated: `google.generativeai` library

**Chat Agent (Stages 2-3)**:

- GPT-4 API access via `openai` library
- Already integrated: BeautifulSoup, NLP libraries

**Codex (Stages 4-6)**:

- GPT-4 API access (same as Chat Agent)
- Historical accuracy data (in database after backfill)

---

## 🎓 Key Concepts

**Likelihood Ratio (LR)**:

- Measures evidence strength: `P(evidence|hypothesis) / P(evidence|¬hypothesis)`
- Range: 0.70 (strong negative) to 1.30 (strong positive)
- 1.0 = neutral (no effect)
- Example: LR=1.25 means evidence increases win probability by 25%

**Bayesian Fusion**:

- Combines qualitative + quantitative LRs
- Final probability = market odds × Π(qualitative_LRs) × Π(quantitative_LRs)
- Confidence weighting: higher confidence LRs weighted more

**Categories 1-21**:

- **1-17**: Qualitative (from articles, tips, analysis)
- **18-21**: Quantitative (from speed ratings, weight, barrier, history)

---

## 🚨 Known Dependencies & Risks

**Critical Path**:

1. Backfill historical data (2-3 days) - **BLOCKING**
2. Stage 1 (Cloud Agent) - must complete before Stage 2
3. Stage 2 (Chat Agent) - must complete before Stage 3
4. Stage 3 (Chat Agent) - must complete before Stage 4
5. Stages 4-6 (Codex) - can work in parallel, sequential internally
6. E2E Integration (All) - final validation

**Risk Mitigation**:

- Start backfill TODAY (don't wait for agent handoff)
- Cloud Agent can start Stage 1 while backfill runs in parallel
- Chat Agent and Codex can prepare/review specs while waiting
- Build comprehensive unit tests in parallel with implementation

---

## 📋 PR Merge Order

1. **`pr/copilot-qualitative-stage1`** (Cloud Agent)
   - Status: Ready to merge after review
   - Merge into: `develop` branch
   - Prerequisite: None (independent)

2. **`pr/copilot-qualitative-stages2-3`** (Chat Agent)
   - Status: Ready to merge after review
   - Merge into: `develop` branch
   - Prerequisite: Stage 1 merged (for API reference)

3. **`pr/codex-qualitative-stages4-6`** (Codex)
   - Status: Ready to merge after review
   - Merge into: `develop` branch
   - Prerequisite: Stages 2-3 merged (for input format)

4. **Integration PR** (All)
   - Connect all 6 stages
   - E2E tests on 10 races
   - Final merge into `main`

---

## 📞 Support & Communication

**Weekly Sync**: Every Friday @ 5pm UTC

- Cloud Agent: Report Stage 1 progress
- Chat Agent: Report Stages 2-3 progress
- Codex: Report Stages 4-6 progress
- Discuss blockers, dependency issues

**Escalation Path**:

1. Agent → Lead Copilot
2. Lead Copilot → Project Owner
3. Async updates in `#racing-analysis-dev` Slack channel

---

## 🎯 Next Action Items

**For Lead/Project Owner**:

- [ ] Review and approve delegation plan
- [ ] Execute backfill script (start TODAY)
- [ ] Confirm Gemini API key for Cloud Agent
- [ ] Confirm GPT-4 access for Chat Agent and Codex

**For Cloud Agent**:

- [ ] Review Stage 1 spec
- [ ] Set up local dev environment
- [ ] Clone repo and create feature branch
- [ ] Begin implementation

**For Chat Agent**:

- [ ] Review Stages 2-3 spec
- [ ] Familiarize with Stage 1 output format
- [ ] Prepare implementation plan
- [ ] Wait for Stage 1 completion before starting

**For Codex**:

- [ ] Review Stages 4-6 spec
- [ ] Familiarize with Stage 3 output format
- [ ] Research historical accuracy metrics
- [ ] Wait for Stage 3 completion before starting

---

## 📚 Reference Materials

- **Full Plan**: `IMPLEMENTATION_PLAN_FORWARD.md` (lines 439-730)
- **Delegation Details**: `DELEGATION_PHASE2_QUALITATIVE.md`
- **Scraper Examples**: `src/data/scrapers/` (reference for multi-stage patterns)
- **Test Examples**: `tests/data/` (reference for test structures)

---

**Status**: Ready for execution ✅
**Awaiting**: Backfill completion + agent assignment
