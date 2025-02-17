from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from core.security import create_access_token
from core.config import settings
from schemas.user import UserCreate, Token
from .user import UserService

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def register(self, user_data: UserCreate) -> Token:
        # Check if user exists
        if self.user_service.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = self.user_service.create_user(user_data)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return Token(access_token=access_token, token_type="bearer")

    def login(self, email: str, password: str) -> Token:
        user = self.user_service.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return Token(access_token=access_token, token_type="bearer")