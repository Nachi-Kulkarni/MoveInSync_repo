"""
Request Confirmation Node (TICKET #5 - Phase 4d)

This node generates human-readable confirmation messages for high-risk actions.

Responsibilities:
1. Check if action requires user confirmation
2. Generate clear, understandable confirmation message
3. Explain consequences in user-friendly language
4. Provide options (confirm/cancel)

Uses Claude Sonnet 4.5 via OpenRouter for natural language generation.
"""

import json
from typing import Dict, Any
from app.agent.state import AgentState
from app.agent.prompts import CONFIRMATION_SYSTEM_PROMPT
from app.utils.openrouter import OpenRouterClient
from app.core.config import settings


async def request_confirmation_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 4: Generate confirmation message for high-risk actions.

    This node is conditionally executed when requires_confirmation is True.
    It uses Claude to generate a clear, user-friendly confirmation message
    that explains the consequences and asks for user approval.

    Args:
        state: Current agent state with consequences

    Returns:
        State update with:
        - confirmation_message: Human-readable message for user
        - requires_confirmation: True (maintained)
        - user_confirmed: False (waiting for user response)

    Flow:
    1. Check if confirmation is needed
    2. Extract consequence details from state
    3. Build prompt for Claude with consequences
    4. Call Claude to generate confirmation message
    5. Return confirmation message for user
    """
    try:
        # Check if confirmation is required
        requires_confirmation = state.get("requires_confirmation", False)

        if not requires_confirmation:
            # No confirmation needed, skip this node
            return {
                "confirmation_message": None,
                "requires_confirmation": False,
                "user_confirmed": False,  # No confirmation needed
                "error": None,
            }

        # Get consequence details
        consequences = state.get("consequences", {})
        intent = state.get("intent", "")
        action_type = state.get("action_type", "")
        risk_level = state.get("risk_level", "low")
        user_input = state.get("user_input", "")

        # Build context for Claude
        user_message = f"""
User requested: "{user_input}"

Intent: {intent}
Action type: {action_type}
Risk level: {risk_level.upper()}

Consequences detected:
{json.dumps(consequences, indent=2)}

Please generate a clear, concise confirmation message that:
1. Explains what will happen
2. Highlights the key consequences
3. Asks the user to confirm or cancel

Keep it under 150 words and use simple, direct language.
"""

        messages = [
            {"role": "system", "content": CONFIRMATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

        # Call Claude via OpenRouter
        client = OpenRouterClient()

        try:
            response = await client.chat_completion(
                model=settings.CLAUDE_MODEL,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent messages
                max_tokens=500,
            )
        except Exception as e:
            # Fallback: Generate simple confirmation message without Claude
            return _generate_fallback_confirmation(state)

        await client.close()

        # Extract confirmation message
        confirmation_message = response["choices"][0]["message"]["content"]

        # Clean up message (remove markdown code blocks if present)
        if "```" in confirmation_message:
            # If there are code blocks, take content before first code block
            parts = confirmation_message.split("```")
            confirmation_message = parts[0].strip()
            # If that's empty, take content after code blocks
            if not confirmation_message and len(parts) > 2:
                confirmation_message = parts[-1].strip()

        # If message is too short or empty, use fallback
        if not confirmation_message or len(confirmation_message) < 20:
            return _generate_fallback_confirmation(state)

        return {
            "confirmation_message": confirmation_message,
            "requires_confirmation": True,
            "user_confirmed": False,  # Waiting for user response
            "error": None,
        }

    except Exception as e:
        # Fallback to simple message
        return _generate_fallback_confirmation(state)


def _generate_fallback_confirmation(state: AgentState) -> Dict[str, Any]:
    """
    Generate a simple fallback confirmation message without Claude.

    Used when Claude API fails or is unavailable.

    Args:
        state: Current agent state

    Returns:
        State update with basic confirmation message
    """
    consequences = state.get("consequences", {})
    intent = state.get("intent", "this action")
    risk_level = state.get("risk_level", "unknown")

    # Build basic confirmation message
    message_parts = [
        f"WARNING: Confirmation Required - {risk_level.upper()} RISK",
        "",
        f"You are about to perform: {intent}",
        ""
    ]

    # Add consequence details if available
    if consequences:
        explanation = consequences.get("explanation", "")
        if explanation:
            message_parts.append("Consequences:")
            # Take first 200 characters of explanation
            message_parts.append(explanation[:200] + "..." if len(explanation) > 200 else explanation)
            message_parts.append("")

        # Add affected bookings info
        affected_bookings = consequences.get("affected_bookings", 0)
        if affected_bookings > 0:
            message_parts.append(f"WARNING: This will affect {affected_bookings} employee bookings")
            message_parts.append("")

    message_parts.append("Do you want to proceed? (yes/no)")

    confirmation_message = "\n".join(message_parts)

    return {
        "confirmation_message": confirmation_message,
        "requires_confirmation": True,
        "user_confirmed": False,
        "error": None,
    }
