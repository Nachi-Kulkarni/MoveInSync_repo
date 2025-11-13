"""
Session Service for Agent Session Management

Handles all session-related operations including:
- Creating and retrieving sessions
- Managing conversation history
- Session TTL and cleanup
- State persistence
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func

from app.models.session import AgentSession
from app.api.deps import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Session TTL settings
SESSION_TTL_HOURS = 24  # Sessions expire after 24 hours of inactivity
CLEANUP_BATCH_SIZE = 100  # Number of sessions to clean up per run


class SessionService:
    """Service for managing agent sessions."""

    @staticmethod
    async def create_or_update_session(
        session_id: str,
        user_input: str,
        agent_response: str,
        context: Dict[str, Any],
        current_state: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> AgentSession:
        """
        Create a new session or update existing session with new conversation turn.

        Args:
            session_id: Unique session identifier
            user_input: User's input message
            agent_response: Agent's response
            context: UI context (page, etc.)
            current_state: Current agent state snapshot
            user_id: Optional user identifier

        Returns:
            Updated AgentSession object
        """
        async for db in get_db():
            try:
                # Try to get existing session
                result = await db.execute(
                    select(AgentSession).where(AgentSession.session_id == session_id)
                )
                session = result.scalar_one_or_none()

                if session:
                    # Update existing session
                    now = datetime.utcnow()

                    # Add new conversation turn
                    conversation_history = session.conversation_history or []
                    conversation_history.append({
                        "role": "user",
                        "content": user_input,
                        "timestamp": now.isoformat()
                    })
                    conversation_history.append({
                        "role": "agent",
                        "content": agent_response,
                        "timestamp": now.isoformat()
                    })

                    # Update session
                    await db.execute(
                        update(AgentSession)
                        .where(AgentSession.session_id == session_id)
                        .values(
                            conversation_history=conversation_history,
                            current_state=current_state,
                            page_context=context.get("page"),
                            updated_at=now,
                            last_message_at=now,
                            is_active=1  # Ensure session is marked as active
                        )
                    )

                    logger.info(f"Updated existing session: {session_id} (history length: {len(conversation_history)})")

                else:
                    # Create new session
                    now = datetime.utcnow()
                    conversation_history = [
                        {
                            "role": "user",
                            "content": user_input,
                            "timestamp": now.isoformat()
                        },
                        {
                            "role": "agent",
                            "content": agent_response,
                            "timestamp": now.isoformat()
                        }
                    ]

                    session = AgentSession(
                        session_id=session_id,
                        user_id=user_id,
                        page_context=context.get("page"),
                        conversation_history=conversation_history,
                        current_state=current_state,
                        created_at=now,
                        updated_at=now,
                        last_message_at=now,
                        is_active=1
                    )

                    db.add(session)
                    logger.info(f"Created new session: {session_id}")

                await db.commit()

                # Refresh to get updated data
                await db.refresh(session)
                return session

            except Exception as e:
                await db.rollback()
                logger.error(f"Failed to create/update session {session_id}: {e}")
                raise

    @staticmethod
    async def get_session(session_id: str) -> Optional[AgentSession]:
        """
        Retrieve session by ID.

        Args:
            session_id: Session identifier

        Returns:
            AgentSession object or None if not found
        """
        async for db in get_db():
            try:
                result = await db.execute(
                    select(AgentSession).where(AgentSession.session_id == session_id)
                )
                session = result.scalar_one_or_none()

                if session:
                    logger.debug(f"Retrieved session: {session_id} (active: {session.is_active})")

                return session

            except Exception as e:
                logger.error(f"Failed to retrieve session {session_id}: {e}")
                return None

    @staticmethod
    async def get_session_history(session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of conversation turns
        """
        session = await SessionService.get_session(session_id)
        if session:
            return session.conversation_history or []
        return []

    @staticmethod
    async def close_session(session_id: str) -> bool:
        """
        Mark session as closed.

        Args:
            session_id: Session identifier

        Returns:
            True if successfully closed, False otherwise
        """
        async for db in get_db():
            try:
                await db.execute(
                    update(AgentSession)
                    .where(AgentSession.session_id == session_id)
                    .values(
                        is_active=0,
                        updated_at=datetime.utcnow()
                    )
                )
                await db.commit()
                logger.info(f"Closed session: {session_id}")
                return True

            except Exception as e:
                await db.rollback()
                logger.error(f"Failed to close session {session_id}: {e}")
                return False

    @staticmethod
    async def cleanup_expired_sessions() -> int:
        """
        Clean up sessions that have expired based on TTL.

        Returns:
            Number of sessions cleaned up
        """
        async for db in get_db():
            try:
                # Calculate expiration threshold
                expiration_time = datetime.utcnow() - timedelta(hours=SESSION_TTL_HOURS)

                # Delete expired sessions
                result = await db.execute(
                    delete(AgentSession)
                    .where(
                        AgentSession.last_message_at < expiration_time
                    )
                )

                deleted_count = result.rowcount
                await db.commit()

                logger.info(f"Cleaned up {deleted_count} expired sessions (older than {SESSION_TTL_HOURS}h)")
                return deleted_count

            except Exception as e:
                await db.rollback()
                logger.error(f"Session cleanup failed: {e}")
                return 0

    @staticmethod
    async def get_session_stats(session_id: str) -> Dict[str, Any]:
        """
        Get session statistics.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session stats
        """
        session = await SessionService.get_session(session_id)
        if not session:
            return {}

        conversation_history = session.conversation_history or []

        # Count user and agent messages
        user_messages = len([msg for msg in conversation_history if msg.get("role") == "user"])
        agent_messages = len([msg for msg in conversation_history if msg.get("role") == "agent"])

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "page_context": session.page_context,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "updated_at": session.updated_at.isoformat() if session.updated_at else None,
            "last_message_at": session.last_message_at.isoformat() if session.last_message_at else None,
            "is_active": bool(session.is_active),
            "total_messages": len(conversation_history),
            "user_messages": user_messages,
            "agent_messages": agent_messages,
            "conversation_turns": min(user_messages, agent_messages),  # Each turn has user + agent
            "has_pending_error": bool(session.last_error),
            "last_error": session.last_error
        }


# Singleton instance
session_service = SessionService()