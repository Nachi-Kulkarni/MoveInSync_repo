"""
Pydantic schemas for tool request/response validation.

These schemas define the structure for tool calls made by the LangGraph agent
and the responses returned by tool functions.
"""
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Base Tool Response Schemas
# ============================================================================

class ToolResponse(BaseModel):
    """
    Standard response format for all tool functions.

    All tools return this consistent structure to make agent integration easier.
    """
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Human-readable message about the operation")
    data: Optional[Any] = Field(None, description="Result data (if success=True)")
    error: Optional[str] = Field(None, description="Error details (if success=False)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Found 3 unassigned vehicles",
                "data": {"count": 3, "vehicles": [...]},
                "error": None
            }
        }


# ============================================================================
# Read Tool Request Schemas
# ============================================================================

class GetUnassignedVehiclesRequest(BaseModel):
    """Request schema for get_unassigned_vehicles_count tool."""
    # No parameters needed - reads all unassigned vehicles
    pass


class GetTripStatusRequest(BaseModel):
    """Request schema for get_trip_status tool."""
    trip_id: int = Field(..., description="ID of the trip to query", gt=0)


class ListStopsForPathRequest(BaseModel):
    """Request schema for list_stops_for_path tool."""
    path_id: int = Field(..., description="ID of the path to query", gt=0)


class ListRoutesByPathRequest(BaseModel):
    """Request schema for list_routes_by_path tool."""
    path_id: int = Field(..., description="ID of the path to query", gt=0)


# ============================================================================
# Create Tool Request Schemas
# ============================================================================

class AssignVehicleToTripRequest(BaseModel):
    """Request schema for assign_vehicle_to_trip tool."""
    trip_id: int = Field(..., description="ID of the trip", gt=0)
    vehicle_id: int = Field(..., description="ID of the vehicle to assign", gt=0)
    driver_id: int = Field(..., description="ID of the driver to assign", gt=0)


class CreateStopRequest(BaseModel):
    """Request schema for create_stop tool."""
    name: str = Field(..., description="Name of the stop", min_length=1, max_length=200)
    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)


class CreatePathRequest(BaseModel):
    """Request schema for create_path tool."""
    path_name: str = Field(..., description="Name of the path", min_length=1, max_length=100)
    ordered_stop_ids: List[int] = Field(..., description="Ordered list of stop IDs", min_length=2)


class CreateRouteRequest(BaseModel):
    """Request schema for create_route tool."""
    path_id: int = Field(..., description="ID of the path to use", gt=0)
    shift_time: str = Field(..., description="Time in HH:MM format", pattern=r"^\d{2}:\d{2}$")
    direction: Literal["UP", "DOWN"] = Field(..., description="Route direction")


# ============================================================================
# Delete Tool Request Schemas
# ============================================================================

class RemoveVehicleFromTripRequest(BaseModel):
    """Request schema for remove_vehicle_from_trip tool."""
    trip_id: int = Field(..., description="ID of the trip", gt=0)


# ============================================================================
# Consequence Tool Request Schemas
# ============================================================================

class GetConsequencesRequest(BaseModel):
    """Request schema for get_consequences_for_action tool."""
    action_type: Literal["remove_vehicle", "assign_vehicle", "create_route", "delete_route"] = Field(
        ...,
        description="Type of action to check consequences for"
    )
    entity_id: int = Field(..., description="ID of the entity affected by the action", gt=0)


class ConsequenceResult(BaseModel):
    """Schema for consequence check results (returned in ToolResponse.data)."""
    risk_level: Literal["none", "low", "high"] = Field(..., description="Risk level of the action")
    action_type: str = Field(..., description="Type of action being evaluated")
    entity_id: int = Field(..., description="ID of the affected entity")
    consequences: List[str] = Field(..., description="List of consequence descriptions")
    explanation: str = Field(..., description="Detailed explanation of consequences")
    proceed_with_caution: bool = Field(..., description="Whether confirmation is required")
    affected_bookings: Optional[int] = Field(None, description="Number of bookings affected (if applicable)")


# ============================================================================
# Tool Metadata Schema (for LangGraph integration)
# ============================================================================

class ToolMetadata(BaseModel):
    """
    Metadata about a tool for agent integration.

    Used by the LangGraph agent to understand tool capabilities and parameters.
    """
    name: str = Field(..., description="Tool function name")
    description: str = Field(..., description="What the tool does")
    category: Literal["read", "create", "delete", "consequence"] = Field(
        ...,
        description="Tool category"
    )
    requires_consequence_check: bool = Field(
        False,
        description="Whether this tool requires consequence checking before execution"
    )
    risk_level: Literal["low", "medium", "high"] = Field(
        "low",
        description="Default risk level of using this tool"
    )
    parameters_schema: Dict[str, Any] = Field(
        ...,
        description="JSON schema of tool parameters"
    )


# ============================================================================
# Tool Registry Schema
# ============================================================================

TOOL_METADATA_REGISTRY: Dict[str, ToolMetadata] = {
    "get_unassigned_vehicles_count": ToolMetadata(
        name="get_unassigned_vehicles_count",
        description="Get count and list of vehicles not currently assigned to any trip",
        category="read",
        requires_consequence_check=False,
        risk_level="low",
        parameters_schema=GetUnassignedVehiclesRequest.model_json_schema()
    ),

    "get_trip_status": ToolMetadata(
        name="get_trip_status",
        description="Get detailed status of a specific trip including bookings and deployment info",
        category="read",
        requires_consequence_check=False,
        risk_level="low",
        parameters_schema=GetTripStatusRequest.model_json_schema()
    ),

    "list_stops_for_path": ToolMetadata(
        name="list_stops_for_path",
        description="List all stops in order for a specific path",
        category="read",
        requires_consequence_check=False,
        risk_level="low",
        parameters_schema=ListStopsForPathRequest.model_json_schema()
    ),

    "list_routes_by_path": ToolMetadata(
        name="list_routes_by_path",
        description="List all routes that use a specific path",
        category="read",
        requires_consequence_check=False,
        risk_level="low",
        parameters_schema=ListRoutesByPathRequest.model_json_schema()
    ),

    "assign_vehicle_to_trip": ToolMetadata(
        name="assign_vehicle_to_trip",
        description="Assign a vehicle and driver to a trip (create deployment)",
        category="create",
        requires_consequence_check=False,
        risk_level="low",
        parameters_schema=AssignVehicleToTripRequest.model_json_schema()
    ),

    "create_stop": ToolMetadata(
        name="create_stop",
        description="Create a new stop (geographic location)",
        category="create",
        requires_consequence_check=False,
        risk_level="low",
        parameters_schema=CreateStopRequest.model_json_schema()
    ),

    "create_path": ToolMetadata(
        name="create_path",
        description="Create a new path as an ordered sequence of stops",
        category="create",
        requires_consequence_check=False,
        risk_level="medium",
        parameters_schema=CreatePathRequest.model_json_schema()
    ),

    "create_route": ToolMetadata(
        name="create_route",
        description="Create a new route by assigning a time to a path",
        category="create",
        requires_consequence_check=False,
        risk_level="medium",
        parameters_schema=CreateRouteRequest.model_json_schema()
    ),

    "remove_vehicle_from_trip": ToolMetadata(
        name="remove_vehicle_from_trip",
        description="Remove vehicle and driver from a trip (requires consequence check if booked)",
        category="delete",
        requires_consequence_check=True,  # CRITICAL: Tribal Knowledge rule
        risk_level="high",
        parameters_schema=RemoveVehicleFromTripRequest.model_json_schema()
    ),

    "get_consequences_for_action": ToolMetadata(
        name="get_consequences_for_action",
        description="Check consequences of an action before executing (Tribal Knowledge)",
        category="consequence",
        requires_consequence_check=False,
        risk_level="low",
        parameters_schema=GetConsequencesRequest.model_json_schema()
    ),
}


# ============================================================================
# Validation Utilities
# ============================================================================

def validate_tool_request(tool_name: str, params: Dict[str, Any]) -> Optional[str]:
    """
    Validate tool request parameters against the schema.

    Args:
        tool_name: Name of the tool
        params: Parameters dictionary

    Returns:
        Error message if validation fails, None if successful
    """
    # Map tool names to request schemas
    schema_map = {
        "get_unassigned_vehicles_count": GetUnassignedVehiclesRequest,
        "get_trip_status": GetTripStatusRequest,
        "list_stops_for_path": ListStopsForPathRequest,
        "list_routes_by_path": ListRoutesByPathRequest,
        "assign_vehicle_to_trip": AssignVehicleToTripRequest,
        "create_stop": CreateStopRequest,
        "create_path": CreatePathRequest,
        "create_route": CreateRouteRequest,
        "remove_vehicle_from_trip": RemoveVehicleFromTripRequest,
        "get_consequences_for_action": GetConsequencesRequest,
    }

    schema_class = schema_map.get(tool_name)
    if not schema_class:
        return f"Unknown tool: {tool_name}"

    try:
        schema_class(**params)
        return None
    except Exception as e:
        return f"Validation error: {str(e)}"


# Export all schemas
__all__ = [
    # Base schemas
    "ToolResponse",

    # Read tool requests
    "GetUnassignedVehiclesRequest",
    "GetTripStatusRequest",
    "ListStopsForPathRequest",
    "ListRoutesByPathRequest",

    # Create tool requests
    "AssignVehicleToTripRequest",
    "CreateStopRequest",
    "CreatePathRequest",
    "CreateRouteRequest",

    # Delete tool requests
    "RemoveVehicleFromTripRequest",

    # Consequence tool requests
    "GetConsequencesRequest",
    "ConsequenceResult",

    # Metadata
    "ToolMetadata",
    "TOOL_METADATA_REGISTRY",

    # Utilities
    "validate_tool_request",
]
