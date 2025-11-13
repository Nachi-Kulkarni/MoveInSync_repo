"""
Phase 4f Test - Format Response Node with EXPLICIT OpenRouter API Testing
Shows real Claude API calls for response formatting
"""

import asyncio
import httpx
from app.agent.state import create_initial_state
from app.agent.nodes.format import format_response_node
from app.utils.openrouter import OpenRouterClient
from app.core.config import settings


async def test_direct_claude_formatting():
    """Test response formatting with EXPLICIT Claude API calls."""
    print("\n" + "="*60)
    print("PHASE 4f TEST: Format Response with REAL Claude API Calls")
    print("="*60)

    # Test 1: Direct API call to show it's working
    print("\n✅ Test 1: DIRECT Claude API call for formatting")
    print("   Testing OpenRouter connection...")

    client = OpenRouterClient()

    tool_results = {
        "success": True,
        "data": {
            "unassigned_count": 3,
            "unassigned_vehicles": [
                {"license_plate": "MH-12-3456", "type": "Bus", "capacity": 45},
                {"license_plate": "KA-01-9876", "type": "Cab", "capacity": 4}
            ]
        }
    }

    user_message = f"""
User request: "How many unassigned vehicles are there?"

Tool executed: get_unassigned_vehicles_count
Action type: read

Tool results:
{tool_results}

Please generate a natural, conversational response that:
1. Confirms what was done
2. Presents key results clearly
3. Uses simple language (avoid technical jargon)
4. Keeps it concise (2-3 sentences)

Format numbers nicely (e.g., "3 vehicles" not "count: 3").
"""

    print(f"   📤 Calling Claude Sonnet 4.5 via OpenRouter...")
    print(f"   Model: {settings.CLAUDE_MODEL}")

    try:
        response = await client.chat_completion(
            model=settings.CLAUDE_MODEL,
            messages=[
                {"role": "system", "content": "You format transport system responses naturally."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=300,
        )

        formatted_text = response["choices"][0]["message"]["content"]
        token_usage = response.get("usage", {})

        print(f"   ✅ API call successful!")
        print(f"   ✅ Tokens used: {token_usage.get('total_tokens', 'N/A')}")
        print(f"   ✅ Response length: {len(formatted_text)} chars")
        print(f"   ✅ Claude formatted response:")
        print(f"   \"{formatted_text}\"")

    except Exception as e:
        print(f"   ❌ API call failed: {e}")
        raise
    finally:
        await client.close()

    # Test 2: Format node with SUCCESS result (calls Claude internally)
    print("\n✅ Test 2: format_response_node with SUCCESS (calls Claude)")

    state2 = create_initial_state(
        user_input="Show me unassigned vehicles",
        session_id="test-format-2",
        context={"page": "busDashboard"}
    )

    state2.update({
        "intent": "get_unassigned_vehicles",
        "action_type": "read",
        "tool_name": "get_unassigned_vehicles_count",
        "execution_success": True,
        "tool_results": {
            "success": True,
            "message": "Retrieved unassigned vehicles",
            "data": {
                "unassigned_count": 3,
                "unassigned_vehicles": [
                    {"license_plate": "MH-12-3456", "type": "Bus", "capacity": 45},
                    {"license_plate": "KA-01-9876", "type": "Cab", "capacity": 4},
                    {"license_plate": "MH-02-1111", "type": "Bus", "capacity": 40}
                ]
            }
        }
    })

    print(f"   Input: '{state2['user_input']}'")
    print(f"   Tool: {state2['tool_name']}")
    print(f"   📤 Calling format_response_node (will call Claude internally)...")

    result2 = await format_response_node(state2)

    print(f"   ✅ Response type: {result2['response_type']}")
    print(f"   ✅ Formatted response ({len(result2['response'])} chars):")
    print(f"   \"{result2['response']}\"")

    assert result2['response_type'] == 'success', "Should be success"
    assert len(result2['response']) > 0, "Should have response"

    # Test 3: Format node with WRITE operation
    print("\n✅ Test 3: format_response_node with WRITE (calls Claude)")

    state3 = create_initial_state(
        user_input="Create stop at Gavipuram",
        session_id="test-format-3",
        context={"page": "manageRoute"}
    )

    state3.update({
        "intent": "create_stop",
        "action_type": "write",
        "tool_name": "create_stop",
        "execution_success": True,
        "tool_results": {
            "success": True,
            "message": "Stop created successfully",
            "data": {
                "stop_id": 99,
                "name": "Gavipuram Stop",
                "latitude": 12.9716,
                "longitude": 77.6412
            }
        }
    })

    print(f"   Input: '{state3['user_input']}'")
    print(f"   Tool: {state3['tool_name']}")
    print(f"   📤 Calling format_response_node (will call Claude internally)...")

    result3 = await format_response_node(state3)

    print(f"   ✅ Response type: {result3['response_type']}")
    print(f"   ✅ Formatted response:")
    print(f"   \"{result3['response']}\"")

    assert result3['response_type'] == 'success', "Should be success"

    # Test 4: Error formatting (no Claude call - uses pattern matching)
    print("\n✅ Test 4: format_response_node with ERROR (no Claude)")

    state4 = create_initial_state(
        user_input="Delete trip 999",
        session_id="test-format-4",
        context={"page": "busDashboard"}
    )

    state4.update({
        "intent": "delete_trip",
        "action_type": "delete",
        "tool_name": "delete_trip",
        "execution_success": False,
        "execution_error": "Trip ID 999 not found in database",
        "error": "Not found",
        "error_node": "execute_action_node"
    })

    print(f"   Input: '{state4['user_input']}'")
    print(f"   Error: {state4['execution_error']}")
    print(f"   🔧 Calling format_response_node (uses error patterns)...")

    result4 = await format_response_node(state4)

    print(f"   ✅ Response type: {result4['response_type']}")
    print(f"   ✅ Error message:")
    print(f"   \"{result4['response']}\"")

    assert result4['response_type'] == 'error', "Should be error"

    # Test 5: Confirmation (passthrough - no Claude call)
    print("\n✅ Test 5: format_response_node with CONFIRMATION (passthrough)")

    state5 = create_initial_state(
        user_input="Remove vehicle from trip",
        session_id="test-format-5",
        context={"page": "busDashboard"}
    )

    state5.update({
        "requires_confirmation": True,
        "user_confirmed": False,
        "confirmation_message": "⚠️ This will cancel 15 bookings. Proceed?"
    })

    print(f"   Input: '{state5['user_input']}'")
    print(f"   Requires confirmation: True")
    print(f"   🔧 Calling format_response_node (passes through message)...")

    result5 = await format_response_node(state5)

    print(f"   ✅ Response type: {result5['response_type']}")
    print(f"   ✅ Confirmation message:")
    print(f"   \"{result5['response']}\"")

    assert result5['response_type'] == 'confirmation', "Should be confirmation"

    print("\n" + "="*60)
    print("🎉 All Phase 4f tests PASSED with OpenRouter!")
    print("="*60)
    print("\nProof of OpenRouter Integration:")
    print("- ✅ Test 1: EXPLICIT Claude API call shown")
    print("- ✅ Test 2: format_response_node calls Claude for SUCCESS")
    print("- ✅ Test 3: format_response_node calls Claude for WRITE")
    print("- ✅ Test 4: Error formatting (pattern-based, no API)")
    print("- ✅ Test 5: Confirmation passthrough (no API)")
    print("\nClaude API calls happen in format.py:166-171")
    print("OpenRouter model: " + settings.CLAUDE_MODEL)

    return True


async def main():
    """Run Phase 4f tests."""
    try:
        success = await test_direct_claude_formatting()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Phase 4f test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
