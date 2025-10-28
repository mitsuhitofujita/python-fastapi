#!/usr/bin/env python3
"""Test database connection check script."""

import sys
from urllib.parse import urlparse

import psycopg2

from config import settings


def check_test_database_connection():
    """Check if test database connection is successful using settings."""
    database_url = settings.database_url_test

    print(f"📌 DATABASE_URL_TEST: {database_url}")
    print("🔄 Attempting to connect to test database...")

    try:
        # Parse DATABASE_URL_TEST
        result = urlparse(database_url)

        # Connect to test database
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port,
            database=result.path[1:],  # Remove leading slash
            user=result.username,
            password=result.password,
        )

        # Test connection with version query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version_row = cursor.fetchone()
        if version_row:
            version = version_row[0]
            print("✅ Successfully connected to test database!")
            print(f"📊 PostgreSQL version: {version}")
        else:
            print("⚠️ Connected but could not retrieve version")

        # Test if we can list tables from main and public schemas
        cursor.execute(
            "SELECT table_schema, table_name FROM information_schema.tables "
            "WHERE table_schema IN ('main', 'public') "
            "ORDER BY table_schema, table_name;"
        )
        tables = cursor.fetchall()
        if tables:
            print(f"\n📋 Found {len(tables)} table(s):")
            for table in tables:
                print(f"   - {table[0]}.{table[1]}")
        else:
            print("\n📋 No tables found in main or public schema")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print("❌ Failed to connect to test database:")
        print(f"   Error: {e!s}")
        return False


if __name__ == "__main__":
    success = check_test_database_connection()
    sys.exit(0 if success else 1)
