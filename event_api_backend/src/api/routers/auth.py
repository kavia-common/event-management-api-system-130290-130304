"""
Authentication routes: user registration and login.

Provides:
- POST /auth/register
- POST /auth/login
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_password_hash, verify_password, create_access_token
from ..models import User
from ..schemas import UserCreate, UserOut, Token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password.",
    responses={409: {"description": "Email already registered"}},
)
# PUBLIC_INTERFACE
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a user with email and password."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login to get JWT access token",
    description="Authenticate using email and password. Returns a JWT bearer token.",
    responses={401: {"description": "Invalid credentials"}},
)
# PUBLIC_INTERFACE
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    User login endpoint.

    Parameters:
    - username: email (per OAuth2PasswordRequestForm)
    - password: password

    Returns:
    - access_token: JWT token
    - token_type: bearer
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(subject=user.id)
    return Token(access_token=token, token_type="bearer")
