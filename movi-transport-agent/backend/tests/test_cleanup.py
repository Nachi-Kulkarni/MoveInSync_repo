"""
Database Cleanup Utility for Test Isolation

This script provides utilities to:
1. Clean up test-created entities before/after test runs
2. Reset database to pristine state
3. Maintain test data integrity

Usage:
    python tests/test_cleanup.py --mode [before|after|full]
"""

import sqlite3
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "database" / "transport.db"


class DatabaseCleanup:
    """Handles database cleanup for test isolation."""

    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path

    def clean_test_stops(self):
        """Remove test-created stops."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        test_stops = ['Odeon Circle', 'MG Road Metro']

        for stop_name in test_stops:
            cursor.execute("DELETE FROM stops WHERE name = ?", (stop_name,))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        print(f"✓ Cleaned {deleted} test stops")
        return deleted

    def clean_test_paths(self):
        """Remove test-created paths."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        test_paths = ['Tech-Loop', 'Metro-Route']

        for path_name in test_paths:
            cursor.execute("DELETE FROM paths WHERE path_name = ?", (path_name,))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        print(f"✓ Cleaned {deleted} test paths")
        return deleted

    def clean_test_routes(self):
        """Remove test-created routes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Routes created by tests (Path-1 at 08:30, Path-2 at 18:45)
        # These have specific patterns we can identify
        cursor.execute("""
            DELETE FROM routes
            WHERE route_id IN (
                SELECT route_id FROM routes
                WHERE path_id IN (1, 2)
                AND shift_time IN ('08:30:00', '18:45:00')
                AND created_at > datetime('now', '-1 hour')
            )
        """)

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        print(f"✓ Cleaned {deleted} test routes")
        return deleted

    def clean_test_deployments(self):
        """Remove test-created vehicle deployments."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clean deployments created in last hour (test artifacts)
        cursor.execute("""
            DELETE FROM deployments
            WHERE deployed_at > datetime('now', '-1 hour')
        """)

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        print(f"✓ Cleaned {deleted} test deployments")
        return deleted

    def setup_test_data(self):
        """Setup required test data (e.g., assign vehicle to trip 6 for test #17)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if trip 6 exists
        cursor.execute("SELECT trip_id FROM daily_trips WHERE trip_id = 6")
        trip_exists = cursor.fetchone() is not None

        if trip_exists:
            # Check if trip 6 already has a vehicle
            cursor.execute("""
                SELECT deployment_id FROM deployments WHERE trip_id = 6
            """)
            existing_deployment = cursor.fetchone()

            if not existing_deployment:
                # Assign a specific vehicle that's NOT used in test cases
                # Test #9 uses KA-01-AB-1234 (vehicle_id=1)
                # Test #10 uses MH-12-GH-3456 (vehicle_id=4)
                # So we use vehicle_id=2 (KA-02-CD-5678) for trip 6
                # Also need driver_id (required field) - use driver_id=2
                cursor.execute("""
                    SELECT vehicle_id, license_plate FROM vehicles
                    WHERE vehicle_id = 2
                """)
                test_vehicle = cursor.fetchone()

                # Get an available driver (driver_id=2)
                cursor.execute("""
                    SELECT driver_id, name FROM drivers
                    WHERE driver_id = 2
                """)
                test_driver = cursor.fetchone()

                if test_vehicle and test_driver:
                    # Check if this vehicle is already assigned
                    cursor.execute("""
                        SELECT deployment_id FROM deployments WHERE vehicle_id = ?
                    """, (test_vehicle[0],))
                    already_assigned = cursor.fetchone()

                    if not already_assigned:
                        cursor.execute("""
                            INSERT INTO deployments (trip_id, vehicle_id, driver_id)
                            VALUES (6, ?, ?)
                        """, (test_vehicle[0], test_driver[0]))
                        conn.commit()
                        print(f"✓ Assigned vehicle {test_vehicle[0]} ({test_vehicle[1]}) and driver {test_driver[0]} ({test_driver[1]}) to trip 6")
                    else:
                        print(f"⚠ Vehicle {test_vehicle[0]} already assigned, skipping")
                else:
                    if not test_vehicle:
                        print("⚠ Vehicle ID 2 not found in database")
                    if not test_driver:
                        print("⚠ Driver ID 2 not found in database")
        else:
            print("⚠ Trip 6 not found")

        conn.close()

    def full_reset(self):
        """Full database reset - use with caution."""
        print("\n⚠️  FULL DATABASE RESET ⚠️")
        print("This will delete ALL test artifacts and reset to initial state.\n")

        confirm = input("Are you sure? Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return

        self.clean_test_stops()
        self.clean_test_paths()
        self.clean_test_routes()
        self.clean_test_deployments()
        print("\n✅ Database reset complete")

    def before_tests(self):
        """Run before test suite."""
        print("\n🧹 Cleaning database before tests...")
        self.clean_test_stops()
        self.clean_test_paths()
        self.clean_test_routes()
        self.clean_test_deployments()

        print("\n🔧 Setting up test data...")
        self.setup_test_data()

        print("\n✅ Database ready for testing")

    def after_tests(self):
        """Run after test suite."""
        print("\n🧹 Cleaning database after tests...")
        self.clean_test_stops()
        self.clean_test_paths()
        self.clean_test_routes()
        self.clean_test_deployments()
        print("\n✅ Cleanup complete")


def main():
    """CLI entry point."""
    cleanup = DatabaseCleanup()

    if len(sys.argv) < 2:
        print("Usage: python test_cleanup.py [before|after|full|setup]")
        print("  before - Clean and setup before tests")
        print("  after  - Clean up after tests")
        print("  full   - Full database reset (interactive)")
        print("  setup  - Just setup test data (e.g., assign vehicle to trip 6)")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "before":
        cleanup.before_tests()
    elif mode == "after":
        cleanup.after_tests()
    elif mode == "full":
        cleanup.full_reset()
    elif mode == "setup":
        print("\n🔧 Setting up test data...")
        cleanup.setup_test_data()
        print("\n✅ Test data setup complete")
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
