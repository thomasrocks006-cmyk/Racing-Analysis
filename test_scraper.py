#!/usr/bin/env python3
"""
Test racing.com scraper on live data.
"""

import sys
from datetime import date
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import logging

from data.scrapers.racing_com import RacingComScraper

# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_scraper():
    """Test the racing.com scraper."""
    scraper = RacingComScraper()

    # Test with a future date that has races
    test_date = date(2026, 1, 1)  # New Year's Day - likely to have races
    test_venue = "mornington"  # From the homepage
    test_race_number = 1

    print(f"\n{'=' * 60}")
    print(f"Testing racing.com scraper")
    print(f"{'=' * 60}")
    print(f"Date: {test_date}")
    print(f"Venue: {test_venue}")
    print(f"Race: {test_race_number}")
    print(f"{'=' * 60}\n")

    try:
        # Attempt to scrape
        race_card = scraper.scrape_race(test_venue, test_date, test_race_number)

        # Display results
        print(f"\n✅ Scrape successful!")
        print(f"\nRace Details:")
        print(f"  - ID: {race_card.race.race_id}")
        print(f"  - Name: {race_card.race.race_name}")
        print(f"  - Distance: {race_card.race.distance}m")
        print(f"  - Track: {race_card.race.track_condition}")
        print(f"  - Prize: ${race_card.race.prize_money:,}")
        print(f"  - Field Size: {race_card.race.field_size}")

        print(f"\nRunners ({len(race_card.runs)}):")
        for i, run in enumerate(race_card.runs[:5], 1):  # Show first 5
            horse = next(h for h in race_card.horses if h.horse_id == run.horse_id)
            jockey = next(j for j in race_card.jockeys if j.jockey_id == run.jockey_id)
            trainer = next(
                t for t in race_card.trainers if t.trainer_id == run.trainer_id
            )

            print(f"  {i}. Barrier {run.barrier}: {horse.name}")
            print(f"     Jockey: {jockey.name}, Trainer: {trainer.name}")
            print(f"     Weight: {run.weight_carried}kg")

        if len(race_card.runs) > 5:
            print(f"  ... and {len(race_card.runs) - 5} more")

        # Check completeness
        completeness = race_card.validate_completeness()
        print(f"\nData Completeness: {completeness:.1f}%")

        # Check if it's placeholder data
        if (
            "Sample" in race_card.race.race_name
            or "Placeholder" in race_card.race.race_name
        ):
            print(f"\n⚠️  WARNING: Using placeholder data (scraping may have failed)")
        else:
            print(f"\n🎉 SUCCESS: Real data scraped from racing.com!")

        return race_card

    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_scraper()
