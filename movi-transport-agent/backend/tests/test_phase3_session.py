"""
Phase 3 Test - Session Persistence Model
Tests database table and SQLAlchemy model functionality
"""

import asyncio
import json
from datetime import datetime, UTC
from sqlalchemy import select, text

from app.core.database import AsyncSessionLocal
from app.models.session import AgentSession
from app.utils.openrouter import OpenRouterClient
from app.core.config import settings
from app.agent.prompts import CLASSIFICATION_SYSTEM_PROMPT


async def test_session_model():
    """Test AgentSession model CRUD operations."""
    print("\n" + "="*60)
    print("PHASE 3 TEST: Session Persistence Model")
    print("="*60)

    async with AsyncSessionLocal() as db:
        # Cleanup: Delete any existing test sessions
        result = await db.execute(
            select(AgentSession).where(AgentSession.session_id == "test-session-123")
        )
        existing = result.scalar_one_or_none()
        if existing:
            await db.delete(existing)
            await db.commit()
            print("Cleaned up existing test session\n")

        # Test 1: Create a new session
        print("✅ Test 1: Create new session")
        session_data = AgentSession(
            session_id="test-session-123",
            user_id="user-456",
            page_context="busDashboard",
            conversation_history=[
                {"role": "user", "content": "How many unassigned vehicles?", "timestamp": datetime.now(UTC).isoformat()},
                {"role": "assistant", "content": "There are 3 unassigned vehicles.", "timestamp": datetime.now(UTC).isoformat()}
            ],
            current_state={
                "session_id": "test-session-123",
                "intent": "list_unassigned_vehicles",
                "action_type": "read",
                "execution_success": True
            },
            is_active=1
        )
        
        db.add(session_data)
        await db.commit()
        print(f"   Created session: {session_data.session_id}")
        print(f"   User ID: {session_data.user_id}")
        print(f"   Page Context: {session_data.page_context}")
        print(f"   Conversation Messages: {len(session_data.conversation_history)}")
        
        # Test 2: Read the session back
        print("\n✅ Test 2: Read session from database")
        result = await db.execute(
            select(AgentSession).where(AgentSession.session_id == "test-session-123")
        )
        retrieved_session = result.scalar_one_or_none()
        
        assert retrieved_session is not None, "Session not found in database"
        assert retrieved_session.session_id == "test-session-123"
        assert retrieved_session.user_id == "user-456"
        assert retrieved_session.page_context == "busDashboard"
        assert len(retrieved_session.conversation_history) == 2
        assert retrieved_session.current_state["intent"] == "list_unassigned_vehicles"
        print(f"   Retrieved session: {retrieved_session.session_id}")
        print(f"   Conversation history intact: {len(retrieved_session.conversation_history)} messages")
        print(f"   Current state preserved: intent={retrieved_session.current_state['intent']}")
        
        # Test 3: Update session
        print("\n✅ Test 3: Update session")
        # Must reassign to trigger SQLAlchemy change detection for JSON columns
        new_history = retrieved_session.conversation_history.copy()
        new_history.append({
            "role": "user",
            "content": "Remove vehicle from Bulk - 00:01",
            "timestamp": datetime.now(UTC).isoformat()
        })
        retrieved_session.conversation_history = new_history

        new_state = retrieved_session.current_state.copy()
        new_state["intent"] = "remove_vehicle"
        retrieved_session.current_state = new_state

        retrieved_session.last_message_at = datetime.now(UTC)

        await db.commit()
        await db.refresh(retrieved_session)

        assert len(retrieved_session.conversation_history) == 3
        assert retrieved_session.current_state["intent"] == "remove_vehicle"
        print(f"   Updated conversation: {len(retrieved_session.conversation_history)} messages")
        print(f"   Updated state: intent={retrieved_session.current_state['intent']}")
        
        # Test 4: to_dict method
        print("\n✅ Test 4: to_dict() serialization")
        session_dict = retrieved_session.to_dict()
        assert "session_id" in session_dict
        assert "conversation_history" in session_dict
        assert "current_state" in session_dict
        print(f"   Serialized to dict: {list(session_dict.keys())}")
        
        # Test 5: Query by user_id (index test)
        print("\n✅ Test 5: Query by user_id (index test)")
        result = await db.execute(
            select(AgentSession).where(AgentSession.user_id == "user-456")
        )
        user_sessions = result.scalars().all()
        assert len(user_sessions) == 1
        print(f"   Found {len(user_sessions)} session(s) for user-456")
        
        # Test 6: Check table schema
        print("\n✅ Test 6: Verify table schema")
        result = await db.execute(text("PRAGMA table_info(agent_sessions)"))
        columns = result.fetchall()
        column_names = [col[1] for col in columns]
        expected_columns = [
            'session_id', 'user_id', 'page_context', 
            'conversation_history', 'current_state',
            'created_at', 'updated_at', 'last_message_at',
            'is_active', 'last_error'
        ]
        for expected in expected_columns:
            assert expected in column_names, f"Missing column: {expected}"
        print(f"   All expected columns present: {len(column_names)} columns")
        
        # Test 7: Check indexes
        print("\n✅ Test 7: Verify indexes")
        result = await db.execute(text("PRAGMA index_list(agent_sessions)"))
        indexes = result.fetchall()
        index_names = [idx[1] for idx in indexes]
        assert any('user_id' in name for name in index_names), "Missing user_id index"
        assert any('is_active' in name for name in index_names), "Missing is_active index"
        print(f"   Indexes verified: {index_names}")
        
        # Test 8: Real OpenRouter API call with session persistence
        print("\n✅ Test 8: Real API call + session persistence")

        # Create a new session for API test
        api_session = AgentSession(
            session_id="api-test-session",
            user_id="api-user",
            page_context="busDashboard",
            conversation_history=[],
            is_active=1
        )
        db.add(api_session)
        await db.commit()

        # Make real OpenRouter call
        client = OpenRouterClient()
        user_message = "Remove vehicle MH-12-3456 from Bulk - 00:01 trip"

        messages = [
            {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

        print(f"   Calling Claude API: '{user_message}'")

        try:
            response = await client.chat_completion(
                model="x-ai/grok-4-fast",
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
            )
        except Exception as e:
            print(f"   Falling back to anthropic/claude-sonnet-4")
            response = await client.chat_completion(
                model="anthropic/claude-sonnet-4",
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
            )

        assistant_message = response["choices"][0]["message"]["content"]
        print(f"   Received {len(assistant_message)} chars response")

        # Parse Claude's response
        try:
            if "```json" in assistant_message:
                assistant_message = assistant_message.split("```json")[1].split("```")[0].strip()
            parsed_response = json.loads(assistant_message)
            print(f"   Parsed intent: {parsed_response.get('intent')}")
            print(f"   Action type: {parsed_response.get('action_type')}")
        except:
            parsed_response = {"raw": assistant_message}

        # Store conversation in session
        new_history = api_session.conversation_history.copy()
        new_history.extend([
            {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now(UTC).isoformat()
            },
            {
                "role": "assistant",
                "content": assistant_message,
                "parsed": parsed_response,
                "timestamp": datetime.now(UTC).isoformat()
            }
        ])
        api_session.conversation_history = new_history
        api_session.current_state = parsed_response
        api_session.last_message_at = datetime.now(UTC)

        await db.commit()
        await db.refresh(api_session)

        # Verify persistence
        assert len(api_session.conversation_history) == 2
        assert api_session.conversation_history[0]["role"] == "user"
        assert api_session.conversation_history[1]["role"] == "assistant"
        assert api_session.current_state.get("intent") is not None
        print(f"   ✅ API response stored in session: {len(api_session.conversation_history)} messages")
        print(f"   ✅ Intent preserved: {api_session.current_state.get('intent')}")

        # Cleanup API test session
        await db.delete(api_session)
        await db.commit()

        # Cleanup original test session
        await db.delete(retrieved_session)
        await db.commit()
        print("\n✅ Cleanup: Test sessions deleted")

        await client.close()

    print("\n" + "="*60)
    print("🎉 All Phase 3 tests PASSED (including real API calls)!")
    print("="*60)
    return True


async def main():
    """Run Phase 3 tests."""
    try:
        success = await test_session_model()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Phase 3 test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
