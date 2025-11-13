from fastapi import APIRouter
from app.api.v1 import trips, routes, stops, vehicles, agent

api_router = APIRouter()

# Include all routers
api_router.include_router(trips.router, tags=["trips"])
api_router.include_router(routes.router, tags=["routes"])
api_router.include_router(stops.router, tags=["stops"])
api_router.include_router(vehicles.router, tags=["vehicles"])
api_router.include_router(agent.router, tags=["agent"])  # TICKET #7: Agent endpoints
