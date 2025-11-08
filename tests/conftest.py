"""Test configuration and fixtures"""

import pytest
import tempfile
from pathlib import Path
import duckdb


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_db(temp_dir):
    """Create test database"""
    db_path = temp_dir / "test.duckdb"
    conn = duckdb.connect(str(db_path))
    
    # Create minimal schema for testing
    conn.execute("""
        CREATE TABLE races (
            race_id VARCHAR PRIMARY KEY,
            venue_code VARCHAR,
            race_date DATE,
            distance INTEGER
        )
    """)
    
    conn.execute("""
        CREATE TABLE runs (
            run_id VARCHAR PRIMARY KEY,
            race_id VARCHAR,
            horse_id VARCHAR,
            finishing_position INTEGER
        )
    """)
    
    yield conn
    conn.close()


@pytest.fixture
def sample_predictions():
    """Sample prediction data for testing metrics"""
    import numpy as np
    return {
        "y_true": np.array([1, 0, 0, 1, 1, 0, 1, 0, 0, 1]),
        "y_prob": np.array([0.8, 0.2, 0.3, 0.7, 0.9, 0.1, 0.6, 0.4, 0.2, 0.75]),
    }
