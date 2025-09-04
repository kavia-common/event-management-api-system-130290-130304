"""
SQLAlchemy models for the application entities: Event, Attendee.
"""

from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .core.database import Base


class Event(Base):
    """Event model with basic scheduling fields."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    # No users table: store a neutral owner identifier (0 by default)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    attendees: Mapped[list["Attendee"]] = relationship(
        "Attendee",
        back_populates="event",
        cascade="all, delete-orphan",
    )


class Attendee(Base):
    """Attendee model; one attendee per email per event."""

    __tablename__ = "attendees"
    __table_args__ = (
        UniqueConstraint("event_id", "email", name="uq_attendee_event_email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    event: Mapped["Event"] = relationship("Event", back_populates="attendees")
