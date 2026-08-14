import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.status_event import StatusEvent


class Application(Base):
    """SQLAlchemy ORM model representing a job application."""

    # 1. Primary Key
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # 2. Company & Role
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # 3. URLs & Job Description Text
    job_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    raw_posting_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 4. Source & Status (Categorical strings)
    source: Mapped[str] = mapped_column(String(64), default="other", index=True)
    current_status: Mapped[str] = mapped_column(String(64), default="APPLIED", index=True)

    # 5. Dates (Crucial for Survival / Response Analytics)
    date_applied: Mapped[date] = mapped_column(
        Date, nullable=False, default=lambda: datetime.now(timezone.utc).date(), index=True
    )
    date_first_response: Mapped[date | None] = mapped_column(Date, nullable=True)

    # 6. Salary, Location & Notes
    salary_range_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_range_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location_type: Mapped[str] = mapped_column(String(64), default="remote", index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 7. Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 8. Append-only Status History (Event Sourcing)
    events: Mapped[list["StatusEvent"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="StatusEvent.timestamp.asc()",
    )
