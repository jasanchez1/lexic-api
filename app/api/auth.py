from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.exceptions import BadRequestException
from app.db.database import get_db
from app.schemas.auth import Login, SignUp, TokenResponse, RefreshToken
from app.schemas.user import User
from app.services.auth import login as login_service
from app.services.auth import signup as signup_service
from app.services.auth import refresh_token as refresh_token_service
from app.services.auth import logout as logout_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(data: Login, db: Session = Depends(get_db)):
    """
    Login endpoint for users with email and password
    """
    return login_service(db, data)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: SignUp, db: Session = Depends(get_db)):
    """
    Signup endpoint to create a new user
    """
    return signup_service(db, data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshToken, db: Session = Depends(get_db)):
    """
    Refresh token endpoint to get a new access token
    """
    if not data.refresh_token:
        raise BadRequestException("Refresh token is required")
        
    return refresh_token_service(db, data.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    data: RefreshToken = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout endpoint to revoke refresh token
    """
    if not data.refresh_token:
        raise BadRequestException("Refresh token is required")
        
    logout_service(db, data.refresh_token)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user