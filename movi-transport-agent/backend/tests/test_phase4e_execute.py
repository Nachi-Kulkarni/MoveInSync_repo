"""
Phase 4e Test - Execute Action Node
Tests tool execution with real TOOL_REGISTRY and database operations
"""

import asyncio
from app.agent.state import create_initial_state
from app.agent.nodes.execute import execute_action_node


async def test_tool_execution():
    """Test execution of different tool types."""
    print("\n" + "="*60)
    print("PHASE 4e TEST: Execute Action Node with TOOL_REGISTRY")
    print("="*60)

    # Test 1: Execute READ tool (no confirmation needed)
    print("\n✅ Test 1: Execute READ tool - get_unassigned_vehicles_count")
    state1 = create_initial_state(
        user_input="How many unassigned vehicles?",
        session_id="test-execute-1",
        context={"page": "busDashboard"}
    )

    # Set up state as if classify node already ran
    state1.update({
        "intent": "get_unassigned_vehicles",
        "action_type": "read",
        "tool_name": "get_unassigned_vehicles_count",
        "tool_params": {},
        "requires_confirmation": False,
        "user_confirmed": False,
    })

    print(f"   Tool: {state1['tool_name']}")
    print(f"   Requires confirmation: {state1['requires_confirmation']}")

    # Execute tool
    execute_result1 = await execute_action_node(state1)

    assert execute_result1.get("error") is None, f"Error: {execute_result1.get('error')}"
    assert execute_result1.get("execution_success") == True, "Execution should succeed"

    tool_results1 = execute_result1.get("tool_results", {})
    print(f"   ✅ Execution success: {execute_result1.get('execution_success')}")
    print(f"   ✅ Tool success: {tool_results1.get('success')}")

    if tool_results1.get("data"):
        data = tool_results1["data"]
        print(f"   ✅ Unassigned count: {data.get('unassigned_count')}")
        print(f"   ✅ Unassigned vehicles: {len(data.get('unassigned_vehicles', []))} vehicles")

    # Verify READ tool executed successfully
    assert tool_results1.get("success") == True, "Tool should return success"
    assert "data" in tool_results1, "Tool should return data"

    # Test 2: Execute tool that requires confirmation but not confirmed
    print("\n✅ Test 2: Try to execute DELETE without confirmation")
    state2 = create_initial_state(
        user_input="Remove vehicle from Bulk - 00:01",
        session_id="test-execute-2",
        context={"page": "busDashboard"}
    )

    state2.update({
        "intent": "remove_vehicle",
        "action_type": "delete",
        "tool_name": "remove_vehicle_from_trip",
        "tool_params": {"trip_id": 1},
        "requires_confirmation": True,
        "user_confirmed": False,  # NOT CONFIRMED
    })

    print(f"   Tool: {state2['tool_name']}")
    print(f"   Requires confirmation: {state2['requires_confirmation']}")
    print(f"   User confirmed: {state2['user_confirmed']}")

    # Try to execute (should fail)
    execute_result2 = await execute_action_node(state2)

    print(f"   ✅ Execution success: {execute_result2.get('execution_success')}")
    print(f"   ✅ Execution error: {execute_result2.get('execution_error')}")

    # Verify execution blocked
    assert execute_result2.get("execution_success") == False, "Should block without confirmation"
    assert "confirmation" in execute_result2.get("execution_error", "").lower(), \
        "Error should mention confirmation"

    # Test 3: Execute DELETE tool WITH confirmation
    print("\n✅ Test 3: Execute DELETE tool WITH user confirmation")
    state3 = create_initial_state(
        user_input="Remove vehicle from trip 6",
        session_id="test-execute-3",
        context={"page": "busDashboard"}
    )

    state3.update({
        "intent": "remove_vehicle",
        "action_type": "delete",
        "tool_name": "remove_vehicle_from_trip",
        "tool_params": {"trip_id": 6},  # Trip 6 actually has a vehicle assigned
        "requires_confirmation": True,
        "user_confirmed": True,  # CONFIRMED!
    })

    print(f"   Tool: {state3['tool_name']}")
    print(f"   Trip ID: {state3['tool_params']['trip_id']}")
    print(f"   User confirmed: {state3['user_confirmed']}")

    # Execute tool
    execute_result3 = await execute_action_node(state3)

    print(f"   ✅ Execution success: {execute_result3.get('execution_success')}")

    tool_results3 = execute_result3.get("tool_results", {})
    if tool_results3:
        print(f"   ✅ Tool success: {tool_results3.get('success')}")
        print(f"   ✅ Message: {tool_results3.get('message', '')[:80]}...")

    # Verify DELETE tool executed
    assert execute_result3.get("execution_success") == True, "Should execute with confirmation"
    assert tool_results3.get("success") == True, "Tool should succeed"

    # Test 4: Execute WRITE tool (create_stop)
    print("\n✅ Test 4: Execute WRITE tool - create_stop")
    state4 = create_initial_state(
        user_input="Create a stop called Test Stop",
        session_id="test-execute-4",
        context={"page": "manageRoute"}
    )

    state4.update({
        "intent": "create_stop",
        "action_type": "write",
        "tool_name": "create_stop",
        "tool_params": {
            "name": "Test Stop - Phase 4e",
            "latitude": 12.9716,
            "longitude": 77.6412
        },
        "requires_confirmation": False,
        "user_confirmed": False,
    })

    print(f"   Tool: {state4['tool_name']}")
    print(f"   Params: name='{state4['tool_params']['name']}'")

    # Execute tool
    execute_result4 = await execute_action_node(state4)

    assert execute_result4.get("error") is None, f"Error: {execute_result4.get('error')}"

    tool_results4 = execute_result4.get("tool_results", {})
    print(f"   ✅ Execution success: {execute_result4.get('execution_success')}")
    print(f"   ✅ Tool success: {tool_results4.get('success')}")

    if tool_results4.get("data"):
        print(f"   ✅ Created stop ID: {tool_results4['data'].get('stop_id')}")

    # Verify WRITE tool executed
    assert execute_result4.get("execution_success") == True, "Should execute successfully"
    assert tool_results4.get("success") == True, "Tool should succeed"

    # Test 5: Handle invalid tool name
    print("\n✅ Test 5: Handle invalid tool name")
    state5 = create_initial_state(
        user_input="Some action",
        session_id="test-execute-5",
        context={"page": "busDashboard"}
    )

    state5.update({
        "intent": "invalid_intent",
        "tool_name": "nonexistent_tool",
        "tool_params": {},
        "requires_confirmation": False,
    })

    print(f"   Tool: {state5['tool_name']}")

    # Try to execute
    execute_result5 = await execute_action_node(state5)

    print(f"   ✅ Execution success: {execute_result5.get('execution_success')}")
    print(f"   ✅ Error: {execute_result5.get('execution_error')}")

    # Verify error handling
    assert execute_result5.get("execution_success") == False, "Should fail for invalid tool"
    assert "not found" in execute_result5.get("execution_error", "").lower(), \
        "Error should mention tool not found"

    print("\n" + "="*60)
    print("🎉 All Phase 4e tests PASSED!")
    print("="*60)
    print("\nSummary:")
    print("- ✅ READ tools execute successfully")
    print("- ✅ WRITE tools execute successfully")
    print("- ✅ DELETE tools require confirmation")
    print("- ✅ Execution blocked without confirmation")
    print("- ✅ Execution succeeds with confirmation")
    print("- ✅ Invalid tools handled gracefully")
    print("- ✅ Real TOOL_REGISTRY integration successful")

    return True


async def main():
    """Run Phase 4e tests."""
    try:
        success = await test_tool_execution()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Phase 4e test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
