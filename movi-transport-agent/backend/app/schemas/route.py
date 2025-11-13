from pydantic import BaseModel


class RouteResponse(BaseModel):
    """Response schema for route data"""

    route_id: int
    path_id: int
    route_display_name: str
    shift_time: str
    direction: str
    start_point: str
    end_point: str
    status: str

    class Config:
        from_attributes = True


class StopResponse(BaseModel):
    """Response schema for stop data"""

    stop_id: int
    name: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
