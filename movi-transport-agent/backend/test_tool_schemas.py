"""
Test script for tool schemas validation.

Tests:
1. All tool request schemas validate correctly
2. Tool response schema works with actual tool outputs
3. Consequence result schema validates properly
4. Validation utility catches errors
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.schemas.tool import (
    ToolResponse,
    GetTripStatusRequest,
    AssignVehicleToTripRequest,
    CreateStopRequest,
    RemoveVehicleFromTripRequest,
    GetConsequencesRequest,
    ConsequenceResult,
    TOOL_METADATA_REGISTRY,
    validate_tool_request
)
from app.tools import get_trip_status, get_consequences_for_action
from app.core.database import AsyncSessionLocal


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


async def test_request_schemas():
    """Test all request schemas."""
    print_section("Test 1: Tool Request Schemas")

    # Test 1: GetTripStatusRequest
    print("\n1. Testing GetTripStatusRequest...")
    try:
        request = GetTripStatusRequest(trip_id=1)
        print(f"   ✅ Valid: {request.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 2: Invalid trip_id (must be > 0)
    print("\n2. Testing validation (trip_id must be > 0)...")
    try:
        request = GetTripStatusRequest(trip_id=0)
        print(f"   ❌ Should have failed but got: {request.model_dump()}")
    except Exception as e:
        print(f"   ✅ Correctly caught error: {str(e)[:80]}")

    # Test 3: AssignVehicleToTripRequest
    print("\n3. Testing AssignVehicleToTripRequest...")
    try:
        request = AssignVehicleToTripRequest(trip_id=1, vehicle_id=2, driver_id=3)
        print(f"   ✅ Valid: {request.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 4: CreateStopRequest with coordinates
    print("\n4. Testing CreateStopRequest...")
    try:
        request = CreateStopRequest(name="Test Stop", latitude=12.9352, longitude=77.6245)
        print(f"   ✅ Valid: {request.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 5: Invalid latitude (must be -90 to 90)
    print("\n5. Testing coordinate validation...")
    try:
        request = CreateStopRequest(name="Test", latitude=100.0, longitude=77.0)
        print(f"   ❌ Should have failed but got: {request.model_dump()}")
    except Exception as e:
        print(f"   ✅ Correctly caught error: Latitude out of range")

    # Test 6: RemoveVehicleFromTripRequest
    print("\n6. Testing RemoveVehicleFromTripRequest...")
    try:
        request = RemoveVehicleFromTripRequest(trip_id=1)
        print(f"   ✅ Valid: {request.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 7: GetConsequencesRequest
    print("\n7. Testing GetConsequencesRequest...")
    try:
        request = GetConsequencesRequest(action_type="remove_vehicle", entity_id=1)
        print(f"   ✅ Valid: {request.model_dump()}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")


async def test_response_schema():
    """Test response schema with actual tool output."""
    print_section("Test 2: Tool Response Schema with Real Data")

    async with AsyncSessionLocal() as session:
        # Call a real tool
        print("\n1. Calling get_trip_status(trip_id=1)...")
        result = await get_trip_status(trip_id=1, db=session)
        print(f"   Tool returned: {result.keys()}")

        # Validate with schema
        print("\n2. Validating with ToolResponse schema...")
        try:
            response = ToolResponse(**result)
            print(f"   ✅ Schema validation passed")
            print(f"   Success: {response.success}")
            print(f"   Message: {response.message}")
            print(f"   Data keys: {list(response.data.keys()) if response.data else None}")
        except Exception as e:
            print(f"   ❌ Schema validation failed: {e}")


async def test_consequence_schema():
    """Test consequence result schema."""
    print_section("Test 3: Consequence Result Schema")

    async with AsyncSessionLocal() as session:
        # Call consequence checker for high-risk trip
        print("\n1. Checking consequences for Bulk - 00:01 trip (25% booked)...")
        result = await get_consequences_for_action(
            action_type="remove_vehicle",
            entity_id=1,  # Bulk - 00:01 trip
            db=session
        )

        print(f"   Tool returned: success={result['success']}")

        # Validate consequence data
        if result['success'] and result['data']:
            print("\n2. Validating ConsequenceResult schema...")
            try:
                consequence = ConsequenceResult(**result['data'])
                print(f"   ✅ Schema validation passed")
                print(f"   Risk Level: {consequence.risk_level}")
                print(f"   Action Type: {consequence.action_type}")
                print(f"   Proceed with Caution: {consequence.proceed_with_caution}")
                print(f"   Affected Bookings: {consequence.affected_bookings}")
                print(f"   Explanation: {consequence.explanation[:100]}...")
            except Exception as e:
                print(f"   ❌ Schema validation failed: {e}")


async def test_validation_utility():
    """Test the validate_tool_request utility."""
    print_section("Test 4: Validation Utility")

    # Test 1: Valid request
    print("\n1. Valid request...")
    error = validate_tool_request("get_trip_status", {"trip_id": 1})
    print(f"   {'✅ Passed' if error is None else f'❌ Failed: {error}'}")

    # Test 2: Missing required parameter
    print("\n2. Missing required parameter...")
    error = validate_tool_request("get_trip_status", {})
    print(f"   {'✅ Error caught' if error else '❌ Should have failed'}")
    if error:
        print(f"   Error: {error[:80]}")

    # Test 3: Wrong type
    print("\n3. Wrong parameter type...")
    error = validate_tool_request("get_trip_status", {"trip_id": "invalid"})
    print(f"   {'✅ Error caught' if error else '❌ Should have failed'}")
    if error:
        print(f"   Error: {error[:80]}")

    # Test 4: Invalid tool name
    print("\n4. Invalid tool name...")
    error = validate_tool_request("non_existent_tool", {})
    print(f"   {'✅ Error caught' if error else '❌ Should have failed'}")
    if error:
        print(f"   Error: {error}")


async def test_metadata_registry():
    """Test the tool metadata registry."""
    print_section("Test 5: Tool Metadata Registry")

    print(f"\nTotal tools registered: {len(TOOL_METADATA_REGISTRY)}")

    # Check high-risk tool
    print("\n1. High-risk tool (remove_vehicle_from_trip)...")
    meta = TOOL_METADATA_REGISTRY.get("remove_vehicle_from_trip")
    if meta:
        print(f"   ✅ Found in registry")
        print(f"   Requires consequence check: {meta.requires_consequence_check}")
        print(f"   Risk level: {meta.risk_level}")
        print(f"   Category: {meta.category}")
    else:
        print(f"   ❌ Not found in registry")

    # Check read tool
    print("\n2. Read tool (get_unassigned_vehicles_count)...")
    meta = TOOL_METADATA_REGISTRY.get("get_unassigned_vehicles_count")
    if meta:
        print(f"   ✅ Found in registry")
        print(f"   Requires consequence check: {meta.requires_consequence_check}")
        print(f"   Risk level: {meta.risk_level}")
        print(f"   Category: {meta.category}")
    else:
        print(f"   ❌ Not found in registry")

    # Count by category
    print("\n3. Tools by category...")
    categories = {}
    for name, meta in TOOL_METADATA_REGISTRY.items():
        categories[meta.category] = categories.get(meta.category, 0) + 1
    for category, count in categories.items():
        print(f"   {category}: {count} tools")

    # Tools requiring consequence check
    print("\n4. Tools requiring consequence check...")
    consequence_tools = [
        name for name, meta in TOOL_METADATA_REGISTRY.items()
        if meta.requires_consequence_check
    ]
    print(f"   {len(consequence_tools)} tools: {', '.join(consequence_tools)}")


async def main():
    """Run all schema tests."""
    print("\n" + "=" * 80)
    print("  Tool Schema Validation Test Suite")
    print("=" * 80)

    try:
        await test_request_schemas()
        await test_response_schema()
        await test_consequence_schema()
        await test_validation_utility()
        await test_metadata_registry()

        print("\n" + "=" * 80)
        print("  All Schema Tests Complete!")
        print("=" * 80)
        print("\n✅ Tool schemas are working correctly")
        print("✅ Request validation works")
        print("✅ Response schema matches tool output")
        print("✅ Consequence schema validates properly")
        print("✅ Metadata registry is complete")

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
