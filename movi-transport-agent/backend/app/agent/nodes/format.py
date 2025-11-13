"""
Format Response Node (TICKET #5 - Phase 4f)

This node formats the final response for the user in natural language.

Responsibilities:
1. Take tool execution results or errors
2. Format them into user-friendly messages
3. Use Claude for natural language generation
4. Handle different response types (success, error, confirmation)
5. Return formatted response ready for UI display

Uses Claude Sonnet 4.5 via OpenRouter for natural language generation.
"""

import json
from typing import Dict, Any
from app.agent.state import AgentState
from app.agent.prompts import RESPONSE_FORMAT_SYSTEM_PROMPT
from app.utils.openrouter import OpenRouterClient
from app.core.config import settings


async def format_response_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 6: Format final response for user display.

    This node takes the results from tool execution (or errors from any node)
    and formats them into a natural, conversational response using Claude.

    Args:
        state: Current agent state with execution results

    Returns:
        State update with:
        - response: Formatted response text for user
        - response_type: Type of response (success, error, confirmation, info)
        - error: None if successful, error message if formatting failed

    Flow:
    1. Check if there's an error from previous nodes
    2. Check if waiting for user confirmation
    3. Check execution results
    4. Build context for Claude
    5. Generate natural language response
    6. Return formatted response

    Response Types:
    - "success": Tool executed successfully
    - "error": Error occurred in any node
    - "confirmation": Waiting for user confirmation
    - "info": Informational response (no tool execution)
    """
    try:
        # Check for errors from any previous node
        error = state.get("error")
        error_node = state.get("error_node")

        if error:
            # Format error response
            return await _format_error_response(state, error, error_node)

        # Check if waiting for confirmation
        requires_confirmation = state.get("requires_confirmation", False)
        user_confirmed = state.get("user_confirmed", False)

        if requires_confirmation and not user_confirmed:
            # Return confirmation message (already formatted by confirmation node)
            confirmation_message = state.get("confirmation_message", "")
            return {
                "response": confirmation_message,
                "response_type": "confirmation",
                "error": None,
            }

        # Check execution results
        execution_success = state.get("execution_success")
        tool_results = state.get("tool_results")
        tool_name = state.get("tool_name")
        user_input = state.get("user_input", "")

        if execution_success is False:
            # Tool execution failed
            execution_error = state.get("execution_error", "Unknown error")
            return await _format_error_response(
                state,
                execution_error,
                "execute_action_node"
            )

        # Tool executed successfully - format results
        if tool_results:
            return await _format_success_response(
                state,
                tool_results,
                tool_name,
                user_input
            )

        # No tool execution (info request or clarification)
        intent = state.get("intent", "")
        return await _format_info_response(state, intent, user_input)

    except Exception as e:
        # Fallback error handling
        return {
            "response": f"Sorry, I encountered an error while formatting the response: {str(e)}",
            "response_type": "error",
            "error": str(e),
        }


async def _format_success_response(
    state: AgentState,
    tool_results: Dict[str, Any],
    tool_name: str,
    user_input: str
) -> Dict[str, Any]:
    """
    Format successful tool execution into natural language.

    Uses Claude to generate a conversational response that:
    - Acknowledges the user's request
    - Presents the results clearly
    - Provides relevant details from tool output
    - Suggests next actions if appropriate
    """
    try:
        # Build context for Claude
        context = {
            "user_input": user_input,
            "tool_name": tool_name,
            "tool_results": tool_results,
            "intent": state.get("intent", ""),
            "action_type": state.get("action_type", ""),
        }

        user_message = f"""
User request: "{user_input}"

Tool executed: {tool_name}
Action type: {context['action_type']}

Tool results:
{json.dumps(tool_results, indent=2)}

Please generate a natural, conversational response that:
1. Confirms what was done
2. Presents key results clearly
3. Uses simple language (avoid technical jargon)
4. Keeps it concise (2-3 sentences)

Format numbers nicely (e.g., "3 vehicles" not "count: 3").
If there's a list, present top 2-3 items.
"""

        messages = [
            {"role": "system", "content": RESPONSE_FORMAT_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

        # Call Claude via OpenRouter
        client = OpenRouterClient()

        try:
            response = await client.chat_completion(
                model=settings.CLAUDE_MODEL,
                messages=messages,
                temperature=0.7,  # More creative for natural responses
                max_tokens=300,
            )
        except Exception as e:
            # Fallback: Generate simple response without Claude
            return _generate_fallback_success_response(tool_results, tool_name)

        await client.close()

        # Extract formatted response
        formatted_response = response["choices"][0]["message"]["content"]

        # Clean up response (remove any markdown)
        if "```" in formatted_response:
            parts = formatted_response.split("```")
            formatted_response = parts[0].strip()
            if not formatted_response and len(parts) > 2:
                formatted_response = parts[-1].strip()

        # Validate response
        if not formatted_response or len(formatted_response) < 10:
            return _generate_fallback_success_response(tool_results, tool_name)

        return {
            "response": formatted_response,
            "response_type": "success",
            "error": None,
            "tool_results": tool_results,  # Pass through for API metadata
        }

    except Exception as e:
        # Fallback to simple response
        return _generate_fallback_success_response(tool_results, tool_name)


async def _format_error_response(
    state: AgentState,
    error: str,
    error_node: str
) -> Dict[str, Any]:
    """
    Format error into user-friendly message.

    Translates technical errors into simple explanations.
    """
    user_input = state.get("user_input", "your request")

    # Common error patterns and user-friendly messages
    error_lower = error.lower()

    if "confirmation" in error_lower:
        message = "This action requires your confirmation before I can proceed. Please confirm or cancel."
    elif "not found" in error_lower:
        message = f"I couldn't find what you're looking for. Please check the details and try again."
    elif "parameter" in error_lower or "missing" in error_lower:
        message = f"I need more information to complete this request. Could you provide more details?"
    elif "database" in error_lower:
        message = "I'm having trouble accessing the data right now. Please try again in a moment."
    elif "authentication" in error_lower or "api" in error_lower:
        message = "I'm having trouble connecting to the service. Please try again."
    else:
        # Generic error message
        message = f"I encountered an issue: {error}"

    return {
        "response": message,
        "response_type": "error",
        "error": error,
    }


async def _format_info_response(
    state: AgentState,
    intent: str,
    user_input: str
) -> Dict[str, Any]:
    """
    Format informational response (no tool execution).

    Used for clarifications, help messages, or when no action is needed.
    """
    message = f"I understand you want to: {intent}. How can I help you with this?"

    return {
        "response": message,
        "response_type": "info",
        "error": None,
    }


def _generate_fallback_success_response(
    tool_results: Dict[str, Any],
    tool_name: str
) -> Dict[str, Any]:
    """
    Generate simple success response without Claude.

    Used when Claude API fails or is unavailable.
    """
    # Extract key information from tool results
    success = tool_results.get("success", False)
    message = tool_results.get("message", "")
    data = tool_results.get("data", {})

    if not success:
        response = f"Action completed but with warnings: {message}"
    elif message:
        response = message
    elif data:
        # Format data simply
        if isinstance(data, dict):
            if "count" in data:
                response = f"Found {data['count']} items."
            elif "id" in data or "stop_id" in data or "path_id" in data:
                id_value = data.get("id") or data.get("stop_id") or data.get("path_id")
                response = f"Successfully created with ID: {id_value}"
            else:
                response = f"Action completed successfully."
        else:
            response = "Action completed successfully."
    else:
        response = "Action completed successfully."

    return {
        "response": response,
        "response_type": "success",
        "error": None,
        "tool_results": tool_results,  # Pass through for API metadata
    }
