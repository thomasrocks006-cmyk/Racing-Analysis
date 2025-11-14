"""
Tests for Jockey/Trainer Stats Builder.

Tests cover:
- Database aggregation logic
- Win rate calculations
- Venue specialization detection
- Distance performance analysis
- Jockey-trainer combinations
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from src.data.models import JockeyStat, TrainerStat
from src.data.scrapers.jockey_stats import JockeyStatsBuilder


class TestJockeyStatsBuilder:
    """Test suite for JockeyStatsBuilder."""

    def test_builder_initialization(self):
        """Test builder initialization with default settings."""
        builder = JockeyStatsBuilder()
        assert builder.db_path == "racing.db"
        assert builder.conn is None

    def test_builder_initialization_custom_path(self):
        """Test builder initialization with custom database path."""
        builder = JockeyStatsBuilder(db_path="/custom/path/racing.db")
        assert builder.db_path == "/custom/path/racing.db"

    @pytest.mark.skipif(
        not hasattr(JockeyStatsBuilder, "__enter__"),
        reason="DuckDB not available"
    )
    def test_context_manager(self):
        """Test context manager opens and closes database connection."""
        with patch("src.data.scrapers.jockey_stats.duckdb") as mock_duckdb:
            mock_conn = Mock()
            mock_duckdb.connect.return_value = mock_conn
            
            with JockeyStatsBuilder() as builder:
                assert builder.conn == mock_conn
            
            # Connection should be closed on exit
            mock_conn.close.assert_called_once()

    def test_calculate_jockey_stats_no_connection(self):
        """Test that calculating stats without connection raises error."""
        builder = JockeyStatsBuilder()
        
        with pytest.raises(RuntimeError, match="Database not connected"):
            builder.calculate_jockey_stats("JOCKEY123")

    @patch("src.data.scrapers.jockey_stats.duckdb")
    def test_calculate_jockey_stats_basic(self, mock_duckdb):
        """Test basic jockey stats calculation."""
        # Setup mock database connection
        mock_conn = Mock()
        mock_duckdb.connect.return_value = mock_conn
        
        # Mock query results
        # Overall stats: (total_rides, total_wins, total_places)
        mock_conn.execute.return_value.fetchone.side_effect = [
            (100, 15, 40),  # Overall stats
            (50, 12, None),  # Strike rate stats
            (10, 3, None),   # Recent form
        ]
        
        # Mock fetchall for venue and distance stats
        mock_conn.execute.return_value.fetchall.return_value = []
        
        with JockeyStatsBuilder() as builder:
            stats = builder.calculate_jockey_stats("JOCKEY123", lookback_days=365)
        
        assert isinstance(stats, JockeyStat)
        assert stats.jockey_id == "JOCKEY123"
        assert stats.total_rides == 100
        assert stats.total_wins == 15
        assert stats.total_places == 40
        
        # Win rate = 15/100 = 0.15
        assert stats.win_rate == Decimal("0.15")
        
        # Place rate = 40/100 = 0.40
        assert stats.place_rate == Decimal("0.40")

    @patch("src.data.scrapers.jockey_stats.duckdb")
    def test_calculate_jockey_stats_zero_rides(self, mock_duckdb):
        """Test jockey stats calculation with zero rides."""
        mock_conn = Mock()
        mock_duckdb.connect.return_value = mock_conn
        
        # Mock zero rides
        mock_conn.execute.return_value.fetchone.side_effect = [
            (0, 0, 0),   # Overall stats
            (0, 0, None),  # Strike rate
            (0, 0, None),  # Recent form
        ]
        mock_conn.execute.return_value.fetchall.return_value = []
        
        with JockeyStatsBuilder() as builder:
            stats = builder.calculate_jockey_stats("JOCKEY_NEW", lookback_days=365)
        
        assert stats.total_rides == 0
        assert stats.total_wins == 0
        assert stats.win_rate == Decimal("0")
        assert stats.place_rate == Decimal("0")

    @patch("src.data.scrapers.jockey_stats.duckdb")
    def test_calculate_trainer_stats_basic(self, mock_duckdb):
        """Test basic trainer stats calculation."""
        mock_conn = Mock()
        mock_duckdb.connect.return_value = mock_conn
        
        # Mock query results
        mock_conn.execute.return_value.fetchone.side_effect = [
            (200, 30, 80),   # Overall stats
            (100, 25, None),  # Strike rate
            (20, 5, None),    # Recent form
        ]
        mock_conn.execute.return_value.fetchall.return_value = []
        
        with JockeyStatsBuilder() as builder:
            stats = builder.calculate_trainer_stats("TRAINER456", lookback_days=365)
        
        assert isinstance(stats, TrainerStat)
        assert stats.trainer_id == "TRAINER456"
        assert stats.total_runners == 200
        assert stats.total_wins == 30
        
        # Win rate = 30/200 = 0.15
        assert stats.win_rate == Decimal("0.15")

    @patch("src.data.scrapers.jockey_stats.duckdb")
    def test_calculate_venue_stats(self, mock_duckdb):
        """Test venue-specific statistics calculation."""
        mock_conn = Mock()
        mock_duckdb.connect.return_value = mock_conn
        
        # Mock venue stats query result
        mock_conn.execute.return_value.fetchall.return_value = [
            ("Flemington", 50, 10),  # 50 rides, 10 wins
            ("Randwick", 30, 9),      # 30 rides, 9 wins
        ]
        
        builder = JockeyStatsBuilder()
        builder.conn = mock_conn
        
        venue_stats = builder._calculate_venue_stats(
            "JOCKEY123",
            date(2024, 1, 1),
            date(2024, 12, 31),
            is_jockey=True
        )
        
        assert "Flemington" in venue_stats
        assert venue_stats["Flemington"]["rides"] == 50
        assert venue_stats["Flemington"]["wins"] == 10
        assert venue_stats["Flemington"]["win_rate"] == 0.2
        
        assert "Randwick" in venue_stats
        assert venue_stats["Randwick"]["win_rate"] == 0.3

    @patch("src.data.scrapers.jockey_stats.duckdb")
    def test_calculate_distance_stats(self, mock_duckdb):
        """Test distance-specific statistics calculation."""
        mock_conn = Mock()
        mock_duckdb.connect.return_value = mock_conn
        
        # Mock distance stats query result
        mock_conn.execute.return_value.fetchall.return_value = [
            ("sprint", 40, 8),   # 40 rides, 8 wins
            ("mile", 35, 6),     # 35 rides, 6 wins
            ("middle", 25, 4),   # 25 rides, 4 wins
        ]
        
        builder = JockeyStatsBuilder()
        builder.conn = mock_conn
        
        distance_stats = builder._calculate_distance_stats(
            "JOCKEY123",
            date(2024, 1, 1),
            date(2024, 12, 31),
            is_jockey=True
        )
        
        assert "sprint" in distance_stats
        assert distance_stats["sprint"]["rides"] == 40
        assert distance_stats["sprint"]["wins"] == 8
        assert distance_stats["sprint"]["win_rate"] == 0.2

    @patch("src.data.scrapers.jockey_stats.duckdb")
    def test_calculate_jockey_combos(self, mock_duckdb):
        """Test jockey-trainer combination statistics."""
        mock_conn = Mock()
        mock_duckdb.connect.return_value = mock_conn
        
        # Mock jockey combo query result
        mock_conn.execute.return_value.fetchall.return_value = [
            ("JOCKEY1", "John Smith", 25, 8),    # 25 rides, 8 wins
            ("JOCKEY2", "Jane Doe", 15, 3),      # 15 rides, 3 wins
        ]
        
        builder = JockeyStatsBuilder()
        builder.conn = mock_conn
        
        combos = builder._calculate_jockey_combos(
            "TRAINER456",
            date(2024, 1, 1),
            date(2024, 12, 31)
        )
        
        assert "JOCKEY1" in combos
        assert combos["JOCKEY1"]["name"] == "John Smith"
        assert combos["JOCKEY1"]["rides"] == 25
        assert combos["JOCKEY1"]["wins"] == 8
        assert combos["JOCKEY1"]["win_rate"] == 0.32  # 8/25

    @patch("src.data.scrapers.jockey_stats.duckdb")
    def test_batch_calculate_jockey_stats(self, mock_duckdb):
        """Test batch calculation of jockey statistics."""
        mock_conn = Mock()
        mock_duckdb.connect.return_value = mock_conn
        
        # Mock successful stats calculation
        def mock_stats_calc(jockey_id, lookback_days):
            return JockeyStat(
                jockey_id=jockey_id,
                stat_date=date.today(),
                lookback_days=lookback_days,
                total_rides=100,
                total_wins=15,
                total_places=40,
                win_rate=Decimal("0.15"),
                place_rate=Decimal("0.40"),
                strike_rate=Decimal("0.20"),
                recent_rides=10,
                recent_wins=2,
                recent_win_rate=Decimal("0.20"),
            )
        
        with JockeyStatsBuilder() as builder:
            with patch.object(builder, "calculate_jockey_stats", side_effect=mock_stats_calc):
                jockey_ids = ["JOCKEY1", "JOCKEY2", "JOCKEY3"]
                stats_list = builder.batch_calculate_jockey_stats(jockey_ids, lookback_days=365)
        
        assert len(stats_list) == 3
        assert all(isinstance(s, JockeyStat) for s in stats_list)
        assert stats_list[0].jockey_id == "JOCKEY1"
        assert stats_list[1].jockey_id == "JOCKEY2"
        assert stats_list[2].jockey_id == "JOCKEY3"

    @patch("src.data.scrapers.jockey_stats.duckdb")
    def test_batch_calculate_trainer_stats(self, mock_duckdb):
        """Test batch calculation of trainer statistics."""
        mock_conn = Mock()
        mock_duckdb.connect.return_value = mock_conn
        
        def mock_trainer_calc(trainer_id, lookback_days):
            return TrainerStat(
                trainer_id=trainer_id,
                stat_date=date.today(),
                lookback_days=lookback_days,
                total_runners=200,
                total_wins=30,
                total_places=80,
                win_rate=Decimal("0.15"),
                place_rate=Decimal("0.40"),
                strike_rate=Decimal("0.25"),
                recent_runners=20,
                recent_wins=4,
                recent_win_rate=Decimal("0.20"),
            )
        
        with JockeyStatsBuilder() as builder:
            with patch.object(builder, "calculate_trainer_stats", side_effect=mock_trainer_calc):
                trainer_ids = ["TRAINER1", "TRAINER2"]
                stats_list = builder.batch_calculate_trainer_stats(trainer_ids)
        
        assert len(stats_list) == 2
        assert all(isinstance(s, TrainerStat) for s in stats_list)

    @patch("src.data.scrapers.jockey_stats.duckdb")
    def test_specialist_venue_detection(self, mock_duckdb):
        """Test detection of specialist venues."""
        mock_conn = Mock()
        mock_duckdb.connect.return_value = mock_conn
        
        # Mock overall stats with 15% win rate
        mock_conn.execute.return_value.fetchone.side_effect = [
            (100, 15, 40),  # Overall: 15% win rate
            (50, 12, None),  # Strike rate
            (10, 3, None),   # Recent form
        ]
        
        # Mock venue stats - Flemington has 25% (specialist), Randwick has 10% (not specialist)
        mock_conn.execute.return_value.fetchall.side_effect = [
            [
                ("Flemington", 20, 5),  # 25% win rate
                ("Randwick", 30, 3),    # 10% win rate
            ],
            [],  # Distance stats
        ]
        
        with JockeyStatsBuilder() as builder:
            stats = builder.calculate_jockey_stats("JOCKEY123")
        
        # Flemington should be identified as specialist venue (25% > 15%)
        assert "Flemington" in stats.specialist_venues
        # Randwick should NOT be specialist (10% < 15%)
        assert "Randwick" not in stats.specialist_venues


@pytest.mark.integration
class TestJockeyStatsBuilderIntegration:
    """Integration tests requiring actual database."""

    @pytest.mark.skip(reason="Requires populated database")
    def test_calculate_stats_with_real_database(self):
        """
        Test stats calculation with real database.
        
        Skipped by default - requires a populated racing database.
        """
        pytest.skip("Requires populated racing database")
