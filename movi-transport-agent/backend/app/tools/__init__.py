"""
Tool functions for Movi Transport Agent.

This module exports all 10 required tool functions that the LangGraph agent can call.

Tool Categories:
1. Read Tools (4): Query database for information
2. Create Tools (4): Create new records
3. Delete Tools (1): Remove/unassign records
4. Consequence Tools (1): Check action consequences (Tribal Knowledge)

Usage in LangGraph:
    from app.tools import (
        get_unassigned_vehicles_count,
        get_trip_status,
        # ... other tools
    )

    # In execute_action_node:
    result = await get_trip_status(trip_id=1, db=session)
"""

# Read Tools (4)
from .read_tools import (
    get_unassigned_vehicles_count,
    get_trip_status,
    list_stops_for_path,
    list_routes_by_path
)

# Create Tools (4)
from .create_tools import (
    assign_vehicle_to_trip,
    create_stop,
    create_path,
    create_route
)

# Delete Tools (1)
from .delete_tools import (
    remove_vehicle_from_trip
)

# Consequence Tools (1)
from .consequence_tools import (
    get_consequences_for_action
)

# Base utilities
from .base import (
    success_response,
    error_response,
    validate_required_params
)


# Tool Registry: Maps action names to tool functions
# This will be used by the LangGraph execute_action_node
TOOL_REGISTRY = {
    # Read operations
    "get_unassigned_vehicles": get_unassigned_vehicles_count,
    "get_unassigned_vehicles_count": get_unassigned_vehicles_count,
    "get_trip_status": get_trip_status,
    "list_stops_for_path": list_stops_for_path,
    "list_routes_by_path": list_routes_by_path,

    # Create operations
    "assign_vehicle": assign_vehicle_to_trip,
    "assign_vehicle_to_trip": assign_vehicle_to_trip,
    "create_stop": create_stop,
    "create_path": create_path,
    "create_route": create_route,

    # Delete operations
    "remove_vehicle": remove_vehicle_from_trip,
    "remove_vehicle_from_trip": remove_vehicle_from_trip,

    # Consequence checking
    "check_consequences": get_consequences_for_action,
    "get_consequences": get_consequences_for_action,
}


# Export all tools
__all__ = [
    # Read tools
    "get_unassigned_vehicles_count",
    "get_trip_status",
    "list_stops_for_path",
    "list_routes_by_path",

    # Create tools
    "assign_vehicle_to_trip",
    "create_stop",
    "create_path",
    "create_route",

    # Delete tools
    "remove_vehicle_from_trip",

    # Consequence tools
    "get_consequences_for_action",

    # Base utilities
    "success_response",
    "error_response",
    "validate_required_params",

    # Tool registry
    "TOOL_REGISTRY",
]


# Tool metadata for LangGraph agent
TOOL_DESCRIPTIONS = {
    "get_unassigned_vehicles_count": "Get count and list of vehicles not currently assigned to any trip",
    "get_trip_status": "Get detailed status of a specific trip including bookings and deployment info",
    "list_stops_for_path": "List all stops in order for a specific path",
    "list_routes_by_path": "List all routes that use a specific path",
    "assign_vehicle_to_trip": "Assign a vehicle and driver to a trip (create deployment)",
    "create_stop": "Create a new stop (geographic location)",
    "create_path": "Create a new path as an ordered sequence of stops",
    "create_route": "Create a new route by assigning a time to a path",
    "remove_vehicle_from_trip": "Remove vehicle and driver from a trip (requires consequence check if booked)",
    "get_consequences_for_action": "Check consequences of an action before executing (Tribal Knowledge)",
}


# Tool parameter schemas - EXACT parameters each tool accepts
# This prevents Claude from hallucinating parameters like 'location_filter'
TOOL_SCHEMAS = {
    "get_unassigned_vehicles_count": {
        "parameters": {},  # No parameters - returns ALL unassigned vehicles
        "description": "Get count and list of vehicles not currently assigned to any trip. NO FILTERS SUPPORTED - returns all unassigned vehicles."
    },
    "get_trip_status": {
        "parameters": {
            "trip_id": {"type": "int", "required": True, "description": "ID of the trip to check"}
        },
        "description": "Get detailed status including bookings, deployment, route info"
    },
    "list_stops_for_path": {
        "parameters": {
            "path_name": {"type": "str", "required": True, "description": "Name of the path (e.g., 'Path-1')"}
        },
        "description": "List all stops in order for a specific path"
    },
    "list_routes_by_path": {
        "parameters": {
            "path_name": {"type": "str", "required": True, "description": "Name of the path (e.g., 'Path-1')"}
        },
        "description": "List all routes that use a specific path"
    },
    "assign_vehicle_to_trip": {
        "parameters": {
            "trip_id": {"type": "int", "required": True, "description": "ID of the trip"},
            "vehicle_id": {"type": "str", "required": True, "description": "License plate of vehicle (e.g., 'MH-12-3456')"},
            "driver_id": {"type": "int", "required": False, "description": "ID of driver (optional)"}
        },
        "description": "Assign a vehicle and optionally a driver to a trip"
    },
    "create_stop": {
        "parameters": {
            "name": {"type": "str", "required": True, "description": "Name of the stop (e.g., 'Gavipuram')"},
            "latitude": {"type": "float", "required": True, "description": "Latitude coordinate"},
            "longitude": {"type": "float", "required": True, "description": "Longitude coordinate"}
        },
        "description": "Create a new stop at geographic location"
    },
    "create_path": {
        "parameters": {
            "path_name": {"type": "str", "required": True, "description": "Name for the new path"},
            "ordered_stop_ids": {"type": "list[int]", "required": True, "description": "Ordered list of stop IDs"}
        },
        "description": "Create a new path with ordered stops"
    },
    "create_route": {
        "parameters": {
            "path_name": {"type": "str", "required": True, "description": "Name of existing path"},
            "shift_time": {"type": "str", "required": True, "description": "Time in HH:MM format (e.g., '19:45')"},
            "direction": {"type": "str", "required": True, "description": "'LOGIN' or 'LOGOUT'"}
        },
        "description": "Create a new route by assigning time to a path"
    },
    "remove_vehicle_from_trip": {
        "parameters": {
            "trip_id": {"type": "int", "required": True, "description": "ID of the trip to remove vehicle from"}
        },
        "description": "Remove vehicle/driver assignment from trip (HIGH RISK if booked)"
    },
    "get_consequences_for_action": {
        "parameters": {
            "action": {"type": "str", "required": True, "description": "Action name (e.g., 'remove_vehicle_from_trip')"},
            "entity_id": {"type": "int", "required": True, "description": "ID of entity being acted upon (e.g., trip_id)"}
        },
        "description": "Check consequences before executing action (Tribal Knowledge)"
    }
}
