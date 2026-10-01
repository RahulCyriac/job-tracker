import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.schemas.status_event import StatusEventCreate
from app.services.application import ApplicationService
from app.schemas.job_parser import JobParseRequest, JobParseResponse
from app.services.job_parser import JobParserService

router = APIRouter()


@router.post("/", response_model=ApplicationResponse, status_code=201)
async def application_create(
    app_in: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await ApplicationService.create(
            db, app_in=app_in, user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[ApplicationResponse])
async def application_get_all(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    source: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await ApplicationService.get_multi(
            db,
            skip=skip,
            limit=limit,
            status=status,
            source=source,
            user_id=current_user.id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=ApplicationResponse)
async def application_get(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = await ApplicationService.get(
        db, application_id=id, user_id=current_user.id
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.patch("/{id}/status", response_model=ApplicationResponse)
async def application_update_status(
    id: uuid.UUID,
    status_in: StatusEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await ApplicationService.update_status(
            db,
            application_id=id,
            status_in=status_in,
            user_id=current_user.id,
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", status_code=204)
async def application_delete(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await ApplicationService.delete(
        db, application_id=id, user_id=current_user.id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
    return None


@router.post("/detect-ghosted", response_model=list[ApplicationResponse])
async def application_detect_ghosted(
    db: AsyncSession = Depends(get_db),
    days_threshold: int = 14,
    current_user: User = Depends(get_current_user),
):
    try:
        return await ApplicationService.detect_and_mark_ghosted(
            db, days_threshold=days_threshold, user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/parse-job", response_model=JobParseResponse)
async def parse(
    req: JobParseRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        return await JobParserService.parse(text=req.text, url=req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
