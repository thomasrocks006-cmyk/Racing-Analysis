"""
Sectional Analysis Engine - Category 20

Analyzes sectional times (L600, L400, L200) to:
- Profile pace patterns (early/mid/late speed)
- Classify running styles (leader, on-pace, mid-pack, closer)
- Calculate finish speed ratings
- Identify sectional balance (even vs sprint finish)
- Compare relative sectional performance within field

Author: Racing Analysis System
Date: November 2025
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import duckdb

logger = logging.getLogger(__name__)


@dataclass
class SectionalProfile:
    """
    Sectional performance profile for a single horse/race.

    Attributes:
        horse_id: Unique horse identifier
        race_id: Unique race identifier
        distance: Total race distance in meters
        L600_time: Last 600m time in seconds (None if not available)
        L400_time: Last 400m time in seconds (None if not available)
        L200_time: Last 200m time in seconds (None if not available)
        L600_speed: Last 600m speed in m/s
        L400_speed: Last 400m speed in m/s
        L200_speed: Last 200m speed in m/s
        finish_speed_rating: Rating for last 200m sprint (0-150)
        pace_profile: Classification (leader/on-pace/mid-pack/closer)
        sectional_balance: Even pace vs sprint finish indicator (-1 to 1)
        L600_percentile: Rank within field (0-100)
        L400_percentile: Rank within field (0-100)
        L200_percentile: Rank within field (0-100)
    """

    horse_id: str
    race_id: str
    distance: int
    L600_time: Optional[float]
    L400_time: Optional[float]
    L200_time: Optional[float]
    L600_speed: Optional[float]
    L400_speed: Optional[float]
    L200_speed: Optional[float]
    finish_speed_rating: int
    pace_profile: str
    sectional_balance: float
    L600_percentile: Optional[float]
    L400_percentile: Optional[float]
    L200_percentile: Optional[float]


class SectionalAnalyzer:
    """
    Analyzes sectional times to identify pace patterns and running styles.

    Uses last 600m, 400m, and 200m splits to:
    - Calculate sectional speeds
    - Rate finish speed (last 200m sprint)
    - Classify running style based on relative sectional performance
    - Measure pace balance (even vs late acceleration)
    """

    def __init__(self, db_path: str = "data/racing.duckdb"):
        """Initialize analyzer with database connection."""
        self.db_path = db_path

    def analyze_sectionals(
        self,
        race_id: str,
        horse_id: str,
        distance: int,
        L600_time: Optional[float] = None,
        L400_time: Optional[float] = None,
        L200_time: Optional[float] = None,
    ) -> SectionalProfile:
        """
        Analyze sectional times for a single performance.

        Args:
            race_id: Race identifier
            horse_id: Horse identifier
            distance: Total race distance in meters
            L600_time: Last 600m time in seconds
            L400_time: Last 400m time in seconds
            L200_time: Last 200m time in seconds

        Returns:
            SectionalProfile with pace analysis
        """
        # Calculate sectional speeds
        L600_speed = 600 / L600_time if L600_time and L600_time > 0 else None
        L400_speed = 400 / L400_time if L400_time and L400_time > 0 else None
        L200_speed = 200 / L200_time if L200_time and L200_time > 0 else None

        # Calculate finish speed rating (0-150 scale, 100 = average)
        finish_speed_rating = self._calculate_finish_speed_rating(L200_speed, distance)

        # Determine pace profile
        pace_profile = self._classify_pace_profile(L600_speed, L400_speed, L200_speed)

        # Calculate sectional balance (-1 = even pace, +1 = strong sprint finish)
        sectional_balance = self._calculate_sectional_balance(
            L600_speed, L400_speed, L200_speed
        )

        # Get field percentiles (will be None if analyzed individually)
        L600_percentile = None
        L400_percentile = None
        L200_percentile = None

        return SectionalProfile(
            horse_id=horse_id,
            race_id=race_id,
            distance=distance,
            L600_time=L600_time,
            L400_time=L400_time,
            L200_time=L200_time,
            L600_speed=L600_speed,
            L400_speed=L400_speed,
            L200_speed=L200_speed,
            finish_speed_rating=finish_speed_rating,
            pace_profile=pace_profile,
            sectional_balance=sectional_balance,
            L600_percentile=L600_percentile,
            L400_percentile=L400_percentile,
            L200_percentile=L200_percentile,
        )

    def analyze_race_sectionals(self, race_id: str) -> list[SectionalProfile]:
        """
        Analyze sectionals for all horses in a race with field percentiles.

        Args:
            race_id: Race identifier

        Returns:
            List of SectionalProfile objects with percentiles
        """
        conn = duckdb.connect(self.db_path, read_only=True)

        try:
            # Get all results with sectional times
            query = """
                SELECT
                    r.race_id,
                    r.horse_id,
                    ra.distance,
                    r.sectional_600m,
                    r.sectional_400m,
                    r.sectional_200m
                FROM results r
                JOIN races ra ON r.race_id = ra.race_id
                WHERE r.race_id = ?
                ORDER BY r.finish_position
            """

            results = conn.execute(query, [race_id]).fetchall()

            if not results:
                logger.warning(f"No results found for race {race_id}")
                return []

            profiles = []
            L600_speeds = []
            L400_speeds = []
            L200_speeds = []

            # First pass: calculate all profiles
            for row in results:
                race_id, horse_id, distance, L600, L400, L200 = row

                profile = self.analyze_sectionals(
                    race_id=race_id,
                    horse_id=horse_id,
                    distance=distance,
                    L600_time=L600,
                    L400_time=L400,
                    L200_time=L200,
                )

                profiles.append(profile)

                # Collect speeds for percentile calculation
                if profile.L600_speed:
                    L600_speeds.append(profile.L600_speed)
                if profile.L400_speed:
                    L400_speeds.append(profile.L400_speed)
                if profile.L200_speed:
                    L200_speeds.append(profile.L200_speed)

            # Second pass: assign percentiles
            for profile in profiles:
                if profile.L600_speed and L600_speeds:
                    profile.L600_percentile = self._calculate_percentile(
                        profile.L600_speed, L600_speeds
                    )
                if profile.L400_speed and L400_speeds:
                    profile.L400_percentile = self._calculate_percentile(
                        profile.L400_speed, L400_speeds
                    )
                if profile.L200_speed and L200_speeds:
                    profile.L200_percentile = self._calculate_percentile(
                        profile.L200_speed, L200_speeds
                    )

            return profiles

        finally:
            conn.close()

    def get_horse_sectional_pattern(
        self, horse_id: str, last_n_starts: int = 5
    ) -> dict:
        """
        Identify typical running style from recent sectional patterns.

        Args:
            horse_id: Horse identifier
            last_n_starts: Number of recent starts to analyze

        Returns:
            Dict with pattern statistics:
                - dominant_style: Most common pace profile
                - avg_L200_percentile: Average finish speed rank
                - consistency: Standard deviation of sectional balance
                - starts_analyzed: Number of runs with sectional data
        """
        conn = duckdb.connect(self.db_path, read_only=True)

        try:
            query = """
                SELECT
                    r.race_id,
                    ra.distance,
                    r.sectional_600m,
                    r.sectional_400m,
                    r.sectional_200m
                FROM results r
                JOIN races ra ON r.race_id = ra.race_id
                WHERE r.horse_id = ?
                    AND r.sectional_200m IS NOT NULL
                ORDER BY ra.date DESC
                LIMIT ?
            """

            results = conn.execute(query, [horse_id, last_n_starts]).fetchall()

            if not results:
                return {
                    "dominant_style": "unknown",
                    "avg_finish_speed": 0,
                    "avg_sectional_balance": 0.0,
                    "consistency": 0.0,
                    "starts_analyzed": 0,
                }

            profiles = []
            for row in results:
                race_id, distance, L600, L400, L200 = row
                profile = self.analyze_sectionals(
                    race_id=race_id,
                    horse_id=horse_id,
                    distance=distance,
                    L600_time=L600,
                    L400_time=L400,
                    L200_time=L200,
                )
                profiles.append(profile)

            # Analyze patterns
            pace_profiles = [p.pace_profile for p in profiles]
            finish_speeds = [p.finish_speed_rating for p in profiles]
            balances = [p.sectional_balance for p in profiles]

            # Find dominant style (most common)
            dominant_style = max(set(pace_profiles), key=pace_profiles.count)

            # Calculate averages
            avg_finish_speed = sum(finish_speeds) / len(finish_speeds)
            avg_balance = sum(balances) / len(balances)

            # Calculate consistency (lower = more consistent)
            if len(balances) > 1:
                mean_balance = sum(balances) / len(balances)
                variance = sum((x - mean_balance) ** 2 for x in balances) / len(
                    balances
                )
                consistency = variance**0.5
            else:
                consistency = 0.0

            return {
                "dominant_style": dominant_style,
                "avg_finish_speed": int(avg_finish_speed),
                "avg_sectional_balance": round(avg_balance, 2),
                "consistency": round(consistency, 2),
                "starts_analyzed": len(profiles),
            }

        finally:
            conn.close()

    def _calculate_finish_speed_rating(
        self, L200_speed: Optional[float], distance: int
    ) -> int:
        """
        Rate the last 200m speed on 0-150 scale.

        Uses distance-adjusted benchmarks:
        - Sprint (<=1200m): Higher baseline speeds expected
        - Mile (1200-1600m): Moderate baseline
        - Middle/Staying (>1600m): Lower baseline, sprint finish more valuable

        Args:
            L200_speed: Speed over last 200m in m/s
            distance: Total race distance in meters

        Returns:
            Rating from 0-150 (100 = average for distance)
        """
        if not L200_speed or L200_speed <= 0:
            return 50  # Below average if no data

        # Distance-based benchmarks (m/s for last 200m)
        if distance <= 1200:
            # Sprint races - expect fast last 200m
            baseline = 17.5  # ~11.4s for 200m
            exceptional = 19.0  # ~10.5s
        elif distance <= 1600:
            # Mile races - moderate last 200m
            baseline = 17.0  # ~11.8s
            exceptional = 18.5  # ~10.8s
        else:
            # Middle/staying - strong finish more impressive
            baseline = 16.5  # ~12.1s
            exceptional = 18.0  # ~11.1s

        # Scale to 0-150
        if L200_speed >= exceptional:
            rating = 130  # Elite finish speed
        elif L200_speed >= baseline:
            # Scale from 100 (baseline) to 130 (exceptional)
            ratio = (L200_speed - baseline) / (exceptional - baseline)
            rating = 100 + int(ratio * 30)
        else:
            # Scale from 50 to 100 based on how far below baseline
            ratio = L200_speed / baseline
            rating = 50 + int(ratio * 50)

        return max(0, min(150, rating))

    def _classify_pace_profile(
        self,
        L600_speed: Optional[float],
        L400_speed: Optional[float],
        L200_speed: Optional[float],
    ) -> str:
        """
        Classify running style based on sectional acceleration pattern.

        Profiles:
        - leader: Fastest early, fades late (L600 > L400 > L200)
        - on-pace: Consistent speed throughout (speeds within 5%)
        - mid-pack: Moderate acceleration (10-20% speed increase)
        - closer: Strong late acceleration (>20% speed increase)

        Args:
            L600_speed: Speed over L600 in m/s
            L400_speed: Speed over L400 in m/s
            L200_speed: Speed over L200 in m/s

        Returns:
            Pace profile classification
        """
        # Need at least L400 and L200 for meaningful classification
        if not L400_speed or not L200_speed:
            return "unknown"

        # Calculate acceleration from L400 to L200
        acceleration = (L200_speed - L400_speed) / L400_speed

        # If we have L600, check early pace
        if L600_speed:
            early_pace = (L400_speed - L600_speed) / L600_speed

            # Leader: Fast early, fades
            if early_pace > 0.05 and acceleration < -0.05:
                return "leader"

            # Strong closer: Slow early, fast late
            if early_pace < -0.05 and acceleration > 0.20:
                return "closer"

        # Classify based on late acceleration alone
        if acceleration > 0.20:
            return "closer"  # Strong late sprint
        elif acceleration > 0.10:
            return "mid-pack"  # Moderate late run
        elif abs(acceleration) <= 0.10:
            return "on-pace"  # Even pace
        else:
            return "leader"  # Fading

    def _calculate_sectional_balance(
        self,
        L600_speed: Optional[float],
        L400_speed: Optional[float],
        L200_speed: Optional[float],
    ) -> float:
        """
        Calculate pace balance indicator.

        Returns:
            -1.0 = very even pace throughout
             0.0 = moderate acceleration
            +1.0 = extreme sprint finish

        Based on coefficient of variation in sectional speeds.
        """
        speeds = []
        if L600_speed:
            speeds.append(L600_speed)
        if L400_speed:
            speeds.append(L400_speed)
        if L200_speed:
            speeds.append(L200_speed)

        if len(speeds) < 2:
            return 0.0  # Neutral if insufficient data

        # Calculate coefficient of variation
        mean_speed = sum(speeds) / len(speeds)
        variance = sum((s - mean_speed) ** 2 for s in speeds) / len(speeds)
        std_dev = variance**0.5
        cv = std_dev / mean_speed if mean_speed > 0 else 0

        # Map CV to -1 to +1 scale
        # CV < 0.02 = very even (near -1)
        # CV > 0.10 = very uneven (near +1)
        if cv < 0.02:
            balance = -1.0
        elif cv > 0.10:
            balance = 1.0
        else:
            # Linear scale between
            balance = (cv - 0.02) / 0.08 * 2 - 1

        return round(balance, 2)

    def _calculate_percentile(self, value: float, field_values: list[float]) -> float:
        """
        Calculate percentile rank within field (0-100).

        Higher percentile = better performance (faster speed).

        Args:
            value: Horse's value
            field_values: All values in field

        Returns:
            Percentile rank (0-100)
        """
        if not field_values:
            return 50.0

        # Sort descending (fastest = best)
        sorted_values = sorted(field_values, reverse=True)

        # Find rank (1-based)
        rank = sorted_values.index(value) + 1

        # Convert to percentile
        percentile = ((len(sorted_values) - rank + 1) / len(sorted_values)) * 100

        return round(percentile, 1)


if __name__ == "__main__":
    """Example usage of sectional analyzer."""

    analyzer = SectionalAnalyzer()

    print("=" * 70)
    print("SECTIONAL ANALYSIS EXAMPLE")
    print("=" * 70)

    # Example 1: Individual horse sectional analysis
    print("\n1. Individual Sectional Analysis:")
    print("-" * 70)

    profile = analyzer.analyze_sectionals(
        race_id="FLE-2025-11-12-R1",
        horse_id="H1001",
        distance=1200,
        L600_time=34.5,  # 600m in 34.5s = 17.4 m/s
        L400_time=22.8,  # 400m in 22.8s = 17.5 m/s
        L200_time=11.2,  # 200m in 11.2s = 17.9 m/s (strong finish)
    )

    print(f"Horse: {profile.horse_id}")
    print(f"Distance: {profile.distance}m")
    print(f"\nSectional Speeds:")
    print(f"  L600: {profile.L600_speed:.2f} m/s ({profile.L600_time:.1f}s)")
    print(f"  L400: {profile.L400_speed:.2f} m/s ({profile.L400_time:.1f}s)")
    print(f"  L200: {profile.L200_speed:.2f} m/s ({profile.L200_time:.1f}s)")
    print(f"\nPace Profile: {profile.pace_profile.upper()}")
    print(f"Finish Speed Rating: {profile.finish_speed_rating}/150")
    print(
        f"Sectional Balance: {profile.sectional_balance:+.2f} {'(sprint finish)' if profile.sectional_balance > 0 else '(even pace)'}"
    )

    # Example 2: Compare different running styles
    print("\n\n2. Running Style Comparison:")
    print("-" * 70)

    styles = [
        ("Leader", 35.0, 23.5, 12.0),  # Fast early, fades
        ("On-Pace", 34.5, 23.0, 11.5),  # Consistent
        ("Closer", 36.0, 23.0, 10.8),  # Slow early, fast late
    ]

    for style_name, L600, L400, L200 in styles:
        p = analyzer.analyze_sectionals(
            "TEST", f"H{style_name}", 1200, L600, L400, L200
        )
        print(f"\n{style_name}:")
        print(f"  Sectionals: {L600:.1f}s / {L400:.1f}s / {L200:.1f}s")
        print(f"  Classification: {p.pace_profile}")
        print(f"  Balance: {p.sectional_balance:+.2f}")
        print(f"  Finish Speed: {p.finish_speed_rating}/150")

    print("\n" + "=" * 70)
