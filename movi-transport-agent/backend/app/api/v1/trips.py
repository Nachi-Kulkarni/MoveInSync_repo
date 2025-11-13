from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models.daily_trip import DailyTrip
from app.models.deployment import Deployment
from app.schemas.trip import TripResponse, TripConsequence

router = APIRouter()


@router.get("/trips", response_model=list[TripResponse])
async def list_trips(db: AsyncSession = Depends(get_db)):
    """List all daily trips"""
    result = await db.execute(select(DailyTrip))
    trips = result.scalars().all()
    return trips


@router.get("/trips/{trip_id}/consequences", response_model=TripConsequence)
async def get_trip_consequences(trip_id: int, db: AsyncSession = Depends(get_db)):
    """Check consequences of actions on a trip (for tribal knowledge flow)"""

    # Get trip details
    result = await db.execute(select(DailyTrip).where(DailyTrip.trip_id == trip_id))
    trip = result.scalar_one_or_none()

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Check if trip has deployment
    deployment_result = await db.execute(
        select(Deployment).where(Deployment.trip_id == trip_id)
    )
    deployment = deployment_result.scalar_one_or_none()

    has_deployment = deployment is not None
    has_bookings = trip.booking_percentage > 0

    # Determine risk level
    if has_deployment and has_bookings:
        risk_level = "high"
        message = f"Trip is {trip.booking_percentage}% booked. Removing vehicle will cancel bookings and break trip-sheet generation."
    elif has_deployment and not has_bookings:
        risk_level = "low"
        message = "Trip has vehicle assigned but no bookings yet. Safe to modify."
    else:
        risk_level = "none"
        message = "No consequences. Trip has no vehicle or bookings."

    return TripConsequence(
        trip_id=trip.trip_id,
        display_name=trip.display_name,
        has_bookings=has_bookings,
        booking_percentage=trip.booking_percentage,
        has_deployment=has_deployment,
        risk_level=risk_level,
        message=message,
    )
