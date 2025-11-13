"""
Agent Request/Response Schemas (TICKET #7)

Pydantic models for agent API endpoints.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


# Request Schemas
class MultimodalData(BaseModel):
    """Multimodal input data."""
    images: Optional[List[str]] = Field(
        None,
        description="List of image URLs or base64-encoded images"
    )
    audio: Optional[str] = Field(
        None,
        description="Audio URL or base64-encoded audio"
    )
    video: Optional[str] = Field(
        None,
        description="Video URL or base64-encoded video"
    )


class AgentMessageRequest(BaseModel):
    """Request schema for agent message endpoint."""
    user_input: str = Field(
        ...,
        description="User's text input",
        min_length=1,
        max_length=1000,
        examples=["Show me all unassigned vehicles"]
    )
    session_id: str = Field(
        ...,
        description="Unique session identifier for conversation continuity",
        min_length=1,
        max_length=100,
        examples=["session-123"]
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Current UI context (page, filters, active items, user role)",
        examples=[
            {
                "page": "busDashboard",
                "user_role": "transport_manager",
                "active_trip": "Bulk - 00:01"
            }
        ]
    )
    multimodal_data: Optional[MultimodalData] = Field(
        None,
        description="Optional multimodal inputs (images, audio, video)"
    )
    user_confirmed: bool = Field(
        False,
        description="Whether user has confirmed a high-risk action"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "Remove vehicle from Bulk - 00:01 trip",
                "session_id": "session-456",
                "context": {
                    "page": "busDashboard",
                    "user_role": "admin"
                },
                "user_confirmed": False
            }
        }


class AgentConfirmationRequest(BaseModel):
    """Request schema for confirmation endpoint."""
    session_id: str = Field(
        ...,
        description="Session identifier for the action to confirm",
        examples=["session-456"]
    )
    user_input: str = Field(
        ...,
        description="Original user input that triggered confirmation",
        examples=["Remove vehicle from Bulk - 00:01 trip"]
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Original context from the message request"
    )
    confirmed: bool = Field(
        ...,
        description="Whether user confirmed (True) or cancelled (False)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-456",
                "user_input": "Remove vehicle from Bulk - 00:01 trip",
                "context": {"page": "busDashboard"},
                "confirmed": True
            }
        }


# Response Schemas
class AgentResponse(BaseModel):
    """Response schema for agent endpoints."""
    response: str = Field(
        ...,
        description="Agent's formatted response message"
    )
    response_type: str = Field(
        ...,
        description="Type of response: 'success', 'error', 'info', 'warning', 'confirmation'"
    )
    session_id: str = Field(
        ...,
        description="Session identifier"
    )
    intent: Optional[str] = Field(
        None,
        description="Classified intent of the user's request"
    )
    action_type: Optional[str] = Field(
        None,
        description="Type of action: 'read', 'write', 'delete', 'unknown'"
    )
    tool_name: Optional[str] = Field(
        None,
        description="Name of the tool that was executed"
    )
    execution_success: Optional[bool] = Field(
        None,
        description="Whether tool execution succeeded (None if not executed)"
    )
    requires_confirmation: bool = Field(
        False,
        description="Whether action requires user confirmation before execution"
    )
    confirmation_message: Optional[str] = Field(
        None,
        description="Message explaining what will happen if user confirms"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if something went wrong"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata (extracted entities, tool results, etc.)"
    )
    audio_url: Optional[str] = Field(
        None,
        description="URL to generated TTS audio for the response (for TICKET #9)"
    )
    ui_action: Optional[Dict[str, Any]] = Field(
        None,
        description="UI action suggestions (e.g., highlight elements, show confirmations)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "There are 3 unassigned vehicles available.",
                "response_type": "success",
                "session_id": "session-123",
                "intent": "list_unassigned_vehicles",
                "action_type": "read",
                "tool_name": "get_unassigned_vehicles_count",
                "execution_success": True,
                "requires_confirmation": False,
                "confirmation_message": None,
                "error": None,
                "metadata": {
                    "unassigned_count": 3
                },
                "timestamp": "2025-11-13T14:30:00.000Z"
            }
        }


class ConversationMessage(BaseModel):
    """Single message in conversation history."""
    role: str = Field(..., description="Message role: 'user' or 'agent'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Show me all unassigned vehicles",
                "timestamp": "2025-11-13T14:30:00.000Z"
            }
        }


class SessionHistoryResponse(BaseModel):
    """Response schema for session history endpoint."""
    session_id: str = Field(..., description="Session identifier")
    active: bool = Field(..., description="Whether session is still active")
    conversation_history: List[ConversationMessage] = Field(
        ..., description="Full conversation history"
    )
    total_messages: int = Field(..., description="Total number of messages")
    user_messages: int = Field(..., description="Number of user messages")
    agent_messages: int = Field(..., description="Number of agent messages")
    conversation_turns: int = Field(..., description="Number of conversation turns")
    created_at: datetime = Field(..., description="Session creation time")
    last_message_at: Optional[datetime] = Field(None, description="Last message time")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-123",
                "active": True,
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Show me all unassigned vehicles",
                        "timestamp": "2025-11-13T14:30:00.000Z"
                    },
                    {
                        "role": "agent",
                        "content": "There are 3 unassigned vehicles available.",
                        "timestamp": "2025-11-13T14:30:05.000Z"
                    }
                ],
                "total_messages": 2,
                "user_messages": 1,
                "agent_messages": 1,
                "conversation_turns": 1,
                "created_at": "2025-11-13T14:30:00.000Z",
                "last_message_at": "2025-11-13T14:30:05.000Z"
            }
        }


class SessionStatusResponse(BaseModel):
    """Response schema for session status endpoint."""
    session_id: str = Field(
        ...,
        description="Session identifier"
    )
    active: bool = Field(
        ...,
        description="Whether session is still active"
    )
    message_count: int = Field(
        ...,
        description="Number of messages in session"
    )
    last_activity: datetime = Field(
        ...,
        description="Timestamp of last activity"
    )
    pending_confirmation: bool = Field(
        False,
        description="Whether there's a pending confirmation action"
    )
    conversation_turns: int = Field(
        default=0,
        description="Number of complete conversation turns"
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Session creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-123",
                "active": True,
                "message_count": 5,
                "last_activity": "2025-11-13T14:30:00.000Z",
                "pending_confirmation": False,
                "conversation_turns": 2,
                "created_at": "2025-11-13T14:25:00.000Z"
            }
        }


# Export all schemas
__all__ = [
    "MultimodalData",
    "AgentMessageRequest",
    "AgentConfirmationRequest",
    "AgentResponse",
    "ConversationMessage",
    "SessionHistoryResponse",
    "SessionStatusResponse",
]
