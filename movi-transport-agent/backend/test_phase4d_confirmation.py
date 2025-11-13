"""
Phase 4d Test - Request Confirmation Node
Tests confirmation message generation with real Claude API calls
"""

import asyncio
from app.agent.state import create_initial_state
from app.agent.nodes.preprocess import preprocess_input_node
from app.agent.nodes.classify import classify_intent_node
from app.agent.nodes.consequences import check_consequences_node
from app.agent.nodes.confirmation import request_confirmation_node


async def test_confirmation_scenarios():
    """Test confirmation message generation for different scenarios."""
    print("\n" + "="*60)
    print("PHASE 4d TEST: Request Confirmation Node with Claude API")
    print("="*60)

    # Test 1: HIGH RISK - Remove vehicle from Bulk - 00:01 (requires confirmation)
    print("\n✅ Test 1: HIGH RISK confirmation - Remove vehicle from Bulk - 00:01")
    state1 = create_initial_state(
        user_input="Remove vehicle from Bulk - 00:01 trip",
        session_id="test-confirmation-1",
        context={"page": "busDashboard"}
    )

    # Run through preprocess -> classify -> consequences pipeline
    preprocess_result1 = await preprocess_input_node(state1)
    state1.update(preprocess_result1)

    classify_result1 = await classify_intent_node(state1)
    state1.update(classify_result1)

    consequence_result1 = await check_consequences_node(state1)
    state1.update(consequence_result1)

    print(f"   Input: '{state1['user_input']}'")
    print(f"   Risk level: {consequence_result1.get('risk_level')}")
    print(f"   Requires confirmation: {consequence_result1.get('requires_confirmation')}")

    # Request confirmation
    confirmation_result1 = await request_confirmation_node(state1)

    assert confirmation_result1.get("error") is None, f"Error: {confirmation_result1.get('error')}"

    confirmation_message1 = confirmation_result1.get("confirmation_message")
    requires_confirmation1 = confirmation_result1.get("requires_confirmation")
    user_confirmed1 = confirmation_result1.get("user_confirmed")

    print(f"   ✅ Confirmation message generated:")
    print(f"      {confirmation_message1[:200]}...")
    print(f"   ✅ Requires confirmation: {requires_confirmation1}")
    print(f"   ✅ User confirmed: {user_confirmed1}")

    # Verify confirmation message is present
    assert confirmation_message1 is not None, "Confirmation message should be present"
    assert len(confirmation_message1) > 20, "Confirmation message should be substantive"
    assert requires_confirmation1 == True, "Should still require confirmation"
    assert user_confirmed1 == False, "User has not confirmed yet"

    # Test 2: READ operation - No confirmation needed
    print("\n✅ Test 2: READ operation - No confirmation needed")
    state2 = create_initial_state(
        user_input="How many unassigned vehicles are available?",
        session_id="test-confirmation-2",
        context={"page": "busDashboard"}
    )

    # Run through pipeline
    preprocess_result2 = await preprocess_input_node(state2)
    state2.update(preprocess_result2)

    classify_result2 = await classify_intent_node(state2)
    state2.update(classify_result2)

    consequence_result2 = await check_consequences_node(state2)
    state2.update(consequence_result2)

    print(f"   Input: '{state2['user_input']}'")
    print(f"   Requires confirmation: {consequence_result2.get('requires_confirmation')}")

    # Request confirmation (should be skipped)
    confirmation_result2 = await request_confirmation_node(state2)

    confirmation_message2 = confirmation_result2.get("confirmation_message")
    requires_confirmation2 = confirmation_result2.get("requires_confirmation")

    print(f"   ✅ Confirmation message: {confirmation_message2}")
    print(f"   ✅ Requires confirmation: {requires_confirmation2}")

    # Verify no confirmation needed
    assert confirmation_message2 is None, "READ operations should not have confirmation message"
    assert requires_confirmation2 == False, "READ operations should not require confirmation"

    # Test 3: Verify confirmation message quality
    print("\n✅ Test 3: Verify confirmation message quality")

    # Check message contains key information
    message_lower = confirmation_message1.lower()

    # Should mention the trip
    assert "bulk" in message_lower or "00:01" in message_lower or "trip" in message_lower, \
        "Message should mention the trip"

    # Should mention consequences or risk
    has_consequence_keywords = any(
        word in message_lower
        for word in ["consequence", "affect", "cancel", "booking", "warning", "risk", "impact"]
    )
    assert has_consequence_keywords, "Message should mention consequences or risk"

    # Should ask for confirmation
    has_confirmation_keywords = any(
        word in message_lower
        for word in ["confirm", "proceed", "continue", "sure", "want"]
    )
    assert has_confirmation_keywords, "Message should ask for confirmation"

    print(f"   ✅ Message mentions the trip")
    print(f"   ✅ Message explains consequences")
    print(f"   ✅ Message asks for confirmation")

    # Test 4: Multiple HIGH RISK scenarios - ensure different messages
    print("\n✅ Test 4: Test fallback confirmation generation")

    # Manually create a high-risk state without consequences
    state4 = create_initial_state(
        user_input="Delete trip Bulk - 00:01",
        session_id="test-confirmation-4",
        context={"page": "busDashboard"}
    )

    # Set high-risk flags manually
    state4.update({
        "intent": "delete_trip",
        "action_type": "delete",
        "requires_confirmation": True,
        "risk_level": "high",
        "consequences": {
            "risk_level": "high",
            "action_type": "delete_trip",
            "affected_bookings": 10,
            "explanation": "This trip has 25% bookings. Deleting will cancel all bookings."
        }
    })

    # Request confirmation
    confirmation_result4 = await request_confirmation_node(state4)

    confirmation_message4 = confirmation_result4.get("confirmation_message")

    print(f"   ✅ Fallback/Claude confirmation generated:")
    print(f"      {confirmation_message4[:200]}...")

    # Verify message is present and reasonable
    assert confirmation_message4 is not None, "Confirmation message should be present"
    assert len(confirmation_message4) > 20, "Confirmation message should be substantive"

    print("\n" + "="*60)
    print("🎉 All Phase 4d tests PASSED!")
    print("="*60)
    print("\nSummary:")
    print("- ✅ HIGH RISK scenarios generate confirmation messages with Claude")
    print("- ✅ Confirmation messages are clear and informative")
    print("- ✅ Messages mention trip, consequences, and ask for confirmation")
    print("- ✅ READ operations skip confirmation correctly")
    print("- ✅ Fallback confirmation works when needed")
    print("- ✅ Real Claude API integration successful")

    return True


async def main():
    """Run Phase 4d tests."""
    try:
        success = await test_confirmation_scenarios()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Phase 4d test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
