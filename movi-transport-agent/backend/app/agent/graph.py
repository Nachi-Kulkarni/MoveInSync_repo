"""
LangGraph Workflow Definition (TICKET #5 - Phase 6)

This module assembles the complete Movi Transport Agent workflow using LangGraph.

Graph Structure:
START -> preprocess_input
       -> classify_intent
       -> [check_consequences?] (conditional)
       -> [request_confirmation?] (conditional)
       -> execute_action
       -> format_response
       -> END

Nodes:
1. preprocess_input - Multimodal input processing (Gemini 2.5 Pro)
2. classify_intent - Intent classification (Claude Sonnet 4.5)
3. check_consequences - Tribal knowledge consequence checking (Database)
4. request_confirmation - Confirmation message generation (Claude Sonnet 4.5)
5. execute_action - Tool execution (TOOL_REGISTRY)
6. format_response - Response formatting (Claude Sonnet 4.5)

Edges:
- Normal edges: START -> preprocess, format_response -> END
- Conditional edges: Based on state (errors, risk level, confirmation)
"""

import os
from typing import Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    preprocess_input_node,
    classify_intent_node,
    check_consequences_node,
    request_confirmation_node,
    execute_action_node,
    format_response_node,
)
from app.agent.edges import (
    route_after_classify,
    route_after_consequences,
    route_after_confirmation,
    route_after_execute,
)


# LangSmith tracing configuration
# Force enable tracing for observability
def _setup_langsmith():
    """Setup LangSmith tracing if API key is available"""
    try:
        from app.core.config import settings as config_settings
        api_key = os.getenv("LANGCHAIN_API_KEY", config_settings.LANGCHAIN_API_KEY)
    except (ImportError, AttributeError):
        api_key = os.getenv("LANGCHAIN_API_KEY", "")
    
    if api_key and api_key.strip():
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = api_key
        os.environ["LANGCHAIN_PROJECT"] = "movi-transport-agent"
        print("✅ LangSmith tracing ENABLED for Movi Transport Agent")
        print(f"   Project: movi-transport-agent")
        print(f"   Endpoint: https://api.smith.langchain.com")
        return True
    else:
        print("⚠️  LangSmith tracing DISABLED (no API key found)")
        return False

ENABLE_LANGSMITH = _setup_langsmith()


def create_movi_agent_graph() -> StateGraph:
    """
    Create and compile the Movi Transport Agent workflow graph.

    Returns:
        Compiled StateGraph ready for execution

    Graph Flow:
    -----------
    START
      |
      v
    preprocess_input (Gemini 2.5 Pro)
      |
      v
    classify_intent (Claude Sonnet 4.5)
      |
      +-- (error?) --> format_response --> END
      |
      +-- (requires_consequence_check=True?) --> check_consequences
      |                                            |
      |                                            +-- (error?) --> format_response
      |                                            |
      |                                            +-- (requires_confirmation=True?) --> request_confirmation
      |                                            |                                       |
      |                                            |                                       +-- (error?) --> format_response
      |                                            |                                       |
      |                                            |                                       +-- (user_confirmed=True?) --> execute_action
      |                                            |                                       |
      |                                            |                                       +-- (else) --> format_response (waiting)
      |                                            |
      |                                            +-- (else) --> execute_action
      |
      +-- (else) --> execute_action
                       |
                       v
                  format_response
                       |
                       v
                      END

    Key Features:
    - Consequence-first pipeline for high-risk actions
    - Conditional routing based on state
    - Error handling at every step
    - User confirmation for destructive operations
    - Multimodal input support (text, audio, image, video)
    - OpenRouter integration (Gemini + Claude)
    """
    # Create state graph
    workflow = StateGraph(AgentState)

    # Add nodes to the graph
    workflow.add_node("preprocess_input", preprocess_input_node)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("check_consequences", check_consequences_node)
    workflow.add_node("request_confirmation", request_confirmation_node)
    workflow.add_node("execute_action", execute_action_node)
    workflow.add_node("format_response", format_response_node)

    # Set entry point
    workflow.set_entry_point("preprocess_input")

    # Add normal edges (always executed in sequence)
    workflow.add_edge("preprocess_input", "classify_intent")

    # Add conditional edges (routing based on state)
    workflow.add_conditional_edges(
        "classify_intent",
        route_after_classify,
        {
            "check_consequences": "check_consequences",
            "execute_action": "execute_action",
            "format_response": "format_response",
        },
    )

    workflow.add_conditional_edges(
        "check_consequences",
        route_after_consequences,
        {
            "request_confirmation": "request_confirmation",
            "execute_action": "execute_action",
            "format_response": "format_response",
        },
    )

    workflow.add_conditional_edges(
        "request_confirmation",
        route_after_confirmation,
        {
            "execute_action": "execute_action",
            "format_response": "format_response",
        },
    )

    workflow.add_conditional_edges(
        "execute_action",
        route_after_execute,
        {
            "format_response": "format_response",
        },
    )

    # Terminal edge (always goes to END)
    workflow.add_edge("format_response", END)

    # Compile the graph
    compiled_graph = workflow.compile()

    return compiled_graph


# Create singleton instance
movi_agent_graph = create_movi_agent_graph()


async def run_movi_agent(
    user_input: str,
    session_id: str,
    context: Dict[str, Any],
    multimodal_data: Dict[str, Any] = None,
    user_confirmed: bool = False,
    preserved_state: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Run the Movi Transport Agent workflow.

    This is the main entry point for executing the agent.

    Args:
        user_input: User's text input
        session_id: Unique session identifier
        context: Current UI context (page, filters, etc.)
        multimodal_data: Optional multimodal inputs (images, audio, video)
        user_confirmed: Whether user has confirmed a high-risk action

    Returns:
        Final agent response with formatted message

    Example:
        >>> result = await run_movi_agent(
        ...     user_input="How many unassigned vehicles?",
        ...     session_id="session-123",
        ...     context={"page": "busDashboard"}
        ... )
        >>> print(result["response"])
        "There are 3 unassigned vehicles available."

    Example (with confirmation):
        >>> # First call - returns confirmation message
        >>> result1 = await run_movi_agent(
        ...     user_input="Remove vehicle from Bulk - 00:01",
        ...     session_id="session-456",
        ...     context={"page": "busDashboard"}
        ... )
        >>> print(result1["response_type"])
        "confirmation"
        >>>
        >>> # Second call - with user confirmation
        >>> result2 = await run_movi_agent(
        ...     user_input="Remove vehicle from Bulk - 00:01",
        ...     session_id="session-456",
        ...     context={"page": "busDashboard"},
        ...     user_confirmed=True
        ... )
        >>> print(result2["response_type"])
        "success"
    """
    # Create initial state
    from app.agent.state import create_initial_state

    initial_state = create_initial_state(
        user_input=user_input,
        session_id=session_id,
        context=context,
        multimodal_data=multimodal_data,  # ADD THIS!
    )

    # Add user confirmation if provided
    if user_confirmed:
        initial_state["user_confirmed"] = True
        
        # If preserved_state is provided (from confirmation flow), FULLY restore it
        # This makes the flow STATEFUL - we continue from where we left off
        if preserved_state:
            print(f"\n{'='*80}")
            print(f"🔄 CONFIRMATION FLOW - Restoring complete state from session")
            print(f"{'='*80}")
            
            # Completely replace initial_state with preserved_state
            # Keep only the new user_confirmed flag and session_id
            initial_state = dict(preserved_state)  # Copy all fields
            initial_state["user_confirmed"] = True
            initial_state["session_id"] = session_id
            initial_state["timestamp"] = datetime.utcnow().isoformat()
            
            # Clear requires_confirmation since user just confirmed
            initial_state["requires_confirmation"] = False
            
            print(f"✅ Restored complete state:")
            print(f"   - intent: {initial_state.get('intent')}")
            print(f"   - action_type: {initial_state.get('action_type')}")
            print(f"   - tool_name: {initial_state.get('tool_name')}")
            print(f"   - tool_params: {initial_state.get('tool_params')}")
            print(f"   - extracted_entities: {initial_state.get('extracted_entities')}")
            print(f"   - risk_level: {initial_state.get('risk_level')}")
            print(f"   - user_confirmed: True")
            print(f"{'='*80}\n")

    # Run the graph
    final_state = await movi_agent_graph.ainvoke(initial_state)

    # Extract response fields for API, but return COMPLETE state for session storage
    response = {
        "response": final_state.get("response", ""),
        "response_type": final_state.get("response_type", "info"),
        "session_id": session_id,
        "intent": final_state.get("intent"),
        "action_type": final_state.get("action_type"),
        "tool_name": final_state.get("tool_name"),
        "execution_success": final_state.get("execution_success"),
        "requires_confirmation": final_state.get("requires_confirmation", False),
        "confirmation_message": final_state.get("confirmation_message"),
        "error": final_state.get("error"),
        "tool_results": final_state.get("tool_results"),  # Include for metadata/UI actions
        
        # CRITICAL: Include ALL state fields for proper session persistence
        # These are needed to restore context during confirmation flow
        "tool_params": final_state.get("tool_params"),
        "extracted_entities": final_state.get("extracted_entities"),
        "consequences": final_state.get("consequences"),
        "risk_level": final_state.get("risk_level"),
        "processed_input": final_state.get("processed_input"),
        "input_modalities": final_state.get("input_modalities"),
        "user_confirmed": final_state.get("user_confirmed"),
        "action_plan": final_state.get("action_plan"),
    }

    return response


# Export main functions
__all__ = [
    "create_movi_agent_graph",
    "movi_agent_graph",
    "run_movi_agent",
]
