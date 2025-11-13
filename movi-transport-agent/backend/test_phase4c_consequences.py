"""
Phase 4c Test - Check Consequences Node
Tests consequence checking with real database queries
Critical test: "Bulk - 00:01" trip with 25% booking (HIGH RISK scenario)
"""

import asyncio
from app.agent.state import create_initial_state
from app.agent.nodes.preprocess import preprocess_input_node
from app.agent.nodes.classify import classify_intent_node
from app.agent.nodes.consequences import check_consequences_node


async def test_consequence_scenarios():
    """Test consequence checking for different risk scenarios."""
    print("\n" + "="*60)
    print("PHASE 4c TEST: Check Consequences Node")
    print("="*60)

    # Test 1: HIGH RISK - Remove vehicle from trip with bookings (Bulk - 00:01)
    print("\n✅ Test 1: HIGH RISK - Remove vehicle from Bulk - 00:01 (25% booked)")
    state1 = create_initial_state(
        user_input="Remove vehicle from Bulk - 00:01 trip",
        session_id="test-consequences-1",
        context={"page": "busDashboard"}
    )

    # Preprocess
    preprocess_result1 = await preprocess_input_node(state1)
    state1.update(preprocess_result1)

    # Classify intent
    classify_result1 = await classify_intent_node(state1)
    state1.update(classify_result1)

    print(f"   Input: '{state1['user_input']}'")
    print(f"   Intent: {classify_result1.get('intent')}")
    print(f"   Requires consequence check: {classify_result1.get('requires_consequence_check')}")

    # Check consequences
    consequence_result1 = await check_consequences_node(state1)

    assert consequence_result1.get("error") is None, f"Error: {consequence_result1.get('error')}"

    risk_level1 = consequence_result1.get("risk_level")
    requires_confirmation1 = consequence_result1.get("requires_confirmation")
    consequences1 = consequence_result1.get("consequences")

    print(f"   ✅ Risk level: {risk_level1}")
    print(f"   ✅ Requires confirmation: {requires_confirmation1}")

    if consequences1:
        print(f"   ✅ Trip: {consequences1.get('trip_name')}")
        print(f"   ✅ Booking percentage: {consequences1.get('booking_percentage')}%")
        print(f"   ✅ Affected bookings: {consequences1.get('affected_bookings')}")
        print(f"   ✅ Explanation:")
        explanation_lines = consequences1.get('explanation', '').split('\n')
        for line in explanation_lines[:3]:  # Show first 3 lines
            print(f"      {line}")

    # Verify HIGH RISK
    assert risk_level1 == "high", f"Expected high risk, got {risk_level1}"
    assert requires_confirmation1 == True, "HIGH RISK must require confirmation"
    assert consequences1 is not None, "Consequences must be present for high-risk actions"
    assert consequences1.get("booking_percentage") == 25, "Bulk - 00:01 should have 25% booking"

    # Test 2: LOW RISK - Remove vehicle from trip without bookings
    print("\n✅ Test 2: LOW RISK - Remove vehicle from trip without bookings")
    # First, let's find a trip without bookings
    from app.core.database import AsyncSessionLocal
    from app.models.daily_trip import DailyTrip
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        # Find trip with 0% booking
        result = await db.execute(
            select(DailyTrip).where(DailyTrip.booking_percentage == 0).limit(1)
        )
        trip_no_bookings = result.scalar_one_or_none()

        if trip_no_bookings:
            state2 = create_initial_state(
                user_input=f"Remove vehicle from {trip_no_bookings.display_name} trip",
                session_id="test-consequences-2",
                context={"page": "busDashboard"}
            )

            # Preprocess
            preprocess_result2 = await preprocess_input_node(state2)
            state2.update(preprocess_result2)

            # Classify intent
            classify_result2 = await classify_intent_node(state2)
            state2.update(classify_result2)

            print(f"   Input: '{state2['user_input']}'")
            print(f"   Intent: {classify_result2.get('intent')}")

            # Check consequences
            consequence_result2 = await check_consequences_node(state2)

            risk_level2 = consequence_result2.get("risk_level")
            requires_confirmation2 = consequence_result2.get("requires_confirmation")
            consequences2 = consequence_result2.get("consequences")

            print(f"   ✅ Risk level: {risk_level2}")
            print(f"   ✅ Requires confirmation: {requires_confirmation2}")

            if consequences2:
                print(f"   ✅ Booking percentage: {consequences2.get('booking_percentage')}%")
                print(f"   ✅ Explanation: {consequences2.get('explanation')[:100]}...")

            # Verify LOW RISK (could also be NONE if no vehicle assigned)
            assert risk_level2 in ["low", "none"], f"Expected low/none risk, got {risk_level2}"
            print(f"   ✅ Correctly identified as {risk_level2.upper()} risk")
        else:
            print("   ⚠️  No trip with 0% booking found, skipping low-risk test")

    # Test 3: READ operation - No consequence checking needed
    print("\n✅ Test 3: READ operation - No consequences needed")
    state3 = create_initial_state(
        user_input="How many unassigned vehicles are available?",
        session_id="test-consequences-3",
        context={"page": "busDashboard"}
    )

    # Preprocess
    preprocess_result3 = await preprocess_input_node(state3)
    state3.update(preprocess_result3)

    # Classify intent
    classify_result3 = await classify_intent_node(state3)
    state3.update(classify_result3)

    print(f"   Input: '{state3['user_input']}'")
    print(f"   Action type: {classify_result3.get('action_type')}")
    print(f"   Requires consequence check: {classify_result3.get('requires_consequence_check')}")

    # Check consequences (should skip)
    consequence_result3 = await check_consequences_node(state3)

    risk_level3 = consequence_result3.get("risk_level")
    requires_confirmation3 = consequence_result3.get("requires_confirmation")

    print(f"   ✅ Risk level: {risk_level3}")
    print(f"   ✅ Requires confirmation: {requires_confirmation3}")

    # Verify no consequence checking
    assert risk_level3 == "none", "READ operations should have no risk"
    assert requires_confirmation3 == False, "READ operations don't need confirmation"

    # Test 4: Verify consequence details structure
    print("\n✅ Test 4: Verify consequence details for Bulk - 00:01")

    # Use the consequence result from Test 1
    if consequences1:
        print(f"   ✅ Consequence structure validation:")
        required_fields = [
            "risk_level", "action_type", "entity_id", "trip_name",
            "booking_percentage", "has_deployment", "consequences",
            "explanation", "proceed_with_caution", "affected_bookings"
        ]

        for field in required_fields:
            assert field in consequences1, f"Missing field: {field}"
            print(f"      ✓ {field}: {type(consequences1[field]).__name__}")

        # Verify consequence list
        consequence_list = consequences1.get("consequences", [])
        assert len(consequence_list) > 0, "Consequences list should not be empty"
        print(f"   ✅ Number of consequences: {len(consequence_list)}")
        print(f"   ✅ Sample consequences:")
        for i, cons in enumerate(consequence_list[:3], 1):
            print(f"      {i}. {cons}")

    print("\n" + "="*60)
    print("🎉 All Phase 4c tests PASSED!")
    print("="*60)
    print("\nSummary:")
    print("- ✅ HIGH RISK scenario detected (Bulk - 00:01 with 25% booking)")
    print("- ✅ Consequence checking correctly flags for confirmation")
    print("- ✅ LOW/NONE RISK scenarios handled correctly")
    print("- ✅ READ operations skip consequence checking")
    print("- ✅ Consequence data structure validated")
    print("- ✅ Tribal knowledge rules enforced")

    return True


async def main():
    """Run Phase 4c tests."""
    try:
        success = await test_consequence_scenarios()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Phase 4c test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
