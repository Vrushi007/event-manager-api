from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


# ============================================
# USER SCHEMAS
# ============================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    is_admin: bool = False


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_admin: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserInToken(BaseModel):
    id: int
    email: str
    is_admin: bool


# ============================================
# TOKEN SCHEMAS
# ============================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInToken


class TokenData(BaseModel):
    user_id: Optional[int] = None
    is_admin: bool = False


# ============================================
# EVENT SCHEMAS
# ============================================

class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    venue: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    capacity: Optional[int] = Field(None, ge=1)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    venue: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = Field(None, ge=1)


class EventResponse(EventBase):
    id: int
    created_by: int
    created_at: datetime
    registered_count: int
    is_full: bool
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# REGISTRATION SCHEMAS
# ============================================

class RegistrationBase(BaseModel):
    event_id: int


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registered_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RegistrationWithUser(RegistrationResponse):
    user: UserResponse
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# RESPONSE MESSAGES
# ============================================

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
