#!/usr/bin/env python
"""Database inspection script for development."""

import os

from sqlalchemy import create_engine, inspect, text


def main():
    """Inspect database schema and data."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable is not set")
        return

    engine = create_engine(database_url)
    inspector = inspect(engine)

    # Display tables
    print("=== Database Tables ===\n")
    tables = inspector.get_table_names()

    for table in tables:
        print(f"📋 {table}")
        columns = inspector.get_columns(table)
        for col in columns:
            nullable = "NULL" if col.get("nullable") else "NOT NULL"
            print(f"  ├─ {col['name']}: {col['type']} ({nullable})")

        # Show indexes
        indexes = inspector.get_indexes(table)
        if indexes:
            print("  └─ Indexes:")
            for idx in indexes:
                print(f"     └─ {idx['name']}: {idx['column_names']}")
        print()

    # Display data samples
    print("=== Data Samples ===\n")
    with engine.connect() as conn:
        for table in tables:
            if table == "alembic_version":
                continue

            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"📊 {table}: {count} rows")

            if count is not None and count > 0:
                result = conn.execute(text(f"SELECT * FROM {table} LIMIT 5"))
                rows = result.fetchall()
                for row in rows:
                    print(f"  └─ {row}")
            print()


if __name__ == "__main__":
    main()
