#!/usr/bin/env python3
"""Fix test database permissions script."""

import sys

import psycopg2


def fix_test_db_permissions():
    """Grant necessary permissions to app_test user on app_test database."""
    print("🔧 Fixing test database permissions...")

    try:
        # Connect as app_local user (has superuser-like privileges)
        conn = psycopg2.connect(
            host="postgres",
            port=5432,
            database="app_test",
            user="app_local",
            password="app_local",
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print("   Granting permissions to app_test user...")

        # Grant all privileges on database
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE app_test TO app_test;")
        print("   ✅ Granted database privileges")

        # Grant usage on public schema
        cursor.execute("GRANT USAGE ON SCHEMA public TO app_test;")
        print("   ✅ Granted schema usage")

        # Grant create on public schema
        cursor.execute("GRANT CREATE ON SCHEMA public TO app_test;")
        print("   ✅ Granted schema create")

        # Grant all on all tables in public schema (if any exist)
        cursor.execute(
            "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_test;"
        )
        print("   ✅ Granted table privileges")

        # Grant all on all sequences in public schema (if any exist)
        cursor.execute(
            "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_test;"
        )
        print("   ✅ Granted sequence privileges")

        # Set default privileges for future tables
        cursor.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            "GRANT ALL ON TABLES TO app_test;"
        )
        print("   ✅ Set default table privileges")

        # Set default privileges for future sequences
        cursor.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            "GRANT ALL ON SEQUENCES TO app_test;"
        )
        print("   ✅ Set default sequence privileges")

        cursor.close()
        conn.close()

        print("\n✅ Test database permissions fixed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Failed to fix permissions: {e!s}")
        return False


if __name__ == "__main__":
    success = fix_test_db_permissions()
    sys.exit(0 if success else 1)
