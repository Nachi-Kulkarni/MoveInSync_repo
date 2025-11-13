"""
Phase 5 Test - Edge Routing Functions
Tests conditional routing logic for LangGraph
"""

import asyncio
from app.agent.state import create_initial_state
from app.agent.edges import (
    route_after_classify,
    route_after_consequences,
    route_after_confirmation,
    route_after_execute,
    get_routing_explanation,
)


async def test_edge_routing():
    """Test conditional routing logic for all edge functions."""
    print("\n" + "="*60)
    print("PHASE 5 TEST: Edge Routing Functions")
    print("="*60)

    # Test 1: route_after_classify - No consequence check needed (READ)
    print("\n✅ Test 1: route_after_classify - READ action (no check)")
    state1 = create_initial_state(
        user_input="How many unassigned vehicles?",
        session_id="test-edge-1",
        context={"page": "busDashboard"}
    )
    state1.update({
        "intent": "get_unassigned_vehicles",
        "action_type": "read",
        "requires_consequence_check": False,
    })

    next_node1 = route_after_classify(state1)
    print(f"   Intent: {state1['intent']}")
    print(f"   Requires check: {state1['requires_consequence_check']}")
    print(f"   ✅ Next node: {next_node1}")

    assert next_node1 == "execute_action", "Should route to execute_action for READ"

    # Test 2: route_after_classify - Consequence check needed (DELETE)
    print("\n✅ Test 2: route_after_classify - DELETE action (needs check)")
    state2 = create_initial_state(
        user_input="Remove vehicle from trip",
        session_id="test-edge-2",
        context={"page": "busDashboard"}
    )
    state2.update({
        "intent": "remove_vehicle",
        "action_type": "delete",
        "requires_consequence_check": True,
    })

    next_node2 = route_after_classify(state2)
    print(f"   Intent: {state2['intent']}")
    print(f"   Requires check: {state2['requires_consequence_check']}")
    print(f"   ✅ Next node: {next_node2}")

    assert next_node2 == "check_consequences", "Should route to check_consequences for DELETE"

    # Test 3: route_after_classify - Error occurred
    print("\n✅ Test 3: route_after_classify - Error in classify")
    state3 = create_initial_state(
        user_input="Invalid action",
        session_id="test-edge-3",
        context={"page": "busDashboard"}
    )
    state3.update({
        "error": "Failed to classify intent",
        "error_node": "classify_intent_node",
    })

    next_node3 = route_after_classify(state3)
    print(f"   Error: {state3['error']}")
    print(f"   ✅ Next node: {next_node3}")

    assert next_node3 == "format_response", "Should route to format_response on error"

    # Test 4: route_after_consequences - Low risk (no confirmation)
    print("\n✅ Test 4: route_after_consequences - LOW RISK")
    state4 = create_initial_state(
        user_input="Remove vehicle from empty trip",
        session_id="test-edge-4",
        context={"page": "busDashboard"}
    )
    state4.update({
        "intent": "remove_vehicle",
        "risk_level": "low",
        "requires_confirmation": False,
    })

    next_node4 = route_after_consequences(state4)
    print(f"   Risk level: {state4['risk_level']}")
    print(f"   Requires confirmation: {state4['requires_confirmation']}")
    print(f"   ✅ Next node: {next_node4}")

    assert next_node4 == "execute_action", "Should route to execute_action for LOW RISK"

    # Test 5: route_after_consequences - High risk (needs confirmation)
    print("\n✅ Test 5: route_after_consequences - HIGH RISK")
    state5 = create_initial_state(
        user_input="Remove vehicle from Bulk-00:01",
        session_id="test-edge-5",
        context={"page": "busDashboard"}
    )
    state5.update({
        "intent": "remove_vehicle",
        "risk_level": "high",
        "requires_confirmation": True,
        "consequences": {"affected_bookings": 15},
    })

    next_node5 = route_after_consequences(state5)
    print(f"   Risk level: {state5['risk_level']}")
    print(f"   Requires confirmation: {state5['requires_confirmation']}")
    print(f"   Affected bookings: {state5['consequences']['affected_bookings']}")
    print(f"   ✅ Next node: {next_node5}")

    assert next_node5 == "request_confirmation", "Should route to request_confirmation for HIGH RISK"

    # Test 6: route_after_consequences - Error occurred
    print("\n✅ Test 6: route_after_consequences - Error in consequences")
    state6 = create_initial_state(
        user_input="Check consequences",
        session_id="test-edge-6",
        context={"page": "busDashboard"}
    )
    state6.update({
        "error": "Database error while checking consequences",
        "error_node": "check_consequences_node",
    })

    next_node6 = route_after_consequences(state6)
    print(f"   Error: {state6['error']}")
    print(f"   ✅ Next node: {next_node6}")

    assert next_node6 == "format_response", "Should route to format_response on error"

    # Test 7: route_after_confirmation - User confirmed
    print("\n✅ Test 7: route_after_confirmation - User CONFIRMED")
    state7 = create_initial_state(
        user_input="Yes, proceed",
        session_id="test-edge-7",
        context={"page": "busDashboard"}
    )
    state7.update({
        "requires_confirmation": True,
        "user_confirmed": True,
    })

    next_node7 = route_after_confirmation(state7)
    print(f"   User confirmed: {state7['user_confirmed']}")
    print(f"   ✅ Next node: {next_node7}")

    assert next_node7 == "execute_action", "Should route to execute_action when confirmed"

    # Test 8: route_after_confirmation - User NOT confirmed (waiting)
    print("\n✅ Test 8: route_after_confirmation - Waiting for user")
    state8 = create_initial_state(
        user_input="Remove vehicle",
        session_id="test-edge-8",
        context={"page": "busDashboard"}
    )
    state8.update({
        "requires_confirmation": True,
        "user_confirmed": False,
        "confirmation_message": "Do you want to proceed?",
    })

    next_node8 = route_after_confirmation(state8)
    print(f"   User confirmed: {state8['user_confirmed']}")
    print(f"   ✅ Next node: {next_node8}")

    assert next_node8 == "format_response", "Should route to format_response when waiting"

    # Test 9: route_after_execute - Always goes to format_response
    print("\n✅ Test 9: route_after_execute - SUCCESS")
    state9 = create_initial_state(
        user_input="Get vehicles",
        session_id="test-edge-9",
        context={"page": "busDashboard"}
    )
    state9.update({
        "execution_success": True,
        "tool_results": {"success": True, "data": {"count": 3}},
    })

    next_node9 = route_after_execute(state9)
    print(f"   Execution success: {state9['execution_success']}")
    print(f"   ✅ Next node: {next_node9}")

    assert next_node9 == "format_response", "Should always route to format_response"

    # Test 10: route_after_execute - FAILURE
    print("\n✅ Test 10: route_after_execute - FAILURE")
    state10 = create_initial_state(
        user_input="Invalid tool",
        session_id="test-edge-10",
        context={"page": "busDashboard"}
    )
    state10.update({
        "execution_success": False,
        "execution_error": "Tool not found",
    })

    next_node10 = route_after_execute(state10)
    print(f"   Execution success: {state10['execution_success']}")
    print(f"   ✅ Next node: {next_node10}")

    assert next_node10 == "format_response", "Should always route to format_response"

    # Test 11: get_routing_explanation - READ path
    print("\n✅ Test 11: get_routing_explanation - READ path")
    state11 = create_initial_state(
        user_input="List vehicles",
        session_id="test-edge-11",
        context={"page": "busDashboard"}
    )
    state11.update({
        "requires_consequence_check": False,
        "execution_success": True,
    })

    explanation11 = get_routing_explanation(state11)
    print(f"   Routing path:")
    print(f"   {explanation11}")

    assert "execute_action" in explanation11, "Should show execute_action in path"

    # Test 12: get_routing_explanation - HIGH RISK with confirmation
    print("\n✅ Test 12: get_routing_explanation - HIGH RISK path")
    state12 = create_initial_state(
        user_input="Remove vehicle from Bulk-00:01",
        session_id="test-edge-12",
        context={"page": "busDashboard"}
    )
    state12.update({
        "requires_consequence_check": True,
        "requires_confirmation": True,
        "user_confirmed": True,
        "execution_success": True,
    })

    explanation12 = get_routing_explanation(state12)
    print(f"   Routing path:")
    print(f"   {explanation12}")

    assert "check_consequences" in explanation12, "Should show check_consequences"
    assert "request_confirmation" in explanation12, "Should show request_confirmation"

    print("\n" + "="*60)
    print("🎉 All Phase 5 tests PASSED!")
    print("="*60)
    print("\nSummary:")
    print("- ✅ route_after_classify works for READ/WRITE/DELETE")
    print("- ✅ route_after_classify handles errors correctly")
    print("- ✅ route_after_consequences routes based on risk level")
    print("- ✅ route_after_consequences handles errors correctly")
    print("- ✅ route_after_confirmation routes on user confirmation")
    print("- ✅ route_after_confirmation waits when not confirmed")
    print("- ✅ route_after_execute always goes to format_response")
    print("- ✅ get_routing_explanation generates correct paths")
    print("\nAll conditional routing logic verified!")

    return True


async def main():
    """Run Phase 5 tests."""
    try:
        success = await test_edge_routing()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Phase 5 test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
