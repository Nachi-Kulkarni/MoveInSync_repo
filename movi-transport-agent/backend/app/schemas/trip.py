from pydantic import BaseModel
from typing import Optional
from datetime import date


class TripResponse(BaseModel):
    """Response schema for trip data"""

    trip_id: int
    route_id: int
    display_name: str
    booking_percentage: int
    live_status: Optional[str] = None
    trip_date: Optional[date] = None
    vehicle_license: Optional[str] = None
    driver_name: Optional[str] = None
    has_vehicle: bool = False

    class Config:
        from_attributes = True


class TripConsequence(BaseModel):
    """Response schema for trip consequence checks"""

    trip_id: int
    display_name: str
    has_bookings: bool
    booking_percentage: int
    has_deployment: bool
    risk_level: str  # "none", "low", "high"
    message: str

    class Config:
        from_attributes = True
