"""
Create operation tools for Movi Transport Agent.

These tools perform write operations to create new records in the database.
"""
import json
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.deployment import Deployment
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.daily_trip import DailyTrip
from app.models.stop import Stop
from app.models.path import Path
from app.models.route import Route
from .base import success_response, error_response


async def assign_vehicle_to_trip(
    trip_id: int,
    vehicle_id: int,
    driver_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Assign a vehicle and driver to a trip by creating a deployment.

    This is a CREATE operation on DYNAMIC assets.

    Args:
        trip_id: The trip ID to assign to
        vehicle_id: The vehicle ID to assign
        driver_id: The driver ID to assign
        db: Database session

    Returns:
        {
            "success": True,
            "data": {"deployment_id": int, ...},
            "message": str
        }

    Example User Query:
        "Assign vehicle 'MH-12-3456' and driver 'Amit' to the 'Path Path - 00:02' trip"
        "Deploy vehicle 1 with driver 2 to trip 5"
    """
    try:
        # Verify trip exists
        trip_result = await db.execute(
            select(DailyTrip).where(DailyTrip.trip_id == trip_id)
        )
        trip = trip_result.scalar_one_or_none()
        if not trip:
            return error_response(
                error=f"Trip ID {trip_id} not found",
                message="Trip not found in database"
            )

        # Verify vehicle exists and is not already assigned
        vehicle_result = await db.execute(
            select(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
        )
        vehicle = vehicle_result.scalar_one_or_none()
        if not vehicle:
            return error_response(
                error=f"Vehicle ID {vehicle_id} not found",
                message="Vehicle not found in database"
            )

        # Check if vehicle is already assigned
        existing_deployment = await db.execute(
            select(Deployment).where(Deployment.vehicle_id == vehicle_id)
        )
        if existing_deployment.scalar_one_or_none():
            return error_response(
                error=f"Vehicle {vehicle.license_plate} is already assigned to another trip",
                message="Vehicle already deployed"
            )

        # Verify driver exists
        driver_result = await db.execute(
            select(Driver).where(Driver.driver_id == driver_id)
        )
        driver = driver_result.scalar_one_or_none()
        if not driver:
            return error_response(
                error=f"Driver ID {driver_id} not found",
                message="Driver not found in database"
            )

        # Check if trip already has a deployment
        trip_deployment = await db.execute(
            select(Deployment).where(Deployment.trip_id == trip_id)
        )
        if trip_deployment.scalar_one_or_none():
            return error_response(
                error=f"Trip '{trip.display_name}' already has a vehicle assigned",
                message="Trip already has deployment"
            )

        # Create deployment
        deployment = Deployment(
            trip_id=trip_id,
            vehicle_id=vehicle_id,
            driver_id=driver_id
        )
        db.add(deployment)
        await db.commit()
        await db.refresh(deployment)

        return success_response(
            data={
                "deployment_id": deployment.deployment_id,
                "trip_id": trip_id,
                "trip_name": trip.display_name,
                "vehicle_id": vehicle_id,
                "vehicle_license": vehicle.license_plate,
                "driver_id": driver_id,
                "driver_name": driver.name
            },
            message=f"Successfully assigned {vehicle.license_plate} and driver {driver.name} to trip '{trip.display_name}'"
        )

    except Exception as e:
        await db.rollback()
        return error_response(
            error=str(e),
            message="Failed to assign vehicle and driver to trip"
        )


async def create_stop(
    name: str,
    latitude: float,
    longitude: float,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Create a new stop (geographic location).

    This is a CREATE operation on STATIC assets.

    Args:
        name: Stop name (e.g., "Odeon Circle")
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        db: Database session

    Returns:
        {
            "success": True,
            "data": {"stop_id": int, ...},
            "message": str
        }

    Example User Query:
        "Create a new stop called 'Odeon Circle'"
        "Add a stop at Koramangala with coordinates 12.9352, 77.6245"
    """
    try:
        # Check if stop with same name already exists
        existing_stop = await db.execute(
            select(Stop).where(Stop.name == name)
        )
        if existing_stop.scalar_one_or_none():
            return error_response(
                error=f"Stop '{name}' already exists",
                message="Stop with this name already exists"
            )

        # Create stop
        stop = Stop(
            name=name,
            latitude=latitude,
            longitude=longitude
        )
        db.add(stop)
        await db.commit()
        await db.refresh(stop)

        return success_response(
            data={
                "stop_id": stop.stop_id,
                "name": stop.name,
                "latitude": stop.latitude,
                "longitude": stop.longitude
            },
            message=f"Successfully created stop '{name}'"
        )

    except Exception as e:
        await db.rollback()
        return error_response(
            error=str(e),
            message=f"Failed to create stop '{name}'"
        )


async def create_path(
    name: str,
    stop_ids: List[int],
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Create a new path as an ordered sequence of stops.

    This is a CREATE operation on STATIC assets.

    Args:
        name: Path name (e.g., "Tech-Loop")
        stop_ids: Ordered list of stop IDs [1, 3, 5]
        db: Database session

    Returns:
        {
            "success": True,
            "data": {"path_id": int, ...},
            "message": str
        }

    Example User Query:
        "Create a new path called 'Tech-Loop' using stops [Gavipuram, Temple, Peenya]"
        "Add path named 'Express' with stops 1, 2, 3"
    """
    try:
        # Check if path with same name already exists
        existing_path = await db.execute(
            select(Path).where(Path.path_name == name)
        )
        if existing_path.scalar_one_or_none():
            return error_response(
                error=f"Path '{name}' already exists",
                message="Path with this name already exists"
            )

        # Verify all stop IDs exist
        for stop_id in stop_ids:
            stop_result = await db.execute(
                select(Stop).where(Stop.stop_id == stop_id)
            )
            if not stop_result.scalar_one_or_none():
                return error_response(
                    error=f"Stop ID {stop_id} not found",
                    message="One or more stops do not exist"
                )

        # Create path with ordered stop IDs as JSON
        path = Path(
            path_name=name,
            ordered_stop_ids=json.dumps(stop_ids)
        )
        db.add(path)
        await db.commit()
        await db.refresh(path)

        # Get stop names for response
        stop_names = []
        for stop_id in stop_ids:
            stop_result = await db.execute(
                select(Stop).where(Stop.stop_id == stop_id)
            )
            stop = stop_result.scalar_one()
            stop_names.append(stop.name)

        return success_response(
            data={
                "path_id": path.path_id,
                "path_name": path.path_name,
                "stop_ids": stop_ids,
                "stop_names": stop_names,
                "stop_count": len(stop_ids)
            },
            message=f"Successfully created path '{name}' with {len(stop_ids)} stops"
        )

    except Exception as e:
        await db.rollback()
        return error_response(
            error=str(e),
            message=f"Failed to create path '{name}'"
        )


async def create_route(
    path_id: int,
    shift_time: str,
    direction: str,
    start_point: str,
    end_point: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Create a new route by assigning a time to a path.

    This is a CREATE operation on STATIC assets.

    Args:
        path_id: The path ID to use
        shift_time: Time for this route (e.g., "19:45")
        direction: "LOGIN" or "LOGOUT"
        start_point: Starting location name
        end_point: Ending location name
        db: Database session

    Returns:
        {
            "success": True,
            "data": {"route_id": int, ...},
            "message": str
        }

    Example User Query:
        "Create a route using Path 1 at 08:00 AM for LOGIN"
        "Add a new route on Path-2 at 19:45 for LOGOUT from Office to Residence"
    """
    try:
        # Verify path exists
        path_result = await db.execute(
            select(Path).where(Path.path_id == path_id)
        )
        path = path_result.scalar_one_or_none()
        if not path:
            return error_response(
                error=f"Path ID {path_id} not found",
                message="Path not found in database"
            )

        # Validate direction
        if direction not in ["LOGIN", "LOGOUT"]:
            return error_response(
                error=f"Invalid direction '{direction}'. Must be 'LOGIN' or 'LOGOUT'",
                message="Invalid direction value"
            )

        # Generate route display name
        route_display_name = f"{path.path_name} - {shift_time}"

        # Create route
        route = Route(
            path_id=path_id,
            route_display_name=route_display_name,
            shift_time=shift_time,
            direction=direction,
            start_point=start_point,
            end_point=end_point,
            status="active"
        )
        db.add(route)
        await db.commit()
        await db.refresh(route)

        return success_response(
            data={
                "route_id": route.route_id,
                "route_display_name": route.route_display_name,
                "path_id": path_id,
                "path_name": path.path_name,
                "shift_time": shift_time,
                "direction": direction,
                "start_point": start_point,
                "end_point": end_point,
                "status": route.status
            },
            message=f"Successfully created route '{route_display_name}'"
        )

    except Exception as e:
        await db.rollback()
        return error_response(
            error=str(e),
            message="Failed to create route"
        )
