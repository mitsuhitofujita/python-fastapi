#!/usr/bin/env python3
"""Reset test database script.

This script:
1. Drops all tables from the test database
2. Runs Alembic migrations from scratch
3. Verifies that tables were created successfully
"""

import os
import subprocess
import sys
from urllib.parse import urlparse

import psycopg2


def get_test_database_url():
    """Get test database URL from environment."""
    database_url = os.getenv("DATABASE_URL_TEST")
    if not database_url:
        print("❌ ERROR: DATABASE_URL_TEST environment variable is not set")
        sys.exit(1)
    return database_url


def drop_all_tables(database_url):
    """Drop all tables from the test database."""
    print("🗑️  Dropping all tables from test database...")

    try:
        result = urlparse(database_url)
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port,
            database=result.path[1:],
            user=result.username,
            password=result.password,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Get all table names from both main and public schemas
        cursor.execute(
            "SELECT table_schema, table_name FROM information_schema.tables "
            "WHERE table_schema IN ('main', 'public') AND table_type = 'BASE TABLE';"
        )
        tables = cursor.fetchall()

        if not tables:
            print("   ℹ️  No tables to drop")
        else:
            # Drop all tables with CASCADE
            for table in tables:
                schema_name = table[0]
                table_name = table[1]
                print(f"   Dropping table: {schema_name}.{table_name}")
                cursor.execute(f'DROP TABLE IF EXISTS "{schema_name}"."{table_name}" CASCADE;')

            print(f"   ✅ Dropped {len(tables)} table(s)")

        # Also drop alembic_version table if exists (in public schema)
        cursor.execute("DROP TABLE IF EXISTS public.alembic_version CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS main.alembic_version CASCADE;")
        print("   ✅ Dropped alembic_version table")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Failed to drop tables: {e!s}")
        return False


def run_migrations():
    """Run Alembic migrations."""
    print("\n🔄 Running Alembic migrations...")

    try:
        # Set environment variable for Alembic
        env = os.environ.copy()
        env["DATABASE_URL"] = env.get("DATABASE_URL_TEST")

        # Run alembic upgrade head
        result = subprocess.run(
            ["uv", "run", "alembic", "upgrade", "head"],
            cwd="/workspace/app/api",
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        print("✅ Migrations completed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed:")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e!s}")
        return False


def verify_tables(database_url):
    """Verify that tables were created successfully."""
    print("\n🔍 Verifying tables...")

    try:
        result = urlparse(database_url)
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port,
            database=result.path[1:],
            user=result.username,
            password=result.password,
        )
        cursor = conn.cursor()

        # Get all table names from main and public schemas
        cursor.execute(
            "SELECT table_schema, table_name FROM information_schema.tables "
            "WHERE table_schema IN ('main', 'public') AND table_type = 'BASE TABLE' "
            "ORDER BY table_schema, table_name;"
        )
        tables = cursor.fetchall()

        if tables:
            print(f"✅ Found {len(tables)} table(s):")
            for table in tables:
                print(f"   - {table[0]}.{table[1]}")
        else:
            print("❌ No tables found!")
            cursor.close()
            conn.close()
            return False

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Failed to verify tables: {e!s}")
        return False


def main():
    """Main execution function."""
    print("=" * 60)
    print("Test Database Reset Script")
    print("=" * 60)

    # Get database URL
    database_url = get_test_database_url()
    print(f"📌 DATABASE_URL_TEST: {database_url}\n")

    # Step 1: Drop all tables
    if not drop_all_tables(database_url):
        print("\n❌ Failed to reset test database")
        sys.exit(1)

    # Step 2: Run migrations
    if not run_migrations():
        print("\n❌ Failed to reset test database")
        sys.exit(1)

    # Step 3: Verify tables
    if not verify_tables(database_url):
        print("\n❌ Failed to reset test database")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ Test database reset completed successfully!")
    print("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()
