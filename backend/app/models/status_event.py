import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.application import Application


class StatusEvent(Base):
    """SQLAlchemy ORM model representing an immutable, append-only status change event."""

    # 1. Primary Key
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # 2. Foreign Key pointing to parent Application
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("application.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 3. Status Transition States
    from_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    to_status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # 4. Timestamp (Crucial for time-in-stage duration & funnel analytics)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # 5. Optional notes for this status event
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 6. Bi-directional link back to Application
    application: Mapped["Application"] = relationship(back_populates="events")