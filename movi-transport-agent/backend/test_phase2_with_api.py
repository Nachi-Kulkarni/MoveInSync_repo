"""
Phase 2 API Test - Test prompts with real Claude API calls via OpenRouter
"""

import asyncio
import json
from app.agent.state import AgentState, create_initial_state, get_state_summary
from app.agent.prompts import (
    PREPROCESSING_SYSTEM_PROMPT,
    CLASSIFICATION_SYSTEM_PROMPT,
    CONFIRMATION_SYSTEM_PROMPT,
    RESPONSE_FORMAT_SYSTEM_PROMPT,
)
from app.utils.openrouter import OpenRouterClient
from app.core.config import settings


async def test_classification_prompt():
    """Test CLASSIFICATION_SYSTEM_PROMPT with real Claude API call."""
    print("\n" + "="*60)
    print("TEST 1: Classification Prompt with Claude API")
    print("="*60)

    client = OpenRouterClient()  # Uses settings by default
    
    # Test input: User wants to remove vehicle from a trip
    user_message = """
    Preprocessed Input:
    {
        "extracted_entities": {
            "trip_ids": ["Bulk - 00:01"],
            "vehicle_ids": ["MH-12-3456"],
            "action_keywords": ["remove"]
        },
        "context_summary": "User is on busDashboard page looking at trip Bulk - 00:01",
        "confidence": "high"
    }
    
    User Input: "Remove vehicle MH-12-3456 from Bulk - 00:01 trip"
    """
    
    messages = [
        {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    print(f"\n📤 Calling Claude with user input: 'Remove vehicle MH-12-3456 from Bulk - 00:01 trip'")
    print(f"   Model: {settings.CLAUDE_MODEL}")
    print(f"   Temperature: {settings.CLAUDE_TEMPERATURE}")
    print(f"   Max Tokens: {settings.CLAUDE_MAX_TOKENS}")

    try:
        response = await client.chat_completion(
            model=settings.CLAUDE_MODEL,
            messages=messages,
            temperature=settings.CLAUDE_TEMPERATURE,
            max_tokens=settings.CLAUDE_MAX_TOKENS,
        )
    except Exception as e:
        print(f"\n❌ API Error: {e}")
        print(f"   Trying with simplified model name...")
        # Try with base model name
        response = await client.chat_completion(
            model="anthropic/claude-sonnet-4.5",
            messages=messages,
            temperature=settings.CLAUDE_TEMPERATURE,
            max_tokens=settings.CLAUDE_MAX_TOKENS,
        )
    
    content = response["choices"][0]["message"]["content"]
    print(f"\n📥 Claude Response:")
    print(content)
    
    # Try to parse as JSON
    try:
        # Remove markdown if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        parsed = json.loads(content)
        print(f"\n✅ Successfully parsed JSON response")
        print(f"   Intent: {parsed.get('intent')}")
        print(f"   Action Type: {parsed.get('action_type')}")
        print(f"   Tool Name: {parsed.get('tool_name')}")
        print(f"   Requires Consequence Check: {parsed.get('requires_consequence_check')}")
        print(f"   Extracted Entities: {parsed.get('extracted_entities')}")
        
        # Validate expected fields
        assert parsed.get('intent') is not None, "Missing 'intent' field"
        assert parsed.get('action_type') in ['read', 'write', 'delete'], f"Invalid action_type: {parsed.get('action_type')}"
        assert parsed.get('tool_name') is not None, "Missing 'tool_name' field"
        assert isinstance(parsed.get('requires_consequence_check'), bool), "requires_consequence_check must be boolean"
        
        # For delete actions, should require consequence check
        if parsed.get('action_type') == 'delete':
            assert parsed.get('requires_consequence_check') == True, "Delete actions must require consequence check"
        
        print("\n✅ All validation checks passed!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Failed to parse JSON: {e}")
        return False
    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        return False


async def test_confirmation_prompt():
    """Test CONFIRMATION_SYSTEM_PROMPT with real Claude API call."""
    print("\n" + "="*60)
    print("TEST 2: Confirmation Prompt with Claude API")
    print("="*60)

    client = OpenRouterClient()  # Uses settings by default
    
    # Test input: High-risk action with consequences
    user_message = """
    Action Plan: "Remove vehicle MH-12-3456 from Bulk-00:01 trip"
    
    Consequence Analysis:
    {
        "risk_level": "high",
        "action_type": "remove_vehicle_from_trip",
        "consequences": [
            "Trip is 25% booked - removing vehicle will cancel bookings",
            "Approximately 15 passengers will be affected",
            "Refunds will be required"
        ],
        "explanation": "This trip has active bookings. Removing the vehicle will cancel all bookings.",
        "proceed_with_caution": true,
        "affected_bookings": 15
    }
    
    Generate a confirmation message for this high-risk action.
    """
    
    messages = [
        {"role": "system", "content": CONFIRMATION_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    print(f"\n📤 Calling Claude to generate confirmation message for HIGH RISK action")

    try:
        response = await client.chat_completion(
            model=settings.CLAUDE_MODEL,
            messages=messages,
            temperature=0.5,  # Slightly higher for more natural language
            max_tokens=1000,
        )
    except Exception as e:
        print(f"   Falling back to: anthropic/claude-sonnet-4")
        response = await client.chat_completion(
            model="anthropic/claude-sonnet-4",
            messages=messages,
            temperature=0.5,
            max_tokens=1000,
        )
    
    content = response["choices"][0]["message"]["content"]
    print(f"\n📥 Claude Response:")
    print(content)
    
    # Try to parse as JSON
    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        parsed = json.loads(content)
        print(f"\n✅ Successfully parsed JSON response")
        print(f"\nConfirmation Message:\n{parsed.get('confirmation_message')}")
        print(f"\nRisk Summary: {parsed.get('risk_summary')}")
        
        # Validate
        assert parsed.get('confirmation_message') is not None, "Missing confirmation_message"
        assert len(parsed.get('confirmation_message', '')) > 50, "Confirmation message too short"
        assert parsed.get('risk_summary') is not None, "Missing risk_summary"
        
        print("\n✅ Confirmation message validation passed!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Failed to parse JSON: {e}")
        return False
    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        return False


async def main():
    """Run all Phase 2 API tests."""
    print("\n" + "🧪 PHASE 2 API TESTS - Testing Prompts with OpenRouter Claude")
    print("="*60)
    
    # Test 1: Classification
    test1_passed = await test_classification_prompt()
    
    # Test 2: Confirmation
    test2_passed = await test_confirmation_prompt()
    
    print("\n" + "="*60)
    print("PHASE 2 API TEST RESULTS")
    print("="*60)
    print(f"Test 1 (Classification): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (Confirmation):   {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All Phase 2 API tests PASSED!")
        return 0
    else:
        print("\n❌ Some Phase 2 API tests FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
