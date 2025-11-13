#!/usr/bin/env python3
"""
Test Betfair API integration.

This script demonstrates the Betfair client capabilities:
1. Authentication
2. Market search
3. Live odds retrieval
4. Market movement tracking
5. Steamer/drifter detection

Requirements:
- Betfair account (free)
- API application key (free from Betfair)
- Environment variables set:
  * BETFAIR_USERNAME
  * BETFAIR_PASSWORD
  * BETFAIR_APP_KEY
"""

import logging
import sys
from datetime import date, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data.scrapers.betfair_client import BetfairClient

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_authentication():
    """Test 1: Authentication"""
    print("\n" + "=" * 60)
    print("TEST 1: Betfair Authentication")
    print("=" * 60)

    client = BetfairClient()

    if not client.trading:
        print("❌ FAILED: Client not initialized")
        print("\nPlease set environment variables:")
        print("  export BETFAIR_USERNAME='your_username'")
        print("  export BETFAIR_PASSWORD='your_password'")
        print("  export BETFAIR_APP_KEY='your_app_key'")
        print("\nGet your app key from:")
        print("  https://developer.betfair.com/en/get-started/")
        return False

    success = client.login()

    if success:
        print("✅ Authentication successful!")
        client.logout()
        return True
    else:
        print("❌ Authentication failed - check credentials")
        return False


def test_market_search():
    """Test 2: Market Search"""
    print("\n" + "=" * 60)
    print("TEST 2: Market Search")
    print("=" * 60)

    with BetfairClient() as client:
        if not client.trading:
            print("❌ SKIPPED: Client not initialized")
            return False

        # Try to find a race (today or tomorrow)
        for days_ahead in [0, 1, 2]:
            test_date = date.today() + timedelta(days=days_ahead)

            print(f"\nSearching for Flemington races on {test_date}...")

            market_id = client.find_race_market(
                venue="Flemington", race_date=test_date, race_number=1
            )

            if market_id:
                print(f"✅ Found market: {market_id}")
                return market_id
            else:
                print(f"⚠️  No Flemington R1 found on {test_date}")

        print("\n❌ Could not find any races (try different venue/date)")
        return None


def test_live_odds(market_id: str = None):
    """Test 3: Live Odds Retrieval"""
    print("\n" + "=" * 60)
    print("TEST 3: Live Odds Retrieval")
    print("=" * 60)

    with BetfairClient() as client:
        if not client.trading:
            print("❌ SKIPPED: Client not initialized")
            return False

        if not market_id:
            print("❌ SKIPPED: No market ID provided")
            return False

        print(f"\nFetching market book for {market_id}...")

        market_book = client.get_market_book(market_id)

        if not market_book:
            print("❌ Failed to get market book")
            return False

        print(f"\n✅ Market Data Retrieved:")
        print(f"  Status: {market_book['status']}")
        print(f"  Total Matched: ${market_book['total_matched']:,.2f}")
        print(f"  Runners: {len(market_book['runners'])}")

        print(f"\nTop 5 Runners:")
        sorted_runners = sorted(
            market_book["runners"],
            key=lambda r: r["back_prices"][0]["price"] if r["back_prices"] else 999,
        )

        for i, runner in enumerate(sorted_runners[:5], 1):
            back = runner["back_prices"][0] if runner["back_prices"] else None
            lay = runner["lay_prices"][0] if runner["lay_prices"] else None

            print(f"\n  {i}. {runner.get('runner_name', 'Unknown')}")
            if back:
                print(f"     Back: ${back['price']} (${back['size']:,.0f} available)")
            if lay:
                print(f"     Lay:  ${lay['price']} (${lay['size']:,.0f} available)")
            print(f"     Matched: ${runner['total_matched']:,.0f}")

        return True


def test_get_race_odds():
    """Test 4: Get Race Odds (High-Level API)"""
    print("\n" + "=" * 60)
    print("TEST 4: Get Race Odds (High-Level API)")
    print("=" * 60)

    with BetfairClient() as client:
        if not client.trading:
            print("❌ SKIPPED: Client not initialized")
            return False

        # Try today or tomorrow
        for days_ahead in [0, 1, 2]:
            test_date = date.today() + timedelta(days=days_ahead)

            print(f"\nTrying Flemington {test_date} R1...")

            odds = client.get_race_odds("Flemington", test_date, 1)

            if odds:
                print(f"\n✅ Retrieved {len(odds)} odds entries:")

                for i, odd in enumerate(odds[:5], 1):
                    print(f"  {i}. ${odd.odds_decimal} (Rank {odd.rank})")
                    print(f"     Matched: ${odd.total_matched}")
                    print(f"     Volume: ${odd.volume}")

                return True

        print("\n⚠️  No odds available (try different date/venue)")
        return False


def test_market_tracking(market_id: str = None, duration_secs: int = 30):
    """Test 5: Market Movement Tracking"""
    print("\n" + "=" * 60)
    print("TEST 5: Market Movement Tracking")
    print("=" * 60)

    if not market_id:
        print("❌ SKIPPED: No market ID provided")
        print("(This test requires an active market)")
        return False

    print(f"\n⚠️  This will track market for {duration_secs} seconds...")
    print("Press Ctrl+C to stop early")

    with BetfairClient() as client:
        if not client.trading:
            print("❌ SKIPPED: Client not initialized")
            return False

        # Track for short duration (30 sec for demo, would be 60-120 min normally)
        snapshots = client.track_market_movements(
            market_id=market_id,
            duration_mins=0,  # Will stop after duration_secs
            interval_secs=10,  # Update every 10 seconds
        )

        if not snapshots:
            print("❌ No snapshots collected")
            return False

        print(f"\n✅ Collected {len(snapshots)} snapshots")

        # Analyze movements
        movements = client.detect_steamers_drifters(snapshots, threshold_pct=5.0)

        if movements["steamers"]:
            print(f"\n🔥 STEAMERS ({len(movements['steamers'])}):")
            for steamer in movements["steamers"][:3]:
                print(
                    f"  • {steamer['runner']}: ${steamer['start_price']:.2f} → ${steamer['end_price']:.2f} ({steamer['change_pct']:+.1f}%)"
                )

        if movements["drifters"]:
            print(f"\n📉 DRIFTERS ({len(movements['drifters'])}):")
            for drifter in movements["drifters"][:3]:
                print(
                    f"  • {drifter['runner']}: ${drifter['start_price']:.2f} → ${drifter['end_price']:.2f} ({drifter['change_pct']:+.1f}%)"
                )

        if not movements["steamers"] and not movements["drifters"]:
            print("\n📊 No significant movements detected (market stable)")

        return True


def main():
    """Run all Betfair tests."""
    print("\n" + "=" * 60)
    print("🏇 BETFAIR API INTEGRATION TEST SUITE")
    print("=" * 60)

    results = {}

    # Test 1: Authentication
    results["auth"] = test_authentication()

    if not results["auth"]:
        print("\n❌ Authentication failed - cannot continue tests")
        print("\nSetup Instructions:")
        print("1. Create Betfair account: https://www.betfair.com.au/")
        print("2. Get API key: https://developer.betfair.com/")
        print("3. Set environment variables (see above)")
        return

    # Test 2: Market Search
    market_id = test_market_search()
    results["search"] = market_id is not None

    # Test 3: Live Odds
    if market_id:
        results["live_odds"] = test_live_odds(market_id)
    else:
        results["live_odds"] = False
        print("\n⚠️  Skipped Test 3 (no market found)")

    # Test 4: Get Race Odds (high-level API)
    results["race_odds"] = test_get_race_odds()

    # Test 5: Market Tracking (optional, requires active market)
    # Uncomment to enable:
    # if market_id:
    #     results['tracking'] = test_market_tracking(market_id, duration_secs=30)

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Betfair integration working.")
    elif passed > 0:
        print("\n⚠️  Some tests passed. Check failed tests above.")
    else:
        print("\n❌ All tests failed. Check configuration.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        logger.error(f"Test suite error: {e}", exc_info=True)
