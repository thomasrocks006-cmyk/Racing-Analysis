"""
Web scrapers for racing data collection.

Available scrapers:
- RacingComScraper: Race cards and field information
- StewardsScraper: Stewards reports and incidents
- MarketOddsCollector: Starting prices and odds data
- WeatherAPI: Track weather metrics (BOM/Weatherzone)
- TABOddsScraper: Fixed odds bookmaker markets
- RacingFormScraper: Historical form with sectional times
"""

from src.data.scrapers.form_scraper import RacingFormScraper
from src.data.scrapers.market_odds import MarketOddsCollector
from src.data.scrapers.racing_com import RacingComScraper
from src.data.scrapers.stewards import StewardsScraper
from src.data.scrapers.tab_odds import TABOddsScraper
from src.data.scrapers.weather_api import WeatherAPI

__all__ = [
    "RacingComScraper",
    "StewardsScraper",
    "MarketOddsCollector",
    "WeatherAPI",
    "TABOddsScraper",
    "RacingFormScraper",
]
