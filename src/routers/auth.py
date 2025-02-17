from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from core.dependencies import get_current_active_user
from services.auth import AuthService
from schemas.user import UserCreate, Token, User as UserSchema

router = APIRouter()

@router.post("/register", response_model=Token)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.register(user_in)

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.login(form_data.username, form_data.password)

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user = Depends(get_current_active_user)):
    return current_user
