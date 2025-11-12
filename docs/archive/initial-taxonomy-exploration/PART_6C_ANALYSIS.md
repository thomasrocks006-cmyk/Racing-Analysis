# Critical Analysis Part 6c: Phase 3 Enhancements, Testing Protocol & Success Metrics

**Covers**: Phase 3 optional enhancements, social media analysis, testing methodology, success metrics, continuous improvement

**Analysis Framework**: Advanced features, testing protocol, competitive benchmarking, accuracy measurement

---

## PART 1: PHASE 3 - ENHANCEMENTS (WEEKS 9-12)

**Primary Goal**: Add optional advanced features, diminishing returns but potential edge

**Critical Components**:
1. Social Media Monitoring (Twitter/X - OPTIONAL, expensive, marginal ROI)
2. Speedmaps Visual Pace Maps (if not added in Phase 2)
3. Selective Human Replay Observation (key races only)
4. Advanced Historical Pattern Recognition

**Expected Outcomes**:
- **Completeness**: 95%+ (vs Phase 2 90-95%)
- **Cost**: $0.15-$1.75 per race (varies significantly based on social media inclusion)
- **Prediction Power**: +5-15% incremental (diminishing returns)
- **Competitive Advantage**: Marginal (most gains achieved in Phase 1-2)

**IMPORTANT RECOMMENDATION**: Phase 3 is OPTIONAL. Phase 1+2 provides 90-95% completeness at $0.10-$0.30/race with excellent ROI. Phase 3 costs increase significantly ($0.15-$1.75/race if including social media) for marginal gains (+5-15% incremental).

---

### Phase 3 Priority 1: Social Media Monitoring (OPTIONAL - LOW ROI)

**Why Included (Despite Low ROI)**:
- Potential for rare insider signals (+8-18% boost when genuine)
- Completeness: ChatGPT 60% → Us 80%
- BUT: 90%+ noise, expensive ($100-500/month), LOW ROI

**Cost-Benefit Analysis**:
```
Twitter API Costs:
- Basic tier: $100/month (limited volume)
- Pro tier: $500/month (higher volume, better for systematic monitoring)

Expected Value:
- ~5-10% of races have genuine insider signals
- Detection accuracy ~30-40% (high false positive rate)
- Genuine signal boost: +8-18% prediction power

ROI Calculation:
- Cost: $100-500/month = $0.25-$1.25 per race (if analyzing 400 races/month)
- Benefit: 5-10% races × 30-40% accuracy × +13% average boost = +0.2-0.5% overall
- Conclusion: MARGINAL ROI (consider only if budget allows Phase 3 experimentation)
```

**Recommendation**: **SKIP social media unless**:
1. Budget allows experimentation ($100-500/month discretionary spend)
2. Focus on high-value races only (Group 1-2, major stakes)
3. Accept 90%+ noise and low ROI for potential rare edge cases

**Implementation** (IF included):
```python
# Week 9: Twitter API Setup (OPTIONAL)
def setup_twitter_monitoring():
    """
    Twitter API v2 setup (requires paid tier $100-500/month)
    """
    import tweepy

    # Authenticate
    client = tweepy.Client(
        bearer_token=os.environ['TWITTER_BEARER_TOKEN'],
        consumer_key=os.environ['TWITTER_API_KEY'],
        consumer_secret=os.environ['TWITTER_API_SECRET'],
        access_token=os.environ['TWITTER_ACCESS_TOKEN'],
        access_token_secret=os.environ['TWITTER_ACCESS_SECRET']
    )

    return client

def monitor_racing_twitter(client, race_keywords, hours_before_race=24):
    """
    Monitor Twitter for racing signals (24h pre-race window)
    """
    # Build search query
    query = ' OR '.join(race_keywords)  # e.g., "Secret Ambition", "Randwick Race 7"
    query += ' -is:retweet'  # Exclude retweets (reduce noise)

    # Time window
    start_time = datetime.now() - timedelta(hours=hours_before_race)

    # Search tweets
    tweets = client.search_recent_tweets(
        query=query,
        start_time=start_time.isoformat() + 'Z',
        max_results=100,
        tweet_fields=['created_at', 'author_id', 'public_metrics', 'entities']
    )

    return tweets.data if tweets.data else []

def filter_credible_racing_tweets(tweets):
    """
    Filter 90%+ noise down to credible signals

    Credibility Tiers:
    - Tier 1: Verified insiders (trainers, jockeys, racing journalists)
    - Tier 2: Unverified insiders (specific trackwork details, industry terminology)
    - Tier 3: Public speculation (opinions, tips, no specific details) - IGNORE
    """
    credible_signals = {
        'tier_1': [],  # Verified insiders (highest credibility)
        'tier_2': [],  # Unverified insiders (moderate credibility)
        'tier_3': []   # Public speculation (ignore)
    }

    # Verified insider account IDs (manually curated list)
    verified_insiders = {
        'trainers': [],      # Populate with known trainer Twitter IDs
        'jockeys': [],       # Populate with known jockey Twitter IDs
        'journalists': []    # Populate with racing journalist Twitter IDs
    }

    for tweet in tweets:
        # Tier 1: Verified insiders
        if tweet.author_id in verified_insiders['trainers'] or \
           tweet.author_id in verified_insiders['jockeys'] or \
           tweet.author_id in verified_insiders['journalists']:
            credible_signals['tier_1'].append({
                'text': tweet.text,
                'author_id': tweet.author_id,
                'created_at': tweet.created_at,
                'credibility': 85%,
                'reasoning': 'Verified insider account'
            })
            continue

        # Tier 2: Unverified insiders (check for insider keywords)
        insider_keywords = [
            'trackwork', 'galloped', 'trialed', 'stable', 'worked',
            'barrier practice', 'jumped out', 'breezed', 'clocked'
        ]

        text_lower = tweet.text.lower()

        # Check for specific details (indicators of insider knowledge)
        has_insider_keywords = any(kw in text_lower for kw in insider_keywords)
        is_detailed = len(tweet.text) > 100  # Detailed tweets more likely genuine

        if has_insider_keywords and is_detailed:
            credible_signals['tier_2'].append({
                'text': tweet.text,
                'author_id': tweet.author_id,
                'created_at': tweet.created_at,
                'credibility': 50%,
                'reasoning': 'Unverified but contains insider keywords and detail'
            })
            continue

        # Tier 3: Public speculation (IGNORE)
        credible_signals['tier_3'].append({
            'text': tweet.text,
            'reason_ignored': 'Public speculation, no specific details'
        })

    # Filter out Tier 3 (public speculation)
    return {
        'tier_1': credible_signals['tier_1'],  # 5-10% of tweets (genuine insiders)
        'tier_2': credible_signals['tier_2'],  # 10-15% of tweets (possible insiders)
        'total_analyzed': len(tweets),
        'noise_filtered': len(credible_signals['tier_3']),  # ~80-90% noise
        'signal_rate': (len(credible_signals['tier_1']) + len(credible_signals['tier_2'])) / len(tweets) * 100
    }

def analyze_social_media_signals(credible_signals, horse_name):
    """
    Analyze social media signals for prediction impact
    """
    impact = 0
    confidence = 50%
    reasons = []

    # Tier 1 signals (verified insiders)
    tier_1_mentions = [s for s in credible_signals['tier_1'] if horse_name.lower() in s['text'].lower()]

    for signal in tier_1_mentions:
        text = signal['text'].lower()

        # Positive signals
        if any(word in text for word in ['impressive', 'strong', 'looks great', 'going well']):
            impact += 12-18%
            confidence = max(confidence, 80%)
            reasons.append(f"Verified insider positive: {signal['text'][:50]}...")

        # Negative signals
        elif any(word in text for word in ['struggling', 'off', 'not right', 'scratched']):
            impact -= 12-18%
            confidence = max(confidence, 80%)
            reasons.append(f"Verified insider negative: {signal['text'][:50]}...")

    # Tier 2 signals (unverified insiders)
    tier_2_mentions = [s for s in credible_signals['tier_2'] if horse_name.lower() in s['text'].lower()]

    for signal in tier_2_mentions:
        text = signal['text'].lower()

        # Positive signals (lower confidence than Tier 1)
        if any(word in text for word in ['galloped well', 'trialed impressive', 'worked strong']):
            impact += 5-10%
            confidence = max(confidence, 60%)
            reasons.append(f"Unverified insider positive: {signal['text'][:50]}...")

        # Negative signals
        elif any(word in text for word in ['poor work', 'off color', 'issues']):
            impact -= 5-10%
            confidence = max(confidence, 60%)
            reasons.append(f"Unverified insider negative: {signal['text'][:50]}...")

    return {
        'impact': impact,
        'confidence': confidence,
        'reasons': reasons,
        'tier_1_signals': len(tier_1_mentions),
        'tier_2_signals': len(tier_2_mentions)
    }
```

**Phase 3 Social Media Coverage** (IF included):
```
✅ Category 7.3: Stable Social Media (80% monitoring official accounts) ⭐ CHATGPT 60%
✅ Category 13.4: Social Media Tips (70% credibility filtering)
✅ Intangibles 16.5: Pre-Race Behavior (60% via social media reports, not direct observation)

Social Media Completeness: 70-80% (vs ChatGPT 60%)
Cost: $100-500/month = $0.25-$1.25/race (EXPENSIVE for marginal gains)
```

**FINAL RECOMMENDATION ON SOCIAL MEDIA**:
❌ **SKIP** - Not worth cost ($0.25-$1.25/race) for marginal ROI (+0.2-0.5% overall). Focus budget on Phase 1-2 priorities (authentication $0.02-$0.10, expert analysis $0.05-$0.20).

---

### Phase 3 Priority 2: Speedmaps Visual Pace Maps (If Not in Phase 2)

**Why Include**:
- Speedmaps provides 90% pace completeness (vs custom model 85%)
- Incremental gain: +5% pace completeness
- Cost: $30-50/month = $0.03-$0.05 per race
- ROI: BETTER than social media (lower cost, higher reliability)

**Implementation**:
```python
# Week 10: Speedmaps Integration (if not done in Phase 2)
def setup_speedmaps_subscription():
    """
    Subscribe to Speedmaps ($30-50/month)
    Similar authentication approach to Punters.com.au
    """
    # Selenium login + cookie extraction
    # (Implementation similar to Phase 1 Racing.com auth)
    pass

def extract_speedmaps_pace_scenario(race_url, session):
    """
    Extract visual pace map from Speedmaps
    """
    response = session.get(race_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Parse Speedmaps visual layout
    pace_map = {
        'early_leaders': [],     # Horses leading in first 400m
        'on_pace': [],           # Horses tracking leaders
        'midfield': [],          # Horses settling midfield
        'back_markers': []       # Horses settling last
    }

    # Extract horse positions from Speedmaps graphic
    # (Speedmaps uses visual representation - scrape HTML positions)

    pace_positions = soup.find_all('div', class_='pace-position')

    for position in pace_positions:
        horse_name = position.find('span', class_='horse').text
        position_category = position['data-category']  # 'leader', 'on_pace', etc.

        pace_map[position_category].append(horse_name)

    return pace_map

def analyze_speedmaps_pace_scenario(pace_map):
    """
    Analyze pace scenario from Speedmaps data
    """
    leader_count = len(pace_map['early_leaders'])

    # Same analysis as custom model, but with higher confidence (visual map more reliable)
    if leader_count >= 5:
        return {
            'scenario': 'PACE COLLAPSE',
            'leader_impact': -12-18%,
            'closer_impact': +12-18%,
            'confidence': 85%,  # Higher confidence with Speedmaps (vs 80% custom)
            'reason': f'{leader_count} leaders (Speedmaps visual pace map)'
        }
    elif leader_count == 1:
        return {
            'scenario': 'UNCONTESTED LEAD',
            'leader_impact': +15-20%,
            'closer_impact': -10-15%,
            'confidence': 85%,
            'reason': 'Single leader (Speedmaps confirms uncontested)'
        }
    else:
        return {
            'scenario': 'MODERATE PACE',
            'leader_impact': 0%,
            'closer_impact': 0%,
            'confidence': 70%,
            'reason': f'{leader_count} leaders (moderate pace, Speedmaps)'
        }
```

**Speedmaps ROI**:
- Cost: $30-50/month = $0.03-$0.05/race
- Benefit: +5% pace completeness (85% → 90%), +2-5% confidence boost
- Conclusion: WORTHWHILE if budget allows (better ROI than social media)

**Recommendation**: ✅ **ADD Speedmaps** in Phase 2 or 3 (good ROI, low cost, higher reliability than social media).

---

### Phase 3 Priority 3: Selective Human Replay Observation (Key Races Only)

**Why Include**:
- Written replay analysis achieves 70% replay completeness (Phase 2)
- Human observation (watch video) achieves 90%+ replay completeness
- BUT: Time-intensive (10-15 min per race to watch replays)
- **Strategy**: Selective observation for key races only (Group 1-2, close betting markets)

**Implementation**:
```python
# Week 11: Selective Human Replay Observation Protocol
def should_watch_replay_manually(race, horse):
    """
    Decide if human replay observation is worthwhile

    Criteria:
    1. High-value race (Group 1-2, major stakes)
    2. Close betting market (horse odds $3-8 range, competitive)
    3. Conflicting signals (stewards vs written analysis disagree)
    4. Recent poor performance with no clear excuse identified
    """
    # Criterion 1: High-value race
    if race['race_type'] in ['Group 1', 'Group 2']:
        return True, 'Group 1-2 race (high stakes, worth detailed analysis)'

    # Criterion 2: Close betting market
    if 3.0 <= horse['current_odds'] <= 8.0:
        # Competitive odds range (potential value bet)
        return True, 'Competitive odds range ($3-$8, potential value)'

    # Criterion 3: Conflicting signals
    if horse.get('stewards_excuse') and horse.get('written_replay_excuse'):
        if horse['stewards_excuse'] != horse['written_replay_excuse']:
            return True, 'Conflicting excuse signals (manual verification needed)'

    # Criterion 4: Poor performance with no excuse
    if horse.get('last_finish_position', 99) > 8 and not horse.get('excuse_identified'):
        return True, 'Poor performance with no excuse identified (investigate)'

    return False, 'Not high-priority for manual observation'

def human_replay_observation_protocol(race, horse):
    """
    Protocol for human to observe and analyze race replay

    Manual observation checklist:
    1. Start position: Was horse slow to begin?
    2. Early position: Did horse settle where intended?
    3. Mid-race: Any incidents (interference, wide running, traffic)?
    4. Straight: Clear run or blocked?
    5. Finish: Strong or weakening?
    6. Overall: Excuses or genuine poor performance?
    """
    observation_form = {
        'race_id': race['id'],
        'horse_name': horse['name'],
        'last_race_date': horse['last_race_date'],
        'replay_url': horse.get('replay_url'),

        'observations': {
            'start': '',       # e.g., "Slow to begin, lost 2 lengths"
            'early': '',       # e.g., "Settled wider than ideal (4-wide)"
            'mid_race': '',    # e.g., "Checked at 600m, lost momentum"
            'straight': '',    # e.g., "Clear run, no excuses"
            'finish': '',      # e.g., "Weak finish, no extra"
            'overall': ''      # e.g., "Multiple excuses: slow start + wide + checked"
        },

        'excuse_classification': {
            'has_excuse': False,  # True if genuine excuse identified
            'excuse_type': '',    # 'slow_start', 'interference', 'wide_run', 'traffic', etc.
            'excuse_severity': 0, # 0-10 scale (10 = major excuse)
            'impact_adjustment': 0%  # e.g., +10-15% if major excuse
        },

        'time_spent_minutes': 0  # Track observation time
    }

    # Manual observation (human watches replay video)
    print(f"\n🎥 MANUAL REPLAY OBSERVATION REQUIRED")
    print(f"Race: {race['venue']} {race['race_number']} - {race['date']}")
    print(f"Horse: {horse['name']} (finished {horse.get('last_finish_position', 'N/A')})")
    print(f"Replay URL: {observation_form['replay_url']}")
    print(f"\nWatch replay and complete observation form...")

    # Human fills out form manually
    # (In production, this could be a web form or CLI input)

    return observation_form
```

**Selective Observation Strategy**:
```
Observation Triggers (prioritize ~10-15% of races):
✅ Group 1-2 races (highest stakes, worth detailed analysis)
✅ Competitive odds $3-$8 (potential value bets)
✅ Conflicting signals (stewards vs written analysis disagree)
✅ Poor performance with no excuse (investigate if underestimated)

Expected Time Investment:
- 10-15 minutes per replay observation
- ~10-15% of races qualify = 40-60 races/month (if analyzing 400 total)
- Total time: 400-900 minutes/month = 7-15 hours/month

ROI:
- Cost: ~7-15 hours human time/month (valued at $20-50/hour = $140-750/month labor)
- Benefit: +20-30% replay completeness (70% → 90%) for key races
- Conclusion: WORTHWHILE for high-value races (Group 1-2), optional for others
```

**Recommendation**: ✅ **ADD selective replay observation** for Group 1-2 races only (focused effort, high ROI on key races).

---

### Phase 3 Priority 4: Advanced Historical Pattern Recognition

**Why Include**:
- Phase 2 achieves 80% historical completeness (basic patterns from form guide)
- Advanced pattern recognition achieves 90% completeness (deep trends)
- Examples: Trainer first-up patterns, jockey venue specialization, sire wet-track bias
- Cost: Development time only (no subscription costs)

**Implementation**:
```python
# Week 12: Advanced Historical Pattern Recognition
def analyze_trainer_first_up_pattern(trainer, venue):
    """
    Analyze trainer's historical first-up performance at venue
    """
    # Query historical database
    first_up_races = database.query(f"""
        SELECT * FROM races
        WHERE trainer = '{trainer}'
        AND venue = '{venue}'
        AND days_since_last_race > 60  -- First-up definition
    """)

    if len(first_up_races) < 5:
        return {'impact': 0%, 'confidence': 30%, 'reason': 'Insufficient first-up data'}

    # Calculate first-up win rate
    wins = sum(1 for race in first_up_races if race['finish_position'] == 1)
    win_rate = wins / len(first_up_races) * 100

    # Compare to trainer's overall win rate
    overall_win_rate = calculate_trainer_overall_win_rate(trainer, venue)

    if win_rate > overall_win_rate * 1.5:  # 50% better first-up
        return {
            'impact': +8-12%,
            'confidence': 75%,
            'reason': f'{trainer} first-up specialist at {venue} ({win_rate:.0f}% vs {overall_win_rate:.0f}% overall)'
        }
    elif win_rate < overall_win_rate * 0.7:  # 30% worse first-up
        return {
            'impact': -8-12%,
            'confidence': 75%,
            'reason': f'{trainer} poor first-up at {venue} ({win_rate:.0f}% vs {overall_win_rate:.0f}% overall)'
        }
    else:
        return {
            'impact': 0%,
            'confidence': 60%,
            'reason': f'{trainer} first-up consistent with overall ({win_rate:.0f}%)'
        }

def analyze_jockey_venue_specialization(jockey, venue):
    """
    Analyze jockey's venue-specific performance
    """
    venue_races = database.query(f"""
        SELECT * FROM races
        WHERE jockey = '{jockey}'
        AND venue = '{venue}'
    """)

    if len(venue_races) < 10:
        return {'impact': 0%, 'confidence': 30%, 'reason': 'Insufficient venue data'}

    venue_win_rate = sum(1 for race in venue_races if race['finish_position'] == 1) / len(venue_races) * 100
    overall_win_rate = calculate_jockey_overall_win_rate(jockey)

    if venue_win_rate > overall_win_rate * 1.3:  # 30% better at venue
        return {
            'impact': +5-8%,
            'confidence': 70%,
            'reason': f'{jockey} specialist at {venue} ({venue_win_rate:.0f}% vs {overall_win_rate:.0f}% overall)'
        }
    elif venue_win_rate < overall_win_rate * 0.7:
        return {
            'impact': -5-8%,
            'confidence': 70%,
            'reason': f'{jockey} struggles at {venue} ({venue_win_rate:.0f}% vs {overall_win_rate:.0f}% overall)'
        }
    else:
        return {'impact': 0%, 'confidence': 60%, 'reason': f'{jockey} consistent at {venue}'}

def analyze_sire_track_condition_bias(sire, track_condition):
    """
    Analyze sire's progeny performance on specific track conditions
    """
    condition_races = database.query(f"""
        SELECT * FROM races
        WHERE sire = '{sire}'
        AND track_condition_category = '{track_condition}'  -- 'Heavy', 'Soft', 'Good', 'Firm'
    """)

    if len(condition_races) < 10:
        return {'impact': 0%, 'confidence': 30%, 'reason': 'Insufficient sire condition data'}

    condition_win_rate = sum(1 for race in condition_races if race['finish_position'] <= 3) / len(condition_races) * 100
    overall_sire_win_rate = calculate_sire_overall_win_rate(sire)

    if condition_win_rate > overall_sire_win_rate * 1.4:  # 40% better in condition
        return {
            'impact': +5-10%,
            'confidence': 65%,
            'reason': f'{sire} progeny excel on {track_condition} ({condition_win_rate:.0f}% vs {overall_sire_win_rate:.0f}% overall)'
        }
    elif condition_win_rate < overall_sire_win_rate * 0.6:
        return {
            'impact': -5-10%,
            'confidence': 65%,
            'reason': f'{sire} progeny struggle on {track_condition} ({condition_win_rate:.0f}% vs {overall_sire_win_rate:.0f}% overall)'
        }
    else:
        return {'impact': 0%, 'confidence': 60%, 'reason': f'{sire} progeny consistent on {track_condition}'}
```

**Advanced Pattern ROI**:
- Cost: ~20-30 hours development time (one-time investment)
- Benefit: +10% historical completeness (80% → 90%), +2-5% niche pattern boost
- Conclusion: WORTHWHILE (one-time effort, ongoing benefit, no subscription cost)

**Recommendation**: ✅ **ADD advanced patterns** in Week 12 (good ROI, no ongoing cost).

---

### PHASE 3 SUMMARY

**Deliverables** (End of Week 12):
```
❌ Social Media Monitoring: NOT RECOMMENDED (expensive $100-500/month, marginal ROI)
✅ Speedmaps Visual Pace Maps: RECOMMENDED if budget allows ($30-50/month, good ROI)
✅ Selective Human Replay Observation: RECOMMENDED for Group 1-2 races (focused effort, high-value)
✅ Advanced Historical Patterns: RECOMMENDED (one-time effort, no ongoing cost)
```

**Metrics**:
- **Completeness**: 95%+ (vs Phase 2 90-95%)
- **Cost**: $0.15-$0.35 per race WITHOUT social media (Speedmaps + labor amortized)
- **Cost**: $0.40-$1.75 per race WITH social media (add Twitter $0.25-$1.25)
- **Speed**: ~12-18 minutes per race (replay observation adds time for key races)
- **Coverage Categories**: 17 of 17 categories (100% category coverage)
- **Competitive Advantages**: Marginal incremental (+5-15% over Phase 2)

**ROI Analysis**:
- **Investment**: ~30-40 hours development time (Weeks 9-12)
- **Ongoing Cost**: $0.15-$0.35/race (no social) OR $0.40-$1.75/race (with social)
- **Prediction Power Gain**: +5-15% incremental (diminishing returns vs Phase 1-2)
- **Payback Period**: 6-12 months (if betting ROI justifies cost), marginal

**FINAL PHASE 3 RECOMMENDATION**:
```
✅ INCLUDE Phase 3 (selective):
  - Speedmaps ($0.03-$0.05/race) ✅
  - Selective replay observation (Group 1-2 only) ✅
  - Advanced historical patterns (one-time effort) ✅

❌ EXCLUDE Phase 3 (expensive, low ROI):
  - Social media monitoring ($0.25-$1.25/race) ❌

Recommended Phase 3 Cost: $0.15-$0.35/race (selective enhancements, good ROI)
NOT RECOMMENDED: Full Phase 3 with social media ($0.40-$1.75/race, marginal ROI)
```

---

## PART 2: TESTING PROTOCOL & COMPETITIVE BENCHMARKING

**Purpose**: Validate system performance vs ChatGPT-5 through head-to-head testing

---

### Testing Methodology: Head-to-Head Comparison

**Approach**: Run both systems (Ours vs ChatGPT-5) on same 3-5 actual races, compare:
1. **Completeness Score** (% taxonomy covered)
2. **Prediction Accuracy** (win probability calibration)
3. **Speed** (minutes per race)
4. **Cost Efficiency** ($/race)

**Test Sample Selection**:
```python
def select_test_races():
    """
    Select 3-5 representative test races for benchmarking

    Criteria:
    - Mix of track types (metro vs provincial)
    - Mix of race classes (Group 1-3, listed, open handicap)
    - Mix of field sizes (8-runner vs 16-runner)
    - Mix of betting market scenarios (favorite clear vs close market)
    - Upcoming races (within next 7 days for real-time testing)
    """
    test_races = [
        {
            'race': 'Flemington Race 7',
            'date': '2024-12-28',
            'class': 'Group 2',
            'distance': '1400m',
            'field_size': 12,
            'market': 'Competitive ($3.50 favorite, 4 horses under $8)',
            'reason': 'High-quality field, competitive betting, pace complexity'
        },
        {
            'race': 'Randwick Race 8',
            'date': '2024-12-28',
            'class': 'Listed',
            'distance': '1200m',
            'field_size': 14,
            'market': 'Clear favorite ($2.20, next best $7.00)',
            'reason': 'Dominant favorite scenario, test bias detection'
        },
        {
            'race': 'Moonee Valley Race 5',
            'date': '2024-12-29',
            'class': 'Open Handicap',
            'distance': '1600m',
            'field_size': 10,
            'market': 'Very competitive (5 horses $4-$7 range)',
            'reason': 'Close market, value bet identification test'
        },
        {
            'race': 'Rosehill Race 7',
            'date': '2024-12-30',
            'class': 'Group 3',
            'distance': '2000m',
            'field_size': 8,
            'market': 'Small field, clear top 3 ($3.00, $4.50, $6.00)',
            'reason': 'Staying race, stamina analysis test'
        },
        {
            'race': 'Caulfield Race 9',
            'date': '2024-12-31',
            'class': 'Group 1',
            'distance': '1600m',
            'field_size': 16,
            'market': 'Wide open (favorite $5.50, 8 horses under $15)',
            'reason': 'Large field Group 1, complexity + quality test'
        }
    ]

    return test_races
```

---

### Testing Metric 1: Completeness Score

**Definition**: % of taxonomy categories covered with high-quality data

**Measurement**:
```python
def measure_completeness(system_output, taxonomy):
    """
    Calculate completeness score for each system

    Args:
        system_output: Analysis output from system (ours or ChatGPT-5)
        taxonomy: 17-category reference taxonomy

    Returns:
        Completeness score (0-100%)
    """
    category_scores = {}

    for category in taxonomy['categories']:
        category_id = category['id']

        # Check if category addressed
        if category_id in system_output:
            category_data = system_output[category_id]

            # Score based on completeness within category
            if category_data.get('data_quality') == 'high':  # Official sources
                category_scores[category_id] = 100%
            elif category_data.get('data_quality') == 'medium':  # Public sources
                category_scores[category_id] = 70%
            elif category_data.get('data_quality') == 'low':  # Inference only
                category_scores[category_id] = 40%
            else:
                category_scores[category_id] = 0%  # Not covered
        else:
            category_scores[category_id] = 0%  # Not covered

    # Weighted average (weight by category importance)
    category_weights = {
        'Category 1-2': 5,
        'Category 3': 8,
        'Category 4': 7,
        'Category 5': 6,
        'Category 6': 7,
        'Category 7': 7,
        'Category 8': 9,
        'Category 9': 8,
        'Category 10': 10,  # Trials (high importance)
        'Category 11': 9,   # Stewards (high importance)
        'Category 12': 9,   # Market (high importance)
        'Category 13': 6,
        'Category 14': 6,
        'Category 15': 8,
        'Category 16': 8,
        'Category 17': 7
    }

    total_weighted_score = sum(category_scores[cat_id] * category_weights[cat_id]
                                for cat_id in category_scores.keys())
    total_weight = sum(category_weights.values())

    overall_completeness = total_weighted_score / total_weight

    return {
        'overall': overall_completeness,
        'by_category': category_scores
    }
```

**Expected Results**:
```
ChatGPT-5 Completeness (validated from deep research):
- Overall: 65-70%
- Key Gaps: Trials (0%), Stewards (0%), Market Movements (30%), Replays (0%)

Our System Completeness (Phase 1):
- Overall: 85-90%
- Solved Gaps: Trials (85%), Stewards (75%), Market (95%), Replays (40%)

Our System Completeness (Phase 2):
- Overall: 90-95%
- Enhanced: Expert (90%), Pace (90%), Replays (70%)

Advantage: +20-30% completeness over ChatGPT-5
```

---

### Testing Metric 2: Prediction Accuracy

**Definition**: Calibration of win probabilities vs actual outcomes

**Measurement**:
```python
def measure_prediction_accuracy(predictions, actual_results, num_races=50):
    """
    Measure prediction accuracy after collecting 50+ race results

    Calibration: For horses predicted 20% win probability, do ~20% actually win?

    Args:
        predictions: List of {horse, predicted_probability, actual_result}
        actual_results: Actual race outcomes
        num_races: Number of races in test sample

    Returns:
        Accuracy metrics (calibration, Brier score, ROI)
    """
    # Group predictions by probability bins
    probability_bins = {
        '0-10%': {'predicted': [], 'actual_wins': 0},
        '10-20%': {'predicted': [], 'actual_wins': 0},
        '20-30%': {'predicted': [], 'actual_wins': 0},
        '30-40%': {'predicted': [], 'actual_wins': 0},
        '40-50%': {'predicted': [], 'actual_wins': 0},
        '50-60%': {'predicted': [], 'actual_wins': 0},
        '60-70%': {'predicted': [], 'actual_wins': 0},
        '70-80%': {'predicted': [], 'actual_wins': 0},
        '80-90%': {'predicted': [], 'actual_wins': 0},
        '90-100%': {'predicted': [], 'actual_wins': 0}
    }

    for prediction in predictions:
        prob = prediction['predicted_probability']
        actual_won = prediction['actual_result'] == 'won'

        # Assign to bin
        if prob < 10:
            bin_key = '0-10%'
        elif prob < 20:
            bin_key = '10-20%'
        # ... (continue for all bins)

        probability_bins[bin_key]['predicted'].append(prob)
        if actual_won:
            probability_bins[bin_key]['actual_wins'] += 1

    # Calculate calibration for each bin
    calibration_errors = []

    for bin_key, bin_data in probability_bins.items():
        if len(bin_data['predicted']) > 0:
            avg_predicted_prob = sum(bin_data['predicted']) / len(bin_data['predicted'])
            actual_win_rate = bin_data['actual_wins'] / len(bin_data['predicted']) * 100

            calibration_error = abs(avg_predicted_prob - actual_win_rate)
            calibration_errors.append(calibration_error)

            print(f"{bin_key}: Predicted {avg_predicted_prob:.1f}%, Actual {actual_win_rate:.1f}%, Error {calibration_error:.1f}%")

    # Overall calibration score (lower error = better)
    mean_calibration_error = sum(calibration_errors) / len(calibration_errors) if calibration_errors else 0

    # Brier score (measures prediction accuracy, 0 = perfect, 1 = worst)
    brier_score = sum((pred['predicted_probability']/100 - (1 if pred['actual_result'] == 'won' else 0))**2
                     for pred in predictions) / len(predictions)

    # Betting ROI (if betting on all overlays)
    total_bet = 0
    total_return = 0

    for prediction in predictions:
        market_odds = prediction['market_odds']
        predicted_prob = prediction['predicted_probability'] / 100

        # Bet if overlay (predicted prob > market prob)
        market_prob = 1 / market_odds

        if predicted_prob > market_prob * 1.1:  # 10% edge threshold
            total_bet += 1  # $1 unit bet

            if prediction['actual_result'] == 'won':
                total_return += market_odds  # Win returns

    betting_roi = ((total_return - total_bet) / total_bet * 100) if total_bet > 0 else 0

    return {
        'mean_calibration_error': mean_calibration_error,
        'brier_score': brier_score,
        'betting_roi': betting_roi,
        'num_predictions': len(predictions)
    }
```

**Expected Results** (after 50+ races):
```
Calibration Target:
- Mean calibration error < 5% (excellent)
- Brier score < 0.15 (good prediction accuracy)

Betting ROI Target:
- Positive ROI (>0%) validates edge over market
- 5-10% ROI excellent (compound long-term)

Comparison to ChatGPT-5:
- ChatGPT-5 likely has ~8-12% calibration error (lacks official data, market movements)
- Our system target: <5% calibration error (more complete data, better accuracy)
```

---

### Testing Metric 3: Speed

**Definition**: Minutes per race to complete analysis

**Measurement**:
```python
import time

def measure_analysis_speed(race):
    """
    Time how long analysis takes per race
    """
    start_time = time.time()

    # Run complete analysis pipeline
    analysis = analyze_race_complete(race)

    end_time = time.time()
    elapsed_minutes = (end_time - start_time) / 60

    return {
        'elapsed_minutes': elapsed_minutes,
        'race_id': race['id']
    }
```

**Speed Targets**:
```
ChatGPT-5 Speed (validated from examples):
- Single race: 13-18 minutes (deep analysis, iterative refinement)
- Multi-race efficiency: 9 races in 13 minutes total (~1.4 min/race when batched)

Our System Speed Targets:
- Phase 1 (initial): 15-20 minutes per race (prioritize completeness over speed)
- Phase 2 (optimized): 12-15 minutes per race (optimize data pipelines)
- Phase 3 (final): 10-13 minutes per race (batch processing, caching)
- Multi-race efficiency: Target <2 min/race when analyzing full race card (amortize authentication, batch API calls)

Goal: MATCH or BEAT ChatGPT-5 speed (10-13 min/race single, <2 min/race batched)
```

---

### Testing Metric 4: Cost Efficiency

**Definition**: $ per race analysis

**Comparison**:
```
ChatGPT-5 Cost:
- API calls: Estimated $0.10-$0.30 per race (GPT-5 API, web browsing, multiple iterations)
- Data access: $0 (public sources only, no subscriptions)
- Total: ~$0.10-$0.30 per race

Our System Cost (Phase 1):
- Racing.com auth: $0.02-$0.10/race (amortized)
- Betfair API: $0 (free)
- BOM weather: $0 (free)
- GPT-5 synthesis: $0.05-$0.15/race (API calls)
- Total: ~$0.07-$0.25/race

Our System Cost (Phase 2):
- Phase 1 costs: $0.07-$0.25
- Punters premium: $0.05-$0.10/race (amortized)
- Speedmaps: $0.03-$0.05/race (optional, amortized)
- Total: ~$0.15-$0.40/race

Cost Comparison:
- Phase 1: COMPETITIVE with ChatGPT ($0.07-$0.25 vs $0.10-$0.30)
- Phase 2: SLIGHTLY HIGHER than ChatGPT ($0.15-$0.40 vs $0.10-$0.30)
- BUT: 20-30% MORE COMPLETE than ChatGPT (better ROI if predictions improve)
```

**Cost-Benefit Analysis**:
```
If Prediction Accuracy Improves by 5%:
- Betting ROI improvement: ~2-5% absolute
- Annual betting volume: $10,000 (example)
- Annual ROI gain: $200-500
- Annual cost increase: $50-150 (Phase 2 subscriptions)
- Net gain: $50-350/year (WORTHWHILE)

Break-even Analysis:
- Need ~2-3% prediction accuracy improvement to justify Phase 2 costs
- Expected improvement: 5-10% (based on +20-30% completeness advantage)
- Conclusion: WORTHWHILE investment if betting regularly
```

---

**Part 6c Complete (Phase 3 + Testing Protocol + Metrics). Ready for Part 6d (Continuous Improvement + Final Summary).**
