# Comprehensive Model Research & Capabilities Analysis

**Date**: November 8, 2025
**Purpose**: Deep dive into ALL available models in GitHub Copilot and comparison with ChatGPT Deep Research
**Status**: Research Phase - Critical for Pipeline Design

---

## 📊 Executive Summary

**Key Findings**:
1. **GitHub Copilot** provides access to multiple frontier models through VS Code LM API
2. **Latest ChatGPT** capabilities need verification (GPT-5/o-series rumored but need confirmation)
3. **Model selection strategy** must be based on task-specific benchmarks
4. **Quality target** must be set against CURRENT ChatGPT Deep Research performance

---

## 🤖 1. Models Available in GitHub Copilot (November 2025)

### **1.1 Confirmed Available Models**

Based on GitHub Copilot documentation and VS Code Language Model API:

#### **A. OpenAI Models**

| Model | Version | Context Window | Capabilities | Best For |
|-------|---------|----------------|--------------|----------|
| **GPT-4o** | 2024-11-20 | 128k tokens | - Strong reasoning<br>- Structured output<br>- Vision capable | General purpose, synthesis |
| **GPT-4o-mini** | 2024-07-18 | 128k tokens | - Fast, efficient<br>- Good for simple tasks | Planning, verification |
| **o1-preview** | 2024-09-12 | 128k tokens | - Advanced reasoning<br>- Chain-of-thought<br>- Math/logic focus | Complex reasoning, analysis |
| **o1-mini** | 2024-09-12 | 128k tokens | - Faster than o1<br>- Still strong reasoning | Efficient reasoning tasks |

**Status**: Need to verify if **GPT-5** or newer o-series models are available

**Key Capabilities**:
- ✅ Function calling / Tool use
- ✅ Structured JSON output
- ✅ Multi-turn conversations
- ✅ Long context (128k tokens)
- ⚠️ o1 models have different pricing/speed trade-offs

#### **B. Anthropic Models**

| Model | Version | Context Window | Capabilities | Best For |
|-------|---------|----------------|--------------|----------|
| **Claude 3.5 Sonnet** | 2024-06-20 | 200k tokens | - Excellent structured output<br>- Strong coding<br>- Good reasoning | Extraction, parsing, coding |
| **Claude 3 Opus** | 2024-02-29 | 200k tokens | - Highest capability<br>- Complex reasoning<br>- Creative tasks | Advanced analysis |
| **Claude 3 Sonnet** | 2024-02-29 | 200k tokens | - Balanced performance<br>- Good speed | General tasks |
| **Claude 3 Haiku** | 2024-03-07 | 200k tokens | - Fastest<br>- Most efficient | Quick tasks, high volume |

**Status**: Need to verify if **Claude 4.5 Sonnet** or **Claude 3.7** (rumored) are available

**Key Capabilities**:
- ✅ Best-in-class structured output (JSON, XML)
- ✅ Excellent at following complex instructions
- ✅ Strong at parsing/extraction tasks
- ✅ 200k context (more than GPT-4o)
- ✅ Constitutional AI (safer, more aligned)

#### **C. Google Models**

| Model | Version | Context Window | Capabilities | Best For |
|-------|---------|----------------|--------------|----------|
| **Gemini 2.0 Flash** | 2024-12-?? | 1M tokens | - Fastest inference<br>- Multimodal<br>- Large context | High-volume, real-time |
| **Gemini 1.5 Pro** | 2024-05-14 | 2M tokens | - Largest context<br>- Strong reasoning<br>- Multimodal | Long documents, analysis |
| **Gemini 1.5 Flash** | 2024-05-14 | 1M tokens | - Fast and efficient<br>- Good performance | General tasks |

**Status**: Verify latest Gemini 2.0 series availability and capabilities

**Key Capabilities**:
- ✅ Massive context windows (1-2M tokens)
- ✅ Native multimodal (text, images, video, audio)
- ✅ Fast inference (Flash models)
- ✅ Competitive performance
- ⚠️ Less known about racing-specific capabilities

---

## 🔍 2. Model Capability Matrix (Racing Analysis Tasks)

### **2.1 Task-Specific Performance Estimates**

Based on general benchmarks and task characteristics:

| Task | GPT-4o | o1-preview | Claude 3.5 Sonnet | Claude Opus | Gemini 2.0 Flash | Winner |
|------|--------|------------|-------------------|-------------|------------------|---------|
| **Structured Data Extraction** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **Claude** |
| **Web Content Parsing** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **Claude** |
| **Reasoning & Synthesis** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **o1/Opus** |
| **Contradiction Resolution** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **o1/GPT-4o** |
| **Pattern Recognition** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **o1** |
| **JSON Output Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **Claude** |
| **Speed (Inference)** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **Gemini Flash** |
| **Cost Efficiency** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | **Gemini/Claude** |
| **Context Length** | 128k | 128k | 200k | 200k | 1M | **Gemini** |
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **Tie** |

### **2.2 Racing-Specific Capability Assessment**

| Capability | Required Level | GPT-4o | o1 | Claude 3.5 | Gemini Flash | Notes |
|------------|----------------|--------|-----|------------|--------------|-------|
| **Parse Stewards Reports** | High | ✅ | ✅ | ✅✅ | ✅ | Claude best at structured extraction |
| **Extract Gear Changes** | High | ✅ | ✅ | ✅✅ | ✅ | Need exact field matching |
| **Analyze Trainer Comments** | Very High | ✅✅ | ✅✅ | ✅ | ✅ | Subtle meaning, needs reasoning |
| **Detect Track Bias** | Very High | ✅ | ✅✅ | ✅ | ✅ | Pattern recognition critical |
| **Resolve Contradictions** | Critical | ✅✅ | ✅✅✅ | ✅ | ✅ | o1 excels at multi-step reasoning |
| **Synthesize Intelligence** | Critical | ✅✅ | ✅✅✅ | ✅✅ | ✅ | Need coherent narrative |
| **Assess Source Quality** | High | ✅ | ✅✅ | ✅ | ✅ | Judgment-based task |
| **Generate Search Queries** | Medium | ✅ | ✅ | ✅ | ✅✅ | Fast generation helpful |
| **Handle Racing Jargon** | High | ✅ | ✅ | ✅ | ✅ | All models struggle without context |

---

## 🏆 3. ChatGPT Deep Research Benchmark (2025)

### **3.1 Current ChatGPT Deep Research Architecture**

**CRITICAL**: Need to verify which model powers Deep Research as of Nov 2025

**Possibilities**:
1. **GPT-5** (if released) - Expected major improvement
2. **o1** or **o3** (reasoning-focused) - Better for complex analysis
3. **GPT-4o** (latest version) - Incremental improvements
4. **Hybrid approach** - Different models per stage

**Expected Capabilities (based on evolution)**:
```
ChatGPT Deep Research (Nov 2025):
├─ Model: GPT-5 or o1/o3 (assumption - NEEDS VERIFICATION)
├─ Context: 128k-200k tokens
├─ Process: Multi-round iterative search (3-5+ rounds)
├─ Sources: 40-100+ web searches
├─ Time: 5-20 minutes (faster than 2024 version)
├─ Quality: Estimated 92-96% (improvement from 90-93%)
└─ Cost: $3-10 per query (may have decreased)
```

### **3.2 Performance Estimates** (Need Validation)

| Metric | 2024 Baseline | 2025 Expected | Evidence Needed |
|--------|---------------|---------------|-----------------|
| **Accuracy** | 90-93% | 92-96% | Real-world tests |
| **Source Coverage** | 30-100 | 40-120+ | Check recent outputs |
| **Time** | 10-30 min | 5-20 min | Measure actual |
| **Contradiction Resolution** | Good | Excellent | Test complex cases |
| **Racing Domain Knowledge** | General | ??? | Test on racing queries |

### **3.3 What We DON'T Know** (Critical Gaps)

❓ **Unknown Factors**:
1. Which model actually powers Deep Research?
2. Has the search strategy improved (more sophisticated query generation)?
3. Does it have racing-specific training data?
4. What's the actual quality on racing analysis tasks?
5. Has cost/speed improved with newer models?
6. Does it use multiple models in ensemble?

**ACTION REQUIRED**: Test ChatGPT Deep Research on racing queries to establish REAL baseline

---

## 📐 4. Optimal Model Selection Strategy

### **4.1 Recommended Pipeline Architecture**

Based on capabilities analysis:

```python
PIPELINE_MODEL_CONFIG = {
    "stage_1_planning": {
        "primary": "gpt-4o-mini",  # Fast planning
        "reasoning": "Fast, cheap, good at generating search strategies",
        "fallback": "gemini-2.0-flash",
        "copilot_requests": 1
    },

    "stage_2_scraping": {
        "method": "Traditional HTTP/Selenium",
        "reasoning": "No LLM needed for raw fetching",
        "copilot_requests": 0
    },

    "stage_3_extraction": {
        "primary": "claude-3.5-sonnet",  # Best structured extraction
        "reasoning": "Superior JSON output, excellent at parsing complex HTML/text",
        "fallback": "claude-3-opus",
        "batch_size": 5,  # Process 5 sources per request
        "copilot_requests": 8-12  # 40-60 sources / 5 per batch
    },

    "stage_4_synthesis_round_1": {
        "primary": "o1-preview",  # Advanced reasoning
        "reasoning": "Best at complex reasoning, pattern recognition, contradictions",
        "fallback": "gpt-4o",
        "copilot_requests": 1
    },

    "stage_4_synthesis_round_2": {
        "primary": "o1-preview",  # Iterative refinement
        "reasoning": "Second pass to catch gaps, resolve remaining contradictions",
        "fallback": "gpt-4o",
        "copilot_requests": 1,
        "conditional": "Only if confidence < 0.90 or contradictions remain"
    },

    "stage_5_verification": {
        "primary": "gpt-4o-mini",  # Fast fact-checking
        "reasoning": "Quick verification of critical claims",
        "fallback": "gemini-2.0-flash",
        "copilot_requests": 1
    },

    "stage_6_quality_assessment": {
        "primary": "o1-mini",  # Efficient reasoning
        "reasoning": "Assess overall quality, confidence calibration",
        "fallback": "gpt-4o-mini",
        "copilot_requests": 1
    }
}

# Total requests per race: 13-17 (within Copilot budget)
# Estimated time: 5-10 minutes (quality-first approach)
# Target quality: ≥95% (match or exceed ChatGPT Deep Research)
```

### **4.2 Model Selection Rationale**

**Why Multiple Models?**
1. **Task-Specific Optimization**: Each model has strengths
2. **Cost Efficiency**: Use expensive models only where needed
3. **Speed**: Fast models for simple tasks, powerful for complex
4. **Robustness**: Fallback options if primary unavailable

**Why Claude for Extraction?**
- Best structured output (JSON parsing)
- Excellent at handling messy HTML/text
- Strong instruction following
- 200k context (can handle long pages)

**Why o1 for Synthesis?**
- Advanced reasoning capabilities
- Better at multi-step logic
- Excellent contradiction resolution
- Worth the extra time for quality

**Why GPT-4o-mini for Planning/Verification?**
- Fast enough for simple tasks
- Good at generating queries
- Cheap (within Copilot limits)
- Reliable for verification checks

---

## 🎯 5. Quality Target Calibration

### **5.1 Establishing Baseline** (Action Required)

**Test Protocol**:
```
1. Select 10 representative races (mix of conditions)
2. Run ChatGPT Deep Research on each
3. Manually verify accuracy of claims
4. Calculate metrics:
   • Precision: % of claims that are accurate
   • Recall: % of important facts captured
   • F1 Score: Harmonic mean
   • Source quality: Tier distribution
   • Time taken: Actual runtime

5. Establish OUR target:
   • Must match or exceed ChatGPT precision
   • Must match or exceed ChatGPT recall
   • Can be slightly slower (5-10 min acceptable)
   • Must provide full source citations
```

### **5.2 Provisional Quality Targets**

Until we have real benchmarks:

| Metric | Conservative Target | Stretch Target |
|--------|---------------------|----------------|
| **Precision** | ≥90% | ≥95% |
| **Recall** | ≥85% | ≥92% |
| **F1 Score** | ≥87% | ≥93% |
| **Source Coverage** | 40-60 sources | 60-80+ sources |
| **Time** | 5-10 min | 3-7 min |
| **Copilot Requests** | 13-17 | 10-15 (optimized) |

### **5.3 Success Criteria**

Our pipeline is "good enough" when:
- ✅ **Precision ≥ ChatGPT** (no false positives)
- ✅ **Recall ≥ 90% of ChatGPT** (catch most important facts)
- ✅ **Time ≤ 2x ChatGPT** (if ChatGPT takes 10 min, we take ≤20 min)
- ✅ **Full provenance** (source URLs for every claim)
- ✅ **Confidence calibration** (when we say 95%, it's accurate 95% of time)

---

## 🔄 6. Comparison: Our Pipeline vs ChatGPT Deep Research

### **6.1 Head-to-Head (Projected)**

| Feature | ChatGPT Deep Research | Our Pipeline | Advantage |
|---------|----------------------|--------------|-----------|
| **Model** | GPT-5/o-series (assumed) | Multi-model (o1, Claude, GPT-4o) | ⚠️ Depends on actual ChatGPT model |
| **Quality** | 92-96% (projected) | ≥95% (target) | 🟰 **Aim for parity** |
| **Speed** | 5-20 min (projected) | 5-10 min | ✅ **Ours (potentially)** |
| **Cost** | $3-10 | $0 (Copilot) | ✅ **Ours** |
| **Sources** | 40-120+ | 40-60+ (expandable) | ⚠️ ChatGPT (more breadth) |
| **Racing-Specific** | General | Optimized for racing | ✅ **Ours** |
| **Transparency** | Limited | Full audit trail | ✅ **Ours** |
| **Customization** | None | Full control | ✅ **Ours** |
| **Iterations** | 3-5+ rounds | 2-3 rounds (configurable) | ⚠️ ChatGPT (more thorough) |

### **6.2 Critical Unknowns**

We CANNOT definitively compare until we:
1. ✅ Verify which model ChatGPT Deep Research uses
2. ✅ Test ChatGPT on racing-specific queries
3. ✅ Measure actual quality, speed, coverage
4. ✅ Build our pipeline and test on same queries
5. ✅ Compare results head-to-head

---

## 📋 7. Action Items (Prioritized)

### **Immediate (This Week)**

1. ✅ **Test ChatGPT Deep Research** on 5 racing queries
   - Measure quality, time, source count
   - Establish real baseline
   - Document model used (if disclosed)

2. ✅ **Verify Copilot Model Availability**
   - Check if GPT-5, o3, Claude 4.5 available
   - Test each model on sample racing extraction task
   - Benchmark performance

3. ✅ **Design Multi-Model Pipeline**
   - Optimal model per stage
   - Request budget calculation
   - Fallback strategies

### **Next Steps (After Baseline Established)**

4. ✅ **Rewrite Qualitative Pipeline Doc**
   - Correct model references
   - Single quality tier (no "standard" mode)
   - Iterative refinement strategy
   - ≥95% quality target

5. ✅ **Design Intelligent Search Strategy**
   - Fixed sources (always checked)
   - Agent-driven discovery
   - Search query generation
   - Source prioritization

6. ✅ **Build Prototype**
   - Implement Stage 3 (extraction) with Claude
   - Test on 10 sample sources
   - Measure accuracy

---

## ❓ 8. Outstanding Questions

### **Critical Questions (Must Answer Before Building)**

1. **What model does ChatGPT Deep Research actually use?**
   - GPT-5? o1? o3? Hybrid?
   - How do we find out?

2. **What is its REAL performance on racing queries?**
   - Need empirical testing, not assumptions

3. **Which models are available in Copilot RIGHT NOW?**
   - Can we access o1? o3? GPT-5?
   - What about Claude 4.5 or 3.7?

4. **What's the request limit strategy?**
   - 1500/month = ~13 requests/race = ~115 races/month
   - Is this enough? Need daily volume estimate

5. **Should we use OpenAI API as fallback?**
   - If Copilot limits hit, switch to paid API?
   - What's the cost threshold?

### **Design Questions (Affect Architecture)**

6. **How many iteration rounds?**
   - 2 rounds? 3 rounds? Adaptive based on confidence?

7. **Source count target?**
   - 40? 60? 80? Balance breadth vs depth

8. **Acceptable runtime?**
   - User wants quality, but 20 min might be too slow
   - Target: 5-10 min? 10-15 min?

9. **Caching strategy?**
   - Cache source content for 24h?
   - Cache analysis for 6h?

10. **Quality threshold for iteration?**
    - If first round confidence > 0.90, skip second round?
    - Or always do 2+ rounds for consistency?

---

## 🎯 9. Next Immediate Action

**TO PROCEED WITH PIPELINE DESIGN, WE MUST:**

### **Step 1: Verify Model Availability** (15 minutes)
Test in Copilot Chat:
```
Prompt: "What language model are you currently using?
        Are o1-preview, Claude 3.5 Sonnet, and Gemini 2.0 Flash available?"
```

### **Step 2: Test ChatGPT Deep Research** (2 hours)
Run on 3 racing queries:
1. "Research HORSE X in RACE Y at TRACK Z on DATE"
2. Measure: time, sources, quality, model disclosed
3. Calculate baseline metrics

### **Step 3: Make Architecture Decisions** (1 hour)
Based on findings:
- Confirm model selection per stage
- Set quality targets (based on real ChatGPT performance)
- Determine iteration strategy
- Calculate request budget

### **Step 4: Rewrite Pipeline Document** (3 hours)
- Correct model references
- Single quality tier
- Intelligent search strategy
- ≥95% target (or higher if ChatGPT exceeds)

---

## 📊 Summary Table: Model Recommendations by Task

| Pipeline Stage | Primary Model | Why | Backup | Requests |
|----------------|---------------|-----|---------|----------|
| Planning | GPT-4o-mini | Fast, cheap planning | Gemini Flash | 1 |
| Scraping | HTTP/Selenium | No LLM needed | - | 0 |
| Extraction | Claude 3.5 Sonnet | Best structured output | Claude Opus | 8-12 |
| Synthesis (R1) | o1-preview | Advanced reasoning | GPT-4o | 1 |
| Synthesis (R2) | o1-preview | Iterative refinement | GPT-4o | 1 |
| Verification | GPT-4o-mini | Fast fact-check | Gemini Flash | 1 |
| Quality Check | o1-mini | Efficient reasoning | GPT-4o-mini | 1 |
| **TOTAL** | **Multi-model** | **Task-optimized** | - | **13-17** |

**Budget**: 1500 requests/month ÷ 15 requests/race = **100 races/month** sustainable

---

**Status**: ⏳ Awaiting model verification and ChatGPT baseline testing
**Next Action**: Test Copilot models + ChatGPT Deep Research
**Blocker**: Cannot finalize architecture without knowing available models and real ChatGPT performance
**Owner**: thomasrocks006-cmyk
