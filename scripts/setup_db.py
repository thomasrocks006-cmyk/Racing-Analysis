#!/usr/bin/env python3
"""
Database setup script for Racing Analysis system.
Creates DuckDB database with schema from configs/database.yml
"""

import duckdb
import yaml
from pathlib import Path
from datetime import datetime

# Paths
ROOT_DIR = Path(__file__).parent.parent
CONFIG_PATH = ROOT_DIR / "configs" / "database.yml"
DB_PATH = ROOT_DIR / "data" / "racing.duckdb"


def load_schema():
    """Load database schema from YAML config"""
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def create_tables(conn, schema):
    """Create all tables defined in schema"""
    print("📋 Creating tables...")
    
    for table_name, table_def in schema.get("tables", {}).items():
        print(f"  - Creating table: {table_name}")
        
        # Build CREATE TABLE statement
        columns = []
        for col_name, col_type in table_def["columns"].items():
            columns.append(f"{col_name} {col_type}")
        
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns)}
            )
        """
        
        conn.execute(create_sql)
        
        # Create indexes
        for index_def in table_def.get("indexes", []):
            try:
                conn.execute(f"CREATE INDEX IF NOT EXISTS {index_def}")
            except Exception as e:
                print(f"    ⚠️  Warning: Could not create index: {e}")
    
    print("✓ Tables created")


def create_views(conn, schema):
    """Create all views defined in schema"""
    print("\n📊 Creating views...")
    
    for view_name, view_def in schema.get("views", {}).items():
        print(f"  - Creating view: {view_name}")
        
        create_sql = f"""
            CREATE OR REPLACE VIEW {view_name} AS
            {view_def['query']}
        """
        
        try:
            conn.execute(create_sql)
        except Exception as e:
            print(f"    ⚠️  Warning: Could not create view: {e}")
    
    print("✓ Views created")


def initialize_metadata(conn):
    """Insert initial metadata records"""
    print("\n🔧 Initializing metadata...")
    
    # Create initial feature version
    conn.execute("""
        INSERT INTO feature_versions (version_id, version_name, description, feature_list, created_at, active)
        VALUES (
            'v0.1.0',
            'Initial Feature Set',
            'Baseline features: sectionals, ratings, trainer/jockey stats',
            '["sectionals", "distance_curve", "going_curve", "trainer_30d", "jockey_track"]',
            ?,
            TRUE
        )
        ON CONFLICT DO NOTHING
    """, [datetime.now()])
    
    print("  - Created initial feature version")
    print("✓ Metadata initialized")


def verify_setup(conn):
    """Verify database setup"""
    print("\n✅ Verifying setup...")
    
    # Check tables
    tables = conn.execute("SHOW TABLES").fetchall()
    print(f"  - Tables created: {len(tables)}")
    
    # Check views
    views = conn.execute("SELECT * FROM information_schema.views WHERE table_schema='main'").fetchall()
    print(f"  - Views created: {len(views)}")
    
    print("✓ Verification complete")


def main():
    """Main setup function"""
    print("=" * 60)
    print("🏇 Racing Analysis - Database Setup")
    print("=" * 60)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Config: {CONFIG_PATH}\n")
    
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Load schema
    print("📖 Loading schema...")
    schema = load_schema()
    print(f"✓ Loaded schema with {len(schema.get('tables', {}))} tables\n")
    
    # Connect to database
    print("🔌 Connecting to database...")
    conn = duckdb.connect(str(DB_PATH))
    print("✓ Connected\n")
    
    try:
        # Create tables
        create_tables(conn, schema)
        
        # Create views
        create_views(conn, schema)
        
        # Initialize metadata
        initialize_metadata(conn)
        
        # Verify
        verify_setup(conn)
        
        # Commit and close
        conn.commit()
        print("\n" + "=" * 60)
        print("✨ Database setup complete!")
        print("=" * 60)
        print(f"\nDatabase location: {DB_PATH}")
        print("You can now run: make status")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
