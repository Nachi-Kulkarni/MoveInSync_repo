from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Path(Base):
    """Path model - Ordered sequences of stops"""

    __tablename__ = "paths"

    path_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    path_name = Column(String, nullable=False, unique=True)
    ordered_stop_ids = Column(Text, nullable=False)  # JSON array: "[1,2,3]"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
