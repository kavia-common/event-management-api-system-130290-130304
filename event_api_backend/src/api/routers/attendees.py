"""
Attendee routes: manage attendees per event.

Business rules:
- Each attendee email can register only once per event
- Event capacity cannot be exceeded
- Only the event owner can remove attendees
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.database import get_db
from ..models import Event, Attendee
from ..schemas import AttendeeCreate, AttendeeOut, PaginatedAttendees
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/events/{event_id}/attendees", tags=["Attendees"])


def _get_event_or_404(db: Session, event_id: int) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post(
    "",
    response_model=AttendeeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register attendee",
    description=(
        "Register a new attendee to an event. Enforces unique email per event and capacity."
    ),
    responses={400: {"description": "Capacity full or duplicate registration"}},
)
# PUBLIC_INTERFACE
def add_attendee(
    event_id: int,
    payload: AttendeeCreate,
    db: Session = Depends(get_db),
):
    """Register a new attendee to an event, enforcing capacity and uniqueness."""
    event = _get_event_or_404(db, event_id)

    # Enforce capacity
    count = (
        db.query(func.count(Attendee.id))
        .filter(Attendee.event_id == event.id)
        .scalar()
        or 0
    )
    if count >= event.capacity:
        raise HTTPException(status_code=400, detail="Event capacity reached")

    # Enforce uniqueness
    dup = (
        db.query(Attendee)
        .filter(Attendee.event_id == event.id, Attendee.email == payload.email)
        .first()
    )
    if dup:
        raise HTTPException(
            status_code=400,
            detail="Attendee already registered for this event",
        )

    attendee = Attendee(event_id=event.id, name=payload.name, email=payload.email)
    db.add(attendee)
    db.commit()
    db.refresh(attendee)
    return attendee


@router.get(
    "",
    response_model=PaginatedAttendees,
    summary="List attendees",
    description="List attendees for the specified event with pagination.",
)
# PUBLIC_INTERFACE
def list_attendees(
    event_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Return paginated attendees for an event."""
    _get_event_or_404(db, event_id)
    query = db.query(Attendee).filter(Attendee.event_id == event_id)
    total = query.count()
    items = (
        query.order_by(Attendee.registered_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return PaginatedAttendees(total=total, items=items)


@router.delete(
    "/{attendee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove attendee",
    description="Remove an attendee from the event. Only the event owner can remove.",
    responses={403: {"description": "Forbidden"}, 404: {"description": "Not found"}},
)
# PUBLIC_INTERFACE
def remove_attendee(
    event_id: int,
    attendee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove an attendee from event; only owner of the event can remove."""
    event = _get_event_or_404(db, event_id)
    if event.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to modify attendees for this event",
        )

    attendee = (
        db.query(Attendee)
        .filter(Attendee.id == attendee_id, Attendee.event_id == event_id)
        .first()
    )
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    db.delete(attendee)
    db.commit()
    return None
