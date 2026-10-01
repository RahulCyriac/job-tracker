from app.db.base_class import Base
import uuid
from datetime import datetime, timezone
from sqlalchemy import Date, DateTime, Integer, String , Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from app.models.application import Application

class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4) 
    email:Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password:Mapped[str] = mapped_column(String(255), nullable=False)
    is_active:Mapped[bool]= mapped_column (Boolean, default=True)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),
      default=lambda: datetime.now(timezone.utc),)
    updated_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),
      default=lambda: datetime.now(timezone.utc),
      onupdate=lambda: datetime.now(timezone.utc),)
    applications: Mapped[list["Application"]] = relationship(
    back_populates="user", cascade="all, delete-orphan")