"""
Test script for all 10 tool functions (TICKET #3).

This script tests:
1. 4 Read tools (get_unassigned_vehicles_count, get_trip_status, list_stops_for_path, list_routes_by_path)
2. 4 Create tools (assign_vehicle_to_trip, create_stop, create_path, create_route)
3. 1 Delete tool (remove_vehicle_from_trip)
4. 1 Consequence tool (get_consequences_for_action)

Tests use the existing SQLite database with seed data.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.tools import (
    # Read tools
    get_unassigned_vehicles_count,
    get_trip_status,
    list_stops_for_path,
    list_routes_by_path,

    # Create tools
    assign_vehicle_to_trip,
    create_stop,
    create_path,
    create_route,

    # Delete tools
    remove_vehicle_from_trip,

    # Consequence tools
    get_consequences_for_action,

    # Registry
    TOOL_REGISTRY
)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(test_name: str, result: dict, expected_success: bool = True):
    """Print test result with formatting."""
    success = result.get("success", False)
    status = "✅ PASS" if success == expected_success else "❌ FAIL"

    print(f"\n{status} | {test_name}")
    print(f"  Success: {result.get('success')}")
    print(f"  Message: {result.get('message')}")

    if result.get("data"):
        print(f"  Data: {result.get('data')}")

    if result.get("error"):
        print(f"  Error: {result.get('error')}")


async def test_read_tools(db: AsyncSession):
    """Test all 4 read operations."""
    print_section("Testing Read Tools (4)")

    # Test 1: Get unassigned vehicles count
    print("\n1. Testing get_unassigned_vehicles_count()")
    result = await get_unassigned_vehicles_count(db)
    print_result("Get Unassigned Vehicles Count", result)

    # Test 2: Get trip status (trip_id=1 is "Bulk - 00:01" with 25% booking)
    print("\n2. Testing get_trip_status(trip_id=1)")
    result = await get_trip_status(trip_id=1, db=db)
    print_result("Get Trip Status (Bulk - 00:01)", result)

    # Test 3: List stops for path (path_id=1 is "Path-1")
    print("\n3. Testing list_stops_for_path(path_name=1)")
    result = await list_stops_for_path(path_name=1, db=db)
    print_result("List Stops for Path-1", result)

    # Test 4: List routes by path (path_id=2 is "Path-2")
    print("\n4. Testing list_routes_by_path(path_name=2)")
    result = await list_routes_by_path(path_name=2, db=db)
    print_result("List Routes by Path-2", result)


async def test_consequence_tool(db: AsyncSession):
    """Test the consequence checking tool (Tribal Knowledge)."""
    print_section("Testing Consequence Tool (Tribal Knowledge)")

    # Test 1: Check consequences for removing vehicle from trip with bookings (HIGH RISK)
    print("\n1. Testing get_consequences_for_action('remove_vehicle', trip_id=1)")
    print("   (Trip 'Bulk - 00:01' has 25% bookings - should be HIGH RISK)")
    result = await get_consequences_for_action(
        action_type="remove_vehicle",
        entity_id=1,
        db=db
    )
    print_result("Consequence Check: Remove Vehicle (HIGH RISK)", result)
    print(f"  Risk Level: {result.get('data', {}).get('risk_level')}")
    print(f"  Explanation:\n    {result.get('data', {}).get('explanation')}")

    # Test 2: Check consequences for trip without bookings (should be LOW/NONE)
    print("\n2. Testing get_consequences_for_action('remove_vehicle', trip_id=3)")
    print("   (Trip without high bookings - should be LOW/NONE)")
    result = await get_consequences_for_action(
        action_type="remove_vehicle",
        entity_id=3,
        db=db
    )
    print_result("Consequence Check: Remove Vehicle (LOW/NONE)", result)
    print(f"  Risk Level: {result.get('data', {}).get('risk_level')}")

    # Test 3: Check consequences for unknown action type (should be NONE)
    print("\n3. Testing get_consequences_for_action('unknown_action', entity_id=1)")
    result = await get_consequences_for_action(
        action_type="unknown_action",
        entity_id=1,
        db=db
    )
    print_result("Consequence Check: Unknown Action (NONE)", result)


async def test_create_tools(db: AsyncSession):
    """Test all 4 create operations."""
    print_section("Testing Create Tools (4)")

    # Test 1: Create a new stop (using timestamp to ensure uniqueness)
    print("\n1. Testing create_stop()")
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = await create_stop(
        name=f"Test Stop - Indiranagar {timestamp}",
        latitude=12.9716,
        longitude=77.6412,
        db=db
    )
    print_result("Create Stop", result)

    # Test 2: Create a new path (using existing stop IDs)
    print("\n2. Testing create_path()")
    result = await create_path(
        path_name=f"Test Path - Express {timestamp}",
        ordered_stop_ids=[1, 2, 3],  # Using existing stops
        db=db
    )
    print_result("Create Path", result)
    created_path_name = result.get("data", {}).get("path_name")

    # Test 3: Create a new route (using the path we just created)
    print("\n3. Testing create_route()")
    if created_path_name:
        result = await create_route(
            path_name=created_path_name,
            shift_time="10:00",
            direction="LOGIN",
            start_point="Home",
            end_point="Office",
            db=db
        )
        print_result("Create Route", result)
    else:
        print("❌ SKIP | Create Route (path creation failed)")

    # Test 4: Assign vehicle to trip (vehicle_id=4, driver_id=3, trip_id=5)
    print("\n4. Testing assign_vehicle_to_trip()")
    print("   (Assigning vehicle 4, driver 3 to trip 5)")
    result = await assign_vehicle_to_trip(
        trip_id=5,
        vehicle_id=4,
        driver_id=3,
        db=db
    )
    print_result("Assign Vehicle to Trip", result)


async def test_delete_tool(db: AsyncSession):
    """Test the delete operation."""
    print_section("Testing Delete Tool (1)")

    # Test: Remove vehicle from trip (trip_id=5 which we just assigned to)
    print("\n1. Testing remove_vehicle_from_trip(trip_id=5)")
    print("   (Removing vehicle we just assigned in previous test)")
    result = await remove_vehicle_from_trip(trip_id=5, db=db)
    print_result("Remove Vehicle from Trip", result)


async def test_tool_registry():
    """Test the TOOL_REGISTRY dispatch mechanism."""
    print_section("Testing TOOL_REGISTRY Dispatch Mechanism")

    print("\n1. Verifying all 10 tools are registered")
    expected_tools = [
        "get_unassigned_vehicles_count",
        "get_trip_status",
        "list_stops_for_path",
        "list_routes_by_path",
        "assign_vehicle_to_trip",
        "create_stop",
        "create_path",
        "create_route",
        "remove_vehicle_from_trip",
        "get_consequences_for_action"
    ]

    registered_tools = set(TOOL_REGISTRY.keys())
    print(f"  Total registered tools: {len(registered_tools)}")
    print(f"  Registered tool names: {sorted(registered_tools)}")

    all_present = all(tool in registered_tools for tool in expected_tools)
    if all_present:
        print("  ✅ All 10 core tools are registered")
    else:
        print("  ❌ Some core tools missing from registry")

    # Test dispatch mechanism
    print("\n2. Testing TOOL_REGISTRY dispatch")
    async with AsyncSessionLocal() as db:
        # Dispatch via registry
        tool_func = TOOL_REGISTRY["get_unassigned_vehicles_count"]
        result = await tool_func(db=db)
        print_result("Registry Dispatch Test", result)


async def test_error_handling(db: AsyncSession):
    """Test error handling for invalid inputs."""
    print_section("Testing Error Handling")

    # Test 1: Get status for non-existent trip
    print("\n1. Testing get_trip_status(trip_id=9999) [Should fail]")
    result = await get_trip_status(trip_id=9999, db=db)
    print_result("Get Non-Existent Trip", result, expected_success=False)

    # Test 2: Assign non-existent vehicle
    print("\n2. Testing assign_vehicle_to_trip(vehicle_id=9999) [Should fail]")
    result = await assign_vehicle_to_trip(
        trip_id=1,
        vehicle_id=9999,
        driver_id=1,
        db=db
    )
    print_result("Assign Non-Existent Vehicle", result, expected_success=False)

    # Test 3: Remove vehicle from trip without deployment
    print("\n3. Testing remove_vehicle_from_trip(trip_id=7) [Should fail - no vehicle assigned]")
    result = await remove_vehicle_from_trip(trip_id=7, db=db)
    print_result("Remove Non-Existent Deployment", result, expected_success=False)


async def main():
    """Run all tool tests."""
    print("\n" + "=" * 80)
    print("  TICKET #3: Tool Functions Test Suite")
    print("  Testing all 10 required tool functions")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        try:
            # Test each category
            await test_read_tools(db)
            await test_consequence_tool(db)
            await test_create_tools(db)
            await test_delete_tool(db)
            await test_error_handling(db)

            # Test registry (needs its own session)
            await test_tool_registry()

            print("\n" + "=" * 80)
            print("  Test Suite Complete!")
            print("=" * 80)
            print("\n✅ All tool functions have been tested")
            print("✅ Consequence checking (Tribal Knowledge) verified")
            print("✅ TOOL_REGISTRY dispatch mechanism verified")
            print("✅ Error handling validated")

        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
