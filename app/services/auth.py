from datetime import datetime, timedelta, UTC
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import UserAlreadyExistsException, InvalidCredentialsException
from app.core.security import authenticate_user, create_access_token, create_refresh_token
from app.db.repositories.users import get_user_by_email, create_user
from app.db.repositories.tokens import create_token, get_token_by_token, revoke_token
from app.models.user import User
from app.schemas.auth import Login, SignUp, TokenResponse
from app.schemas.user import UserCreate


def login(db: Session, data: Login) -> TokenResponse:
    """
    Authenticate user and return tokens
    """
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise InvalidCredentialsException()
        
    return create_tokens_for_user(db, user)


def signup(db: Session, data: SignUp) -> TokenResponse:
    """
    Register a new user and return tokens
    """
    # Check if user exists
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise UserAlreadyExistsException(data.email)
        
    # Create user
    user_in = UserCreate(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name
    )
    user = create_user(db, user_in)
    
    # Create and return tokens
    return create_tokens_for_user(db, user)


def refresh_token(db: Session, refresh_token: str) -> TokenResponse:
    """
    Create new access token using refresh token
    """
    from jose import jwt, JWTError
    from app.core.exceptions import InvalidTokenException
    from app.db.repositories.users import get_user_by_id
    
    try:
        # Decode refresh token
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Validate token type
        if payload.get("type") != "refresh":
            raise InvalidTokenException()
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenException()
            
        # Check jti value
        jti = payload.get("jti")
        if not jti:
            raise InvalidTokenException()
            
        # Check if token is in database
        db_token = get_token_by_token(db, jti)
        if not db_token or db_token.is_revoked:
            raise InvalidTokenException()
            
        # Get user from database
        user = get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise InvalidTokenException()
            
        # Revoke old refresh token
        revoke_token(db, db_token)
        
        # Create new tokens
        return create_tokens_for_user(db, user)
        
    except (JWTError, InvalidTokenException):
        raise InvalidTokenException()


def create_tokens_for_user(db: Session, user: User) -> TokenResponse:
    """
    Create access and refresh tokens for user
    """
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token, jti = create_refresh_token(subject=user.id)
    
    # Store refresh token in database
    refresh_token_expires = datetime.now(tz=UTC) + timedelta(days=7)
    create_token(
        db=db,
        user_id=user.id,
        token=jti,
        token_type="refresh",
        expires_at=refresh_token_expires
    )
    
    # Return tokens
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id)
    )


def logout(db: Session, refresh_token: str) -> None:
    """
    Logout user by revoking refresh token
    """
    from jose import jwt, JWTError
    
    try:
        # Decode refresh token
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Get jti value
        jti = payload.get("jti")
        if jti:
            # Revoke token in database
            db_token = get_token_by_token(db, jti)
            if db_token:
                revoke_token(db, db_token)
    except JWTError:
        # Invalid token, nothing to do
        pass