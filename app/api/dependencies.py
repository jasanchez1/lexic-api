from typing import Generator, Optional

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsException, InvalidTokenException, TokenExpiredException
from app.db.database import get_db
from app.db.repositories.users import get_user_by_id
from app.models.user import User
from app.schemas.token import TokenPayload

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current authenticated user
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # Check token type and expiration
        if token_data.type != "access":
            raise InvalidTokenException()
            
    except (JWTError, ValidationError):
        raise InvalidCredentialsException()
        
    # Get user from database
    user = get_user_by_id(db, token_data.sub)
    if not user:
        raise InvalidCredentialsException()
        
    if not user.is_active:
        raise InvalidCredentialsException()
        
    return user


def get_current_active_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current active and verified user
    """
    if not current_user.is_verified:
        raise InvalidCredentialsException()
        
    return current_user


def get_optional_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Dependency to get the current user if authenticated, None otherwise
    """
    if not token:
        return None
        
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # Check token type
        if token_data.type != "access":
            return None
            
    except (JWTError, ValidationError):
        return None
        
    # Get user from database
    user = get_user_by_id(db, token_data.sub)
    if not user or not user.is_active:
        return None
        
    return user