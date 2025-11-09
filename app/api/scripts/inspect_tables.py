#!/usr/bin/env python
"""Database table inspection script for verifying migrations."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect, text

from config import settings


def show_table_indexes(inspector, table: str) -> None:
    """Show only indexes for a specific table."""
    print(f"\n=== {table} INDEXES ===")
    indexes = inspector.get_indexes(table, schema="main")
    if indexes:
        for idx in indexes:
            unique = "UNIQUE" if idx.get("unique") else "INDEX"
            col_names = [col for col in idx["column_names"] if col is not None]
            cols = ", ".join(col_names)
            dialect_opts = idx.get("dialect_options", {})
            where_clause = dialect_opts.get("postgresql_where", "")
            where_info = f" WHERE {where_clause}" if where_clause else ""
            print(f"  {idx['name']} ({unique}): [{cols}]{where_info}")
    else:
        print("  (none)")


def show_table_details(inspector, table: str) -> None:
    """Show full details for a specific table."""
    print(f"\n{'=' * 80}")
    print(f"TABLE: main.{table}")
    print("=" * 80)

    # Columns
    print("\nCOLUMNS:")
    columns = inspector.get_columns(table, schema="main")
    for col in columns:
        nullable = "NULL" if col.get("nullable") else "NOT NULL"
        default = f", default={col.get('default')}" if col.get("default") else ""
        print(f"  - {col['name']}: {col['type']} ({nullable}{default})")

    # Indexes
    print("\nINDEXES:")
    indexes = inspector.get_indexes(table, schema="main")
    if indexes:
        for idx in indexes:
            unique = "UNIQUE" if idx.get("unique") else "INDEX"
            col_names = [col for col in idx["column_names"] if col is not None]
            cols = ", ".join(col_names)
            dialect_opts = idx.get("dialect_options", {})
            where_clause = dialect_opts.get("postgresql_where", "")
            where_info = f" WHERE {where_clause}" if where_clause else ""
            print(f"  - {idx['name']} ({unique}): [{cols}]{where_info}")
    else:
        print("  (none)")

    # Foreign Keys
    print("\nFOREIGN KEYS:")
    fks = inspector.get_foreign_keys(table, schema="main")
    if fks:
        for fk in fks:
            const_cols = ", ".join(fk["constrained_columns"])
            ref_schema = fk.get("referred_schema", "public")
            ref_table = fk["referred_table"]
            ref_cols = ", ".join(fk["referred_columns"])
            on_delete = fk.get("ondelete", "NO ACTION")
            print(
                f"  - {fk.get('name', '(unnamed)')}: [{const_cols}] -> {ref_schema}.{ref_table}[{ref_cols}] (ON DELETE: {on_delete})"
            )
    else:
        print("  (none)")

    # Primary Key
    print("\nPRIMARY KEY:")
    pk = inspector.get_pk_constraint(table, schema="main")
    if pk and pk.get("constrained_columns"):
        pk_cols = ", ".join(pk["constrained_columns"])
        print(f"  - {pk.get('name', '(unnamed)')}: [{pk_cols}]")
    else:
        print("  (none)")


def inspect_tables(table_name: str | None = None, show_indexes_only: bool = False):
    """Inspect and display all tables, columns, indexes, and constraints.

    Args:
        table_name: Optional table name to inspect. If None, inspect all tables.
        show_indexes_only: If True, only show indexes for specified table(s).
    """
    engine = create_engine(settings.database_url)
    inspector = inspect(engine)

    # Get all tables in main schema
    all_tables = inspector.get_table_names(schema="main")

    # Filter tables if table_name is specified
    if table_name:
        if table_name not in all_tables:
            print(f"Error: Table '{table_name}' not found in main schema")
            print(f"Available tables: {', '.join(all_tables)}")
            return
        tables = [table_name]
    else:
        tables = all_tables

    # Show summary header only if not showing indexes only
    if not show_indexes_only:
        print("=" * 80)
        print("DATABASE TABLES IN 'main' SCHEMA")
        print("=" * 80)
        print(f"\nTotal tables: {len(all_tables)}")
        print(f"Tables: {', '.join(all_tables)}\n")

    # Display detailed information for each table
    for table in sorted(tables):
        if show_indexes_only:
            show_table_indexes(inspector, table)
        else:
            show_table_details(inspector, table)

    # Check current migration version (skip if show_indexes_only)
    if not show_indexes_only:
        print(f"\n{'=' * 80}")
        print("ALEMBIC VERSION")
        print("=" * 80)

        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT version_num FROM main.alembic_version LIMIT 1")
            )
            version = result.scalar()
            print(f"\nCurrent migration version: {version}")

        print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Inspect database tables, columns, indexes, and constraints"
    )
    parser.add_argument(
        "-t",
        "--table",
        type=str,
        help="Specific table name to inspect (default: all tables)",
    )
    parser.add_argument(
        "-i",
        "--indexes-only",
        action="store_true",
        help="Show only indexes (useful for quick checks)",
    )

    args = parser.parse_args()
    inspect_tables(table_name=args.table, show_indexes_only=args.indexes_only)
