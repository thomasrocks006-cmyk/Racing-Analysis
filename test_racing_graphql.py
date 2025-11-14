"""
Test the Racing.com GraphQL scraper with live data.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.scrapers.racing_com_graphql import RacingComGraphQLScraper


def test_get_meetings():
    """Test fetching all meetings for today."""
    print("=" * 80)
    print("TEST 1: Get Today's Meetings")
    print("=" * 80)
    
    scraper = RacingComGraphQLScraper()
    today = date.today()
    
    print(f"\nQuerying meetings for {today}...")
    meetings = scraper.get_meetings_by_date(today)
    
    print(f"\n✅ Found {len(meetings)} meetings:")
    for meet in meetings:
        print(f"\n📍 {meet.get('venueName')} (Code: {meet.get('venueCode')})")
        print(f"   State: {meet.get('state')} | Track: {meet.get('trackCondition')}")
        print(f"   Rail: {meet.get('railPosition')} | Weather: {meet.get('weather')}")
        print(f"   Races: {meet.get('racesCount', len(meet.get('races', [])))}")
        
        races = meet.get('races', [])
        if races:
            print(f"   First: R{races[0].get('raceNumber')} - {races[0].get('name')}")


def test_scrape_race():
    """Test scraping a specific race."""
    print("\n" + "=" * 80)
    print("TEST 2: Scrape a Specific Race")
    print("=" * 80)
    
    scraper = RacingComGraphQLScraper()
    today = date.today()
    
    # Get first available meeting
    meetings = scraper.get_meetings_by_date(today)
    
    if not meetings:
        print(f"\n⚠️  No meetings found for {today}")
        # Try tomorrow
        tomorrow = today + timedelta(days=1)
        print(f"Trying {tomorrow}...")
        meetings = scraper.get_meetings_by_date(tomorrow)
        today = tomorrow
    
    if not meetings:
        print("\n❌ No meetings found for today or tomorrow")
        return
    
    # Find a meeting with races
    target_meeting = None
    for meet in meetings:
        races = meet.get('races', [])
        if races and meet.get('racesCount', 0) > 0:
            target_meeting = meet
            break
    
    if not target_meeting:
        print("\n❌ No meetings with active races found")
        return
    
    venue = target_meeting['venueName']
    race_number = 1  # Try first race
    
    print(f"\nScraping {venue} R{race_number} on {today}...")
    
    try:
        race_card = scraper.scrape_race(venue, today, race_number)
        
        print(f"\n✅ SUCCESS! Scraped race card:")
        print(f"\n🏁 RACE DETAILS:")
        print(f"   ID: {race_card.race.race_id}")
        print(f"   Name: {race_card.race.race_name}")
        print(f"   Venue: {race_card.race.venue}")
        print(f"   Distance: {race_card.race.distance}m")
        print(f"   Class: {race_card.race.class_level}")
        print(f"   Track: {race_card.race.track_condition} ({race_card.race.track_type.value if race_card.race.track_type else 'N/A'})")
        print(f"   Rail: {race_card.race.rail_position}")
        print(f"   Weather: {race_card.race.weather}")
        print(f"   Prize: ${race_card.race.prize_money}")
        
        print(f"\n🐴 RUNNERS ({len(race_card.runs)}):")
        for i, run in enumerate(race_card.runs[:10], 1):  # Show first 10
            horse = next((h for h in race_card.horses if h.name == run.horse_name), None)
            gear = next((g for g in race_card.gear if g.horse_name == run.horse_name), None)
            
            print(f"\n   {i}. {run.horse_name}")
            if horse:
                print(f"      Age/Sex: {horse.age}yo {horse.sex.value} | Colour: {horse.colour}")
            print(f"      Jockey: {run.jockey_name}")
            print(f"      Trainer: {run.trainer_name}")
            print(f"      Barrier: {run.barrier} | Weight: {run.weight}kg")
            if gear:
                print(f"      Gear: {gear.gear_description}")
                if gear.is_first_time:
                    print(f"      ⚙️  GEAR CHANGE: {gear.gear_changes}")
        
        if len(race_card.runs) > 10:
            print(f"\n   ... and {len(race_card.runs) - 10} more runners")
        
        completeness = race_card.validate_completeness()
        print(f"\n📊 Data Completeness: {completeness:.1f}%")
        print(f"   Complete: {race_card.race.is_complete}")
        
    except Exception as e:
        print(f"\n❌ Failed to scrape race: {e}")
        import traceback
        traceback.print_exc()


def test_historical_race():
    """Test scraping a historical race with known data."""
    print("\n" + "=" * 80)
    print("TEST 3: Scrape Historical Race")
    print("=" * 80)
    
    scraper = RacingComGraphQLScraper()
    
    # Try yesterday
    yesterday = date.today() - timedelta(days=1)
    
    print(f"\nQuerying meetings for {yesterday}...")
    meetings = scraper.get_meetings_by_date(yesterday)
    
    if not meetings:
        print(f"\n⚠️  No meetings found for {yesterday}")
        return
    
    print(f"✅ Found {len(meetings)} meetings")
    
    # Try to scrape first race from first meeting
    venue = meetings[0]['venueName']
    
    try:
        race_card = scraper.scrape_race(venue, yesterday, 1)
        print(f"\n✅ Successfully scraped {venue} R1 from {yesterday}")
        print(f"   Runners: {len(race_card.runs)}")
        print(f"   Completeness: {race_card.validate_completeness():.1f}%")
    except Exception as e:
        print(f"\n⚠️  Could not scrape historical race: {e}")


if __name__ == "__main__":
    print("\n🏇 RACING.COM GRAPHQL SCRAPER TESTS\n")
    
    try:
        test_get_meetings()
        test_scrape_race()
        test_historical_race()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETE")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
