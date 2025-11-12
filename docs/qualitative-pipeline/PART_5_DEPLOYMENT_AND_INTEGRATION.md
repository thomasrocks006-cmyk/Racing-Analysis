# Qualitative Pipeline Architecture - Part 5: Deployment & Integration
**Created:** November 9, 2025
**Status:** Production-Ready Design
**Purpose:** Production deployment and fusion model integration

**Related Documents:**
- Part 1: Overview & Categories 1-8
- Part 2: Categories 9-17
- Part 3: LLM Chain & Synthesis
- Part 4: Integration Matrices A, B, C
- Quantitative Pipeline (Parts 1-3)
- FUSION_MODEL_ARCHITECTURE.md

---

## 📋 Table of Contents

1. [Output Format for Fusion](#output-format)
2. [Source Hierarchy & Scraping](#sources)
3. [API Endpoints](#api)
4. [Deployment Architecture](#deployment)
5. [Monitoring & Quality](#monitoring)

---

## 📤 1. Output Format for Fusion Model {#output-format}

### **Qualitative Pipeline Output Schema**

```python
QUALITATIVE_OUTPUT_SCHEMA = {
    "race_id": "string (FLE_20251109_R7)",
    "horse_id": "string",
    "horse_name": "string",

    # Likelihood Ratios by category group
    "lr_form_fitness": "float (0.50-1.50)",    # Categories 1-3
    "lr_conditions": "float (0.50-1.50)",      # Categories 4-7
    "lr_tactics": "float (0.50-1.50)",         # Categories 8-14
    "lr_context": "float (0.50-1.50)",         # Categories 15-17

    # Combined LR (multiplication)
    "lr_product": "float (0.25-4.0)",
    "lr_product_adjusted": "float (after integration matrices)",

    # Confidence & reasoning
    "overall_confidence": "float (0-1)",
    "reasoning": {
        "form_fitness": "string",
        "conditions": "string",
        "tactics": "string",
        "context": "string",
        "synthesis": "string"
    },

    # Key factors
    "key_strengths": ["string"],          # Top 3-5 positives
    "key_concerns": ["string"],           # Top 3-5 negatives
    "race_narrative": "string (150-300 chars)",

    # Integration matrix outputs
    "matrix_adjustments": {
        "matrix_a_total": "float",
        "matrix_b_total": "float",
        "matrix_c_total": "float"
    },

    # Category-level details (for audit trail)
    "category_lrs": {
        "1": "float",  # Race Metadata
        "2": "float",  # Race Type & Class
        # ... up to 17
    },

    # Source provenance
    "sources_count": "int (20-40)",
    "sources_official": "int",
    "sources_expert": "int",
    "sources_news": "int",
    "top_sources": [
        {
            "url": "string",
            "type": "official|expert|news|social",
            "claims_count": "int",
            "quality_score": "float (0-1)"
        }
    ],

    # Pipeline metadata
    "model_chain": "Gemini Flash → GPT-5 → Claude Sonnet 4.5 → GPT-4o",
    "processing_time_seconds": "float (300-420s typical)",
    "cost_dollars": "float (0.62 typical)",
    "prediction_timestamp": "ISO 8601"
}
```

### **Python Output Class**

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class QualitativeOutput(BaseModel):
    """
    Structured output from qualitative pipeline for fusion model.
    """
    race_id: str
    horse_id: str
    horse_name: str

    # Likelihood Ratios
    lr_form_fitness: float = Field(ge=0.50, le=1.50)
    lr_conditions: float = Field(ge=0.50, le=1.50)
    lr_tactics: float = Field(ge=0.50, le=1.50)
    lr_context: float = Field(ge=0.50, le=1.50)
    lr_product: float = Field(ge=0.25, le=4.0)
    lr_product_adjusted: float = Field(ge=0.25, le=4.0)

    # Confidence
    overall_confidence: float = Field(ge=0.0, le=1.0)

    # Reasoning
    reasoning: Dict[str, str]
    key_strengths: List[str]
    key_concerns: List[str]
    race_narrative: str = Field(max_length=300)

    # Integration matrices
    matrix_adjustments: Dict[str, float]
    category_lrs: Dict[str, float]

    # Provenance
    sources_count: int
    sources_official: int
    sources_expert: int
    top_sources: List[Dict]

    # Metadata
    model_chain: str
    processing_time_seconds: float
    cost_dollars: float
    prediction_timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "race_id": "FLE_20251109_R7",
                "horse_id": "12345",
                "horse_name": "Nature Strip",
                "lr_form_fitness": 1.18,
                "lr_conditions": 0.92,
                "lr_tactics": 1.35,
                "lr_context": 1.08,
                "lr_product": 1.60,
                "lr_product_adjusted": 1.68,
                "overall_confidence": 0.78
            }
        }
```

---

## 🌐 2. Source Hierarchy & Scraping {#sources}

### **Source Quality Tiers**

| Tier | Sources | Access | Quality | Priority |
|------|---------|--------|---------|----------|
| **1 (Official)** | Stewards reports, Barrier trials, Official sectionals | Selenium auth | 0.95-1.0 | HIGH |
| **2 (Expert)** | Racing.com, Punters.com.au, Racenet | API/scraping | 0.75-0.90 | HIGH |
| **3 (News)** | Herald Sun, Racing Post, ATR | RSS/scraping | 0.60-0.75 | MEDIUM |
| **4 (Social)** | Trainer/jockey Twitter, Stables | API | 0.50-0.70 | LOW |

### **Scraping Implementation**

```python
import asyncio
from playwright.async_api import async_playwright
import httpx
from bs4 import BeautifulSoup

class RacingDataScraper:
    """
    Asynchronous scraping with authentication for official sources.
    """

    def __init__(self):
        self.rate_limits = {
            'racing.com': 2.0,      # seconds between requests
            'punters.com.au': 2.0,
            'racenet.com.au': 1.5,
            'stewards.racing.com': 3.0
        }
        self.last_request_time = {}

    async def scrape_all_sources(
        self,
        queries: List[dict],
        use_auth: bool = True
    ) -> List[dict]:
        """
        Scrape all sources in parallel with rate limiting.

        Args:
            queries: List from planning stage
            use_auth: Use Selenium for authenticated scraping

        Returns:
            List of {url, content, status}
        """
        results = []

        # Group queries by priority
        official = [q for q in queries if q['source_type'] == 'official']
        expert = [q for q in queries if q['source_type'] == 'expert']
        other = [q for q in queries if q['source_type'] in ['news', 'social']]

        # Scrape official sources first (sequential with auth)
        if use_auth:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()

                # Load cookies (pre-authenticated)
                await context.add_cookies(self._load_auth_cookies())

                for query in official:
                    result = await self._scrape_with_playwright(context, query)
                    results.append(result)

                await browser.close()

        # Scrape expert/news/social in parallel (no auth)
        tasks = []
        for query in expert + other:
            tasks.append(self._scrape_with_httpx(query))

        expert_results = await asyncio.gather(*tasks)
        results.extend(expert_results)

        return results

    async def _scrape_with_playwright(
        self,
        context,
        query: dict
    ) -> dict:
        """
        Scrape with Playwright (for JS-heavy sites).
        """
        page = await context.new_page()

        try:
            await page.goto(query['url'], timeout=10000)
            await page.wait_for_load_state('networkidle')

            content = await page.content()

            return {
                'url': query['url'],
                'content': content,
                'status': 'success',
                'category': query['category']
            }

        except Exception as e:
            return {
                'url': query['url'],
                'content': '',
                'status': 'failed',
                'error': str(e),
                'category': query['category']
            }

        finally:
            await page.close()

    async def _scrape_with_httpx(self, query: dict) -> dict:
        """
        Scrape with httpx (faster for static content).
        """
        # Rate limiting
        domain = self._get_domain(query['url'])
        await self._rate_limit(domain)

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(query['url'])
                response.raise_for_status()

                return {
                    'url': query['url'],
                    'content': response.text,
                    'status': 'success',
                    'category': query['category']
                }

            except Exception as e:
                return {
                    'url': query['url'],
                    'content': '',
                    'status': 'failed',
                    'error': str(e),
                    'category': query['category']
                }

    async def _rate_limit(self, domain: str):
        """
        Enforce rate limiting per domain.
        """
        if domain in self.rate_limits:
            if domain in self.last_request_time:
                elapsed = asyncio.get_event_loop().time() - self.last_request_time[domain]
                wait_time = self.rate_limits[domain] - elapsed
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

            self.last_request_time[domain] = asyncio.get_event_loop().time()

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        return urlparse(url).netloc

    def _load_auth_cookies(self) -> List[dict]:
        """
        Load pre-authenticated cookies for official sites.

        These would be generated once via manual login and stored.
        """
        import json
        with open('config/racing_auth_cookies.json', 'r') as f:
            return json.load(f)
```

---

## 🚀 3. API Endpoints {#api}

### **FastAPI Implementation**

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Qualitative Racing Analysis API", version="1.0.0")

# Initialize pipeline
qualitative_pipeline = QualitativePipeline()

class RaceAnalysisRequest(BaseModel):
    """Request schema for qualitative analysis."""
    race_id: str
    track: str
    distance: int
    going: int
    horses: List[dict]
    depth: str = "standard"  # "standard" or "deep"

class QualitativeResponse(BaseModel):
    """Response schema."""
    race_id: str
    analyses: List[QualitativeOutput]
    metadata: dict

@app.post("/api/v1/analyze", response_model=QualitativeResponse)
async def analyze_race(request: RaceAnalysisRequest, background_tasks: BackgroundTasks):
    """
    **Qualitative Analysis Endpoint**

    Generate likelihood ratios for all horses in a race using:
    - Categories 1-17 from Master Taxonomy
    - GPT-5 deep reasoning
    - Claude Sonnet 4.5 synthesis
    - Gemini Flash extraction
    - Integration Matrices A, B, C

    Returns:
        Likelihood ratios ready for fusion with quantitative base probabilities
    """
    try:
        analyses = []

        for horse in request.horses:
            # Run qualitative pipeline
            output = await qualitative_pipeline.analyze_horse(
                race=request.dict(),
                horse=horse,
                depth=request.depth
            )

            analyses.append(output)

            # Log to monitoring (async)
            background_tasks.add_task(
                log_analysis,
                output
            )

        return QualitativeResponse(
            race_id=request.race_id,
            analyses=analyses,
            metadata={
                'pipeline_version': '1.0.0',
                'total_horses': len(analyses),
                'avg_processing_time': sum(a.processing_time_seconds for a in analyses) / len(analyses),
                'total_cost': sum(a.cost_dollars for a in analyses)
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sources/{horse_id}")
async def get_horse_sources(horse_id: str, race_id: str):
    """
    **Source Inspection Endpoint**

    Get all sources scraped for a specific horse (debugging).
    """
    try:
        sources = qualitative_pipeline.get_sources(race_id, horse_id)

        return {
            'horse_id': horse_id,
            'race_id': race_id,
            'sources': sources,
            'total_count': len(sources)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """
    **Health Check**

    Verify all models and services are available.
    """
    return {
        'status': 'healthy',
        'models': {
            'gemini_flash': qualitative_pipeline.check_gemini(),
            'gpt5': qualitative_pipeline.check_gpt5(),
            'claude_sonnet': qualitative_pipeline.check_claude(),
            'gpt4o': qualitative_pipeline.check_gpt4o()
        },
        'scraping': qualitative_pipeline.check_scraping(),
        'version': '1.0.0'
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

---

## 🏗️ 4. Deployment Architecture {#deployment}

### **Infrastructure Design**

```
┌─────────────────────────────────────────────────────────────┐
│                     Production System                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Streamlit  │◄────────│   FastAPI    │                 │
│  │   Dashboard  │         │   Backend    │                 │
│  │  (Port 8501) │         │  (Port 8000) │                 │
│  └──────────────┘         └───────┬──────┘                 │
│         │                          │                        │
│         │                          ▼                        │
│         │          ┌───────────────────────────┐           │
│         │          │  Qualitative API (8002)   │           │
│         │          │  - Scraping               │           │
│         │          │  - Gemini Flash           │           │
│         │          │  - GPT-5                  │           │
│         │          │  - Claude Sonnet          │           │
│         │          │  - GPT-4o                 │           │
│         │          └───────────┬───────────────┘           │
│         │                      │                            │
│         │          ┌───────────────────────────┐           │
│         │          │  Quantitative API (8001)  │           │
│         │          │  - CatBoost/LightGBM      │           │
│         │          │  - Feature engineering    │           │
│         │          │  - Calibration            │           │
│         │          └───────────┬───────────────┘           │
│         │                      │                            │
│         ▼                      ▼                            │
│  ┌──────────────────────────────────────┐                  │
│  │       Fusion Model (8000)            │                  │
│  │  - Bayesian LR integration           │                  │
│  │  - Field normalization               │                  │
│  │  - Final calibration                 │                  │
│  └───────────┬──────────────────────────┘                  │
│              │                                              │
│              ▼                                              │
│  ┌──────────────────────────────────────┐                  │
│  │          DuckDB Data Warehouse       │                  │
│  │  - Raw race data                     │                  │
│  │  - Scraped sources                   │                  │
│  │  - Qualitative claims                │                  │
│  │  - Quantitative features             │                  │
│  │  - Final predictions                 │                  │
│  └──────────────────────────────────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### **Docker Compose**

```yaml
version: '3.8'

services:
  qualitative_api:
    build:
      context: .
      dockerfile: Dockerfile.qualitative
    ports:
      - "8002:8002"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - PIPELINE_VERSION=1.0.0
    volumes:
      - ./config:/app/config:ro
      - ./data:/app/data
    depends_on:
      - duckdb
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  quantitative_api:
    build:
      context: .
      dockerfile: Dockerfile.quantitative
    ports:
      - "8001:8001"
    volumes:
      - ./models:/app/models:ro
      - ./data:/app/data
    depends_on:
      - duckdb

  fusion_model:
    build:
      context: .
      dockerfile: Dockerfile.fusion
    ports:
      - "8000:8000"
    depends_on:
      - qualitative_api
      - quantitative_api

  dashboard:
    image: streamlit:latest
    ports:
      - "8501:8501"
    volumes:
      - ./dashboard:/app
    depends_on:
      - fusion_model

  duckdb:
    image: duckdb/duckdb:latest
    volumes:
      - ./data/warehouse:/data
```

---

## 📊 5. Monitoring & Quality Assurance {#monitoring}

### **Quality Metrics**

```python
class QualitativeMonitor:
    """
    Monitor qualitative pipeline quality and performance.
    """

    def __init__(self, db_path: str = 'data/qual_monitoring.duckdb'):
        self.db = duckdb.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        """Create monitoring tables."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS qualitative_analyses (
                analysis_id VARCHAR PRIMARY KEY,
                race_id VARCHAR,
                horse_id VARCHAR,
                timestamp TIMESTAMP,
                lr_product FLOAT,
                confidence FLOAT,
                sources_count INT,
                sources_official INT,
                processing_time FLOAT,
                cost_dollars FLOAT,
                model_chain VARCHAR
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS quality_flags (
                flag_id VARCHAR PRIMARY KEY,
                analysis_id VARCHAR,
                flag_type VARCHAR,  # 'hallucination', 'low_confidence', 'missing_sources'
                severity VARCHAR,   # 'low', 'medium', 'high'
                description TEXT,
                timestamp TIMESTAMP
            )
        """)

    def log_analysis(self, output: QualitativeOutput):
        """Log analysis to monitoring database."""
        self.db.execute("""
            INSERT INTO qualitative_analyses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            f"{output.race_id}_{output.horse_id}",
            output.race_id,
            output.horse_id,
            output.prediction_timestamp,
            output.lr_product_adjusted,
            output.overall_confidence,
            output.sources_count,
            output.sources_official,
            output.processing_time_seconds,
            output.cost_dollars,
            output.model_chain
        ])

    def flag_quality_issue(
        self,
        analysis_id: str,
        flag_type: str,
        severity: str,
        description: str
    ):
        """Flag a quality issue for review."""
        self.db.execute("""
            INSERT INTO quality_flags VALUES (?, ?, ?, ?, ?, ?)
        """, [
            f"{analysis_id}_{flag_type}_{datetime.now().isoformat()}",
            analysis_id,
            flag_type,
            severity,
            description,
            datetime.now()
        ])

    def get_daily_metrics(self, date: str) -> dict:
        """Calculate daily quality metrics."""
        metrics = self.db.execute("""
            SELECT
                COUNT(*) as total_analyses,
                AVG(lr_product) as avg_lr,
                AVG(confidence) as avg_confidence,
                AVG(sources_official) as avg_official_sources,
                AVG(processing_time) as avg_processing_time,
                SUM(cost_dollars) as total_cost
            FROM qualitative_analyses
            WHERE DATE(timestamp) = ?
        """, [date]).fetchone()

        flags = self.db.execute("""
            SELECT flag_type, COUNT(*) as count
            FROM quality_flags
            WHERE DATE(timestamp) = ?
            GROUP BY flag_type
        """, [date]).fetchall()

        return {
            'total_analyses': metrics[0],
            'avg_lr_product': metrics[1],
            'avg_confidence': metrics[2],
            'avg_official_sources': metrics[3],
            'avg_processing_time': metrics[4],
            'total_cost': metrics[5],
            'quality_flags': dict(flags)
        }

    def detect_hallucinations(self, output: QualitativeOutput) -> bool:
        """
        Detect potential hallucinations via cross-checking.

        Red flags:
        - Very high LR (>2.5) with low confidence (<0.60)
        - Strong claim with no official sources
        - Contradictory reasoning
        """
        hallucination_detected = False

        # Red flag 1: High LR, low confidence
        if output.lr_product_adjusted > 2.5 and output.overall_confidence < 0.60:
            self.flag_quality_issue(
                f"{output.race_id}_{output.horse_id}",
                'hallucination',
                'high',
                f"High LR ({output.lr_product_adjusted:.2f}) with low confidence ({output.overall_confidence:.2f})"
            )
            hallucination_detected = True

        # Red flag 2: Strong positive but no official sources
        if output.lr_product_adjusted > 1.8 and output.sources_official == 0:
            self.flag_quality_issue(
                f"{output.race_id}_{output.horse_id}",
                'missing_sources',
                'medium',
                f"Strong positive LR ({output.lr_product_adjusted:.2f}) with 0 official sources"
            )
            hallucination_detected = True

        return hallucination_detected
```

---

## 🎯 Success Criteria

### **Production Readiness Checklist**

- [x] Category-level LR generation (Categories 1-17)
- [x] Multi-stage LLM pipeline (Gemini → GPT-5 → Claude → GPT-4o)
- [x] Integration Matrices A, B, C implementation
- [x] Source scraping (official + expert + news + social)
- [x] Output format for fusion model
- [x] API endpoints with health checks
- [x] Deployment architecture (Docker Compose)
- [x] Monitoring & quality assurance
- [x] Hallucination detection

### **Performance Targets**

| Metric | Target | Production Threshold |
|--------|--------|---------------------|
| Processing Time | 5-7 min/race | <10 min |
| Cost per Race | $0.62 | <$1.00 |
| Official Sources | 8-12 | >5 |
| Overall Confidence | >0.70 | >0.60 |
| LR Product Range | 0.50-2.50 | 0.30-3.50 |
| Hallucination Rate | <2% | <5% |

### **Integration Success**

- [ ] Qualitative LRs correctly formatted for fusion model
- [ ] Integration Matrix C signals properly extracted
- [ ] Chemistry × Quantitative bridge functional
- [ ] Distance × Pedigree validation working
- [ ] Weather × Going suit confirmation operational
- [ ] API uptime >99% over 30 days

---

## 🔄 Integration with Quantitative Pipeline

```python
async def full_prediction_pipeline(race: dict) -> dict:
    """
    Complete prediction: Qualitative + Quantitative + Fusion.
    """
    # Step 1: Run qualitative pipeline (parallel per horse)
    qual_tasks = []
    for horse in race['horses']:
        task = qualitative_pipeline.analyze_horse(race, horse)
        qual_tasks.append(task)

    qual_outputs = await asyncio.gather(*qual_tasks)

    # Step 2: Run quantitative pipeline (parallel per horse)
    quant_tasks = []
    for horse in race['horses']:
        task = quantitative_pipeline.predict(race, horse)
        quant_tasks.append(task)

    quant_outputs = await asyncio.gather(*quant_tasks)

    # Step 3: Fusion model (Bayesian integration)
    final_predictions = []
    for qual, quant in zip(qual_outputs, quant_outputs):
        fused = fusion_model.integrate(qual, quant)
        final_predictions.append(fused)

    # Step 4: Field normalization
    final_predictions = fusion_model.normalize_field(final_predictions)

    return {
        'race_id': race['race_id'],
        'predictions': final_predictions,
        'metadata': {
            'qualitative_avg_lr': sum(q.lr_product_adjusted for q in qual_outputs) / len(qual_outputs),
            'quantitative_avg_prob': sum(q.win_prob_base for q in quant_outputs) / len(quant_outputs),
            'total_processing_time': sum(q.processing_time_seconds for q in qual_outputs) + sum(q.processing_time_seconds for q in quant_outputs),
            'total_cost': sum(q.cost_dollars for q in qual_outputs) + sum(q.cost_dollars for q in quant_outputs)
        }
    }
```

---

**End of Part 5 - Qualitative Pipeline Complete**

**Next Steps:**
1. Implement Fusion Model Architecture (Bayesian LR → Base Probability integration)
2. Update Phase 1 Roadmap with pipeline timing
3. Begin implementation (Week 1: Data warehouse + scraping infrastructure)

**Total Qualitative Pipeline Documentation: ~4,800 lines across 5 parts**
