from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Event
from app.schemas import EventCreate, EventResponse, MessageResponse
from app.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new event (admin only)
    """
    # Validate end_time if provided
    if event_data.end_time and event_data.end_time <= event_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Create event
    new_event = Event(
        title=event_data.title,
        description=event_data.description,
        venue=event_data.venue,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        capacity=event_data.capacity,
        created_by=current_user.id
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return MessageResponse(
        message="Event created successfully",
        detail=f"Event ID: {new_event.id}"
    )


@router.get("", response_model=List[EventResponse])
def list_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all events
    """
    events = db.query(Event).order_by(Event.start_time).offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific event by ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event


@router.delete("/{event_id}", response_model=MessageResponse)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete an event (admin only)
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(event)
    db.commit()
    
    return MessageResponse(
        message="Event deleted successfully",
        detail=f"Event ID: {event_id}"
    )
