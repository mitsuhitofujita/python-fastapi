#!/usr/bin/env python3
"""Database connection check script."""

import os
import sys
from urllib.parse import urlparse

import psycopg2


def check_database_connection():
    """Check if database connection is successful using DATABASE_URL."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set")
        return False

    print(f"📌 DATABASE_URL: {database_url}")
    print("🔄 Attempting to connect to database...")

    try:
        # Parse DATABASE_URL
        result = urlparse(database_url)

        # Connect to database
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
        version = cursor.fetchone()[0]
        print("✅ Successfully connected to database!")
        print(f"📊 PostgreSQL version: {version}")

        # Test if we can list tables
        cursor.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public';"
        )
        tables = cursor.fetchall()
        if tables:
            print(f"\n📋 Found {len(tables)} table(s) in public schema:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("\n📋 No tables found in public schema")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print("❌ Failed to connect to database:")
        print(f"   Error: {e!s}")
        return False


if __name__ == "__main__":
    success = check_database_connection()
    sys.exit(0 if success else 1)
