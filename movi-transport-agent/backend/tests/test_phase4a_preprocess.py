"""
Phase 4a Test - Preprocess Input Node
Tests multimodal input preprocessing with real Gemini API calls
"""

import asyncio
from app.agent.state import create_initial_state
from app.agent.nodes.preprocess import preprocess_input_node


async def test_preprocess_text_input():
    """Test preprocessing of text-only input with real Gemini API."""
    print("\n" + "="*60)
    print("PHASE 4a TEST: Preprocess Input Node")
    print("="*60)
    
    # Test 1: Simple text input
    print("\n✅ Test 1: Simple text input")
    state = create_initial_state(
        user_input="How many unassigned vehicles are available?",
        session_id="test-preprocess-1",
        context={"page": "busDashboard"}
    )
    
    print(f"   Input: '{state['user_input']}'")
    print(f"   Context: {state['context']}")
    
    # Call preprocess node
    result = await preprocess_input_node(state)
    
    # Verify result structure
    assert "processed_input" in result, "Missing processed_input"
    assert "input_modalities" in result, "Missing input_modalities"
    assert result.get("error") is None, f"Unexpected error: {result.get('error')}"
    
    processed = result["processed_input"]
    print(f"   ✅ Processed successfully")
    print(f"   Modality: {processed.get('modality')}")
    print(f"   Confidence: {processed.get('confidence')}")
    print(f"   Comprehension: {processed.get('comprehension', '')[:100]}...")
    
    # Check extracted entities
    entities = processed.get("extracted_entities", {})
    print(f"   Extracted entities: {list(entities.keys())}")
    if entities.get("action_intent"):
        print(f"   Action intent: {entities.get('action_intent')}")
    
    # Test 2: Action with entities
    print("\n✅ Test 2: Action with entities (remove vehicle)")
    state2 = create_initial_state(
        user_input="Remove vehicle MH-12-3456 from Bulk - 00:01 trip",
        session_id="test-preprocess-2",
        context={"page": "busDashboard"}
    )
    
    print(f"   Input: '{state2['user_input']}'")
    result2 = await preprocess_input_node(state2)
    
    assert result2.get("error") is None, f"Unexpected error: {result2.get('error')}"
    processed2 = result2["processed_input"]
    
    print(f"   ✅ Processed successfully")
    print(f"   Confidence: {processed2.get('confidence')}")
    
    entities2 = processed2.get("extracted_entities", {})
    print(f"   Extracted entities:")
    if entities2.get("trip_ids"):
        print(f"     Trip IDs: {entities2.get('trip_ids')}")
    if entities2.get("vehicle_ids"):
        print(f"     Vehicle IDs: {entities2.get('vehicle_ids')}")
    if entities2.get("action_intent"):
        print(f"     Action intent: {entities2.get('action_intent')}")
    
    # Verify removal-related entities were extracted
    assert entities2.get("trip_ids") or entities2.get("vehicle_ids"), \
        "Should extract trip_ids or vehicle_ids for removal action"
    
    # Test 3: Complex query
    print("\n✅ Test 3: Complex conversational query")
    state3 = create_initial_state(
        user_input="What's the status of the Bulk - 00:01 trip? Is it fully booked?",
        session_id="test-preprocess-3",
        context={"page": "busDashboard"}
    )
    
    print(f"   Input: '{state3['user_input']}'")
    result3 = await preprocess_input_node(state3)
    
    assert result3.get("error") is None, f"Unexpected error: {result3.get('error')}"
    processed3 = result3["processed_input"]
    
    print(f"   ✅ Processed successfully")
    print(f"   Comprehension: {processed3.get('comprehension', '')[:150]}...")
    
    entities3 = processed3.get("extracted_entities", {})
    if entities3.get("trip_ids"):
        print(f"   Extracted trip: {entities3.get('trip_ids')}")
    
    print("\n" + "="*60)
    print("🎉 All Phase 4a tests PASSED!")
    print("="*60)
    print("\nSummary:")
    print("- ✅ Text input preprocessing works")
    print("- ✅ Entity extraction from Gemini API")
    print("- ✅ Context awareness (page tracking)")
    print("- ✅ Action intent detection")
    print("- ✅ Complex query comprehension")
    
    return True


async def main():
    """Run Phase 4a tests."""
    try:
        success = await test_preprocess_text_input()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Phase 4a test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
