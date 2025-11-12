"""
Speed ratings calculator for racing data.

Implements Category 18 from the quantitative pipeline:
- Base speed calculation from race times
- Track condition adjustments
- Distance adjustments
- Sectional-based ratings
- Comparative speed figures

Usage:
    from src.features.speed_ratings import SpeedRatingsEngine

    engine = SpeedRatingsEngine()
    rating = engine.calculate_speed_rating(race_result)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

import duckdb

logger = logging.getLogger(__name__)


@dataclass
class SpeedRating:
    """Speed rating result."""

    horse_id: str
    race_id: str
    base_speed: float
    adjusted_speed: float
    track_adjustment: float
    distance_adjustment: float
    sectional_rating: float | None
    final_rating: int
    percentile: float | None


class SpeedRatingsEngine:
    """
    Calculate speed ratings for horses.

    Speed ratings normalize race times accounting for:
    - Track conditions (Good 3 vs Soft 7)
    - Distance variations (1200m vs 2000m)
    - Sectional times (finishing speed)
    - Track bias and rail position

    Rating scale: 0-150 (higher = faster)
    - 100 = Average open-class horse
    - 110+ = Group level
    - 120+ = Group 1 quality
    """

    # Track condition multipliers (Good 3 = baseline 1.0)
    TRACK_ADJUSTMENTS = {
        "firm": 0.98,
        "good 3": 1.0,
        "good 4": 1.01,
        "soft 5": 1.03,
        "soft 6": 1.05,
        "soft 7": 1.07,
        "heavy 8": 1.10,
        "heavy 9": 1.12,
        "heavy 10": 1.15,
    }

    # Distance par times (seconds per 100m for average horse)
    DISTANCE_PARS = {
        1000: 6.0,
        1200: 6.1,
        1400: 6.2,
        1600: 6.3,
        2000: 6.4,
        2400: 6.5,
    }

    def __init__(self, db_path: str = "data/racing.duckdb"):
        """
        Initialize speed ratings engine.

        Args:
            db_path: Path to DuckDB database
        """
        self.db_path = db_path

    def calculate_speed_rating(
        self,
        race_id: str,
        horse_id: str,
        race_time: float,
        distance: int,
        track_condition: str,
        sectional_times: dict[str, float] | None = None,
    ) -> SpeedRating:
        """
        Calculate speed rating for a single performance.

        Args:
            race_id: Race identifier
            horse_id: Horse identifier
            race_time: Total race time in seconds
            distance: Race distance in meters
            track_condition: Track condition (e.g., "Good 4")
            sectional_times: Dict with '600m', '400m', '200m' splits

        Returns:
            SpeedRating object
        """
        # 1. Calculate base speed (meters per second)
        base_speed = distance / race_time

        # 2. Apply track condition adjustment
        track_adj = self._get_track_adjustment(track_condition)
        adjusted_speed = base_speed * (1 / track_adj)  # Adjust for slower tracks

        # 3. Apply distance adjustment (longer races have different pars)
        distance_adj = self._get_distance_adjustment(distance, race_time)

        # 4. Calculate sectional rating if available
        sectional_rating = None
        if sectional_times:
            sectional_rating = self._calculate_sectional_rating(
                sectional_times, distance
            )

        # 5. Normalize to 0-150 scale (100 = average)
        # Base conversion: 16.67 m/s = rating 100 (1200m in 72s)
        raw_rating = (adjusted_speed / 16.67) * 100

        # Apply distance and sectional adjustments
        if sectional_rating:
            final_rating = int((raw_rating * 0.7) + (sectional_rating * 0.3))
        else:
            final_rating = int(raw_rating + distance_adj)

        # Clamp to 0-150
        final_rating = max(0, min(150, final_rating))

        return SpeedRating(
            horse_id=horse_id,
            race_id=race_id,
            base_speed=base_speed,
            adjusted_speed=adjusted_speed,
            track_adjustment=track_adj,
            distance_adjustment=distance_adj,
            sectional_rating=sectional_rating,
            final_rating=final_rating,
            percentile=None,  # Calculate separately with population data
        )

    def calculate_race_ratings(self, race_id: str) -> list[SpeedRating]:
        """
        Calculate speed ratings for all horses in a race.

        Args:
            race_id: Race identifier

        Returns:
            List of SpeedRating objects sorted by rating (descending)
        """
        con = duckdb.connect(self.db_path, read_only=True)

        try:
            # Query race results with sectionals
            query = """
                SELECT
                    r.race_id,
                    r.distance,
                    r.track_condition,
                    res.horse_id,
                    res.race_time,
                    res.sectional_600m,
                    res.sectional_400m,
                    res.sectional_200m,
                    res.finish_position
                FROM results res
                JOIN races r ON res.race_id = r.race_id
                JOIN runs run ON res.run_id = run.run_id
                WHERE r.race_id = ?
                  AND res.race_time IS NOT NULL
                ORDER BY res.finish_position
            """

            rows = con.execute(query, [race_id]).fetchall()

            ratings = []
            for row in rows:
                (
                    race_id,
                    distance,
                    track_condition,
                    horse_id,
                    race_time,
                    sect_600,
                    sect_400,
                    sect_200,
                    position,
                ) = row

                # Build sectional times dict
                sectional_times = {}
                if sect_600:
                    sectional_times["600m"] = float(sect_600)
                if sect_400:
                    sectional_times["400m"] = float(sect_400)
                if sect_200:
                    sectional_times["200m"] = float(sect_200)

                rating = self.calculate_speed_rating(
                    race_id=race_id,
                    horse_id=horse_id,
                    race_time=float(race_time),
                    distance=distance,
                    track_condition=track_condition or "good 4",
                    sectional_times=sectional_times if sectional_times else None,
                )

                ratings.append(rating)

            # Calculate percentiles within race
            if ratings:
                sorted_ratings = sorted(
                    ratings, key=lambda x: x.final_rating, reverse=True
                )
                for i, rating in enumerate(sorted_ratings):
                    rating.percentile = (
                        (len(sorted_ratings) - i) / len(sorted_ratings)
                    ) * 100

            return ratings

        finally:
            con.close()

    def _get_track_adjustment(self, track_condition: str) -> float:
        """Get track condition adjustment multiplier."""
        if not track_condition:
            return 1.0

        condition_lower = track_condition.lower().strip()

        # Try exact match first
        if condition_lower in self.TRACK_ADJUSTMENTS:
            return self.TRACK_ADJUSTMENTS[condition_lower]

        # Parse "Good 4" format
        for key in self.TRACK_ADJUSTMENTS:
            if key in condition_lower:
                return self.TRACK_ADJUSTMENTS[key]

        # Default to Good 4
        logger.warning(f"Unknown track condition: {track_condition}, using Good 4")
        return 1.0

    def _get_distance_adjustment(self, distance: int, race_time: float) -> float:
        """
        Calculate distance-based adjustment.

        Compares actual time to par time for distance.
        """
        # Find closest par distance
        closest_par = min(self.DISTANCE_PARS.keys(), key=lambda x: abs(x - distance))
        par_per_100m = self.DISTANCE_PARS[closest_par]

        # Expected time at par
        expected_time = (distance / 100) * par_per_100m

        # Time difference as rating adjustment
        time_diff = expected_time - race_time
        adjustment = (time_diff / expected_time) * 10  # +/- 10 points max

        return adjustment

    def _calculate_sectional_rating(
        self, sectional_times: dict[str, float], distance: int
    ) -> float:
        """
        Calculate rating based on sectional times.

        Emphasizes strong finish (last 400m, 200m).
        """
        if "200m" not in sectional_times:
            return 100.0  # Default

        # Last 200m speed (higher = better)
        last_200_speed = 200 / sectional_times["200m"]

        # Expected last 200m for average horse: ~12 seconds = 16.67 m/s
        # Scale: 16.67 m/s = rating 100
        sectional_rating = (last_200_speed / 16.67) * 100

        # If we have 400m, weight it
        if "400m" in sectional_times:
            last_400_speed = 400 / sectional_times["400m"]
            last_400_rating = (last_400_speed / 16.67) * 100

            # 70% last 200m, 30% last 400m
            sectional_rating = (sectional_rating * 0.7) + (last_400_rating * 0.3)

        return sectional_rating

    def get_horse_average_rating(
        self, horse_id: str, last_n_starts: int = 5
    ) -> dict[str, Any]:
        """
        Get average speed rating for a horse over recent starts.

        Args:
            horse_id: Horse identifier
            last_n_starts: Number of recent starts to average

        Returns:
            dict with average, best, and consistency metrics
        """
        con = duckdb.connect(self.db_path, read_only=True)

        try:
            # Get recent results
            query = """
                SELECT
                    r.race_id,
                    r.distance,
                    r.track_condition,
                    r.date,
                    res.race_time,
                    res.sectional_600m,
                    res.sectional_400m,
                    res.sectional_200m,
                    res.speed_rating
                FROM results res
                JOIN races r ON res.race_id = r.race_id
                JOIN runs run ON res.run_id = run.run_id
                WHERE run.horse_id = ?
                  AND res.race_time IS NOT NULL
                ORDER BY r.date DESC
                LIMIT ?
            """

            rows = con.execute(query, [horse_id, last_n_starts]).fetchall()

            if not rows:
                return {
                    "average": None,
                    "best": None,
                    "worst": None,
                    "std_dev": None,
                    "starts": 0,
                }

            ratings = []
            for row in rows:
                # Use stored rating if available, otherwise calculate
                if row[8] is not None:
                    ratings.append(row[8])
                else:
                    # Calculate on the fly
                    sectional_times = {}
                    if row[5]:
                        sectional_times["600m"] = float(row[5])
                    if row[6]:
                        sectional_times["400m"] = float(row[6])
                    if row[7]:
                        sectional_times["200m"] = float(row[7])

                    rating = self.calculate_speed_rating(
                        race_id=row[0],
                        horse_id=horse_id,
                        race_time=float(row[4]),
                        distance=row[1],
                        track_condition=row[2] or "good 4",
                        sectional_times=sectional_times if sectional_times else None,
                    )
                    ratings.append(rating.final_rating)

            # Calculate statistics
            import statistics

            return {
                "average": statistics.mean(ratings),
                "best": max(ratings),
                "worst": min(ratings),
                "std_dev": statistics.stdev(ratings) if len(ratings) > 1 else 0,
                "starts": len(ratings),
            }

        finally:
            con.close()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = SpeedRatingsEngine()

    # Example: Calculate rating for a hypothetical race
    rating = engine.calculate_speed_rating(
        race_id="FLE-2025-11-12-R1",
        horse_id="H1001",
        race_time=72.5,  # 72.5 seconds
        distance=1200,  # 1200m
        track_condition="Good 4",
        sectional_times={"600m": 34.2, "400m": 22.8, "200m": 11.4},
    )

    print(f"\nSpeed Rating Example:")
    print(f"  Horse: {rating.horse_id}")
    print(f"  Base speed: {rating.base_speed:.2f} m/s")
    print(f"  Track adjustment: {rating.track_adjustment:.3f}")
    print(f"  Distance adjustment: {rating.distance_adjustment:+.1f}")
    print(f"  Sectional rating: {rating.sectional_rating:.1f}")
    print(f"  Final Rating: {rating.final_rating}")
