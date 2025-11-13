from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Vehicle(Base):
    """Vehicle model - Transport assets"""

    __tablename__ = "vehicles"

    vehicle_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    license_plate = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)  # "Bus" or "Cab"
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
