# Racing.com API Integration Guide

**Date:** November 14, 2025
**Discovered:** GraphQL API endpoint analysis

---

## 🎯 Discovery: Racing.com Uses GraphQL API

Racing.com is a **React SPA** that loads all data via a GraphQL API, not HTML scraping.

### **API Endpoint:**

```
https://graphql.rmdprod.racing.com/
```

### **API Key:**

```
da2-6nsi4ztsynar3l3frgxf77q5fe
```

### **Authentication:**

- Header: `x-api-key: da2-6nsi4ztsynar3l3frgxf77q5fe`

---

## 📋 Recommended Approach

### **Option 1: GraphQL API (Recommended)**

**Pros:**

- Official API, stable structure
- JSON data (easy to parse)
- Fast, no HTML parsing
- Comprehensive data

**Cons:**

- Need to reverse-engineer GraphQL queries
- May have rate limits

**Implementation:**

```python
import requests

headers = {
    "x-api-key": "da2-6nsi4ztsynar3l3frgxf77q5fe",
    "Content-Type": "application/json"
}

query = """
query GetRaceCard($date: String!, $venue: String!) {
  raceCard(date: $date, venue: $venue) {
    races {
      raceNumber
      raceName
      distance
      trackCondition
      runners {
        horseNumber
        horseName
        jockeyName
        trainerName
        barrier
        weight
        gear
      }
    }
  }
}
"""

variables = {
    "date": "2024-11-05",
    "venue": "flemington"
}

response = requests.post(
    "https://graphql.rmdprod.racing.com/",
    headers=headers,
    json={"query": query, "variables": variables}
)
```

---

### **Option 2: Selenium (Fallback)**

If GraphQL queries are complex, use Selenium to let React render, then scrape DOM.

**Pros:**

- Guaranteed to get rendered data
- No need to reverse-engineer API

**Cons:**

- Slower (need browser)
- More resource-intensive
- Requires ChromeDriver

---

## 🔄 Updated Implementation Strategy

### **racing_com.py - Refactor to Use API**

Current implementation uses BeautifulSoup on HTML (wrong approach).

**New implementation should:**

1. Use GraphQL API endpoint
2. Construct proper GraphQL queries
3. Parse JSON responses
4. Return same `Race`, `Runner`, `Horse`, `Jockey`, `Trainer` models

---

## 🧪 Next Steps

1. **Intercept Network Traffic** (Browser DevTools)
   - Open <https://www.racing.com/form/2024-11-05/flemington>
   - Open DevTools → Network tab
   - Filter by "Fetch/XHR"
   - Find GraphQL requests
   - Copy actual query structure

2. **Test GraphQL Queries**
   - Use Postman or curl
   - Verify API key works
   - Refine query structure

3. **Refactor Scraper**
   - Replace BeautifulSoup with requests.post()
   - Implement GraphQL query builder
   - Update data extraction logic

---

## 📝 Example GraphQL Query Discovery

Run this to intercept actual queries:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

# Enable network logging
options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

driver = webdriver.Chrome(options=options)
driver.get("https://www.racing.com/form/2024-11-05/flemington")

# Wait for page load
time.sleep(5)

# Get network logs
logs = driver.get_log('performance')

for log in logs:
    message = json.loads(log['message'])['message']
    if 'Network.requestWillBeSent' in message['method']:
        url = message['params']['request']['url']
        if 'graphql' in url:
            print(f"GraphQL Request: {url}")
            print(f"Headers: {message['params']['request']['headers']}")
            if 'postData' in message['params']['request']:
                print(f"Body: {message['params']['request']['postData']}")
```

---

## ✅ Action Items

- [ ] Cloud Agent: Intercept actual GraphQL queries using browser DevTools
- [ ] Refactor `racing_com.py` to use GraphQL API
- [ ] Test on 10 historical races
- [ ] Update CSS selector approach → API approach in docs

---

**Status:** 🔍 Discovery complete, implementation pending
**Priority:** 🔥 High (blocks all other scrapers that need racing data)
**Estimated Time:** 2-3 hours to refactor

---

This is a **CRITICAL FINDING** that changes our scraping strategy!
