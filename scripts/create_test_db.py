#!/usr/bin/env python3
"""Script to create test database.

This script uses psycopg2 (sync) to create the test database
because it requires AUTOCOMMIT mode for CREATE DATABASE.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_test_database():
    """Create test database if it doesn't exist."""
    # Connect to app_local database to create app_local_test
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        user="app_local",
        password="app_local",
        database="app_local",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()

    # Check if database exists
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = 'app_local_test'"
    )
    exists = cursor.fetchone()

    if not exists:
        # Create database
        cursor.execute("CREATE DATABASE app_local_test")
        print("✓ Test database 'app_local_test' created")
    else:
        print("✓ Test database 'app_local_test' already exists")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    create_test_database()
