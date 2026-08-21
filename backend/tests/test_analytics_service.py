from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.application import ApplicationCreate
from app.schemas.status_event import StatusEventCreate
from app.services.analytics import AnalyticsService
from app.services.application import ApplicationService


@pytest.mark.asyncio
async def test_analytics_empty_database(db_session: AsyncSession):
    analytics = await AnalyticsService.analytics_computes_metrics(db_session)
    assert analytics.total_applications == 0
    assert analytics.median_response_time_days is None
    assert analytics.ghosted_count == 0
    assert analytics.sources == {}
    assert analytics.funnel.applied == 0


@pytest.mark.asyncio
async def test_analytics_computes_metrics(db_session: AsyncSession):
    today = datetime.now(timezone.utc).date()

    # App 1: Google (source=referral, applied 10 days ago, responded 6 days ago -> 4 days response time)
    app1 = await ApplicationService.create(
        db_session,
        app_in=ApplicationCreate(
            company_name="Google",
            role_title="Backend Engineer",
            location_type="remote",
            source="referral",
            date_applied=today - timedelta(days=10),
        ),
    )
    await ApplicationService.update_status(
        db_session,
        application_id=app1.id,
        status_in=StatusEventCreate(to_status="INTERVIEWING", note="Passed initial screening"),
    )
    # Explicitly set historical date_first_response for exact test scenario
    app1.date_first_response = today - timedelta(days=6)
    await db_session.commit()

    # App 2: Netflix (source=linkedin, applied 15 days ago, responded 5 days ago -> 10 days response time)
    app2 = await ApplicationService.create(
        db_session,
        app_in=ApplicationCreate(
            company_name="Netflix",
            role_title="Senior Platform Engineer",
            location_type="remote",
            source="linkedin",
            date_applied=today - timedelta(days=15),
        ),
    )
    await ApplicationService.update_status(
        db_session,
        application_id=app2.id,
        status_in=StatusEventCreate(to_status="SCREENING", note="Recruiter call scheduled"),
    )
    app2.date_first_response = today - timedelta(days=5)
    await db_session.commit()

    # App 3: Stripe (source=linkedin, applied 20 days ago, ghosted -> response time is None)
    app3 = await ApplicationService.create(
        db_session,
        app_in=ApplicationCreate(
            company_name="Stripe",
            role_title="Infrastructure Engineer",
            location_type="remote",
            source="linkedin",
            date_applied=today - timedelta(days=20),
        ),
    )
    await ApplicationService.update_status(
        db_session,
        application_id=app3.id,
        status_in=StatusEventCreate(to_status="GHOSTED", note="No response after 14 days"),
    )
    # Ensure ghosted application has date_first_response as None
    app3.date_first_response = None
    await db_session.commit()

    # Run Analytics Service
    analytics = await AnalyticsService.analytics_computes_metrics(db_session)

    # Assert Invariants matching our predictions!
    assert analytics.total_applications == 3
    assert analytics.ghosted_count == 1
    assert analytics.responded_count == 2
    assert analytics.active_count == 0
    assert analytics.median_response_time_days == 7.0
    assert analytics.sources["linkedin"].total == 2
    assert analytics.sources["linkedin"].responded == 1
    assert analytics.sources["linkedin"].response_rate_pct == 50.0
    assert analytics.sources["referral"].total == 1
    assert analytics.sources["referral"].responded == 1
    assert analytics.sources["referral"].response_rate_pct == 100.0
    assert analytics.funnel.interviewing == 1
    assert analytics.funnel.screening == 1
    assert analytics.funnel.ghosted == 1