# 🧠 Project Context Directory

**Purpose:** Prevent AI agents from hallucinating about implementation status by providing complete, accurate context.

## 📁 Files in This Directory

### 1. **MASTER_CONTEXT.md** ⭐ Most Important

**What:** Single source of truth for the entire project
**Contains:**

- Complete architecture overview
- Implementation status (verified)
- Design principles and constraints
- Common mistakes to avoid
- Verification protocols
- Current priorities

**When to read:** FIRST, before any analysis or architectural judgment

---

### 2. **project_snapshot.json** 🤖 Automated

**What:** Machine-readable project state
**Contains:**

- File tree (all 286 files)
- Documentation summaries
- Implementation status per component
- Architectural state
- Critical files list
- Current priorities

**When to read:** When you need structured data about implementation status

**How to regenerate:**

```bash
python scripts/generate_project_snapshot.py
```

---

### 3. **AI_AGENT_INSTRUCTIONS.md** 📋 Protocol

**What:** Step-by-step instructions for AI agents
**Contains:**

- Verification protocol
- Confidence level indicators
- DO/DON'T lists
- Current reality summary
- Context management workflows

**When to read:** Before starting any complex task or analysis

---

## 🚨 Why This Directory Exists

### The Problem We Solved

**Before:** AI agents (even Claude Sonnet 4.5) would:

- ❌ Claim we built 60% of system (actually ~10%)
- ❌ Suggest simplifying architecture (it's correct as designed)
- ❌ Assume scrapers work (they return fake data)
- ❌ Miss that qualitative pipeline doesn't exist
- ❌ Hallucinate about fusion model implementation

**Root Cause:** Context starvation

- Local agents only see small file windows
- Cloud agents don't auto-load design docs
- No persistent memory of project state
- Documentation completeness ≠ code completeness

**Solution:** Context Engineering

1. ✅ MASTER_CONTEXT.md - Persistent system summary
2. ✅ project_snapshot.json - Automated status tracking
3. ✅ AI_AGENT_INSTRUCTIONS.md - Verification protocols
4. ✅ VS Code settings - Full workspace indexing
5. ✅ Critical files flagged in settings

---

## 🔄 How to Use This System

### For Humans

**When asking AI for analysis:**

1. Tell agent to read `project_context/MASTER_CONTEXT.md` first
2. Use "Add to Chat" for key architecture docs
3. Prefer Cloud Agent (Sonnet 4.5) for complex tasks
4. Regenerate snapshot after major changes

**Example prompt:**

```
Read project_context/MASTER_CONTEXT.md and
project_context/project_snapshot.json first.

Then analyze [your question here].

Use confidence indicators for all claims.
```

### For AI Agents

**Start every session:**

```python
1. read("project_context/MASTER_CONTEXT.md")
2. read("project_context/project_snapshot.json")
3. understand_current_state()
4. then_respond_to_user()
```

**Before claiming anything is "implemented":**

```python
1. check_master_context()
2. verify_with_source_code()
3. use_confidence_indicators()
4. if_uncertain_say_so()
```

---

## 📊 Current Project State (Auto-Generated)

**Last Snapshot:** November 13, 2025

```json
{
  "documentation": "100% ✅",
  "implementation": "~10% ⚠️",
  "critical_gaps": [
    "Scrapers (0% working - all placeholders)",
    "Qualitative pipeline (0% - doesn't exist)",
    "Fusion model (0% - only docstring)",
    "Database (only ~10 placeholder races)"
  ]
}
```

See `project_snapshot.json` for detailed breakdown.

---

## 🎯 Critical Files AI Should Always Read

As configured in `.vscode/settings.json`:

1. `project_context/MASTER_CONTEXT.md` - Start here
2. `project_context/project_snapshot.json` - Current state
3. `project_context/AI_AGENT_INSTRUCTIONS.md` - Protocol
4. `MASTER_PLAN.md` - System architecture
5. `IMPLEMENTATION_REALITY_CHECK.md` - Reality check
6. `DATA_SOURCE_MAPPING_AND_SCRAPING_ARCHITECTURE.md` - Data sources
7. `docs/FUSION_MODEL_ARCHITECTURE.md` - Fusion specs

---

## 🛠️ Maintenance

### When to Regenerate Snapshot

- After implementing new features
- After major architectural changes
- After populating database with real data
- Weekly during active development

```bash
python scripts/generate_project_snapshot.py
```

### When to Update MASTER_CONTEXT.md

- When implementation status changes significantly
- When priorities shift
- When new critical issues emerge
- When design decisions are made

**Manual edit required - not auto-generated**

---

## 🧪 Verification

To test if context engineering is working:

**Bad Agent Behavior (Before):**

```
Agent: "We've built 60% of the system and the quantitative
        pipeline is production-ready!"
```

**Good Agent Behavior (After):**

```
Agent: "📋 DOCUMENTED: System architecture is complete
        ❌ NOT IMPLEMENTED: Only ~10% working code
        🔍 NEED TO CHECK: Verifying scraper implementation...
        ✅ VERIFIED: Scrapers return placeholder data only"
```

---

## 📝 Summary

This directory exists to give AI agents the **full context** they need to:

1. ✅ Understand what's actually implemented vs documented
2. ✅ Avoid hallucinating about system state
3. ✅ Build exactly as designed in master plan
4. ✅ Use confidence indicators for all claims
5. ✅ Verify before making assertions

**Result:** Accurate, honest, context-aware AI assistance

---

*Created: November 13, 2025*
*Purpose: Eliminate AI agent hallucination through context engineering*
