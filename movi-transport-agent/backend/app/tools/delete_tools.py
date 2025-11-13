"""
Delete operation tools for Movi Transport Agent.

These tools perform delete operations on the database.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.deployment import Deployment
from app.models.daily_trip import DailyTrip
from app.models.vehicle import Vehicle
from .base import success_response, error_response


async def remove_vehicle_from_trip(trip_id, db: AsyncSession) -> Dict[str, Any]:
    """
    Remove vehicle and driver assignment from a trip (delete deployment).

    This is a DELETE operation on DYNAMIC assets.

    IMPORTANT: This should trigger the "Tribal Knowledge" consequence flow
    if the trip has any bookings.

    Args:
        trip_id: The trip ID (int) or display_name (str) to remove vehicle from
        db: Database session

    Returns:
        {
            "success": True,
            "data": {"trip_id": int, "removed_vehicle": str, ...},
            "message": str
        }

    Example User Query:
        "Remove the vehicle from 'Bulk - 00:01'"
        "Unassign vehicle from trip 1"

    Note: In the LangGraph flow, this action should be preceded by
    check_consequences_node if the trip has bookings.
    """
    try:
        # Resolve trip_id (can be int or string name)
        if isinstance(trip_id, str):
            # Try to convert to int first
            try:
                trip_id = int(trip_id)
            except ValueError:
                # It's a trip name, look it up with fuzzy matching
                trip_name_search = trip_id.strip()

                # Try exact match first
                trip_lookup_result = await db.execute(
                    select(DailyTrip).where(DailyTrip.display_name == trip_name_search)
                )
                trip = trip_lookup_result.scalar_one_or_none()

                # If no exact match, try case-insensitive match
                if not trip:
                    trip_lookup_result = await db.execute(
                        select(DailyTrip).where(DailyTrip.display_name.ilike(trip_name_search))
                    )
                    trip = trip_lookup_result.scalar_one_or_none()

                # If still no match, try partial match (for time format variations like "6:00" vs "06:00")
                if not trip:
                    # Normalize time format in search string (6:00 → 06:00)
                    import re
                    normalized_search = re.sub(r'\b(\d):(\d{2})\b', r'0\1:\2', trip_name_search)

                    trip_lookup_result = await db.execute(
                        select(DailyTrip).where(DailyTrip.display_name.ilike(f"%{normalized_search}%"))
                    )
                    trip = trip_lookup_result.scalar_one_or_none()

                if not trip:
                    # Get similar trip names for helpful error
                    all_trips_result = await db.execute(
                        select(DailyTrip.display_name).limit(10)
                    )
                    available_trips = [row[0] for row in all_trips_result.fetchall()]

                    return error_response(
                        error=f"Trip '{trip_id}' not found. Available trips: {', '.join(available_trips[:5])}...",
                        message="Trip not found in database"
                    )
                trip_id = trip.trip_id

        # Verify trip exists (if we have an int ID)
        trip_result = await db.execute(
            select(DailyTrip).where(DailyTrip.trip_id == trip_id)
        )
        trip = trip_result.scalar_one_or_none()
        if not trip:
            return error_response(
                error=f"Trip ID {trip_id} not found",
                message="Trip not found in database"
            )

        # Get deployment info before deleting
        deployment_result = await db.execute(
            select(Deployment, Vehicle)
            .join(Vehicle, Deployment.vehicle_id == Vehicle.vehicle_id)
            .where(Deployment.trip_id == trip_id)
        )
        deployment_row = deployment_result.first()

        if not deployment_row:
            return error_response(
                error=f"No vehicle assigned to trip '{trip.display_name}'",
                message="Trip has no deployment to remove"
            )

        deployment, vehicle = deployment_row

        # Delete deployment
        await db.execute(
            delete(Deployment).where(Deployment.trip_id == trip_id)
        )
        await db.commit()

        return success_response(
            data={
                "trip_id": trip_id,
                "trip_name": trip.display_name,
                "removed_vehicle_id": vehicle.vehicle_id,
                "removed_vehicle_license": vehicle.license_plate,
                "removed_deployment_id": deployment.deployment_id
            },
            message=f"Successfully removed vehicle {vehicle.license_plate} from trip '{trip.display_name}'"
        )

    except Exception as e:
        await db.rollback()
        return error_response(
            error=str(e),
            message=f"Failed to remove vehicle from trip {trip_id}"
        )
