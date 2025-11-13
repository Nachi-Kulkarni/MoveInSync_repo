"""
Classify Intent Node (TICKET #5 - Phase 4b)

This node uses Claude Sonnet 4.5 to classify user intent and extract entities.

Responsibilities:
1. Analyze preprocessed input from Gemini
2. Classify intent (list_trips, remove_vehicle, create_stop, etc.)
3. Extract structured entities for tool execution
4. Determine action type (read/write/delete) for routing
5. Check if consequence analysis is needed
"""

import json
from typing import Dict, Any
from app.agent.state import AgentState
from app.agent.prompts import CLASSIFICATION_SYSTEM_PROMPT
from app.utils.openrouter import OpenRouterClient
from app.core.config import settings
from app.schemas.tool import TOOL_METADATA_REGISTRY


async def classify_intent_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 2: Classify user intent using Claude.
    
    Uses Claude Sonnet 4.5 via OpenRouter to:
    - Classify intent from preprocessed input
    - Extract entities (trip_ids, vehicle_ids, etc.)
    - Determine action type (read/write/delete)
    - Flag if consequence check is needed
    
    Args:
        state: Current agent state with processed_input
        
    Returns:
        State update with:
        - intent: Classified intent (e.g., "remove_vehicle")
        - action_type: "read", "write", or "delete"
        - extracted_entities: Structured entities
        - action_plan: Natural language explanation
        - requires_consequence_check: Boolean flag
        - tool_name: Tool to execute
        - tool_params: Parameters for tool
    """
    try:
        # Get processed input
        processed_input = state.get("processed_input", {})
        user_input = state.get("user_input", "")
        
        # Build prompt for Claude
        user_message = f"""
Preprocessed Input (from Gemini):
{json.dumps(processed_input, indent=2)}

Original User Input: "{user_input}"

Please classify the intent and extract entities for tool execution.
"""
        
        messages = [
            {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        # Call Claude via OpenRouter
        client = OpenRouterClient()
        
        try:
            response = await client.chat_completion(
                model=settings.CLAUDE_MODEL,
                messages=messages,
                temperature=settings.CLAUDE_TEMPERATURE,
                max_tokens=settings.CLAUDE_MAX_TOKENS,
            )
        except Exception as e:
            # Fallback to simpler model name
            response = await client.chat_completion(
                model="anthropic/claude-sonnet-4",
                messages=messages,
                temperature=settings.CLAUDE_TEMPERATURE,
                max_tokens=settings.CLAUDE_MAX_TOKENS,
            )
        
        await client.close()
        
        # Parse Claude's response
        content = response["choices"][0]["message"]["content"]
        
        # Clean markdown if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        classification = json.loads(content)
        
        # Validate and extract fields
        intent = classification.get("intent")
        action_type = classification.get("action_type")
        tool_name = classification.get("tool_name")
        
        # Get requires_consequence_check from tool metadata or Claude
        requires_check = classification.get("requires_consequence_check", False)
        if tool_name and tool_name in TOOL_METADATA_REGISTRY:
            tool_metadata = TOOL_METADATA_REGISTRY[tool_name]
            requires_check = tool_metadata.requires_consequence_check
        
        return {
            "intent": intent,
            "action_type": action_type,
            "extracted_entities": classification.get("extracted_entities", {}),
            "action_plan": classification.get("action_plan", ""),
            "requires_consequence_check": requires_check,
            "tool_name": tool_name,
            "tool_params": classification.get("tool_params", {}),
            "error": None,
        }
        
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse Claude response as JSON: {str(e)}",
            "error_node": "classify_intent_node"
        }
    except Exception as e:
        return {
            "error": f"Classification failed: {str(e)}",
            "error_node": "classify_intent_node"
        }
