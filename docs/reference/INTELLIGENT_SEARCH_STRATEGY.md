# Intelligent Search Strategy - Hybrid Fixed + Autonomous

**Date**: November 8, 2025
**Purpose**: Define how the agent searches for racing intelligence
**Approach**: Fixed mandatory sources + Intelligent autonomous discovery

---

## 🎯 Core Principle

**Hybrid Strategy**:
1. **Fixed Sources** (Always Checked) - 20-30 mandatory sources we KNOW are valuable
2. **Intelligent Discovery** (Agent-Driven) - 20-40 additional sources based on context

**Reasoning**:
- Fixed sources ensure we never miss critical official data
- Agent discovery allows adaptation to race-specific context
- Combines reliability with flexibility

---

## 📋 1. Fixed Mandatory Sources (Always Scraped)

### **Tier 1: Official Australian Racing (CRITICAL - Never Skip)**

```python
MANDATORY_TIER_1_SOURCES = [
    {
        "name": "Racing Victoria Stewards Reports",
        "url_pattern": "https://www.racingvictoria.com.au/the-sport/stewards/{track}/{date}",
        "data": ["Vet checks", "Gear changes", "Incidents", "Stand-downs", "Track conditions"],
        "reliability": 1.00,
        "frequency": "Every race",
        "scrape_method": "HTTP + HTML parsing",
        "failure_action": "CRITICAL - Abort if unavailable"
    },
    {
        "name": "Racing.com Form Guide",
        "url_pattern": "https://www.racing.com/form-guide/{track}/{date}/race-{number}",
        "data": ["Fields", "Barriers", "Weights", "Jockey/Trainer", "Prices", "Ratings"],
        "reliability": 0.98,
        "frequency": "Every race",
        "scrape_method": "HTTP + JSON API (if available)",
        "failure_action": "CRITICAL - Use fallback (Punters.com)"
    },
    {
        "name": "Racing.com Trial Results",
        "url_pattern": "https://www.racing.com/form-guide/trials/{track}/{date}",
        "data": ["Trial times", "Sectionals", "Jockey comments", "Gallop quality"],
        "reliability": 0.95,
        "frequency": "If trials within 30 days",
        "scrape_method": "HTTP + HTML parsing",
        "failure_action": "WARN - Continue without"
    },
    {
        "name": "Racing.com Track Conditions",
        "url_pattern": "https://www.racing.com/tracks/{track}",
        "data": ["Going", "Rail position", "Penetrometer", "Weather"],
        "reliability": 0.98,
        "frequency": "Every race",
        "scrape_method": "HTTP + JSON API",
        "failure_action": "CRITICAL - Use weather API fallback"
    },
    {
        "name": "Racing.com Scratchings",
        "url_pattern": "https://www.racing.com/scratchings/{date}",
        "data": ["Late withdrawals", "Vet scratches", "Emergency runners"],
        "reliability": 1.00,
        "frequency": "Every race (check 2h before)",
        "scrape_method": "HTTP + HTML parsing",
        "failure_action": "CRITICAL - Abort if unavailable"
    }
]
```

### **Tier 2: Expert Australian Analysis (HIGH PRIORITY)**

```python
MANDATORY_TIER_2_SOURCES = [
    {
        "name": "Racing.com Expert Tips",
        "url": "https://www.racing.com/tips/{track}/{date}/race-{number}",
        "data": ["Expert selections", "Confidence levels", "Analysis", "Best bets"],
        "reliability": 0.85,
        "experts": ["Michael Felgate", "Brad Gray", "Others"],
        "frequency": "Every race"
    },
    {
        "name": "Punters.com.au Form Analysis",
        "url": "https://www.punters.com.au/racing-form-guide/{track}/{date}/{race}",
        "data": ["Speed maps", "Ratings", "Tips", "Scratchings alerts"],
        "reliability": 0.82,
        "frequency": "Every race"
    },
    {
        "name": "Racenet Form & Tips",
        "url": "https://www.racenet.com.au/form-guide/{track}-{date}/race-{number}",
        "data": ["Form ratings", "Selections", "Track bias notes"],
        "reliability": 0.80,
        "frequency": "Every race"
    },
    {
        "name": "Timeform Australia",
        "url": "https://www.timeform.com/horse-racing/racecards/{track}/{date}/race-{number}",
        "data": ["Timeform ratings", "Flags", "Analysis"],
        "reliability": 0.88,
        "frequency": "Every race",
        "note": "Premium content - check access"
    },
    {
        "name": "Betfair Hub - Racing Analysis",
        "url": "https://betting.betfair.com/horse-racing/australian-racing/",
        "data": ["Market analysis", "Value tips", "Betting insights"],
        "reliability": 0.75,
        "frequency": "Major races only"
    }
]
```

### **Tier 3: Major Racing Media (ALWAYS CHECK)**

```python
MANDATORY_TIER_3_SOURCES = [
    {
        "name": "Racing.com News",
        "url": "https://www.racing.com/news/",
        "search": "{horse_name} OR {trainer} OR {jockey} OR {track}",
        "data": ["Stable reports", "Trainer interviews", "Injury updates"],
        "reliability": 0.78,
        "recency": "Last 7 days"
    },
    {
        "name": "Herald Sun Racing",
        "url": "https://www.heraldsun.com.au/sport/superracing/",
        "search": "{track} race {number} OR {horse_name}",
        "data": ["News", "Stable visits", "Insider info"],
        "reliability": 0.72,
        "recency": "Last 7 days"
    },
    {
        "name": "The Age Racing",
        "url": "https://www.theage.com.au/sport/racing/",
        "search": "{track} {date} OR {horse_name}",
        "data": ["Preview articles", "Expert columns"],
        "reliability": 0.72,
        "recency": "Last 7 days"
    },
    {
        "name": "Racing.com Video Replays",
        "url": "https://www.racing.com/replays/",
        "search": "{horse_name} last 3 starts",
        "data": ["Visual form assessment", "Running style"],
        "reliability": 0.95,
        "note": "Video analysis - may need human review initially"
    }
]
```

### **Tier 4: Weather & Track Data (MANDATORY)**

```python
MANDATORY_WEATHER_SOURCES = [
    {
        "name": "Bureau of Meteorology (BOM)",
        "url": "http://www.bom.gov.au/",
        "api": "BOM API or Web Scrape",
        "data": ["Hourly forecast", "Rainfall", "Wind", "Temperature"],
        "reliability": 0.98,
        "frequency": "Every race (3-hour window)"
    },
    {
        "name": "Open-Meteo Weather API",
        "url": "https://open-meteo.com/",
        "api": "Free API",
        "data": ["Forecast", "Historical", "Precipitation"],
        "reliability": 0.95,
        "frequency": "Every race"
    },
    {
        "name": "Racing.com Track Inspection",
        "url": "https://www.racing.com/news/track-inspections/",
        "data": ["Track manager quotes", "Going changes", "Rail moves"],
        "reliability": 0.90,
        "frequency": "Morning of race"
    }
]
```

**Total Fixed Sources**: ~20-25 sources checked EVERY TIME

---

## 🤖 2. Intelligent Autonomous Discovery

### **2.1 When Agent Searches Autonomously**

The agent should intelligently search for ADDITIONAL sources when:

1. **High-Stakes Race** (Group 1, Listed, Prize > $200k)
   - Search international form
   - Check breeding/pedigree analysis
   - Look for international expert opinions

2. **Specific Concerns Identified**
   - Horse hasn't run in 90+ days → Search for trial reports, injury news
   - First-time gear change → Search for stable comments on why
   - Track bias reported → Search for recent meeting reports
   - Jockey change → Search for booking significance

3. **Contradictions in Fixed Sources**
   - Expert A says "best chance", Expert B says "avoid"
   - Search for additional context, recent stable news

4. **Information Gaps**
   - Fixed sources don't mention horse → Check if emergency runner, search news
   - Gear change not explained → Search trainer interviews
   - Unusual betting move → Search for social media signals

### **2.2 Agent Search Strategy**

```python
class IntelligentSearchAgent:
    """
    Agent that decides WHEN and WHERE to search beyond fixed sources
    """

    def should_search_additional(self, context: dict) -> bool:
        """
        Decide if we need more sources beyond mandatory ones
        """
        triggers = []

        # High-stakes race
        if context['prize_money'] > 200000:
            triggers.append("high_stakes")

        # Information gaps
        if context['missing_data']:
            triggers.append(f"missing: {context['missing_data']}")

        # Contradictions
        if context['contradictions']:
            triggers.append("contradictions_detected")

        # Specific concerns
        if any([
            context.get('days_since_run', 0) > 90,
            context.get('first_time_blinkers'),
            context.get('jockey_change_late'),
            context.get('track_bias_reports')
        ]):
            triggers.append("specific_concern")

        return len(triggers) > 0, triggers

    def generate_search_queries(self, horse: str, trigger: str) -> list[str]:
        """
        Generate intelligent search queries based on trigger
        """
        queries = []

        if trigger == "high_stakes":
            queries.extend([
                f"{horse} recent form overseas",
                f"{horse} pedigree analysis",
                f"{horse} breeding suited to distance",
                f"{horse} international ratings"
            ])

        elif "missing" in trigger:
            missing_field = trigger.split(":")[1].strip()
            queries.append(f"{horse} {missing_field}")

        elif trigger == "contradictions_detected":
            queries.extend([
                f"{horse} stable confidence",
                f"{horse} trainer comments this week",
                f"{horse} latest trackwork"
            ])

        elif trigger == "specific_concern":
            queries.extend([
                f"{horse} injury update",
                f"{horse} barrier trial recent",
                f"{horse} gear change reason"
            ])

        return queries

    def select_additional_sources(self, queries: list[str]) -> list[dict]:
        """
        For each query, decide which sources to check
        """
        additional_sources = []

        for query in queries:
            # Use LLM to intelligently select sources
            # Based on query type, select most relevant sources

            if "overseas" in query or "international" in query:
                additional_sources.extend([
                    {"name": "Racing Post (UK)", "url": "https://www.racingpost.com/"},
                    {"name": "Equibase (USA)", "url": "https://www.equibase.com/"},
                    {"name": "Hong Kong Jockey Club", "url": "https://racing.hkjc.com/"}
                ])

            if "pedigree" in query or "breeding" in query:
                additional_sources.extend([
                    {"name": "Arion Pedigrees", "url": "https://www.arion.co.nz/"},
                    {"name": "Thoroughbred Pedigree", "url": "https://www.thoroughbredpedigree.com/"}
                ])

            if "stable" in query or "trainer" in query:
                additional_sources.extend([
                    {"name": "Trainer Twitter/X", "search": f"twitter.com/{trainer_handle}"},
                    {"name": "Stable Facebook", "search": f"facebook.com/{stable_name}"}
                ])

            if "trial" in query or "trackwork" in query:
                additional_sources.extend([
                    {"name": "Trackwork reports", "url": "https://www.racing.com/trackwork"},
                    {"name": "Jump-out results", "search": f"{track} jump-outs"}
                ])

        # Deduplicate and prioritize
        return self._deduplicate_and_prioritize(additional_sources)

    def _deduplicate_and_prioritize(self, sources: list[dict]) -> list[dict]:
        """Remove duplicates, sort by relevance"""
        seen = set()
        unique = []
        for source in sources:
            if source['name'] not in seen:
                seen.add(source['name'])
                unique.append(source)
        return unique[:20]  # Limit to 20 additional sources
```

### **2.3 Autonomous Search Process**

```
Step 1: ANALYZE CONTEXT
  Input: Race details, fixed source data
  Process: Identify triggers (high stakes, gaps, contradictions)
  Output: List of triggers requiring additional research

Step 2: GENERATE QUERIES
  Input: Triggers + Horse/Race context
  Model: GPT-4o-mini (fast query generation)
  Process: Create targeted search queries
  Output: 5-20 specific queries

Step 3: SELECT SOURCES
  Input: Queries
  Model: o1-mini (intelligent source selection)
  Process: For each query, determine best sources to check
  Output: 10-30 additional sources (URLs or search terms)

Step 4: EXECUTE SEARCHES
  Method:
    • Direct URL fetch (if known)
    • Google/Bing search API (if search term)
    • Racing-specific search engines
  Process: Parallel scraping of additional sources
  Output: Raw content from additional sources

Step 5: EXTRACT ADDITIONAL INTELLIGENCE
  Model: Claude 3.5 Sonnet (extraction specialist)
  Process: Extract relevant facts from additional sources
  Output: Additional claims with metadata

Step 6: MERGE WITH FIXED SOURCE DATA
  Process: Combine fixed + autonomous intelligence
  Output: Comprehensive intelligence report
```

---

## 🌐 3. Expanded Source Library

### **3.1 Australian Racing Sources** (Beyond Mandatory)

```python
OPTIONAL_AUSTRALIAN_SOURCES = [
    # Betting Intelligence
    "https://www.tab.com.au/sports/racing",
    "https://www.bet365.com.au/horse-racing",
    "https://www.sportsbet.com.au/betting/horse-racing",

    # Racing Forums & Community
    "https://www.reddit.com/r/horseracing/",
    "https://www.racing-forum.com/",

    # Bloodstock & Breeding
    "https://www.thoroughbrednews.com.au/",
    "https://www.bloodstock.com.au/",

    # Social Media (Verified Accounts)
    "twitter.com/RacingVictoria",
    "twitter.com/Racing_NSW",
    "twitter.com/Racing_Qld",

    # Specialist Sites
    "https://www.championdata.com.au/racing",
    "https://www.thedragons.com.au/"  # Form analysis
]
```

### **3.2 International Sources** (High-Stakes Only)

```python
INTERNATIONAL_SOURCES = {
    "UK": [
        "https://www.racingpost.com/",
        "https://www.attheraces.com/",
        "https://www.britishhorseracing.com/"
    ],
    "USA": [
        "https://www.equibase.com/",
        "https://www.drf.com/"  # Daily Racing Form
    ],
    "Hong Kong": [
        "https://racing.hkjc.com/"
    ],
    "Japan": [
        "https://japanracing.jp/en/"
    ],
    "New Zealand": [
        "https://www.nzracing.co.nz/"
    ]
}
```

### **3.3 Specialized Data Sources**

```python
SPECIALIZED_SOURCES = {
    "track_bias": [
        "https://www.racing.com/news/track-bias",
        "Recent meeting reports (last 7 days)",
        "Social media track condition posts"
    ],

    "breeding_pedigree": [
        "https://www.arion.co.nz/",
        "https://www.thoroughbredpedigree.com/",
        "https://www.bloodhorse.com/"
    ],

    "trials_jumpouts": [
        "https://www.racing.com/form-guide/trials",
        "State-specific trial sites",
        "Trackwork galleries"
    ],

    "veterinary": [
        "Stewards vet reports",
        "Racing Victoria veterinary notices",
        "Trainer public statements on injuries"
    ],

    "market_intelligence": [
        "Betfair price history API",
        "TAB price movements",
        "Bookmaker odds comparison sites"
    ]
}
```

---

## 🔍 4. Search Methodology

### **4.1 Web Search Approach**

```python
class WebSearchStrategy:
    """
    How the agent actually searches the web
    """

    def search(self, query: str, method: str = "auto") -> list[dict]:
        """
        Execute web search using most appropriate method
        """

        if method == "direct_url":
            # We know exact URL pattern
            url = self.construct_url(query)
            return self.fetch_url(url)

        elif method == "google_search":
            # Use Google search (limited to racing domains)
            return self.google_custom_search(
                query=query,
                site_restrictions=[
                    "racing.com",
                    "racenet.com.au",
                    "punters.com.au",
                    # ... etc
                ],
                date_range="past_7_days"
            )

        elif method == "bing_search":
            # Bing search API (alternative to Google)
            return self.bing_search_api(query, filters={
                "sites": ["racing.com", "*.racing.com"],
                "freshness": "Week"
            })

        elif method == "auto":
            # Intelligently choose method
            if self.has_url_pattern(query):
                return self.search(query, "direct_url")
            else:
                return self.search(query, "google_search")

    def construct_url(self, query_params: dict) -> str:
        """
        Build URL from parameters using known patterns
        """
        # Example: Racing.com form guide
        if query_params['site'] == 'racing.com_form':
            return (
                f"https://www.racing.com/form-guide/"
                f"{query_params['track']}/"
                f"{query_params['date']}/"
                f"race-{query_params['race_number']}"
            )
        # ... more patterns

    def google_custom_search(self, query: str, site_restrictions: list,
                            date_range: str) -> list[dict]:
        """
        Use Google Custom Search API (or scrape Google)
        """
        # Construct Google search URL
        sites = " OR ".join([f"site:{site}" for site in site_restrictions])
        full_query = f"{query} {sites}"

        # Use API or BeautifulSoup scraping
        results = self._fetch_google_results(full_query, date_range)

        return [
            {
                "url": result['url'],
                "title": result['title'],
                "snippet": result['snippet'],
                "source": self._extract_domain(result['url'])
            }
            for result in results[:10]  # Top 10 results
        ]
```

### **4.2 Search Query Generation**

```python
def generate_search_query(context: dict, intent: str) -> str:
    """
    Generate optimal search query for intent

    Model: GPT-4o-mini (fast, cheap)
    """

    prompt = f"""
    Generate a search query to find information about:

    Horse: {context['horse_name']}
    Race: {context['track']} Race {context['race_number']} on {context['date']}
    Intent: {intent}

    Requirements:
    - Specific to this horse/race
    - Include relevant racing terms
    - Optimize for Australian racing sites
    - Focus on recent information (last 7 days)

    Examples:
    - Intent: "gear changes" → "{horse_name} blinkers first time"
    - Intent: "stable confidence" → "{trainer} {horse_name} comments this week"
    - Intent: "track bias" → "{track} track bias {date} meeting"

    Generate query:
    """

    # Use LLM to generate query
    query = llm.generate(prompt, max_tokens=50)
    return query.strip()
```

### **4.3 Source Prioritization**

```python
def prioritize_sources(sources: list[dict], context: dict) -> list[dict]:
    """
    Rank sources by expected value for this specific query

    Model: o1-mini (efficient reasoning)
    """

    scored_sources = []

    for source in sources:
        score = 0.0

        # Base reliability score
        score += source.get('reliability', 0.5) * 0.4

        # Recency bonus
        if source.get('last_updated_hours', 999) < 24:
            score += 0.2

        # Relevance to race type
        if context['race_type'] in source.get('specialization', []):
            score += 0.2

        # Authority bonus (official sources)
        if 'official' in source.get('tags', []):
            score += 0.2

        scored_sources.append((score, source))

    # Sort by score descending
    scored_sources.sort(reverse=True, key=lambda x: x[0])

    return [source for score, source in scored_sources]
```

---

## 📊 5. Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────┐
│           USER INPUT: Race Location + Number         │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│        STAGE 1: FIXED SOURCE SCRAPING               │
│  Always scrape 20-25 mandatory sources              │
│  • Official sources (Tier 1): 5 sources             │
│  • Expert analysis (Tier 2): 5 sources              │
│  • Major media (Tier 3): 5 sources                  │
│  • Weather/Track (Tier 4): 3 sources                │
│  Time: 30-60 seconds (parallel)                     │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│        STAGE 2: ANALYZE FIXED SOURCE DATA           │
│  Model: GPT-4o-mini                                 │
│  • Extract initial intelligence                     │
│  • Identify information gaps                        │
│  • Detect contradictions                            │
│  • Assess if additional search needed               │
│  Output: Triggers for autonomous search             │
└───────────────────────┬─────────────────────────────┘
                        ↓
                   ┌────┴─────┐
                   │ Gaps?    │
                   │ Triggers?│
                   └────┬─────┘
                        ↓
                   YES / NO
                        │
            ┌───────────┴───────────┐
            ↓ YES                   ↓ NO (Skip to extraction)
┌─────────────────────────────────────────────────────┐
│    STAGE 3: INTELLIGENT AUTONOMOUS SEARCH           │
│  Model: o1-mini (query generation + source select)  │
│  • Generate targeted search queries (5-20)          │
│  • Select additional sources (10-30)                │
│  • Execute searches (Google/Bing/Direct)            │
│  • Scrape additional sources                        │
│  Time: 60-120 seconds                               │
│  Output: 10-30 additional source contents           │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│        STAGE 4: COMPREHENSIVE EXTRACTION            │
│  Model: Claude 3.5 Sonnet                           │
│  • Extract facts from ALL sources (fixed + added)   │
│  • Batch process: 5 sources per request             │
│  • Total: 30-55 sources → 6-11 requests             │
│  Time: 30-60 seconds                                │
│  Output: Structured claims with metadata            │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│        STAGE 5: SYNTHESIS & REASONING               │
│  Model: o1-preview (advanced reasoning)             │
│  Round 1:                                           │
│    • Combine all claims                             │
│    • Resolve contradictions                         │
│    • Infer patterns                                 │
│    • Generate intelligence report                   │
│  Round 2 (if confidence < 0.90):                    │
│    • Identify remaining gaps                        │
│    • Generate follow-up queries                     │
│    • Re-run search → extract → synthesize           │
│  Time: 60-120 seconds                               │
│  Output: Final intelligence with confidence         │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│        STAGE 6: VERIFICATION & QUALITY              │
│  Model: GPT-4o-mini + o1-mini                       │
│  • Verify critical claims                           │
│  • Check source citations                           │
│  • Assess overall quality                           │
│  • Flag uncertainties                               │
│  Time: 20-30 seconds                                │
│  Output: Verified intelligence report               │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│           FINAL OUTPUT: QUALITATIVE INTEL           │
│  • Per-horse intelligence (5 categories)            │
│  • Source citations for every claim                 │
│  • Confidence scores per claim                      │
│  • Quality assessment                               │
│  • Search metadata (sources checked, time, cost)    │
└─────────────────────────────────────────────────────┘
```

**Total Time**: 5-10 minutes (quality-first approach)
**Total Sources**: 30-55 sources (20-25 fixed + 10-30 intelligent)
**Total Copilot Requests**: 13-17 requests
**Quality Target**: ≥95% accuracy

---

## 📋 6. Implementation Checklist

### **Phase 1: Fixed Sources** (Week 1)
- [ ] Build scrapers for 25 mandatory sources
- [ ] Test scraping reliability
- [ ] Implement error handling/fallbacks
- [ ] Cache strategy (24h for most sources)

### **Phase 2: Intelligent Search** (Week 2)
- [ ] Implement trigger detection logic
- [ ] Build query generation (GPT-4o-mini)
- [ ] Implement source selection (o1-mini)
- [ ] Integrate Google/Bing search APIs
- [ ] Test on 10 sample races

### **Phase 3: Integration** (Week 3)
- [ ] Combine fixed + intelligent sources
- [ ] Implement Claude extraction pipeline
- [ ] Add o1-preview synthesis (2 rounds)
- [ ] Build verification layer
- [ ] End-to-end testing

---

**Status**: Design Complete - Ready for Implementation
**Next**: Build scrapers for fixed sources (Phase 1)
**Owner**: thomasrocks006-cmyk
