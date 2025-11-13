from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Route(Base):
    """Route model - Path + Time combinations (static assets)"""

    __tablename__ = "routes"

    route_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    path_id = Column(Integer, ForeignKey("paths.path_id"), nullable=False)
    route_display_name = Column(String, nullable=False)  # e.g., "Path2 - 19:45"
    shift_time = Column(String, nullable=False)  # e.g., "19:45"
    direction = Column(String, nullable=False)  # "LOGIN" or "LOGOUT"
    start_point = Column(String, nullable=False)
    end_point = Column(String, nullable=False)
    status = Column(String, default="active")  # "active" or "deactivated"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
