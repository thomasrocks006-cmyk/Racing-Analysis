"""
Class ratings calculator for racing data.

Implements Category 19 from the quantitative pipeline:
- Race class level assessment
- Prize money weighting
- Field quality analysis
- Historical class performance

Usage:
    from src.features.class_ratings import ClassRatingsEngine

    engine = ClassRatingsEngine()
    rating = engine.calculate_class_rating(race_id, horse_id)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import duckdb

logger = logging.getLogger(__name__)


@dataclass
class ClassRating:
    """Class rating result."""

    horse_id: str
    race_id: str
    race_class: str
    prize_money: int
    field_quality: float
    class_score: int  # 0-150
    percentile: float | None


class ClassRatingsEngine:
    """
    Calculate class ratings for horses.

    Class ratings measure the quality of opposition faced:
    - Group 1: 140-150
    - Group 2: 130-139
    - Group 3: 120-129
    - Listed: 110-119
    - BM100+: 100-109
    - BM78-99: 85-99
    - BM64-77: 70-84
    - Maiden: 50-69
    """

    # Class level base scores
    CLASS_SCORES = {
        "g1": 145,
        "group 1": 145,
        "g2": 135,
        "group 2": 135,
        "g3": 125,
        "group 3": 125,
        "listed": 115,
        "bm100": 105,
        "bm90": 95,
        "bm78": 85,
        "bm70": 75,
        "bm64": 70,
        "maiden": 60,
        "mdn": 60,
    }

    def __init__(self, db_path: str = "data/racing.duckdb"):
        """Initialize class ratings engine."""
        self.db_path = db_path

    def calculate_class_rating(self, race_id: str, horse_id: str) -> ClassRating:
        """
        Calculate class rating for a performance.

        Args:
            race_id: Race identifier
            horse_id: Horse identifier

        Returns:
            ClassRating object
        """
        con = duckdb.connect(self.db_path, read_only=True)

        try:
            # Get race details
            query = """
                SELECT
                    r.class_level,
                    r.prize_money,
                    r.field_size,
                    res.finish_position
                FROM results res
                JOIN races r ON res.race_id = r.race_id
                JOIN runs run ON res.run_id = run.run_id
                WHERE r.race_id = ? AND run.horse_id = ?
            """

            row = con.execute(query, [race_id, horse_id]).fetchone()

            if not row:
                raise ValueError(f"No result found for {race_id} / {horse_id}")

            class_level, prize_money, field_size, finish_pos = row

            # Base class score
            base_score = self._get_class_score(class_level)

            # Prize money adjustment (+/- 5 points)
            prize_adj = self._calculate_prize_adjustment(prize_money or 0)

            # Field quality adjustment (+/- 5 points)
            field_quality = self._calculate_field_quality(race_id)

            # Final score
            class_score = int(base_score + prize_adj + (field_quality * 5))
            class_score = max(50, min(150, class_score))

            return ClassRating(
                horse_id=horse_id,
                race_id=race_id,
                race_class=class_level or "Unknown",
                prize_money=prize_money or 0,
                field_quality=field_quality,
                class_score=class_score,
                percentile=None,
            )

        finally:
            con.close()

    def _get_class_score(self, class_level: str | None) -> int:
        """Get base score for class level."""
        if not class_level:
            return 70  # Default to mid-level

        class_lower = class_level.lower().strip()

        # Exact match
        if class_lower in self.CLASS_SCORES:
            return self.CLASS_SCORES[class_lower]

        # Parse BM ratings (e.g., "BM78" -> 85)
        if "bm" in class_lower:
            try:
                # Extract number
                bm_num = int("".join(c for c in class_lower if c.isdigit()))
                # Map to score (rough approximation)
                if bm_num >= 100:
                    return 105
                elif bm_num >= 90:
                    return 95
                elif bm_num >= 78:
                    return 85
                elif bm_num >= 70:
                    return 75
                else:
                    return 70
            except ValueError:
                pass

        # Check for group races
        for key in self.CLASS_SCORES:
            if key in class_lower:
                return self.CLASS_SCORES[key]

        logger.warning(f"Unknown class level: {class_level}, using default 70")
        return 70

    def _calculate_prize_adjustment(self, prize_money: int) -> float:
        """
        Calculate adjustment based on prize money.

        Returns adjustment in range -5 to +5
        """
        if prize_money == 0:
            return 0

        # $100k = baseline (0 adjustment)
        # $1M+ = +5
        # $20k = -5
        baseline = 100000

        if prize_money >= 1000000:
            return 5.0
        elif prize_money <= 20000:
            return -5.0
        else:
            # Linear scale
            ratio = prize_money / baseline
            return (ratio - 1) * 5

    def _calculate_field_quality(self, race_id: str) -> float:
        """
        Calculate field quality score (0-1).

        Based on:
        - Number of previous winners
        - Average class of field
        - Presence of Group performers
        """
        # TODO: Implement with historical data
        # For now, return neutral
        return 0.5

    def get_horse_average_class(self, horse_id: str, last_n_starts: int = 5) -> dict:
        """Get average class rating over recent starts."""
        con = duckdb.connect(self.db_path, read_only=True)

        try:
            query = """
                SELECT
                    r.race_id,
                    r.class_level,
                    r.prize_money,
                    r.date,
                    res.class_rating
                FROM results res
                JOIN races r ON res.race_id = r.race_id
                JOIN runs run ON res.run_id = run.run_id
                WHERE run.horse_id = ?
                ORDER BY r.date DESC
                LIMIT ?
            """

            rows = con.execute(query, [horse_id, last_n_starts]).fetchall()

            if not rows:
                return {"average": None, "best": None, "starts": 0}

            ratings = []
            for row in rows:
                if row[4] is not None:
                    ratings.append(row[4])
                else:
                    # Calculate on the fly
                    rating = self.calculate_class_rating(row[0], horse_id)
                    ratings.append(rating.class_score)

            import statistics

            return {
                "average": statistics.mean(ratings),
                "best": max(ratings),
                "worst": min(ratings),
                "starts": len(ratings),
            }

        finally:
            con.close()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    engine = ClassRatingsEngine()

    print("\nClass Rating Scale:")
    print("  Group 1:     140-150")
    print("  Group 2:     130-139")
    print("  Group 3:     120-129")
    print("  Listed:      110-119")
    print("  BM100+:      100-109")
    print("  BM78-99:     85-99")
    print("  Maiden:      50-69")
