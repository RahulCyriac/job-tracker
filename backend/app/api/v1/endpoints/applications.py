import fastapi
from fastapi import APIRouter, Depends, HTTPException
from app.services.application import ApplicationService
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.schemas.status_event import StatusEventCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
import uuid

router = fastapi.APIRouter()


@router.post("/", response_model=ApplicationResponse)
async def application_create(
    app_in: ApplicationCreate, db: AsyncSession = Depends(get_db)
):
    try:
        application = await ApplicationService.create(db, app_in=app_in)
        return application
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[ApplicationResponse])
async def application_get_all(skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    source: str | None = None,
    db: AsyncSession = Depends(get_db),): 
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
        application = await ApplicationService.update_status(
            db, application_id=id, status_in=status_in
        )
        return application
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.delete("/{id}", response_model=ApplicationResponse)
async def application_delete(
    id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    
    application = await ApplicationService.delete(db, application_id=id)
    if not application:
        raise HTTPException(status_code=204, detail="Application not found")
    return application