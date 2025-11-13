from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Deployment(Base):
    """Deployment model - Vehicle-Driver assignments to trips"""

    __tablename__ = "deployments"

    deployment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(Integer, ForeignKey("daily_trips.trip_id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.vehicle_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=False)
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())


