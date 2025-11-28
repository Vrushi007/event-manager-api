from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import bcrypt
import hashlib

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    full_name = Column(String(120), nullable=True)
    password_hash = Column(String(256), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    registrations = relationship("Registration", back_populates="user", cascade="all, delete-orphan")
    created_events = relationship("Event", back_populates="creator", cascade="all, delete-orphan")

    def set_password(self, password: str):
        # Pre-hash with SHA256 to ensure we never exceed bcrypt's 72-byte limit
        # This is a common pattern to handle long passwords securely
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            # Hash with SHA256 first to get a fixed 64-character hex string
            password = hashlib.sha256(password_bytes).hexdigest()
            password_bytes = password.encode("utf-8")
        
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    def verify_password(self, password: str) -> bool:
        # Apply the same transformation for verification
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            password = hashlib.sha256(password_bytes).hexdigest()
            password_bytes = password.encode("utf-8")
        
        # Verify password against stored hash
        stored_hash = self.password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, stored_hash)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    venue = Column(String(255), nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    capacity = Column(Integer, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="created_events")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")

    @property
    def registered_count(self) -> int:
        return len(self.registrations)

    @property
    def is_full(self) -> bool:
        if self.capacity is None:
            return False
        return self.registered_count >= self.capacity


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
