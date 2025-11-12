"""
Pedigree Analysis Engine - Category 21

Analyzes bloodline performance to:
- Rate sire, dam, and dam sire (broodmare sire) quality
- Calculate distance suitability based on progeny performance
- Assess surface preferences (turf vs synthetic)
- Evaluate pedigree fit for specific race conditions

Based on progeny statistics:
- Win rate and strike rate
- Stakes winners produced
- Average earnings
- Distance range performance

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
class PedigreeRating:
    """
    Pedigree performance rating for a horse.

    Attributes:
        horse_id: Unique horse identifier
        sire: Sire (father) name
        dam: Dam (mother) name
        dam_sire: Dam's sire (broodmare sire) name
        sire_rating: Sire quality rating (0-150)
        dam_rating: Dam quality rating (0-150)
        dam_sire_rating: Broodmare sire quality rating (0-150)
        distance_suitability: Suitability for race distance (0-100%)
        surface_suitability: Suitability for race surface (0-100%)
        overall_pedigree_score: Combined pedigree score (0-150)
        distance_category: Sprint/Mile/Middle/Staying classification
    """

    horse_id: str
    sire: str
    dam: str
    dam_sire: str
    sire_rating: int
    dam_rating: int
    dam_sire_rating: int
    distance_suitability: float
    surface_suitability: float
    overall_pedigree_score: int
    distance_category: str


class PedigreeAnalyzer:
    """
    Analyzes pedigree quality and suitability for race conditions.

    Uses progeny performance data to rate stallions and broodmare sires.
    Calculates distance and surface suitability based on family patterns.
    """

    # Distance categories (meters)
    SPRINT_MAX = 1200
    MILE_MAX = 1600
    MIDDLE_MAX = 2000

    def __init__(self, db_path: str = "data/racing.duckdb"):
        """Initialize analyzer with database connection."""
        self.db_path = db_path

    def analyze_pedigree(
        self,
        horse_id: str,
        race_distance: int,
        race_surface: str = "turf",
    ) -> PedigreeRating:
        """
        Analyze pedigree for a horse and specific race conditions.

        Args:
            horse_id: Horse identifier
            race_distance: Race distance in meters
            race_surface: Race surface type (turf/synthetic)

        Returns:
            PedigreeRating with quality scores and suitability
        """
        conn = duckdb.connect(self.db_path, read_only=True)

        try:
            # Get horse pedigree
            query = """
                SELECT sire, dam, dam_sire
                FROM horses
                WHERE horse_id = ?
            """

            result = conn.execute(query, [horse_id]).fetchone()

            if not result:
                logger.warning(f"Horse {horse_id} not found in database")
                return self._default_rating(horse_id, race_distance)

            sire, dam, dam_sire = result

            # Rate each component
            sire_rating = self._rate_stallion(sire, conn)
            dam_rating = self._rate_broodmare(dam, conn)
            dam_sire_rating = self._rate_stallion(dam_sire, conn)

            # Calculate distance suitability
            distance_category = self._classify_distance(race_distance)
            distance_suitability = self._calculate_distance_suitability(
                sire, race_distance, conn
            )

            # Calculate surface suitability
            surface_suitability = self._calculate_surface_suitability(
                sire, race_surface, conn
            )

            # Calculate overall pedigree score
            # Weighted: Sire 50%, Dam sire 30%, Dam 20%
            overall_score = int(
                sire_rating * 0.50
                + dam_sire_rating * 0.30
                + dam_rating * 0.20
            )

            # Adjust for suitability
            suitability_factor = (distance_suitability + surface_suitability) / 200
            overall_score = int(overall_score * (0.8 + suitability_factor * 0.4))
            overall_score = max(0, min(150, overall_score))

            return PedigreeRating(
                horse_id=horse_id,
                sire=sire or "Unknown",
                dam=dam or "Unknown",
                dam_sire=dam_sire or "Unknown",
                sire_rating=sire_rating,
                dam_rating=dam_rating,
                dam_sire_rating=dam_sire_rating,
                distance_suitability=distance_suitability,
                surface_suitability=surface_suitability,
                overall_pedigree_score=overall_score,
                distance_category=distance_category,
            )

        finally:
            conn.close()

    def get_sire_statistics(self, sire_name: str) -> dict:
        """
        Get detailed statistics for a stallion.

        Args:
            sire_name: Stallion name

        Returns:
            Dict with progeny statistics:
                - progeny_count: Number of offspring
                - winners: Number of individual winners
                - win_rate: Percentage of winners
                - stakes_winners: Number of stakes winners
                - avg_earnings: Average earnings per runner
                - best_distance: Most successful distance range
        """
        conn = duckdb.connect(self.db_path, read_only=True)

        try:
            # Get progeny performance
            query = """
                SELECT
                    COUNT(DISTINCT h.horse_id) as progeny_count,
                    COUNT(DISTINCT CASE WHEN r.finish_position = 1 THEN h.horse_id END) as winners,
                    COUNT(DISTINCT CASE WHEN ra.race_class LIKE '%G%' OR ra.race_class LIKE '%Listed%'
                                   THEN h.horse_id END) as stakes_winners,
                    AVG(r.prize_money) as avg_earnings
                FROM horses h
                LEFT JOIN results r ON h.horse_id = r.horse_id
                LEFT JOIN races ra ON r.race_id = ra.race_id
                WHERE h.sire = ?
            """

            result = conn.execute(query, [sire_name]).fetchone()

            if not result or result[0] == 0:
                return {
                    "progeny_count": 0,
                    "winners": 0,
                    "win_rate": 0.0,
                    "stakes_winners": 0,
                    "avg_earnings": 0,
                    "best_distance": "unknown",
                }

            progeny_count, winners, stakes_winners, avg_earnings = result

            win_rate = (winners / progeny_count * 100) if progeny_count > 0 else 0

            # Find best distance range
            best_distance = self._find_best_distance_range(sire_name, conn)

            return {
                "progeny_count": progeny_count,
                "winners": winners or 0,
                "win_rate": round(win_rate, 1),
                "stakes_winners": stakes_winners or 0,
                "avg_earnings": int(avg_earnings or 0),
                "best_distance": best_distance,
            }

        finally:
            conn.close()

    def _rate_stallion(self, sire_name: str, conn) -> int:
        """
        Rate stallion quality based on progeny performance.

        Rating scale 0-150:
        - 140+: Elite sire (multiple Group 1 winners)
        - 120-139: High-class sire (Group winners)
        - 100-119: Above-average sire (stakes winners)
        - 80-99: Average sire (regular winners)
        - 60-79: Below-average sire (few winners)
        - <60: Poor sire statistics

        Args:
            sire_name: Stallion name
            conn: Database connection

        Returns:
            Sire rating (0-150)
        """
        if not sire_name:
            return 70  # Neutral for unknown

        query = """
            SELECT
                COUNT(DISTINCT h.horse_id) as progeny,
                COUNT(DISTINCT CASE WHEN r.finish_position = 1 THEN h.horse_id END) as winners,
                COUNT(DISTINCT CASE WHEN ra.race_class LIKE '%G1%' OR ra.race_class LIKE '%Group 1%'
                               THEN h.horse_id END) as g1_winners,
                COUNT(DISTINCT CASE WHEN ra.race_class LIKE '%G%' OR ra.race_class LIKE '%Listed%'
                               THEN h.horse_id END) as stakes_winners,
                AVG(CASE WHEN r.finish_position = 1 THEN r.prize_money END) as avg_win_prizemoney
            FROM horses h
            LEFT JOIN results r ON h.horse_id = r.horse_id
            LEFT JOIN races ra ON r.race_id = ra.race_id
            WHERE h.sire = ?
        """

        result = conn.execute(query, [sire_name]).fetchone()

        if not result or result[0] == 0:
            return 70  # Default neutral rating

        progeny, winners, g1_winners, stakes_winners, avg_prizemoney = result

        # Calculate base rating from win rate
        win_rate = winners / progeny if progeny > 0 else 0
        base_rating = 60 + int(win_rate * 100)  # 0% = 60, 100% = 160 (capped later)

        # Adjust for quality of winners
        if g1_winners and g1_winners > 0:
            base_rating += 30  # Elite sire bonus
        elif stakes_winners and stakes_winners > 0:
            base_rating += 15  # Stakes sire bonus

        # Adjust for prize money (indicator of class)
        if avg_prizemoney and avg_prizemoney > 100000:
            base_rating += 10
        elif avg_prizemoney and avg_prizemoney > 50000:
            base_rating += 5

        return max(50, min(150, base_rating))

    def _rate_broodmare(self, dam_name: str, conn) -> int:
        """
        Rate broodmare quality based on produce record.

        Similar to stallion rating but adjusted for smaller sample sizes.

        Args:
            dam_name: Broodmare name
            conn: Database connection

        Returns:
            Dam rating (0-150)
        """
        if not dam_name:
            return 70  # Neutral for unknown

        query = """
            SELECT
                COUNT(DISTINCT h.horse_id) as foals,
                COUNT(DISTINCT CASE WHEN r.finish_position = 1 THEN h.horse_id END) as winners,
                COUNT(DISTINCT CASE WHEN ra.race_class LIKE '%G%' OR ra.race_class LIKE '%Listed%'
                               THEN h.horse_id END) as stakes_winners
            FROM horses h
            LEFT JOIN results r ON h.horse_id = r.horse_id
            LEFT JOIN races ra ON r.race_id = ra.race_id
            WHERE h.dam = ?
        """

        result = conn.execute(query, [dam_name]).fetchone()

        if not result or result[0] == 0:
            return 70  # Default neutral

        foals, winners, stakes_winners = result

        # Simpler rating for dams (smaller samples)
        if stakes_winners and stakes_winners > 0:
            return 130  # Produced stakes winner
        elif winners and winners > 0:
            win_rate = winners / foals if foals > 0 else 0
            return 80 + int(win_rate * 50)
        else:
            return 65  # No winners yet

    def _calculate_distance_suitability(
        self, sire_name: str, race_distance: int, conn
    ) -> float:
        """
        Calculate suitability for specific race distance.

        Based on progeny performance at similar distances.

        Args:
            sire_name: Stallion name
            race_distance: Target race distance
            conn: Database connection

        Returns:
            Suitability percentage (0-100)
        """
        if not sire_name:
            return 50.0  # Neutral

        # Define distance range (±200m)
        min_dist = race_distance - 200
        max_dist = race_distance + 200

        query = """
            SELECT
                COUNT(*) as races,
                AVG(CASE WHEN r.finish_position <= 3 THEN 1.0 ELSE 0.0 END) as top3_rate
            FROM horses h
            JOIN results r ON h.horse_id = r.horse_id
            JOIN races ra ON r.race_id = ra.race_id
            WHERE h.sire = ?
                AND ra.distance BETWEEN ? AND ?
        """

        result = conn.execute(query, [sire_name, min_dist, max_dist]).fetchone()

        if not result or result[0] < 5:
            # Insufficient data - use distance category matching
            return self._estimate_distance_suitability(sire_name, race_distance, conn)

        races, top3_rate = result

        # Convert top-3 rate to suitability percentage
        # 33% top-3 rate = average (50% suitability)
        # 50%+ top-3 rate = excellent (100% suitability)
        if top3_rate >= 0.50:
            suitability = 100.0
        elif top3_rate >= 0.33:
            suitability = 50 + (top3_rate - 0.33) * 300
        else:
            suitability = top3_rate * 150

        return round(min(100, suitability), 1)

    def _estimate_distance_suitability(
        self, sire_name: str, race_distance: int, conn
    ) -> float:
        """Estimate suitability when insufficient data at specific distance."""
        # Get sire's overall best distance range
        best_range = self._find_best_distance_range(sire_name, conn)

        race_category = self._classify_distance(race_distance)

        # Match categories
        if best_range == race_category:
            return 75.0  # Good match
        elif best_range == "unknown":
            return 50.0  # Neutral
        else:
            return 40.0  # Mismatch

    def _calculate_surface_suitability(
        self, sire_name: str, race_surface: str, conn
    ) -> float:
        """
        Calculate suitability for race surface.

        Args:
            sire_name: Stallion name
            race_surface: Surface type (turf/synthetic)
            conn: Database connection

        Returns:
            Suitability percentage (0-100)
        """
        if not sire_name:
            return 50.0

        # Most Australian racing is turf, so default high for turf
        if race_surface.lower() == "turf":
            return 85.0  # Most sires suit turf

        # For synthetic, check actual performance
        query = """
            SELECT
                COUNT(*) as races,
                AVG(CASE WHEN r.finish_position <= 3 THEN 1.0 ELSE 0.0 END) as top3_rate
            FROM horses h
            JOIN results r ON h.horse_id = r.horse_id
            JOIN races ra ON r.race_id = ra.race_id
            WHERE h.sire = ?
                AND LOWER(ra.track_type) = ?
        """

        result = conn.execute(
            query, [sire_name, race_surface.lower()]
        ).fetchone()

        if not result or result[0] < 3:
            return 60.0  # Neutral for synthetic with limited data

        races, top3_rate = result

        # Convert to suitability
        suitability = top3_rate * 200
        return round(min(100, suitability), 1)

    def _find_best_distance_range(self, sire_name: str, conn) -> str:
        """Find the distance range where sire's progeny perform best."""
        query = """
            SELECT
                CASE
                    WHEN ra.distance <= 1200 THEN 'sprint'
                    WHEN ra.distance <= 1600 THEN 'mile'
                    WHEN ra.distance <= 2000 THEN 'middle'
                    ELSE 'staying'
                END as distance_cat,
                COUNT(*) as races,
                AVG(CASE WHEN r.finish_position = 1 THEN 1.0 ELSE 0.0 END) as win_rate
            FROM horses h
            JOIN results r ON h.horse_id = r.horse_id
            JOIN races ra ON r.race_id = ra.race_id
            WHERE h.sire = ?
            GROUP BY distance_cat
            ORDER BY win_rate DESC
            LIMIT 1
        """

        result = conn.execute(query, [sire_name]).fetchone()

        if not result or result[1] < 3:
            return "unknown"

        return result[0]

    def _classify_distance(self, distance: int) -> str:
        """Classify distance into category."""
        if distance <= self.SPRINT_MAX:
            return "sprint"
        elif distance <= self.MILE_MAX:
            return "mile"
        elif distance <= self.MIDDLE_MAX:
            return "middle"
        else:
            return "staying"

    def _default_rating(self, horse_id: str, race_distance: int) -> PedigreeRating:
        """Return default rating when pedigree data unavailable."""
        return PedigreeRating(
            horse_id=horse_id,
            sire="Unknown",
            dam="Unknown",
            dam_sire="Unknown",
            sire_rating=70,
            dam_rating=70,
            dam_sire_rating=70,
            distance_suitability=50.0,
            surface_suitability=50.0,
            overall_pedigree_score=70,
            distance_category=self._classify_distance(race_distance),
        )


if __name__ == "__main__":
    """Example usage of pedigree analyzer."""

    analyzer = PedigreeAnalyzer()

    print("=" * 70)
    print("PEDIGREE ANALYSIS EXAMPLE")
    print("=" * 70)

    # Example 1: Analyze pedigree for specific race
    print("\n1. Pedigree Analysis for 1200m Sprint:")
    print("-" * 70)

    # Create sample rating (would normally query database)
    rating = PedigreeRating(
        horse_id="H1001",
        sire="Written Tycoon",
        dam="Flying Princess",
        dam_sire="Fastnet Rock",
        sire_rating=135,  # Elite sprint sire
        dam_rating=95,  # Good produce record
        dam_sire_rating=140,  # Elite broodmare sire
        distance_suitability=95.0,  # Excellent for sprint
        surface_suitability=85.0,  # Good on turf
        overall_pedigree_score=125,
        distance_category="sprint",
    )

    print(f"Horse: {rating.horse_id}")
    print(f"\nPedigree:")
    print(f"  Sire: {rating.sire} (Rating: {rating.sire_rating}/150)")
    print(f"  Dam: {rating.dam} (Rating: {rating.dam_rating}/150)")
    print(f"  Dam Sire: {rating.dam_sire} (Rating: {rating.dam_sire_rating}/150)")
    print(f"\nRace Suitability:")
    print(f"  Distance: {rating.distance_category.upper()} ({rating.distance_suitability:.1f}% suited)")
    print(f"  Surface: Turf ({rating.surface_suitability:.1f}% suited)")
    print(f"\nOverall Pedigree Score: {rating.overall_pedigree_score}/150")

    # Example 2: Compare sprint vs staying pedigrees
    print("\n\n2. Pedigree Comparison - Sprint vs Staying:")
    print("-" * 70)

    sprint_ped = PedigreeRating(
        horse_id="H_SPRINT",
        sire="I Am Invincible",
        dam="Sprinter Mare",
        dam_sire="Exceed And Excel",
        sire_rating=145,
        dam_rating=90,
        dam_sire_rating=135,
        distance_suitability=98.0,  # Bred for sprint
        surface_suitability=85.0,
        overall_pedigree_score=132,
        distance_category="sprint",
    )

    staying_ped = PedigreeRating(
        horse_id="H_STAYING",
        sire="Galileo",
        dam="Stayer Mare",
        dam_sire="Montjeu",
        sire_rating=150,
        dam_rating=100,
        dam_sire_rating=145,
        distance_suitability=95.0,  # Bred to stay
        surface_suitability=90.0,
        overall_pedigree_score=138,
        distance_category="staying",
    )

    for ped in [sprint_ped, staying_ped]:
        print(f"\n{ped.distance_category.upper()} Pedigree:")
        print(f"  Sire: {ped.sire} ({ped.sire_rating}/150)")
        print(f"  Dam Sire: {ped.dam_sire} ({ped.dam_sire_rating}/150)")
        print(f"  Overall Score: {ped.overall_pedigree_score}/150")

    print("\n" + "=" * 70)
