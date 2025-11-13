"""
LangGraph Agent Core (TICKET #5)

This package contains the LangGraph agent implementation with 6 nodes:
- preprocess_input_node: Multimodal input processing
- classify_intent_node: Intent classification with Claude
- check_consequences_node: Tribal knowledge consequence checking
- request_confirmation_node: Generate confirmation message
- execute_action_node: Execute tools via TOOL_REGISTRY
- format_response_node: Format final response

Entry point: graph.py exports the compiled StateGraph
"""

from app.agent.state import AgentState
from app.agent.prompts import (
    PREPROCESSING_SYSTEM_PROMPT,
    CLASSIFICATION_SYSTEM_PROMPT,
    CONFIRMATION_SYSTEM_PROMPT,
    RESPONSE_FORMAT_SYSTEM_PROMPT,
)

__all__ = [
    "AgentState",
    "PREPROCESSING_SYSTEM_PROMPT",
    "CLASSIFICATION_SYSTEM_PROMPT",
    "CONFIRMATION_SYSTEM_PROMPT",
    "RESPONSE_FORMAT_SYSTEM_PROMPT",
]
