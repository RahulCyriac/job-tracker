import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.schemas.status_event import StatusEventCreate
from app.services.application import ApplicationService

router = APIRouter()


@router.post("/", response_model=ApplicationResponse, status_code=201)
async def application_create(
    app_in: ApplicationCreate, db: AsyncSession = Depends(get_db)
):
    try:
        return await ApplicationService.create(db, app_in=app_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[ApplicationResponse])
async def application_get_all(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    source: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await ApplicationService.get_multi(
            db, skip=skip, limit=limit, status=status, source=source
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=ApplicationResponse)
async def application_get(
    id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    application = await ApplicationService.get(db, application_id=id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.patch("/{id}/status", response_model=ApplicationResponse)
async def application_update_status(
    id: uuid.UUID,
    status_in: StatusEventCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await ApplicationService.update_status(
            db, application_id=id, status_in=status_in
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", status_code=204)
async def application_delete(
    id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    deleted = await ApplicationService.delete(db, application_id=id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
    return None


@router.post("/detect-ghosted", response_model=list[ApplicationResponse])
async def application_detect_ghosted(
    db: AsyncSession = Depends(get_db),
    days_threshold: int = 14,
):
    try:
        return await ApplicationService.detect_and_mark_ghosted(
            db, days_threshold=days_threshold
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
