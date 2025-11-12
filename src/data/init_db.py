"""
Database initialization script for Racing Analysis DuckDB database.

This script creates the DuckDB database and loads the schema from schema.sql.
Run this script once to set up the database before data ingestion.

Usage:
    python src/data/init_db.py
    python src/data/init_db.py --force  # Force recreate if exists
    python src/data/init_db.py --verify-only  # Only verify schema
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import duckdb

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCHEMA_PATH = PROJECT_ROOT / "src" / "data" / "schema.sql"
DB_PATH = PROJECT_ROOT / "data" / "racing.duckdb"


def load_schema(schema_path: Path = SCHEMA_PATH) -> str:
    """Load SQL schema from file."""
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    logger.info(f"Loading schema from {schema_path}")
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    return schema_sql


def create_database(
    db_path: Path = DB_PATH, schema_path: Path = SCHEMA_PATH, force: bool = False
) -> None:
    """
    Create DuckDB database and initialize schema.

    Args:
        db_path: Path to DuckDB database file
        schema_path: Path to SQL schema file
        force: If True, delete existing database before creating
    """
    # Create data directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if database exists
    if db_path.exists():
        if force:
            logger.warning(f"Force flag set. Deleting existing database: {db_path}")
            db_path.unlink()
        else:
            logger.error(
                f"Database already exists: {db_path}. Use --force to recreate."
            )
            raise FileExistsError(
                f"Database already exists: {db_path}. Use --force to recreate."
            )

    # Load schema
    schema_sql = load_schema(schema_path)

    # Create database and execute schema
    logger.info(f"Creating database at {db_path}")
    con = duckdb.connect(str(db_path))

    try:
        # Execute schema (split by semicolon for multiple statements)
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement:  # Skip empty statements
                logger.debug(f"Executing: {statement[:50]}...")
                con.execute(statement)

        con.commit()
        logger.info("Schema loaded successfully")

        # Verify schema
        verify_schema(con)

    except Exception as e:
        logger.error(f"Error creating database: {e}")
        con.close()
        # Clean up failed database
        if db_path.exists():
            db_path.unlink()
        raise

    finally:
        con.close()

    logger.info(f"Database created successfully at {db_path}")


def verify_schema(con: duckdb.DuckDBPyConnection | None = None) -> dict:
    """
    Verify database schema is complete.

    Args:
        con: DuckDB connection (if None, will connect to default DB_PATH)

    Returns:
        dict with verification results
    """
    should_close = False
    if con is None:
        if not DB_PATH.exists():
            raise FileNotFoundError(f"Database not found: {DB_PATH}")
        con = duckdb.connect(str(DB_PATH))
        should_close = True

    try:
        # Expected tables
        expected_tables = {
            "races",
            "horses",
            "jockeys",
            "trainers",
            "runs",
            "results",
            "market_odds",
            "stewards",
            "gear",
        }

        # Expected views
        expected_views = {
            "v_race_card",
            "v_race_results",
            "v_incomplete_races",
            "v_incomplete_runs",
        }

        # Expected indexes (partial list - critical ones)
        expected_indexes = {
            "idx_races_date",
            "idx_races_venue",
            "idx_runs_horse_id",
            "idx_runs_race_id",
            "idx_results_position",
        }

        # Check tables
        tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' AND table_type = 'BASE TABLE'"
        actual_tables = {row[0] for row in con.execute(tables_query).fetchall()}

        # Check views
        views_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' AND table_type = 'VIEW'"
        actual_views = {row[0] for row in con.execute(views_query).fetchall()}

        # Check indexes (DuckDB-specific query)
        indexes_query = "SELECT index_name FROM duckdb_indexes()"
        actual_indexes = {row[0] for row in con.execute(indexes_query).fetchall()}

        # Verify
        missing_tables = expected_tables - actual_tables
        missing_views = expected_views - actual_views
        missing_indexes = expected_indexes - actual_indexes

        # Log results
        logger.info("Schema Verification Results:")
        logger.info(f"  Tables: {len(actual_tables)}/{len(expected_tables)}")
        if missing_tables:
            logger.warning(f"  Missing tables: {missing_tables}")
        else:
            logger.info(f"  ✓ All expected tables present: {actual_tables}")

        logger.info(f"  Views: {len(actual_views)}/{len(expected_views)}")
        if missing_views:
            logger.warning(f"  Missing views: {missing_views}")
        else:
            logger.info(f"  ✓ All expected views present: {actual_views}")

        logger.info(f"  Indexes: {len(actual_indexes)} found")
        if missing_indexes:
            logger.warning(f"  Missing indexes: {missing_indexes}")
        else:
            logger.info(
                f"  ✓ All critical indexes present (checked {len(expected_indexes)})"
            )

        # Return verification results
        is_valid = (
            len(missing_tables) == 0
            and len(missing_views) == 0
            and len(missing_indexes) == 0
        )

        results = {
            "valid": is_valid,
            "tables": {
                "expected": expected_tables,
                "actual": actual_tables,
                "missing": missing_tables,
            },
            "views": {
                "expected": expected_views,
                "actual": actual_views,
                "missing": missing_views,
            },
            "indexes": {
                "expected": expected_indexes,
                "actual": actual_indexes,
                "missing": missing_indexes,
            },
        }

        if is_valid:
            logger.info("✓ Schema verification PASSED")
        else:
            logger.error("✗ Schema verification FAILED - see warnings above")

        return results

    finally:
        if should_close:
            con.close()


def main():
    """Main entry point for database initialization."""
    parser = argparse.ArgumentParser(description="Initialize Racing Analysis database")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recreate database if it already exists",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing database schema (don't create)",
    )
    parser.add_argument(
        "--db-path", type=Path, default=DB_PATH, help="Path to database file"
    )
    parser.add_argument(
        "--schema-path", type=Path, default=SCHEMA_PATH, help="Path to schema SQL file"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Set debug logging if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)

    try:
        if args.verify_only:
            # Verify existing database
            logger.info("Verifying database schema...")
            verify_schema()
        else:
            # Create database
            logger.info("Initializing database...")
            create_database(
                db_path=args.db_path, schema_path=args.schema_path, force=args.force
            )

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
