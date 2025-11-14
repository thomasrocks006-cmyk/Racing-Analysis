# Agent Skill: Deep Critical Analysis

## Purpose
Perform rigorous, multi-layered critical analysis with built-in self-assessment checkpoints: identifying gaps, testing assumptions, challenging conclusions, and providing harsh but fair critique at multiple levels.

## When to Use
- "Use deep-critical-analysis skill: Thoroughly analyze..."
- "Use deep-critical-analysis skill: Identify all flaws and risks in..."
- "Use deep-critical-analysis skill: Do a ruthless assessment of..."
- "Use deep-critical-analysis skill: Find everything wrong with..."
- "Use deep-critical-analysis skill: Critical review with tough questions..."

## Typical Workflow

### Layer 1: Gap Analysis (Initial Assessment)

1. **Define the Target System**
   - Current state: What exists now?
   - Desired state: What should exist?
   - Gap: What's missing or wrong?

2. **Identify Gap Categories**
   - Knowledge gaps (missing understanding)
   - Performance gaps (not meeting requirements)
   - Architecture gaps (design flaws)
   - Data gaps (incomplete or wrong data)
   - Testing gaps (insufficient validation)
   - Documentation gaps (missing or unclear guidance)

3. **Severity Assessment**
   - Critical: Blocks deployment or core functionality
   - Major: Significantly impacts performance/quality
   - Minor: Cosmetic or low-impact issues
   - Deferred: Can be addressed later

**Checkpoint 1: Are we missing any categories?**
- Run through mental checklist of all possible gap types
- Ask: "What haven't we considered?"

---

### Layer 2: Deep Assumption Analysis

1. **Identify All Assumptions**
   - Explicit: Stated clearly
   - Implicit: Unstated but present in code/design
   - Hidden: Not obvious until challenged

2. **Challenge Each Assumption**
   - Is this still valid?
   - What if it's wrong?
   - What evidence supports it?
   - How would we know if it failed?
   - What would break if this assumption changed?

3. **Test Assumption Validity**
   - Historical: Has this assumption held in the past?
   - Logical: Does this make logical sense?
   - Empirical: Do we have data supporting it?
   - Contextual: Is it valid in our current context?

**Checkpoint 2: Did we challenge every assumption?**
- Review list: Are there assumptions we accepted too readily?
- Look for groupthink or inherited wisdom never questioned
- Ask: "What would someone from outside our domain say?"

---

### Layer 3: Critical Questions & Tough Assessment

1. **Ask Harsh Questions**
   - What's the worst that could happen?
   - How could this fail catastrophically?
   - What did we ignore or downplay?
   - Where are we being overconfident?
   - What would an adversary exploit?
   - What will we regret in 2 years?

2. **Challenge Core Reasoning**
   - Is this logic sound or just convincing?
   - Are we confusing correlation with causation?
   - Are we anchored on the first solution?
   - Is there survivorship bias in our examples?
   - Are we dismissing viable alternatives too quickly?

3. **Identify Blind Spots**
   - What don't we know that we don't know?
   - What perspectives are we missing?
   - What domain expertise would change our view?
   - What would newcomers see immediately?

4. **Evaluate Trade-offs Honestly**
   - What are we sacrificing?
   - Is the trade-off worth it?
   - Could we have a better trade-off?
   - Did we consider all stakeholder perspectives?

**Checkpoint 3: Were we tough enough?**
- Review questions: Are they actually challenging or just rhetorical?
- Did we accept comfortable answers?
- Did we push until we got uncomfortable?

---

### Layer 4: Final Comprehensive Review

1. **Summary of Findings**
   - Gap analysis results: What's missing?
   - Assumption validity: What's shaky?
   - Critical risks: What could fail?
   - Blind spots: What are we missing?

2. **Severity & Impact Matrix**
   - High impact + High probability: Critical fixes needed
   - High impact + Low probability: Monitor closely
   - Low impact + High probability: Nice to fix
   - Low impact + Low probability: Defer

3. **Recommendations Ranked by ROI**
   - Effort to fix vs. Risk reduction
   - Effort to fix vs. Value gained
   - Quick wins vs. strategic investments

4. **Implementation Roadmap**
   - What must be fixed immediately?
   - What should be fixed in next sprint?
   - What can be deferred?
   - What needs more investigation?

**Final Checkpoint: Is this assessment complete and fair?**
- Did we identify all major gaps?
- Were we thorough but not perfectionist?
- Are recommendations actionable?
- Did we avoid analysis paralysis?

---

## Code Patterns for Rigorous Analysis

```python
class CriticalAnalyzer:
    """Multi-layer critical analysis framework."""
    
    def __init__(self, system):
        self.system = system
        self.findings = {
            'gaps': [],
            'assumptions': [],
            'risks': [],
            'blind_spots': [],
            'recommendations': []
        }
    
    def analyze(self):
        """Run complete 4-layer analysis."""
        layer1_gaps = self._layer1_gap_analysis()
        layer2_assumptions = self._layer2_assumption_analysis()
        layer3_critical = self._layer3_critical_questions()
        layer4_review = self._layer4_final_review()
        
        return self._synthesize_findings(
            layer1_gaps, 
            layer2_assumptions, 
            layer3_critical, 
            layer4_review
        )
    
    def _layer1_gap_analysis(self):
        """Identify all gaps between current and desired state."""
        gaps = {
            'knowledge': self._find_knowledge_gaps(),
            'performance': self._find_performance_gaps(),
            'architecture': self._find_architecture_gaps(),
            'data': self._find_data_gaps(),
            'testing': self._find_testing_gaps(),
            'documentation': self._find_documentation_gaps(),
        }
        
        # Checkpoint: Self-assess completeness
        self._checkpoint_gaps_complete(gaps)
        return gaps
    
    def _layer2_assumption_analysis(self):
        """Challenge all assumptions."""
        assumptions = self._extract_all_assumptions()
        
        challenged = {}
        for assumption, context in assumptions.items():
            challenged[assumption] = {
                'still_valid': self._test_assumption(assumption, context),
                'evidence': self._find_evidence(assumption),
                'failure_modes': self._identify_failure_modes(assumption),
                'consequence_if_wrong': self._assess_consequence(assumption),
            }
        
        # Checkpoint: Self-assess assumption rigor
        self._checkpoint_assumptions_thorough(challenged)
        return challenged
    
    def _layer3_critical_questions(self):
        """Ask tough questions about design."""
        questions = [
            self._worst_case_scenarios(),
            self._failure_modes(),
            self._ignored_factors(),
            self._overconfidence_areas(),
            self._adversarial_attacks(),
            self._future_regrets(),
        ]
        
        answers = {}
        for question_set in questions:
            for question in question_set:
                answers[question] = self._answer_critically(question)
        
        # Checkpoint: Self-assess question quality
        self._checkpoint_questions_harsh(answers)
        return answers
    
    def _layer4_final_review(self):
        """Synthesize all findings into recommendations."""
        severity_matrix = self._build_severity_matrix()
        recommendations = self._rank_by_roi(severity_matrix)
        roadmap = self._create_implementation_roadmap(recommendations)
        
        # Final checkpoint: Assessment completeness
        self._checkpoint_final_review_complete(roadmap)
        return roadmap
    
    def _checkpoint_gaps_complete(self, gaps):
        """Self-assess: Did we find all gap types?"""
        gap_types = list(gaps.keys())
        # Ask: Are there any gap categories we missed?
        # Return assessment
    
    def _checkpoint_assumptions_thorough(self, challenged):
        """Self-assess: Did we really challenge assumptions?"""
        # Count how many assumptions we questioned thoroughly
        # Review: Are there assumptions we accepted too easily?
        # Return assessment
    
    def _checkpoint_questions_harsh(self, answers):
        """Self-assess: Were questions actually tough?"""
        # Assess: Did we make ourselves uncomfortable?
        # Review: Are there harder questions we should ask?
        # Return assessment
    
    def _checkpoint_final_review_complete(self, roadmap):
        """Self-assess: Is this analysis complete?"""
        # Review: Have we covered all angles?
        # Assess: Are recommendations actionable?
        # Return final assessment
```

## Gap Analysis Framework

### Knowledge Gaps
- What domain expertise do we lack?
- Are there fundamentals we don't understand?
- What literature should we have read?
- What patterns should we know about?

### Performance Gaps
- What are actual vs. target performance metrics?
- Where are bottlenecks?
- What could be optimized?
- What's acceptable vs. unacceptable?

### Architecture Gaps
- Are there design flaws?
- Is the structure aligned with requirements?
- Are there scalability issues?
- Is maintainability sufficient?

### Data Gaps
- Is our data complete?
- Is data quality sufficient?
- Are we missing important data sources?
- Is data validation adequate?

### Testing Gaps
- What's not being tested?
- Are edge cases covered?
- Is error handling tested?
- Are integration points tested?

### Documentation Gaps
- Are architecture decisions documented?
- Is the system understandable to newcomers?
- Are tradeoffs explained?
- Are known issues documented?

## Tough Questions Checklist

### Worst Case & Failure
- [ ] What's the worst that could happen?
- [ ] How would we know if it happened?
- [ ] Could we prevent it? At what cost?
- [ ] What would recovery look like?

### Assumptions & Logic
- [ ] What are we assuming without evidence?
- [ ] Could we be wrong about this?
- [ ] What would prove us wrong?
- [ ] Is this logical or just intuitive?

### Overconfidence & Bias
- [ ] Where are we too confident?
- [ ] What perspectives are we missing?
- [ ] Are we falling for a common fallacy?
- [ ] What would make us wrong?

### Trade-offs & Alternatives
- [ ] What are we sacrificing?
- [ ] Is this the only way?
- [ ] Did we consider alternatives seriously?
- [ ] Could we have a better trade-off?

### Hidden Costs & Risks
- [ ] What aren't we counting?
- [ ] What could become expensive?
- [ ] What technical debt are we creating?
- [ ] What will compound over time?

## Success Criteria
- ✅ Gap analysis completed across 6+ categories
- ✅ Every major assumption explicitly challenged
- ✅ Tough questions answered honestly
- ✅ Blind spots identified
- ✅ Self-assessment checkpoints passed
- ✅ Recommendations are specific and actionable
- ✅ Trade-offs and risks clearly documented
- ✅ Honest assessment of our own overconfidence
