"""
ETL Pipeline for racing data ingestion.

This pipeline orchestrates:
1. Scraping: Collect data from multiple sources
2. Validation: Validate using Pydantic models
3. Loading: Insert into DuckDB database

Features:
- Error handling and retry logic
- Data quality monitoring
- Logging and metrics
- Idempotent operations (safe re-runs)

Usage:
    from src.data.etl_pipeline import RacingETL

    etl = RacingETL()
    etl.ingest_race("FLE", "2025-11-12", race_number=1)
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from pathlib import Path

import duckdb
from pydantic import ValidationError

from src.data.models import RaceCard
from src.data.scrapers import MarketOddsCollector, RacingComScraper, StewardsScraper

logger = logging.getLogger(__name__)


class RacingETL:
    """
    ETL pipeline for racing data.

    Handles complete data flow:
    - Extract: Scrape from Racing.com, stewards, odds
    - Transform: Validate with Pydantic models
    - Load: Insert into DuckDB with conflict resolution
    """

    def __init__(self, db_path: str | Path = "data/racing.duckdb"):
        """
        Initialize ETL pipeline.

        Args:
            db_path: Path to DuckDB database
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {db_path}. Run init_db.py first."
            )

        self.race_scraper = RacingComScraper()
        self.stewards_scraper = StewardsScraper()
        self.odds_collector = MarketOddsCollector()

        logger.info(f"ETL pipeline initialized with database: {db_path}")

    def ingest_race(self, venue: str, race_date: date | str, race_number: int) -> dict:
        """
        Ingest complete race data.

        Args:
            venue: Venue code (e.g., 'FLE', 'RAN')
            race_date: Race date
            race_number: Race number

        Returns:
            dict with ingestion metrics
        """
        if isinstance(race_date, str):
            race_date = date.fromisoformat(race_date)

        race_id = f"{venue}-{race_date.isoformat()}-R{race_number}"

        logger.info(f"Starting ingestion for {race_id}")

        metrics = {
            "race_id": race_id,
            "status": "started",
            "scraped": {},
            "validated": {},
            "inserted": {},
            "errors": [],
        }

        try:
            # EXTRACT: Scrape data from sources
            logger.info(f"Extracting data for {race_id}")

            race_card = self.race_scraper.scrape_race(venue, race_date, race_number)
            metrics["scraped"]["race_card"] = True
            metrics["scraped"]["runners"] = len(race_card.runs)

            stewards_reports = self.stewards_scraper.scrape_race_reports(
                venue, race_date, race_number
            )
            metrics["scraped"]["stewards"] = len(stewards_reports)

            odds_data = self.odds_collector.collect_starting_prices(
                venue, race_date, race_number
            )
            metrics["scraped"]["odds"] = len(odds_data)

            # TRANSFORM: Validate data
            logger.info(f"Validating data for {race_id}")

            try:
                # Race card is already validated via Pydantic
                completeness = race_card.validate_completeness()
                metrics["validated"]["race_card"] = True
                metrics["validated"]["completeness"] = completeness

                if completeness < 80.0:
                    logger.warning(
                        f"Race card completeness below threshold: {completeness:.1f}%"
                    )
                    metrics["errors"].append(
                        f"Low completeness: {completeness:.1f}% (threshold: 80%)"
                    )

            except ValidationError as e:
                logger.error(f"Validation error for race card: {e}")
                metrics["errors"].append(f"Validation error: {str(e)}")
                metrics["status"] = "failed"
                return metrics

            # LOAD: Insert into database
            logger.info(f"Loading data for {race_id}")

            con = duckdb.connect(str(self.db_path))
            try:
                # Insert race
                self._insert_race(con, race_card.race)
                metrics["inserted"]["race"] = 1

                # Insert master data (horses, jockeys, trainers)
                self._insert_horses(con, race_card.horses)
                metrics["inserted"]["horses"] = len(race_card.horses)

                self._insert_jockeys(con, race_card.jockeys)
                metrics["inserted"]["jockeys"] = len(race_card.jockeys)

                self._insert_trainers(con, race_card.trainers)
                metrics["inserted"]["trainers"] = len(race_card.trainers)

                # Insert runs
                self._insert_runs(con, race_card.runs)
                metrics["inserted"]["runs"] = len(race_card.runs)

                # Insert gear
                if race_card.gear:
                    self._insert_gear(con, race_card.gear)
                    metrics["inserted"]["gear"] = len(race_card.gear)

                # Insert stewards reports
                if stewards_reports:
                    self._insert_stewards(con, stewards_reports)
                    metrics["inserted"]["stewards"] = len(stewards_reports)

                # Insert odds (temporarily skip to avoid FK constraint - will fix in Week 2)
                # TODO: Week 2 - Integrate odds with actual run_ids from race card
                # if odds_data:
                #     self._insert_odds(con, odds_data)
                #     metrics["inserted"]["odds"] = len(odds_data)
                metrics["inserted"]["odds"] = 0  # Placeholder

                con.commit()
                metrics["status"] = "success"
                logger.info(f"Successfully ingested {race_id}")

            except Exception as e:
                logger.error(f"Database error: {e}", exc_info=True)
                con.rollback()
                metrics["errors"].append(f"Database error: {str(e)}")
                metrics["status"] = "failed"
                raise

            finally:
                con.close()

        except Exception as e:
            logger.error(f"ETL failed for {race_id}: {e}", exc_info=True)
            metrics["errors"].append(str(e))
            metrics["status"] = "failed"

        return metrics

    def _insert_race(self, con: duckdb.DuckDBPyConnection, race) -> None:
        """Insert race (with conflict resolution)."""
        con.execute(
            """
            INSERT OR REPLACE INTO races (
                race_id, date, venue, venue_name, race_number, race_name,
                distance, track_condition, track_type, rail_position, weather,
                class_level, prize_money, race_time, actual_start_time,
                field_size, race_type, age_restriction, sex_restriction,
                scraped_at, data_source, is_complete
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                race.rail_position,
                race.weather,
                race.class_level,
                race.prize_money,
                race.race_time,
                race.actual_start_time,
                race.field_size,
                race.race_type,
                race.age_restriction,
                race.sex_restriction,
                race.scraped_at,
                race.data_source,
                race.is_complete,
            ],
        )

    def _insert_horses(self, con: duckdb.DuckDBPyConnection, horses: list) -> None:
        """Insert horses (upsert - update if exists)."""
        for horse in horses:
            con.execute(
                """
                INSERT OR REPLACE INTO horses (
                    horse_id, name, foaling_date, age, sex, color,
                    sire, sire_id, dam, dam_id, dam_sire, breeder, country, owner,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    horse.horse_id,
                    horse.name,
                    horse.foaling_date,
                    horse.age,
                    horse.sex,
                    horse.color,
                    horse.sire,
                    horse.sire_id,
                    horse.dam,
                    horse.dam_id,
                    horse.dam_sire,
                    horse.breeder,
                    horse.country,
                    horse.owner,
                    horse.created_at,
                    datetime.now(),  # Update timestamp
                ],
            )

    def _insert_jockeys(self, con: duckdb.DuckDBPyConnection, jockeys: list) -> None:
        """Insert jockeys (upsert)."""
        for jockey in jockeys:
            con.execute(
                """
                INSERT OR REPLACE INTO jockeys (
                    jockey_id, name, active_since, apprentice, claim_weight,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    jockey.jockey_id,
                    jockey.name,
                    jockey.active_since,
                    jockey.apprentice,
                    jockey.claim_weight,
                    jockey.created_at,
                    datetime.now(),
                ],
            )

    def _insert_trainers(self, con: duckdb.DuckDBPyConnection, trainers: list) -> None:
        """Insert trainers (upsert)."""
        for trainer in trainers:
            con.execute(
                """
                INSERT OR REPLACE INTO trainers (
                    trainer_id, name, stable_location, state, active_since,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    trainer.trainer_id,
                    trainer.name,
                    trainer.stable_location,
                    trainer.state,
                    trainer.active_since,
                    trainer.created_at,
                    datetime.now(),
                ],
            )

    def _insert_runs(self, con: duckdb.DuckDBPyConnection, runs: list) -> None:
        """Insert runs."""
        for run in runs:
            con.execute(
                """
                INSERT OR REPLACE INTO runs (
                    run_id, race_id, horse_id, jockey_id, trainer_id,
                    barrier, weight_carried, handicap_weight, weight_penalty,
                    emergency, scratched, scratched_time, late_scratching,
                    runner_number, saddle_cloth, starting_price_win, starting_price_place,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    run.run_id,
                    run.race_id,
                    run.horse_id,
                    run.jockey_id,
                    run.trainer_id,
                    run.barrier,
                    run.weight_carried,
                    run.handicap_weight,
                    run.weight_penalty,
                    run.emergency,
                    run.scratched,
                    run.scratched_time,
                    run.late_scratching,
                    run.runner_number,
                    run.saddle_cloth,
                    run.starting_price_win,
                    run.starting_price_place,
                    run.created_at,
                ],
            )

    def _insert_gear(self, con: duckdb.DuckDBPyConnection, gear_list: list) -> None:
        """Insert gear."""
        for gear in gear_list:
            con.execute(
                """
                INSERT OR REPLACE INTO gear (
                    gear_id, run_id, gear_type, gear_code, first_time,
                    removed, change_type, previous_gear
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    gear.gear_id,
                    gear.run_id,
                    gear.gear_type,
                    gear.gear_code,
                    gear.first_time,
                    gear.removed,
                    gear.change_type,
                    gear.previous_gear,
                ],
            )

    def _insert_stewards(self, con: duckdb.DuckDBPyConnection, reports: list) -> None:
        """Insert stewards reports."""
        for report in reports:
            # Keep lists as-is for DuckDB arrays
            horses_list = report.horses_involved if report.horses_involved else None
            jockeys_list = report.jockeys_involved if report.jockeys_involved else None

            con.execute(
                """
                INSERT OR REPLACE INTO stewards (
                    steward_id, race_id, run_id, report_type, report_text,
                    incident_description, action_taken, horses_involved,
                    jockeys_involved, severity, outcome, published_at, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    report.steward_id,
                    report.race_id,
                    report.run_id,
                    report.report_type,
                    report.report_text,
                    report.incident_description,
                    report.action_taken,
                    horses_list,
                    jockeys_list,
                    report.severity,
                    report.outcome,
                    report.published_at,
                    report.scraped_at,
                ],
            )

    def _insert_odds(self, con: duckdb.DuckDBPyConnection, odds_list: list) -> None:
        """Insert market odds."""
        for odds in odds_list:
            con.execute(
                """
                INSERT OR REPLACE INTO market_odds (
                    odds_id, run_id, race_id, timestamp, source, odds_type,
                    odds_decimal, odds_fractional, odds_american,
                    volume, market_percentage, rank
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    odds.odds_id,
                    odds.run_id,
                    odds.race_id,
                    odds.timestamp,
                    odds.source,
                    odds.odds_type,
                    odds.odds_decimal,
                    odds.odds_fractional,
                    odds.odds_american,
                    odds.volume,
                    odds.market_percentage,
                    odds.rank,
                ],
            )

    def get_data_quality_report(self) -> dict:
        """
        Generate data quality report.

        Returns:
            dict with quality metrics
        """
        con = duckdb.connect(str(self.db_path), read_only=True)

        try:
            # Count incomplete races
            incomplete_races = con.execute(
                "SELECT COUNT(*) FROM v_incomplete_races"
            ).fetchone()[0]

            # Count incomplete runs
            incomplete_runs = con.execute(
                "SELECT COUNT(*) FROM v_incomplete_runs"
            ).fetchone()[0]

            # Total races
            total_races = con.execute("SELECT COUNT(*) FROM races").fetchone()[0]

            # Total runs
            total_runs = con.execute("SELECT COUNT(*) FROM runs").fetchone()[0]

            report = {
                "total_races": total_races,
                "incomplete_races": incomplete_races,
                "race_completeness": (
                    (total_races - incomplete_races) / total_races * 100
                    if total_races > 0
                    else 0
                ),
                "total_runs": total_runs,
                "incomplete_runs": incomplete_runs,
                "run_completeness": (
                    (total_runs - incomplete_runs) / total_runs * 100
                    if total_runs > 0
                    else 0
                ),
            }

            return report

        finally:
            con.close()

    def close(self):
        """Cleanup resources."""
        self.race_scraper.close()
        self.stewards_scraper.close()
        self.odds_collector.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with RacingETL() as etl:
        # Ingest a race
        metrics = etl.ingest_race("FLE", date.today(), 1)

        print("\nIngestion Metrics:")
        print(f"  Status: {metrics['status']}")
        print(f"  Race ID: {metrics['race_id']}")
        print(f"\n  Scraped:")
        for key, val in metrics["scraped"].items():
            print(f"    {key}: {val}")
        print(f"\n  Inserted:")
        for key, val in metrics["inserted"].items():
            print(f"    {key}: {val}")

        if metrics["errors"]:
            print(f"\n  Errors: {len(metrics['errors'])}")
            for err in metrics["errors"]:
                print(f"    - {err}")

        # Get quality report
        quality = etl.get_data_quality_report()
        print("\nData Quality Report:")
        print(f"  Total races: {quality['total_races']}")
        print(f"  Race completeness: {quality['race_completeness']:.1f}%")
        print(f"  Total runs: {quality['total_runs']}")
        print(f"  Run completeness: {quality['run_completeness']:.1f}%")
