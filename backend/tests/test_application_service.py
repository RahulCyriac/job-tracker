from datetime import date, datetime, timezone, timedelta
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.application import ApplicationCreate
from app.schemas.status_event import StatusEventCreate
from app.services.application import ApplicationService

@pytest.mark.asyncio
async def test_create_application_creates_initial_event(
    db_session: AsyncSession,
):
  app_in = ApplicationCreate(
      company_name="Google",
      role_title="Backend Engineer",
      location_type="remote",
  )

  # 1. Execute Service
  application = await ApplicationService.create(db_session, app_in=app_in)

  # 2. Assert Invariants
  assert application.id is not None
  assert application.company_name == "Google"
  assert application.current_status == "APPLIED"
  assert len(application.events) == 1
  assert application.events[0].from_status is None
  assert application.events[0].to_status == "APPLIED"


@pytest.mark.asyncio
async def test_update_status_appends_event_and_records_first_response(
    db_session: AsyncSession,
):
  app_in = ApplicationCreate(
      company_name="Stripe",
      role_title="Systems Engineer",
  )

  # 1. Create Application
  application = await ApplicationService.create(db_session, app_in=app_in)
  assert application.date_first_response is None

  # 2. Update Status to INTERVIEWING
  status_in = StatusEventCreate(
      to_status="INTERVIEWING", note="Passed initial screening"
  )
  updated_app = await ApplicationService.update_status(
      db_session, application_id=application.id, status_in=status_in
  )

  # 3. Assert Survival Analytics Invariants
  assert updated_app.current_status == "INTERVIEWING"
  assert updated_app.date_first_response == datetime.now(timezone.utc).date()
  assert len(updated_app.events) == 2
  assert updated_app.events[1].from_status == "APPLIED"
  assert updated_app.events[1].to_status == "INTERVIEWING"
  assert updated_app.events[1].note == "Passed initial screening"

@pytest.mark.asyncio
async def test_detect_and_mark_ghosted_applications(db_session: AsyncSession):
  today = datetime.now(timezone.utc).date()
  # 1. Create a recent application (3 days ago - should NOT be ghosted)
  recent_app = await ApplicationService.create(
      db_session,
      app_in=ApplicationCreate(
          company_name="Recent Corp",
          role_title="Backend Dev",
          date_applied=today - timedelta(days=3),
      ),
  )
  # 2. Create an old application (20 days ago - SHOULD be ghosted)
  old_app = await ApplicationService.create(
      db_session,
      app_in=ApplicationCreate(
          company_name="Ghost Corp",
          role_title="SDE 1",
          date_applied=today - timedelta(days=20),
      ),
  )
  # 3. Execute Ghost Detection Service (14-day threshold)
  ghosted_apps = await ApplicationService.detect_and_mark_ghosted(
      db_session, days_threshold=14
  )
  # 4. Assert Invariants
  assert len(ghosted_apps) == 1
  assert ghosted_apps[0].id == old_app.id
  assert ghosted_apps[0].current_status == "GHOSTED"
  assert ghosted_apps[0].date_first_response is None
  assert len(ghosted_apps[0].events) == 2
  assert ghosted_apps[0].events[1].from_status == "APPLIED"
  assert ghosted_apps[0].events[1].to_status == "GHOSTED"