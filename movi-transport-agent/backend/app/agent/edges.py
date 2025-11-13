"""
Edge Routing Functions (TICKET #5 - Phase 5)

These functions implement conditional routing logic in the LangGraph.
They determine which node to execute next based on the current state.

Edge Functions:
1. route_after_classify - Route after intent classification
2. route_after_consequences - Route after consequence checking
3. route_after_confirmation - Route after confirmation request
4. route_after_execute - Route after tool execution

Each function returns the name of the next node to execute.
"""

from typing import Literal
from app.agent.state import AgentState


def route_after_classify(
    state: AgentState
) -> Literal["check_consequences", "execute_action", "format_response"]:
    """
    Route after classify_intent_node.

    Decision logic:
    1. If error occurred ' format_response (to show error)
    2. If requires_consequence_check=True ' check_consequences
    3. Otherwise ' execute_action (safe to execute directly)

    Args:
        state: Current agent state

    Returns:
        Next node name: "check_consequences", "execute_action", or "format_response"
    """
    # Check for errors
    error = state.get("error")
    if error:
        return "format_response"

    # Check if consequences need to be checked
    requires_consequence_check = state.get("requires_consequence_check", False)

    if requires_consequence_check:
        # High-risk action - check consequences first
        return "check_consequences"
    else:
        # Low-risk action - safe to execute directly
        return "execute_action"


def route_after_consequences(
    state: AgentState
) -> Literal["request_confirmation", "execute_action", "format_response"]:
    """
    Route after check_consequences_node.

    Decision logic:
    1. If error occurred → format_response
    2. If user_confirmed=True → execute_action (skip confirmation, already confirmed)
    3. If requires_confirmation=True → request_confirmation
    4. Otherwise → execute_action (low risk, no confirmation needed)

    Args:
        state: Current agent state

    Returns:
        Next node name: "request_confirmation", "execute_action", or "format_response"
    """
    # Check for errors
    error = state.get("error")
    if error:
        return "format_response"

    # Check if user has already confirmed (confirmation retry flow)
    user_confirmed = state.get("user_confirmed", False)
    if user_confirmed:
        # User already confirmed - skip confirmation and execute directly
        return "execute_action"

    # Check if user confirmation is required
    requires_confirmation = state.get("requires_confirmation", False)

    if requires_confirmation:
        # High-risk action - get user confirmation
        return "request_confirmation"
    else:
        # Low risk or no consequences - safe to execute
        return "execute_action"


def route_after_confirmation(
    state: AgentState
) -> Literal["execute_action", "format_response"]:
    """
    Route after request_confirmation_node.

    Decision logic:
    1. If error occurred ' format_response
    2. If user_confirmed=True ' execute_action
    3. Otherwise ' format_response (wait for user confirmation)

    Note: In a real application, this would return to a "wait for user input" node.
    For now, we return format_response which will display the confirmation message.

    Args:
        state: Current agent state

    Returns:
        Next node name: "execute_action" or "format_response"
    """
    # Check for errors
    error = state.get("error")
    if error:
        return "format_response"

    # Check if user has confirmed
    user_confirmed = state.get("user_confirmed", False)

    if user_confirmed:
        # User confirmed - proceed with execution
        return "execute_action"
    else:
        # Waiting for user confirmation - show confirmation message
        return "format_response"


def route_after_execute(
    state: AgentState
) -> Literal["format_response"]:
    """
    Route after execute_action_node.

    Decision logic:
    Always ' format_response (to format execution results or errors)

    This is a terminal routing function - execution always goes to format_response
    after tool execution, whether successful or failed.

    Args:
        state: Current agent state

    Returns:
        Next node name: "format_response"
    """
    # Always go to format_response to display results
    return "format_response"


# Helper function for debugging routing decisions
def get_routing_explanation(state: AgentState) -> str:
    """
    Get human-readable explanation of routing decisions.

    Useful for debugging and logging.

    Args:
        state: Current agent state

    Returns:
        String explaining the routing path
    """
    path = []

    # Start with classification
    path.append("START ' preprocess ' classify")

    # After classify
    if state.get("error"):
        path.append(" ' format_response (error in classify)")
        return " ".join(path)

    requires_check = state.get("requires_consequence_check", False)
    if requires_check:
        path.append(" ' check_consequences")

        # After consequences
        if state.get("error"):
            path.append(" ' format_response (error in consequences)")
            return " ".join(path)

        requires_conf = state.get("requires_confirmation", False)
        if requires_conf:
            path.append(" ' request_confirmation")

            # After confirmation
            if state.get("error"):
                path.append(" ' format_response (error in confirmation)")
                return " ".join(path)

            user_conf = state.get("user_confirmed", False)
            if user_conf:
                path.append(" ' execute_action")
            else:
                path.append(" ' format_response (waiting for confirmation)")
                return " ".join(path)
        else:
            path.append(" ' execute_action (low risk)")
    else:
        path.append(" ' execute_action (no check needed)")

    # After execute
    path.append(" ' format_response")
    path.append(" ' END")

    return " ".join(path)


# Export all routing functions
__all__ = [
    "route_after_classify",
    "route_after_consequences",
    "route_after_confirmation",
    "route_after_execute",
    "get_routing_explanation",
]
