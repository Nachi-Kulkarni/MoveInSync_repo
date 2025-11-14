"""
AgentState TypedDict for LangGraph StateGraph (TICKET #5)

This defines the state schema that flows through all 6 nodes.
State is immutable - each node returns updates that get merged.
"""

from typing import TypedDict, Optional, List, Dict, Any, Literal
from datetime import datetime


class AgentState(TypedDict, total=False):
    """
    State schema for the Movi Transport Agent LangGraph.

    Flow:
    1. preprocess_input_node: Sets user_input, processed_input, context
    2. classify_intent_node: Sets intent, extracted_entities, action_plan
    3. check_consequences_node: Sets consequences (if needed)
    4. request_confirmation_node: Sets confirmation_required, confirmation_message
    5. execute_action_node: Sets tool_results, execution_success
    6. format_response_node: Sets final_response

    Conditional edges use: action_type, requires_confirmation, execution_success
    """

    # ========== Input Processing (Node 1) ==========
    user_input: str  # Original user input (text/audio/image/video)
    input_modalities: List[str]  # ["text", "image", "audio", "video"]
    processed_input: Dict[str, Any]  # Output from GeminiMultimodalProcessor
    context: Dict[str, Any]  # Page context, session info
    multimodal_data: Optional[Dict[str, Any]]  # Multimodal inputs (images, audio, video)

    # ========== Intent Classification (Node 2) ==========
    intent: Optional[str]  # "list_trips", "remove_vehicle", "create_stop", etc.
    action_type: Optional[Literal["read", "write", "delete"]]  # For edge routing
    extracted_entities: Dict[str, Any]  # trip_ids, vehicle_ids, stop_names, etc.
    action_plan: Optional[str]  # Natural language explanation of what will be done
    requires_consequence_check: bool  # From TOOL_METADATA_REGISTRY

    # ========== Consequence Checking (Node 3) ==========
    consequences: Optional[Dict[str, Any]]  # ConsequenceResult from consequence_tools
    risk_level: Optional[Literal["none", "low", "high"]]  # none/low/high

    # ========== Confirmation Flow (Node 4) ==========
    requires_confirmation: bool  # True if high risk or user preference
    confirmation_message: Optional[str]  # Human-readable confirmation prompt
    user_confirmed: bool  # Set by API when user responds

    # ========== Tool Execution (Node 5) ==========
    tool_name: Optional[str]  # Name of tool to execute
    tool_params: Optional[Dict[str, Any]]  # Validated parameters
    tool_results: Optional[Dict[str, Any]]  # ToolResponse from execution
    execution_success: bool  # True if tool succeeded
    execution_error: Optional[str]  # Error message if failed

    # ========== Response Formatting (Node 6) ==========
    response: Optional[str]  # Human-readable response to user
    response_type: Optional[Literal["success", "error", "confirmation", "info"]]  # Response type for UI
    final_response: Optional[str]  # Legacy field (for backwards compatibility)
    response_metadata: Optional[Dict[str, Any]]  # Additional UI hints

    # ========== Session Management ==========
    session_id: str  # Persistent conversation session
    timestamp: str  # ISO format timestamp
    conversation_history: List[Dict[str, str]]  # Previous messages

    # ========== Error Handling ==========
    error: Optional[str]  # Set if any node encounters an error
    error_node: Optional[str]  # Which node raised the error


# State update helpers (for nodes to return)
def create_initial_state(
    user_input: str,
    session_id: str,
    context: Optional[Dict[str, Any]] = None,
    multimodal_data: Optional[Dict[str, Any]] = None
) -> AgentState:
    """Create initial state for a new agent invocation."""
    return {
        "user_input": user_input,
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "context": context or {},
        "multimodal_data": multimodal_data or {},  # ADD THIS!
        "input_modalities": [],
        "conversation_history": [],
        "requires_confirmation": False,
        "user_confirmed": False,
        "execution_success": False,
        "requires_consequence_check": False,
    }


def state_has_error(state: AgentState) -> bool:
    """Check if state contains an error."""
    return state.get("error") is not None


def get_state_summary(state: AgentState) -> Dict[str, Any]:
    """Get summary of current state for debugging."""
    return {
        "session_id": state.get("session_id"),
        "intent": state.get("intent"),
        "action_type": state.get("action_type"),
        "risk_level": state.get("risk_level"),
        "requires_confirmation": state.get("requires_confirmation"),
        "execution_success": state.get("execution_success"),
        "has_error": state_has_error(state),
    }
