from datetime import datetime, timezone,timedelta
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.application import Application
from app.models.status_event import StatusEvent
from app.schemas.application import ApplicationCreate
from app.schemas.status_event import StatusEventCreate


class ApplicationService:

    @staticmethod
    async def create(db: AsyncSession, *, app_in: ApplicationCreate) -> Application:
        app_data = app_in.model_dump(exclude_unset=True)
        application = Application(**app_data)

        # Invariant 1: Append initial StatusEvent
        initial_event = StatusEvent(from_status=None, to_status="APPLIED")
        application.events.append(initial_event)

        db.add(application)
        await db.commit()
        await db.refresh(application, attribute_names=["events"])
        return application

    @staticmethod
    async def update_status(
        db: AsyncSession,
        *,
        application_id: uuid.UUID,
        status_in: StatusEventCreate,
    ) -> Application:
        # Query application with loaded events
        stmt = (
            select(Application)
            .where(Application.id == application_id)
            .options(selectinload(Application.events))
        )
        application = await db.scalar(stmt)
        if not application:
            raise ValueError(f"Application {application_id} not found")

        old_status = application.current_status
        application.current_status = status_in.to_status

        # Invariant 2: Auto-record first response date
        if (
            application.date_first_response is None
            and status_in.to_status != "APPLIED"
        ):
            application.date_first_response = datetime.now(timezone.utc).date()

        # Append new event
        new_event = StatusEvent(
            from_status=old_status,
            to_status=status_in.to_status,
            note=status_in.note,
        )
        application.events.append(new_event)

        await db.commit()
        await db.refresh(application, attribute_names=["events"])
        return application




    @staticmethod
    async def get(
            db: AsyncSession, *, application_id: uuid.UUID
        ) -> Application | None:
        stmt = (
            select(Application)
            .where(Application.id == application_id)
            .options(selectinload(Application.events))
        )
        return await db.scalar(stmt)

    @staticmethod
    async def get_multi(
            db: AsyncSession,
            *,
            skip: int = 0,
            limit: int = 100,
            status: str | None = None,
            source: str | None = None,
        ) -> list[Application]:
        stmt = (
            select(Application)
            .options(selectinload(Application.events))
            .order_by(Application.created_at.desc())
        )

        if status:
            stmt = stmt.where(Application.current_status == status)
        if source:
            stmt = stmt.where(Application.source == source)

        stmt = stmt.offset(skip).limit(limit)
        result = await db.scalars(stmt)
        return list(result.all())

    @staticmethod
    async def delete(db: AsyncSession, *, application_id: uuid.UUID) -> bool:
        stmt = select(Application).where(Application.id == application_id)
        application = await db.scalar(stmt)
        if not application:
            return False
        await db.delete(application)
        await db.commit()
        return True

    @staticmethod
    async def detect_and_mark_ghosted(db: AsyncSession,days_threshold: int = 14):
        today = datetime.now(timezone.utc).date()
        cutoff_date = today - timedelta(days=days_threshold)
        stmt = (select(Application)
                .where(Application.date_applied<=cutoff_date , Application.current_status == "APPLIED").options(selectinload(Application.events)))
        result = await db.scalars(stmt)
        apps_to_ghost = result.all()
        for i in apps_to_ghost:
                i.current_status="GHOSTED"
                new_event = StatusEvent(from_status = "APPLIED", to_status = "GHOSTED",note = f"Auto-detected as ghosted after {days_threshold} days of inactivity")
                i.events.append(new_event)
        
        
        await db.commit()
        return apps_to_ghost