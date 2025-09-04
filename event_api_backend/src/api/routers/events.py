"""
Event routes: CRUD for events with validation and business rules.

Business rules:
- end_time must be after start_time
- capacity must be >= number of existing attendees on update
- only event owner can update/delete
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.database import get_db
from ..models import Event, Attendee
from ..schemas import EventCreate, EventOut, EventUpdate, PaginatedEvents
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/events", tags=["Events"])


def _validate_event_times(start_time: datetime, end_time: datetime):
    if end_time <= start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")


@router.post(
    "",
    response_model=EventOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create event",
    description="Create a new event owned by the authenticated user.",
)
# PUBLIC_INTERFACE
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new event after validating time range."""
    _validate_event_times(payload.start_time, payload.end_time)
    event = Event(
        title=payload.title,
        description=payload.description,
        location=payload.location,
        start_time=payload.start_time,
        end_time=payload.end_time,
        capacity=payload.capacity,
        owner_id=current_user.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get(
    "",
    response_model=PaginatedEvents,
    summary="List events",
    description="List events with pagination and optional text search on title.",
)
# PUBLIC_INTERFACE
def list_events(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(default=None, description="Search query for title"),
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=20, ge=1, le=100, description="Pagination limit"),
):
    """Return paginated events, optionally filtered by title search."""
    query = db.query(Event)
    if q:
        query = query.filter(Event.title.ilike(f"%{q}%"))
    total = query.count()
    items = (
        query.order_by(Event.start_time.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return PaginatedEvents(total=total, items=items)


@router.get(
    "/{event_id}",
    response_model=EventOut,
    summary="Get event by id",
    description="Retrieve an event by its identifier.",
    responses={404: {"description": "Event not found"}},
)
# PUBLIC_INTERFACE
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get a single event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch(
    "/{event_id}",
    response_model=EventOut,
    summary="Update event",
    description="Update fields of an event. Only the owner can update.",
    responses={403: {"description": "Forbidden"}, 404: {"description": "Event not found"}},
)
# PUBLIC_INTERFACE
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an event, enforcing time and capacity rules and ownership."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to modify this event",
        )

    # Validate times if both provided or one provided (use existing for comparison)
    start_time = payload.start_time or event.start_time
    end_time = payload.end_time or event.end_time
    _validate_event_times(start_time, end_time)

    # Validate capacity cannot be less than current attendees
    if payload.capacity is not None:
        attendee_count = (
            db.query(func.count(Attendee.id))
            .filter(Attendee.event_id == event.id)
            .scalar()
            or 0
        )
        if payload.capacity < attendee_count:
            raise HTTPException(
                status_code=400,
                detail=(
                    "capacity cannot be less than current attendee count "
                    f"({attendee_count})"
                ),
            )

    # Apply updates
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete event",
    description="Delete an event. Only the owner can delete.",
    responses={403: {"description": "Forbidden"}, 404: {"description": "Event not found"}},
)
# PUBLIC_INTERFACE
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an event and its attendees (cascade)."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this event",
        )

    db.delete(event)
    db.commit()
    return None
