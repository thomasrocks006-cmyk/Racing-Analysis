"""
Racing.com GraphQL API scraper for race card data.

This scraper uses the official Racing.com GraphQL API to extract:
- Race event details (venue, distance, track conditions, class, prize money)
- Field information (horses, jockeys, trainers)
- Entry details (barriers, weights, gear)
- Historical form data

The GraphQL API is significantly more reliable than HTML scraping as it:
- Returns structured JSON data
- Is less prone to breaking changes
- Provides complete, validated data
- Is faster and more efficient

Usage:
    from src.data.scrapers.racing_com_graphql import RacingComGraphQLScraper

    scraper = RacingComGraphQLScraper()
    race_card = scraper.scrape_race("flemington", "2025-11-14", race_number=1)
"""

from __future__ import annotations

import logging
import time
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import requests

from src.data.models import (
    Gear,
    GearType,
    Horse,
    Jockey,
    Race,
    RaceCard,
    Run,
    SexType,
    TrackType,
    Trainer,
)

logger = logging.getLogger(__name__)


class RacingComGraphQLScraper:
    """
    GraphQL API scraper for Racing.com race card data.

    Uses the official Racing.com GraphQL endpoint for reliable, structured data access.
    """

    GRAPHQL_URL = "https://graphql.rmdprod.racing.com/"
    API_KEY = "da2-6nsi4ztsynar3l3frgxf77q5fe"
    
    HEADERS = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    # GraphQL query for fetching race data
    RACE_QUERY = """
    query GetMeetingRace($venueName: String!, $date: String!) {
      GetMeetingByVenue(venueName: $venueName, date: $date) {
        id
        venueName
        venueCode
        date
        track
        trackCondition
        trackRating
        railPosition
        weather
        weatherText
        weatherIcon
        weatherAirTemp
        weatherWindSpeed
        weatherWindDirection
        state
        country
        penetrometer
        races {
          id
          raceNumber
          name
          distance
          class
          status
          raceEntries {
            barrierNumber
            weight
            handicapRating
            gearList
            gearChanges
            gearHasChanges
            emergencyNumber
            emergency
            horse {
              name
              sex
              age
              colour
            }
            jockey {
              name
              surname
            }
            trainer {
              name
              surname
            }
          }
        }
      }
    }
    """

    def __init__(self, delay_between_requests: float = 0.5):
        """
        Initialize GraphQL scraper.

        Args:
            delay_between_requests: Delay in seconds between requests (be polite!)
        """
        self.delay = delay_between_requests
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def scrape_race(
        self, venue: str, race_date: date | str, race_number: int
    ) -> RaceCard:
        """
        Scrape a complete race card from Racing.com GraphQL API.

        Args:
            venue: Venue name (e.g., 'flemington', 'randwick', 'caulfield')
            race_date: Race date (YYYY-MM-DD or date object)
            race_number: Race number (1-12)

        Returns:
            RaceCard object with all race data

        Example:
            >>> scraper = RacingComGraphQLScraper()
            >>> card = scraper.scrape_race("flemington", "2025-11-14", 1)
            >>> print(f"Race: {card.race.race_name}, Runners: {len(card.runs)}")
        """
        if isinstance(race_date, str):
            race_date = date.fromisoformat(race_date)

        venue_name = venue.lower()
        date_str = race_date.isoformat()

        logger.info(f"Scraping {venue_name} {date_str} R{race_number} via GraphQL")

        try:
            # Execute GraphQL query with rate limiting
            time.sleep(self.delay)
            
            response = self.session.post(
                self.GRAPHQL_URL,
                json={
                    "query": self.RACE_QUERY,
                    "variables": {
                        "venueName": venue_name,
                        "date": date_str
                    }
                },
                timeout=15
            )
            response.raise_for_status()

            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                error_msgs = [e.get("message", str(e)) for e in data["errors"]]
                logger.error(f"GraphQL errors: {', '.join(error_msgs)}")
                raise ValueError(f"GraphQL query failed: {error_msgs}")

            # Extract meeting and race data
            meeting = data.get("data", {}).get("GetMeetingByVenue")
            if not meeting:
                raise ValueError(f"No meeting found for {venue_name} on {date_str}")

            # Handle case where API returns a list
            if isinstance(meeting, list):
                if not meeting:
                    raise ValueError(f"No meeting found for {venue_name} on {date_str}")
                meeting = meeting[0]  # Take first meeting (usually the main one, not trials)

            races = meeting.get("races", [])
            if not races:
                raise ValueError(f"No races found at {venue_name} on {date_str}")

            # Filter for our specific race number
            race_data = next((r for r in races if r.get("raceNumber") == race_number), None)
            if not race_data:
                raise ValueError(f"Race {race_number} not found at {venue_name} on {date_str}")
            
            # Build race ID
            venue_code = meeting.get("venueCode", venue_name.upper()[:3])
            race_id = f"{venue_code}-{date_str}-R{race_number}"

            race = self._parse_race(meeting, race_data, race_id, race_date, race_number, venue_code)
            horses, jockeys, trainers, runs, gear = self._parse_entries(
                race_data.get("raceEntries", []), race_id
            )

            # Build race card
            race_card = RaceCard(
                race=race,
                runs=runs,
                horses=horses,
                jockeys=jockeys,
                trainers=trainers,
                gear=gear,
            )

            # Update completeness
            completeness = race_card.validate_completeness()
            race.is_complete = completeness >= 80.0

            logger.info(
                f"✅ Scraped {len(race_card.runs)} runners from {race_id} "
                f"(completeness: {completeness:.1f}%)"
            )

            return race_card

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query GraphQL API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing GraphQL response: {e}", exc_info=True)
            raise

    def _parse_race(
        self, meeting: dict, race_data: dict, race_id: str, race_date: date, race_number: int, venue_code: str
    ) -> Race:
        """
        Parse race details from GraphQL response.

        Args:
            meeting: Meeting data from GraphQL
            race_data: Race data from GraphQL
            race_id: Generated race ID
            race_date: Race date
            race_number: Race number

        Returns:
            Race model instance
        """
        # Parse track type
        track_type = TrackType.TURF  # Default
        track_str = meeting.get("track", "").lower()
        if "synthetic" in track_str or "all weather" in track_str:
            track_type = TrackType.SYNTHETIC

        # Parse race start time
        start_time = None
        start_datetime_str = race_data.get("raceStartDateTime")
        if start_datetime_str:
            try:
                start_time = datetime.fromisoformat(start_datetime_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return Race(
            race_id=race_id,
            date=race_date,
            venue=str(meeting.get("venueCode", "UNK")),
            venue_name=meeting.get("venueName", "Unknown"),
            race_number=race_number,
            race_name=race_data.get("name", f"Race {race_number}"),
            distance=self._parse_distance(race_data.get("distance")) or 1200,  # Default 1200m
            track_condition=meeting.get("trackCondition"),
            track_type=track_type,
            rail_position=meeting.get("railPosition"),
            weather=meeting.get("weather"),
            class_level=race_data.get("class"),
            race_time=start_time.time() if start_time else None,
            actual_start_time=start_time,
            field_size=len(race_data.get("raceEntries", [])) or None,
            data_source="racing.com-graphql",
        )

    def _parse_entries(
        self, entries: list[dict], race_id: str
    ) -> tuple[list[Horse], list[Jockey], list[Trainer], list[Run], list[Gear]]:
        """
        Parse race entries into model instances.

        Args:
            entries: List of race entry data from GraphQL
            race_id: Race ID

        Returns:
            Tuple of (horses, jockeys, trainers, runs, gear)
        """
        horses = []
        jockeys = []
        trainers = []
        runs = []
        gear_list = []

        for entry in entries:
            # Parse horse
            horse_data = entry.get("horse", {})
            horse_name = horse_data.get("name", "Unknown")
            
            sex = SexType.UNKNOWN
            sex_str = horse_data.get("sex", "").upper()
            if sex_str in ["G", "GELDING"]:
                sex = SexType.GELDING
            elif sex_str in ["M", "MARE"]:
                sex = SexType.MARE
            elif sex_str in ["H", "HORSE"]:
                sex = SexType.HORSE
            elif sex_str in ["C", "COLT"]:
                sex = SexType.COLT
            elif sex_str in ["F", "FILLY"]:
                sex = SexType.FILLY

            horse = Horse(
                name=horse_name,
                age=self._parse_int(horse_data.get("age")),
                sex=sex,
                colour=horse_data.get("colour"),
                sire=horse_data.get("sire"),
                dam=horse_data.get("dam"),
            )
            horses.append(horse)

            # Parse jockey
            jockey_data = entry.get("jockey", {})
            jockey_name = jockey_data.get("name") or jockey_data.get("surname", "Unknown")
            
            jockey = Jockey(name=jockey_name)
            jockeys.append(jockey)

            # Parse trainer
            trainer_data = entry.get("trainer", {})
            trainer_name = trainer_data.get("name") or trainer_data.get("surname", "Unknown")
            
            trainer = Trainer(name=trainer_name)
            trainers.append(trainer)

            # Parse run
            barrier = self._parse_int(entry.get("barrierNumber"))
            weight = self._parse_decimal(entry.get("weight"))
            
            run = Run(
                race_id=race_id,
                horse_name=horse_name,
                jockey_name=jockey_name,
                trainer_name=trainer_name,
                barrier=barrier,
                weight=weight,
                handicap_rating=self._parse_int(entry.get("handicapRating")),
                emergency=entry.get("emergency", False),
                emergency_number=self._parse_int(entry.get("emergencyNumber")),
            )
            runs.append(run)

            # Parse gear
            if entry.get("gearList"):
                gear_str = entry.get("gearList", "")
                gear_changes = entry.get("gearChanges", "")
                has_changes = entry.get("gearHasChanges", False)
                
                gear = Gear(
                    race_id=race_id,
                    horse_name=horse_name,
                    gear_type=self._parse_gear_type(gear_str),
                    gear_description=gear_str,
                    is_first_time=has_changes,
                    gear_changes=gear_changes if has_changes else None,
                )
                gear_list.append(gear)

        return horses, jockeys, trainers, runs, gear_list

    def _parse_distance(self, distance_str: str | int | None) -> int | None:
        """Parse distance string/int to meters."""
        if distance_str is None:
            return None
        try:
            # Handle "1200m" or 1200
            if isinstance(distance_str, str):
                distance_str = distance_str.replace("m", "").replace("M", "").strip()
            return int(distance_str)
        except (ValueError, AttributeError):
            return None

    def _parse_decimal(self, value: str | float | None) -> Decimal | None:
        """Parse string/float to Decimal."""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None

    def _parse_int(self, value: str | int | None) -> int | None:
        """Parse string/int to int."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _parse_gear_type(self, gear_str: str) -> GearType:
        """Parse gear description to GearType enum."""
        if not gear_str:
            return GearType.NONE

        gear_lower = gear_str.lower()
        
        if "blinker" in gear_lower:
            return GearType.BLINKERS
        elif "visor" in gear_lower:
            return GearType.VISOR
        elif "tongue" in gear_lower or "tt" in gear_lower:
            return GearType.TONGUE_TIE
        elif "lugging" in gear_lower or "bit" in gear_lower:
            return GearType.LUGGING_BIT
        elif "nose" in gear_lower:
            return GearType.NOSE_ROLL
        elif "winker" in gear_lower:
            return GearType.WINKERS
        elif "hood" in gear_lower:
            return GearType.PACIFIERS
        else:
            return GearType.OTHER

    def get_meetings_by_date(self, race_date: date | str) -> list[dict]:
        """
        Get all race meetings for a specific date.

        Args:
            race_date: Date to query (YYYY-MM-DD or date object)

        Returns:
            List of meeting dictionaries with venue, track conditions, race count, etc.

        Example:
            >>> scraper = RacingComGraphQLScraper()
            >>> meetings = scraper.get_meetings_by_date("2025-11-14")
            >>> for meet in meetings:
            ...     print(f"{meet['venueName']}: {meet['racesCount']} races")
        """
        if isinstance(race_date, str):
            race_date = date.fromisoformat(race_date)

        date_str = race_date.isoformat()

        query = """
        query GetMeetings($date: String!) {
          GetMeetingByDate(date: $date) {
            id
            venueName
            venueCode
            date
            track
            trackCondition
            railPosition
            weather
            state
            country
            racesCount
            races {
              raceNumber
              name
              distance
              status
            }
          }
        }
        """

        try:
            time.sleep(self.delay)
            
            response = self.session.post(
                self.GRAPHQL_URL,
                json={"query": query, "variables": {"date": date_str}},
                timeout=15
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                error_msgs = [e.get("message", str(e)) for e in data["errors"]]
                logger.error(f"GraphQL errors: {', '.join(error_msgs)}")
                return []

            meetings = data.get("data", {}).get("GetMeetingByDate", [])
            if isinstance(meetings, dict):
                meetings = [meetings]

            return meetings

        except Exception as e:
            logger.error(f"Failed to fetch meetings for {date_str}: {e}")
            return []
