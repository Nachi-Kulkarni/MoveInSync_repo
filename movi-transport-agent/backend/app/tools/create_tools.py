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
    trip_id,
    vehicle_id: str,
    driver_id = None,  # Accept both int (driver ID) and str (driver name)
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Assign a vehicle and optionally a driver to a trip by creating a deployment.

    This is a CREATE operation on DYNAMIC assets.

    Args:
        trip_id: The trip ID (int) or display_name (str) to assign to
        vehicle_id: The vehicle license plate (str like "MH-12-3456") or vehicle ID (int)
        driver_id: The driver ID (int) or driver name (str like "Amit" or "Amit Kumar") - optional
        db: Database session

    Returns:
        {
            "success": True,
            "data": {"deployment_id": int, ...},
            "message": str
        }

    Example User Query:
        "Assign vehicle 'MH-12-GH-3456' and driver 'Amit' to the 'Path Path - 00:02' trip"
        "Assign vehicle 'KA-01-AB-1234' to trip 1"
        "Deploy vehicle 1 with driver 2 to trip 5"
    """
    try:
        # Resolve trip_id (can be int or string name)
        if isinstance(trip_id, str):
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

        # Resolve vehicle_id (can be license plate string or int ID)
        if isinstance(vehicle_id, str):
            # Try to convert to int first
            try:
                vehicle_id = int(vehicle_id)
                vehicle_result = await db.execute(
                    select(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
                )
            except ValueError:
                # It's a license plate, look it up
                vehicle_result = await db.execute(
                    select(Vehicle).where(Vehicle.license_plate == vehicle_id)
                )
        else:
            vehicle_result = await db.execute(
                select(Vehicle).where(Vehicle.vehicle_id == vehicle_id)
            )

        vehicle = vehicle_result.scalar_one_or_none()
        if not vehicle:
            return error_response(
                error=f"Vehicle '{vehicle_id}' not found",
                message="Vehicle not found in database"
            )

        # Check if vehicle is already assigned
        existing_deployment = await db.execute(
            select(Deployment).where(Deployment.vehicle_id == vehicle.vehicle_id)
        )
        if existing_deployment.scalar_one_or_none():
            return error_response(
                error=f"Vehicle {vehicle.license_plate} is already assigned to another trip",
                message="Vehicle already deployed"
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

        # Get or verify driver
        driver = None
        if driver_id is not None:
            # Resolve driver_id (can be int ID or string name)
            if isinstance(driver_id, int):
                # It's a driver ID
                driver_result = await db.execute(
                    select(Driver).where(Driver.driver_id == driver_id)
                )
                driver = driver_result.scalar_one_or_none()
                if not driver:
                    return error_response(
                        error=f"Driver ID {driver_id} not found",
                        message="Driver not found in database"
                    )
            else:
                # It's a driver name - try partial match
                driver_name = str(driver_id).strip()
                # Try exact match first
                driver_result = await db.execute(
                    select(Driver).where(Driver.name == driver_name)
                )
                driver = driver_result.scalar_one_or_none()

                if not driver:
                    # Try partial match (e.g., "Amit" matches "Amit Kumar")
                    driver_result = await db.execute(
                        select(Driver).where(Driver.name.like(f"%{driver_name}%"))
                    )
                    driver = driver_result.scalar_one_or_none()

                if not driver:
                    # Get available drivers for helpful error
                    all_drivers_result = await db.execute(
                        select(Driver.name).order_by(Driver.name)
                    )
                    available_drivers = [row[0] for row in all_drivers_result.fetchall()]
                    return error_response(
                        error=f"Driver '{driver_name}' not found. Available drivers: {', '.join(available_drivers)}",
                        message="Driver not found in database"
                    )
        else:
            # Auto-assign an available driver (driver_id is required by database)
            # First, try to find unassigned driver
            unassigned_driver_result = await db.execute(
                select(Driver)
                .outerjoin(Deployment, Driver.driver_id == Deployment.driver_id)
                .where(Deployment.driver_id.is_(None))
                .limit(1)
            )
            driver = unassigned_driver_result.scalar_one_or_none()

            if not driver:
                # If no unassigned drivers, use any driver (reassignment allowed)
                any_driver_result = await db.execute(
                    select(Driver).limit(1)
                )
                driver = any_driver_result.scalar_one_or_none()

            if not driver:
                return error_response(
                    error="No drivers available in the system",
                    message="Cannot assign vehicle without a driver"
                )

        # Create deployment
        deployment = Deployment(
            trip_id=trip_id,
            vehicle_id=vehicle.vehicle_id,
            driver_id=driver.driver_id
        )
        db.add(deployment)
        await db.commit()
        await db.refresh(deployment)

        # Build response message
        if driver:
            message = f"Successfully assigned {vehicle.license_plate} and driver {driver.name} to trip '{trip.display_name}'"
            driver_data = {"driver_id": driver.driver_id, "driver_name": driver.name}
        else:
            message = f"Successfully assigned {vehicle.license_plate} to trip '{trip.display_name}' (no driver assigned)"
            driver_data = {"driver_id": None, "driver_name": None}

        return success_response(
            data={
                "deployment_id": deployment.deployment_id,
                "trip_id": trip_id,
                "trip_name": trip.display_name,
                "vehicle_id": vehicle.vehicle_id,
                "vehicle_license": vehicle.license_plate,
                **driver_data
            },
            message=message
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
    path_name: str,
    ordered_stop_ids: List,  # Accept both int and str (stop IDs or stop names)
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Create a new path as an ordered sequence of stops.

    This is a CREATE operation on STATIC assets.

    Args:
        path_name: Path name (e.g., "Tech-Loop")
        ordered_stop_ids: Ordered list of stop IDs [1, 3, 5] OR stop names ["Gavipuram", "Temple", "Peenya"]
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
            select(Path).where(Path.path_name == path_name)
        )
        if existing_path.scalar_one_or_none():
            return error_response(
                error=f"Path '{path_name}' already exists",
                message="Path with this name already exists"
            )

        # Resolve stop names to stop IDs if needed
        resolved_stop_ids = []
        not_found_stops = []

        for stop_identifier in ordered_stop_ids:
            if isinstance(stop_identifier, int):
                # It's already a stop ID, verify it exists
                stop_result = await db.execute(
                    select(Stop).where(Stop.stop_id == stop_identifier)
                )
                stop = stop_result.scalar_one_or_none()
                if not stop:
                    not_found_stops.append(f"ID {stop_identifier}")
                else:
                    resolved_stop_ids.append(stop_identifier)
            else:
                # It's a stop name (string), resolve to ID
                stop_name = str(stop_identifier).strip()
                stop_result = await db.execute(
                    select(Stop).where(Stop.name == stop_name)
                )
                stop = stop_result.scalar_one_or_none()
                if not stop:
                    not_found_stops.append(f"'{stop_name}'")
                else:
                    resolved_stop_ids.append(stop.stop_id)

        if not_found_stops:
            # Get available stop names for helpful error message
            all_stops_result = await db.execute(
                select(Stop.name).order_by(Stop.name)
            )
            available_stops = [row[0] for row in all_stops_result.fetchall()]

            return error_response(
                error=f"Stop(s) not found: {', '.join(not_found_stops)}",
                message=f"Could not find stops: {', '.join(not_found_stops)}. Available stops: {', '.join(available_stops[:10])}..."
            )

        # Create path with resolved stop IDs as JSON
        path = Path(
            path_name=path_name,
            ordered_stop_ids=json.dumps(resolved_stop_ids)
        )
        db.add(path)
        await db.commit()
        await db.refresh(path)

        # Get stop names for response
        stop_names = []
        for stop_id in resolved_stop_ids:
            stop_result = await db.execute(
                select(Stop).where(Stop.stop_id == stop_id)
            )
            stop = stop_result.scalar_one()
            stop_names.append(stop.name)

        return success_response(
            data={
                "path_id": path.path_id,
                "path_name": path.path_name,
                "stop_ids": resolved_stop_ids,
                "stop_names": stop_names,
                "stop_count": len(resolved_stop_ids)
            },
            message=f"Successfully created path '{path_name}' with {len(resolved_stop_ids)} stops: {', '.join(stop_names)}"
        )

    except Exception as e:
        await db.rollback()
        return error_response(
            error=str(e),
            message=f"Failed to create path '{path_name}'"
        )


async def create_route(
    path_name: str,
    shift_time: str,
    direction: str,
    start_point: str = None,
    end_point: str = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Create a new route by assigning a time to a path.

    This is a CREATE operation on STATIC assets.

    Args:
        path_name: The path name (str like "Path-1") or path ID (can be converted from str)
        shift_time: Time for this route (e.g., "19:45")
        direction: "LOGIN" or "LOGOUT"
        start_point: Starting location name (optional)
        end_point: Ending location name (optional)
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
            path_id=path.path_id,
            route_display_name=route_display_name,
            shift_time=shift_time,
            direction=direction,
            start_point=start_point or path.path_name,  # Default to path name if not provided
            end_point=end_point or path.path_name,  # Default to path name if not provided
            status="active"
        )
        db.add(route)
        await db.commit()
        await db.refresh(route)

        return success_response(
            data={
                "route_id": route.route_id,
                "route_display_name": route.route_display_name,
                "path_id": path.path_id,  # Use path.path_id instead of path_id variable
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
