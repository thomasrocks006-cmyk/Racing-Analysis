# Critical Analysis Part 5d: Search Strategy & Implementation Framework

**Covers**: Intelligent Search Methodology, Discovery vs Fixed Sources, Implementation Priorities, Integration Architecture

**Analysis Framework**: Search Pattern Design, Source Selection Logic, Quality Verification, Cost Optimization, Phase-Based Implementation

---

## INTELLIGENT SEARCH STRATEGY FRAMEWORK

**Overall Approach**:
- **Fixed Sources**: Core sources checked EVERY RACE (form guide, odds, trials, stewards)
- **Intelligent Discovery**: Agent decides contextually what additional sources to search
- **Quality Verification**: Cross-reference sources, detect contradictions, timestamp validation
- **Cost Optimization**: Prioritize free/low-cost sources, expensive sources only when high value

**Key Insight**: Search strategy is NOT just a fixed list. Agent intelligently discovers relevant information based on race context, horse specifics, and available data quality.

---

## PART 1: FIXED SOURCES (CHECKED EVERY RACE)

**Definition**: Sources that provide CORE DATA required for every race analysis, checked systematically regardless of race context.

---

### Fixed Source Category 1: Official Racing Data (TIER 1 - Phase 1 CRITICAL)

**Sources**:
1. **Racing.com Form Guide** (1.2)
   - **What**: Complete race card, horse/jockey/trainer details, weights, barriers
   - **Why Fixed**: Foundation data required for ALL races
   - **Access**: Authenticated scraping (Selenium + cookies)
   - **Cost**: $0.02-$0.10/race (amortized authentication)
   - **Frequency**: Once per race (day-of or day-before)

2. **Barrier Trial Results** (1.3)
   - **What**: Recent trial performances (last 7-21 days)
   - **Why Fixed**: CRITICAL fitness indicator (18-25% prediction power)
   - **Access**: Racing.com authenticated scraping
   - **Cost**: Included in 1.2 (same authentication)
   - **Frequency**: Once per horse (check last 3 trials)

3. **Stewards Reports** (1.4)
   - **What**: Last start incidents, gear changes, veterinary reports
   - **Why Fixed**: CRITICAL excuse identification (15-22% prediction power)
   - **Access**: Racing.com authenticated scraping
   - **Cost**: Included in 1.2 (same authentication)
   - **Frequency**: Once per horse (last start only, or last 2-3 if incidents)

**Implementation**:
```python
def fetch_fixed_official_sources(race_id):
    """
    Fetch core official racing data (checked every race)
    """
    # Authenticate once
    session_cookies = authenticate_racing_com()

    # 1. Form guide (complete race card)
    form_guide = fetch_form_guide(race_id, session_cookies)

    # 2. Barrier trials (for each horse in race)
    trials = {}
    for horse in form_guide['horses']:
        trials[horse['name']] = fetch_trials(horse['name'], session_cookies, last_n=3)

    # 3. Stewards reports (for each horse's last start)
    stewards = {}
    for horse in form_guide['horses']:
        stewards[horse['name']] = fetch_stewards_report(
            horse['last_start_venue'],
            horse['last_start_date'],
            session_cookies
        )

    return {
        'form_guide': form_guide,
        'trials': trials,
        'stewards': stewards
    }
```

**Rationale**: These three sources provide ~60% of predictive information (form guide basics + trials 18-25% + stewards 15-22%). MUST-HAVE for every race.

---

### Fixed Source Category 2: Market Data (TIER 4 - Phase 1 CRITICAL)

**Sources**:
1. **Betfair Exchange - Real-Time Odds** (4.1)
   - **What**: Current odds, market movements (last 2 hours pre-race)
   - **Why Fixed**: Market movements are CRITICAL signals (12-18% prediction power)
   - **Access**: Betfair API (free)
   - **Cost**: $0
   - **Frequency**: Continuous (every 5-15 minutes for 2 hours pre-race)

**Implementation**:
```python
def track_market_movements(market_id, duration_minutes=120):
    """
    Track market movements continuously (fixed for every race)
    """
    movements = []
    start_time = datetime.now()

    while (datetime.now() - start_time).seconds < duration_minutes * 60:
        # Fetch current odds
        market_data = betfair_api.get_market_book(market_id)

        # Store snapshot
        movements.append({
            'timestamp': datetime.now(),
            'odds': extract_odds(market_data)
        })

        # Wait 5-15 minutes
        time.sleep(300)  # 5 minutes

    # Analyze movements
    return analyze_movements(movements)
```

**Rationale**: Market movements provide CRITICAL REAL-TIME SIGNALS (steaming +12-18%, drifting -12-18%). ChatGPT cannot access (30% static only). MUST-HAVE.

---

### Fixed Source Category 3: Weather Data (TIER 6 - Phase 1-2)

**Sources**:
1. **Bureau of Meteorology API** (6.1)
   - **What**: Current weather + forecast (rain, temperature, wind)
   - **Why Fixed**: Track condition prediction depends on weather
   - **Access**: BOM API (free)
   - **Cost**: $0
   - **Frequency**: Once per race day (morning of race)

**Implementation**:
```python
def fetch_weather_data(venue, race_date):
    """
    Fetch weather data (fixed for every race)
    """
    # Get current weather observations
    current_weather = bom_api.get_current_weather(venue_station_id[venue])

    # Get race day forecast
    forecast = bom_api.get_forecast(venue_location_code[venue], race_date)

    # Predict track condition
    predicted_condition = predict_track_condition(current_weather, forecast)

    return {
        'current': current_weather,
        'forecast': forecast,
        'predicted_condition': predicted_condition
    }
```

**Rationale**: Weather determines track condition (Category 3.1). Free API, easy integration, CRITICAL for condition-dependent analysis.

---

## PART 2: INTELLIGENT DISCOVERY SOURCES (CONTEXT-DEPENDENT)

**Definition**: Sources checked based on RACE CONTEXT, horse-specific factors, or data gaps identified during analysis. Agent DECIDES what additional sources to query.

---

### Discovery Pattern 1: Expert Analysis (TIER 2 - When Available)

**Trigger Conditions**:
- High-profile race (Group 1-3, major stakes)
- Difficult pace scenario (need expert pace analysis)
- Close betting market (need expert consensus to break ties)

**Sources**:
1. **Punters.com.au Premium** (2.1)
   - **When**: Major races, expert consensus needed
   - **What**: "Horses to watch/avoid", expert ratings, pace analysis
   - **Access**: Authenticated scraping (subscription)
   - **Cost**: $0.05-$0.10/race (amortized)

2. **Speedmaps.com.au** (2.3)
   - **When**: Complex pace scenarios (many early speed horses, pace collapse risk)
   - **What**: Visual pace maps, sectional projections
   - **Access**: Authenticated scraping (subscription)
   - **Cost**: $0.08-$0.13/race (amortized)

**Implementation**:
```python
def should_fetch_expert_analysis(race):
    """
    Decide if expert analysis needed (intelligent discovery)
    """
    # Trigger 1: High-profile race
    if race['race_type'] in ['Group 1', 'Group 2', 'Group 3', 'Listed']:
        return True

    # Trigger 2: Complex pace scenario
    early_speed_count = count_early_speed_horses(race['horses'])
    if early_speed_count >= 5:  # Many early speed horses = complex pace
        return True

    # Trigger 3: Close betting market
    odds_spread = max(race['odds']) - min(race['odds'])
    if odds_spread < 3.0:  # Close market (all horses $2-5 range)
        return True

    return False

def fetch_expert_analysis(race):
    """
    Fetch expert analysis (only when triggered)
    """
    if not should_fetch_expert_analysis(race):
        return None  # Skip (save cost)

    # Fetch Punters.com.au analysis
    expert_preview = fetch_punters_preview(race['id'], session_cookies)

    # If complex pace, also fetch Speedmaps
    if count_early_speed_horses(race['horses']) >= 5:
        pace_map = fetch_speedmap(race['id'], session_cookies)
    else:
        pace_map = None

    return {
        'expert_preview': expert_preview,
        'pace_map': pace_map
    }
```

**Rationale**: Expert analysis costs $0.05-$0.20/race. Only valuable for complex races (major stakes, complex pace). Save cost by skipping routine races.

---

### Discovery Pattern 2: Supplementary Media (TIER 3 - When Gaps Identified)

**Trigger Conditions**:
- Health uncertainty (no trial since long break, post-race distress last start)
- Gear change (need explanation for why gear changed)
- Jockey switch (need explanation for why jockey changed)
- Stable confidence unclear (major trainer but no clear signals)

**Sources**:
1. **Racing.com News** (3.1)
   - **When**: Health uncertainty, gear changes, stable confidence unclear
   - **What**: Injury updates, gear change explanations, trainer quotes
   - **Access**: Standard HTTP scraping (free)
   - **Cost**: $0

2. **Broadcaster Previews** (3.3)
   - **When**: Close race, need additional expert consensus
   - **What**: Expert selections, betting analysis
   - **Access**: Standard HTTP scraping (free)
   - **Cost**: $0

**Implementation**:
```python
def should_fetch_media_sources(horse):
    """
    Decide if media sources needed for specific horse
    """
    # Trigger 1: Health uncertainty
    if horse['last_trial_days_ago'] > 30:  # No trial in last 30 days
        return True, 'health_update'

    # Trigger 2: Gear change
    if horse['gear_change'] != 'None':
        return True, 'gear_explanation'

    # Trigger 3: Jockey switch (elite → moderate or vice versa)
    if horse['jockey_changed'] and abs(horse['jockey_quality_delta']) > 10:
        return True, 'jockey_switch_reason'

    return False, None

def fetch_media_sources(horse, reason):
    """
    Fetch media sources (only when triggered for specific horse)
    """
    query_keywords = {
        'health_update': f"{horse['name']} injury OR fitness OR health",
        'gear_explanation': f"{horse['name']} blinkers OR gear change",
        'jockey_switch_reason': f"{horse['name']} jockey OR rider change"
    }

    # Search Racing.com news
    news_articles = search_racing_com_news(query_keywords[reason])

    # Extract relevant information
    insights = extract_insights(news_articles, reason)

    return insights
```

**Rationale**: Media sources provide supplementary insights (injury updates, gear explanations). Only query when GAPS identified (avoid unnecessary searches).

---

### Discovery Pattern 3: Social Media (TIER 7 - When High-Value Signals Expected)

**Trigger Conditions**:
- Major stable (Chris Waller, Gai Waterhouse, Godolphin) + major race
- Early jockey booking detected (elite jockey committed weeks in advance)
- Mysterious market movement (strong steaming with no obvious reason)

**Sources**:
1. **Official Trainer Social Media** (7.3)
   - **When**: Major stable + major race, early booking announced
   - **What**: Stable confidence quotes, health updates, booking announcements
   - **Access**: Twitter API (if implementing)
   - **Cost**: Included in Twitter API (if implemented)

**Implementation**:
```python
def should_fetch_social_media(race, horse):
    """
    Decide if social media monitoring needed (intelligent discovery)
    """
    # Trigger 1: Major stable + major race
    if horse['trainer'] in MAJOR_TRAINERS and race['race_type'] in ['Group 1', 'Group 2']:
        return True

    # Trigger 2: Elite jockey booking (may have been announced on social media)
    if horse['jockey'] in ELITE_JOCKEYS:
        return True

    # Trigger 3: Mysterious market movement
    if horse['market_movement'] < -20 and horse['reason_unclear']:  # Strong steam, no obvious reason
        return True

    return False

def fetch_social_media(horse):
    """
    Fetch social media insights (only when triggered)
    """
    if not should_fetch_social_media(race, horse):
        return None  # Skip (save API calls)

    # Search trainer's recent tweets
    trainer_handle = get_trainer_twitter_handle(horse['trainer'])
    tweets = twitter_api.search_tweets(f"from:{trainer_handle} {horse['name']}", count=20)

    # Filter for confidence signals
    confidence_signals = detect_confidence_signals(tweets)

    return confidence_signals
```

**Rationale**: Social media monitoring is EXPENSIVE ($100-500/month API) and HIGH NOISE (90%+). Only query for high-value scenarios (major stables, major races, elite bookings).

---

## PART 3: QUALITY VERIFICATION FRAMEWORK

**Purpose**: Ensure data quality, detect contradictions, validate timestamps, assess source reliability.

---

### Verification Pattern 1: Cross-Reference Validation

**Method**: Compare information across multiple sources, flag contradictions.

**Implementation**:
```python
def cross_reference_validation(data_sources):
    """
    Cross-reference data across sources, detect contradictions
    """
    contradictions = []

    # Example 1: Barrier number cross-reference
    barriers = {
        'form_guide': data_sources['form_guide']['horse_x']['barrier'],
        'betfair': data_sources['betfair']['horse_x']['barrier']
    }

    if len(set(barriers.values())) > 1:  # Different barriers reported
        contradictions.append({
            'type': 'barrier_mismatch',
            'sources': barriers,
            'resolution': 'Use Racing.com (Tier 1, most authoritative)'
        })

    # Example 2: Jockey cross-reference
    jockeys = {
        'form_guide': data_sources['form_guide']['horse_x']['jockey'],
        'media': data_sources['media']['horse_x']['jockey']
    }

    if len(set(jockeys.values())) > 1:  # Different jockeys reported
        # Check for late jockey change
        contradictions.append({
            'type': 'jockey_change',
            'sources': jockeys,
            'resolution': 'Check stewards reports for late change (11.3)'
        })

    # Example 3: Gear change cross-reference
    gear = {
        'form_guide': data_sources['form_guide']['horse_x']['gear'],
        'stewards': data_sources['stewards']['horse_x']['gear']
    }

    if gear['form_guide'] != gear['stewards']:
        contradictions.append({
            'type': 'gear_mismatch',
            'sources': gear,
            'resolution': 'Use stewards report (Tier 1, official notification)'
        })

    return contradictions
```

**Rationale**: Contradictions indicate late changes (jockey switches), data errors, or outdated information. Cross-reference validation catches these issues.

---

### Verification Pattern 2: Timestamp Validation

**Method**: Verify data recency, flag stale data, prioritize recent sources.

**Implementation**:
```python
def timestamp_validation(data_sources):
    """
    Validate data timestamps, flag stale data
    """
    warnings = []

    # Example 1: Trial recency
    trial_date = data_sources['trials']['horse_x']['last_trial_date']
    days_ago = (datetime.now() - trial_date).days

    if days_ago > 21:  # Trial older than 3 weeks
        warnings.append({
            'type': 'stale_trial',
            'horse': 'horse_x',
            'days_ago': days_ago,
            'impact': 'Reduce trial confidence (trial data dated)'
        })

    # Example 2: Odds staleness (market movements)
    odds_timestamp = data_sources['betfair']['timestamp']
    minutes_ago = (datetime.now() - odds_timestamp).seconds / 60

    if minutes_ago > 30:  # Odds older than 30 minutes
        warnings.append({
            'type': 'stale_odds',
            'minutes_ago': minutes_ago,
            'impact': 'Re-fetch odds (market may have moved)'
        })

    # Example 3: Weather forecast recency
    forecast_timestamp = data_sources['weather']['forecast_timestamp']
    hours_ago = (datetime.now() - forecast_timestamp).seconds / 3600

    if hours_ago > 12:  # Forecast older than 12 hours
        warnings.append({
            'type': 'stale_forecast',
            'hours_ago': hours_ago,
            'impact': 'Re-fetch forecast (weather may have changed)'
        })

    return warnings
```

**Rationale**: Stale data reduces prediction accuracy. Trials older than 3 weeks less predictive. Odds must be recent (market moves quickly). Forecasts change (re-fetch if >12h old).

---

### Verification Pattern 3: Source Reliability Scoring

**Method**: Assign reliability scores to sources, weight information accordingly.

**Implementation**:
```python
# Source reliability scores (1-10)
SOURCE_RELIABILITY = {
    # Tier 1: Official sources (highest reliability)
    'racing_com_form_guide': 10,
    'racing_com_trials': 10,
    'racing_com_stewards': 10,

    # Tier 2: Expert paywalled (high reliability)
    'punters_com_au': 9,
    'timeform': 8,
    'speedmaps': 9,

    # Tier 3: Mainstream media (moderate reliability)
    'racing_com_news': 8,
    'broadcaster_previews': 7,
    'newspapers': 7,

    # Tier 4: Market sources (high reliability for odds, moderate for sentiment)
    'betfair_odds': 9,
    'bookmaker_promotions': 6,

    # Tier 6: Weather (high reliability)
    'bom_weather': 10,
    'venue_weather': 9,

    # Tier 7: Social media (low reliability, high noise)
    'twitter_verified_trainer': 7,
    'twitter_unverified_insider': 4,
    'twitter_public': 2,
    'forums': 3
}

def weight_information_by_reliability(conflicting_sources):
    """
    When sources conflict, weight by reliability score
    """
    weighted_scores = {}

    for source, value in conflicting_sources.items():
        reliability = SOURCE_RELIABILITY[source]

        if value not in weighted_scores:
            weighted_scores[value] = 0
        weighted_scores[value] += reliability

    # Choose value with highest weighted score
    best_value = max(weighted_scores, key=weighted_scores.get)

    return best_value
```

**Rationale**: Not all sources equally reliable. Tier 1 (official) > Tier 2 (expert) > Tier 3 (media) > Tier 7 (social). Weight conflicting information accordingly.

---

## PART 4: COST OPTIMIZATION STRATEGY

**Purpose**: Minimize costs while maximizing prediction accuracy. Prioritize free/low-cost sources, expensive sources only when necessary.

---

### Cost Optimization Pattern 1: Tiered Source Querying

**Strategy**: Query free sources first (Tier 1, 4, 6), expensive sources only if gaps remain.

**Implementation**:
```python
def optimized_data_collection(race):
    """
    Cost-optimized data collection strategy
    """
    # PHASE 1: Free sources (always query)
    data = {}

    # Tier 1: Official sources (free after authentication)
    data['official'] = fetch_fixed_official_sources(race['id'])  # $0.02-$0.10

    # Tier 4: Market data (free)
    data['market'] = track_market_movements(race['betfair_market_id'])  # $0

    # Tier 6: Weather (free)
    data['weather'] = fetch_weather_data(race['venue'], race['date'])  # $0

    # PHASE 2: Assess if expert sources needed (cost-benefit)
    if should_fetch_expert_analysis(race):
        data['expert'] = fetch_expert_analysis(race)  # $0.05-$0.20
    else:
        data['expert'] = None  # Save $0.05-$0.20 per race

    # PHASE 3: Assess if media sources needed (free, but time cost)
    media_needed = []
    for horse in race['horses']:
        if should_fetch_media_sources(horse)[0]:
            media_needed.append(horse)

    if media_needed:
        data['media'] = {horse['name']: fetch_media_sources(horse, reason)
                         for horse in media_needed}  # $0 (free)
    else:
        data['media'] = None  # Save API calls

    # PHASE 4: Assess if social media needed (expensive, rarely needed)
    if TWITTER_API_ENABLED:  # Only if Twitter API implemented
        social_needed = [horse for horse in race['horses']
                        if should_fetch_social_media(race, horse)]

        if social_needed:
            data['social'] = {horse['name']: fetch_social_media(horse)
                             for horse in social_needed}  # API calls
        else:
            data['social'] = None  # Save API calls
    else:
        data['social'] = None  # Skip (Twitter API not implemented)

    return data
```

**Cost Breakdown**:
- Phase 1 (Free sources): $0.02-$0.10 per race (fixed cost, always query)
- Phase 2 (Expert sources): $0.05-$0.20 per race (conditional, ~30-50% of races)
- Phase 3 (Media sources): $0 (free, conditional, ~20-40% of horses)
- Phase 4 (Social media): $0.25-$1.25 per race if implemented (rare, ~5-10% of races)

**Total Typical Cost**: $0.07-$0.30 per race (Phase 1 + selective Phase 2)

---

### Cost Optimization Pattern 2: Batch Processing

**Strategy**: Process multiple races together, share authentication/API calls.

**Implementation**:
```python
def batch_data_collection(race_card):
    """
    Process full race card together (share authentication)
    """
    # Authenticate once for all races
    session_cookies = authenticate_racing_com()  # One authentication for 8-12 races

    # Fetch all races on card
    race_data = {}
    for race in race_card:
        # Use same session cookies
        race_data[race['id']] = {
            'form_guide': fetch_form_guide(race['id'], session_cookies),
            'trials': fetch_trials_batch([horse['name'] for horse in race['horses']],
                                         session_cookies),
            'stewards': fetch_stewards_batch(race['horses'], session_cookies)
        }

    # Amortize authentication cost across all races
    # $0.10 authentication / 10 races = $0.01 per race

    return race_data
```

**Rationale**: Authenticate once, process multiple races. Reduces per-race cost ($0.10 → $0.01 per race when processing 10 races).

---

### Cost Optimization Pattern 3: Caching & Reuse

**Strategy**: Cache data that doesn't change, avoid redundant queries.

**Implementation**:
```python
# Cache layer
CACHE = {
    'trainer_statistics': {},  # Trainer stats don't change intraday
    'jockey_statistics': {},   # Jockey stats don't change intraday
    'historical_results': {},  # Historical results don't change
    'venue_characteristics': {} # Venue characteristics don't change
}

def fetch_trainer_statistics(trainer_name):
    """
    Fetch trainer stats with caching
    """
    if trainer_name in CACHE['trainer_statistics']:
        # Use cached data (avoid redundant query)
        return CACHE['trainer_statistics'][trainer_name]

    # Fetch if not cached
    stats = fetch_trainer_stats_from_source(trainer_name)

    # Cache for future use
    CACHE['trainer_statistics'][trainer_name] = stats

    return stats
```

**Rationale**: Trainer/jockey statistics don't change intraday. Cache once, reuse across multiple races. Reduces API calls by ~60-70%.

---

## PART 5: PHASE-BASED IMPLEMENTATION ROADMAP

**Purpose**: Prioritize implementation by phase, maximize ROI at each stage.

---

### PHASE 1: CORE FOUNDATION (Weeks 1-4)

**Objective**: Solve ChatGPT's biggest blind spots, establish foundation data access.

**Implementation**:
1. **Racing.com Authentication** (1.1) - CRITICAL
   - Selenium + session cookies
   - Unlocks: Form guide (1.2), Trials (1.3), Stewards (1.4), Replays metadata (1.5)
   - **Impact**: +33-47% prediction power (three entire categories unlocked)
   - **Cost**: $0-40/month + $0.02-$0.10/race

2. **Betfair API Integration** (4.1) - CRITICAL
   - Real-time market movement tracking
   - **Impact**: +8-15% prediction power (ChatGPT 30% → Us 95%)
   - **Cost**: $0 (free API)

3. **BOM Weather API** (6.1) - ESSENTIAL
   - Track condition prediction
   - **Impact**: Category 3.1 depends on weather
   - **Cost**: $0 (free API)

**Phase 1 Deliverables**:
- Authenticated access to all Racing.com sources (form guide, trials, stewards, replays)
- Real-time market movement tracking (Betfair API)
- Weather integration (BOM API)
- Basic data collection pipeline (fixed sources only)

**Phase 1 Cost**: $0.02-$0.10 per race (Racing.com authentication only, other sources free)

**Phase 1 ROI**: HIGHEST (unlock +33-47% prediction power for $0.02-$0.10/race)

---

### PHASE 2: EXPERT INTEGRATION (Weeks 5-8)

**Objective**: Add expert analysis, supplementary media, enhance prediction accuracy.

**Implementation**:
1. **Punters.com.au Subscription** (2.1) - HIGH VALUE
   - Premium expert analysis, "horses to watch/avoid"
   - **Impact**: +8-15% prediction power
   - **Cost**: $20-40/month + $0.05-$0.10/race

2. **Racing.com News Extraction** (3.1) - SUPPLEMENTARY
   - Injury updates, gear explanations, stable quotes
   - **Impact**: +3-8% incremental
   - **Cost**: $0 (free)

3. **Broadcaster Previews** (3.3) - EXPERT CONSENSUS
   - Sky Racing, Tab.com.au previews
   - **Impact**: +2-5% incremental (consensus contribution)
   - **Cost**: $0 (free)

4. **Intelligent Discovery Logic** - COST OPTIMIZATION
   - Implement "should_fetch_expert_analysis()" logic
   - Only query expensive sources when needed
   - **Impact**: Reduce costs by 30-50% (skip routine races)

**Phase 2 Deliverables**:
- Punters.com.au integration (authenticated scraping)
- Media source extraction (Racing.com news, broadcaster previews)
- Intelligent discovery framework (context-aware source selection)
- Quality verification (cross-reference validation, timestamp checks)

**Phase 2 Cost**: $0.10-$0.30 per race (includes Phase 1 + selective expert sources)

**Phase 2 ROI**: HIGH (add +13-28% incremental prediction power for $0.08-$0.20 additional)

---

### PHASE 3: ENHANCEMENTS (Weeks 9-12)

**Objective**: Add advanced features, social media monitoring (optional), historical analysis.

**Implementation**:
1. **Speedmaps Subscription** (2.3) - PACE ANALYSIS (Optional)
   - Visual pace maps for complex pace scenarios
   - **Impact**: +5-12% incremental (when complex pace)
   - **Cost**: $30-50/month + $0.08-$0.13/race
   - **Alternative**: Build own pace model (save subscription)

2. **Race Replay Written Analysis** (1.5) - VISUAL INSIGHTS
   - Extract Racing.com written replay summaries
   - **Impact**: +5-10% incremental (supplement stewards reports)
   - **Cost**: $0.05-$0.10/race (GPT-5 analysis)

3. **Venue Weather Stations** (6.2) - ACCURACY (Optional)
   - On-site weather measurements (when available)
   - **Impact**: +2-5% incremental accuracy
   - **Cost**: $0 (free from venue websites)

4. **Official Trainer Social Media** (7.3) - CONFIDENCE SIGNALS (Optional, if implementing social media)
   - Monitor verified trainer accounts
   - **Impact**: +3-8% incremental (health updates, confidence signals)
   - **Cost**: Included in Twitter API (if implementing)

5. **Twitter Insider Monitoring** (7.1) - HIGH NOISE (Optional, low priority)
   - Real-time Twitter monitoring + credibility filtering
   - **Impact**: +5-12% when genuine insider detected (but rare, 90%+ noise)
   - **Cost**: $100-500/month + $0.25-$1.25/race
   - **Recommendation**: SKIP unless budget allows (low ROI)

**Phase 3 Deliverables**:
- Pace analysis enhancement (Speedmaps or own model)
- Replay written analysis extraction
- Venue weather integration
- Social media monitoring (optional, only if budget allows)
- Historical pattern analysis (seasonal patterns, market accuracy)

**Phase 3 Cost**:
- Without social media: $0.15-$0.50 per race
- With social media: $0.40-$1.75 per race (includes Twitter API)

**Phase 3 ROI**: MODERATE (incremental improvements, some high-cost low-ROI options)

---

## PART 6: INTEGRATION ARCHITECTURE

**Purpose**: How all sources integrate into unified prediction system.

---

### Integration Pattern 1: Data Flow Architecture

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │  Tier 1       │  │  Tier 4       │  │  Tier 6       │  │
│  │  Official     │  │  Market       │  │  Weather      │  │
│  │  (Racing.com) │  │  (Betfair)    │  │  (BOM)        │  │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘  │
│          │                  │                  │            │
│          └──────────┬───────┴──────────┬───────┘            │
│                     │                  │                    │
│              ┌──────▼──────────────────▼──────┐             │
│              │   UNIFIED DATA LAYER            │             │
│              │   (Normalized, Validated)       │             │
│              └──────┬──────────────────────────┘             │
└─────────────────────┼────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────┐
│                  INTELLIGENT DISCOVERY LAYER                  │
├───────────────────────────────────────────────────────────────┤
│  IF gaps detected OR complex race OR high-value scenario:    │
│    ┌───────────────┐  ┌───────────────┐  ┌───────────────┐ │
│    │  Tier 2       │  │  Tier 3       │  │  Tier 7       │ │
│    │  Expert       │  │  Media        │  │  Social       │ │
│    │  (Conditional)│  │  (Conditional)│  │  (Rare)       │ │
│    └───────┬───────┘  └───────┬───────┘  └───────┬───────┘ │
│            │                  │                  │           │
│            └──────────┬───────┴──────────┬───────┘           │
│                       │                  │                   │
│                ┌──────▼──────────────────▼──────┐            │
│                │  SUPPLEMENTARY DATA LAYER       │            │
│                │  (Context-Dependent)            │            │
│                └──────┬──────────────────────────┘            │
└───────────────────────┼───────────────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────────────┐
│                  QUALITY VERIFICATION LAYER                    │
├────────────────────────────────────────────────────────────────┤
│  - Cross-reference validation (detect contradictions)          │
│  - Timestamp validation (flag stale data)                      │
│  - Reliability weighting (Tier 1 > Tier 2 > ... > Tier 7)    │
│  - Conflict resolution (choose most reliable source)           │
└───────────────────────┬────────────────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────────────┐
│                  SYNTHESIS & REASONING LAYER                   │
├────────────────────────────────────────────────────────────────┤
│  - GPT-5 Analysis (reason over all collected data)             │
│  - Category-by-category prediction adjustment                  │
│  - Multiplicative impact calculation                           │
│  - Confidence scoring                                          │
└───────────────────────┬────────────────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────────────┐
│                     PREDICTION OUTPUT                          │
├────────────────────────────────────────────────────────────────┤
│  - Win probability per horse                                   │
│  - Confidence score (0-100%)                                   │
│  - Key factors (top 3-5 prediction drivers)                   │
│  - Completeness score (% of taxonomy covered)                  │
└────────────────────────────────────────────────────────────────┘
```

---

### Integration Pattern 2: Cross-Horse Analysis

**Strategy**: Analyze horses RELATIVE to each other (not in isolation).

**Implementation**:
```python
def cross_horse_analysis(race_data):
    """
    Analyze horses relative to each other
    """
    horses = race_data['horses']

    # Example 1: Pace scenario (relative early speed)
    early_speed_horses = [h for h in horses if h['running_style'] == 'Leader/On-Pace']

    if len(early_speed_horses) >= 5:  # Many early speed horses
        # Pace collapse scenario (too many wanting to lead)
        for horse in early_speed_horses:
            horse['adjustments']['pace_collapse_risk'] = -10-15%  # Penalty for leaders

        # Closers benefit
        closers = [h for h in horses if h['running_style'] == 'Off-Pace/Closer']
        for horse in closers:
            horse['adjustments']['pace_collapse_benefit'] = +10-15%  # Boost for closers

    # Example 2: Class comparison (relative class advantage)
    avg_rating = sum([h['rating'] for h in horses]) / len(horses)

    for horse in horses:
        class_diff = horse['rating'] - avg_rating

        if class_diff > 10:  # 10+ points above average
            horse['adjustments']['class_advantage'] = +8-12%  # Class boost
        elif class_diff < -10:  # 10+ points below average
            horse['adjustments']['class_disadvantage'] = -8-12%  # Class penalty

    # Example 3: Barrier position (relative draw advantage)
    inside_barrier_bias = race_data['track_bias']['inside_barrier_advantage']

    for horse in horses:
        if inside_barrier_bias and horse['barrier'] <= 5:
            horse['adjustments']['inside_draw_advantage'] = +8-15%  # Inside draw boost
        elif inside_barrier_bias and horse['barrier'] >= 10:
            horse['adjustments']['wide_draw_disadvantage'] = -10-18%  # Wide draw penalty

    return horses
```

**Rationale**: Horses compete against EACH OTHER. Pace scenario depends on ALL horses (not just one). Class advantage is RELATIVE. Barrier bias affects all horses differently.

---

## SUMMARY: SEARCH STRATEGY IMPLEMENTATION

### Fixed Sources (Every Race):
1. Racing.com form guide, trials, stewards (Tier 1) - $0.02-$0.10
2. Betfair real-time odds (Tier 4) - $0
3. BOM weather (Tier 6) - $0

**Total Fixed Cost**: $0.02-$0.10 per race

### Intelligent Discovery (Context-Dependent):
1. Expert analysis (Tier 2) - $0.05-$0.20 when complex race (~30-50% of races)
2. Media sources (Tier 3) - $0 when gaps identified (~20-40% of horses)
3. Social media (Tier 7) - $0.25-$1.25 when high-value scenario (~5-10% of races, optional)

**Total Discovery Cost**: $0-$0.30 per race typically ($0.25-$1.55 if implementing social media)

### Quality Verification:
1. Cross-reference validation (detect contradictions)
2. Timestamp validation (flag stale data)
3. Reliability weighting (Tier 1 > 2 > 3 > 7)

### Phase-Based Implementation:
- **Phase 1** (Weeks 1-4): Core foundation (official + market + weather) - $0.02-$0.10/race
- **Phase 2** (Weeks 5-8): Expert integration (selective) - $0.10-$0.30/race
- **Phase 3** (Weeks 9-12): Enhancements (optional social media) - $0.15-$1.75/race

**Recommended**: Phase 1 + Phase 2 (no social media) = $0.10-$0.30 per race with excellent coverage

---

**Part 5d Complete (Search Strategy & Implementation Framework). Source hierarchy analysis COMPLETE (Parts 5a-5d). Ready for Part 6 (Integration Strategy & Implementation Priorities).**
