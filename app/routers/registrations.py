from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Event, Registration
from app.schemas import RegistrationResponse, RegistrationWithUser, MessageResponse
from app.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/registrations", tags=["Registrations"])


@router.post("/events/{event_id}/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register_for_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register current user for an event
    """
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if already registered
    existing_registration = db.query(Registration).filter(
        Registration.user_id == current_user.id,
        Registration.event_id == event_id
    ).first()
    
    if existing_registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already registered for this event"
        )
    
    # Check capacity
    if event.is_full:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is full"
        )
    
    # Create registration
    new_registration = Registration(
        user_id=current_user.id,
        event_id=event_id
    )
    
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)
    
    return MessageResponse(
        message="Successfully registered for event",
        detail=f"Registration ID: {new_registration.id}"
    )


@router.delete("/events/{event_id}/register", response_model=MessageResponse)
def unregister_from_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unregister current user from an event
    """
    # Find registration
    registration = db.query(Registration).filter(
        Registration.user_id == current_user.id,
        Registration.event_id == event_id
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )
    
    db.delete(registration)
    db.commit()
    
    return MessageResponse(
        message="Successfully unregistered from event",
        detail=f"Event ID: {event_id}"
    )


@router.get("/events/{event_id}/registrations", response_model=List[RegistrationWithUser])
def get_event_registrations(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all registrations for an event (admin or event creator only)
    """
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check permission (admin or event creator)
    if not current_user.is_admin and event.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view registrations for this event"
        )
    
    # Get registrations
    registrations = db.query(Registration).filter(
        Registration.event_id == event_id
    ).all()
    
    return registrations


@router.get("/my-registrations", response_model=List[RegistrationResponse])
def get_my_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all registrations for the current user
    """
    registrations = db.query(Registration).filter(
        Registration.user_id == current_user.id
    ).all()
    
    return registrations
