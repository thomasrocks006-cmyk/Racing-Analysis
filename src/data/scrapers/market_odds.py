"""
Market odds collector for racing data.

Collects starting prices and basic market information.
Full Betfair integration will be implemented in Week 2.

Sources:
- Racing.com starting prices
- TAB fixed odds (where available)

Usage:
    from src.data.scrapers.market_odds import MarketOddsCollector

    collector = MarketOddsCollector()
    odds = collector.collect_starting_prices("FLE", "2025-11-12", race_number=1)
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal

import requests

from src.data.models import MarketOdds, OddsType

logger = logging.getLogger(__name__)


class MarketOddsCollector:
    """
    Collector for market odds data.

    Phase 1: Starting prices only
    Phase 2 (Week 2): Full Betfair integration with time-series data
    """

    BASE_URL = "https://www.racing.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def __init__(self):
        """Initialize odds collector."""
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def collect_starting_prices(
        self, venue: str, race_date: date | str, race_number: int
    ) -> list[MarketOdds]:
        """
        Collect starting prices for a race.

        Args:
            venue: Venue code
            race_date: Race date
            race_number: Race number

        Returns:
            List of MarketOdds objects (one per runner)
        """
        if isinstance(race_date, str):
            race_date = date.fromisoformat(race_date)

        race_id = f"{venue}-{race_date.isoformat()}-R{race_number}"

        logger.info(f"Collecting starting prices for {race_id}")

        # TODO: Implement actual odds collection
        # For now, return sample structure
        odds_data = self._create_sample_odds(race_id)

        logger.info(f"Collected starting prices for {len(odds_data)} runners")
        return odds_data

    def _create_sample_odds(self, race_id: str) -> list[MarketOdds]:
        """Create sample odds data."""
        # Sample starting prices for 10 runners
        sample_sp = [
            Decimal("3.50"),
            Decimal("4.20"),
            Decimal("5.00"),
            Decimal("7.50"),
            Decimal("8.00"),
            Decimal("11.00"),
            Decimal("15.00"),
            Decimal("21.00"),
            Decimal("31.00"),
            Decimal("51.00"),
        ]

        odds_list = []
        for i, sp in enumerate(sample_sp, 1):
            # Create run_id (would come from actual race card)
            run_id = f"{race_id}-H{1000 + i}"

            # Win odds
            odds_list.append(
                MarketOdds(
                    odds_id=f"ODDS-{run_id}-WIN",
                    run_id=run_id,
                    race_id=race_id,
                    timestamp=datetime.now(),
                    source="racing.com",
                    odds_type=OddsType.WIN,
                    odds_decimal=sp,
                    rank=i,  # Rank by favoritism
                )
            )

            # Place odds (roughly 1/4 of win odds for top 3)
            if i <= 3:
                place_odds = round(
                    Decimal("1.0") + (sp - Decimal("1.0")) / Decimal("4.0"), 2
                )
                odds_list.append(
                    MarketOdds(
                        odds_id=f"ODDS-{run_id}-PLACE",
                        run_id=run_id,
                        race_id=race_id,
                        timestamp=datetime.now(),
                        source="racing.com",
                        odds_type=OddsType.PLACE,
                        odds_decimal=place_odds,
                    )
                )

        return odds_list

    def collect_betfair_odds(
        self, venue: str, race_date: date | str, race_number: int
    ) -> list[MarketOdds]:
        """
        Collect Betfair exchange odds (time-series).

        Uses the BetfairClient for real API integration.

        Args:
            venue: Venue code
            race_date: Race date
            race_number: Race number

        Returns:
            List of MarketOdds objects with timestamp series
        """
        try:
            from src.data.scrapers.betfair_client import BetfairClient

            with BetfairClient() as client:
                odds = client.get_race_odds(venue, race_date, race_number)

                if odds:
                    logger.info(f"✅ Collected Betfair odds for {len(odds)} runners")
                    return odds
                else:
                    logger.warning("No Betfair odds available")
                    return []

        except ImportError:
            logger.error("BetfairClient not available - install betfairlightweight")
            return []
        except Exception as e:
            logger.error(f"Error collecting Betfair odds: {e}")
            return []

    def close(self):
        """Close session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with MarketOddsCollector() as collector:
        odds = collector.collect_starting_prices("FLE", date.today(), 1)

        print(f"\nStarting Prices: {len(odds)} entries")
        print("\nWin odds (top 5):")
        win_odds = [o for o in odds if o.odds_type == OddsType.WIN][:5]
        for i, odd in enumerate(win_odds, 1):
            print(f"  {i}. ${odd.odds_decimal} (Rank {odd.rank})")
