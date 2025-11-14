"""
Jockey/Trainer Statistics Builder

This module:
- Calculates jockey and trainer statistics from database
- No web scraping required (pure database aggregation)
- Computes: win_rate, strike_rate, track_specialization, recent_form
- Supports flexible lookback periods

Usage:
    from src.data.scrapers.jockey_stats import JockeyStatsBuilder

    builder = JockeyStatsBuilder(db_connection)
    stats = builder.calculate_jockey_stats("JOCKEY123", lookback_days=365)
    trainer_stats = builder.calculate_trainer_stats("TRAINER456", lookback_days=180)
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

try:
    import duckdb
except ImportError:
    duckdb = None  # Make optional for testing

from src.data.models import JockeyStat, TrainerStat

logger = logging.getLogger(__name__)


class JockeyStatsBuilder:
    """
    Calculate jockey and trainer statistics from database.

    This is a pure database aggregation tool - no web scraping.
    It queries the existing race data and computes performance metrics.

    CONFIDENCE: HIGH - database queries are deterministic
    SQL aggregation is reliable and efficient.
    """

    def __init__(self, db_path: str = "racing.db"):
        """
        Initialize stats builder.

        Args:
            db_path: Path to DuckDB database
        """
        self.db_path = db_path
        self.conn: duckdb.DuckDBPyConnection | None = None

        logger.info(f"Initialized JockeyStatsBuilder (db={db_path})")

    def __enter__(self):
        """Context manager entry - open database connection."""
        if duckdb is None:
            raise ImportError("duckdb package required for stats builder")
        self.conn = duckdb.connect(self.db_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close database connection."""
        if self.conn:
            self.conn.close()

    def calculate_jockey_stats(
        self,
        jockey_id: str,
        lookback_days: int = 365,
        stat_date: date | None = None,
    ) -> JockeyStat:
        """
        Calculate comprehensive jockey statistics.

        Args:
            jockey_id: Jockey identifier
            lookback_days: Number of days to analyze (default: 365)
            stat_date: Date to calculate stats as of (default: today)

        Returns:
            JockeyStat model with all calculated metrics

        Calculations:
        - Overall win rate: wins / total rides
        - Place rate: (wins + places) / total rides
        - Strike rate: wins / rides where horse was competitive (top 50% of field)
        - Recent form: Last 14 days performance
        - Venue specialization: Venues where win_rate > overall
        - Distance performance: Breakdown by distance ranges

        CONFIDENCE: HIGH - SQL aggregation is reliable
        """
        if not self.conn:
            raise RuntimeError("Database not connected. Use context manager.")

        stat_date = stat_date or date.today()
        cutoff_date = stat_date - timedelta(days=lookback_days)

        logger.info(
            f"Calculating jockey stats: {jockey_id} "
            f"(period: {cutoff_date} to {stat_date})"
        )

        # Get overall statistics
        # CONFIDENCE: HIGH - standard SQL aggregation
        overall_query = """
            SELECT
                COUNT(*) as total_rides,
                SUM(CASE WHEN res.finish_position = 1 THEN 1 ELSE 0 END) as total_wins,
                SUM(CASE WHEN res.finish_position <= 3 THEN 1 ELSE 0 END) as total_places
            FROM runs r
            JOIN results res ON res.run_id = r.run_id
            JOIN races race ON race.race_id = r.race_id
            WHERE r.jockey_id = ?
              AND r.scratched = FALSE
              AND race.date BETWEEN ? AND ?
        """

        overall = self.conn.execute(
            overall_query, [jockey_id, cutoff_date, stat_date]
        ).fetchone()

        total_rides = overall[0] or 0
        total_wins = overall[1] or 0
        total_places = overall[2] or 0

        # Calculate rates
        win_rate = Decimal(total_wins) / Decimal(total_rides) if total_rides > 0 else Decimal(0)
        place_rate = Decimal(total_places) / Decimal(total_rides) if total_rides > 0 else Decimal(0)

        # Calculate strike rate (wins when horse was competitive)
        # CONFIDENCE: MEDIUM - "competitive" definition is heuristic
        strike_rate_query = """
            SELECT
                COUNT(*) as competitive_rides,
                SUM(CASE WHEN res.finish_position = 1 THEN 1 ELSE 0 END) as competitive_wins
            FROM runs r
            JOIN results res ON res.run_id = r.run_id
            JOIN races race ON race.race_id = r.race_id
            WHERE r.jockey_id = ?
              AND r.scratched = FALSE
              AND race.date BETWEEN ? AND ?
              AND res.finish_position <= (race.field_size / 2.0)  -- Top 50%
        """

        strike = self.conn.execute(
            strike_rate_query, [jockey_id, cutoff_date, stat_date]
        ).fetchone()

        competitive_rides = strike[0] or 0
        competitive_wins = strike[1] or 0
        strike_rate = (
            Decimal(competitive_wins) / Decimal(competitive_rides)
            if competitive_rides > 0
            else Decimal(0)
        )

        # Get recent form (last 14 days)
        recent_cutoff = stat_date - timedelta(days=14)
        recent_query = """
            SELECT
                COUNT(*) as recent_rides,
                SUM(CASE WHEN res.finish_position = 1 THEN 1 ELSE 0 END) as recent_wins
            FROM runs r
            JOIN results res ON res.run_id = r.run_id
            JOIN races race ON race.race_id = r.race_id
            WHERE r.jockey_id = ?
              AND r.scratched = FALSE
              AND race.date BETWEEN ? AND ?
        """

        recent = self.conn.execute(
            recent_query, [jockey_id, recent_cutoff, stat_date]
        ).fetchone()

        recent_rides = recent[0] or 0
        recent_wins = recent[1] or 0
        recent_win_rate = (
            Decimal(recent_wins) / Decimal(recent_rides)
            if recent_rides > 0
            else Decimal(0)
        )

        # Get venue-specific statistics
        venue_stats = self._calculate_venue_stats(
            jockey_id, cutoff_date, stat_date, is_jockey=True
        )

        # Get distance-specific statistics
        distance_stats = self._calculate_distance_stats(
            jockey_id, cutoff_date, stat_date, is_jockey=True
        )

        # Identify specialist venues (win_rate > overall)
        specialist_venues = [
            venue
            for venue, stats in venue_stats.items()
            if stats.get("win_rate", 0) > float(win_rate)
        ]

        # Create JockeyStat model
        jockey_stat = JockeyStat(
            jockey_id=jockey_id,
            stat_date=stat_date,
            lookback_days=lookback_days,
            total_rides=total_rides,
            total_wins=total_wins,
            total_places=total_places,
            win_rate=win_rate,
            place_rate=place_rate,
            strike_rate=strike_rate,
            recent_rides=recent_rides,
            recent_wins=recent_wins,
            recent_win_rate=recent_win_rate,
            venue_stats=venue_stats,
            distance_stats=distance_stats,
            specialist_venues=specialist_venues,
        )

        logger.info(
            f"✓ Calculated jockey stats: {jockey_id} - "
            f"{total_rides} rides, {total_wins} wins, "
            f"win_rate={win_rate:.3f}"
        )

        return jockey_stat

    def calculate_trainer_stats(
        self,
        trainer_id: str,
        lookback_days: int = 365,
        stat_date: date | None = None,
    ) -> TrainerStat:
        """
        Calculate comprehensive trainer statistics.

        Args:
            trainer_id: Trainer identifier
            lookback_days: Number of days to analyze
            stat_date: Date to calculate stats as of (default: today)

        Returns:
            TrainerStat model with all calculated metrics

        CONFIDENCE: HIGH - SQL aggregation is reliable
        """
        if not self.conn:
            raise RuntimeError("Database not connected. Use context manager.")

        stat_date = stat_date or date.today()
        cutoff_date = stat_date - timedelta(days=lookback_days)

        logger.info(
            f"Calculating trainer stats: {trainer_id} "
            f"(period: {cutoff_date} to {stat_date})"
        )

        # Get overall statistics
        overall_query = """
            SELECT
                COUNT(*) as total_runners,
                SUM(CASE WHEN res.finish_position = 1 THEN 1 ELSE 0 END) as total_wins,
                SUM(CASE WHEN res.finish_position <= 3 THEN 1 ELSE 0 END) as total_places
            FROM runs r
            JOIN results res ON res.run_id = r.run_id
            JOIN races race ON race.race_id = r.race_id
            WHERE r.trainer_id = ?
              AND r.scratched = FALSE
              AND race.date BETWEEN ? AND ?
        """

        overall = self.conn.execute(
            overall_query, [trainer_id, cutoff_date, stat_date]
        ).fetchone()

        total_runners = overall[0] or 0
        total_wins = overall[1] or 0
        total_places = overall[2] or 0

        win_rate = Decimal(total_wins) / Decimal(total_runners) if total_runners > 0 else Decimal(0)
        place_rate = Decimal(total_places) / Decimal(total_runners) if total_runners > 0 else Decimal(0)

        # Strike rate calculation
        strike_rate_query = """
            SELECT
                COUNT(*) as competitive_runners,
                SUM(CASE WHEN res.finish_position = 1 THEN 1 ELSE 0 END) as competitive_wins
            FROM runs r
            JOIN results res ON res.run_id = r.run_id
            JOIN races race ON race.race_id = r.race_id
            WHERE r.trainer_id = ?
              AND r.scratched = FALSE
              AND race.date BETWEEN ? AND ?
              AND res.finish_position <= (race.field_size / 2.0)
        """

        strike = self.conn.execute(
            strike_rate_query, [trainer_id, cutoff_date, stat_date]
        ).fetchone()

        competitive_runners = strike[0] or 0
        competitive_wins = strike[1] or 0
        strike_rate = (
            Decimal(competitive_wins) / Decimal(competitive_runners)
            if competitive_runners > 0
            else Decimal(0)
        )

        # Recent form
        recent_cutoff = stat_date - timedelta(days=14)
        recent_query = """
            SELECT
                COUNT(*) as recent_runners,
                SUM(CASE WHEN res.finish_position = 1 THEN 1 ELSE 0 END) as recent_wins
            FROM runs r
            JOIN results res ON res.run_id = r.run_id
            JOIN races race ON race.race_id = r.race_id
            WHERE r.trainer_id = ?
              AND r.scratched = FALSE
              AND race.date BETWEEN ? AND ?
        """

        recent = self.conn.execute(
            recent_query, [trainer_id, recent_cutoff, stat_date]
        ).fetchone()

        recent_runners = recent[0] or 0
        recent_wins = recent[1] or 0
        recent_win_rate = (
            Decimal(recent_wins) / Decimal(recent_runners)
            if recent_runners > 0
            else Decimal(0)
        )

        # Jockey combinations (CONFIDENCE: HIGH - useful signal)
        jockey_combos = self._calculate_jockey_combos(
            trainer_id, cutoff_date, stat_date
        )

        # Venue stats
        venue_stats = self._calculate_venue_stats(
            trainer_id, cutoff_date, stat_date, is_jockey=False
        )

        # Specialist venues
        specialist_venues = [
            venue
            for venue, stats in venue_stats.items()
            if stats.get("win_rate", 0) > float(win_rate)
        ]

        trainer_stat = TrainerStat(
            trainer_id=trainer_id,
            stat_date=stat_date,
            lookback_days=lookback_days,
            total_runners=total_runners,
            total_wins=total_wins,
            total_places=total_places,
            win_rate=win_rate,
            place_rate=place_rate,
            strike_rate=strike_rate,
            recent_runners=recent_runners,
            recent_wins=recent_wins,
            recent_win_rate=recent_win_rate,
            jockey_combos=jockey_combos,
            venue_stats=venue_stats,
            specialist_venues=specialist_venues,
        )

        logger.info(
            f"✓ Calculated trainer stats: {trainer_id} - "
            f"{total_runners} runners, {total_wins} wins, "
            f"win_rate={win_rate:.3f}"
        )

        return trainer_stat

    def _calculate_venue_stats(
        self,
        person_id: str,
        start_date: date,
        end_date: date,
        is_jockey: bool = True,
    ) -> dict[str, dict[str, Any]]:
        """
        Calculate venue-specific statistics.

        CONFIDENCE: HIGH - simple GROUP BY query
        """
        if not self.conn:
            return {}

        id_field = "jockey_id" if is_jockey else "trainer_id"

        query = f"""
            SELECT
                race.venue,
                COUNT(*) as rides,
                SUM(CASE WHEN res.finish_position = 1 THEN 1 ELSE 0 END) as wins
            FROM runs r
            JOIN results res ON res.run_id = r.run_id
            JOIN races race ON race.race_id = r.race_id
            WHERE r.{id_field} = ?
              AND r.scratched = FALSE
              AND race.date BETWEEN ? AND ?
            GROUP BY race.venue
            HAVING COUNT(*) >= 5  -- Minimum 5 rides for statistical significance
        """

        results = self.conn.execute(query, [person_id, start_date, end_date]).fetchall()

        venue_stats = {}
        for row in results:
            venue, rides, wins = row
            win_rate = wins / rides if rides > 0 else 0.0
            venue_stats[venue] = {
                "rides": rides,
                "wins": wins,
                "win_rate": win_rate,
            }

        return venue_stats

    def _calculate_distance_stats(
        self,
        person_id: str,
        start_date: date,
        end_date: date,
        is_jockey: bool = True,
    ) -> dict[str, dict[str, Any]]:
        """
        Calculate distance-specific statistics.

        Distance ranges:
        - Sprint: 1000-1200m
        - Mile: 1201-1600m
        - Middle: 1601-2000m
        - Long: 2001-2400m
        - Staying: 2401+m

        CONFIDENCE: HIGH - distance categorization is domain knowledge
        """
        if not self.conn:
            return {}

        id_field = "jockey_id" if is_jockey else "trainer_id"

        query = f"""
            SELECT
                CASE
                    WHEN race.distance <= 1200 THEN 'sprint'
                    WHEN race.distance <= 1600 THEN 'mile'
                    WHEN race.distance <= 2000 THEN 'middle'
                    WHEN race.distance <= 2400 THEN 'long'
                    ELSE 'staying'
                END as distance_range,
                COUNT(*) as rides,
                SUM(CASE WHEN res.finish_position = 1 THEN 1 ELSE 0 END) as wins
            FROM runs r
            JOIN results res ON res.run_id = r.run_id
            JOIN races race ON race.race_id = r.race_id
            WHERE r.{id_field} = ?
              AND r.scratched = FALSE
              AND race.date BETWEEN ? AND ?
            GROUP BY distance_range
        """

        results = self.conn.execute(query, [person_id, start_date, end_date]).fetchall()

        distance_stats = {}
        for row in results:
            dist_range, rides, wins = row
            win_rate = wins / rides if rides > 0 else 0.0
            distance_stats[dist_range] = {
                "rides": rides,
                "wins": wins,
                "win_rate": win_rate,
            }

        return distance_stats

    def _calculate_jockey_combos(
        self,
        trainer_id: str,
        start_date: date,
        end_date: date,
    ) -> dict[str, dict[str, Any]]:
        """
        Calculate trainer-jockey combination statistics.

        This is valuable signal - certain trainer/jockey combos
        have historically high win rates.

        CONFIDENCE: HIGH - well-known in racing analytics
        """
        if not self.conn:
            return {}

        query = """
            SELECT
                r.jockey_id,
                j.name as jockey_name,
                COUNT(*) as rides,
                SUM(CASE WHEN res.finish_position = 1 THEN 1 ELSE 0 END) as wins
            FROM runs r
            JOIN results res ON res.run_id = r.run_id
            JOIN races race ON race.race_id = r.race_id
            LEFT JOIN jockeys j ON j.jockey_id = r.jockey_id
            WHERE r.trainer_id = ?
              AND r.scratched = FALSE
              AND race.date BETWEEN ? AND ?
            GROUP BY r.jockey_id, j.name
            HAVING COUNT(*) >= 5  -- Minimum 5 rides together
            ORDER BY wins DESC
        """

        results = self.conn.execute(query, [trainer_id, start_date, end_date]).fetchall()

        jockey_combos = {}
        for row in results:
            jockey_id, jockey_name, rides, wins = row
            win_rate = wins / rides if rides > 0 else 0.0
            jockey_combos[jockey_id] = {
                "name": jockey_name,
                "rides": rides,
                "wins": wins,
                "win_rate": win_rate,
            }

        return jockey_combos

    def batch_calculate_jockey_stats(
        self,
        jockey_ids: list[str],
        lookback_days: int = 365,
    ) -> list[JockeyStat]:
        """
        Calculate stats for multiple jockeys efficiently.

        Args:
            jockey_ids: List of jockey IDs to process
            lookback_days: Lookback period

        Returns:
            List of JockeyStat models

        CONFIDENCE: HIGH - batch processing is efficient
        """
        stats = []

        for jockey_id in jockey_ids:
            try:
                stat = self.calculate_jockey_stats(jockey_id, lookback_days)
                stats.append(stat)
            except Exception as e:
                logger.error(f"Failed to calculate stats for {jockey_id}: {e}")
                continue

        return stats

    def batch_calculate_trainer_stats(
        self,
        trainer_ids: list[str],
        lookback_days: int = 365,
    ) -> list[TrainerStat]:
        """
        Calculate stats for multiple trainers efficiently.

        Args:
            trainer_ids: List of trainer IDs to process
            lookback_days: Lookback period

        Returns:
            List of TrainerStat models
        """
        stats = []

        for trainer_id in trainer_ids:
            try:
                stat = self.calculate_trainer_stats(trainer_id, lookback_days)
                stats.append(stat)
            except Exception as e:
                logger.error(f"Failed to calculate stats for {trainer_id}: {e}")
                continue

        return stats
