from datetime import date, datetime
import uuid
from pydantic import BaseModel, ConfigDict

from app.schemas.status_event import StatusEventResponse


# 1. Incoming payload schema for creating an application
class ApplicationCreate(BaseModel):
    company_name: str
    role_title: str
    job_url: str | None = None
    raw_posting_text: str | None = None
    source: str = "other"
    date_applied: date | None = None
    salary_range_min: int | None = None
    salary_range_max: int | None = None
    location_type: str = "remote"
    notes: str | None = None


# 2. Outgoing response schema returned to the frontend / client
class ApplicationResponse(BaseModel):
    id: uuid.UUID
    company_name: str
    role_title: str
    job_url: str | None = None
    raw_posting_text: str | None = None
    source: str
    current_status: str
    date_applied: date
    date_first_response: date | None = None
    salary_range_min: int | None = None
    salary_range_max: int | None = None
    location_type: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    events: list[StatusEventResponse] = []

    model_config = ConfigDict(from_attributes=True)