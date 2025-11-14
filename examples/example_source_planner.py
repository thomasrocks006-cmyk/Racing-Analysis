"""
Example usage of the Stage 1 Source Planning Agent.

This script demonstrates how to use the SourcePlanningAgent to identify
and prioritize information sources for race analysis.
"""

import os
from datetime import date
from decimal import Decimal

from src.data.models import (
    Horse,
    Jockey,
    MarketOdds,
    OddsType,
    Race,
    Run,
    SexType,
    Trainer,
    TrackType,
)
from src.pipelines.qualitative.stage1_source_planner import (
    SourcePlanningAgent,
    create_race_context_from_models,
)


def example_basic_usage():
    """Example 1: Basic usage with minimal race context."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Usage with Minimal Race Context")
    print("=" * 70)

    # Initialize agent (requires GOOGLE_API_KEY environment variable)
    # For testing without API key, you can catch the ValueError
    try:
        agent = SourcePlanningAgent()
    except ValueError as e:
        print(f"⚠️  {e}")
        print("Set GOOGLE_API_KEY environment variable to run this example.")
        return

    # Create minimal race context
    race_context = {
        "race_id": "FLE-2025-11-14-R1",
        "venue": "FLE",
        "distance": 1200,
    }

    # Plan sources
    print("\nPlanning sources for race...")
    plan = agent.plan_sources(race_context)

    # Display results
    print(f"\nRace: {plan.race_id}")
    print(f"Venue: {plan.venue}")
    print(f"Distance: {plan.distance}m")
    print(f"Total sources recommended: {plan.total_sources}")
    print(f"\nHigh priority sources (relevance >= 0.7): {len(plan.high_priority_sources)}")

    print("\nTop 10 Sources:")
    for i, source in enumerate(plan.sources[:10], 1):
        print(f"{i:2d}. [{source.relevance_score:.2f}] {source.source_type}")
        print(f"    Category: {source.category} | {source.description}")


def example_detailed_race():
    """Example 2: Detailed race with runner information."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Detailed Race with Runner Information")
    print("=" * 70)

    try:
        agent = SourcePlanningAgent()
    except ValueError as e:
        print(f"⚠️  {e}")
        return

    # Create detailed race context
    race_context = {
        "race_id": "FLE-2025-11-14-R6",
        "race_name": "Group 1 Champions Sprint",
        "venue": "FLE",
        "venue_name": "Flemington",
        "distance": 1200,
        "race_type": "Group 1",
        "track_condition": "Good 4",
        "field_size": 12,
        "prize_money": 1000000,
        "runners": [
            {
                "horse_name": "Nature Strip",
                "barrier": 5,
                "jockey_name": "J. McDonald",
                "trainer_name": "C. Waller",
                "odds": 2.50,
            },
            {
                "horse_name": "Home Affairs",
                "barrier": 3,
                "jockey_name": "D. Oliver",
                "trainer_name": "T. Dabernig",
                "odds": 4.20,
            },
            {
                "horse_name": "Eduardo",
                "barrier": 8,
                "jockey_name": "M. Zahra",
                "trainer_name": "J. Moloney",
                "odds": 6.50,
            },
        ],
        "market_context": {
            "favourite_odds": 2.50,
        },
    }

    # Plan sources
    print("\nPlanning sources for Group 1 race...")
    plan = agent.plan_sources(race_context)

    # Display results
    print(f"\nRace: {plan.race_name}")
    print(f"Venue: {plan.venue_name or plan.venue}")
    print(f"Distance: {plan.distance}m")
    print(f"Total sources: {plan.total_sources}")

    # Show sources by category
    print("\nSources by Category:")
    categories = {}
    for source in plan.sources:
        if source.category not in categories:
            categories[source.category] = []
        categories[source.category].append(source)

    for category in sorted(categories.keys()):
        sources = categories[category]
        print(f"\nCategory {category}: {len(sources)} source(s)")
        for source in sources:
            print(f"  - {source.source_type} (relevance: {source.relevance_score:.2f})")


def example_from_pydantic_models():
    """Example 3: Creating race context from Pydantic models."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Creating Race Context from Pydantic Models")
    print("=" * 70)

    try:
        agent = SourcePlanningAgent()
    except ValueError as e:
        print(f"⚠️  {e}")
        return

    # Create sample race using Pydantic models
    race = Race(
        race_id="RAN-2025-11-14-R4",
        date=date(2025, 11, 14),
        venue="RAN",
        venue_name="Randwick",
        race_number=4,
        race_name="Listed Stakes",
        distance=1400,
        track_condition="Good 4",
        track_type=TrackType.TURF,
        class_level="Listed",
        field_size=10,
        prize_money=200000,
        data_source="racing.com",
    )

    # Create sample runner data
    horse = Horse(
        horse_id="H001",
        name="Winx",
        age=5,
        sex=SexType.MARE,
    )

    jockey = Jockey(
        jockey_id="J001",
        name="H. Bowman",
    )

    trainer = Trainer(
        trainer_id="T001",
        name="C. Waller",
        state="NSW",
    )

    run = Run(
        run_id="R001",
        race_id="RAN-2025-11-14-R4",
        horse_id="H001",
        jockey_id="J001",
        trainer_id="T001",
        barrier=5,
        weight_carried=Decimal("57.5"),
    )

    odds = MarketOdds(
        odds_id="O001",
        run_id="R001",
        race_id="RAN-2025-11-14-R4",
        timestamp=date.today(),
        source="betfair",
        odds_type=OddsType.WIN,
        odds_decimal=Decimal("3.50"),
    )

    # Create race context from models
    print("\nCreating race context from Pydantic models...")
    race_context = create_race_context_from_models(
        race=race,
        runs=[run],
        horses=[horse],
        jockeys=[jockey],
        trainers=[trainer],
        market_odds=[odds],
    )

    # Plan sources
    print("Planning sources...")
    plan = agent.plan_sources(race_context)

    # Display results
    print(f"\nRace: {plan.race_name}")
    print(f"Venue: {plan.venue}")
    print(f"Distance: {plan.distance}m")
    print(f"Sources recommended: {plan.total_sources}")

    # Show high priority sources
    print(f"\nHigh Priority Sources ({len(plan.high_priority_sources)}):")
    for source in plan.high_priority_sources[:5]:
        print(f"  - {source.source_type}")
        print(f"    Relevance: {source.relevance_score:.2f} | Category: {source.category}")
        print(f"    {source.description}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("SOURCE PLANNING AGENT - USAGE EXAMPLES")
    print("=" * 70)

    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  WARNING: GOOGLE_API_KEY not set in environment")
        print("These examples will not run without a valid API key.")
        print("\nTo run the examples:")
        print("1. Get a Google API key from https://makersuite.google.com/app/apikey")
        print("2. Set the environment variable:")
        print("   export GOOGLE_API_KEY='your-api-key-here'")
        print("3. Run this script again\n")
        return

    # Run examples
    example_basic_usage()
    example_detailed_race()
    example_from_pydantic_models()

    print("\n" + "=" * 70)
    print("Examples completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
