from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api.deps import get_db
from app.models.vehicle import Vehicle
from app.models.deployment import Deployment

router = APIRouter()


@router.get("/vehicles/unassigned")
async def get_unassigned_vehicles_count(db: AsyncSession = Depends(get_db)):
    """Get count of vehicles not assigned to any trip"""

    # Subquery to get all assigned vehicle IDs
    assigned_vehicle_ids_subquery = select(Deployment.vehicle_id).distinct().subquery()

    # Count vehicles NOT IN assigned list
    result = await db.execute(
        select(func.count(Vehicle.vehicle_id)).where(
            Vehicle.vehicle_id.not_in(select(assigned_vehicle_ids_subquery))
        )
    )
    count = result.scalar()

    return {"unassigned_count": count}
