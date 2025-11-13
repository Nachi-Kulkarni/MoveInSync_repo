"""
Read operation tools for Movi Transport Agent.

These tools perform read-only queries on the database for both static and dynamic assets.
"""
import json
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.vehicle import Vehicle
from app.models.deployment import Deployment
from app.models.daily_trip import DailyTrip
from app.models.route import Route
from app.models.path import Path
from app.models.stop import Stop
from app.models.driver import Driver
from .base import success_response, error_response


async def get_unassigned_vehicles_count(db: AsyncSession) -> Dict[str, Any]:
    """
    Get count of vehicles that are not currently assigned to any trip.

    This is a READ operation on DYNAMIC assets.

    Args:
        db: Database session

    Returns:
        {
            "success": True,
            "data": {"count": int, "vehicles": [...]},
            "message": str
        }

    Example User Query:
        "How many vehicles are not assigned?"
        "Show me unassigned vehicles"
    """
    try:
        # Subquery to get all assigned vehicle IDs
        assigned_vehicle_ids_subquery = select(Deployment.vehicle_id).distinct().subquery()

        # Get unassigned vehicles
        result = await db.execute(
            select(Vehicle).where(
                Vehicle.vehicle_id.not_in(select(assigned_vehicle_ids_subquery))
            )
        )
        unassigned_vehicles = result.scalars().all()

        vehicles_data = [
            {
                "vehicle_id": v.vehicle_id,
                "license_plate": v.license_plate,
                "type": v.type,
                "capacity": v.capacity
            }
            for v in unassigned_vehicles
        ]

        return success_response(
            data={
                "count": len(vehicles_data),
                "vehicles": vehicles_data
            },
            message=f"Found {len(vehicles_data)} unassigned vehicles"
        )

    except Exception as e:
        return error_response(
            error=str(e),
            message="Failed to fetch unassigned vehicles count"
        )


async def get_trip_status(trip_id, db: AsyncSession) -> Dict[str, Any]:
    """
    Get detailed status of a specific trip including bookings and deployment.

    This is a READ operation on DYNAMIC assets.

    Args:
        trip_id: The trip ID (int) or display_name (str) to query
        db: Database session

    Returns:
        {
            "success": True,
            "data": {
                "trip_id": int,
                "display_name": str,
                "booking_percentage": int,
                "live_status": str,
                "route_id": int,
                "deployment": {...} or None
            },
            "message": str
        }

    Example User Query:
        "What's the status of the 'Bulk - 00:01' trip?"
        "Show me details for trip 1"
    """
    try:
        # Resolve trip_id (can be int or string name)
        if isinstance(trip_id, str):
            # Try to convert to int first
            try:
                trip_id = int(trip_id)
            except ValueError:
                # It's a trip name, look it up
                trip_lookup_result = await db.execute(
                    select(DailyTrip).where(DailyTrip.display_name == trip_id)
                )
                trip = trip_lookup_result.scalar_one_or_none()
                if not trip:
                    return error_response(
                        error=f"Trip '{trip_id}' not found",
                        message="Trip not found in database"
                    )
                trip_id = trip.trip_id

        # Get trip details (if we have an int ID)
        result = await db.execute(
            select(DailyTrip).where(DailyTrip.trip_id == trip_id)
        )
        trip = result.scalar_one_or_none()

        if not trip:
            return error_response(
                error=f"Trip ID {trip_id} not found",
                message="Trip not found in database"
            )

        # Get deployment info if exists
        deployment_result = await db.execute(
            select(Deployment, Vehicle, Driver)
            .join(Vehicle, Deployment.vehicle_id == Vehicle.vehicle_id)
            .join(Driver, Deployment.driver_id == Driver.driver_id)
            .where(Deployment.trip_id == trip_id)
        )
        deployment_row = deployment_result.first()

        deployment_data = None
        if deployment_row:
            deployment, vehicle, driver = deployment_row
            deployment_data = {
                "deployment_id": deployment.deployment_id,
                "vehicle": {
                    "vehicle_id": vehicle.vehicle_id,
                    "license_plate": vehicle.license_plate,
                    "type": vehicle.type
                },
                "driver": {
                    "driver_id": driver.driver_id,
                    "name": driver.name,
                    "phone": driver.phone_number
                }
            }

        trip_data = {
            "trip_id": trip.trip_id,
            "display_name": trip.display_name,
            "booking_percentage": trip.booking_percentage,
            "live_status": trip.live_status,
            "route_id": trip.route_id,
            "deployment": deployment_data
        }

        return success_response(
            data=trip_data,
            message=f"Retrieved status for trip '{trip.display_name}'"
        )

    except Exception as e:
        return error_response(
            error=str(e),
            message=f"Failed to fetch trip status for trip_id {trip_id}"
        )


async def list_stops_for_path(path_name: str, db: AsyncSession) -> Dict[str, Any]:
    """
    List all stops in order for a specific path.

    This is a READ operation on STATIC assets.

    Args:
        path_name: The path name (str like "Path-1") or path ID (can be converted from str)
        db: Database session

    Returns:
        {
            "success": True,
            "data": {
                "path_id": int,
                "path_name": str,
                "stops": [{"stop_id": int, "name": str, ...}, ...]
            },
            "message": str
        }

    Example User Query:
        "List all stops for 'Path-2'"
        "Show me the stops in Path 1"
    """
    try:
        # Resolve path_name to path object
        if isinstance(path_name, int):
            # If somehow an int is passed, use it as path_id
            result = await db.execute(
                select(Path).where(Path.path_id == path_name)
            )
        else:
            # Try to convert to int first
            try:
                path_id = int(path_name)
                result = await db.execute(
                    select(Path).where(Path.path_id == path_id)
                )
            except ValueError:
                # It's a path name string, look it up
                result = await db.execute(
                    select(Path).where(Path.path_name == path_name)
                )

        path = result.scalar_one_or_none()

        if not path:
            return error_response(
                error=f"Path '{path_name}' not found",
                message="Path not found in database"
            )

        # Parse ordered stop IDs (stored as JSON string)
        try:
            stop_ids = json.loads(path.ordered_stop_ids)
        except json.JSONDecodeError:
            return error_response(
                error="Invalid stop IDs format in path",
                message="Path data is corrupted"
            )

        # Get stop details in order
        stops_data = []
        for stop_id in stop_ids:
            stop_result = await db.execute(
                select(Stop).where(Stop.stop_id == stop_id)
            )
            stop = stop_result.scalar_one_or_none()
            if stop:
                stops_data.append({
                    "stop_id": stop.stop_id,
                    "name": stop.name,
                    "latitude": stop.latitude,
                    "longitude": stop.longitude
                })

        return success_response(
            data={
                "path_id": path.path_id,
                "path_name": path.path_name,
                "stops": stops_data,
                "stop_count": len(stops_data)
            },
            message=f"Retrieved {len(stops_data)} stops for path '{path.path_name}'"
        )

    except Exception as e:
        return error_response(
            error=str(e),
            message=f"Failed to fetch stops for path '{path_name}'"
        )


async def list_routes_by_path(path_name: str, db: AsyncSession) -> Dict[str, Any]:
    """
    List all routes that use a specific path.

    This is a READ operation on STATIC assets.

    Args:
        path_name: The path name (str like "Path-1") or path ID (can be converted from str)
        db: Database session

    Returns:
        {
            "success": True,
            "data": {
                "path_id": int,
                "routes": [{"route_id": int, "route_display_name": str, ...}, ...]
            },
            "message": str
        }

    Example User Query:
        "Show me all routes that use 'Path-1'"
        "Which routes are on Path 2?"
    """
    try:
        # Resolve path_name to path object
        if isinstance(path_name, int):
            # If somehow an int is passed, use it as path_id
            path_result = await db.execute(
                select(Path).where(Path.path_id == path_name)
            )
        else:
            # Try to convert to int first
            try:
                path_id = int(path_name)
                path_result = await db.execute(
                    select(Path).where(Path.path_id == path_id)
                )
            except ValueError:
                # It's a path name string, look it up
                path_result = await db.execute(
                    select(Path).where(Path.path_name == path_name)
                )

        path = path_result.scalar_one_or_none()

        if not path:
            return error_response(
                error=f"Path '{path_name}' not found",
                message="Path not found in database"
            )

        # Get all routes for this path
        result = await db.execute(
            select(Route).where(Route.path_id == path.path_id)
        )
        routes = result.scalars().all()

        routes_data = [
            {
                "route_id": r.route_id,
                "route_display_name": r.route_display_name,
                "shift_time": r.shift_time,
                "direction": r.direction,
                "start_point": r.start_point,
                "end_point": r.end_point,
                "status": r.status
            }
            for r in routes
        ]

        return success_response(
            data={
                "path_id": path.path_id,
                "path_name": path.path_name,
                "routes": routes_data,
                "route_count": len(routes_data)
            },
            message=f"Found {len(routes_data)} routes using path '{path.path_name}'"
        )

    except Exception as e:
        return error_response(
            error=str(e),
            message=f"Failed to fetch routes for path '{path_name}'"
        )
