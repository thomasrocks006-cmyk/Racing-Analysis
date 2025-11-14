#!/usr/bin/env python3
"""
Test Racing.com Selenium scraper on Melbourne Cup 2024.

Tests:
1. Can we fetch race data with Selenium?
2. What's the actual data completeness?
3. What CSS selectors work?
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.scrapers.racing_com_selenium import RacingComSeleniumScraper

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_melbourne_cup():
    """Test scraping Melbourne Cup 2024 (Race 7)."""
    logger.info("=" * 60)
    logger.info("Testing Racing.com Selenium Scraper")
    logger.info("Target: Melbourne Cup 2024 - Flemington R7")
    logger.info("=" * 60)

    try:
        with RacingComSeleniumScraper(headless=True) as scraper:
            # Scrape Melbourne Cup (Race 7, November 5, 2024)
            race_card = scraper.scrape_race("flemington", "2024-11-05", race_number=7)

            # Display results
            logger.info("\n" + "=" * 60)
            logger.info("SCRAPING RESULTS")
            logger.info("=" * 60)

            logger.info(f"\nRace: {race_card.race.race_name}")
            logger.info(f"Distance: {race_card.race.distance}m")
            logger.info(f"Track Condition: {race_card.race.track_condition}")
            logger.info(f"Prize Money: ${race_card.race.prize_money:,}")
            logger.info(f"Field Size: {race_card.race.field_size}")

            logger.info(f"\nRunners Found: {len(race_card.runs)}")
            logger.info(f"Horses: {len(race_card.horses)}")
            logger.info(f"Jockeys: {len(race_card.jockeys)}")
            logger.info(f"Trainers: {len(race_card.trainers)}")

            # Show first 5 runners
            if race_card.runs:
                logger.info("\nFirst 5 Runners:")
                for i, run in enumerate(race_card.runs[:5]):
                    horse = next((h for h in race_card.horses if h.horse_id == run.horse_id), None)
                    jockey = next((j for j in race_card.jockeys if j.jockey_id == run.jockey_id), None)
                    
                    horse_name = horse.name if horse else "Unknown"
                    jockey_name = jockey.name if jockey else "Unknown"
                    
                    logger.info(
                        f"  {run.barrier}. {horse_name} - "
                        f"{jockey_name} ({run.weight_carried}kg)"
                    )

            # Calculate completeness
            completeness = race_card.validate_completeness()
            logger.info(f"\n📊 Data Completeness: {completeness:.1f}%")

            if completeness >= 80:
                logger.info("✅ PASS - Completeness >= 80%")
            else:
                logger.warning(f"⚠️  FAIL - Completeness < 80% (need improvement)")

            logger.info("\n" + "=" * 60)

            return race_card, completeness >= 80

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return None, False


def test_multiple_races():
    """Test scraping multiple Melbourne Cup day races."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Multiple Races - Melbourne Cup Day 2024")
    logger.info("=" * 60)

    results = []

    try:
        with RacingComSeleniumScraper(headless=True) as scraper:
            # Test races 1, 5, 7, 10 (Melbourne Cup)
            test_races = [1, 5, 7, 10]

            for race_num in test_races:
                logger.info(f"\nScraping Flemington R{race_num}...")
                
                try:
                    race_card = scraper.scrape_race(
                        "flemington", "2024-11-05", race_number=race_num
                    )
                    
                    completeness = race_card.validate_completeness()
                    runners = len(race_card.runs)
                    
                    results.append({
                        "race": race_num,
                        "completeness": completeness,
                        "runners": runners,
                        "pass": completeness >= 80,
                    })
                    
                    logger.info(
                        f"  R{race_num}: {runners} runners, "
                        f"{completeness:.1f}% complete "
                        f"{'✅' if completeness >= 80 else '⚠️'}"
                    )
                
                except Exception as e:
                    logger.error(f"  R{race_num}: Failed - {e}")
                    results.append({
                        "race": race_num,
                        "completeness": 0,
                        "runners": 0,
                        "pass": False,
                    })

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for r in results if r["pass"])
        total = len(results)
        avg_completeness = sum(r["completeness"] for r in results) / total if total > 0 else 0
        
        logger.info(f"Tests Passed: {passed}/{total}")
        logger.info(f"Average Completeness: {avg_completeness:.1f}%")
        
        if passed == total:
            logger.info("✅ ALL TESTS PASSED")
        else:
            logger.warning(f"⚠️  {total - passed} test(s) failed")

        logger.info("=" * 60)

        return results, passed == total

    except Exception as e:
        logger.error(f"❌ Multiple race test failed: {e}", exc_info=True)
        return [], False


if __name__ == "__main__":
    logger.info("Starting Racing.com Scraper Tests\n")

    # Test 1: Melbourne Cup
    logger.info("TEST 1: Melbourne Cup 2024 (Flemington R7)")
    race_card, test1_pass = test_melbourne_cup()

    # Test 2: Multiple races
    logger.info("\n\nTEST 2: Multiple Races")
    results, test2_pass = test_multiple_races()

    # Final result
    logger.info("\n" + "=" * 60)
    logger.info("FINAL RESULT")
    logger.info("=" * 60)
    
    if test1_pass and test2_pass:
        logger.info("✅ ALL TESTS PASSED - Scraper is functional!")
        sys.exit(0)
    else:
        logger.warning("⚠️  SOME TESTS FAILED - Scraper needs refinement")
        logger.info("\nNext steps:")
        logger.info("1. Inspect actual Racing.com HTML in browser DevTools")
        logger.info("2. Update CSS selectors in racing_com_selenium.py")
        logger.info("3. Test again")
        sys.exit(1)
