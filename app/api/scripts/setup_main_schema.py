#!/usr/bin/env python3
"""Setup main schema in existing databases."""

import sys

import psycopg2


def setup_schema(db_name, user, password):
    """Setup main schema in a database."""
    print(f"\n🔧 Setting up main schema in {db_name} database...")

    try:
        conn = psycopg2.connect(
            host="postgres",
            port=5432,
            database=db_name,
            user="app_local",
            password="app_local",
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Create main schema
        cursor.execute("CREATE SCHEMA IF NOT EXISTS main;")
        print(f"   ✅ Created main schema")

        # Grant privileges to user
        cursor.execute(f"GRANT ALL ON SCHEMA main TO {user};")
        print(f"   ✅ Granted schema privileges to {user}")

        # Set default search_path
        cursor.execute(f"ALTER USER {user} SET search_path TO main, public;")
        print(f"   ✅ Set default search_path for {user}")

        # Set default privileges
        cursor.execute(
            f"ALTER DEFAULT PRIVILEGES FOR USER {user} IN SCHEMA main "
            f"GRANT ALL ON TABLES TO {user};"
        )
        cursor.execute(
            f"ALTER DEFAULT PRIVILEGES FOR USER {user} IN SCHEMA main "
            f"GRANT ALL ON SEQUENCES TO {user};"
        )
        print(f"   ✅ Set default privileges for {user}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"   ❌ Failed: {e!s}")
        return False


def main():
    """Main execution function."""
    print("=" * 60)
    print("Setup Main Schema Script")
    print("=" * 60)

    success = True

    # Setup main schema in app_local database
    if not setup_schema("app_local", "app_local", "app_local"):
        success = False

    # Setup main schema in app_test database
    if not setup_schema("app_test", "app_test", "app_test"):
        success = False

    if success:
        print("\n" + "=" * 60)
        print("✅ Main schema setup completed successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Main schema setup failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
