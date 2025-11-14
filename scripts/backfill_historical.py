#!/usr/bin/env python3
"""
Historical Data Backfill Script

Populates database with 200+ historical races from Spring Carnival 2024.
This is a PREREQUISITE for Phase 2 (Qualitative Pipeline).

Usage:
    python scripts/backfill_historical.py --venue flemington --start 2024-10-01 --end 2024-11-30
    python scripts/backfill_historical.py --all  # All 5 venues, Oct-Nov 2024
    python scripts/backfill_historical.py --sample  # 20 races for testing
"""

import sys
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Optional
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.models import Race, Run, Result, Horse, Jockey, Trainer
from src.data.scrapers.racing_com_graphql import RacingComGraphQLScraper
from src.data.scrapers.betfair_client import BetfairClient
from src.data.scrapers.weather_api import WeatherAPI
import duckdb

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HistoricalDataBackfill:
    """Backfill historical races from Spring Carnival 2024"""

    # Target venues for backfill
    VENUES = {
        'flemington': {'state': 'VIC', 'min_races': 50},
        'caulfield': {'state': 'VIC', 'min_races': 40},
        'moonee-valley': {'state': 'VIC', 'min_races': 30},
        'randwick': {'state': 'NSW', 'min_races': 40},
        'rosehill': {'state': 'NSW', 'min_races': 40},
    }

    def __init__(self, db_path: str = 'racing.db'):
        """Initialize backfill system"""
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)

        # Initialize scrapers
        self.graphql_scraper = RacingComGraphQLScraper()
        self.weather_api = WeatherAPI()
        # Note: Betfair requires credentials, will skip if not available

        self.stats = {
            'races_attempted': 0,
            'races_successful': 0,
            'races_failed': 0,
            'runners_total': 0,
            'errors': []
        }

    def backfill_all_venues(self, start_date: date, end_date: date):
        """Backfill all target venues for date range"""
        logger.info(f"Starting backfill: {start_date} to {end_date}")

        total_races_target = sum(v['min_races'] for v in self.VENUES.values())
        logger.info(f"Target: {total_races_target} races across {len(self.VENUES)} venues")

        for venue, venue_config in self.VENUES.items():
            logger.info(f"\n{'='*70}")
            logger.info(f"VENUE: {venue.upper()} (target: {venue_config['min_races']} races)")
            logger.info(f"{'='*70}")

            self.backfill_venue(venue, start_date, end_date)

        self.print_summary()

    def backfill_venue(self, venue: str, start_date: date, end_date: date):
        """Backfill single venue for date range"""
        races_for_venue = 0
        current_date = start_date

        while current_date <= end_date:
            logger.info(f"\n{venue} - {current_date}")

            try:
                # Get race meetings for this venue/date
                race_list = self.graphql_scraper.get_races(venue, current_date)

                if not race_list:
                    logger.debug(f"  No races found")
                    current_date += timedelta(days=1)
                    continue

                logger.info(f"  Found {len(race_list)} races")

                for race_num, race_data in enumerate(race_list, 1):
                    try:
                        self.backfill_race(venue, current_date, race_num, race_data)
                        races_for_venue += 1

                    except Exception as e:
                        logger.error(f"  Race {race_num} failed: {e}")
                        self.stats['races_failed'] += 1
                        self.stats['errors'].append({
                            'venue': venue,
                            'date': current_date,
                            'race_num': race_num,
                            'error': str(e)
                        })

                current_date += timedelta(days=1)

            except Exception as e:
                logger.error(f"Venue {venue} on {current_date} failed: {e}")
                self.stats['errors'].append({
                    'venue': venue,
                    'date': current_date,
                    'error': str(e)
                })
                current_date += timedelta(days=1)

        logger.info(f"\n{venue}: {races_for_venue} races successfully backfilled")

    def backfill_race(self, venue: str, race_date: date, race_num: int, race_data: dict):
        """Backfill single race"""
        self.stats['races_attempted'] += 1

        # Extract race details from GraphQL data
        race = Race(
            race_id=f"{venue.upper()}-{race_date}-R{race_num}",
            venue=venue,
            date=race_date,
            race_number=race_num,
            race_name=race_data.get('name', f"Race {race_num}"),
            distance=race_data.get('distance', 0),
            track_condition=race_data.get('condition', 'Unknown'),
            rail_position=race_data.get('rail_position'),
            class_type=race_data.get('class', 'UNKNOWN'),
            prize_money=race_data.get('prize', 0),
        )

        # Store race
        self.conn.execute("""
            INSERT INTO races (race_id, venue, date, race_number, race_name, distance, 
                              track_condition, rail_position, class_type, prize_money)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            race.race_id, race.venue, race.date, race.race_number, race.race_name,
            race.distance, race.track_condition, race.rail_position, race.class_type,
            race.prize_money
        ])

        # Process runners
        if 'runners' in race_data:
            for runner_data in race_data['runners']:
                self._process_runner(race.race_id, runner_data)

        self.stats['races_successful'] += 1
        logger.info(f"  ✓ R{race_num}: {race.race_name} ({race.distance}m)")

    def _process_runner(self, race_id: str, runner_data: dict):
        """Process single runner and insert into database"""
        # Extract horse
        horse_id = runner_data.get('horse_id', f"HORSE-{runner_data.get('name', 'UNKNOWN')}")
        horse_name = runner_data.get('name', 'Unknown Horse')

        # Extract jockey
        jockey_id = runner_data.get('jockey_id', 'UNKNOWN')
        jockey_name = runner_data.get('jockey_name', 'Unknown Jockey')

        # Extract trainer
        trainer_id = runner_data.get('trainer_id', 'UNKNOWN')
        trainer_name = runner_data.get('trainer_name', 'Unknown Trainer')

        # Insert or get horse
        self.conn.execute("""
            INSERT OR IGNORE INTO horses (horse_id, name) VALUES (?, ?)
        """, [horse_id, horse_name])

        # Insert or get jockey
        self.conn.execute("""
            INSERT OR IGNORE INTO jockeys (jockey_id, name) VALUES (?, ?)
        """, [jockey_id, jockey_name])

        # Insert or get trainer
        self.conn.execute("""
            INSERT OR IGNORE INTO trainers (trainer_id, name) VALUES (?, ?)
        """, [trainer_id, trainer_name])

        # Insert run
        run_id = f"{race_id}-{runner_data.get('barrier', 0)}"

        self.conn.execute("""
            INSERT INTO runs (
                run_id, race_id, horse_id, jockey_id, trainer_id, barrier,
                weight, scratched, data_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            run_id, race_id, horse_id, jockey_id, trainer_id,
            runner_data.get('barrier', 0),
            runner_data.get('weight', 0),
            runner_data.get('scratched', False),
            'racing_com'
        ])

        # If race has results, insert those too
        if 'result' in runner_data:
            result = Result(
                run_id=run_id,
                finish_position=runner_data['result'].get('position'),
                margin=runner_data['result'].get('margin'),
                starting_price=runner_data['result'].get('sp'),
                data_source='racing_com'
            )

            self.conn.execute("""
                INSERT INTO results (run_id, finish_position, margin, starting_price, data_source)
                VALUES (?, ?, ?, ?, ?)
            """, [
                result.run_id, result.finish_position, result.margin,
                result.starting_price, result.data_source
            ])

        self.stats['runners_total'] += 1

    def print_summary(self):
        """Print backfill summary"""
        logger.info(f"\n{'='*70}")
        logger.info("BACKFILL SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"Races attempted: {self.stats['races_attempted']}")
        logger.info(f"Races successful: {self.stats['races_successful']}")
        logger.info(f"Races failed: {self.stats['races_failed']}")
        logger.info(f"Total runners: {self.stats['runners_total']}")

        if self.stats['errors']:
            logger.warning(f"\nErrors ({len(self.stats['errors'])} total):")
            for error in self.stats['errors'][:10]:  # Show first 10
                logger.warning(f"  - {error}")

        success_rate = (
            self.stats['races_successful'] / self.stats['races_attempted'] * 100
            if self.stats['races_attempted'] > 0 else 0
        )
        logger.info(f"\nSuccess rate: {success_rate:.1f}%")
        logger.info(f"{'='*70}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Backfill historical racing data'
    )
    parser.add_argument(
        '--venue',
        help='Single venue to backfill'
    )
    parser.add_argument(
        '--start',
        type=lambda s: date.fromisoformat(s),
        default=date(2024, 10, 1),
        help='Start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end',
        type=lambda s: date.fromisoformat(s),
        default=date(2024, 11, 30),
        help='End date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Backfill all venues'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Backfill 20 races for testing'
    )
    parser.add_argument(
        '--db',
        default='racing.db',
        help='Database path'
    )

    args = parser.parse_args()

    backfill = HistoricalDataBackfill(db_path=args.db)

    if args.sample:
        logger.info("Running SAMPLE backfill (20 races)")
        backfill.backfill_venue('flemington', date(2024, 11, 1), date(2024, 11, 5))

    elif args.all:
        logger.info("Running ALL VENUES backfill")
        backfill.backfill_all_venues(args.start, args.end)

    elif args.venue:
        logger.info(f"Backfilling {args.venue}")
        backfill.backfill_venue(args.venue, args.start, args.end)

    else:
        logger.info("Running DEFAULT backfill (all venues, Oct-Nov 2024)")
        backfill.backfill_all_venues(args.start, args.end)


if __name__ == '__main__':
    main()
