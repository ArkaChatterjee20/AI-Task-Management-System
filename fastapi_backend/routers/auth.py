
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_backend.database import get_db
from fastapi_backend.db_models import User
from fastapi_backend.models.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from fastapi_backend.services.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

bearer_scheme = HTTPBearer()


# =====================================================
# GET CURRENT AUTHENTICATED USER
# =====================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# =====================================================
# USER REGISTRATION
# =====================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    email = str(user_data.email).strip().lower()

    # Step 1: Check whether the email already exists
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    # Step 2: Release the database connection
    db.rollback()

    # Step 3: Hash the password without holding a DB connection
    hashed_password = hash_password(user_data.password)

    # Step 4: Create the new user
    new_user = User(
        email=email,
        password_hash=hashed_password,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    return new_user
# =====================================================
# USER LOGIN
# =====================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    email = str(login_data.email).strip().lower()

    # Step 1: Retrieve user information
    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 2: Copy required values before releasing the session
    user_id = user.user_id
    stored_password_hash = user.password_hash

    # Step 3: Release the database connection
    db.rollback()

    # Step 4: Verify password without holding a DB connection
    if not verify_password(
        login_data.password,
        stored_password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 5: Generate JWT
    access_token = create_access_token(user_id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

# =====================================================
# CURRENT USER PROFILE
# =====================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user
