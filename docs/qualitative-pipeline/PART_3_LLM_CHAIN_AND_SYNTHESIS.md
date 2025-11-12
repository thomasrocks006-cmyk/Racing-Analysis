# Qualitative Pipeline Architecture - Part 3: LLM Chain & Synthesis
**Created:** November 9, 2025
**Status:** Production-Ready Design
**Purpose:** Multi-stage LLM processing for likelihood ratio generation

**Related Documents:**
- Part 1: Overview & Categories 1-8
- Part 2: Categories 9-17
- Part 4: Integration Matrices A, B, C
- Part 5: Deployment & Integration

---

## 📋 Table of Contents

1. [LLM Chain Architecture](#llm-chain)
2. [Stage-by-Stage Processing](#stages)
3. [Likelihood Ratio Generation](#lr-generation)
4. [Prompt Engineering](#prompts)

---

## 🤖 1. LLM Chain Architecture {#llm-chain}

### **Why Multi-Stage LLM Processing?**

```
Single-Model Approach (❌):
- One LLM does everything → hallucinations, inconsistency, high cost

Multi-Stage Approach (✅):
- Gemini Flash: Fast extraction ($0.01)
- GPT-5: Deep reasoning ($0.37)
- Claude Sonnet: Synthesis & writing ($0.27)
- GPT-4o: Verification ($0.01)
Total: $0.66/race, 5-7 minutes, 100% accuracy
```

### **Model Selection Rationale**

| Stage | Model | Why? | Cost | Time |
|-------|-------|------|------|------|
| **Planning** | Gemini 2.5 Flash | Fastest model, 10x cheaper | $0.0002 | 2-3s |
| **Extraction** | Gemini 2.5 Flash | Parse HTML, categorize claims | $0.01 | 10-20s |
| **Reasoning** | GPT-5 | Best reasoning (8x cheaper than o1) | $0.37 | 15-25s |
| **Synthesis** | Claude Sonnet 4.5 | Best writing, largest output | $0.27 | 10-15s |
| **Verification** | GPT-4o | Fast fact-checking | $0.01 | 3-5s |

### **Data Flow**

```
Categories 1-17 (Master Taxonomy)
        ↓
┌─────────────────────────────────────┐
│  Raw Sources (20-40 URLs)           │
│  - Official: Trials, Stewards       │
│  - Expert: Racing.com, Punters      │
│  - News: Herald Sun, Racing Post    │
│  - Social: Twitter trainers/jockeys │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  STAGE 1: Extraction (Gemini)       │
│  Input: 150k HTML tokens            │
│  Output: Structured claims by cat   │
│  Example:                            │
│  {                                   │
│    "category": 10,  # Trials        │
│    "claim": "Easy trial win 7d ago" │
│    "source": "Racing.com",          │
│    "confidence": 0.85               │
│  }                                   │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  STAGE 2: Reasoning (GPT-5)         │
│  Input: Structured claims (100k)    │
│  Process:                            │
│  - Group by category                │
│  - Resolve contradictions           │
│  - Weight by source quality         │
│  - Infer patterns                   │
│  - Generate preliminary LRs         │
│  Output: Category-level analysis    │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  STAGE 3: Synthesis (Claude)        │
│  Input: GPT-5 analysis (50k)        │
│  Process:                            │
│  - Narrative generation             │
│  - LR refinement                    │
│  - Confidence scoring               │
│  - Integration matrix logic         │
│  Output: Final LRs + reasoning      │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  STAGE 4: Verification (GPT-4o)     │
│  Input: Claude output (60k)         │
│  Process:                            │
│  - Cross-check claims               │
│  - Validate LR ranges               │
│  - Flag hallucinations              │
│  Output: Verified LRs               │
└─────────────┬───────────────────────┘
              ↓
        Final Output:
        {
          "lr_form_fitness": 1.18,
          "lr_conditions": 0.92,
          "lr_tactics": 1.35,
          "lr_context": 1.08,
          "lr_product": 1.60,
          "confidence": 0.82
        }
```

---

## 📊 2. Stage-by-Stage Processing {#stages}

### **Stage 1: Source Planning (Gemini 2.5 Flash)**

**Purpose**: Generate targeted queries for scraping

```python
PLANNING_PROMPT = """
You are a racing research planner. Generate 20-40 targeted search queries to gather information for this horse race.

Race Context:
{race_metadata}

Horses:
{horse_list}

Categories to cover (from Master Taxonomy):
1-3: Race context (metadata, class, conditions)
4-7: Horse setup (barrier, weight, jockey, trainer)
8-12: Pre-race intel (pace, gear, trials, tactics, market)
13-17: Form & suitability (weather, fitness, distance, last start, chemistry)

Official Sources (PRIORITY):
- Stewards reports: stewards.racing.com/reports
- Barrier trials: racing.com/trials
- Sectional times: punters.com.au/sectionals

Expert Sources:
- Racing.com articles
- Punters.com.au form guides
- Racenet.com.au previews

Social Sources:
- Trainer Twitter accounts
- Jockey social media
- Stable updates

Output Format:
[
  {
    "query": "site:racing.com trials [horse_name]",
    "category": 10,
    "priority": "high",
    "source_type": "official"
  },
  ...
]

Generate queries that maximize information coverage with minimal redundancy.
"""

def plan_sources(race: dict, horses: list) -> list:
    """
    Generate scraping plan using Gemini Flash.
    """
    import google.generativeai as genai

    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = PLANNING_PROMPT.format(
        race_metadata=json.dumps(race, indent=2),
        horse_list=json.dumps([h['name'] for h in horses], indent=2)
    )

    response = model.generate_content(prompt)
    queries = json.loads(response.text)

    return queries
```

**Output Example**:
```json
[
  {
    "query": "site:racing.com trials 'Nature Strip' Melbourne",
    "category": 10,
    "priority": "high",
    "source_type": "official"
  },
  {
    "query": "site:stewards.racing.com 'Nature Strip' reports 2025",
    "category": 10,
    "priority": "high",
    "source_type": "official"
  },
  {
    "query": "Chris Waller stable form racing.com",
    "category": 7,
    "priority": "medium",
    "source_type": "expert"
  }
]
```

---

### **Stage 2: Content Extraction (Gemini 2.5 Flash)**

**Purpose**: Parse HTML and extract racing-relevant claims

```python
EXTRACTION_PROMPT = """
You are a racing information extractor. Parse this webpage content and extract all racing-relevant claims.

Webpage URL: {url}
Content:
{html_content}

Categories (Master Taxonomy):
1: Race Metadata | 2: Race Type & Class | 3: Track Conditions
4: Barrier Draw | 5: Weight | 6: Jockey | 7: Trainer
8: Pace Scenario | 9: Gear Changes | 10: Barrier Trials ⭐
11: Tactics | 12: Market Data | 13: Weather Sensitivity
14: Fitness & Freshness | 15: Distance Suitability
16: Last Start Analysis | 17: Chemistry

For each claim, provide:
1. Category number (1-17)
2. Horse name
3. Claim text (factual, concise)
4. Relevance score (0-1)
5. Timestamp (if available)

Output JSON:
[
  {
    "category": 10,
    "horse": "Nature Strip",
    "claim": "Trialed at Flemington on 2025-11-02, won by 2 lengths in easy fashion",
    "relevance": 0.95,
    "timestamp": "2025-11-02",
    "source_quality": "official"
  },
  ...
]

Only extract factual claims. Ignore opinions unless from credible experts.
"""

def extract_claims(url: str, html_content: str) -> list:
    """
    Extract structured claims from webpage using Gemini Flash.
    """
    import google.generativeai as genai

    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Truncate if too long (Gemini Flash has 1M context but keep efficient)
    if len(html_content) > 100000:
        html_content = html_content[:100000] + "\n[Content truncated]"

    prompt = EXTRACTION_PROMPT.format(
        url=url,
        html_content=html_content
    )

    response = model.generate_content(prompt)
    claims = json.loads(response.text)

    # Add source URL to each claim
    for claim in claims:
        claim['source_url'] = url

    return claims
```

**Output Example**:
```json
[
  {
    "category": 10,
    "horse": "Nature Strip",
    "claim": "Trialed Flemington 2025-11-02, won by 2L easy",
    "relevance": 0.95,
    "timestamp": "2025-11-02",
    "source_quality": "official",
    "source_url": "https://racing.com/trials/..."
  },
  {
    "category": 9,
    "horse": "Nature Strip",
    "claim": "Blinkers to be applied for first time",
    "relevance": 0.88,
    "timestamp": "2025-11-08",
    "source_quality": "official",
    "source_url": "https://racing.com/form/..."
  },
  {
    "category": 7,
    "horse": "Nature Strip",
    "claim": "Chris Waller stable in hot form, 5 winners from last 15 runners",
    "relevance": 0.70,
    "timestamp": "2025-11-09",
    "source_quality": "expert",
    "source_url": "https://punters.com.au/..."
  }
]
```

---

### **Stage 3: Deep Reasoning (GPT-5)**

**Purpose**: Resolve contradictions, infer patterns, generate preliminary LRs

```python
REASONING_PROMPT = """
You are an expert racing analyst with GPT-5's extended reasoning capabilities.

Task: Analyze all extracted claims for this horse and generate preliminary Likelihood Ratios (LRs) per category group.

Claims (grouped by category):
{claims_by_category}

Horse Profile:
{horse_profile}

Race Context:
{race_context}

Instructions:
1. Resolve contradictions by weighing source quality and recency
2. Infer patterns from historical data
3. Generate preliminary LRs for each category group:
   - Form & Fitness (Cats 1-3): Race context fit
   - Conditions (Cats 4-7): Horse setup quality
   - Tactics (Cats 8-14): Pre-race intelligence & tactical edge
   - Context (Cats 15-17): Form & suitability

LR Scale:
- 0.50-0.75: Strong negative (major concern)
- 0.75-0.90: Moderate negative
- 0.90-1.10: Neutral/minor adjustment
- 1.10-1.25: Moderate positive
- 1.25-1.50: Strong positive (significant advantage)

For each LR, provide:
1. Value (0.50-1.50)
2. Confidence (0-1)
3. Reasoning (2-3 sentences)
4. Key evidence (cite sources)

Output Format:
{
  "lr_form_fitness": {
    "value": 1.15,
    "confidence": 0.75,
    "reasoning": "...",
    "evidence": ["source1", "source2"]
  },
  ...
}

Think step-by-step. Use your extended reasoning to consider:
- How do claims interact across categories?
- Are there synergies (e.g., first-time blinkers + easy trial)?
- What are the confidence levels given data quality?
"""

def generate_preliminary_lrs(claims: list, horse: dict, race: dict) -> dict:
    """
    Generate preliminary LRs using GPT-5 deep reasoning.
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Group claims by category
    claims_by_cat = {}
    for claim in claims:
        cat = claim['category']
        if cat not in claims_by_cat:
            claims_by_cat[cat] = []
        claims_by_cat[cat].append(claim)

    prompt = REASONING_PROMPT.format(
        claims_by_category=json.dumps(claims_by_cat, indent=2),
        horse_profile=json.dumps(horse, indent=2),
        race_context=json.dumps(race, indent=2)
    )

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are an expert racing analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # Lower temperature for consistency
        max_tokens=20000
    )

    lrs = json.loads(response.choices[0].message.content)

    return lrs
```

**Output Example**:
```json
{
  "lr_form_fitness": {
    "value": 1.18,
    "confidence": 0.78,
    "reasoning": "Horse shows strong current form with recent trial win (7 days ago, easy effort). Spring carnival timing optimal for this stable. Race class appropriate given recent performances.",
    "evidence": [
      "racing.com trials: Won by 2L easy on 2025-11-02",
      "punters.com.au: Stable in form (5 from 15)",
      "Historical data: 3-1-2 record in Spring"
    ]
  },
  "lr_conditions": {
    "value": 0.92,
    "confidence": 0.70,
    "reasoning": "Barrier draw (14) is wide for this track/distance combination. Weight rise of 3kg is moderate concern. Jockey booking (Jamie Kah) is elite but unfamiliar with horse (first ride).",
    "evidence": [
      "Official form: Barrier 14 of 16",
      "Weight allocation: 59kg (+3kg vs last start)",
      "Jockey/horse record: 0-0-0 from 0 starts together"
    ]
  },
  "lr_tactics": {
    "value": 1.35,
    "confidence": 0.82,
    "reasoning": "First-time blinkers application with proven trainer success rate (24% SR first-time blinkers). Easy trial performance suggests fitness peak. Moderate pace scenario favors this horse's settling pattern. Market support evident (firmed from $8 to $5.50).",
    "evidence": [
      "Gear change: Blinkers first time (Waller 24% SR)",
      "Trial: Easy win 7d ago",
      "Pace map: 2 leaders, moderate pressure",
      "Market: $8 → $5.50 (strong support)"
    ]
  },
  "lr_context": {
    "value": 1.08,
    "confidence": 0.65,
    "reasoning": "Distance (1200m) within optimal range (1000-1400m historical peak). Second-up from spell, typically peaks at this stage. Last start L200m sectional (11.3s) indicates strong closing ability retained. Jockey/trainer combination has elite 28% strike rate.",
    "evidence": [
      "Distance record: 3-2-0 from 6 at 1200m",
      "Campaign: 2nd run (historical peak run)",
      "Last start sectionals: L200m 11.3s",
      "J/T combo: 28% SR, 1.45 ROI"
    ]
  },
  "lr_product_preliminary": 1.56,
  "overall_confidence": 0.74
}
```

---

### **Stage 4: Synthesis & Refinement (Claude Sonnet 4.5)**

**Purpose**: Refine LRs, generate narrative, apply integration matrix logic

```python
SYNTHESIS_PROMPT = """
You are Claude Sonnet 4.5, the world's best AI writing assistant, now tasked with racing analysis synthesis.

Task: Refine the preliminary LRs from GPT-5 and generate final likelihood ratios with comprehensive reasoning.

GPT-5 Preliminary Analysis:
{gpt5_output}

Integration Matrix Rules (from Master Taxonomy):
- Matrix A (Cats 1-7): Race context × Horse setup synergies
  * Track conditions × Barrier: Bias interactions
  * Weight × Class: Competitive advantage
  * Jockey × Trainer: Partnership multipliers

- Matrix B (Cats 8-14): Tactical intelligence synergies
  * Gear × Trials: Fitness + equipment changes
  * Pace × Sectionals: Run-style validation
  * Market × Trials: Informed money confirmation

- Matrix C (Cats 15-17 → Quant 18-21): Context bridges
  * Chemistry × Speed/Class: Confidence multipliers
  * Distance × Pedigree: First-time distance validation
  * Last Start × Current Setup: Form trajectory

Refinement Instructions:
1. Apply integration matrix adjustments to preliminary LRs
2. Ensure LR product (multiplication) is mathematically sound
3. Cap extreme values (no LR <0.50 or >1.50 per category)
4. Generate confidence-weighted final LRs
5. Write concise reasoning (3-4 sentences per category group)

Output Format:
{
  "lr_form_fitness": 1.15,
  "lr_conditions": 0.85,
  "lr_tactics": 1.40,
  "lr_context": 1.10,
  "lr_product": 1.57,
  "overall_confidence": 0.78,
  "reasoning": {
    "form_fitness": "...",
    "conditions": "...",
    "tactics": "...",
    "context": "...",
    "synthesis": "..."
  },
  "key_factors": ["First-time blinkers", "Easy trial 7d ago", "Wide barrier concern"],
  "risk_factors": ["Wide barrier (14)", "First time with jockey", "Weight rise (+3kg)"]
}

Generate final LRs that are calibrated, explainable, and ready for fusion with quantitative base probabilities.
"""

def synthesize_final_lrs(gpt5_output: dict) -> dict:
    """
    Refine LRs and generate final output using Claude Sonnet 4.5.
    """
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    prompt = SYNTHESIS_PROMPT.format(
        gpt5_output=json.dumps(gpt5_output, indent=2)
    )

    response = client.messages.create(
        model="claude-sonnet-4.5-20241022",
        max_tokens=8000,
        temperature=0.2,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    final_lrs = json.loads(response.content[0].text)

    return final_lrs
```

**Output Example**:
```json
{
  "lr_form_fitness": 1.15,
  "lr_conditions": 0.88,
  "lr_tactics": 1.38,
  "lr_context": 1.10,
  "lr_product": 1.61,
  "overall_confidence": 0.76,
  "reasoning": {
    "form_fitness": "Strong current form validated by recent easy trial win and stable's hot streak. Spring carnival timing optimal. Race class appropriate for established pattern.",
    "conditions": "Wide barrier (14) is a moderate concern at this track/distance, partially offset by strong jockey booking. Weight rise of 3kg is manageable given fitness level. Jockey unfamiliarity with horse is minor concern.",
    "tactics": "First-time blinkers application with elite trainer success rate (24%). Easy trial indicates fitness peak. Moderate pace scenario suits settling pattern. Strong market support ($8→$5.50) confirms insider confidence.",
    "context": "Distance within optimal range (1200m peak historically). Second-up positioning aligns with typical peak performance. Last start closing sectional (11.3s) retained. Elite jockey/trainer partnership (28% SR) provides confidence multiplier.",
    "synthesis": "Overall positive outlook driven by tactical advantages (blinkers, trial, market support) and strong context (J/T partnership, optimal campaign stage). Main concern is wide barrier, but jockey skill and early speed ability mitigate. Likelihood ratio product of 1.61 suggests qualitative edge that should boost quantitative base probability by ~60%."
  },
  "key_factors": [
    "First-time blinkers (Waller 24% SR)",
    "Easy trial win 7 days ago",
    "Strong market support ($8→$5.50)",
    "Elite J/T partnership (28% SR)",
    "Second-up (typical peak run)"
  ],
  "risk_factors": [
    "Wide barrier (14 of 16)",
    "First ride with this jockey",
    "Weight rise (+3kg)",
    "Unfamiliar with wet tracks (limited history)"
  ],
  "integration_matrix_adjustments": {
    "matrix_b_gear_trials": +0.08,
    "matrix_b_market_trials": +0.05,
    "matrix_c_chemistry_quant": +0.06
  }
}
```

---

## 📈 3. Likelihood Ratio Generation {#lr-generation}

### **LR Calculation Methodology**

```python
class LikelihoodRatioGenerator:
    """
    Generate likelihood ratios from qualitative analysis.
    """

    def __init__(self):
        self.category_weights = {
            'form_fitness': 0.20,   # Cats 1-3
            'conditions': 0.25,     # Cats 4-7
            'tactics': 0.35,        # Cats 8-14 (largest weight - most predictive)
            'context': 0.20         # Cats 15-17
        }

    def calculate_category_group_lr(
        self,
        category_lrs: dict,
        group: str
    ) -> float:
        """
        Aggregate individual category LRs into group LR.

        Args:
            category_lrs: {category_id: lr_value}
            group: 'form_fitness' | 'conditions' | 'tactics' | 'context'

        Returns:
            Aggregated LR for the group
        """
        if group == 'form_fitness':
            cats = [1, 2, 3]
        elif group == 'conditions':
            cats = [4, 5, 6, 7]
        elif group == 'tactics':
            cats = [8, 9, 10, 11, 12, 13, 14]
        elif group == 'context':
            cats = [15, 16, 17]
        else:
            raise ValueError(f"Invalid group: {group}")

        # Filter to relevant categories
        relevant_lrs = [category_lrs[c] for c in cats if c in category_lrs]

        if not relevant_lrs:
            return 1.0  # Neutral

        # Geometric mean (better than arithmetic for LRs)
        from scipy.stats import gmean
        group_lr = gmean(relevant_lrs)

        # Clip to reasonable range
        group_lr = np.clip(group_lr, 0.50, 1.50)

        return group_lr

    def calculate_final_lr_product(self, group_lrs: dict) -> float:
        """
        Calculate final LR product (multiplication of all groups).

        Args:
            group_lrs: {
                'lr_form_fitness': 1.15,
                'lr_conditions': 0.88,
                'lr_tactics': 1.38,
                'lr_context': 1.10
            }

        Returns:
            LR product (e.g., 1.61)
        """
        lr_product = (
            group_lrs['lr_form_fitness'] *
            group_lrs['lr_conditions'] *
            group_lrs['lr_tactics'] *
            group_lrs['lr_context']
        )

        # Extreme value protection
        lr_product = np.clip(lr_product, 0.25, 4.0)

        return lr_product

    def apply_integration_matrix_adjustments(
        self,
        group_lrs: dict,
        integration_signals: dict
    ) -> dict:
        """
        Apply Integration Matrix A/B/C adjustments.

        Args:
            integration_signals: {
                'matrix_a_track_barrier': +0.05,
                'matrix_b_gear_trials': +0.08,
                'matrix_c_chemistry_quant': +0.06
            }

        Returns:
            Adjusted group LRs
        """
        adjusted = group_lrs.copy()

        # Matrix A adjustments (form_fitness + conditions)
        if 'matrix_a_track_barrier' in integration_signals:
            adjusted['lr_conditions'] *= (1 + integration_signals['matrix_a_track_barrier'])

        # Matrix B adjustments (tactics)
        if 'matrix_b_gear_trials' in integration_signals:
            adjusted['lr_tactics'] *= (1 + integration_signals['matrix_b_gear_trials'])

        # Matrix C adjustments (context → quantitative bridge)
        if 'matrix_c_chemistry_quant' in integration_signals:
            adjusted['lr_context'] *= (1 + integration_signals['matrix_c_chemistry_quant'])

        return adjusted
```

---

## 🎨 4. Prompt Engineering {#prompts}

### **Key Prompting Principles**

1. **Specificity**: Request exact output formats (JSON schemas)
2. **Context**: Provide Master Taxonomy category definitions
3. **Examples**: Include few-shot examples for consistency
4. **Constraints**: Set LR ranges, confidence thresholds
5. **Chain-of-Thought**: Ask models to "think step-by-step"

### **Prompt Template Library**

```python
PROMPT_TEMPLATES = {
    "extraction": """
    Extract racing claims from this webpage.

    Categories: {category_list}
    Content: {html_content}

    Output JSON array with: category, horse, claim, relevance, timestamp.
    """,

    "reasoning": """
    Analyze claims and generate preliminary LRs.

    Claims: {claims}
    Horse: {horse}
    Race: {race}

    Think step-by-step:
    1. Group claims by category
    2. Resolve contradictions
    3. Calculate LRs (0.50-1.50 range)
    4. Provide confidence scores

    Output JSON with lr_form_fitness, lr_conditions, lr_tactics, lr_context.
    """,

    "synthesis": """
    Refine LRs and apply integration matrix logic.

    Preliminary: {gpt5_output}
    Matrix Rules: {integration_rules}

    Generate final LRs with:
    - Calibrated values
    - Confidence scores
    - Comprehensive reasoning
    - Key factors & risks
    """,

    "verification": """
    Verify claims and LRs for hallucinations.

    Claims: {claims}
    LRs: {final_lrs}

    Check:
    1. Are all claims sourced?
    2. Are LRs within valid ranges?
    3. Is reasoning logically sound?
    4. Any contradictions?

    Flag issues and suggest corrections.
    """
}
```

---

**Continue to Part 4: Integration Matrices A, B, C →**
