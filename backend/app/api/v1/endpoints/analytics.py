

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics import AnalyticsService

router = APIRouter()
@router.get("/",response_model=AnalyticsResponse)
async def analytics_get_all(
    db:AsyncSession = Depends(get_db)
):
    try:
        return await AnalyticsService.analytics_computes_metrics(db)
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e)) 