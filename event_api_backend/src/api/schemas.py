"""
Pydantic schemas for request and response bodies.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator


# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


# PUBLIC_INTERFACE
class UserBase(BaseModel):
    """Base user fields."""
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(default=None, description="Full name of the user")


class UserCreate(UserBase):
    """Request schema for user registration."""
    password: str = Field(..., min_length=8, description="Strong password")


class UserLogin(BaseModel):
    """Request schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class UserOut(UserBase):
    """Response schema for user data."""
    id: int = Field(..., description="User identifier")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# Event schemas
# PUBLIC_INTERFACE
class EventBase(BaseModel):
    """Common event fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Event title")
    description: Optional[str] = Field(default=None, description="Event description")
    location: Optional[str] = Field(default=None, description="Event location")
    start_time: datetime = Field(..., description="Event start date-time (UTC)")
    end_time: datetime = Field(..., description="Event end date-time (UTC)")
    capacity: int = Field(default=100, ge=1, le=100000, description="Maximum attendees count")

    @field_validator("end_time")
    @classmethod
    def check_end_after_start(cls, v, info):
        # Cross-field validation will happen in routers where we have both values
        return v


class EventCreate(EventBase):
    """Request schema to create a new event."""
    pass


class EventUpdate(BaseModel):
    """Request schema to update event fields."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    capacity: Optional[int] = Field(default=None, ge=1, le=100000)


class EventOut(EventBase):
    """Response schema for event data."""
    id: int = Field(..., description="Event identifier")
    owner_id: int = Field(..., description="User id of the creator")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# Attendee schemas
# PUBLIC_INTERFACE
class AttendeeBase(BaseModel):
    """Common attendee fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Attendee name")
    email: EmailStr = Field(..., description="Attendee email")


class AttendeeCreate(AttendeeBase):
    """Request schema to register an attendee for an event."""
    pass


class AttendeeOut(AttendeeBase):
    """Response schema for attendee data."""
    id: int = Field(..., description="Attendee identifier")
    event_id: int = Field(..., description="Event identifier the attendee registered for")
    registered_at: datetime = Field(..., description="Registration timestamp")

    class Config:
        from_attributes = True


# Pagination helpers
# PUBLIC_INTERFACE
class PaginatedEvents(BaseModel):
    """Paginated response for events."""
    total: int = Field(..., description="Total number of events")
    items: List[EventOut] = Field(..., description="List of events for current page")


# PUBLIC_INTERFACE
class PaginatedAttendees(BaseModel):
    """Paginated response for attendees."""
    total: int = Field(..., description="Total number of attendees for the event")
    items: List[AttendeeOut] = Field(..., description="List of attendees for current page")
