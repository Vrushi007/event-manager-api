from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token, UserInToken, MessageResponse
from app.dependencies import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        is_admin=user_data.is_admin
    )
    new_user.set_password(user_data.password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return MessageResponse(
        message="User created successfully",
        detail=f"User ID: {new_user.id}"
    )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password to get access token.
    
    For Swagger UI testing:
    - Username field = your email
    - Password field = your password
    """
    # Find user by email (OAuth2PasswordRequestForm uses 'username' field)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "is_admin": user.is_admin
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserInToken(
            id=user.id,
            email=user.email,
            is_admin=user.is_admin
        )
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_db)
):
    """
    Get current user information
    """
    from app.dependencies import get_current_user
    current_user = Depends(get_current_user)
    return current_user
