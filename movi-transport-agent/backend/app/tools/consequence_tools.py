"""
Consequence checking tools for Movi Transport Agent.

These tools implement the "Tribal Knowledge" flow by checking consequences
of actions before they are executed.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.daily_trip import DailyTrip
from app.models.deployment import Deployment
from app.models.vehicle import Vehicle
from .base import success_response, error_response


async def get_consequences_for_action(
    action_type: str,
    entity_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Check consequences of performing an action on an entity.

    This is the CORE of the "Tribal Knowledge" flow.

    This tool analyzes the impact of actions like removing a vehicle from a trip
    and returns risk level and detailed explanations.

    Args:
        action_type: Type of action (e.g., "remove_vehicle", "delete_trip", etc.)
        entity_id: ID of the entity being acted upon
        db: Database session

    Returns:
        {
            "success": True,
            "data": {
                "risk_level": "none" | "low" | "high",
                "action_type": str,
                "entity_id": int,
                "consequences": [str],  # List of consequence descriptions
                "affected_bookings": int (if applicable),
                "explanation": str,  # Detailed explanation
                "proceed_with_caution": bool
            },
            "message": str
        }

    Risk Levels:
    - "none": Safe to proceed, no consequences
    - "low": Minor consequences, user should be informed
    - "high": Significant consequences, requires confirmation

    Example Flow:
        User: "Remove vehicle from 'Bulk - 00:01'"
        -> classify_intent_node detects action_type="remove_vehicle"
        -> check_consequences_node calls get_consequences_for_action("remove_vehicle", trip_id=1)
        -> Returns: risk_level="high", explanation="Trip is 25% booked..."
        -> Conditional edge routes to get_confirmation_node
        -> User confirms -> execute_action_node removes vehicle
    """
    try:
        # Route to appropriate consequence checker based on action type
        if action_type == "remove_vehicle":
            return await _check_remove_vehicle_consequences(entity_id, db)
        elif action_type == "delete_trip":
            return await _check_delete_trip_consequences(entity_id, db)
        elif action_type == "deactivate_route":
            return await _check_deactivate_route_consequences(entity_id, db)
        else:
            # For other actions, return no consequences (read-only or creation)
            return success_response(
                data={
                    "risk_level": "none",
                    "action_type": action_type,
                    "entity_id": entity_id,
                    "consequences": [],
                    "explanation": f"Action '{action_type}' has no significant consequences",
                    "proceed_with_caution": False
                },
                message="No consequences detected"
            )

    except Exception as e:
        return error_response(
            error=str(e),
            message=f"Failed to check consequences for action '{action_type}'"
        )


async def _check_remove_vehicle_consequences(
    trip_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Check consequences of removing a vehicle from a trip.

    This is the CRITICAL tribal knowledge rule:
    - If trip has bookings > 0%, removing vehicle will:
      1. Cancel all bookings
      2. Break trip-sheet generation
      3. Affect employees who booked this trip

    Args:
        trip_id: Trip ID to check
        db: Database session

    Returns:
        Consequence analysis with risk_level
    """
    # Get trip details
    trip_result = await db.execute(
        select(DailyTrip).where(DailyTrip.trip_id == trip_id)
    )
    trip = trip_result.scalar_one_or_none()

    if not trip:
        return error_response(
            error=f"Trip ID {trip_id} not found",
            message="Cannot check consequences for non-existent trip"
        )

    # Check if trip has deployment
    deployment_result = await db.execute(
        select(Deployment, Vehicle)
        .join(Vehicle, Deployment.vehicle_id == Vehicle.vehicle_id)
        .where(Deployment.trip_id == trip_id)
    )
    deployment_row = deployment_result.first()

    has_deployment = deployment_row is not None
    has_bookings = trip.booking_percentage > 0

    consequences = []
    risk_level = "none"
    explanation = ""

    if not has_deployment:
        # No vehicle assigned, no consequences
        risk_level = "none"
        explanation = f"Trip '{trip.display_name}' has no vehicle assigned. No action needed."
        consequences.append("No vehicle currently assigned to this trip")

    elif has_bookings:
        # HIGH RISK: Trip has bookings
        risk_level = "high"
        _, vehicle = deployment_row

        # Estimate affected employees (assuming average capacity usage)
        estimated_bookings = int(vehicle.capacity * trip.booking_percentage / 100)

        explanation = (
            f"WARNING - CRITICAL: Trip '{trip.display_name}' is {trip.booking_percentage}% booked. "
            f"Removing vehicle '{vehicle.license_plate}' will:\n"
            f"1. Cancel approximately {estimated_bookings} employee bookings\n"
            f"2. Break trip-sheet generation for this route\n"
            f"3. Require immediate notification to affected employees\n"
            f"4. May cause operational disruption"
        )

        consequences.extend([
            f"Trip is {trip.booking_percentage}% booked",
            f"Approximately {estimated_bookings} employees will be affected",
            "All bookings will be cancelled",
            "Trip-sheet generation will fail",
            "Employees need to be notified immediately"
        ])

    else:
        # LOW RISK: Vehicle assigned but no bookings yet
        risk_level = "low"
        _, vehicle = deployment_row

        explanation = (
            f"Trip '{trip.display_name}' has vehicle '{vehicle.license_plate}' assigned "
            f"but no bookings yet ({trip.booking_percentage}% booked). "
            f"Safe to remove, but trip will need a vehicle before employees can book."
        )

        consequences.extend([
            "Vehicle is assigned but no bookings exist yet",
            "Safe to remove without affecting employees",
            "Trip will need reassignment before accepting bookings"
        ])

    return success_response(
        data={
            "risk_level": risk_level,
            "action_type": "remove_vehicle",
            "entity_id": trip_id,
            "trip_name": trip.display_name,
            "booking_percentage": trip.booking_percentage,
            "has_deployment": has_deployment,
            "consequences": consequences,
            "explanation": explanation,
            "proceed_with_caution": risk_level == "high",
            "affected_bookings": int(vehicle.capacity * trip.booking_percentage / 100) if has_bookings and deployment_row else 0
        },
        message=f"Consequence check complete: {risk_level.upper()} risk"
    )


async def _check_delete_trip_consequences(
    trip_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Check consequences of deleting a trip.

    Args:
        trip_id: Trip ID to check
        db: Database session

    Returns:
        Consequence analysis
    """
    # Similar logic to remove_vehicle, but for trip deletion
    trip_result = await db.execute(
        select(DailyTrip).where(DailyTrip.trip_id == trip_id)
    )
    trip = trip_result.scalar_one_or_none()

    if not trip:
        return error_response(
            error=f"Trip ID {trip_id} not found",
            message="Cannot check consequences for non-existent trip"
        )

    has_bookings = trip.booking_percentage > 0

    if has_bookings:
        risk_level = "high"
        explanation = f"Trip '{trip.display_name}' has {trip.booking_percentage}% bookings. Deleting will cancel all bookings."
    else:
        risk_level = "low"
        explanation = f"Trip '{trip.display_name}' has no bookings. Safe to delete."

    return success_response(
        data={
            "risk_level": risk_level,
            "action_type": "delete_trip",
            "entity_id": trip_id,
            "consequences": [explanation],
            "explanation": explanation,
            "proceed_with_caution": risk_level == "high"
        },
        message=f"Consequence check complete: {risk_level.upper()} risk"
    )


async def _check_deactivate_route_consequences(
    route_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Check consequences of deactivating a route.

    Args:
        route_id: Route ID to check
        db: Database session

    Returns:
        Consequence analysis
    """
    from app.models.route import Route

    # Check how many active trips use this route
    trips_result = await db.execute(
        select(DailyTrip).where(DailyTrip.route_id == route_id)
    )
    trips = trips_result.scalars().all()

    active_trips_with_bookings = [t for t in trips if t.booking_percentage > 0]

    if active_trips_with_bookings:
        risk_level = "high"
        explanation = f"Route has {len(active_trips_with_bookings)} active trips with bookings. Deactivating will affect ongoing operations."
    else:
        risk_level = "low"
        explanation = "Route has no active trips with bookings. Safe to deactivate."

    return success_response(
        data={
            "risk_level": risk_level,
            "action_type": "deactivate_route",
            "entity_id": route_id,
            "consequences": [explanation],
            "explanation": explanation,
            "proceed_with_caution": risk_level == "high",
            "affected_trips": len(active_trips_with_bookings)
        },
        message=f"Consequence check complete: {risk_level.upper()} risk"
    )
