import statistics
import uuid

from app.schemas.analytics import AnalyticsResponse, FunnelMetric, SourceMetric
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.application import Application
from sqlalchemy import select


class AnalyticsService:
    @staticmethod
    async def analytics_computes_metrics(
        db: AsyncSession,
        *,
        user_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 0,
    ) -> AnalyticsResponse:
        stmt = select(Application)
        if user_id is not None:
            stmt = stmt.where(Application.user_id == user_id)

        result = await db.scalars(stmt)
        apps = result.all()

        if not apps:
            return AnalyticsResponse(
                total_applications=0,
                ghosted_count=0,
                active_count=0,
                responded_count=0,
                median_response_time_days=None,
                sources={},
                funnel=FunnelMetric(
                    applied=0,
                    screening=0,
                    interviewing=0,
                    offer=0,
                    rejected=0,
                    ghosted=0,
                ),
            )

        count_total = len(apps)
        count_ghost, count_responded, count_active = 0, 0, 0
        median_list = []
        sources_dict = {}
        unique_sources = set(app.source or "other" for app in apps)

        for src in unique_sources:
            src_apps = [a for a in apps if (a.source or "other") == src]
            number_of_src_apps = len(src_apps)
            responded_src_apps = sum(
                1
                for a in apps
                if (a.source or "other") == src and a.date_first_response is not None
            )
            sources_dict[src] = SourceMetric(
                total=number_of_src_apps,
                responded=responded_src_apps,
                response_rate_pct=responded_src_apps / number_of_src_apps * 100,
            )

        for app in apps:
            if app.current_status == "GHOSTED":
                count_ghost += 1
            if app.current_status == "APPLIED":
                count_active += 1
            if app.date_first_response is not None:
                count_responded += 1
                median = (app.date_first_response - app.date_applied).days
                median_list.append(median)

        median_respone_time_days = (
            float(statistics.median(median_list)) if median_list else None
        )

        funnel_dict = {
            "applied": sum(1 for a in apps if a.current_status == "APPLIED"),
            "screening": sum(1 for a in apps if a.current_status == "SCREENING"),
            "interviewing": sum(
                1 for a in apps if a.current_status == "INTERVIEWING"
            ),
            "offer": sum(1 for a in apps if a.current_status == "OFFER"),
            "rejected": sum(1 for a in apps if a.current_status == "REJECTED"),
            "ghosted": sum(1 for a in apps if a.current_status == "GHOSTED"),
        }

        return AnalyticsResponse(
            total_applications=count_total,
            ghosted_count=count_ghost,
            active_count=count_active,
            responded_count=count_responded,
            median_response_time_days=median_respone_time_days,
            sources=sources_dict,
            funnel=FunnelMetric(**funnel_dict),
        )