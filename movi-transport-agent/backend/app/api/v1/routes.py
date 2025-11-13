from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models.route import Route
from app.schemas.route import RouteResponse

router = APIRouter()


@router.get("/routes", response_model=list[RouteResponse])
async def list_routes(db: AsyncSession = Depends(get_db)):
    """List all routes"""
    result = await db.execute(select(Route))
    routes = result.scalars().all()
    return routes
