"""
End-to-end test: Ingest 5 races and verify data quality.

This script:
1. Ingests 5 race cards through the ETL pipeline
2. Validates data completeness (80%+ threshold)
3. Generates data quality reports
4. Verifies database integrity
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from src.data.etl_pipeline import RacingETL

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_ingest_5_races():
    """Test ingesting 5 races."""
    print("=" * 70)
    print("END-TO-END TEST: Ingest 5 Races")
    print("=" * 70)

    # Test scenarios: Different venues and race numbers
    test_races = [
        ("FLE", date.today(), 1),
        ("FLE", date.today(), 2),
        ("RAN", date.today(), 1),
        ("CAU", date.today(), 1),
        ("MOR", date.today(), 1),
    ]

    with RacingETL() as etl:
        results = []

        print("\n" + "-" * 70)
        print("INGESTION PHASE")
        print("-" * 70)

        for venue, race_date, race_number in test_races:
            race_id = f"{venue}-{race_date.isoformat()}-R{race_number}"
            print(f"\nIngesting: {race_id}")

            metrics = etl.ingest_race(venue, race_date, race_number)
            results.append(metrics)

            if metrics["status"] == "success":
                print(f"  ✓ SUCCESS")
                print(f"    Runners: {metrics['scraped']['runners']}")
                print(
                    f"    Completeness: {metrics['validated']['completeness']:.1f}%"
                )
                print(
                    f"    Inserted: {metrics['inserted']['runs']} runs, "
                    f"{metrics['inserted']['horses']} horses"
                )
            else:
                print(f"  ✗ FAILED")
                for err in metrics.get("errors", []):
                    print(f"    Error: {err}")

        print("\n" + "-" * 70)
        print("VALIDATION PHASE")
        print("-" * 70)

        # Check success rate
        successful = sum(1 for r in results if r["status"] == "success")
        success_rate = (successful / len(results) * 100) if results else 0

        print(f"\nIngestion Success Rate: {success_rate:.0f}%")
        print(f"  Successful: {successful}/{len(results)}")

        if success_rate < 80:
            print(f"  ✗ FAIL: Below 80% threshold")
            return False

        print(f"  ✓ PASS: Meets 80% threshold")

        # Check data completeness
        print("\nData Completeness:")
        for result in results:
            if result["status"] == "success":
                completeness = result["validated"]["completeness"]
                race_id = result["race_id"]

                if completeness >= 80.0:
                    print(f"  ✓ {race_id}: {completeness:.1f}%")
                else:
                    print(f"  ✗ {race_id}: {completeness:.1f}% (below threshold)")

        # Get overall data quality report
        print("\n" + "-" * 70)
        print("DATA QUALITY REPORT")
        print("-" * 70)

        quality = etl.get_data_quality_report()

        print(f"\nDatabase Statistics:")
        print(f"  Total races: {quality['total_races']}")
        print(f"  Incomplete races: {quality['incomplete_races']}")
        print(f"  Race completeness: {quality['race_completeness']:.1f}%")
        print()
        print(f"  Total runs: {quality['total_runs']}")
        print(f"  Incomplete runs: {quality['incomplete_runs']}")
        print(f"  Run completeness: {quality['run_completeness']:.1f}%")

        # Overall pass/fail
        print("\n" + "=" * 70)

        if success_rate >= 80.0 and quality["race_completeness"] >= 80.0:
            print("END-TO-END TEST: ✓ PASSED")
            print("=" * 70)
            print("\nKey Achievements:")
            print(f"  ✓ {successful}/{len(results)} races ingested successfully")
            print(
                f"  ✓ {quality['race_completeness']:.1f}% race data completeness"
            )
            print(f"  ✓ {quality['run_completeness']:.1f}% run data completeness")
            print(f"  ✓ {quality['total_runs']} total runners in database")
            print("\nWeek 1 objectives COMPLETE! Ready for Week 2.")
            return True
        else:
            print("END-TO-END TEST: ✗ FAILED")
            print("=" * 70)
            return False


def main():
    """Run end-to-end test."""
    print("\n" + "=" * 70)
    print("PHASE 1 WEEK 1 - END-TO-END TEST")
    print("=" * 70 + "\n")

    try:
        success = test_ingest_5_races()
        return 0 if success else 1

    except Exception as e:
        logger.error(f"End-to-end test failed: {e}", exc_info=True)
        print(f"\n✗ TEST FAILED: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
