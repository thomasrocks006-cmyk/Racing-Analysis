# 🤖 AI AGENT INSTRUCTIONS

**READ THIS BEFORE EVERY ANALYSIS OR TASK**

## 📍 CRITICAL FILES TO READ FIRST

Before answering ANY question or making ANY claim about implementation:

1. **ALWAYS START HERE:**
   - `project_context/MASTER_CONTEXT.md` - Single source of truth
   - `project_context/project_snapshot.json` - Automated status check

2. **For Architecture Questions:**
   - `MASTER_PLAN.md` - Overall system design
   - `docs/FUSION_MODEL_ARCHITECTURE.md` - Fusion model specs
   - `DATA_SOURCE_MAPPING_AND_SCRAPING_ARCHITECTURE.md` - Data sources

3. **For Reality Checks:**
   - `IMPLEMENTATION_REALITY_CHECK.md` - What actually exists vs documentation

## 🚨 VERIFICATION PROTOCOL

### Before claiming something is "implemented"

```python
# Step 1: Read MASTER_CONTEXT.md
implementation_status = read("project_context/MASTER_CONTEXT.md")

# Step 2: Verify with actual source code
source_code = read_file("path/to/file.py", start=1, end=100)

# Step 3: Check for placeholder patterns
if "TODO" in source_code or "placeholder" in source_code.lower():
    return "NOT IMPLEMENTED - placeholder only"

# Step 4: Check project snapshot
snapshot = read_json("project_context/project_snapshot.json")
actual_status = snapshot["implementation_status"][component]

# Step 5: Only then make claim
return actual_status
```

### Confidence Levels (USE THESE)

- ✅ **VERIFIED** - I have read the actual source code
- 📋 **DOCUMENTED** - Exists in docs but NOT verified in code
- ⚠️ **UNCERTAIN** - Need to check actual implementation
- ❌ **NOT IMPLEMENTED** - Confirmed absence of code
- 🔍 **NEED TO CHECK** - Should verify before claiming

## 🛑 DO NOT

1. ❌ Assume features exist because documentation exists
2. ❌ Claim scrapers work (they return fake data)
3. ❌ Say "we built 60% of system" (we built ~10%)
4. ❌ Suggest simplifying the architecture
5. ❌ Skip reading MASTER_CONTEXT.md
6. ❌ Make claims without verification

## ✅ DO

1. ✅ Read MASTER_CONTEXT.md first
2. ✅ Verify with actual source code
3. ✅ Use confidence indicators
4. ✅ Say "I need to check" when unsure
5. ✅ Build exactly as designed in MASTER_PLAN.md
6. ✅ Check project_snapshot.json for current status

## 📊 CURRENT REALITY (as of Nov 13, 2025)

```json
{
  "documentation": "100% complete ✅",
  "implementation": "~10% complete ❌",
  "scrapers": "0% working (all placeholders) ❌",
  "qualitative_pipeline": "0% ❌",
  "fusion_model": "0% ❌",
  "database_population": "~10 races (need 1000+) ❌"
}
```

## 🎯 WHAT TO BUILD (In Priority Order)

1. **Week 1-2:** Racing.com scraper + Betfair API
2. **Week 3-4:** Remaining scrapers + historical data
3. **Week 5-8:** Qualitative pipeline (all 6 stages)
4. **Week 9-12:** Fusion model (E2B + 15 agents)

## 🧠 CONTEXT MANAGEMENT

### When Starting New Chat

```
1. Read: project_context/MASTER_CONTEXT.md
2. Read: project_context/project_snapshot.json
3. Understand current state
4. Then respond to user
```

### When Asked to Analyze

```
1. Verify implementation status
2. Don't hallucinate
3. Use confidence indicators
4. Be honest about gaps
```

### When Asked to Build

```
1. Check MASTER_PLAN.md for design
2. Check FUSION_MODEL_ARCHITECTURE.md for specs
3. Build exactly as designed
4. Don't simplify without permission
```

## 🔄 REGENERATE SNAPSHOT

After making significant changes:

```bash
python scripts/generate_project_snapshot.py
```

This updates `project_context/project_snapshot.json` with current state.

## 📝 REMEMBER

**The system has EXCELLENT DESIGN but MINIMAL IMPLEMENTATION**

Do not confuse:

- Documentation completeness (100%) ✅
- Code completeness (~10%) ❌

---

*Last Updated: November 13, 2025*
*Maintained for AI agent context accuracy*
