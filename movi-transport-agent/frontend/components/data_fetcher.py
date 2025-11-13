"""
Data fetcher module for fetching data from backend API.
Handles async HTTP requests to FastAPI backend.
"""

import httpx
import pandas as pd
from typing import List, Dict, Optional, Any
import os


# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"


async def fetch_trips() -> pd.DataFrame:
    """
    Fetch all trips from backend API.

    Returns:
        DataFrame with columns: Trip Name, Booking %, Live Status
        Returns empty DataFrame on error
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE}/trips")
            response.raise_for_status()
            data = response.json()

            # Transform data for display
            trips_data = []
            for trip in data:
                trips_data.append({
                    "Trip Name": trip.get("display_name", "Unknown"),
                    "Booking %": f"{trip.get('booking_percentage', 0)}%",
                    "Live Status": trip.get("live_status", "N/A")
                })

            return pd.DataFrame(trips_data)

    except Exception as e:
        print(f"Error fetching trips: {e}")
        return pd.DataFrame(columns=["Trip Name", "Booking %", "Live Status"])


async def fetch_routes() -> pd.DataFrame:
    """
    Fetch all routes from backend API.

    Returns:
        DataFrame with columns: Route ID, Route Name, Direction, Shift Time,
        Start Point, End Point, Capacity, Status
        Returns empty DataFrame on error
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE}/routes")
            response.raise_for_status()
            data = response.json()

            # Transform data for display
            routes_data = []
            for route in data:
                routes_data.append({
                    "Route ID": route.get("route_id", "N/A"),
                    "Route Name": route.get("route_display_name", "Unknown"),
                    "Direction": route.get("direction", "N/A"),
                    "Shift Time": route.get("shift_time", "N/A"),
                    "Start Point": route.get("start_point", "N/A"),
                    "End Point": route.get("end_point", "N/A"),
                    "Status": route.get("status", "N/A")
                })

            return pd.DataFrame(routes_data)

    except Exception as e:
        print(f"Error fetching routes: {e}")
        return pd.DataFrame(columns=[
            "Route ID", "Route Name", "Direction", "Shift Time",
            "Start Point", "End Point", "Status"
        ])


async def fetch_stops() -> List[Dict[str, Any]]:
    """
    Fetch all stops from backend API.

    Returns:
        List of stop dictionaries with name, latitude, longitude
        Returns empty list on error
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE}/stops")
            response.raise_for_status()
            data = response.json()

            return data

    except Exception as e:
        print(f"Error fetching stops: {e}")
        return []


def fetch_trips_sync() -> pd.DataFrame:
    """
    Synchronous wrapper for fetch_trips.
    Used by Gradio components.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(fetch_trips())


def fetch_routes_sync() -> pd.DataFrame:
    """
    Synchronous wrapper for fetch_routes.
    Used by Gradio components.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(fetch_routes())


def fetch_stops_sync() -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for fetch_stops.
    Used by Gradio components.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(fetch_stops())
