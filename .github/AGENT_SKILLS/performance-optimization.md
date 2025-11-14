# Agent Skill: Performance & Optimization

## Purpose

Diagnose, profile, and optimize system performance: identifying bottlenecks, measuring improvements, applying optimizations, and achieving performance targets with data-driven decisions.

## When to Use

- "Use performance-optimization skill: Optimize the scraper for speed"
- "Use performance-optimization skill: Profile this pipeline for bottlenecks"
- "Use performance-optimization skill: Improve model training speed"
- "Use performance-optimization skill: Optimize database queries"
- "Use performance-optimization skill: Benchmark and compare approaches"

## Typical Workflow

1. **Establish Baselines**
   - Define current performance metrics
   - Identify performance targets
   - Establish measurement methodology
   - Create reproducible test scenarios

2. **Profile & Identify Bottlenecks**
   - Use profilers (cProfile, memory_profiler, etc.)
   - Measure execution time at each stage
   - Identify hotspots and allocations
   - Find the Pareto principle (80/20) - where is 80% of time spent?

3. **Diagnose Root Causes**
   - Is it algorithmic complexity?
   - Is it I/O bound (network, disk)?
   - Is it memory pressure?
   - Is it contention or synchronization?
   - Is it garbage collection?

4. **Generate Optimization Strategies**
   - Algorithm improvements (reduce complexity)
   - Caching and memoization
   - Parallelization and async
   - Memory optimization
   - Database query optimization

5. **Implement & Measure**
   - Apply optimization incrementally
   - Measure improvement vs. baseline
   - Ensure correctness (tests still pass)
   - Calculate time/effort vs. gain ratio

6. **Document Trade-offs**
   - What changed?
   - What trade-offs were made?
   - What constraints are there?
   - When might this optimization break?

## Code Patterns for Performance

```python
import time
import cProfile
import pstats
from functools import wraps
from memory_profiler import profile

class PerformanceAnalyzer:
    """Profile and optimize code performance."""

    def __init__(self, func):
        self.func = func
        self.baseline = None
        self.profile_results = None

    def profile_execution(self, *args, **kwargs):
        """Profile function execution."""
        profiler = cProfile.Profile()
        profiler.enable()

        start = time.time()
        result = self.func(*args, **kwargs)
        elapsed = time.time() - start

        profiler.disable()
        self.profile_results = profiler

        return result, elapsed

    def report(self):
        """Generate performance report."""
        if not self.profile_results:
            return "No profiling data available"

        stats = pstats.Stats(self.profile_results)
        stats.sort_stats('cumulative')

        return stats.print_stats(10)  # Top 10 functions

# Measure different approaches
def benchmark_approaches(approaches, test_data, iterations=100):
    """Compare performance of different implementations."""
    results = {}

    for name, func in approaches.items():
        times = []
        for _ in range(iterations):
            start = time.time()
            func(test_data)
            times.append(time.time() - start)

        results[name] = {
            'min': min(times),
            'max': max(times),
            'avg': sum(times) / len(times),
            'total': sum(times),
        }

    return results

# Caching optimization pattern
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(param1, param2):
    """Cached expensive operation."""
    # computation here
    return result

# Parallel optimization pattern
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def parallelize_scraper(races, max_workers=4):
    """Parallel scraping with thread pool."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(scrape_single_race, races))
    return results

# Database query optimization
def optimized_query():
    """Optimized DuckDB query."""
    # Bad: Load all data then filter
    # all_races = conn.execute("SELECT * FROM races").fetchall()
    # filtered = [r for r in all_races if r['venue'] == 'flemington']

    # Good: Filter in database
    filtered = conn.execute("""
        SELECT * FROM races
        WHERE venue = 'flemington'
        LIMIT 1000
    """).fetchall()

    return filtered
```

## Performance Optimization Strategies

### Algorithmic Optimization

- Reduce Big O complexity (O(n²) → O(n log n))
- Eliminate redundant operations
- Apply dynamic programming
- Use better data structures

### I/O Optimization

- Batch requests (not individual API calls)
- Enable connection pooling
- Use async/await for concurrent I/O
- Compress data in transit
- Cache frequently accessed data

### Memory Optimization

- Use generators instead of loading all data
- Release large objects when done
- Use streaming for large files
- Profile memory usage
- Identify memory leaks

### Parallelization

- Use ThreadPoolExecutor for I/O-bound tasks
- Use ProcessPoolExecutor for CPU-bound tasks
- Identify parallelizable sections
- Manage thread/process overhead
- Watch for synchronization bottlenecks

### Caching Strategies

- Cache expensive computations
- Cache API responses
- Use Redis for distributed caching
- Implement cache invalidation strategy
- Monitor cache hit rates

## Common Optimization Tasks

### Profile Slow Function

- [ ] Get baseline timing
- [ ] Profile with cProfile
- [ ] Identify top 3 hotspots
- [ ] Measure their contribution
- [ ] Propose optimization for each

### Optimize Database Queries

- [ ] Review current query
- [ ] Add indexes where needed
- [ ] Reduce data transferred
- [ ] Use query plan analyzer
- [ ] Benchmark improvement

### Reduce Memory Usage

- [ ] Profile memory with memory_profiler
- [ ] Identify large allocations
- [ ] Convert to generators
- [ ] Stream large datasets
- [ ] Measure peak memory reduction

### Speed Up Scraper

- [ ] Profile scraping pipeline
- [ ] Identify bottleneck (API limit vs. parsing vs. storage)
- [ ] Parallelize where possible
- [ ] Cache responses
- [ ] Benchmark improvement

## Performance Metrics to Track

| Metric | Tool | Target |
|--------|------|--------|
| Execution Time | time, cProfile | < target_ms |
| Memory Usage | memory_profiler | < target_mb |
| CPU Usage | cProfile | < target_% |
| I/O Operations | requests hooks | minimize |
| Cache Hit Rate | custom tracking | > 80% |
| Latency (p50, p95, p99) | timing | < target_ms |

## Success Criteria

- ✅ Performance baseline established and measured
- ✅ Bottlenecks identified with profiling data
- ✅ Root cause understood (algorithmic, I/O, memory, etc.)
- ✅ Optimization strategy proposed with trade-offs
- ✅ Implementation achieves target improvement
- ✅ Correctness verified (tests still pass)
- ✅ Regression prevented with performance benchmarks
- ✅ Trade-offs documented (e.g., memory vs. speed)
