"""
Execute Action Node (TICKET #5 - Phase 4e)

This node executes the selected tool from the TOOL_REGISTRY.

Responsibilities:
1. Verify user confirmation (if required)
2. Look up tool function in TOOL_REGISTRY
3. Execute tool with provided parameters (with retry logic)
4. Handle success/error responses
5. Return execution results
6. Log detailed execution information (input/output/duration)

All tools are async functions that require a database session.
"""

import time
import logging
from typing import Dict, Any
from app.agent.state import AgentState
from app.tools import TOOL_REGISTRY
from app.api.deps import get_db
from app.utils.retry import retry_with_backoff, log_tool_execution
from app.utils.logger import get_logger

# Configure logger for this node
logger = get_logger(__name__)


async def execute_action_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 5: Execute the selected tool action.

    This node executes the tool function identified by the classify node.
    It handles database session management, retry logic, and detailed logging.

    Args:
        state: Current agent state with tool_name and tool_params

    Returns:
        State update with:
        - tool_results: Results from tool execution
        - execution_success: Boolean indicating success
        - execution_error: Error message if failed
        - execution_attempts: Number of execution attempts made
        - execution_duration: Total execution time including retries

    Flow:
    1. Check if confirmation was required and obtained
    2. Get tool_name and tool_params from state
    3. Look up tool function in TOOL_REGISTRY
    4. Get database session
    5. Execute tool with retry logic and detailed logging
    6. Return results
    """
    start_time = time.time()
    logger.info("Execute action node started")

    try:
        # Check if confirmation was required
        requires_confirmation = state.get("requires_confirmation", False)
        user_confirmed = state.get("user_confirmed", False)

        if requires_confirmation and not user_confirmed:
            # Cannot execute without user confirmation
            duration = time.time() - start_time
            logger.warning(f"Execution blocked: confirmation required after {duration:.2f}s")
            return {
                "tool_results": None,
                "execution_success": False,
                "execution_error": "Action requires user confirmation but confirmation not received",
                "error": "Confirmation required",
                "error_node": "execute_action_node",
                "execution_attempts": 1,
                "execution_duration": duration
            }

        # Get tool details from state
        tool_name = state.get("tool_name")
        tool_params = state.get("tool_params", {})

        logger.info(f"Preparing to execute tool: {tool_name}")

        if not tool_name:
            duration = time.time() - start_time
            logger.error(f"No tool specified in state after {duration:.2f}s")
            return {
                "tool_results": None,
                "execution_success": False,
                "execution_error": "No tool specified for execution",
                "error": "Missing tool_name",
                "error_node": "execute_action_node",
                "execution_attempts": 1,
                "execution_duration": duration
            }

        # Look up tool function in registry
        tool_function = TOOL_REGISTRY.get(tool_name)

        if not tool_function:
            duration = time.time() - start_time
            logger.error(f"Tool '{tool_name}' not found in TOOL_REGISTRY after {duration:.2f}s")
            return {
                "tool_results": None,
                "execution_success": False,
                "execution_error": f"Tool '{tool_name}' not found in TOOL_REGISTRY",
                "error": f"Unknown tool: {tool_name}",
                "error_node": "execute_action_node",
                "execution_attempts": 1,
                "execution_duration": duration
            }

        # Get database session and execute tool with retry
        async for db in get_db():
            # Add db to params (excluding from logs for security)
            execution_params = {**tool_params, "db": db}

            logger.info(f"Executing tool '{tool_name}' with retry logic (max 2 attempts)")

            try:
                # Execute tool with retry logic
                retry_result = await retry_with_backoff(
                    tool_function,
                    max_attempts=2,
                    base_delay=1.0,
                    max_delay=3.0,
                    retry_on=[Exception],  # Retry on all exceptions
                    **execution_params
                )

                # Log detailed execution information
                total_duration = time.time() - start_time
                log_tool_execution(tool_name, tool_params, retry_result, total_duration)

                # Handle execution result
                if retry_result["success"]:
                    logger.info(f"Tool '{tool_name}' execution completed successfully")
                    return {
                        "tool_results": retry_result["result"],
                        "execution_success": True,
                        "execution_error": None,
                        "error": None,
                        "execution_attempts": retry_result["attempts"],
                        "execution_duration": total_duration
                    }
                else:
                    # Tool execution failed after retries
                    logger.error(f"Tool '{tool_name}' failed after {retry_result['attempts']} attempts: {retry_result['error']}")
                    return {
                        "tool_results": retry_result["result"],
                        "execution_success": False,
                        "execution_error": retry_result["error"],
                        "error": retry_result["error"],
                        "error_node": "execute_action_node",
                        "execution_attempts": retry_result["attempts"],
                        "execution_duration": total_duration
                    }

            except TypeError as e:
                # Parameter mismatch (shouldn't happen with retry logic, but handle anyway)
                duration = time.time() - start_time
                logger.error(f"Parameter type error for tool '{tool_name}': {e}")
                return {
                    "tool_results": None,
                    "execution_success": False,
                    "execution_error": f"Parameter error when calling {tool_name}: {str(e)}",
                    "error": f"Parameter mismatch: {str(e)}",
                    "error_node": "execute_action_node",
                    "execution_attempts": 1,
                    "execution_duration": duration
                }

        # If we get here, database session failed
        duration = time.time() - start_time
        logger.error(f"Failed to get database session after {duration:.2f}s")
        return {
            "tool_results": None,
            "execution_success": False,
            "execution_error": "Failed to get database session",
            "error": "Database session failed",
            "error_node": "execute_action_node",
            "execution_attempts": 1,
            "execution_duration": duration
        }

    except Exception as e:
        # Node-level exception
        duration = time.time() - start_time
        logger.error(f"Execute action node failed with {type(e).__name__}: {e}")
        return {
            "tool_results": None,
            "execution_success": False,
            "execution_error": f"Execute action node failed: {str(e)}",
            "error": str(e),
            "error_node": "execute_action_node",
            "execution_attempts": 1,
            "execution_duration": duration
        }
