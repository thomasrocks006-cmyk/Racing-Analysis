"""Integration tests for database operations"""

import pytest


def test_database_connection(test_db):
    """Test database connection"""
    result = test_db.execute("SELECT 1 as test").fetchone()
    assert result[0] == 1


def test_insert_race(test_db):
    """Test inserting a race"""
    test_db.execute("""
        INSERT INTO races (race_id, venue_code, race_date, distance)
        VALUES ('TEST-2025-11-09-R1', 'TEST', '2025-11-09', 1200)
    """)
    
    result = test_db.execute("SELECT COUNT(*) FROM races").fetchone()
    assert result[0] == 1


def test_query_races(test_db):
    """Test querying races"""
    # Insert test data
    test_db.execute("""
        INSERT INTO races (race_id, venue_code, race_date, distance)
        VALUES 
            ('TEST-2025-11-09-R1', 'TEST', '2025-11-09', 1200),
            ('TEST-2025-11-09-R2', 'TEST', '2025-11-09', 1400)
    """)
    
    result = test_db.execute("""
        SELECT COUNT(*) FROM races WHERE venue_code = 'TEST'
    """).fetchone()
    
    assert result[0] == 2
