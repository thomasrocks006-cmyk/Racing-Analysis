# Documentation Manifest

**Last Updated:** 2025-11-12
**Status:** Current Architecture Documentation
**Purpose:** Master index for all Racing Analysis system documentation

---

## 📚 Canonical Architecture Documents

### **Foundation** (Read First)

1. **[MASTER_PLAN.md](../MASTER_PLAN.md)** - System architecture, implementation phases, technology stack
2. **[README.md](../README.md)** - Quick start and project overview
3. **[TAXONOMY_OVERVIEW.md](../TAXONOMY_OVERVIEW.md)** - Complete 21-category taxonomy + 3 integration matrices

### **Pipeline Architectures** (Implementation Specifications)

#### Qualitative Pipeline (Categories 1-17)

**Location:** `docs/qualitative-pipeline/`
**Total:** ~5,000 lines of production-ready design
**Output:** Likelihood Ratios (LRs) for each horse
**Cost:** $0.66/race | Runtime: 5-7 minutes

**Parts:**

- **[Part 1: Overview & Categories 1-8](qualitative-pipeline/PART_1_OVERVIEW_AND_CATEGORIES_1-8.md)** - Race Context & Horse Setup (Track, Weather, Barriers, Gear, Jockey/Trainer, Market)
- **[Part 2: Categories 9-17](qualitative-pipeline/PART_2_CATEGORIES_9-17.md)** - Pre-Race Intelligence & Form Analysis (Last Start, Recent Form, Class Movement, Sectionals, Distance/Track/Tempo suitability)
- **[Part 3: LLM Chain & Synthesis](qualitative-pipeline/PART_3_LLM_CHAIN_AND_SYNTHESIS.md)** - Multi-stage LLM processing (Gemini Flash → GPT-5 → Claude Sonnet 4.5 → GPT-4o)
- **[Part 4: Integration Matrices](qualitative-pipeline/PART_4_INTEGRATION_MATRICES.md)** - Cross-category synergies (Matrix A, B, C implementations)
- **[Part 5: Deployment & Integration](qualitative-pipeline/PART_5_DEPLOYMENT_AND_INTEGRATION.md)** - FastAPI, monitoring, fusion model interface

**Key Technologies:** Gemini Flash 2.0, GPT-5 Preview, Claude Sonnet 4.5, GPT-4o, LangChain, FastAPI

#### Quantitative Pipeline (Categories 18-21)

**Location:** `docs/quantitative-pipeline/`
**Total:** ~3,100 lines of production-ready design
**Output:** Base probabilities for each horse
**Cost:** $0.00/race (local inference) | Runtime: 1-2 minutes

**Parts:**

- **[Part 1: Overview & Categories](quantitative-pipeline/PART_1_OVERVIEW_AND_CATEGORIES.md)** - Speed Ratings (Cat 18), Class Ratings (Cat 19), Sectional Analysis (Cat 20), Pedigree Analysis (Cat 21)
- **[Part 2: Feature Engineering & ML Models](quantitative-pipeline/PART_2_FEATURE_ENGINEERING_AND_ML.md)** - 100+ engineered features, ensemble models (CatBoost + LightGBM + XGBoost)
- **[Part 3: Integration & Deployment](quantitative-pipeline/PART_3_INTEGRATION_AND_DEPLOYMENT.md)** - Isotonic calibration, conformal prediction, FastAPI integration

**Key Technologies:** CatBoost, LightGBM, XGBoost, scikit-learn, pandas, FastAPI

#### Fusion Model (Bayesian Integration)

**Location:** `docs/`
**Total:** ~2,200 lines of architecture + critical analysis
**Output:** Final race probabilities (integrated from qual + quant)
**Cost:** $0.30/race | Runtime: 30-60 seconds

**Documents:**

- **[FUSION_MODEL_ARCHITECTURE.md](FUSION_MODEL_ARCHITECTURE.md)** - Concurrent multi-agent Bayesian fusion (1,530 lines)
  - 15 concurrent agents via E2B forking
  - Specialized strategies: Bayesian LR weighting, calibration methods, normalization, uncertainty quantification
  - OpenHands micro-agent orchestration
  - Consensus synthesis with outlier detection
  - Performance: Brier score 0.16, ROI 7.2%

- **[FUSION_MODEL_CRITICAL_ANALYSIS.md](FUSION_MODEL_CRITICAL_ANALYSIS.md)** - Validation & decision analysis (684 lines)
  - Comparative evaluation: Concurrent vs Sequential approaches
  - Cost-benefit analysis: $0.30/race → 567% ROI
  - Enhanced implementation: Adaptive weighting, agent performance tracking
  - Final verdict: APPROVED concurrent architecture + adaptive enhancements

**Key Technologies:** E2B Sandboxes, OpenHands Framework, Bayesian statistics, ensemble voting

---

## 🔧 Setup & Reference Documentation

### Setup Guides

**Location:** `docs/setup/` (to be created)

**API Setup:**

- **[AI_API_FINAL_SUMMARY.md](AI_API_FINAL_SUMMARY.md)** - OpenAI, Anthropic, GLM API configuration
- **[AI_API_OVERVIEW.md](AI_API_OVERVIEW.md)** - High-level API strategy overview
- **[COPILOT_API_COMPLETE_SUMMARY.md](COPILOT_API_COMPLETE_SUMMARY.md)** - GitHub Copilot API integration
- **[COPILOT_API_SETUP.md](COPILOT_API_SETUP.md)** - Copilot setup instructions

**Environment Setup:**

- **[GLM_SETUP_GUIDE.md](GLM_SETUP_GUIDE.md)** - Zhipu GLM API setup (China-specific)
- **[GLM_SUBSCRIPTION_SETUP.md](GLM_SUBSCRIPTION_SETUP.md)** - GLM subscription details
- **[GITHUB_COPILOT_SETUP.md](GITHUB_COPILOT_SETUP.md)** - GitHub Copilot configuration

**Multi-Agent Orchestration:**

- **[FINAL_MULTI_AGENT_SOLUTION.md](FINAL_MULTI_AGENT_SOLUTION.md)** - Multi-agent execution patterns
- **[COPILOT_MULTI_AGENT_OPTIONS.md](COPILOT_MULTI_AGENT_OPTIONS.md)** - Agent orchestration options
- **[AI_ORCHESTRATION_ARCHITECTURE.md](AI_ORCHESTRATION_ARCHITECTURE.md)** - Overall AI agent architecture

**Getting Started:**

- **[GET_STARTED.md](GET_STARTED.md)** - Phase 0 completion checklist
- **[QUICK_START.md](QUICK_START.md)** - Fast track to running the system

### Reference Documentation

**Location:** `docs/reference/` (to be created)

**Model Research:**

- **[MODEL_RESEARCH_2025.md](MODEL_RESEARCH_2025.md)** - LLM model selection research (GPT-5, Gemini Flash 2.0, Claude Sonnet 4.5)
- **[CHATGPT5_DEEP_RESEARCH_ANALYSIS.md](CHATGPT5_DEEP_RESEARCH_ANALYSIS.md)** - GPT-5 capabilities and benchmarks
- **[CHATGPT5_METHODOLOGY_VERIFICATION.md](CHATGPT5_METHODOLOGY_VERIFICATION.md)** - GPT-5 methodology validation
- **[CORRECT_MODEL_INFO.md](CORRECT_MODEL_INFO.md)** - Verified model specifications

**Search & Optimization:**

- **[INTELLIGENT_SEARCH_STRATEGY.md](INTELLIGENT_SEARCH_STRATEGY.md)** - Search optimization techniques

**Taxonomy Evolution:**

- **[COMPREHENSIVE_INFORMATION_TAXONOMY.md](COMPREHENSIVE_INFORMATION_TAXONOMY.md)** - Full taxonomy exploration (16,926 lines)
- **[COMPREHENSIVE_TAXONOMY_MASTER/](COMPREHENSIVE_TAXONOMY_MASTER/)** - Master taxonomy parts (18 files)

### Project Management

- **[PROJECT_TODO.md](../PROJECT_TODO.md)** - Active task tracking
- **[PROGRESS.md](PROGRESS.md)** - Build progress tracker
- **[PHASE_0_SUMMARY.md](PHASE_0_SUMMARY.md)** - Phase 0 completion summary

---

## 🗄️ Archive

### Superseded Documents

**Location:** `docs/archive/superseded-pipeline-docs/` (to be created)

- **QUALITATIVE_PIPELINE_ARCHITECTURE.md** (~1,330 lines)
  **Status:** OBSOLETE
  **Replaced by:** qualitative-pipeline/ (5-part architecture)
  **Reason:** Initial single-file design superseded by comprehensive multi-part documentation

- **QUALITATIVE_SUMMARY.md**
  **Status:** OBSOLETE
  **Replaced by:** qualitative-pipeline/PART_5_DEPLOYMENT_AND_INTEGRATION.md
  **Reason:** Summary file no longer needed; Part 5 contains all deployment details

### Initial Taxonomy Exploration

**Location:** `docs/archive/initial-taxonomy-exploration/` (to be created)

- **taxonomy-analysis/** (~44 PART files)
  **Status:** ARCHIVED
  **Replaced by:** TAXONOMY_OVERVIEW.md + pipeline architectures
  **Reason:** Initial exploratory analysis completed; canonical taxonomy established
  **Note:** Retained for historical reference of design evolution

---

## 📊 Documentation Statistics

- **Total Markdown Files:** 178
- **Canonical Architecture:** ~10,000 lines
  - Qualitative Pipeline: ~5,000 lines
  - Quantitative Pipeline: ~3,100 lines
  - Fusion Model: ~2,200 lines
- **Setup/Reference:** ~5,000 lines
- **Archive:** ~40,000+ lines (historical/exploratory)
- **Active Development Phase:** Phase 0 → Phase 1 transition

---

## 🎯 Reading Order for New Developers

### Quick Start (30 minutes)

1. **[README.md](../README.md)** - What is this project?
2. **[MASTER_PLAN.md](../MASTER_PLAN.md)** - How is it architected?
3. **[TAXONOMY_OVERVIEW.md](../TAXONOMY_OVERVIEW.md)** - What are the 21 categories?

### Architecture Deep Dive (3-4 hours)

4. **Qualitative Pipeline** - Read Parts 1-5 in order
5. **Quantitative Pipeline** - Read Parts 1-3 in order
6. **Fusion Model** - Read architecture, then critical analysis

### Implementation Preparation (1-2 hours)

7. **[GET_STARTED.md](GET_STARTED.md)** - Phase 0 setup checklist
8. **[PROJECT_TODO.md](../PROJECT_TODO.md)** - Current active tasks
9. **Setup Guides** - API keys, environment configuration

### Reference Materials (as needed)

10. **Model Research** - LLM selection rationale
11. **Multi-Agent Patterns** - Orchestration strategies
12. **Taxonomy Master** - Full 16,926-line taxonomy details

---

## 🔄 Maintenance

### Update Schedule

- **After major design decision** → Update DOCS_MANIFEST.md with new canonical document
- **After implementation phase** → Update PROGRESS.md and PROJECT_TODO.md
- **Before phase start** → Review canonical docs for accuracy
- **Weekly** → Check for obsolete/duplicate documents

### Deprecation Process

1. Mark document with `⚠️ DEPRECATED` header at top
2. Add pointer to replacement document
3. Move to `docs/archive/` with explanatory README
4. Update DOCS_MANIFEST.md to reflect change
5. Verify no active references to deprecated file

### Archive Policy

- **Keep:** Historical design decisions, evolution of thinking
- **Delete:** True duplicates, temp files, scratch notes
- **Consolidate:** Scattered setup docs, multiple summaries

---

## 🤖 Copilot Integration

### Best Practices

1. **Reference this manifest** when asking architecture questions
2. **Use specific doc names** in queries: "Based on FUSION_MODEL_ARCHITECTURE.md Part 2..."
3. **Cite canonical sources** when discussing design: "According to qualitative-pipeline/PART_3..."
4. **Link related docs** in conversations: "This relates to Integration Matrix C in Part 4"

### What Copilot Can Access

- ✅ All markdown files in workspace (automatically indexed)
- ✅ Recent conversation context (last ~50 messages)
- ✅ Explicitly mentioned documents (when you reference them)
- ✅ Code files and structure (via semantic search)

### What You DON'T Need

- ❌ COPILOT_CONTEXT.md regeneration (Copilot reads repo directly)
- ❌ Front-matter in all files (Copilot uses semantic understanding)
- ❌ Separate IDEAS.csv or REQUIREMENTS.csv (info is in docs)
- ❌ Background indexing watchers (Copilot indexes on-demand)

### Pro Tips

- **Keep manifest open** in editor when working on architecture
- **Use "Explain this codebase"** to get context-aware answers
- **Reference specific line ranges** when discussing implementation details
- **Ask cross-document questions:** "How does the fusion model integrate with qualitative Part 5?"

---

## 🔍 Finding Information

### By Topic

| What You Need | Where to Find It |
|---------------|------------------|
| **System overview** | MASTER_PLAN.md, README.md |
| **Category definitions** | TAXONOMY_OVERVIEW.md |
| **Qualitative LLM chain** | qualitative-pipeline/PART_3_LLM_CHAIN_AND_SYNTHESIS.md |
| **ML models & features** | quantitative-pipeline/PART_2_FEATURE_ENGINEERING_AND_ML.md |
| **Integration matrices** | qualitative-pipeline/PART_4_INTEGRATION_MATRICES.md |
| **Bayesian fusion logic** | FUSION_MODEL_ARCHITECTURE.md |
| **API setup** | AI_API_FINAL_SUMMARY.md, COPILOT_API_COMPLETE_SUMMARY.md |
| **Multi-agent orchestration** | FINAL_MULTI_AGENT_SOLUTION.md, AI_ORCHESTRATION_ARCHITECTURE.md |
| **Model selection rationale** | MODEL_RESEARCH_2025.md, CHATGPT5_DEEP_RESEARCH_ANALYSIS.md |
| **Current tasks** | PROJECT_TODO.md |
| **Phase 0 completion** | GET_STARTED.md, PHASE_0_SUMMARY.md |

### By Development Phase

| Phase | Key Documents |
|-------|--------------|
| **Phase 0** (Design) | All canonical architecture docs, PHASE_0_SUMMARY.md |
| **Phase 1** (Implementation) | Deployment sections in each pipeline (Part 5 qual, Part 3 quant) |
| **Phase 2** (Integration) | FUSION_MODEL_ARCHITECTURE.md, integration matrices |
| **Phase 3** (Production) | Monitoring, scaling sections in each Part 5/Part 3 |

---

## 📝 Document Status Legend

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| **CANONICAL** | Source of truth for this topic | Use for implementation |
| **CURRENT** | Up-to-date, actively maintained | Safe to reference |
| **REFERENCE** | Background info, not implementation spec | Use for context only |
| **OBSOLETE** | Superseded by newer document | Check replacement |
| **ARCHIVED** | Historical/exploratory, not current | For reference only |
| **IN PROGRESS** | Being actively written/updated | May have gaps |

---

## 🚀 Next Steps (Implementation Roadmap)

### Immediate (This Week)

1. ✅ Create DOCS_MANIFEST.md (this file)
2. 🔄 Archive obsolete taxonomy exploration files
3. 🔄 Archive superseded pipeline documents
4. 🔄 Consolidate setup documentation
5. ⏳ Add status headers to canonical documents
6. ⏳ Update MASTER_PLAN.md with fusion model details

### Near-Term (Next 2 Weeks)

7. ⏳ Create archive/README.md explaining historical docs
8. ⏳ Consolidate scattered setup guides into unified SETUP.md
9. ⏳ Begin Phase 1 implementation (data layer)

### Long-Term (Next Month)

10. ⏳ Generate implementation checklists from pipeline Parts 5/3
11. ⏳ Create integration test specifications
12. ⏳ Document CI/CD pipeline

---

**Last Review:** 2025-11-12
**Next Review:** 2025-11-19 (1 week)
**Maintained By:** Primary development team
**Questions?** Reference this manifest first, then ask in project discussions
