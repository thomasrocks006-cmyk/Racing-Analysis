# Agent Skill: Creativity & Innovation

## Purpose
Handle creative problem-solving and innovative thinking: brainstorming alternatives, finding novel approaches, challenging assumptions, and thinking outside conventional patterns.

## When to Use
- "Use creativity skill: Brainstorm alternative architectures for..."
- "Use creativity skill: Challenge our assumptions about..."
- "Use creativity skill: Find creative solutions to..."
- "Use creativity skill: What unconventional approaches could..."
- "Use creativity skill: Break through this design deadlock..."

## Typical Workflow

1. **Problem Reframing**
   - Examine the constraint from multiple angles
   - Question unstated assumptions
   - Identify hidden requirements or opportunities
   - Look for patterns in successful solutions elsewhere

2. **Divergent Thinking**
   - Generate 5-10 alternative approaches (no filtering)
   - Mix and combine ideas from different domains
   - Apply creative techniques (SCAMPER, analogies, role reversal)
   - Consider "what if" scenarios

3. **Evaluation & Synthesis**
   - Assess each alternative on multiple dimensions
   - Identify unexpected synergies
   - Combine best elements into hybrid solutions
   - Rank by novelty, feasibility, and impact

4. **Implementation Guidance**
   - Outline how to prototype the most promising idea
   - Identify risks and mitigation strategies
   - Suggest quick experiments to validate approach
   - Connect to your existing project patterns

## Creative Techniques to Apply

### SCAMPER Method
- **Substitute** - Replace a component with something else
- **Combine** - Merge with another concept or technology
- **Adapt** - Adjust for a different purpose or context
- **Modify** - Change attributes, scale, or structure
- **Put to another use** - Apply in a different context
- **Eliminate** - Remove elements, simplify
- **Reverse** - Invert the process or relationships

### Cross-Domain Thinking
- Borrow patterns from biology (evolution, adaptation)
- Apply game theory concepts
- Use storytelling approaches
- Consider systems thinking
- Learn from nature's solutions (biomimicry)

### Constraint Relaxation
- "What if we had unlimited budget?"
- "What if latency didn't matter?"
- "What if we could store unlimited data?"
- "What if we ignored certain constraints?"
- Then work backward to realistic solutions

## Code Patterns to Consider

```python
# Prototype creative idea quickly
class ExperimentalApproach:
    """Quick test of unconventional idea."""
    def __init__(self, hypothesis):
        self.hypothesis = hypothesis
        self.results = {}
    
    def test(self, data, conditions):
        """Run quick experiment to validate."""
        result = self._execute(data, conditions)
        self.results[conditions] = result
        return result
    
    def assess(self):
        """Evaluate if hypothesis holds."""
        return self._score_results()

# Adaptive pattern matching
def find_unconventional_solution(problem, search_space):
    """Search for non-obvious solutions."""
    candidates = []
    
    # Try standard approaches
    candidates.extend(standard_solutions(problem))
    
    # Try cross-domain solutions
    candidates.extend(biomimicry_solutions(problem))
    candidates.extend(game_theory_solutions(problem))
    candidates.extend(chaos_theory_solutions(problem))
    
    # Score by novelty AND feasibility
    return rank_by_novelty_and_feasibility(candidates)
```

## Key Questions to Ask

- What would a completely different industry do?
- What if we inverted this problem?
- What constraints are self-imposed vs. real?
- What would the ideal solution look like (ignoring constraints)?
- How might this fail in unexpected ways?
- What adjacent problems could this solve?
- What if we combined this with something from a different domain?

## Common Creative Tasks

### Brainstorm Alternative Architectures
- [ ] List all current architectural assumptions
- [ ] Question each assumption (why do we do it this way?)
- [ ] Propose 3-5 completely different architectures
- [ ] Compare on trade-offs (simplicity, performance, maintenance)
- [ ] Identify hybrid approaches combining best elements
- [ ] Prototype the most promising alternative

### Challenge Technical Assumptions
- [ ] What assumptions underlie this design?
- [ ] Are they still valid?
- [ ] What if we removed this constraint?
- [ ] What becomes possible if we relax this requirement?
- [ ] What emerging tech could change this trade-off?

### Find Novel Solutions to Bottlenecks
- [ ] Analyze the bottleneck from first principles
- [ ] Apply creative techniques to generate alternatives
- [ ] Consider non-technical solutions
- [ ] Look for solutions in adjacent domains
- [ ] Evaluate for unexpected side benefits

### Innovate Feature Design
- [ ] What would make this 10x better?
- [ ] What adjacent features become possible?
- [ ] How might a user use this in unexpected ways?
- [ ] What emerging patterns could inspire this?

## Success Criteria
- ✅ At least 5-10 genuinely different alternatives generated
- ✅ Non-obvious approaches included (not just variations)
- ✅ Cross-domain thinking applied
- ✅ Assumptions explicitly challenged
- ✅ Hybrid solutions synthesized
- ✅ Feasible prototype path identified
- ✅ Novel approach clearly explained with rationale
