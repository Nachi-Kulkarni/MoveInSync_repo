from app.schemas.trip import TripResponse, TripConsequence
from app.schemas.route import RouteResponse, StopResponse
from app.schemas.tool import (
    ToolResponse,
    ToolMetadata,
    TOOL_METADATA_REGISTRY,
    validate_tool_request,
    # Request schemas
    GetUnassignedVehiclesRequest,
    GetTripStatusRequest,
    ListStopsForPathRequest,
    ListRoutesByPathRequest,
    AssignVehicleToTripRequest,
    CreateStopRequest,
    CreatePathRequest,
    CreateRouteRequest,
    RemoveVehicleFromTripRequest,
    GetConsequencesRequest,
    ConsequenceResult,
)

__all__ = [
    # Trip schemas
    "TripResponse",
    "TripConsequence",
    # Route schemas
    "RouteResponse",
    "StopResponse",
    # Tool schemas
    "ToolResponse",
    "ToolMetadata",
    "TOOL_METADATA_REGISTRY",
    "validate_tool_request",
    # Tool request schemas
    "GetUnassignedVehiclesRequest",
    "GetTripStatusRequest",
    "ListStopsForPathRequest",
    "ListRoutesByPathRequest",
    "AssignVehicleToTripRequest",
    "CreateStopRequest",
    "CreatePathRequest",
    "CreateRouteRequest",
    "RemoveVehicleFromTripRequest",
    "GetConsequencesRequest",
    "ConsequenceResult",
]
