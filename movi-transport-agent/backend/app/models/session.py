"""
Agent Session Model for persisting conversation state (TICKET #5)

This model stores agent session data including:
- Session ID (for conversation continuity)
- User context (page, preferences)
- Conversation history
- Current state snapshot
- Timestamps for session management
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class AgentSession(Base):
    """
    Agent session persistence for conversation continuity.
    
    Stores full conversation history and state snapshots to enable:
    - Multi-turn conversations
    - Context awareness across requests
    - Session resumption after interruptions
    - Debugging and analytics
    """
    
    __tablename__ = "agent_sessions"
    
    # Primary key
    session_id = Column(String(100), primary_key=True, index=True)
    
    # User context
    user_id = Column(String(100), nullable=True, index=True)  # Optional user identification
    page_context = Column(String(50), nullable=True)  # "busDashboard" or "manageRoute"
    
    # Conversation data (stored as JSON)
    conversation_history = Column(JSON, nullable=False, default=list)
    # Format: [{"role": "user", "content": "...", "timestamp": "..."}, ...]
    
    # Current state snapshot (AgentState as JSON)
    current_state = Column(JSON, nullable=True)
    
    # Session metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Session status
    is_active = Column(Integer, default=1, nullable=False)  # 1=active, 0=closed
    
    # Optional: Store last error for debugging
    last_error = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AgentSession(session_id={self.session_id}, user_id={self.user_id}, active={self.is_active})>"
    
    def to_dict(self):
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "page_context": self.page_context,
            "conversation_history": self.conversation_history,
            "current_state": self.current_state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "is_active": bool(self.is_active),
            "last_error": self.last_error,
        }
