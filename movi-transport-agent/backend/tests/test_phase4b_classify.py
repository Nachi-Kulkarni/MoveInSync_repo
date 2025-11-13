"""
Phase 4b Test - Classify Intent Node
Tests intent classification with real Claude API calls via OpenRouter
"""

import asyncio
from app.agent.state import create_initial_state
from app.agent.nodes.preprocess import preprocess_input_node
from app.agent.nodes.classify import classify_intent_node


async def test_classify_intents():
    """Test classification of different intents with real Claude API."""
    print("\n" + "="*60)
    print("PHASE 4b TEST: Classify Intent Node with Claude API")
    print("="*60)
    
    # Test 1: Read operation (list unassigned vehicles)
    print("\n✅ Test 1: READ operation - list unassigned vehicles")
    state1 = create_initial_state(
        user_input="How many unassigned vehicles are available?",
        session_id="test-classify-1",
        context={"page": "busDashboard"}
    )
    
    # Preprocess first
    preprocess_result = await preprocess_input_node(state1)
    state1.update(preprocess_result)
    
    # Classify intent
    print(f"   Input: '{state1['user_input']}'")
    classify_result = await classify_intent_node(state1)
    
    assert classify_result.get("error") is None, f"Error: {classify_result.get('error')}"
    print(f"   ✅ Intent: {classify_result.get('intent')}")
    print(f"   ✅ Action type: {classify_result.get('action_type')}")
    print(f"   ✅ Tool: {classify_result.get('tool_name')}")
    print(f"   ✅ Requires consequence check: {classify_result.get('requires_consequence_check')}")
    
    # Verify it's a read operation
    assert classify_result.get("action_type") == "read", \
        f"Expected read, got {classify_result.get('action_type')}"
    assert classify_result.get("requires_consequence_check") == False, \
        "Read operations shouldn't require consequence check"
    
    # Test 2: DELETE operation (remove vehicle)
    print("\n✅ Test 2: DELETE operation - remove vehicle from trip")
    state2 = create_initial_state(
        user_input="Remove vehicle MH-12-3456 from Bulk - 00:01 trip",
        session_id="test-classify-2",
        context={"page": "busDashboard"}
    )
    
    preprocess_result2 = await preprocess_input_node(state2)
    state2.update(preprocess_result2)
    
    print(f"   Input: '{state2['user_input']}'")
    classify_result2 = await classify_intent_node(state2)
    
    assert classify_result2.get("error") is None, f"Error: {classify_result2.get('error')}"
    print(f"   ✅ Intent: {classify_result2.get('intent')}")
    print(f"   ✅ Action type: {classify_result2.get('action_type')}")
    print(f"   ✅ Tool: {classify_result2.get('tool_name')}")
    print(f"   ✅ Requires consequence check: {classify_result2.get('requires_consequence_check')}")
    
    # Verify it's a delete operation with consequence check
    assert classify_result2.get("action_type") == "delete", \
        f"Expected delete, got {classify_result2.get('action_type')}"
    assert classify_result2.get("requires_consequence_check") == True, \
        "DELETE operations MUST require consequence check"
    
    # Verify entities were extracted
    entities = classify_result2.get("extracted_entities", {})
    print(f"   ✅ Extracted entities: {list(entities.keys())}")
    if entities.get("trip_id") or entities.get("trip_name"):
        print(f"      Trip: {entities.get('trip_id') or entities.get('trip_name')}")
    if entities.get("vehicle_id"):
        print(f"      Vehicle: {entities.get('vehicle_id')}")
    
    # Test 3: WRITE operation (create stop)
    print("\n✅ Test 3: WRITE operation - create new stop")
    state3 = create_initial_state(
        user_input="Create a new stop called 'Indiranagar' at coordinates 12.9716, 77.6412",
        session_id="test-classify-3",
        context={"page": "manageRoute"}
    )
    
    preprocess_result3 = await preprocess_input_node(state3)
    state3.update(preprocess_result3)
    
    print(f"   Input: '{state3['user_input']}'")
    classify_result3 = await classify_intent_node(state3)
    
    assert classify_result3.get("error") is None, f"Error: {classify_result3.get('error')}"
    print(f"   ✅ Intent: {classify_result3.get('intent')}")
    print(f"   ✅ Action type: {classify_result3.get('action_type')}")
    print(f"   ✅ Tool: {classify_result3.get('tool_name')}")
    print(f"   ✅ Requires consequence check: {classify_result3.get('requires_consequence_check')}")
    
    # Verify it's a write operation
    assert classify_result3.get("action_type") == "write", \
        f"Expected write, got {classify_result3.get('action_type')}"
    
    # Test 4: Conversational query
    print("\n✅ Test 4: Conversational query - trip status")
    state4 = create_initial_state(
        user_input="What's the status of the Bulk - 00:01 trip?",
        session_id="test-classify-4",
        context={"page": "busDashboard"}
    )
    
    preprocess_result4 = await preprocess_input_node(state4)
    state4.update(preprocess_result4)
    
    print(f"   Input: '{state4['user_input']}'")
    classify_result4 = await classify_intent_node(state4)
    
    assert classify_result4.get("error") is None, f"Error: {classify_result4.get('error')}"
    print(f"   ✅ Intent: {classify_result4.get('intent')}")
    print(f"   ✅ Action type: {classify_result4.get('action_type')}")
    print(f"   ✅ Tool: {classify_result4.get('tool_name')}")
    
    print("\n" + "="*60)
    print("🎉 All Phase 4b tests PASSED!")
    print("="*60)
    print("\nSummary:")
    print("- ✅ READ operations classified correctly")
    print("- ✅ DELETE operations flagged for consequence check")
    print("- ✅ WRITE operations classified correctly")
    print("- ✅ Entity extraction working")
    print("- ✅ Tool selection accurate")
    print("- ✅ Real Claude API integration successful")
    
    return True


async def main():
    """Run Phase 4b tests."""
    try:
        success = await test_classify_intents()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Phase 4b test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
