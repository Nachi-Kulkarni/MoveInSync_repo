from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class DailyTrip(Base):
    """DailyTrip model - Daily instances of routes (dynamic operations)"""

    __tablename__ = "daily_trips"

    trip_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey("routes.route_id"), nullable=False)
    display_name = Column(String, nullable=False)  # e.g., "Bulk - 00:01"
    booking_percentage = Column(Integer, default=0)  # 0-100
    live_status = Column(String)  # e.g., "00:01 IN", "COMPLETED"
    trip_date = Column(Date, server_default=func.date())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
