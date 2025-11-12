"""
Test script to verify database creation and data insertion.

This script:
1. Verifies database schema
2. Creates sample racing data using Pydantic models
3. Inserts data into DuckDB
4. Queries data to verify integrity
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

import duckdb

from src.data.models import Race, Horse, Jockey, Trainer, Run

# Database path
DB_PATH = "data/racing.duckdb"


def test_database_schema():
    """Test 1: Verify database schema is complete"""
    print("=" * 60)
    print("TEST 1: Database Schema Verification")
    print("=" * 60)

    con = duckdb.connect(DB_PATH, read_only=True)

    # Check tables
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    expected_tables = {
        "races",
        "horses",
        "jockeys",
        "trainers",
        "runs",
        "results",
        "market_odds",
        "stewards",
        "gear",
    }

    print(f"Expected tables: {len(expected_tables)}")
    print(f"Actual tables:   {len(tables & expected_tables)}")

    # Check views
    views_query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'VIEW'"
    views = {row[0] for row in con.execute(views_query).fetchall()}
    expected_views = {
        "v_race_card",
        "v_race_results",
        "v_incomplete_races",
        "v_incomplete_runs",
    }

    print(f"Expected views:  {len(expected_views)}")
    print(f"Actual views:    {len(views & expected_views)}")

    con.close()

    # Verify
    assert tables >= expected_tables, f"Missing tables: {expected_tables - tables}"
    assert views >= expected_views, f"Missing views: {expected_views - views}"

    print("✓ Schema verification PASSED\n")


def test_pydantic_models():
    """Test 2: Verify Pydantic models validate correctly"""
    print("=" * 60)
    print("TEST 2: Pydantic Model Validation")
    print("=" * 60)

    # Create sample race
    race = Race(
        race_id="FLE-2025-11-12-R1",
        date=date(2025, 11, 12),
        venue="FLE",
        venue_name="Flemington",
        race_number=1,
        race_name="Maidens Plate",
        distance=1200,
        track_condition="Good 4",
        track_type="turf",
        class_level="Maiden",
        prize_money=50000,
        race_time=time(12, 30),
        field_size=12,
        scraped_at=datetime.now(),
        data_source="racing.com",
    )
    print(f"✓ Created race: {race.race_id}")

    # Create sample horse
    horse = Horse(
        horse_id="H12345",
        name="Test Runner",
        age=3,
        sex="colt",
        sire="Fastnet Rock",
        dam="Test Mare",
        dam_sire="More Than Ready",
    )
    print(f"✓ Created horse: {horse.name}")

    # Create sample jockey
    jockey = Jockey(
        jockey_id="J123",
        name="John Smith",
        apprentice=False,
    )
    print(f"✓ Created jockey: {jockey.name}")

    # Create sample trainer
    trainer = Trainer(
        trainer_id="T456",
        name="Jane Doe",
        state="VIC",
    )
    print(f"✓ Created trainer: {trainer.name}")

    # Create sample run
    run = Run(
        run_id="RUN-FLE-2025-11-12-R1-H12345",
        race_id=race.race_id,
        horse_id=horse.horse_id,
        jockey_id=jockey.jockey_id,
        trainer_id=trainer.trainer_id,
        barrier=5,
        weight_carried=Decimal("58.5"),
    )
    print(f"✓ Created run: {run.run_id}")

    print("✓ All models validated successfully\n")

    return race, horse, jockey, trainer, run


def test_data_insertion(race, horse, jockey, trainer, run):
    """Test 3: Insert data into database"""
    print("=" * 60)
    print("TEST 3: Data Insertion")
    print("=" * 60)

    con = duckdb.connect(DB_PATH)

    try:
        # Insert race
        con.execute(
            """
            INSERT INTO races (
                race_id, date, venue, venue_name, race_number, race_name,
                distance, track_condition, track_type, class_level,
                prize_money, race_time, field_size, scraped_at,
                data_source, is_complete
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                race.race_id,
                race.date,
                race.venue,
                race.venue_name,
                race.race_number,
                race.race_name,
                race.distance,
                race.track_condition,
                race.track_type,
                race.class_level,
                race.prize_money,
                race.race_time,
                race.field_size,
                race.scraped_at,
                race.data_source,
                race.is_complete,
            ],
        )
        print(f"✓ Inserted race: {race.race_id}")

        # Insert horse
        con.execute(
            """
            INSERT INTO horses (
                horse_id, name, age, sex, sire, dam, dam_sire, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                horse.horse_id,
                horse.name,
                horse.age,
                horse.sex,
                horse.sire,
                horse.dam,
                horse.dam_sire,
                horse.created_at,
                horse.updated_at,
            ],
        )
        print(f"✓ Inserted horse: {horse.name}")

        # Insert jockey
        con.execute(
            """
            INSERT INTO jockeys (
                jockey_id, name, apprentice, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?)
        """,
            [
                jockey.jockey_id,
                jockey.name,
                jockey.apprentice,
                jockey.created_at,
                jockey.updated_at,
            ],
        )
        print(f"✓ Inserted jockey: {jockey.name}")

        # Insert trainer
        con.execute(
            """
            INSERT INTO trainers (
                trainer_id, name, state, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?)
        """,
            [
                trainer.trainer_id,
                trainer.name,
                trainer.state,
                trainer.created_at,
                trainer.updated_at,
            ],
        )
        print(f"✓ Inserted trainer: {trainer.name}")

        # Insert run
        con.execute(
            """
            INSERT INTO runs (
                run_id, race_id, horse_id, jockey_id, trainer_id,
                barrier, weight_carried, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                run.run_id,
                run.race_id,
                run.horse_id,
                run.jockey_id,
                run.trainer_id,
                run.barrier,
                run.weight_carried,
                run.created_at,
            ],
        )
        print(f"✓ Inserted run: {run.run_id}")

        con.commit()
        print("✓ All data committed successfully\n")

    except Exception as e:
        print(f"✗ Insertion failed: {e}")
        con.rollback()
        raise
    finally:
        con.close()


def test_data_queries():
    """Test 4: Query data and verify views work"""
    print("=" * 60)
    print("TEST 4: Data Queries & Views")
    print("=" * 60)

    con = duckdb.connect(DB_PATH, read_only=True)

    # Query race card view
    race_card = con.execute(
        """
        SELECT race_id, horse_name, jockey_name, trainer_name, barrier, weight_carried
        FROM v_race_card
        WHERE race_id = 'FLE-2025-11-12-R1'
    """
    ).fetchall()

    print(f"Race card entries: {len(race_card)}")
    if race_card:
        print(f"  Horse: {race_card[0][1]}")
        print(f"  Jockey: {race_card[0][2]}")
        print(f"  Trainer: {race_card[0][3]}")
        print(f"  Barrier: {race_card[0][4]}")
        print(f"  Weight: {race_card[0][5]}")

    # Check data quality view
    incomplete_races = con.execute("SELECT * FROM v_incomplete_races").fetchall()
    print(f"\nIncomplete races: {len(incomplete_races)}")

    con.close()

    assert len(race_card) == 1, "Expected 1 runner in race card"
    print("✓ Query tests PASSED\n")


def cleanup_test_data():
    """Clean up test data"""
    print("=" * 60)
    print("CLEANUP: Removing test data")
    print("=" * 60)

    con = duckdb.connect(DB_PATH)

    try:
        con.execute("DELETE FROM runs WHERE race_id = 'FLE-2025-11-12-R1'")
        con.execute("DELETE FROM races WHERE race_id = 'FLE-2025-11-12-R1'")
        con.execute("DELETE FROM horses WHERE horse_id = 'H12345'")
        con.execute("DELETE FROM jockeys WHERE jockey_id = 'J123'")
        con.execute("DELETE FROM trainers WHERE trainer_id = 'T456'")
        con.commit()
        print("✓ Test data removed\n")
    finally:
        con.close()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RACING ANALYSIS DATABASE TESTS")
    print("=" * 60 + "\n")

    try:
        # Test 1: Schema
        test_database_schema()

        # Test 2: Pydantic models
        race, horse, jockey, trainer, run = test_pydantic_models()

        # Test 3: Insert data
        test_data_insertion(race, horse, jockey, trainer, run)

        # Test 4: Query data
        test_data_queries()

        # Cleanup
        cleanup_test_data()

        # Summary
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nDatabase is ready for data ingestion!")

    except Exception as e:
        print(f"\n✗ TESTS FAILED: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
