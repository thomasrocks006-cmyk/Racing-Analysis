# 🎯 MASTER CONTEXT - Racing Analysis System

**Last Updated:** November 13, 2025
**Purpose:** Single source of truth for AI agents to understand the complete system architecture and implementation status
**Critical:** READ THIS FILE FIRST before making any architectural judgments or analysis

---

## 🚨 CRITICAL RULES FOR AI AGENTS

### **Rule #1: NEVER Simplify the Architecture**

The master plan is **correct as designed**. Do not suggest simplifications unless explicitly asked. The dual-pipeline + fusion model architecture is the competitive advantage.

### **Rule #2: NEVER Make Up Implementation Status**

- If you haven't read the actual code files, say "I need to check the implementation"
- Do not assume features exist based on documentation
- Always verify with `grep_search`, `read_file`, or `semantic_search` before claiming something is implemented

### **Rule #3: NEVER Hallucinate About What's Built**

The system has extensive documentation but **minimal working code**. Default assumption:

- ✅ Documentation exists
- ❌ Implementation does NOT exist (until verified)

### **Rule #4: Build What Was Designed**

Follow MASTER_PLAN.md, FUSION_MODEL_ARCHITECTURE.md, and the 21-category taxonomy exactly as specified. These are correct and should not be changed without explicit user request.

---

## 📋 PROJECT OVERVIEW

### **Project Name:** Racing Analysis System

### **Goal:** High-accuracy horse racing prediction using qualitative + quantitative dual-pipeline fusion

### **Core Architecture (DO NOT CHANGE):**

```
21-Category Taxonomy
    ↓
Dual Pipeline System:
    ↓
1. Qualitative Pipeline (Categories 1-17)
   - 6 stages with GPT-5/Gemini/Claude
   - Cost: $0.62/race
   - Time: 5-7 minutes
   - Output: Likelihood Ratios (LRs)
    ↓
2. Quantitative Pipeline (Categories 18-21)
   - ML models (LightGBM/XGBoost/CatBoost)
   - Cost: <$0.01/race
   - Time: 10-30 seconds
   - Output: Base probabilities
    ↓
3. Fusion Model (15 Concurrent Agents)
   - E2B sandboxes for parallel execution
   - OpenHands orchestration
   - Bayesian LR fusion
   - Consensus synthesis
   - Output: Final calibrated probabilities
```

### **Expected Performance (AS DESIGNED):**

- Brier score: <0.16
- ROI: >7.2%
- Calibration error: <2%
- Runtime: 30-60s (parallel execution)

---

## 📁 CRITICAL DOCUMENTS (Read These Before Analysis)

### **Architecture & Planning:**

1. **MASTER_PLAN.md** (1039 lines)
   - Complete system architecture
   - Dual pipeline specifications
   - Implementation phases
   - **STATUS:** ✅ Complete and correct

2. **FUSION_MODEL_ARCHITECTURE.md** (1530 lines)
   - 15-agent concurrent fusion design
   - E2B + OpenHands integration
   - Bayesian LR algorithms
   - **STATUS:** ✅ Complete design, ❌ NOT IMPLEMENTED

3. **DATA_SOURCE_MAPPING_AND_SCRAPING_ARCHITECTURE.md**
   - All 21 categories → data sources
   - 40+ scraper specifications
   - Implementation roadmap
   - **STATUS:** ✅ Complete mapping created Nov 12, 2025

4. **COMPREHENSIVE_TAXONOMY_MASTER/** (26 parts, 16,926 lines)
   - Categories 1-21 detailed specifications
   - Integration matrices A/B/C
   - Implementation roadmaps
   - **STATUS:** ✅ Complete specifications

### **Reality Check Documents:**

5. **IMPLEMENTATION_REALITY_CHECK.md**
   - Honest assessment: ~10% working code
   - What exists vs what's documented
   - **READ THIS to avoid false claims**

---

## 🎯 WHAT ACTUALLY EXISTS (Implementation Status)

### ✅ **COMPLETE:**

1. **Documentation (100%)**
   - Master plan ✅
   - Fusion model architecture ✅
   - 21-category taxonomy ✅
   - Data source mapping ✅

2. **Database Schema (90%)**
   - DuckDB with 13 tables ✅
   - Proper schema design ✅
   - Only ~10 placeholder races ⚠️
   - Location: `src/data/init_db.py`, `src/data/schema.sql`

3. **Deployment Infrastructure (100%)**
   - Docker + docker-compose ✅
   - FastAPI server ✅
   - Prometheus + Grafana setup ✅
   - Location: `src/deployment/`, `docker-compose.yml`

### ⚠️ **PARTIAL (Exists but Incomplete):**

4. **Quantitative ML Pipeline (40%)**
   - Feature engineering code exists ⚠️
   - ML models code exists ⚠️
   - Calibration code exists ⚠️
   - **BUT:** All trained on placeholder data
   - **Location:** `src/features/`, `src/models/`, `src/calibration/`
   - **Issue:** Cannot validate without real data

5. **Scrapers (5%)**
   - `src/data/scrapers/racing_com.py` - ❌ Returns fake data
   - `src/data/scrapers/stewards.py` - ❌ Returns fake data
   - `src/data/scrapers/market_odds.py` - ❌ Returns fake data
   - **Reality:** ZERO live web scraping implemented

6. **Orchestration (15%)**
   - Basic agent API wrappers exist ⚠️
   - Location: `src/orchestration/agents/`
   - **BUT:** Not connected to fusion model
   - No E2B integration ❌
   - No OpenHands integration ❌

### ❌ **NOT IMPLEMENTED (0%):**

7. **Qualitative Pipeline (0%)**
   - No Stage 1: Source Planning ❌
   - No Stage 2: Parallel Scraping ❌
   - No Stage 3: Content Extraction ❌
   - No Stage 4: Deep Reasoning (GPT-5) ❌
   - No Stage 5: Synthesis (Claude) ❌
   - No Stage 6: Quality Verification ❌
   - **Directory doesn't exist:** `src/qualitative/` NOT FOUND

8. **Fusion Model (0%)**
   - `src/fusion/__init__.py` contains only: `"""Qualitative research fusion"""`
   - No Bayesian LR logic ❌
   - No E2B integration ❌
   - No OpenHands integration ❌
   - No 15-agent system ❌
   - No consensus synthesis ❌

9. **Live Data Collection (0%)**
   - No Betfair API integration ❌
   - No live racing.com scraping ❌
   - No 15-40 sources per race ❌
   - Database has ~10 placeholder races only

---

## 🏗️ IMPLEMENTATION PRIORITIES (What to Build Next)

### **Phase 1: Data Foundation (Weeks 1-4)**

**Critical Path - System is non-functional without this**

1. **Week 1-2: Core Scrapers**
   - [ ] Rewrite `racing_com.py` with real BeautifulSoup scraping
   - [ ] Integrate Betfair API (Categories 8-9)
   - [ ] Build weather API integration (Category 3)
   - [ ] Populate 100+ historical races

2. **Week 3-4: Extended Scrapers**
   - [ ] Stewards reports scraper (PDF parsing)
   - [ ] Barrier trials scraper
   - [ ] Gear changes scraper
   - [ ] Expert commentary scraper
   - [ ] Target: 500+ historical races

### **Phase 2: Qualitative Pipeline (Weeks 5-8)**

**Competitive Advantage - Build as Designed**

3. **Week 5-6: Stages 1-3**
   - [ ] Stage 1: Source Planning (Gemini 2.5 Flash)
   - [ ] Stage 2: Parallel Scraping (15-40 sources)
   - [ ] Stage 3: Content Extraction (Gemini)

4. **Week 7-8: Stages 4-6**
   - [ ] Stage 4: Deep Reasoning (GPT-5 Extended Thinking)
   - [ ] Stage 5: Synthesis (Claude Sonnet 4.5)
   - [ ] Stage 6: Quality Verification (GPT-4o)

### **Phase 3: Fusion Model (Weeks 9-12)**

**Integration Layer - Build as Designed**

5. **Week 9-10: E2B + Bayesian Logic**
   - [ ] E2B sandbox integration
   - [ ] Bayesian LR update algorithm
   - [ ] Single-agent fusion (test)
   - [ ] Expand to 15 concurrent agents

6. **Week 11-12: OpenHands + Consensus**
   - [ ] OpenHands orchestration
   - [ ] Consensus synthesis
   - [ ] Outlier detection
   - [ ] Full system integration test

---

## 💡 DESIGN PRINCIPLES (Never Violate These)

### **1. No Data Leakage**

- Strict event-time ordering
- Train/test splits respect time boundaries
- No look-ahead bias in features

### **2. Dual Pipeline Architecture**

- Qualitative (Categories 1-17) → LRs
- Quantitative (Categories 18-21) → Probabilities
- Fusion → Combined predictions
- **Do not merge or simplify this structure**

### **3. Multi-Agent Fusion**

- 15 specialized agents with different strategies
- E2B parallel execution
- Consensus synthesis
- **Do not reduce to single agent unless explicitly requested**

### **4. 21-Category Taxonomy**

- Foundation of all feature engineering
- Each category has specific data sources
- Integration matrices link categories
- **Do not skip categories or merge them**

### **5. Uncertainty Quantification**

- All predictions include confidence intervals
- Conformal prediction sets
- Calibration monitoring
- **Never output point predictions without uncertainty**

---

## 🔧 WORKING STYLE & CONSTRAINTS

### **Code Quality:**

- Type hints required (Python 3.11+)
- Comprehensive error handling
- Logging for all major operations
- Unit tests for critical functions

### **Data Sources:**

- Non-commercial personal use only
- Respect rate limits (1-2 seconds between requests)
- Cache aggressively
- Handle failures gracefully

### **AI Model Usage:**

- GPT-5: Deep reasoning, contradiction resolution
- Claude Sonnet 4.5: Long-form synthesis, reports
- Gemini 2.5 Flash: Fast extraction, source planning
- GPT-4o: Quality verification, fact-checking

### **Performance Targets:**

- Qualitative pipeline: 5-7 minutes
- Quantitative pipeline: 10-30 seconds
- Fusion model: 30-60 seconds (parallel)
- Total end-to-end: 7-8 minutes max

---

## 📊 CURRENT METRICS (What We Can Actually Measure)

### **Documentation:**

- Lines of specifications: 16,926 ✅
- Architecture documents: 85+ files ✅
- Completeness: 100% ✅

### **Implementation:**

- Python files: 75 files
- Total lines of code: ~11,000
- **Working scrapers: 0** ❌
- **Historical races: ~10** ❌
- **Qualitative pipeline: 0%** ❌
- **Fusion model: 0%** ❌

### **Validation Status:**

- Cannot validate backtests (no data) ❌
- Cannot validate ROI (no data) ❌
- Cannot validate Brier score (no data) ❌
- **System is non-functional for production** ❌

---

## 🚨 COMMON MISTAKES TO AVOID

### **Mistake #1: "We've built 60% of the system"**

❌ **FALSE** - We have ~10% working code
✅ **TRUE** - We have 100% design documentation

### **Mistake #2: "Simplify the dual pipeline"**

❌ **NEVER** - The dual pipeline is the competitive advantage
✅ **BUILD IT** - As designed in MASTER_PLAN.md

### **Mistake #3: "The quantitative pipeline is production-ready"**

❌ **FALSE** - It's trained on placeholder data only
✅ **TRUE** - The code structure exists but needs real data

### **Mistake #4: "Maybe skip the qualitative pipeline"**

❌ **NEVER** - That's 30-40% of predictive signal
✅ **BUILD IT** - All 6 stages as designed

### **Mistake #5: "15 agents is too complex, use 3"**

❌ **NO** - 15 agents reduces variance and improves consensus
✅ **BUILD IT** - As designed in FUSION_MODEL_ARCHITECTURE.md

### **Mistake #6: "Scrapers are working"**

❌ **FALSE** - All scrapers return placeholder data
✅ **TRUE** - We need to build 40+ live scrapers

---

## 📚 KEY FILE LOCATIONS

### **Documentation:**

- Master plan: `MASTER_PLAN.md`
- Fusion architecture: `docs/FUSION_MODEL_ARCHITECTURE.md`
- Taxonomy: `docs/COMPREHENSIVE_TAXONOMY_MASTER/PART_*.md`
- Data sources: `DATA_SOURCE_MAPPING_AND_SCRAPING_ARCHITECTURE.md`

### **Implementation:**

- Database: `src/data/init_db.py`, `src/data/schema.sql`
- Scrapers: `src/data/scrapers/*.py` (all placeholder)
- Features: `src/features/*.py`
- Models: `src/models/*.py`
- Fusion: `src/fusion/__init__.py` (empty)
- Qualitative: NOT CREATED YET

### **Configuration:**

- Environment: `.env.example`
- Docker: `docker-compose.yml`
- Python: `pyproject.toml`

---

## 🎯 VERIFICATION CHECKLIST (Before Making Claims)

Before saying something is "implemented" or "complete", verify:

1. [ ] Read the actual source file with `read_file`
2. [ ] Check for placeholder/fake data returns
3. [ ] Verify imports and dependencies exist
4. [ ] Check if directory structure exists
5. [ ] Search for actual implementation logic (not just comments)
6. [ ] Verify with `grep_search` for key functions/classes
7. [ ] Check git history if needed
8. [ ] Cross-reference with IMPLEMENTATION_REALITY_CHECK.md

**If you can't verify → say "I need to check" → do NOT assume it exists**

---

## 🔄 NEXT ACTIONS (Current Priority)

### **Immediate (This Week):**

1. Build racing.com live scraper (replace placeholder)
2. Integrate Betfair API
3. Populate 100 historical races

### **Short Term (Next 2 Weeks):**

4. Build remaining core scrapers (stewards, trials, gear)
5. Populate 500+ historical races
6. Begin qualitative pipeline Stage 1

### **Medium Term (Next 4-6 Weeks):**

7. Complete qualitative pipeline (all 6 stages)
8. Build fusion model (E2B + 15 agents)
9. Full system integration

### **Long Term (Next 8-12 Weeks):**

10. Production deployment
11. Live race validation
12. Performance optimization

---

## 🧠 CONTEXT FOR AGENTS

**When you're asked to analyze the system:**

1. Read MASTER_CONTEXT.md (this file) FIRST
2. Read IMPLEMENTATION_REALITY_CHECK.md
3. Read DATA_SOURCE_MAPPING_AND_SCRAPING_ARCHITECTURE.md
4. Then analyze actual code with verification

**When you're asked to build something:**

1. Check MASTER_PLAN.md for the designed architecture
2. Check FUSION_MODEL_ARCHITECTURE.md for fusion specs
3. Check COMPREHENSIVE_TAXONOMY_MASTER for category specs
4. Build exactly as designed (don't simplify)

**When you're unsure:**

1. Say "I need to verify this"
2. Use grep_search or read_file to check
3. Don't hallucinate or guess
4. Ask for clarification

---

## ✅ CONFIDENCE INDICATORS

When making statements, use confidence indicators:

- **✅ VERIFIED:** I have read the source code
- **📋 DOCUMENTED:** Exists in documentation but not verified in code
- **⚠️ UNCERTAIN:** Need to check actual implementation
- **❌ NOT IMPLEMENTED:** Confirmed absence of code
- **🔍 NEED TO CHECK:** Should verify before claiming

---

**Last Updated:** November 13, 2025
**Maintained By:** Project team
**Version:** 1.0
**Next Review:** When significant architecture changes occur

---

# 🎯 REMEMBER

## The system has EXCELLENT DESIGN but MINIMAL IMPLEMENTATION

**Do not confuse documentation completeness with code completeness**
