"""
Base utilities and helpers for tool functions.

All tool functions follow a consistent return format:
{
    "success": bool,
    "data": Any (if success),
    "message": str,
    "error": str (if not success)
}
"""
from typing import Dict, Any, Optional


def success_response(data: Any, message: str = "Operation successful") -> Dict[str, Any]:
    """
    Create a successful tool response.

    Args:
        data: The result data
        message: Success message

    Returns:
        Structured success response dictionary
    """
    return {
        "success": True,
        "data": data,
        "message": message
    }


def error_response(error: str, message: str = "Operation failed") -> Dict[str, Any]:
    """
    Create an error tool response.

    Args:
        error: Error description
        message: Error message

    Returns:
        Structured error response dictionary
    """
    return {
        "success": False,
        "error": error,
        "message": message
    }


def validate_required_params(params: Dict[str, Any], required: list[str]) -> Optional[str]:
    """
    Validate that all required parameters are present.

    Args:
        params: Parameter dictionary
        required: List of required parameter names

    Returns:
        Error message if validation fails, None if successful
    """
    missing = [key for key in required if key not in params or params[key] is None]
    if missing:
        return f"Missing required parameters: {', '.join(missing)}"
    return None
