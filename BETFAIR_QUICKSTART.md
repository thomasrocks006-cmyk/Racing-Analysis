# Betfair Quick Start Guide

## 1. Setup (5 minutes)

### Get Betfair Credentials

```bash
# 1. Create account: https://www.betfair.com.au/
# 2. Get API key: https://developer.betfair.com/ (My Account → API Settings)
# 3. Set environment variables:

export BETFAIR_USERNAME='your_username'
export BETFAIR_PASSWORD='your_password'
export BETFAIR_APP_KEY='your_app_key'
```

### Install Library

```bash
pip install betfairlightweight
```

## 2. Basic Usage

### Get Live Odds

```python
from src.data.scrapers.betfair_client import BetfairClient
from datetime import date

with BetfairClient() as client:
    odds = client.get_race_odds("Flemington", date.today(), 1)

    for odd in odds[:5]:
        print(f"${odd.odds_decimal} (Matched: ${odd.total_matched})")
```

### Track Market Movements

```python
with BetfairClient() as client:
    market_id = client.find_race_market("Randwick", date.today(), 3)

    snapshots = client.track_market_movements(
        market_id,
        duration_mins=60,
        interval_secs=300
    )

    movements = client.detect_steamers_drifters(snapshots)

    print(f"🔥 Steamers: {len(movements['steamers'])}")
    print(f"📉 Drifters: {len(movements['drifters'])}")
```

## 3. Test Your Setup

```bash
python test_betfair.py
```

Expected output:

```
✅ Authentication successful!
✅ Found market: 1.234567890
✅ Retrieved 12 odds entries
```

## 4. Common Issues

### "Client not initialized"

→ Check environment variables are set

```bash
echo $BETFAIR_USERNAME  # Should show your username
```

### "Authentication failed"

→ Verify credentials on Betfair website
→ Check app key is correct (32-character string)

### "No market found"

→ Race not available on Betfair yet (usually listed 24-48h before)
→ Try different venue/date

## 5. API Limits

- Free tier: 1,000 requests/hour
- Our typical usage: 200-500 requests/day
- Well within limits ✅

## 6. Next Steps

After setup:

1. Test on live race day
2. Integrate with database
3. Set up continuous monitoring
4. Build steam/drift alerts
