from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models.stop import Stop
from app.schemas.route import StopResponse

router = APIRouter()


@router.get("/stops", response_model=list[StopResponse])
async def list_stops(db: AsyncSession = Depends(get_db)):
    """List all stops"""
    result = await db.execute(select(Stop))
    stops = result.scalars().all()
    return stops
