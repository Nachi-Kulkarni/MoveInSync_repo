"""
Check Consequences Node (TICKET #5 - Phase 4c)

This node implements the "Tribal Knowledge" flow by checking consequences
of actions before they are executed.

Responsibilities:
1. Check if action requires consequence analysis
2. Call consequence checking tools for risky actions
3. Determine risk level (none/low/high)
4. Populate state with consequence details for confirmation

Tribal Knowledge Rules:
- DELETE operations (especially remove_vehicle) require consequence checks
- Trips with bookings > 0% are HIGH RISK
- Removing vehicles from booked trips cancels bookings
- Confirmation required for HIGH RISK actions
"""

from typing import Dict, Any, Optional
from sqlalchemy import select
from app.agent.state import AgentState
from app.tools.consequence_tools import get_consequences_for_action
from app.api.deps import get_db
from app.models.daily_trip import DailyTrip
from app.models.route import Route
from sqlalchemy.ext.asyncio import AsyncSession


async def _resolve_trip_id(trip_identifier: Any, db: AsyncSession) -> Optional[int]:
    """
    Resolve trip identifier to trip_id.

    Args:
        trip_identifier: Can be trip_id (int) or trip name (str)
        db: Database session

    Returns:
        trip_id as integer, or None if not found
    """
    # If already an integer, return it
    if isinstance(trip_identifier, int):
        return trip_identifier

    # If string, try to convert to int first
    if isinstance(trip_identifier, str):
        # Try direct integer conversion
        try:
            return int(trip_identifier)
        except ValueError:
            pass

        # Look up by display_name
        result = await db.execute(
            select(DailyTrip.trip_id).where(DailyTrip.display_name == trip_identifier)
        )
        trip_id = result.scalar_one_or_none()
        return trip_id

    return None


async def _resolve_route_id(route_identifier: Any, db: AsyncSession) -> Optional[int]:
    """
    Resolve route identifier to route_id.

    Args:
        route_identifier: Can be route_id (int) or route name (str)
        db: Database session

    Returns:
        route_id as integer, or None if not found
    """
    # If already an integer, return it
    if isinstance(route_identifier, int):
        return route_identifier

    # If string, try to convert to int first
    if isinstance(route_identifier, str):
        # Try direct integer conversion
        try:
            return int(route_identifier)
        except ValueError:
            pass

        # Look up by name
        result = await db.execute(
            select(Route.route_id).where(Route.route_name == route_identifier)
        )
        route_id = result.scalar_one_or_none()
        return route_id

    return None


async def check_consequences_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 3: Check consequences of actions requiring tribal knowledge.

    This node is conditionally executed based on requires_consequence_check flag.
    It analyzes the impact of risky actions (like removing vehicles from trips)
    and provides detailed consequence information for user confirmation.

    Args:
        state: Current agent state with classified intent

    Returns:
        State update with:
        - consequences: Dict with risk analysis
        - risk_level: "none", "low", or "high"
        - requires_confirmation: True if high risk

    Flow:
    1. Check if consequence analysis is needed
    2. Extract action parameters from state
    3. Call get_consequences_for_action() tool
    4. Parse risk level and consequences
    5. Set requires_confirmation flag for high-risk actions
    """
    try:
        # Check if this action requires consequence checking
        requires_check = state.get("requires_consequence_check", False)

        if not requires_check:
            # Skip consequence checking for safe actions
            return {
                "consequences": None,
                "risk_level": "none",
                "requires_confirmation": False,
                "error": None,
            }

        # Get action details from state
        intent = state.get("intent")
        action_type = state.get("action_type")
        tool_params = state.get("tool_params", {})
        extracted_entities = state.get("extracted_entities", {})

        # Determine entity_id based on action type
        entity_id = None

        if intent == "remove_vehicle" or action_type == "delete":
            # For remove_vehicle, entity_id is the trip_id
            entity_id = tool_params.get("trip_id")

            # If trip_id not in tool_params, try extracted_entities
            if not entity_id:
                entity_id = extracted_entities.get("trip_id")

            # Also try trip_name and trip_ids (array)
            if not entity_id:
                entity_id = extracted_entities.get("trip_name")

            if not entity_id and extracted_entities.get("trip_ids"):
                # If trip_ids is an array, take the first one
                trip_ids = extracted_entities.get("trip_ids", [])
                if trip_ids and len(trip_ids) > 0:
                    entity_id = trip_ids[0]

            # Use "remove_vehicle" as action_type for consequence checking
            consequence_action_type = "remove_vehicle"

        elif intent == "delete_trip":
            entity_id = tool_params.get("trip_id")
            if not entity_id:
                entity_id = extracted_entities.get("trip_id") or extracted_entities.get("trip_name")
            if not entity_id and extracted_entities.get("trip_ids"):
                trip_ids = extracted_entities.get("trip_ids", [])
                if trip_ids:
                    entity_id = trip_ids[0]
            consequence_action_type = "delete_trip"

        elif intent == "deactivate_route":
            entity_id = tool_params.get("route_id")
            if not entity_id:
                entity_id = extracted_entities.get("route_id") or extracted_entities.get("route_name")
            consequence_action_type = "deactivate_route"

        else:
            # Unknown action requiring consequence check
            return {
                "consequences": None,
                "risk_level": "low",
                "requires_confirmation": False,
                "error": f"Consequence checking not implemented for intent: {intent}",
                "error_node": "check_consequences_node"
            }

        if not entity_id:
            # Cannot check consequences without entity_id
            return {
                "consequences": None,
                "risk_level": "low",
                "requires_confirmation": False,
                "error": f"Missing entity_id for consequence checking (intent: {intent})",
                "error_node": "check_consequences_node"
            }

        # Get database session
        async for db in get_db():
            # Resolve entity_id (could be name or ID)
            if consequence_action_type in ["remove_vehicle", "delete_trip"]:
                resolved_entity_id = await _resolve_trip_id(entity_id, db)
            elif consequence_action_type == "deactivate_route":
                resolved_entity_id = await _resolve_route_id(entity_id, db)
            else:
                resolved_entity_id = entity_id

            if not resolved_entity_id:
                return {
                    "consequences": None,
                    "risk_level": "low",
                    "requires_confirmation": False,
                    "error": f"Could not resolve entity identifier '{entity_id}' to ID",
                    "error_node": "check_consequences_node"
                }

            # Call consequence checking tool
            consequence_result = await get_consequences_for_action(
                action_type=consequence_action_type,
                entity_id=resolved_entity_id,
                db=db
            )

            # Check if tool call succeeded
            if not consequence_result.get("success"):
                return {
                    "consequences": None,
                    "risk_level": "low",
                    "requires_confirmation": False,
                    "error": consequence_result.get("error", "Consequence check failed"),
                    "error_node": "check_consequences_node"
                }

            # Extract consequence data
            consequence_data = consequence_result.get("data", {})
            risk_level = consequence_data.get("risk_level", "none")

            # Determine if confirmation is required
            # HIGH risk always requires confirmation
            # LOW risk may require confirmation based on context
            requires_confirmation = risk_level == "high"

            return {
                "consequences": consequence_data,
                "risk_level": risk_level,
                "requires_confirmation": requires_confirmation,
                "error": None,
            }

        # If we get here, database session failed
        return {
            "consequences": None,
            "risk_level": "low",
            "requires_confirmation": False,
            "error": "Failed to get database session",
            "error_node": "check_consequences_node"
        }

    except Exception as e:
        return {
            "consequences": None,
            "risk_level": "low",
            "requires_confirmation": False,
            "error": f"Consequence checking failed: {str(e)}",
            "error_node": "check_consequences_node"
        }
