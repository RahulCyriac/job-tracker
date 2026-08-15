from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict


# 1. Incoming payload schema when changing an application status
class StatusEventCreate(BaseModel):
    to_status: str
    note: str | None = None


# 2. Outgoing response schema matching exact StatusEvent model field order
class StatusEventResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    from_status: str | None = None
    to_status: str
    timestamp: datetime
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)