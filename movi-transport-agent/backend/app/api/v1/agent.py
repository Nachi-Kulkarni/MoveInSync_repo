"""
Agent API Endpoints (TICKET #7)

REST API endpoints for agent interaction:
- POST /api/v1/agent/message - Send message to agent
- POST /api/v1/agent/confirm - Confirm high-risk action
- GET /api/v1/agent/session/{session_id} - Get session status
"""

from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.schemas.agent import (
    AgentMessageRequest,
    AgentConfirmationRequest,
    AgentResponse,
    ConversationMessage,
    SessionHistoryResponse,
    SessionStatusResponse,
)
from app.agent.graph import run_movi_agent
from app.services.session_service import session_service
from app.utils.tts import get_tts_client
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])


class TTSRequest(BaseModel):
    """Request schema for TTS generation."""
    text: str
    voice: str = "coral"
    streaming: bool = False


@router.post(
    "/message",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to Movi Transport Agent",
    description="""
    Send a text, voice, image, or video message to the Movi Transport Agent.

    The agent will:
    1. Process multimodal input (Gemini 2.5 Pro)
    2. Classify intent (Claude Sonnet 4.5)
    3. Check consequences if high-risk (Database)
    4. Request confirmation if needed (Claude Sonnet 4.5)
    5. Execute action via tools (TOOL_REGISTRY)
    6. Format response (Claude Sonnet 4.5)

    If the action requires confirmation, the response will have:
    - response_type: "confirmation"
    - requires_confirmation: true
    - confirmation_message: "Message explaining consequences"

    The frontend should then show a confirmation dialog and call POST /agent/confirm.
    """,
)
async def send_message(request: AgentMessageRequest) -> AgentResponse:
    """
    Send a message to the agent and get a response.

    Args:
        request: AgentMessageRequest with user input, session ID, context, etc.

    Returns:
        AgentResponse with formatted message and metadata

    Raises:
        HTTPException: If agent execution fails
    """
    try:
        logger.info(
            f"Agent message received: session={request.session_id}, "
            f"input_length={len(request.user_input)}, "
            f"page={request.context.get('page')}"
        )

        # Convert multimodal_data to dict if provided
        multimodal_dict = None
        if request.multimodal_data:
            multimodal_dict = request.multimodal_data.model_dump()

        # Run the agent graph
        result = await run_movi_agent(
            user_input=request.user_input,
            session_id=request.session_id,
            context=request.context,
            multimodal_data=multimodal_dict,
            user_confirmed=request.user_confirmed,
        )

        # Persist session with conversation turn
        try:
            session = await session_service.create_or_update_session(
                session_id=request.session_id,
                user_input=request.user_input,
                agent_response=result["response"],
                context=request.context,
                current_state=result,  # Store the complete agent state
                user_id=request.context.get("user_id")
            )
            logger.debug(f"Session persisted: {request.session_id}")
        except Exception as e:
            # Don't fail the request if session persistence fails, just log it
            logger.warning(f"Session persistence failed for {request.session_id}: {e}")

        # Prepare response with enhanced fields
        ui_action = None
        if result.get("requires_confirmation"):
            ui_action = {
                "type": "show_confirmation",
                "message": result.get("confirmation_message", "Please confirm this action"),
                "action_id": result.get("tool_name"),
                "risk_level": result.get("risk_level", "medium")
            }
        elif result.get("tool_results") and result.get("action_type") in ["create", "update", "write"]:
            ui_action = {
                "type": "refresh_ui",
                "target": result.get("tool_name"),
                "message": f"Data updated by {result.get('tool_name')}"
            }

        # Convert result to AgentResponse with enhanced fields
        response = AgentResponse(
            response=result["response"],
            response_type=result["response_type"],
            session_id=result["session_id"],
            intent=result.get("intent"),
            action_type=result.get("action_type"),
            tool_name=result.get("tool_name"),
            execution_success=result.get("execution_success"),
            requires_confirmation=result.get("requires_confirmation", False),
            confirmation_message=result.get("confirmation_message"),
            error=result.get("error"),
            metadata=result.get("tool_results"),  # Include tool results in metadata
            audio_url=None,  # TTS support will be added in TICKET #9
            ui_action=ui_action,  # UI action suggestions
        )

        logger.info(
            f"Agent response: session={request.session_id}, "
            f"type={response.response_type}, "
            f"intent={response.intent}, "
            f"requires_confirmation={response.requires_confirmation}, "
            f"ui_action={bool(response.ui_action)}"
        )

        return response

    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}",
        )


@router.post(
    "/confirm",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm or cancel high-risk action",
    description="""
    After receiving a confirmation request from POST /agent/message,
    the user can confirm or cancel the action using this endpoint.

    If confirmed=true, the agent will:
    - Execute the high-risk action
    - Return success or error response

    If confirmed=false, the agent will:
    - Cancel the action
    - Return info message saying action was cancelled
    """,
)
async def confirm_action(request: AgentConfirmationRequest) -> AgentResponse:
    """
    Confirm or cancel a high-risk action.

    Args:
        request: AgentConfirmationRequest with session ID and confirmation status

    Returns:
        AgentResponse with execution result or cancellation message

    Raises:
        HTTPException: If agent execution fails
    """
    try:
        logger.info(
            f"Confirmation received: session={request.session_id}, "
            f"confirmed={request.confirmed}"
        )

        if not request.confirmed:
            # User cancelled - return info message
            return AgentResponse(
                response="Action cancelled by user.",
                response_type="info",
                session_id=request.session_id,
                intent=None,
                action_type=None,
                tool_name=None,
                execution_success=False,
                requires_confirmation=False,
                confirmation_message=None,
                error=None,
                metadata={"cancelled": True},
            )

        # User confirmed - re-run agent with user_confirmed=True
        result = await run_movi_agent(
            user_input=request.user_input,
            session_id=request.session_id,
            context=request.context,
            multimodal_data=None,
            user_confirmed=True,  # This will skip confirmation and execute
        )

        # Convert result to AgentResponse
        response = AgentResponse(
            response=result["response"],
            response_type=result["response_type"],
            session_id=result["session_id"],
            intent=result.get("intent"),
            action_type=result.get("action_type"),
            tool_name=result.get("tool_name"),
            execution_success=result.get("execution_success"),
            requires_confirmation=False,  # Should be False after execution
            confirmation_message=None,
            error=result.get("error"),
            metadata={"confirmed": True},
        )

        logger.info(
            f"Confirmed action executed: session={request.session_id}, "
            f"success={response.execution_success}"
        )

        return response

    except Exception as e:
        logger.error(f"Confirmation handling failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Confirmation handling failed: {str(e)}",
        )


@router.get(
    "/session/{session_id}",
    response_model=SessionStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get session status",
    description="""
    Get the current status of an agent session.

    This endpoint is useful for:
    - Checking if a session is still active
    - Getting the number of messages exchanged
    - Checking if there's a pending confirmation action

    Note: Session persistence is not yet fully implemented (TICKET #5 - session.py).
    This endpoint currently returns mock data.
    """,
)
async def get_session_status(session_id: str) -> SessionStatusResponse:
    """
    Get session status.

    Args:
        session_id: Session identifier

    Returns:
        SessionStatusResponse with session metadata

    Raises:
        HTTPException: If session not found
    """
    try:
        logger.info(f"Session status requested: session={session_id}")

        # Get real session data from database
        session_stats = await session_service.get_session_stats(session_id)

        if not session_stats:
            # Session not found
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        # Check if there's a pending confirmation in the current state
        pending_confirmation = False
        if session_stats.get("current_state"):
            pending_confirmation = session_stats["current_state"].get("requires_confirmation", False)

        response = SessionStatusResponse(
            session_id=session_id,
            active=session_stats["is_active"],
            message_count=session_stats["total_messages"],
            last_activity=datetime.fromisoformat(session_stats["last_message_at"]) if session_stats.get("last_message_at") else datetime.utcnow(),
            pending_confirmation=pending_confirmation,
            conversation_turns=session_stats["conversation_turns"],
            created_at=datetime.fromisoformat(session_stats["created_at"]) if session_stats.get("created_at") else None
        )

        logger.info(
            f"Session status retrieved: session={session_id}, "
            f"active={response.active}, "
            f"messages={response.message_count}, "
            f"turns={response.conversation_turns}"
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Session status retrieval failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session {session_id}: {str(e)}",
        )


@router.get(
    "/session/{session_id}/history",
    response_model=SessionHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get full conversation history",
    description="""
    Get the complete conversation history for a session.

    This endpoint returns:
    - All user and agent messages in chronological order
    - Session metadata (creation time, message counts, etc.)
    - Whether the session is still active

    Useful for:
    - Displaying conversation history in chat interfaces
    - Debugging conversation flows
    - Session analytics and analysis
    """,
)
async def get_session_history(session_id: str) -> SessionHistoryResponse:
    """
    Get full conversation history for a session.

    Args:
        session_id: Session identifier

    Returns:
        SessionHistoryResponse with complete conversation history

    Raises:
        HTTPException: If session not found
    """
    try:
        logger.info(f"Session history requested: session={session_id}")

        # Get session data
        session = await session_service.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        # Get conversation history
        conversation_history = await session_service.get_session_history(session_id)

        # Convert to ConversationMessage objects
        conversation_messages = []
        for msg in conversation_history:
            try:
                conversation_messages.append(
                    ConversationMessage(
                        role=msg["role"],
                        content=msg["content"],
                        timestamp=datetime.fromisoformat(msg["timestamp"])
                    )
                )
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping malformed message in session {session_id}: {e}")
                continue

        # Count user and agent messages
        user_messages = len([msg for msg in conversation_messages if msg.role == "user"])
        agent_messages = len([msg for msg in conversation_messages if msg.role == "agent"])
        conversation_turns = min(user_messages, agent_messages)

        response = SessionHistoryResponse(
            session_id=session_id,
            active=bool(session.is_active),
            conversation_history=conversation_messages,
            total_messages=len(conversation_messages),
            user_messages=user_messages,
            agent_messages=agent_messages,
            conversation_turns=conversation_turns,
            created_at=session.created_at,
            last_message_at=session.last_message_at
        )

        logger.info(
            f"Session history retrieved: session={session_id}, "
            f"messages={response.total_messages}, "
            f"turns={response.conversation_turns}"
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        logger.error(f"Session history retrieval failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session history for {session_id}: {str(e)}",
        )


@router.post(
    "/session/cleanup",
    status_code=status.HTTP_200_OK,
    summary="Cleanup expired sessions",
    description="""
    Clean up sessions that have expired based on TTL (24 hours of inactivity).

    This endpoint:
    - Deletes sessions older than 24 hours
    - Returns number of sessions cleaned up
    - Useful for maintenance and database cleanup

    Note: This is an admin endpoint for maintenance purposes.
    """,
)
async def cleanup_expired_sessions(session_id: str = None) -> Dict[str, int]:
    """
    Clean up expired sessions.

    Returns:
        Dictionary with number of sessions cleaned up
    """
    try:
        logger.info("Starting expired session cleanup")

        cleaned_count = await session_service.cleanup_expired_sessions()

        logger.info(f"Session cleanup completed: {cleaned_count} sessions removed")

        return {"cleaned_sessions": cleaned_count}

    except Exception as e:
        logger.error(f"Session cleanup failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session cleanup failed: {str(e)}",
        )


@router.post(
    "/tts",
    status_code=status.HTTP_200_OK,
    summary="Generate Text-to-Speech audio",
    description="""
    Generate speech audio from text using OpenAI TTS.

    This endpoint:
    - Converts text responses to speech using OpenAI's TTS model
    - Returns audio in MP3 format (default) or streaming WAV
    - Supports multiple voices (default: "coral" - warm and friendly)
    - Used by frontend for automatic voice output of agent responses

    Response:
    - Non-streaming: Returns audio/mp3 file
    - Streaming: Returns audio/wav stream for real-time playback
    """,
)
async def generate_tts(request: TTSRequest):
    """
    Generate TTS audio from text.

    Args:
        request: TTSRequest with text, voice, and streaming options

    Returns:
        StreamingResponse with audio content

    Raises:
        HTTPException: If TTS generation fails
    """
    try:
        logger.info(f"TTS request received: text_length={len(request.text)}, voice={request.voice}, streaming={request.streaming}")

        tts_client = get_tts_client()

        if request.streaming:
            # Streaming response for real-time playback
            async def audio_stream():
                async for chunk in tts_client.generate_speech_streaming(
                    text=request.text,
                    voice=request.voice,
                    response_format="wav"
                ):
                    yield chunk

            return StreamingResponse(
                audio_stream(),
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "inline; filename=speech.wav",
                    "Cache-Control": "no-cache"
                }
            )
        else:
            # Non-streaming response (MP3)
            audio_bytes = await tts_client.generate_speech(
                text=request.text,
                voice=request.voice,
                response_format="mp3"
            )

            logger.info(f"TTS generated successfully: audio_size={len(audio_bytes)} bytes")

            return StreamingResponse(
                iter([audio_bytes]),
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": "inline; filename=speech.mp3",
                    "Content-Length": str(len(audio_bytes)),
                    "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
                }
            )

    except Exception as e:
        logger.error(f"TTS generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS generation failed: {str(e)}",
        )


# Export router
__all__ = ["router"]
