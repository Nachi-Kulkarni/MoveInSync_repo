"""
Retry utility functions for tool execution with backoff logic.

Used by execute_action_node for handling transient failures.
"""

import asyncio
import time
import logging
from typing import Any, Callable, Optional, Dict, List
from functools import wraps

logger = logging.getLogger(__name__)


async def retry_with_backoff(
    func: Callable,
    *args,
    max_attempts: int = 2,
    base_delay: float = 1.0,
    max_delay: float = 5.0,
    backoff_factor: float = 2.0,
    retry_on: Optional[List[type]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute a function with retry logic and exponential backoff.

    Args:
        func: Async function to execute
        *args: Positional arguments for the function
        max_attempts: Maximum number of attempts (default: 2)
        base_delay: Initial delay between attempts in seconds (default: 1.0)
        max_delay: Maximum delay between attempts in seconds (default: 5.0)
        backoff_factor: Multiplier for exponential backoff (default: 2.0)
        retry_on: List of exception types to retry on (default: [Exception])
        **kwargs: Keyword arguments for the function

    Returns:
        Dictionary with:
        - success: Boolean indicating if execution succeeded
        - result: Function result if successful
        - error: Error message if failed
        - attempts: Number of attempts made
        - total_duration: Total time spent including delays

    Example:
        result = await retry_with_backoff(
            my_tool_function,
            param1="value",
            param2=123,
            max_attempts=3
        )
    """
    if retry_on is None:
        retry_on = [Exception]

    attempts = 0
    start_time = time.time()
    last_exception = None

    while attempts < max_attempts:
        attempts += 1

        try:
            logger.info(f"Executing {func.__name__} (attempt {attempts}/{max_attempts})")

            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Check if result indicates success (tools return {"success": bool, ...})
            if isinstance(result, dict) and result.get("success") is False:
                # Tool returned explicit failure
                tool_error = result.get("error", "Tool returned failure")
                logger.warning(f"Tool {func.__name__} returned failure on attempt {attempts}: {tool_error}")

                if attempts < max_attempts:
                    # Wait before retry
                    delay = min(base_delay * (backoff_factor ** (attempts - 1)), max_delay)
                    logger.info(f"Retrying {func.__name__} in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed
                    total_duration = time.time() - start_time
                    return {
                        "success": False,
                        "result": result,
                        "error": f"Tool failed after {attempts} attempts: {tool_error}",
                        "attempts": attempts,
                        "total_duration": total_duration
                    }
            else:
                # Success
                total_duration = time.time() - start_time
                logger.info(f"Tool {func.__name__} succeeded on attempt {attempts}")
                return {
                    "success": True,
                    "result": result,
                    "error": None,
                    "attempts": attempts,
                    "total_duration": total_duration
                }

        except Exception as e:
            last_exception = e

            # Check if this exception type should be retried
            should_retry = any(isinstance(e, exc_type) for exc_type in retry_on)

            if should_retry and attempts < max_attempts:
                logger.warning(f"Tool {func.__name__} raised {type(e).__name__} on attempt {attempts}: {e}")

                # Wait before retry
                delay = min(base_delay * (backoff_factor ** (attempts - 1)), max_delay)
                logger.info(f"Retrying {func.__name__} in {delay:.2f}s...")
                await asyncio.sleep(delay)
            else:
                # Exception shouldn't be retried or max attempts reached
                logger.error(f"Tool {func.__name__} failed with {type(e).__name__} on attempt {attempts}: {e}")
                total_duration = time.time() - start_time
                return {
                    "success": False,
                    "result": None,
                    "error": f"Tool raised {type(e).__name__} after {attempts} attempts: {str(e)}",
                    "attempts": attempts,
                    "total_duration": total_duration
                }

    # Should never reach here
    total_duration = time.time() - start_time
    return {
        "success": False,
        "result": None,
        "error": f"Unexpected error after {attempts} attempts",
        "attempts": attempts,
        "total_duration": total_duration
    }


def log_tool_execution(
    tool_name: str,
    tool_params: Dict[str, Any],
    execution_result: Dict[str, Any],
    duration: float
) -> None:
    """
    Log detailed information about tool execution.

    Args:
        tool_name: Name of the tool that was executed
        tool_params: Parameters passed to the tool
        execution_result: Result returned from retry_with_backoff
        duration: Total execution duration including retries
    """
    if execution_result["success"]:
        logger.info(
            f"Tool '{tool_name}' executed successfully in {duration:.2f}s "
            f"(attempt {execution_result['attempts']}/{execution_result.get('max_attempts', 'N/A')})"
        )
    else:
        logger.error(
            f"Tool '{tool_name}' failed after {duration:.2f}s "
            f"(attempt {execution_result['attempts']}/{execution_result.get('max_attempts', 'N/A')}): "
            f"{execution_result['error']}"
        )

    # Log parameter summary (exclude sensitive data like db sessions)
    safe_params = {k: v for k, v in tool_params.items() if k != 'db'}
    if safe_params:
        logger.debug(f"Tool '{tool_name}' parameters: {safe_params}")