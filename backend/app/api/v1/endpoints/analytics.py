from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/", response_model=AnalyticsResponse)
async def analytics_get_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await AnalyticsService.analytics_computes_metrics(
            db, user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))