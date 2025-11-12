"""
Integration example: Using GitHub Copilot API with Racing Analysis
Demonstrates how to get AI assistance for feature engineering and model selection.
"""

from src.api.copilot_api import MultiAgent


def analyze_feature_engineering():
    """Get expert opinions on feature engineering for racing model."""
    print("=" * 70)
    print("Feature Engineering Analysis")
    print("=" * 70)

    agents = MultiAgent.create_racing_analysts()

    query = """
    I have a horse racing dataset with:
    - Horse: past speed ratings, career win%, days since last race
    - Jockey: career win%, jockey-horse combination history
    - Track: going (firm/soft), distance, class level
    - Market: Betfair odds, liquidity

    What are the top 5 derived features I should engineer to predict:
    1. Win probability
    2. Place probability (top 3)

    Focus on features that:
    - Capture form/momentum
    - Don't leak future information
    - Work well with gradient boosting models
    """

    print("\nConsulting 3 racing analysts...\n")
    results = agents.analyze(query)

    # Show each analyst's perspective
    for agent_name, result in results.items():
        if result.get("success"):
            print(f"\n{agent_name}:")
            print("-" * 70)
            print(result["content"])
        else:
            print(f"\n{agent_name}: Error - {result.get('message')}")

    # Get synthesis
    print("\n" + "=" * 70)
    print("Synthesized Recommendation:")
    print("=" * 70)
    synthesis = agents.synthesize(query, results)
    if synthesis.get("success"):
        print(synthesis["content"])

    return results, synthesis


def analyze_model_selection():
    """Get expert opinions on CatBoost vs LightGBM."""
    print("\n\n" + "=" * 70)
    print("Model Selection Analysis")
    print("=" * 70)

    agents = MultiAgent.create_racing_analysts()

    query = """
    For horse racing prediction, should I use CatBoost or LightGBM?

    Context:
    - 50k training samples, 20 features
    - Mix of categorical (horse_id, jockey_id, track_id) and numerical
    - Need calibrated probabilities (not just rankings)
    - Training speed matters (daily retraining)
    - Will ensemble with other models

    Compare on:
    1. Categorical feature handling
    2. Training speed
    3. Probability calibration quality
    4. Ease of hyperparameter tuning
    5. Memory usage
    """

    print("\nConsulting 3 experts...\n")
    results = agents.analyze(query)

    # Show key points from each analyst
    for agent_name, result in results.items():
        if result.get("success"):
            # Just show first 300 chars as preview
            preview = result["content"][:300].replace("\n", " ")
            print(f"{agent_name}: {preview}...")

    # Get final recommendation
    print("\n" + "=" * 70)
    print("Final Recommendation:")
    print("=" * 70)
    synthesis = agents.synthesize(query, results)
    if synthesis.get("success"):
        print(synthesis["content"])

    return results, synthesis


def analyze_calibration_strategy():
    """Get expert opinions on probability calibration approach."""
    print("\n\n" + "=" * 70)
    print("Calibration Strategy Analysis")
    print("=" * 70)

    agents = MultiAgent.create_racing_analysts()

    query = """
    My gradient boosting models give win probabilities that need calibration.

    Current approach:
    1. Train CatBoost/LightGBM with log loss
    2. Apply isotonic regression on validation fold
    3. Evaluate calibration with reliability diagrams and Brier score

    Questions:
    1. Should I use isotonic or Platt scaling?
    2. How to handle small sample sizes for low-probability events?
    3. Should I calibrate win/place separately or jointly?
    4. How to validate calibration is working correctly?
    """

    print("\nConsulting 3 experts...\n")
    results = agents.analyze(query)

    synthesis = agents.synthesize(query, results)

    # Show just the synthesis (most important)
    if synthesis.get("success"):
        print("\nRecommendation:")
        print(synthesis["content"])

    return results, synthesis


def get_code_review():
    """Get code review from specialized agents."""
    print("\n\n" + "=" * 70)
    print("Code Review Example")
    print("=" * 70)

    agents = MultiAgent.create_code_reviewers()

    # Example code to review
    code = """
def compute_form_features(horse_id, race_date):
    recent_races = get_races(horse_id, before=race_date, limit=5)

    avg_speed = sum([r['speed_rating'] for r in recent_races]) / len(recent_races)
    win_pct = sum([1 for r in recent_races if r['position'] == 1]) / len(recent_races)

    days_since_last = (race_date - recent_races[0]['date']).days

    return {
        'avg_speed_last_5': avg_speed,
        'win_pct_last_5': win_pct,
        'days_since_last_race': days_since_last
    }
"""

    query = f"Review this Python function for racing feature engineering:\n\n{code}"

    print("\nGetting review from 3 specialists...\n")
    results = agents.analyze(query)

    for agent_name, result in results.items():
        if result.get("success"):
            print(f"\n{agent_name}:")
            print(result["content"][:250] + "...")


if __name__ == "__main__":
    print("\nGitHub Copilot API - Racing Analysis Integration")
    print("Using your 1500 premium requests for expert AI assistance\n")

    # Run analyses
    # Each analyze() uses 3 premium requests
    # Each synthesize() uses 1 more premium request

    # Example 1: Feature engineering (3 requests)
    feature_results, feature_synthesis = analyze_feature_engineering()

    # Example 2: Model selection (3 requests)
    model_results, model_synthesis = analyze_model_selection()

    # Example 3: Calibration strategy (4 requests: 3 + 1 synthesis)
    calib_results, calib_synthesis = analyze_calibration_strategy()

    # Example 4: Code review (3 requests)
    get_code_review()

    # Total premium requests used: 3 + 3 + 4 + 3 = 13 requests

    print("\n\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)
    print("\nPremium requests used: ~13")
    print("Remaining budget: ~1487 requests")
    print("\nKey insights generated:")
    print("✓ Top 5 features to engineer")
    print("✓ CatBoost vs LightGBM recommendation")
    print("✓ Calibration strategy")
    print("✓ Code quality review")
