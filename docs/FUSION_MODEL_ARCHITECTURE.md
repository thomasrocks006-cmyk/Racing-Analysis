# Fusion Model Architecture - Concurrent Multi-Agent Bayesian Integration

**Created:** November 10, 2025
**Status:** Production-Ready Design
**Purpose:** Bayesian fusion of qualitative LRs + quantitative probabilities with concurrent agent execution

**Related Documents:**

- Qualitative Pipeline (Parts 1-5)
- Quantitative Pipeline (Parts 1-3)
- MASTER_PLAN.md
- FINAL_MULTI_AGENT_SOLUTION.md

---

## 📋 Table of Contents

1. [Fusion Model Overview](#overview)
2. [Concurrent Agent Architecture](#concurrent-agents)
3. [Bayesian Likelihood Ratio Theory](#bayesian-theory)
4. [Integration Algorithms](#integration)
5. [Implementation](#implementation)
6. [Performance & Optimization](#performance)

---

## 🎯 1. Fusion Model Overview {#overview}

### **The Problem**

We have two independent pipelines producing different output types:

**Qualitative Pipeline** (Categories 1-17):

- Output: Likelihood Ratios (LRs) per category group
- Example: `lr_form_fitness=1.18, lr_conditions=0.92, lr_tactics=1.35, lr_context=1.08`
- Combined: `lr_product = 1.18 × 0.92 × 1.35 × 1.08 = 1.60`
- Represents: "This horse is 60% MORE likely to win than we initially thought"

**Quantitative Pipeline** (Categories 18-21):

- Output: Base win/place probabilities from ML models
- Example: `win_prob_base = 0.18` (18% chance of winning)
- Represents: "Based on numerical data, this horse has 18% chance"

**The Goal:**
Combine these using Bayesian likelihood ratios to produce final calibrated probabilities.

### **Why Bayesian Fusion?**

```
Prior Probability (Quantitative) + New Evidence (Qualitative) = Posterior Probability (Fused)

P(win|all_evidence) = P(win|quant_features) × LR(qual_evidence) / normalization_constant

Example:
- Base probability: 18%
- Qualitative LR: 1.60 (60% boost)
- Fused probability: 18% × 1.60 = 28.8% (before normalization)
```

### **Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONCURRENT FUSION ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────┐         ┌──────────────────────┐            │
│  │  QUALITATIVE PIPELINE │         │ QUANTITATIVE PIPELINE │            │
│  │  (Categories 1-17)    │         │  (Categories 18-21)   │            │
│  │                       │         │                       │            │
│  │  • 5-7 min runtime    │         │  • 10-30s runtime     │            │
│  │  • $0.62/race cost    │         │  • <$0.01/race cost   │            │
│  │  • LR output          │         │  • Probability output │            │
│  └───────────┬───────────┘         └───────────┬───────────┘            │
│              │                                  │                        │
│              └────────────┬─────────────────────┘                        │
│                           ▼                                              │
│              ┌────────────────────────────┐                              │
│              │   CONCURRENT FUSION LAYER   │                             │
│              │   (E2B + OpenHands)         │                             │
│              │                             │                             │
│              │  ┌─────────────────────┐   │                             │
│              │  │   E2B Fork Manager   │   │                             │
│              │  │   - Fork 15 agents   │   │                             │
│              │  │   - Parallel compute │   │                             │
│              │  │   - Result synthesis │   │                             │
│              │  └─────────┬───────────┘   │                             │
│              │            │               │                             │
│              │            ▼               │                             │
│              │  ┌─────────────────────┐   │                             │
│              │  │ OpenHands Micro-Agents│  │                             │
│              │  │                     │   │                             │
│              │  │  1. BayesianUpdater │   │                             │
│              │  │  2. FieldNormalizer │   │                             │
│              │  │  3. CalibrationAgent│   │                             │
│              │  │  4. UncertaintyQuant│   │                             │
│              │  │  5. ProvenanceTracker│  │                             │
│              │  │  6. MatrixIntegrator │   │                             │
│              │  │  7. EdgeCalculator  │   │                             │
│              │  │  8. ConfidenceScorer│   │                             │
│              │  │  9. ConflictResolver│   │                             │
│              │  │ 10. OutlierDetector │   │                             │
│              │  │ 11. ConsensusBuilder│   │                             │
│              │  │ 12. ValidationAgent │   │                             │
│              │  │ 13. ExplanationGen  │   │                             │
│              │  │ 14. MonitoringAgent │   │                             │
│              │  │ 15. SynthesisAgent  │   │                             │
│              │  └─────────┬───────────┘   │                             │
│              │            │               │                             │
│              └────────────┼───────────────┘                             │
│                           ▼                                              │
│              ┌────────────────────────────┐                              │
│              │   FUSED PREDICTIONS        │                              │
│              │                            │                              │
│              │  • Final win/place probs   │                              │
│              │  • Confidence intervals    │                              │
│              │  • Edge vs market          │                              │
│              │  • Full provenance         │                              │
│              │  • Explainable reasoning   │                              │
│              └────────────────────────────┘                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔀 2. Concurrent Agent Architecture {#concurrent-agents}

### **Why Concurrent Agents?**

**Problem with Sequential Processing:**

- Qualitative pipeline: 5-7 minutes
- Quantitative pipeline: 10-30 seconds
- Fusion processing: 5-10 seconds per approach
- Total sequential: 6+ minutes per race

**Solution with Concurrent Agents:**

- Fork 15 micro-agents in parallel
- Each tries different fusion approach
- Synthesize best results
- Total concurrent: 7-8 minutes (pipelines + parallel fusion)

### **E2B Forking Capability**

```python
from e2b import Sandbox

class E2BForkManager:
    """
    Manage parallel agent execution using E2B's forking capability.

    E2B allows creating multiple sandbox instances (forks) that run
    identical code with different parameters in parallel.
    """

    def __init__(self, max_forks: int = 15):
        self.max_forks = max_forks
        self.sandboxes = []

    async def fork_agents(
        self,
        qual_output: dict,
        quant_output: dict,
        num_agents: int = 15
    ) -> List[dict]:
        """
        Fork multiple agents to try different fusion approaches in parallel.

        Args:
            qual_output: Qualitative pipeline output (LRs)
            quant_output: Quantitative pipeline output (base probs)
            num_agents: Number of parallel agents (15 recommended)

        Returns:
            List of fusion results from each agent
        """
        tasks = []

        # Create agent tasks with different strategies
        agent_strategies = self._generate_strategies(num_agents)

        # Fork sandboxes for each agent
        for i, strategy in enumerate(agent_strategies):
            sandbox = Sandbox(template="python")
            self.sandboxes.append(sandbox)

            # Each sandbox runs fusion with different strategy
            task = self._run_fusion_in_sandbox(
                sandbox,
                qual_output,
                quant_output,
                strategy,
                agent_id=i
            )
            tasks.append(task)

        # Execute all in parallel
        results = await asyncio.gather(*tasks)

        # Clean up sandboxes
        await self._cleanup_sandboxes()

        return results

    def _generate_strategies(self, num_agents: int) -> List[dict]:
        """
        Generate diverse fusion strategies for each agent.

        Agent 1-3: Different LR weighting schemes
        Agent 4-6: Different calibration methods
        Agent 7-9: Different normalization approaches
        Agent 10-12: Different uncertainty quantification
        Agent 13-15: Different confidence scoring
        """
        strategies = []

        # Agents 1-3: LR weighting variations
        strategies.append({
            'name': 'BayesianUpdater_Conservative',
            'lr_weight': 0.8,  # Conservative: reduce LR impact
            'calibration': 'isotonic',
            'normalization': 'softmax'
        })
        strategies.append({
            'name': 'BayesianUpdater_Aggressive',
            'lr_weight': 1.2,  # Aggressive: amplify LR impact
            'calibration': 'isotonic',
            'normalization': 'softmax'
        })
        strategies.append({
            'name': 'BayesianUpdater_Balanced',
            'lr_weight': 1.0,  # Standard Bayesian
            'calibration': 'isotonic',
            'normalization': 'softmax'
        })

        # Agents 4-6: Calibration variations
        strategies.append({
            'name': 'CalibrationAgent_Isotonic',
            'lr_weight': 1.0,
            'calibration': 'isotonic',  # Track-specific isotonic
            'normalization': 'softmax'
        })
        strategies.append({
            'name': 'CalibrationAgent_Temperature',
            'lr_weight': 1.0,
            'calibration': 'temperature',  # Global temperature scaling
            'normalization': 'softmax'
        })
        strategies.append({
            'name': 'CalibrationAgent_Platt',
            'lr_weight': 1.0,
            'calibration': 'platt',  # Platt scaling (logistic)
            'normalization': 'softmax'
        })

        # Agents 7-9: Normalization variations
        strategies.append({
            'name': 'FieldNormalizer_Softmax',
            'lr_weight': 1.0,
            'calibration': 'isotonic',
            'normalization': 'softmax',  # Standard softmax
            'temperature': 1.0
        })
        strategies.append({
            'name': 'FieldNormalizer_HardNorm',
            'lr_weight': 1.0,
            'calibration': 'isotonic',
            'normalization': 'hard',  # Simple division normalization
        })
        strategies.append({
            'name': 'FieldNormalizer_TemperatureSoftmax',
            'lr_weight': 1.0,
            'calibration': 'isotonic',
            'normalization': 'softmax',
            'temperature': 1.5  # Higher temp = more uniform probs
        })

        # Agents 10-12: Uncertainty quantification
        strategies.append({
            'name': 'UncertaintyQuant_Conformal',
            'lr_weight': 1.0,
            'calibration': 'isotonic',
            'normalization': 'softmax',
            'uncertainty': 'conformal',  # Conformal prediction sets
            'coverage': 0.90
        })
        strategies.append({
            'name': 'UncertaintyQuant_Bootstrapped',
            'lr_weight': 1.0,
            'calibration': 'isotonic',
            'normalization': 'softmax',
            'uncertainty': 'bootstrap',  # Bootstrap confidence intervals
            'n_bootstrap': 1000
        })
        strategies.append({
            'name': 'UncertaintyQuant_BayesianCredible',
            'lr_weight': 1.0,
            'calibration': 'isotonic',
            'normalization': 'softmax',
            'uncertainty': 'bayesian',  # Bayesian credible intervals
            'prior': 'jeffrey'
        })

        # Agents 13-15: Matrix integration & synthesis
        strategies.append({
            'name': 'MatrixIntegrator_Conservative',
            'lr_weight': 1.0,
            'calibration': 'isotonic',
            'normalization': 'softmax',
            'matrix_c_weight': 0.8,  # Reduce Matrix C impact
        })
        strategies.append({
            'name': 'MatrixIntegrator_Aggressive',
            'lr_weight': 1.0,
            'calibration': 'isotonic',
            'normalization': 'softmax',
            'matrix_c_weight': 1.2,  # Amplify Matrix C impact
        })
        strategies.append({
            'name': 'SynthesisAgent_Ensemble',
            'lr_weight': 1.0,
            'calibration': 'ensemble',  # Average of isotonic + temperature
            'normalization': 'softmax',
            'ensemble_weights': [0.6, 0.4]  # 60% isotonic, 40% temp
        })

        return strategies[:num_agents]

    async def _run_fusion_in_sandbox(
        self,
        sandbox: Sandbox,
        qual_output: dict,
        quant_output: dict,
        strategy: dict,
        agent_id: int
    ) -> dict:
        """
        Run fusion algorithm in isolated sandbox with specific strategy.
        """
        # Upload fusion code to sandbox
        fusion_code = self._generate_fusion_code(strategy)
        await sandbox.filesystem.write("/fusion.py", fusion_code)

        # Upload data
        import json
        await sandbox.filesystem.write(
            "/qual_data.json",
            json.dumps(qual_output)
        )
        await sandbox.filesystem.write(
            "/quant_data.json",
            json.dumps(quant_output)
        )

        # Execute fusion
        result = await sandbox.process.start_and_wait(
            "python /fusion.py"
        )

        # Parse output
        output = json.loads(result.stdout)
        output['agent_id'] = agent_id
        output['strategy'] = strategy['name']

        return output

    async def _cleanup_sandboxes(self):
        """Close all sandboxes."""
        for sandbox in self.sandboxes:
            await sandbox.close()
        self.sandboxes = []
```

### **OpenHands Micro-Agent Framework**

```python
from openhands import Agent, AgentConfig, Workspace

class OpenHandsMicroAgentOrchestrator:
    """
    Orchestrate 15 specialized micro-agents using OpenHands framework.

    OpenHands provides:
    - Agent coordination primitives
    - Message passing between agents
    - Shared workspace for data exchange
    - Result aggregation
    """

    def __init__(self):
        self.workspace = Workspace()
        self.agents = []
        self._initialize_agents()

    def _initialize_agents(self):
        """Create 15 specialized micro-agents."""

        # Agent 1: BayesianUpdater
        self.agents.append(Agent(
            name="BayesianUpdater",
            config=AgentConfig(
                instruction="""
                Apply Bayesian likelihood ratio update:
                1. Convert base_prob to odds: base_odds = p / (1-p)
                2. Apply LR: updated_odds = base_odds × lr_product
                3. Convert back: fused_prob = updated_odds / (1 + updated_odds)
                """,
                expertise="bayesian_statistics"
            )
        ))

        # Agent 2: FieldNormalizer
        self.agents.append(Agent(
            name="FieldNormalizer",
            config=AgentConfig(
                instruction="""
                Normalize probabilities across field:
                1. Sum all horse probabilities
                2. If sum != 1.0, divide each by sum
                3. Handle edge cases (scratched horses)
                """,
                expertise="probability_normalization"
            )
        ))

        # Agent 3: CalibrationAgent
        self.agents.append(Agent(
            name="CalibrationAgent",
            config=AgentConfig(
                instruction="""
                Apply calibration curves:
                1. Load track-specific isotonic calibration
                2. Apply to fused probabilities
                3. Validate calibration quality (ECE)
                """,
                expertise="model_calibration"
            )
        ))

        # Agent 4: UncertaintyQuantifier
        self.agents.append(Agent(
            name="UncertaintyQuantifier",
            config=AgentConfig(
                instruction="""
                Compute confidence intervals:
                1. Conformal prediction sets (90% coverage)
                2. Combine qual + quant uncertainties
                3. Compute prediction intervals
                """,
                expertise="uncertainty_quantification"
            )
        ))

        # Agent 5: ProvenanceTracker
        self.agents.append(Agent(
            name="ProvenanceTracker",
            config=AgentConfig(
                instruction="""
                Track full provenance chain:
                1. Qualitative sources (URLs, claims)
                2. Quantitative features (importance scores)
                3. Fusion parameters (LR weights, calibration)
                """,
                expertise="data_lineage"
            )
        ))

        # Agent 6: MatrixIntegrator
        self.agents.append(Agent(
            name="MatrixIntegrator",
            config=AgentConfig(
                instruction="""
                Apply Integration Matrix C adjustments:
                1. Extract chemistry_quantitative multiplier
                2. Extract distance_pedigree adjustment
                3. Extract weather_pedigree_going adjustment
                4. Apply to fused probability
                """,
                expertise="matrix_operations"
            )
        ))

        # Agent 7: EdgeCalculator
        self.agents.append(Agent(
            name="EdgeCalculator",
            config=AgentConfig(
                instruction="""
                Calculate edge vs market:
                1. Get Betfair/TAB market odds
                2. Convert to implied probabilities
                3. Calculate edge: (our_prob - market_prob) / market_prob
                4. Identify value opportunities
                """,
                expertise="market_analysis"
            )
        ))

        # Agent 8: ConfidenceScorer
        self.agents.append(Agent(
            name="ConfidenceScorer",
            config=AgentConfig(
                instruction="""
                Score overall confidence:
                1. Qualitative confidence (source quality)
                2. Quantitative confidence (model uncertainty)
                3. Agreement score (qual vs quant alignment)
                4. Final confidence: weighted average
                """,
                expertise="confidence_estimation"
            )
        ))

        # Agent 9: ConflictResolver
        self.agents.append(Agent(
            name="ConflictResolver",
            config=AgentConfig(
                instruction="""
                Resolve qual-quant conflicts:
                1. Detect large disagreements (LR far from 1.0)
                2. Investigate root causes
                3. Weight based on confidence
                4. Generate explanation
                """,
                expertise="conflict_resolution"
            )
        ))

        # Agent 10: OutlierDetector
        self.agents.append(Agent(
            name="OutlierDetector",
            config=AgentConfig(
                instruction="""
                Detect anomalous predictions:
                1. Check if fused_prob >> base_prob (LR > 2.5)
                2. Check if fused_prob << base_prob (LR < 0.4)
                3. Flag for manual review
                4. Log anomaly details
                """,
                expertise="anomaly_detection"
            )
        ))

        # Agent 11: ConsensusBuilder
        self.agents.append(Agent(
            name="ConsensusBuilder",
            config=AgentConfig(
                instruction="""
                Build consensus across agents:
                1. Collect results from all 15 agents
                2. Weight by confidence scores
                3. Compute weighted average
                4. Detect outlier agents
                """,
                expertise="ensemble_methods"
            )
        ))

        # Agent 12: ValidationAgent
        self.agents.append(Agent(
            name="ValidationAgent",
            config=AgentConfig(
                instruction="""
                Validate fusion output:
                1. Check probabilities sum to 1.0
                2. Check all probs in [0, 1]
                3. Check LR product in [0.25, 4.0]
                4. Verify provenance completeness
                """,
                expertise="data_validation"
            )
        ))

        # Agent 13: ExplanationGenerator
        self.agents.append(Agent(
            name="ExplanationGenerator",
            config=AgentConfig(
                instruction="""
                Generate human-readable explanation:
                1. Summarize key drivers (top 3 qual factors)
                2. Summarize key features (top 5 quant features)
                3. Explain fusion logic
                4. Provide confidence rationale
                """,
                expertise="natural_language_generation"
            )
        ))

        # Agent 14: MonitoringAgent
        self.agents.append(Agent(
            name="MonitoringAgent",
            config=AgentConfig(
                instruction="""
                Monitor fusion performance:
                1. Track processing time
                2. Track API costs
                3. Log errors/warnings
                4. Update performance metrics
                """,
                expertise="system_monitoring"
            )
        ))

        # Agent 15: SynthesisAgent
        self.agents.append(Agent(
            name="SynthesisAgent",
            config=AgentConfig(
                instruction="""
                Synthesize final output:
                1. Aggregate results from agents 1-14
                2. Select best fusion result
                3. Combine uncertainty estimates
                4. Package final prediction
                """,
                expertise="result_synthesis"
            )
        ))

    async def run_concurrent_fusion(
        self,
        qual_output: dict,
        quant_output: dict
    ) -> dict:
        """
        Run all 15 agents in parallel, synthesize results.
        """
        # Store inputs in shared workspace
        self.workspace.write("qual_output.json", qual_output)
        self.workspace.write("quant_output.json", quant_output)

        # Run agents in parallel
        tasks = []
        for agent in self.agents:
            task = agent.run(workspace=self.workspace)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # SynthesisAgent aggregates all results
        synthesis_agent = self.agents[-1]  # Agent 15
        final_output = await synthesis_agent.synthesize(results)

        return final_output
```

---

## 📐 3. Bayesian Likelihood Ratio Theory {#bayesian-theory}

### **Mathematical Foundation**

**Bayes' Theorem:**

```
P(A|B) = P(B|A) × P(A) / P(B)

In our context:
P(win|qual_evidence) = P(qual_evidence|win) × P(win) / P(qual_evidence)

Simplified using Likelihood Ratios:
Posterior Odds = Prior Odds × Likelihood Ratio

Where:
- Prior Odds = P(win) / P(not_win)  [from quantitative pipeline]
- Likelihood Ratio = P(qual_evidence|win) / P(qual_evidence|not_win)  [from qualitative pipeline]
- Posterior Odds = P(win|qual_evidence) / P(not_win|qual_evidence)  [final fused result]
```

**Converting Between Probabilities and Odds:**

```python
def prob_to_odds(p: float) -> float:
    """Convert probability to odds."""
    return p / (1 - p)

def odds_to_prob(odds: float) -> float:
    """Convert odds to probability."""
    return odds / (1 + odds)
```

**Example Calculation:**

```python
# Step 1: Quantitative base probability
base_prob = 0.18  # 18% win chance

# Step 2: Convert to odds
base_odds = 0.18 / (1 - 0.18) = 0.18 / 0.82 = 0.2195

# Step 3: Qualitative Likelihood Ratio
lr_product = 1.60  # 60% boost from qualitative evidence

# Step 4: Apply Bayesian update
posterior_odds = base_odds × lr_product = 0.2195 × 1.60 = 0.3512

# Step 5: Convert back to probability
posterior_prob = posterior_odds / (1 + posterior_odds)
              = 0.3512 / (1 + 0.3512)
              = 0.3512 / 1.3512
              = 0.260  # 26% win chance (after fusion)

# Result: Base 18% → Fused 26% (8 percentage point increase)
```

### **Why This Works**

1. **Quantitative pipeline** gives us a "base rate" (prior probability) based on historical patterns
2. **Qualitative pipeline** gives us "new evidence" (likelihood ratio) based on current race context
3. **Bayesian fusion** mathematically combines them, weighting by reliability
4. **Field normalization** ensures all horse probabilities sum to 100%

### **LR Interpretation Guide**

| LR Range | Interpretation | Effect on 20% Base Prob |
|----------|----------------|------------------------|
| 0.25 | Very strong negative | 20% → 5.6% |
| 0.50 | Strong negative | 20% → 11.1% |
| 0.75 | Moderate negative | 20% → 16.0% |
| 1.00 | Neutral (no change) | 20% → 20.0% |
| 1.25 | Moderate positive | 20% → 23.8% |
| 1.50 | Strong positive | 20% → 27.3% |
| 2.00 | Very strong positive | 20% → 33.3% |
| 4.00 | Extreme positive | 20% → 50.0% |

---

## 🔧 4. Integration Algorithms {#integration}

### **Algorithm 1: Basic Bayesian Fusion**

```python
def bayesian_fusion_basic(
    base_prob: float,
    lr_product: float
) -> float:
    """
    Basic Bayesian likelihood ratio fusion.

    Args:
        base_prob: Quantitative base probability (0-1)
        lr_product: Qualitative likelihood ratio (0.25-4.0)

    Returns:
        Fused probability (0-1)
    """
    # Convert to odds
    base_odds = base_prob / (1 - base_prob)

    # Apply LR
    posterior_odds = base_odds * lr_product

    # Convert back to probability
    posterior_prob = posterior_odds / (1 + posterior_odds)

    return posterior_prob
```

### **Algorithm 2: Matrix C Enhanced Fusion**

```python
def bayesian_fusion_with_matrix_c(
    base_prob: float,
    lr_product: float,
    chemistry_multiplier: float,
    distance_adjustment: float,
    weather_adjustment: float
) -> float:
    """
    Bayesian fusion with Integration Matrix C adjustments.

    Matrix C provides three types of qual → quant bridges:
    1. Chemistry × Quantitative: Confidence multiplier (0.90-1.15)
    2. Distance × Pedigree: Suitability adjustment (-0.08 to +0.10)
    3. Weather × Pedigree × Going: Condition adjustment (-0.12 to +0.08)
    """
    # Step 1: Apply chemistry multiplier to LR
    adjusted_lr = lr_product * chemistry_multiplier

    # Step 2: Basic Bayesian fusion
    base_odds = base_prob / (1 - base_prob)
    posterior_odds = base_odds * adjusted_lr
    posterior_prob = posterior_odds / (1 + posterior_odds)

    # Step 3: Apply additive adjustments from Matrix C
    total_adjustment = distance_adjustment + weather_adjustment
    adjusted_prob = posterior_prob * (1 + total_adjustment)

    # Step 4: Clip to valid range
    adjusted_prob = max(0.01, min(0.99, adjusted_prob))

    return adjusted_prob
```

### **Algorithm 3: Field Normalization**

```python
def normalize_field(
    horse_probs: List[float],
    method: str = "softmax",
    temperature: float = 1.0
) -> List[float]:
    """
    Normalize probabilities across field to sum to 1.0.

    Args:
        horse_probs: Raw fused probabilities per horse
        method: "softmax", "hard", or "temperature"
        temperature: Softmax temperature (higher = more uniform)

    Returns:
        Normalized probabilities summing to 1.0
    """
    import numpy as np

    if method == "hard":
        # Simple division normalization
        total = sum(horse_probs)
        return [p / total for p in horse_probs]

    elif method == "softmax":
        # Softmax normalization (differentiable, smoother)
        log_probs = [np.log(p) / temperature for p in horse_probs]
        exp_probs = [np.exp(lp) for lp in log_probs]
        total = sum(exp_probs)
        return [ep / total for ep in exp_probs]

    elif method == "temperature":
        # Temperature-scaled hard normalization
        scaled_probs = [p ** (1/temperature) for p in horse_probs]
        total = sum(scaled_probs)
        return [sp / total for sp in scaled_probs]

    else:
        raise ValueError(f"Unknown normalization method: {method}")
```

### **Algorithm 4: Calibration Application**

```python
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
import pickle

class FusionCalibrator:
    """
    Apply calibration to fused probabilities.

    Trained on historical predictions vs actual outcomes.
    """

    def __init__(self, track_group: str):
        """
        Load calibration curves for track group.

        Track groups:
        - "metro": Flemington, Randwick, Caulfield
        - "provincial": Sandown, Rosehill
        - "country": All others
        """
        self.track_group = track_group
        self.isotonic = self._load_isotonic_calibrator()
        self.temperature = self._load_temperature_calibrator()

    def _load_isotonic_calibrator(self) -> IsotonicRegression:
        """Load pre-trained isotonic regression."""
        path = f"models/calibration/isotonic_{self.track_group}.pkl"
        with open(path, 'rb') as f:
            return pickle.load(f)

    def _load_temperature_calibrator(self) -> dict:
        """Load temperature scaling parameters."""
        path = f"models/calibration/temperature_{self.track_group}.pkl"
        with open(path, 'rb') as f:
            return pickle.load(f)

    def calibrate(
        self,
        raw_probs: List[float],
        method: str = "isotonic"
    ) -> List[float]:
        """
        Apply calibration to raw fused probabilities.

        Args:
            raw_probs: Uncalibrated probabilities
            method: "isotonic", "temperature", or "ensemble"

        Returns:
            Calibrated probabilities
        """
        import numpy as np

        if method == "isotonic":
            # Isotonic regression (non-parametric, track-specific)
            return self.isotonic.predict(np.array(raw_probs))

        elif method == "temperature":
            # Temperature scaling (global parameter)
            temp = self.temperature['temperature']
            log_probs = np.log(np.array(raw_probs)) / temp
            exp_probs = np.exp(log_probs)
            return exp_probs / exp_probs.sum()

        elif method == "ensemble":
            # Weighted ensemble of isotonic + temperature
            iso_probs = self.isotonic.predict(np.array(raw_probs))
            temp_probs = self.calibrate(raw_probs, method="temperature")

            # Weight: 70% isotonic, 30% temperature (tunable)
            return 0.7 * iso_probs + 0.3 * temp_probs

        else:
            raise ValueError(f"Unknown calibration method: {method}")
```

### **Algorithm 5: Uncertainty Quantification**

```python
from mapie.regression import MapieRegressor
from mapie.classification import MapieClassifier
import numpy as np

class FusionUncertaintyQuantifier:
    """
    Compute confidence intervals for fused predictions.

    Uses conformal prediction for distribution-free guarantees.
    """

    def __init__(self, coverage: float = 0.90):
        """
        Initialize with target coverage level.

        Args:
            coverage: Desired coverage (e.g., 0.90 = 90% confidence)
        """
        self.coverage = coverage
        self.mapie_clf = None

    def fit(self, X_cal: np.ndarray, y_cal: np.ndarray):
        """
        Fit conformal predictor on calibration set.

        Args:
            X_cal: Calibration features (fused_probs)
            y_cal: Calibration targets (actual outcomes)
        """
        from sklearn.ensemble import RandomForestClassifier

        # Base classifier
        base_clf = RandomForestClassifier(n_estimators=100)

        # Wrap with MAPIE for conformal prediction
        self.mapie_clf = MapieClassifier(
            estimator=base_clf,
            method="score",
            cv="prefit"
        )

        self.mapie_clf.fit(X_cal, y_cal)

    def predict_with_intervals(
        self,
        fused_probs: List[float]
    ) -> dict:
        """
        Predict with confidence intervals.

        Returns:
            {
                'point_estimate': float,
                'lower_bound': float,
                'upper_bound': float,
                'prediction_set': List[int]  # Possible outcomes
            }
        """
        X = np.array(fused_probs).reshape(1, -1)

        # Conformal prediction
        y_pred, y_pis = self.mapie_clf.predict(
            X,
            alpha=1 - self.coverage
        )

        # Extract intervals
        lower = y_pis[0, 0, 0]
        upper = y_pis[0, 1, 0]

        return {
            'point_estimate': float(y_pred[0]),
            'lower_bound': float(lower),
            'upper_bound': float(upper),
            'prediction_set': list(y_pis[0, :, :].flatten()),
            'coverage': self.coverage
        }
```

---

## 💻 5. Implementation {#implementation}

### **Complete Fusion Pipeline**

```python
import asyncio
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class FusionOutput:
    """Final fused prediction output."""
    race_id: str
    horse_id: str
    horse_name: str

    # Probabilities
    win_prob_base: float  # From quantitative
    win_prob_fused: float  # After Bayesian fusion
    win_prob_calibrated: float  # After calibration
    place_prob_base: float
    place_prob_fused: float
    place_prob_calibrated: float

    # Confidence intervals
    win_prob_lower: float
    win_prob_upper: float
    place_prob_lower: float
    place_prob_upper: float

    # Fair odds
    win_fair_odds: float
    place_fair_odds: float

    # Market comparison
    betfair_win_odds: float
    betfair_place_odds: float
    win_edge: float  # (our_prob - market_prob) / market_prob
    place_edge: float

    # Provenance
    qualitative_lr: float
    qualitative_confidence: float
    quantitative_confidence: float
    matrix_c_chemistry: float
    matrix_c_distance: float
    matrix_c_weather: float

    # Explanation
    key_qualitative_factors: List[str]
    key_quantitative_features: List[str]
    fusion_reasoning: str
    confidence_rationale: str

    # Metadata
    processing_time_seconds: float
    total_cost_dollars: float
    consensus_score: float  # Agreement across 15 agents
    outlier_detected: bool


class ConcurrentFusionModel:
    """
    Production fusion model with concurrent agent execution.

    Combines:
    - E2B forking for parallel agent execution
    - OpenHands micro-agents for specialized tasks
    - Bayesian likelihood ratio integration
    - Conformal uncertainty quantification
    """

    def __init__(
        self,
        use_e2b: bool = True,
        use_openhands: bool = True,
        num_agents: int = 15
    ):
        self.use_e2b = use_e2b
        self.use_openhands = use_openhands
        self.num_agents = num_agents

        # Initialize managers
        if use_e2b:
            self.e2b_manager = E2BForkManager(max_forks=num_agents)

        if use_openhands:
            self.openhands_orchestrator = OpenHandsMicroAgentOrchestrator()

        # Load calibrators
        self.calibrators = {
            'metro': FusionCalibrator('metro'),
            'provincial': FusionCalibrator('provincial'),
            'country': FusionCalibrator('country')
        }

        # Initialize uncertainty quantifier
        self.uncertainty_quantifier = FusionUncertaintyQuantifier(coverage=0.90)

    async def fuse_race(
        self,
        race: dict,
        qual_outputs: List[dict],
        quant_outputs: List[dict],
        market_data: dict
    ) -> List[FusionOutput]:
        """
        Fuse qualitative + quantitative predictions for entire race.

        Args:
            race: Race metadata (track, distance, going, etc.)
            qual_outputs: Qualitative pipeline outputs (one per horse)
            quant_outputs: Quantitative pipeline outputs (one per horse)
            market_data: Betfair/TAB market prices

        Returns:
            List of FusionOutput (one per horse)
        """
        fusion_results = []

        # Process each horse in parallel
        tasks = []
        for qual, quant in zip(qual_outputs, quant_outputs):
            task = self._fuse_horse(
                race=race,
                qual_output=qual,
                quant_output=quant,
                market_data=market_data
            )
            tasks.append(task)

        horse_results = await asyncio.gather(*tasks)

        # Field normalization (across all horses)
        win_probs = [r['win_prob_fused'] for r in horse_results]
        place_probs = [r['place_prob_fused'] for r in horse_results]

        win_probs_normalized = normalize_field(win_probs, method="softmax")
        place_probs_normalized = normalize_field(place_probs, method="softmax")

        # Update each horse with normalized probabilities
        for i, result in enumerate(horse_results):
            result['win_prob_fused'] = win_probs_normalized[i]
            result['place_prob_fused'] = place_probs_normalized[i]

            # Apply calibration
            track_group = self._get_track_group(race['track'])
            calibrator = self.calibrators[track_group]

            result['win_prob_calibrated'] = calibrator.calibrate(
                [result['win_prob_fused']],
                method="ensemble"
            )[0]
            result['place_prob_calibrated'] = calibrator.calibrate(
                [result['place_prob_fused']],
                method="ensemble"
            )[0]

            # Create FusionOutput
            fusion_output = FusionOutput(**result)
            fusion_results.append(fusion_output)

        return fusion_results

    async def _fuse_horse(
        self,
        race: dict,
        qual_output: dict,
        quant_output: dict,
        market_data: dict
    ) -> dict:
        """
        Fuse predictions for single horse using concurrent agents.
        """
        import time
        start_time = time.time()

        # Option 1: E2B Forking (parallel sandbox execution)
        if self.use_e2b:
            agent_results = await self.e2b_manager.fork_agents(
                qual_output,
                quant_output,
                num_agents=self.num_agents
            )

        # Option 2: OpenHands Micro-Agents (coordinated execution)
        elif self.use_openhands:
            agent_results = await self.openhands_orchestrator.run_concurrent_fusion(
                qual_output,
                quant_output
            )

        # Option 3: Sequential (fallback)
        else:
            agent_results = [self._sequential_fusion(qual_output, quant_output)]

        # Synthesize results from all agents
        synthesized = self._synthesize_agent_results(agent_results)

        # Calculate edge vs market
        horse_id = qual_output['horse_id']
        betfair_win_odds = market_data.get(horse_id, {}).get('win_odds', 0)
        betfair_place_odds = market_data.get(horse_id, {}).get('place_odds', 0)

        market_win_prob = 1 / betfair_win_odds if betfair_win_odds > 0 else 0
        market_place_prob = 1 / betfair_place_odds if betfair_place_odds > 0 else 0

        win_edge = (synthesized['win_prob_fused'] - market_win_prob) / market_win_prob if market_win_prob > 0 else 0
        place_edge = (synthesized['place_prob_fused'] - market_place_prob) / market_place_prob if market_place_prob > 0 else 0

        # Calculate fair odds
        win_fair_odds = 1 / synthesized['win_prob_fused'] if synthesized['win_prob_fused'] > 0 else 999
        place_fair_odds = 1 / synthesized['place_prob_fused'] if synthesized['place_prob_fused'] > 0 else 999

        # Compute uncertainty intervals
        uncertainty = self.uncertainty_quantifier.predict_with_intervals(
            [synthesized['win_prob_fused'], synthesized['place_prob_fused']]
        )

        processing_time = time.time() - start_time

        return {
            'race_id': race['race_id'],
            'horse_id': qual_output['horse_id'],
            'horse_name': qual_output['horse_name'],
            'win_prob_base': quant_output['win_prob_base'],
            'win_prob_fused': synthesized['win_prob_fused'],
            'win_prob_calibrated': 0.0,  # Set after field normalization
            'place_prob_base': quant_output['place_prob_base'],
            'place_prob_fused': synthesized['place_prob_fused'],
            'place_prob_calibrated': 0.0,  # Set after field normalization
            'win_prob_lower': uncertainty['lower_bound'],
            'win_prob_upper': uncertainty['upper_bound'],
            'place_prob_lower': uncertainty['lower_bound'] * 2.5,  # Rough approximation
            'place_prob_upper': uncertainty['upper_bound'] * 2.5,
            'win_fair_odds': win_fair_odds,
            'place_fair_odds': place_fair_odds,
            'betfair_win_odds': betfair_win_odds,
            'betfair_place_odds': betfair_place_odds,
            'win_edge': win_edge,
            'place_edge': place_edge,
            'qualitative_lr': qual_output['lr_product_adjusted'],
            'qualitative_confidence': qual_output['overall_confidence'],
            'quantitative_confidence': quant_output.get('confidence', 0.75),
            'matrix_c_chemistry': qual_output['matrix_adjustments']['matrix_c_total'],
            'matrix_c_distance': 0.0,  # Extract from matrix breakdown
            'matrix_c_weather': 0.0,  # Extract from matrix breakdown
            'key_qualitative_factors': qual_output['key_strengths'][:3],
            'key_quantitative_features': quant_output.get('top_features', [])[:5],
            'fusion_reasoning': synthesized['reasoning'],
            'confidence_rationale': synthesized['confidence_rationale'],
            'processing_time_seconds': processing_time,
            'total_cost_dollars': qual_output['cost_dollars'] + quant_output.get('cost_dollars', 0.0),
            'consensus_score': synthesized['consensus_score'],
            'outlier_detected': synthesized['outlier_detected']
        }

    def _synthesize_agent_results(self, agent_results: List[dict]) -> dict:
        """
        Synthesize results from 15 concurrent agents.

        Strategy:
        1. Remove outlier agents (>2 std from mean)
        2. Weight by confidence scores
        3. Compute weighted average
        4. Generate consensus reasoning
        """
        import numpy as np

        # Extract probabilities from each agent
        win_probs = [r['win_prob_fused'] for r in agent_results]
        place_probs = [r['place_prob_fused'] for r in agent_results]
        confidences = [r.get('confidence', 0.75) for r in agent_results]

        # Detect outliers (>2 std from mean)
        win_mean = np.mean(win_probs)
        win_std = np.std(win_probs)

        valid_agents = []
        for i, wp in enumerate(win_probs):
            if abs(wp - win_mean) <= 2 * win_std:
                valid_agents.append(i)

        # Weighted average (by confidence)
        total_weight = sum(confidences[i] for i in valid_agents)
        win_prob_consensus = sum(
            win_probs[i] * confidences[i] for i in valid_agents
        ) / total_weight
        place_prob_consensus = sum(
            place_probs[i] * confidences[i] for i in valid_agents
        ) / total_weight

        # Consensus score (lower variance = higher consensus)
        consensus_score = 1 - (win_std / win_mean) if win_mean > 0 else 0.5

        # Outlier detection
        outlier_detected = len(valid_agents) < len(agent_results)

        # Generate reasoning
        reasoning = self._generate_consensus_reasoning(agent_results, valid_agents)

        return {
            'win_prob_fused': win_prob_consensus,
            'place_prob_fused': place_prob_consensus,
            'consensus_score': consensus_score,
            'outlier_detected': outlier_detected,
            'num_valid_agents': len(valid_agents),
            'reasoning': reasoning,
            'confidence_rationale': f"Consensus from {len(valid_agents)}/{len(agent_results)} agents (score: {consensus_score:.2f})"
        }

    def _generate_consensus_reasoning(
        self,
        agent_results: List[dict],
        valid_agents: List[int]
    ) -> str:
        """Generate human-readable consensus reasoning."""
        # Aggregate reasoning from valid agents
        reasoning_points = []
        for i in valid_agents[:5]:  # Top 5 agents
            agent = agent_results[i]
            reasoning_points.append(f"• {agent.get('strategy', 'Agent')}: {agent.get('reasoning', 'N/A')}")

        return "\n".join(reasoning_points)

    def _sequential_fusion(
        self,
        qual_output: dict,
        quant_output: dict
    ) -> dict:
        """Fallback sequential fusion (no concurrent agents)."""
        # Basic Bayesian fusion with Matrix C
        win_prob_fused = bayesian_fusion_with_matrix_c(
            base_prob=quant_output['win_prob_base'],
            lr_product=qual_output['lr_product_adjusted'],
            chemistry_multiplier=qual_output['matrix_adjustments']['matrix_c_total'],
            distance_adjustment=0.0,
            weather_adjustment=0.0
        )

        place_prob_fused = bayesian_fusion_with_matrix_c(
            base_prob=quant_output['place_prob_base'],
            lr_product=qual_output['lr_product_adjusted'],
            chemistry_multiplier=qual_output['matrix_adjustments']['matrix_c_total'],
            distance_adjustment=0.0,
            weather_adjustment=0.0
        )

        return {
            'win_prob_fused': win_prob_fused,
            'place_prob_fused': place_prob_fused,
            'confidence': 0.70,
            'strategy': 'Sequential',
            'reasoning': 'Basic Bayesian fusion with Matrix C adjustments'
        }

    def _get_track_group(self, track: str) -> str:
        """Determine track group for calibration."""
        metro_tracks = ['flemington', 'randwick', 'caulfield', 'rosehill']
        provincial_tracks = ['sandown', 'moonee valley', 'warwick farm']

        track_lower = track.lower()
        if track_lower in metro_tracks:
            return 'metro'
        elif track_lower in provincial_tracks:
            return 'provincial'
        else:
            return 'country'
```

---

## ⚡ 6. Performance & Optimization {#performance}

### **Processing Time Breakdown**

| Component | Sequential | Concurrent (E2B) | Speedup |
|-----------|-----------|------------------|---------|
| Qualitative Pipeline | 5-7 min | 5-7 min | 1x (same) |
| Quantitative Pipeline | 10-30s | 10-30s | 1x (same) |
| Fusion (15 approaches) | 75-150s | 5-10s | **15x** |
| Field Normalization | 1-2s | 1-2s | 1x (same) |
| Calibration | 1-2s | 1-2s | 1x (same) |
| **Total** | **8-10 min** | **6-8 min** | **1.3x** |

**Key Insight:** Main bottleneck is qualitative pipeline (5-7 min). Concurrent fusion provides 15x speedup on fusion itself, but overall speedup is limited by pipeline latency.

### **Cost Analysis**

**Per Race (12 horse field):**

```
Qualitative: $0.62/race × 12 horses = $7.44
Quantitative: $0.01/race × 12 horses = $0.12
Fusion (E2B): $0.05/race × 12 horses = $0.60  (15 sandboxes)
Fusion (OpenHands): $0.02/race × 12 horses = $0.24  (coordination overhead)
Fusion (Sequential): $0.00  (no additional cost)

Total with E2B: $8.16/race
Total with OpenHands: $7.80/race
Total Sequential: $7.56/race
```

**Monthly Cost (100 races, 1200 horses):**

```
E2B: $816/month
OpenHands: $780/month
Sequential: $756/month

Extra cost for concurrency: $24-60/month
Benefit: 15x faster fusion, higher accuracy (ensemble of 15 approaches)
```

### **Accuracy Improvements**

Concurrent multi-agent fusion provides:

- **Ensemble diversity**: 15 different strategies reduce bias
- **Outlier detection**: Remove bad agent predictions
- **Confidence calibration**: Weighted by agent agreement
- **Robustness**: Less sensitive to single agent failures

**Expected Gains:**

- Brier score: 0.18 → 0.16 (11% improvement)
- Calibration error: 3% → 2% (33% improvement)
- ROI: 5% → 7% (40% improvement)

### **Production Deployment Strategy**

**Phase 1: Sequential (Weeks 1-4)**

- Use basic sequential fusion
- Validate Bayesian integration logic
- Build calibration curves
- **Cost**: $7.56/race

**Phase 2: E2B Forking (Weeks 5-8)**

- Deploy E2B concurrent agents
- A/B test vs sequential
- Measure accuracy improvements
- **Cost**: $8.16/race (+$0.60)

**Phase 3: Hybrid (Weeks 9+)**

- Use E2B for high-stakes races (Group 1/2)
- Use sequential for low-stakes (country races)
- Optimize cost/performance tradeoff
- **Cost**: ~$7.80/race (blended)

---

## 🎯 Success Criteria

### **Fusion Model Targets**

| Metric | Target | Stretch Goal |
|--------|--------|--------------|
| Brier Score | <0.18 | <0.16 |
| AUC-ROC | >0.75 | >0.78 |
| Calibration Error (ECE) | <3% | <2% |
| Win Accuracy (Top 3) | >75% | >80% |
| ROI (after commission) | >5% | >7% |
| Processing Time | <8 min | <6 min |
| Cost per Race | <$10 | <$8 |

### **Integration Checklist**

- [x] Bayesian LR theory documented
- [x] Basic fusion algorithm implemented
- [x] Matrix C integration designed
- [x] Field normalization methods defined
- [x] Calibration framework specified
- [x] Uncertainty quantification (conformal prediction)
- [x] E2B forking manager designed
- [x] OpenHands micro-agent orchestrator designed
- [x] 15 specialized agents defined
- [x] Consensus synthesis algorithm
- [x] Outlier detection mechanism
- [ ] Production deployment (Phase 1-3)
- [ ] Backtest validation (1000+ races)
- [ ] Live testing (50+ races)

---

## 📚 References

**Bayesian Statistics:**

- Jaynes, E.T. (2003). "Probability Theory: The Logic of Science"
- Gelman et al. (2013). "Bayesian Data Analysis"

**Conformal Prediction:**

- Vovk et al. (2005). "Algorithmic Learning in a Random World"
- Angelopoulos & Bates (2022). "Conformal Prediction: A Gentle Introduction"

**Multi-Agent Systems:**

- E2B Documentation: <https://e2b.dev/docs>
- OpenHands Framework: <https://github.com/All-Hands-AI/OpenHands>

**Racing Prediction:**

- Benter, W. (2008). "Computer Based Horse Race Handicapping"
- Bolton & Chapman (1986). "Searching for Positive Returns at the Track"

---

**End of Fusion Model Architecture**

**Next Steps:**

1. Begin Phase 1 implementation (Data layer + ETL)
2. Build calibration curves from historical data
3. Deploy sequential fusion first (validate logic)
4. Integrate E2B forking in Phase 2
5. Backtest on 1000+ historical races

**Total Documentation: ~5,900 lines across 6 major documents**

- Qualitative Pipeline: 4,800 lines (5 parts)
- Quantitative Pipeline: 3,100 lines (3 parts, from earlier)
- Fusion Model: 1,100 lines (this document)
